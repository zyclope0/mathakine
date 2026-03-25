"""
Service applicatif pour la soumission de tentatives de défis logiques.
Orchestration tentative/progression : transaction, persistance, mapping réponse.
LOT 2 / LOT 2.1 : boundary de soumission de réponse challenge.
LOT A6 : point d'entrée sync pour le handler via run_db_bound().
LOT B1 : use case typé (Command/Result, exceptions métier).
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.exceptions import ChallengeAttemptRecordError, ChallengeNotFoundError
from app.schemas.logic_challenge import (
    ChallengeAttemptRequest,
    ChallengeBadgeEarned,
    ChallengeProgressNotification,
    SubmitChallengeAttemptCommand,
    SubmitChallengeAttemptResult,
)
from app.services.challenges.challenge_answer_service import check_answer
from app.services.challenges.challenge_progress_service import (
    normalize_challenge_type_key,
    upsert_challenge_progress,
)
from app.services.challenges.logic_challenge_service import LogicChallengeService
from app.services.exercises.exercise_attempt_service import POINTS_PER_CORRECT_EXERCISE
from app.services.gamification.gamification_service import GamificationService
from app.services.gamification.point_source import PointEventSourceType
from app.services.progress.streak_service import update_user_streak

logger = get_logger(__name__)


def _badge_dict_to_earned(badge_dict: dict) -> ChallengeBadgeEarned:
    """Convertit un dict badge (BadgeService) en ChallengeBadgeEarned."""
    return ChallengeBadgeEarned(
        badge_id=badge_dict.get("id"),
        code=badge_dict.get("code"),
        name=badge_dict.get("name"),
        description=badge_dict.get("description"),
        star_wars_title=badge_dict.get("star_wars_title"),
        difficulty=badge_dict.get("difficulty"),
        points_reward=badge_dict.get("points_reward"),
        earned_at=badge_dict.get("earned_at"),
    )


def _progress_dict_to_notification(
    progress_dict: dict,
) -> ChallengeProgressNotification:
    """Convertit un dict progress (BadgeService.get_closest_progress_notification)."""
    return ChallengeProgressNotification(
        name=progress_dict.get("name"),
        remaining=progress_dict.get("remaining"),
    )


def _execute_attempt(
    cmd: SubmitChallengeAttemptCommand, db: Session
) -> SubmitChallengeAttemptResult:
    """
    Exécution métier d'une tentative (synchrone, appelé dans db_session).
    Responsabilités : validation réponse, persistance, badges, streak, daily, notification.
    """
    challenge = LogicChallengeService.get_challenge_or_raise(db, cmd.challenge_id)
    challenge_type = (
        str(challenge.challenge_type).lower() if challenge.challenge_type else ""
    )
    is_correct = check_answer(
        challenge_type=challenge_type,
        user_answer=cmd.user_solution,
        correct_answer=challenge.correct_answer or "",
        visual_data=getattr(challenge, "visual_data", None),
    )

    attempt_data = {
        "user_id": cmd.user_id,
        "challenge_id": cmd.challenge_id,
        "user_solution": cmd.user_solution,
        "is_correct": is_correct,
        "time_spent": cmd.time_spent,
        "hints_used": cmd.hints_used_count,
    }
    attempt = LogicChallengeService.record_attempt(db, attempt_data, auto_commit=False)
    if not attempt:
        raise ChallengeAttemptRecordError("Impossible d'enregistrer la tentative.")

    try:
        progress_savepoint = db.begin_nested()
        upsert_challenge_progress(
            db,
            cmd.user_id,
            normalize_challenge_type_key(challenge),
            is_correct,
        )
        progress_savepoint.commit()
    except Exception as progress_err:
        if "progress_savepoint" in locals() and progress_savepoint.is_active:
            progress_savepoint.rollback()
        logger.warning(
            "challenge_progress upsert (best effort): %s",
            progress_err,
            exc_info=True,
        )

    new_badges: list[ChallengeBadgeEarned] = []
    if is_correct:
        try:
            # Pas de savepoint dédié : aligné sur exercise_attempt_service (apply_points direct).
            GamificationService.apply_points(
                db,
                cmd.user_id,
                POINTS_PER_CORRECT_EXERCISE,
                PointEventSourceType.LOGIC_CHALLENGE_COMPLETED,
                source_id=cmd.challenge_id,
            )
        except Exception as gamif_err:
            logger.error(
                "Gamification error on challenge %s: %s",
                cmd.challenge_id,
                gamif_err,
            )

        try:
            from app.services.badges.badge_service import BadgeService

            badge_service = BadgeService(db, auto_commit=False)
            raw_badges = badge_service.check_and_award_badges(cmd.user_id)
            new_badges = [_badge_dict_to_earned(b) for b in raw_badges]
        except (SQLAlchemyError, TypeError, ValueError) as badge_err:
            logger.warning(
                "Badge check après défi (best effort): %s",
                badge_err,
                exc_info=True,
            )

    try:
        streak_savepoint = db.begin_nested()
        update_user_streak(db, cmd.user_id, auto_commit=False)
        streak_savepoint.commit()
    except (SQLAlchemyError, TypeError, ValueError):
        if "streak_savepoint" in locals() and streak_savepoint.is_active:
            streak_savepoint.rollback()
        logger.debug("Streak update skipped", exc_info=True)

    if is_correct:
        try:
            from app.services.progress.daily_challenge_service import (
                record_logic_challenge_completed,
            )

            daily_savepoint = db.begin_nested()
            record_logic_challenge_completed(db, cmd.user_id, is_correct)
            daily_savepoint.commit()
        except Exception:
            if "daily_savepoint" in locals() and daily_savepoint.is_active:
                daily_savepoint.rollback()
            logger.debug("Daily challenge update skipped (logic)", exc_info=True)

    progress_notification: ChallengeProgressNotification | None = None
    if not new_badges:
        try:
            from app.services.badges.badge_service import BadgeService

            svc = BadgeService(db, auto_commit=False)
            raw_notif = svc.get_closest_progress_notification(cmd.user_id)
            if raw_notif:
                progress_notification = _progress_dict_to_notification(raw_notif)
        except (SQLAlchemyError, TypeError, ValueError):
            logger.debug(
                "Progress notification skipped (best effort)",
                exc_info=True,
            )

    db.commit()
    db.refresh(attempt)

    hints_remaining: int | None = None
    if not is_correct:
        hints_list = challenge.hints if isinstance(challenge.hints, list) else []
        hints_remaining = max(0, len(hints_list) - cmd.hints_used_count)

    return SubmitChallengeAttemptResult(
        is_correct=is_correct,
        explanation=challenge.solution_explanation if is_correct else None,
        new_badges=new_badges,
        progress_notification=progress_notification,
        hints_remaining=hints_remaining,
    )


def submit_challenge_attempt_sync(
    db: Session,
    challenge_id: int,
    user_id: int,
    user_solution: str,
    time_spent: float | None = None,
    hints_used_count: int = 0,
) -> SubmitChallengeAttemptResult:
    """
    Version synchrone pour appel avec session fournie (compat LogicChallengeService).
    """
    cmd = SubmitChallengeAttemptCommand(
        challenge_id=challenge_id,
        user_id=user_id,
        user_solution=user_solution,
        time_spent=time_spent,
        hints_used_count=hints_used_count,
    )
    return _execute_attempt(cmd, db)


def submit_challenge_attempt(
    challenge_id: int,
    user_id: int,
    request: ChallengeAttemptRequest,
) -> SubmitChallengeAttemptResult:
    """
    Soumet une tentative de réponse pour un défi logique (sync).
    Exécuté via run_db_bound() depuis le handler.

    Args:
        challenge_id: ID du défi
        user_id: ID de l'utilisateur
        request: Payload validé (user_solution, time_spent, hints_used_count)

    Returns:
        SubmitChallengeAttemptResult typé

    Raises:
        ChallengeNotFoundError: si le défi n'existe pas
        ChallengeAttemptRecordError: si l'enregistrement échoue
    """
    cmd = SubmitChallengeAttemptCommand(
        challenge_id=challenge_id,
        user_id=user_id,
        user_solution=request.user_solution,
        time_spent=request.time_spent,
        hints_used_count=request.hints_used_count,
    )
    with sync_db_session() as db:
        return _execute_attempt(cmd, db)

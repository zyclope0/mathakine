"""
Service applicatif pour la soumission de tentatives de défis logiques.
Orchestration tentative/progression : transaction, persistance, mapping réponse.
LOT 2 / LOT 2.1 : boundary de soumission de réponse challenge.
"""

from typing import Any, Dict

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.exceptions import ChallengeNotFoundError
from app.schemas.logic_challenge import ChallengeAttemptRequest
from app.services.challenge_answer_service import check_answer
from app.services.logic_challenge_service import LogicChallengeService
from app.utils.db_utils import db_session

logger = get_logger(__name__)


def _orchestrate_attempt(
    db: Session,
    challenge_id: int,
    user_id: int,
    user_solution: str,
    time_spent: Any,
    hints_used_count: int,
) -> Dict[str, Any]:
    """
    Orchestration métier d'une tentative de défi (synchrone, appelé dans db_session).
    """
    challenge = LogicChallengeService.get_challenge_or_raise(db, challenge_id)
    challenge_type = (
        str(challenge.challenge_type).lower() if challenge.challenge_type else ""
    )
    is_correct = check_answer(
        challenge_type=challenge_type,
        user_answer=user_solution,
        correct_answer=challenge.correct_answer or "",
        visual_data=getattr(challenge, "visual_data", None),
    )

    attempt_data = {
        "user_id": user_id,
        "challenge_id": challenge_id,
        "user_solution": user_solution,
        "is_correct": is_correct,
        "time_spent": time_spent,
        "hints_used": hints_used_count,
    }
    attempt = LogicChallengeService.record_attempt(db, attempt_data, auto_commit=False)
    if not attempt:
        raise ValueError("Impossible d'enregistrer la tentative.")

    new_badges = []
    if is_correct:
        try:
            from app.services.badge_service import BadgeService

            badge_service = BadgeService(db, auto_commit=False)
            new_badges = badge_service.check_and_award_badges(user_id)
        except (SQLAlchemyError, TypeError, ValueError) as badge_err:
            logger.warning(
                "Badge check après défi (best effort): %s",
                badge_err,
                exc_info=True,
            )

    try:
        from app.services.streak_service import update_user_streak

        streak_savepoint = db.begin_nested()
        update_user_streak(db, user_id, auto_commit=False)
        streak_savepoint.commit()
    except ImportError:
        logger.warning("Streak service indisponible (ImportError)", exc_info=True)
    except (SQLAlchemyError, TypeError, ValueError):
        if "streak_savepoint" in locals() and streak_savepoint.is_active:
            streak_savepoint.rollback()
        logger.debug("Streak update skipped", exc_info=True)

    if is_correct:
        try:
            from app.services.daily_challenge_service import (
                record_logic_challenge_completed,
            )

            daily_savepoint = db.begin_nested()
            record_logic_challenge_completed(db, user_id, is_correct)
            daily_savepoint.commit()
        except Exception:
            if "daily_savepoint" in locals() and daily_savepoint.is_active:
                daily_savepoint.rollback()
            logger.debug("Daily challenge update skipped (logic)", exc_info=True)

    progress_notif = None
    if not new_badges:
        try:
            from app.services.badge_service import BadgeService

            svc = BadgeService(db, auto_commit=False)
            progress_notif = svc.get_closest_progress_notification(user_id)
        except (SQLAlchemyError, TypeError, ValueError):
            logger.debug(
                "Progress notification skipped (best effort)",
                exc_info=True,
            )

    db.commit()
    db.refresh(attempt)

    response_data = {
        "is_correct": is_correct,
        "explanation": challenge.solution_explanation if is_correct else None,
        "new_badges": new_badges,
    }
    if progress_notif:
        response_data["progress_notification"] = progress_notif

    if not is_correct:
        hints_list = challenge.hints if isinstance(challenge.hints, list) else []
        response_data["hints_remaining"] = len(hints_list) - hints_used_count

    return response_data


def submit_challenge_attempt_sync(
    db: Session,
    challenge_id: int,
    user_id: int,
    user_solution: str,
    time_spent: Any = None,
    hints_used_count: int = 0,
) -> Dict[str, Any]:
    """
    Version synchrone pour appel avec session fournie (compat LogicChallengeService).
    """
    return _orchestrate_attempt(
        db, challenge_id, user_id, user_solution, time_spent, hints_used_count
    )


async def submit_challenge_attempt(
    challenge_id: int,
    user_id: int,
    request: ChallengeAttemptRequest,
) -> Dict[str, Any]:
    """
    Soumet une tentative de réponse pour un défi logique.
    Gère la transaction, la persistance tentative/progression et retourne le dict de réponse.

    Args:
        challenge_id: ID du défi
        user_id: ID de l'utilisateur
        request: Payload validé (user_solution, time_spent, hints_used_count)

    Returns:
        Dict avec is_correct, explanation, new_badges, progress_notification, hints_remaining

    Raises:
        ChallengeNotFoundError: si le défi n'existe pas
    """
    async with db_session() as db:
        return _orchestrate_attempt(
            db,
            challenge_id,
            user_id,
            request.user_solution,
            request.time_spent,
            request.hints_used_count,
        )

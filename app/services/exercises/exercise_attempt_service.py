"""
Service applicatif pour l'orchestration de la soumission de réponse.

Responsabilité : validation réponse, correction, orchestration badges/streak/daily,
transaction, construction SubmitAnswerResponse.
"""

from typing import Any, Dict

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.exceptions import ExerciseNotFoundError, ExerciseSubmitError
from app.models.exercise import ExerciseType
from app.models.user import User
from app.repositories.exercise_attempt_repository import (
    create_attempt,
    get_exercise_for_submit_validation,
    update_progress_after_attempt,
)
from app.schemas.exercise import SubmitAnswerResponse
from app.services.gamification.gamification_service import GamificationService
from app.services.gamification.point_source import PointEventSourceType
from app.services.progress.streak_service import update_user_streak
from app.services.spaced_repetition.spaced_repetition_service import (
    record_exercise_attempt_for_spaced_repetition,
)
from app.utils.exercise_answer_compare import answers_equivalent_numeric_tolerant
from app.utils.json_utils import make_json_serializable

logger = get_logger(__name__)

POINTS_PER_CORRECT_EXERCISE = 10


def _check_answer_correct(exercise: Dict[str, Any], selected_answer: Any) -> bool:
    """
    Détermine si la réponse est correcte selon le type d'exercice.

    - TEXTE / MIXTE : insensible à la casse (strip).
    - Autres types : égalité stricte après strip, puis tolérance explicite :
      pourcentage (45 % ≈ 45), virgule décimale (3,5 ≈ 3.5), fraction ≈ décimal (1/2 ≈ 0.5).
    """
    correct_answer = exercise.get("correct_answer")
    if not correct_answer:
        return False
    text_based = {ExerciseType.TEXTE.value, ExerciseType.MIXTE.value}
    exercise_type = str(exercise.get("exercise_type", "")).upper()
    selected = str(selected_answer).strip()
    correct = str(correct_answer).strip()
    if exercise_type in text_based:
        return selected.lower() == correct.lower()
    if selected == correct:
        return True
    return answers_equivalent_numeric_tolerant(selected, correct)


def submit_answer(
    db: Session,
    exercise_id: int,
    user_id: int,
    selected_answer: Any,
    time_spent: float = 0,
) -> SubmitAnswerResponse:
    """
    Traite la soumission d'une réponse : validation, enregistrement, progression,
    badges, streak, daily challenge.
    Retourne SubmitAnswerResponse pour la réponse HTTP.
    Lève ExerciseNotFoundError (404) ou ExerciseSubmitError (500) en cas d'erreur métier.
    """
    exercise = get_exercise_for_submit_validation(db, exercise_id)
    if not exercise:
        raise ExerciseNotFoundError()

    correct_answer = exercise.get("correct_answer")
    if not correct_answer:
        logger.error("ERREUR: L'exercice %s n'a pas de correct_answer", exercise_id)
        raise ExerciseSubmitError(
            500, "L'exercice n'a pas de réponse correcte définie."
        )

    is_correct = _check_answer_correct(exercise, selected_answer)
    logger.debug(
        "Réponse correcte? %s (selected: '%s', correct: '%s')",
        is_correct,
        selected_answer,
        correct_answer,
    )

    attempt_data = {
        "user_id": user_id,
        "exercise_id": exercise_id,
        "user_answer": selected_answer,
        "is_correct": is_correct,
        "time_spent": time_spent,
    }

    attempt_obj = create_attempt(db, attempt_data)
    if not attempt_obj:
        logger.error("ERREUR: La tentative n'a pas été enregistrée correctement")
        raise ExerciseSubmitError(
            500, "Erreur lors de l'enregistrement de la tentative"
        )

    logger.info("Tentative enregistrée avec succès")

    exercise_type = exercise.get("exercise_type", "")
    tier_val = exercise.get("difficulty_tier")
    tier_absent = 1 if tier_val is None else 0
    tier_token = "none" if tier_val is None else str(int(tier_val))
    outcome = "correct" if is_correct else "incorrect"
    # F43-A1 — structured observability: grep ``f43_exercise_attempt`` ; aggregate by
    # difficulty_tier / tier_absent / outcome (no schema change).
    logger.info(
        "f43_exercise_attempt: user_id=%%s exercise_id=%%s exercise_type=%%s difficulty_tier=%%s tier_absent=%%s outcome=%%s",
        user_id,
        exercise_id,
        exercise_type,
        tier_token,
        tier_absent,
        outcome,
    )
    difficulty = exercise.get("difficulty", "")

    user_for_progress = db.query(User).filter(User.id == user_id).first()

    try:
        progress_savepoint = db.begin_nested()
        update_progress_after_attempt(
            db,
            user_id,
            exercise_type,
            difficulty,
            is_correct,
            time_spent,
            user=user_for_progress,
        )
        progress_savepoint.commit()
    except SQLAlchemyError as stats_err:
        if "progress_savepoint" in locals() and progress_savepoint.is_active:
            progress_savepoint.rollback()
        logger.error("Erreur DB lors de la mise à jour des statistiques: %s", stats_err)
    except (TypeError, ValueError) as stats_err:
        if "progress_savepoint" in locals() and progress_savepoint.is_active:
            progress_savepoint.rollback()
        logger.error(
            "Erreur de données lors de la mise à jour des statistiques: %s", stats_err
        )

    try:
        sr_savepoint = db.begin_nested()
        record_exercise_attempt_for_spaced_repetition(
            db,
            user_id=user_id,
            exercise_id=exercise_id,
            is_correct=is_correct,
            time_spent_seconds=float(time_spent or 0),
            attempt_id=int(attempt_obj.id),
        )
        sr_savepoint.commit()
    except SQLAlchemyError as sr_err:
        if "sr_savepoint" in locals() and sr_savepoint.is_active:
            sr_savepoint.rollback()
        logger.error("Erreur DB lors de la mise à jour spaced repetition: %s", sr_err)
    except (TypeError, ValueError) as sr_err:
        if "sr_savepoint" in locals() and sr_savepoint.is_active:
            sr_savepoint.rollback()
        logger.error(
            "Erreur de données lors de la mise à jour spaced repetition: %s", sr_err
        )

    if is_correct:
        try:
            # Pas de savepoint dédié : aligné sur daily_challenge / badges (apply_points direct).
            # Un nested + with_for_update (PostgreSQL) sur la ligne users peut échouer en imbriqué.
            GamificationService.apply_points(
                db,
                user_id,
                POINTS_PER_CORRECT_EXERCISE,
                PointEventSourceType.EXERCISE_COMPLETED,
                source_id=exercise_id,
            )
        except Exception as gamif_err:
            logger.error(
                "Gamification error on exercise {}: {}", exercise_id, gamif_err
            )

    new_badges = []
    try:
        from app.services.badges.badge_service import BadgeService

        badge_service = BadgeService(db, auto_commit=False)
        attempt_for_badges = {
            "exercise_type": exercise_type,
            "is_correct": is_correct,
            "time_spent": time_spent,
            "exercise_id": exercise_id,
            "created_at": (
                attempt_obj.created_at.isoformat() if attempt_obj.created_at else None
            ),
        }
        new_badges = badge_service.check_and_award_badges(user_id, attempt_for_badges)
        if new_badges:
            logger.info(
                "🎖️ %s nouveaux badges attribués à l'utilisateur %s",
                len(new_badges),
                user_id,
            )
    except SQLAlchemyError as e:
        logger.warning(
            "⚠️ Erreur DB lors de la vérification des badges",
            exc_info=True,
        )
    except (TypeError, ValueError) as e:
        logger.warning(
            "⚠️ Erreur de données lors de la vérification des badges",
            exc_info=True,
        )

    try:
        streak_savepoint = db.begin_nested()
        update_user_streak(db, user_id, auto_commit=False)
        streak_savepoint.commit()
    except SQLAlchemyError:
        if "streak_savepoint" in locals() and streak_savepoint.is_active:
            streak_savepoint.rollback()
        logger.debug("Streak update skipped (DB error)", exc_info=True)
    except (TypeError, ValueError):
        if "streak_savepoint" in locals() and streak_savepoint.is_active:
            streak_savepoint.rollback()
        logger.debug("Streak update skipped (data/type error)", exc_info=True)

    try:
        from app.services.progress.daily_challenge_service import (
            record_exercise_completed,
        )

        daily_savepoint = db.begin_nested()
        record_exercise_completed(db, user_id, exercise_type, is_correct)
        daily_savepoint.commit()
    except Exception:
        if "daily_savepoint" in locals() and daily_savepoint.is_active:
            daily_savepoint.rollback()
        logger.debug("Daily challenge update skipped", exc_info=True)

    progress_notif = None
    if not new_badges:
        try:
            from app.services.badges.badge_service import BadgeService

            badge_svc = BadgeService(db, auto_commit=False)
            progress_notif = badge_svc.get_closest_progress_notification(user_id)
        except (SQLAlchemyError, TypeError, ValueError):
            logger.debug("Badge progress notification skipped", exc_info=True)

    db.commit()
    db.refresh(attempt_obj)
    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=correct_answer,
        explanation=exercise.get("explanation") or "",
        attempt_id=attempt_obj.id,
        new_badges=make_json_serializable(new_badges) if new_badges else None,
        badges_earned=len(new_badges) if new_badges else None,
        progress_notification=progress_notif,
    )


def submit_answer_sync(
    exercise_id: int,
    user_id: int,
    selected_answer: Any,
    time_spent: float = 0,
) -> SubmitAnswerResponse:
    """
    Point d'entrée sync pour soumission de réponse.
    Ouvre sync_db_session et délègue à submit_answer.
    Utilisé par les handlers via run_db_bound().
    """
    with sync_db_session() as db:
        return submit_answer(db, exercise_id, user_id, selected_answer, time_spent)

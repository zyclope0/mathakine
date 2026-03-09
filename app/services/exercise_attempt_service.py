"""
Service applicatif pour l'orchestration de la soumission de réponse.

Responsabilité : validation réponse, correction, orchestration badges/streak/daily,
transaction, construction SubmitAnswerResponse.
"""

from typing import Any, Dict

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.exceptions import ExerciseNotFoundError, ExerciseSubmitError
from app.models.exercise import ExerciseType
from app.repositories.exercise_attempt_repository import (
    create_attempt,
    get_exercise_for_submit_validation,
    update_progress_after_attempt,
)
from app.schemas.exercise import SubmitAnswerResponse
from app.utils.json_utils import make_json_serializable

logger = get_logger(__name__)


def _check_answer_correct(exercise: Dict[str, Any], selected_answer: Any) -> bool:
    """
    Détermine si la réponse est correcte selon le type d'exercice.
    TEXTE/MIXTE : comparaison insensible à la casse ; autres : stricte.
    """
    correct_answer = exercise.get("correct_answer")
    if not correct_answer:
        return False
    text_based = [ExerciseType.TEXTE.value, ExerciseType.MIXTE.value]
    exercise_type = exercise.get("exercise_type", "")
    if exercise_type in text_based:
        return (
            str(selected_answer).lower().strip() == str(correct_answer).lower().strip()
        )
    return str(selected_answer).strip() == str(correct_answer).strip()


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
        logger.error(f"ERREUR: L'exercice {exercise_id} n'a pas de correct_answer")
        raise ExerciseSubmitError(
            500, "L'exercice n'a pas de réponse correcte définie."
        )

    is_correct = _check_answer_correct(exercise, selected_answer)
    logger.debug(
        f"Réponse correcte? {is_correct} "
        f"(selected: '{selected_answer}', correct: '{correct_answer}')"
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
    difficulty = exercise.get("difficulty", "")

    try:
        progress_savepoint = db.begin_nested()
        update_progress_after_attempt(
            db, user_id, exercise_type, difficulty, is_correct, time_spent
        )
        progress_savepoint.commit()
    except SQLAlchemyError as stats_err:
        if "progress_savepoint" in locals() and progress_savepoint.is_active:
            progress_savepoint.rollback()
        logger.error(f"Erreur DB lors de la mise à jour des statistiques: {stats_err}")
    except (TypeError, ValueError) as stats_err:
        if "progress_savepoint" in locals() and progress_savepoint.is_active:
            progress_savepoint.rollback()
        logger.error(
            f"Erreur de données lors de la mise à jour des statistiques: {stats_err}"
        )

    new_badges = []
    try:
        from app.services.badge_service import BadgeService

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
                f"🎖️ {len(new_badges)} nouveaux badges attribués "
                f"à l'utilisateur {user_id}"
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
        from app.services.streak_service import update_user_streak
    except ImportError:
        logger.warning("Streak service indisponible (ImportError)", exc_info=True)
    else:
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
        from app.services.daily_challenge_service import record_exercise_completed

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
            from app.services.badge_service import BadgeService

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

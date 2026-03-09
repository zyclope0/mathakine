"""
Repository pour les opérations de données liées à la soumission de réponse.

Responsabilité : lecture exercice pour validation, création tentative, mise à jour progression.
"""

from typing import Any, Dict, Optional

from sqlalchemy import String, cast
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.progress import Progress
from app.utils.json_utils import safe_parse_json

logger = get_logger(__name__)


def get_exercise_for_submit_validation(
    db: Session, exercise_id: int
) -> Optional[Dict[str, Any]]:
    """
    Récupère un exercice pour validation de réponse (submit_answer).
    Inclut correct_answer. Utilise cast() pour éviter les erreurs enum.

    Returns:
        Dict avec id, exercise_type, difficulty, correct_answer, choices, question, explanation
        ou None si non trouvé.
    """
    try:
        exercise_row = (
            db.query(
                Exercise.id,
                Exercise.question,
                Exercise.correct_answer,
                Exercise.choices,
                Exercise.explanation,
                cast(Exercise.exercise_type, String).label("exercise_type_str"),
                cast(Exercise.difficulty, String).label("difficulty_str"),
            )
            .filter(Exercise.id == exercise_id)
            .first()
        )

        if not exercise_row:
            return None

        return _row_to_submit_dict(exercise_row)
    except SQLAlchemyError as err:
        logger.error(f"Erreur get_exercise_for_submit_validation {exercise_id}: {err}")
        return None


def _row_to_submit_dict(row: Any) -> Dict[str, Any]:
    """Mappe une row exercice vers dict pour validation submit."""
    return {
        "id": row.id,
        "exercise_type": (
            (row.exercise_type_str or "ADDITION").upper()
            if getattr(row, "exercise_type_str", None)
            else "ADDITION"
        ),
        "difficulty": (
            (row.difficulty_str or "PADAWAN").upper()
            if getattr(row, "difficulty_str", None)
            else "PADAWAN"
        ),
        "choices": safe_parse_json(getattr(row, "choices", None), []),
        "question": getattr(row, "question", ""),
        "explanation": getattr(row, "explanation") or "",
        "correct_answer": getattr(row, "correct_answer", ""),
    }


def create_attempt(db: Session, attempt_data: Dict[str, Any]) -> Optional[Attempt]:
    """
    Crée une tentative. Aucun side effect (pas de mise à jour progression).

    Returns:
        La tentative créée ou None en cas d'erreur.
    """
    try:
        attempt = Attempt(**attempt_data)
        db.add(attempt)
        db.flush()
        return attempt
    except SQLAlchemyError as err:
        logger.error(f"Erreur create_attempt: {err}")
        return None


def update_progress_after_attempt(
    db: Session,
    user_id: int,
    exercise_type: str,
    difficulty: str,
    is_correct: bool,
    time_spent: float,
) -> None:
    """
    Met à jour ou crée Progress après une tentative.
    Extrait de _update_user_statistics.
    """
    progress = (
        db.query(Progress)
        .filter(
            Progress.user_id == user_id,
            Progress.exercise_type == exercise_type,
        )
        .first()
    )

    if progress:
        progress.total_attempts += 1
        if is_correct:
            progress.correct_attempts += 1
            progress.streak += 1
            if progress.streak > progress.highest_streak:
                progress.highest_streak = progress.streak
        else:
            progress.streak = 0

        if progress.average_time is None:
            progress.average_time = time_spent
        else:
            total_time = (
                progress.average_time * (progress.total_attempts - 1) + time_spent
            )
            progress.average_time = total_time / progress.total_attempts

        progress.completion_rate = progress.calculate_completion_rate()
        progress.update_mastery_level()
    else:
        new_progress = Progress(
            user_id=user_id,
            exercise_type=exercise_type,
            difficulty=difficulty or "initie",
            total_attempts=1,
            correct_attempts=1 if is_correct else 0,
            average_time=time_spent,
            streak=1 if is_correct else 0,
            highest_streak=1 if is_correct else 0,
        )
        db.add(new_progress)

    db.flush()

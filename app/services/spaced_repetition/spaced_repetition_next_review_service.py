"""
F04-P4 : prochaine révision due (lecture seule), payload review-safe pour l'API.
"""

from datetime import date, datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.repositories.spaced_repetition_repository import (
    fetch_next_due_spaced_repetition_item,
)
from app.services.spaced_repetition.spaced_repetition_read_service import (
    get_spaced_repetition_user_summary,
)
from app.utils.json_utils import make_json_serializable
from app.utils.review_safe_exercise import exercise_to_review_safe_dict


def build_next_review_api_payload(
    db: Session,
    user_id: int,
    *,
    today: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Agrège le résumé F04 existant et la prochaine carte due (si exercice actif).
    ``has_due_review`` est vrai uniquement si une carte *actionnable* existe.
    """
    when = today if today is not None else datetime.now(timezone.utc).date()
    summary = get_spaced_repetition_user_summary(db, user_id, today=when)
    item = fetch_next_due_spaced_repetition_item(db, user_id, when)
    if item is None:
        return {
            "has_due_review": False,
            "summary": summary,
            "next_review": None,
        }

    exercise = (
        db.query(Exercise)
        .filter(Exercise.id == item.exercise_id)
        .filter(Exercise.is_active.is_(True))
        .filter(Exercise.is_archived.is_(False))
        .first()
    )
    if exercise is None:
        return {
            "has_due_review": False,
            "summary": summary,
            "next_review": None,
        }

    due_status = "overdue" if item.next_review_date < when else "due_today"
    exercise_payload = make_json_serializable(exercise_to_review_safe_dict(exercise))

    return {
        "has_due_review": True,
        "summary": summary,
        "next_review": {
            "review_item_id": item.id,
            "exercise_id": item.exercise_id,
            "due_status": due_status,
            "next_review_date": item.next_review_date.isoformat(),
            "exercise": exercise_payload,
        },
    }


def get_next_review_api_payload(user_id: int) -> Dict[str, Any]:
    """Facade sync pour ``run_db_bound`` : session courte, aucune écriture SR."""
    from app.core.db_boundary import sync_db_session

    with sync_db_session() as db:
        return build_next_review_api_payload(db, user_id)

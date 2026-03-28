"""
Lecture agrégée F04 pour le dashboard API — aucune écriture, pas de SM-2.
"""

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.types import SpacedRepetitionUserSummary
from app.repositories.spaced_repetition_repository import (
    aggregate_spaced_repetition_for_user,
)


def get_spaced_repetition_user_summary(
    db: Session,
    user_id: int,
    *,
    today: Optional[date] = None,
) -> SpacedRepetitionUserSummary:
    """
    Agrégat user-level aligné sur la date UTC du moteur SR (soumissions exercices).
    """
    when = today if today is not None else datetime.now(timezone.utc).date()
    active, overdue, due_today, next_future = aggregate_spaced_repetition_for_user(
        db, user_id, when
    )
    return {
        "f04_initialized": active > 0,
        "active_cards_count": active,
        "due_today_count": due_today,
        "overdue_count": overdue,
        "next_review_date": (
            next_future.isoformat() if next_future is not None else None
        ),
    }

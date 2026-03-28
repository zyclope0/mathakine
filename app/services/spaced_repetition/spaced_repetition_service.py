"""
Apply SM-2 updates after a standard exercise attempt (F04-P1).

Idempotent per ``attempt_id`` via ``last_attempt_id``.
"""

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.spaced_repetition_item import SpacedRepetitionItem
from app.repositories.spaced_repetition_repository import (
    get_item_for_user_exercise,
    persist_spaced_repetition_item,
)
from app.services.spaced_repetition.sm2_engine import (
    SM2TransitionInput,
    apply_sm2_transition,
    derive_quality_from_attempt,
)

logger = get_logger(__name__)


def _utc_review_date() -> date:
    return datetime.now(timezone.utc).date()


def record_exercise_attempt_for_spaced_repetition(
    db: Session,
    *,
    user_id: int,
    exercise_id: int,
    is_correct: bool,
    time_spent_seconds: float,
    attempt_id: int,
    review_date: Optional[date] = None,
) -> None:
    """
    Upsert SR row for (user_id, exercise_id) from one attempt.

    Safe to call inside a nested transaction; logs and swallows DB errors
    so submit_answer still completes (aligned with progress/streak pattern).
    """
    when = review_date if review_date is not None else _utc_review_date()
    quality = derive_quality_from_attempt(is_correct, time_spent_seconds)

    existing = get_item_for_user_exercise(db, user_id, exercise_id)
    if existing is not None and existing.last_attempt_id == attempt_id:
        logger.debug(
            "spaced_repetition skip duplicate attempt_id=%s user=%s exercise=%s",
            attempt_id,
            user_id,
            exercise_id,
        )
        return

    prev: Optional[SM2TransitionInput] = None
    if existing is not None:
        prev = SM2TransitionInput(
            ease_factor=float(existing.ease_factor),
            interval_days=int(existing.interval_days),
            repetition_count=int(existing.repetition_count),
        )

    result = apply_sm2_transition(prev, quality, when)

    if existing is None:
        row = SpacedRepetitionItem(
            user_id=user_id,
            exercise_id=exercise_id,
            ease_factor=result.ease_factor,
            interval_days=result.interval_days,
            next_review_date=result.next_review_date,
            repetition_count=result.repetition_count,
            last_quality=result.last_quality,
            last_attempt_id=attempt_id,
        )
    else:
        row = existing
        row.ease_factor = result.ease_factor
        row.interval_days = result.interval_days
        row.next_review_date = result.next_review_date
        row.repetition_count = result.repetition_count
        row.last_quality = result.last_quality
        row.last_attempt_id = attempt_id

    persist_spaced_repetition_item(db, row)

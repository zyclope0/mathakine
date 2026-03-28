"""Persistence for spaced repetition items (F04)."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.spaced_repetition_item import SpacedRepetitionItem


def get_item_for_user_exercise(
    db: Session, user_id: int, exercise_id: int
) -> Optional[SpacedRepetitionItem]:
    return (
        db.query(SpacedRepetitionItem)
        .filter(
            SpacedRepetitionItem.user_id == user_id,
            SpacedRepetitionItem.exercise_id == exercise_id,
        )
        .first()
    )


def persist_spaced_repetition_item(db: Session, row: SpacedRepetitionItem) -> None:
    db.add(row)
    db.flush()

"""Persistence for spaced repetition items (F04)."""

from datetime import date
from typing import Optional, Tuple

from sqlalchemy import case, func
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


def aggregate_spaced_repetition_for_user(
    db: Session, user_id: int, today: date
) -> Tuple[int, int, int, Optional[date]]:
    """
    Read-model : une requête agrégée par utilisateur.

    Returns:
        (active_cards_count, overdue_count, due_today_count, next_future_review_date)
        ``next_future_review_date`` = min(next_review_date) où date > today, sinon None.
    """
    overdue_flag = case(
        (SpacedRepetitionItem.next_review_date < today, 1),
        else_=0,
    )
    due_today_flag = case(
        (SpacedRepetitionItem.next_review_date == today, 1),
        else_=0,
    )
    future_date = case(
        (
            SpacedRepetitionItem.next_review_date > today,
            SpacedRepetitionItem.next_review_date,
        ),
        else_=None,
    )

    row = (
        db.query(
            func.count(SpacedRepetitionItem.id).label("n"),
            func.coalesce(func.sum(overdue_flag), 0).label("overdue"),
            func.coalesce(func.sum(due_today_flag), 0).label("due_today"),
            func.min(future_date).label("next_future"),
        )
        .filter(SpacedRepetitionItem.user_id == user_id)
        .one()
    )

    n = int(row.n or 0)
    overdue = int(row.overdue or 0)
    due_today = int(row.due_today or 0)
    next_future: Optional[date] = row.next_future
    return n, overdue, due_today, next_future

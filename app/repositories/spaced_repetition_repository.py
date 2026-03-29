"""Persistence for spaced repetition items (F04)."""

from datetime import date
from typing import Optional, Tuple

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
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

    Ne compte que les cartes actionnables (exercice actif, non archivé).

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
        .join(Exercise, SpacedRepetitionItem.exercise_id == Exercise.id)
        .filter(SpacedRepetitionItem.user_id == user_id)
        .filter(Exercise.is_active.is_(True))
        .filter(Exercise.is_archived.is_(False))
        .one()
    )

    n = int(row.n or 0)
    overdue = int(row.overdue or 0)
    due_today = int(row.due_today or 0)
    next_future: Optional[date] = row.next_future
    return n, overdue, due_today, next_future


def fetch_next_due_spaced_repetition_item(
    db: Session, user_id: int, today: date
) -> Optional[SpacedRepetitionItem]:
    """
    Prochaine carte due (lecture seule) : ``next_review_date`` <= today (UTC),
    exercice actif et non archivé.

    Ordonnancement pédagogique :
    1. en retard (date < today) avant ceux dus ce jour même
    2. plus ancienne ``next_review_date`` en premier
    3. ``SpacedRepetitionItem.id`` croissant (stable)
    """
    overdue_first = case(
        (SpacedRepetitionItem.next_review_date < today, 0),
        else_=1,
    )
    return (
        db.query(SpacedRepetitionItem)
        .join(Exercise, SpacedRepetitionItem.exercise_id == Exercise.id)
        .filter(SpacedRepetitionItem.user_id == user_id)
        .filter(SpacedRepetitionItem.next_review_date <= today)
        .filter(Exercise.is_active.is_(True))
        .filter(Exercise.is_archived.is_(False))
        .order_by(
            overdue_first.asc(),
            SpacedRepetitionItem.next_review_date.asc(),
            SpacedRepetitionItem.id.asc(),
        )
        .first()
    )

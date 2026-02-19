"""
Service de calcul de la série d'entraînement (streak).

Jours consécutifs avec au moins une activité (exercice ou défi).
"""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallengeAttempt
from app.models.user import User

logger = get_logger(__name__)


def _activity_dates_for_user(db: Session, user_id: int) -> set[date]:
    """Retourne l'ensemble des dates (UTC) où l'utilisateur a eu une activité."""
    dates = set()

    # Dates des tentatives exercices
    for (d,) in db.query(func.date(Attempt.created_at)).filter(
        Attempt.user_id == user_id
    ).distinct().all():
        if d:
            dates.add(d)

    # Dates des tentatives défis
    for (d,) in db.query(func.date(LogicChallengeAttempt.created_at)).filter(
        LogicChallengeAttempt.user_id == user_id
    ).distinct().all():
        if d:
            dates.add(d)

    return dates


def compute_streak(activity_dates: set[date], reference_date: date) -> int:
    """
    Calcule la série de jours consécutifs jusqu'à reference_date.
    Si reference_date n'est pas dans activity_dates, retourne 0.
    """
    if reference_date not in activity_dates:
        return 0

    count = 0
    d = reference_date
    while d in activity_dates:
        count += 1
        d -= timedelta(days=1)
    return count


def update_user_streak(db: Session, user_id: int) -> tuple[int, int]:
    """
    Recalcule et met à jour le streak de l'utilisateur.
    Retourne (current_streak, best_streak).
    """
    today = date.today()
    activity_dates = _activity_dates_for_user(db, user_id)
    current = compute_streak(activity_dates, today)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return (0, 0)

    prev_best = user.best_streak or 0
    best = max(prev_best, current)

    user.current_streak = current
    user.best_streak = best
    user.last_activity_date = today if today in activity_dates else user.last_activity_date
    db.commit()

    return (current, best)

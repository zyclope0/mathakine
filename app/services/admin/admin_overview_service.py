"""
KPIs globaux admin (B3.4).

Overview : total_users, total_exercises, total_challenges, total_attempts.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge
from app.models.user import User


def get_overview_for_api(db: Session) -> dict:
    """KPIs globaux : users, exercises, challenges, attempts."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_exercises = (
        db.query(func.count(Exercise.id))
        .filter(Exercise.is_archived.is_(False))
        .scalar()
        or 0
    )
    total_challenges = (
        db.query(func.count(LogicChallenge.id))
        .filter(LogicChallenge.is_archived.is_(False))
        .scalar()
        or 0
    )
    total_attempts = db.query(func.count(Attempt.id)).scalar() or 0
    return {
        "total_users": total_users,
        "total_exercises": total_exercises,
        "total_challenges": total_challenges,
        "total_attempts": total_attempts,
    }

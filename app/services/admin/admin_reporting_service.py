"""
Service rapports périodiques admin (B3.4).

Rapports par période : inscriptions, activité, taux succès.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, union
from sqlalchemy.orm import Session

from app.core.types import AdminReportDict
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallengeAttempt
from app.models.user import User


def get_reports_for_api(
    db: Session,
    *,
    period: str = "7d",
) -> AdminReportDict:
    """Rapports par période : new_users, attempts, success_rate, active_users."""
    days = 7 if period == "7d" else 30
    since = datetime.now(timezone.utc) - timedelta(days=days)

    new_users = (
        db.query(func.count(User.id)).filter(User.created_at >= since).scalar() or 0
    )
    attempts_exercises = (
        db.query(
            func.count(Attempt.id).label("total"),
            func.sum(case((Attempt.is_correct.is_(True), 1), else_=0)).label("correct"),
        )
        .filter(Attempt.created_at >= since)
        .first()
    )
    total_attempts = attempts_exercises[0] or 0
    correct_attempts = attempts_exercises[1] or 0
    challenge_attempts_count = (
        db.query(func.count(LogicChallengeAttempt.id))
        .filter(LogicChallengeAttempt.created_at >= since)
        .scalar()
        or 0
    )
    challenge_correct = (
        db.query(func.count(LogicChallengeAttempt.id))
        .filter(
            LogicChallengeAttempt.created_at >= since,
            LogicChallengeAttempt.is_correct.is_(True),
        )
        .scalar()
        or 0
    )
    q1 = db.query(Attempt.user_id).filter(Attempt.created_at >= since).distinct()
    q2 = (
        db.query(LogicChallengeAttempt.user_id)
        .filter(LogicChallengeAttempt.created_at >= since)
        .distinct()
    )
    u = union(q1, q2).subquery()
    active_users_count = db.query(func.count()).select_from(u).scalar() or 0
    total_attempts_all = total_attempts + challenge_attempts_count
    total_correct_all = correct_attempts + challenge_correct
    success_rate = (
        round((total_correct_all / total_attempts_all * 100), 1)
        if total_attempts_all > 0
        else 0.0
    )
    return {
        "period": period,
        "days": days,
        "new_users": new_users,
        "attempts_exercises": total_attempts,
        "attempts_challenges": challenge_attempts_count,
        "total_attempts": total_attempts_all,
        "success_rate": success_rate,
        "active_users": active_users_count,
    }

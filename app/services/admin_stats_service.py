"""
Service admin pour statistiques, rapports, audit log et modération.

Extrait de AdminService.
Phase 3, item 3.3c — audit architecture 03/2026.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from sqlalchemy import case, func, union
from sqlalchemy.orm import Session, joinedload

from app.models.admin_audit_log import AdminAuditLog
from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt
from app.models.user import User
from app.services.admin_helpers import parse_json_safe


class AdminStatsService:
    """Statistiques, rapports, audit log et modération admin."""

    @staticmethod
    def get_overview_for_api(db: Session) -> Dict[str, int]:
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_exercises = (
            db.query(func.count(Exercise.id))
            .filter(Exercise.is_archived == False)
            .scalar()
            or 0
        )
        total_challenges = (
            db.query(func.count(LogicChallenge.id))
            .filter(LogicChallenge.is_archived == False)
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

    @staticmethod
    def get_audit_log_for_api(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        action_filter: Optional[str] = None,
        resource_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        q = (
            db.query(AdminAuditLog)
            .options(joinedload(AdminAuditLog.admin_user))
            .order_by(AdminAuditLog.created_at.desc())
        )
        if action_filter:
            q = q.filter(AdminAuditLog.action == action_filter)
        if resource_filter:
            q = q.filter(AdminAuditLog.resource_type == resource_filter)
        total = q.count()
        logs = q.offset(skip).limit(limit).all()
        items = []
        for log in logs:
            admin_username = log.admin_user.username if log.admin_user else None
            items.append(
                {
                    "id": log.id,
                    "admin_user_id": log.admin_user_id,
                    "admin_username": admin_username,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "details": parse_json_safe(log.details),
                    "created_at": (
                        log.created_at.isoformat() if log.created_at else None
                    ),
                }
            )
        return {"items": items, "total": total}

    @staticmethod
    def get_moderation_for_api(
        db: Session,
        *,
        mod_type: str = "all",
        skip: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "exercises": [],
            "challenges": [],
            "total_exercises": 0,
            "total_challenges": 0,
        }
        if mod_type in ("exercises", "all"):
            q_ex = db.query(Exercise).filter(Exercise.ai_generated == True)
            result["total_exercises"] = q_ex.count()
            rows_ex = (
                q_ex.order_by(Exercise.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            for e in rows_ex:
                result["exercises"].append(
                    {
                        "id": e.id,
                        "title": e.title,
                        "exercise_type": e.exercise_type or "",
                        "age_group": e.age_group or "",
                        "is_archived": e.is_archived,
                        "created_at": (
                            e.created_at.isoformat() if e.created_at else None
                        ),
                    }
                )
        if mod_type in ("challenges", "all"):
            q_ch = db.query(LogicChallenge)
            result["total_challenges"] = q_ch.count()
            rows_ch = (
                q_ch.order_by(LogicChallenge.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            for c in rows_ch:
                ct_val = (
                    c.challenge_type.value
                    if hasattr(c.challenge_type, "value")
                    else str(c.challenge_type)
                )
                ag_val = (
                    c.age_group.value
                    if hasattr(c.age_group, "value")
                    else str(c.age_group)
                )
                result["challenges"].append(
                    {
                        "id": c.id,
                        "title": c.title,
                        "challenge_type": ct_val,
                        "age_group": ag_val,
                        "is_archived": c.is_archived,
                        "created_at": (
                            c.created_at.isoformat() if c.created_at else None
                        ),
                    }
                )
        return result

    @staticmethod
    def get_reports_for_api(
        db: Session,
        *,
        period: str = "7d",
    ) -> Dict[str, Any]:
        days = 7 if period == "7d" else 30
        since = datetime.now(timezone.utc) - timedelta(days=days)

        new_users = (
            db.query(func.count(User.id)).filter(User.created_at >= since).scalar() or 0
        )
        attempts_exercises = (
            db.query(
                func.count(Attempt.id).label("total"),
                func.sum(case((Attempt.is_correct == True, 1), else_=0)).label(
                    "correct"
                ),
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
                LogicChallengeAttempt.is_correct == True,
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

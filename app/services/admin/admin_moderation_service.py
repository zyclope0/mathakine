"""
Service modération admin (B3.4).

Contenu généré par IA pour modération : exercises, challenges.
"""

from typing import Any, Dict

from sqlalchemy.orm import Session

from app.core.types import ModerationDict
from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge


def get_moderation_for_api(
    db: Session,
    *,
    mod_type: str = "all",
    skip: int = 0,
    limit: int = 50,
) -> ModerationDict:
    """Contenu IA pour modération : exercises et/ou challenges selon mod_type."""
    result: Dict[str, Any] = {
        "exercises": [],
        "challenges": [],
        "total_exercises": 0,
        "total_challenges": 0,
    }
    if mod_type in ("exercises", "all"):
        q_ex = db.query(Exercise).filter(Exercise.ai_generated.is_(True))
        result["total_exercises"] = q_ex.count()
        rows_ex = (
            q_ex.order_by(Exercise.created_at.desc()).offset(skip).limit(limit).all()
        )
        for e in rows_ex:
            result["exercises"].append(
                {
                    "id": e.id,
                    "title": e.title,
                    "exercise_type": e.exercise_type or "",
                    "age_group": e.age_group or "",
                    "is_archived": e.is_archived,
                    "created_at": (e.created_at.isoformat() if e.created_at else None),
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
                c.age_group.value if hasattr(c.age_group, "value") else str(c.age_group)
            )
            result["challenges"].append(
                {
                    "id": c.id,
                    "title": c.title,
                    "challenge_type": ct_val,
                    "age_group": ag_val,
                    "is_archived": c.is_archived,
                    "created_at": (c.created_at.isoformat() if c.created_at else None),
                }
            )
    return result

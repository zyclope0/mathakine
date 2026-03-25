"""
Statistiques agrégées des défis logiques pour l'API (symétrique /api/exercises/stats).
"""

from typing import Any, Dict

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.logic_challenge import LogicChallenge


class ChallengeStatsService:
    """Compteurs globaux défis actifs : par type, difficulté (libellé), groupe d'âge."""

    @staticmethod
    def get_challenges_stats_for_api(db: Session) -> Dict[str, Any]:
        base = db.query(func.count(LogicChallenge.id)).filter(
            LogicChallenge.is_active.is_(True),
            LogicChallenge.is_archived.is_(False),
        )
        total = base.scalar() or 0

        total_archived = (
            db.query(func.count(LogicChallenge.id))
            .filter(LogicChallenge.is_archived.is_(True))
            .scalar()
            or 0
        )

        def _pct(count: int) -> float:
            return round((count / total * 100), 1) if total > 0 else 0.0

        by_type_query = (
            db.query(LogicChallenge.challenge_type, func.count(LogicChallenge.id))
            .filter(
                LogicChallenge.is_active.is_(True),
                LogicChallenge.is_archived.is_(False),
            )
            .group_by(LogicChallenge.challenge_type)
            .all()
        )
        by_type: Dict[str, Dict[str, Any]] = {}
        for ch_type, count in by_type_query:
            if ch_type is None:
                key = "unknown"
            else:
                raw = getattr(ch_type, "value", ch_type)
                key = str(raw).lower()
            by_type[key] = {"count": count, "percentage": _pct(count)}

        by_difficulty_query = (
            db.query(LogicChallenge.difficulty, func.count(LogicChallenge.id))
            .filter(
                LogicChallenge.is_active.is_(True),
                LogicChallenge.is_archived.is_(False),
            )
            .group_by(LogicChallenge.difficulty)
            .all()
        )
        by_difficulty: Dict[str, Dict[str, Any]] = {}
        for diff, count in by_difficulty_query:
            key = (
                str(diff).strip().upper()
                if diff is not None and str(diff).strip()
                else "UNSPECIFIED"
            )
            by_difficulty[key] = {"count": count, "percentage": _pct(count)}

        by_age_query = (
            db.query(LogicChallenge.age_group, func.count(LogicChallenge.id))
            .filter(
                LogicChallenge.is_active.is_(True),
                LogicChallenge.is_archived.is_(False),
            )
            .group_by(LogicChallenge.age_group)
            .all()
        )
        by_age_group: Dict[str, Dict[str, Any]] = {}
        for age_g, count in by_age_query:
            if age_g is None:
                key = "UNKNOWN"
            else:
                key = str(getattr(age_g, "value", age_g))
            by_age_group[key] = {"count": count, "percentage": _pct(count)}

        return {
            "total": total,
            "total_archived": total_archived,
            "by_type": by_type,
            "by_difficulty": by_difficulty,
            "by_age_group": by_age_group,
        }

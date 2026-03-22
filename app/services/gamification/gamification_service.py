"""
Moteur unique de gamification persistante : attribution de points + ledger + colonnes users.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.point_event import PointEvent
from app.models.user import User
from app.services.gamification.compute import compute_state_from_total_points
from app.services.gamification.constants import POINTS_PER_LEVEL
from app.services.gamification.exceptions import (
    GamificationUserNotFoundError,
    InvalidGamificationPointsDeltaError,
)
from app.services.gamification.level_titles import LEVEL_TITLES
from app.services.gamification.point_source import PointEventSourceType

logger = get_logger(__name__)


class GamificationService:
    """Porte d'entrée métier pour les points de compte (hors IRT / maîtrise pédagogique)."""

    @staticmethod
    def build_level_indicator_payload(user: User) -> Dict[str, Any]:
        """
        Structure stable pour API (/me, profil) — alignée sur les colonnes persistées.

        Ne dépend pas d'un filtre temporel du dashboard.
        """
        total = int(getattr(user, "total_points", None) or 0)
        level = int(getattr(user, "current_level", None) or 1)
        if level < 1:
            level = 1

        xp_raw = getattr(user, "experience_points", None)
        if xp_raw is None:
            _, _, computed_xp, _ = compute_state_from_total_points(total)
            current_xp = computed_xp
        else:
            current_xp = max(0, int(xp_raw))
            if POINTS_PER_LEVEL > 0:
                current_xp = min(current_xp, POINTS_PER_LEVEL - 1)

        title = LEVEL_TITLES.get(level) or f"Niveau {level}"

        return {
            "current": level,
            "title": title,
            "current_xp": current_xp,
            "next_level_xp": POINTS_PER_LEVEL,
            "jedi_rank": getattr(user, "jedi_rank", None) or "youngling",
        }

    @staticmethod
    def apply_points(
        db: Session,
        user_id: int,
        points_delta: int,
        source_type: PointEventSourceType,
        *,
        source_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Applique un gain de points, recalcule niveau / XP palier / rang, écrit le ledger.

        Returns:
            Snapshot dict (total_points, current_level, experience_points, jedi_rank,
            gamification_level) pour réponses API éventuelles.

        Raises:
            InvalidGamificationPointsDeltaError: si delta <= 0
            GamificationUserNotFoundError: si utilisateur absent
        """
        if points_delta <= 0:
            raise InvalidGamificationPointsDeltaError(
                "Le delta de points doit être strictement positif."
            )

        # Pas de with_for_update ici : SQLite (tests) ne le supporte pas ; charge faible sur ce flux.
        user = db.query(User).filter(User.id == user_id).one_or_none()
        if user is None:
            raise GamificationUserNotFoundError(f"Utilisateur {user_id} introuvable.")

        balance_before = int(getattr(user, "total_points", None) or 0)
        new_total, new_level, new_xp, new_rank = compute_state_from_total_points(
            balance_before + points_delta
        )

        user.total_points = new_total
        user.current_level = new_level
        user.experience_points = new_xp
        user.jedi_rank = new_rank

        event = PointEvent(
            user_id=user_id,
            source_type=str(source_type),
            source_id=source_id,
            points_delta=points_delta,
            balance_after=new_total,
            details=details,
        )
        db.add(event)
        db.flush()

        payload = GamificationService.build_level_indicator_payload(user)
        logger.info(
            "Gamification: user=%s source=%s delta=%s balance=%s level=%s",
            user_id,
            source_type,
            points_delta,
            new_total,
            new_level,
        )
        return {
            "total_points": new_total,
            "current_level": new_level,
            "experience_points": new_xp,
            "jedi_rank": new_rank,
            "gamification_level": payload,
        }

"""
Moteur unique de gamification persistante : attribution de points + ledger + colonnes users.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.point_event import PointEvent
from app.models.user import User
from app.services.gamification.compute import (
    canonicalize_progression_rank_bucket,
    compute_state_from_total_points,
    level_and_xp_from_total_points,
    points_to_gain_next_level,
)
from app.services.gamification.exceptions import (
    GamificationUserNotFoundError,
    InvalidGamificationPointsDeltaError,
)
from app.services.gamification.point_source import PointEventSourceType

logger = get_logger(__name__)


class GamificationService:
    """Porte d'entrée métier pour les points de compte (hors IRT / maîtrise pédagogique)."""

    @staticmethod
    def build_level_indicator_payload(user: User) -> Dict[str, Any]:
        """
        Structure stable pour API (/me, profil) — dérivée de ``total_points`` (vérité).

        Les colonnes ORM sont mises à jour à chaque ``apply_points`` ; l'indicateur
        recalcule niveau / XP palier / coût suivant pour éviter tout décalage lecture.
        """
        total = int(getattr(user, "total_points", None) or 0)
        level, current_xp = level_and_xp_from_total_points(total)
        next_cost = points_to_gain_next_level(level)

        # F42-P5 : pas de ``title`` narratif (ancien LEVEL_TITLES).
        # F43-A3 : ``progression_rank`` = clé publique préférée ; ``jedi_rank`` = alias legacy (même valeur).
        rank_bucket = canonicalize_progression_rank_bucket(
            getattr(user, "jedi_rank", None), level
        )
        return {
            "current": level,
            "current_xp": current_xp,
            "next_level_xp": next_cost,
            "jedi_rank": rank_bucket,
            "progression_rank": rank_bucket,
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
            Snapshot dict (total_points, current_level, experience_points,
            jedi_rank + progression_rank alias F43-A3, gamification_level)
            pour réponses API éventuelles.

        Raises:
            InvalidGamificationPointsDeltaError: si delta <= 0
            GamificationUserNotFoundError: si utilisateur absent
        """
        if points_delta <= 0:
            raise InvalidGamificationPointsDeltaError(
                "Le delta de points doit être strictement positif."
            )

        # Verrou ligne (PostgreSQL) pour éviter double attribution en charge parallèle
        # (ex. Gunicorn multi-worker). SQLite (tests CI) ne supporte pas FOR UPDATE :
        # on n'appelle with_for_update que si dialect.name == "postgresql".
        bind = db.get_bind()
        is_postgres = bind.dialect.name == "postgresql"
        query = db.query(User).filter(User.id == user_id)
        if is_postgres:
            query = query.with_for_update()
        user = query.one_or_none()
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
            "progression_rank": new_rank,
            "gamification_level": payload,
        }

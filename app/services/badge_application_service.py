"""
Façade applicative pour les endpoints badges utilisateur/public (LOT 7).

Centralise l'ouverture DB, l'instanciation de BadgeService et l'orchestration
des opérations métier. Les handlers ne font que : parse request, validation
minimale, appel façade, mapping HTTP.
"""

from typing import Any, Dict, List

from app.services.badge_service import BadgeService
from app.utils.db_utils import db_session


class BadgeApplicationService:
    """Façade pour les opérations badge utilisateur/public."""

    @staticmethod
    async def get_user_badges(user_id: int) -> Dict[str, Any]:
        """GET /api/badges/user — badges obtenus + user_stats."""
        async with db_session() as db:
            return BadgeService(db).get_user_badges(user_id)

    @staticmethod
    async def get_available_badges() -> List[Dict[str, Any]]:
        """GET /api/badges/available — liste des badges disponibles."""
        async with db_session() as db:
            return BadgeService(db).get_available_badges()

    @staticmethod
    async def check_and_award_badges(user_id: int) -> List[Dict[str, Any]]:
        """POST /api/badges/check — vérification et attribution des badges mérités."""
        async with db_session() as db:
            return BadgeService(db).check_and_award_badges(user_id)

    @staticmethod
    async def get_user_gamification_stats(user_id: int) -> Dict[str, Any]:
        """GET /api/badges/stats — statistiques de gamification (sans cache)."""
        async with db_session() as db:
            return BadgeService(db).get_user_gamification_stats(user_id)

    @staticmethod
    async def set_pinned_badges(user_id: int, badge_ids: List[int]) -> List[int]:
        """PATCH /api/badges/pin — épingler 1-3 badges parmi ceux obtenus."""
        async with db_session() as db:
            return BadgeService(db).set_pinned_badges(user_id, badge_ids)

    @staticmethod
    async def get_badges_rarity_stats() -> Dict[str, Any]:
        """GET /api/badges/rarity — stats rareté par badge (sans cache)."""
        async with db_session() as db:
            return BadgeService(db).get_badges_rarity_stats()

    @staticmethod
    async def get_badges_progress(user_id: int) -> Dict[str, Any]:
        """GET /api/challenges/badges/progress — progression vers les badges."""
        async with db_session() as db:
            return BadgeService(db).get_badges_progress(user_id)

"""
Façade applicative pour les endpoints badges utilisateur/public (LOT 7).

Centralise l'ouverture DB, l'instanciation de BadgeService et l'orchestration
des opérations métier. Les handlers ne font que : parse request, validation
minimale, appel façade via run_db_bound, mapping HTTP.

LOT A6 : sync + sync_db_session, exécuté via run_db_bound() depuis les handlers.
LOT B2 : contrats explicites (PinBadgesResult) pour set_pinned_badges.
"""

from typing import Any, Dict, List

from app.schemas.badge import PinBadgesResult
from app.services.badge_service import BadgeService
from app.utils.db_utils import sync_db_session


class BadgeApplicationService:
    """Façade pour les opérations badge utilisateur/public."""

    @staticmethod
    def get_user_badges(user_id: int) -> Dict[str, Any]:
        """GET /api/badges/user — badges obtenus + user_stats."""
        with sync_db_session() as db:
            return BadgeService(db).get_user_badges(user_id)

    @staticmethod
    def get_available_badges() -> List[Dict[str, Any]]:
        """GET /api/badges/available — liste des badges disponibles."""
        with sync_db_session() as db:
            return BadgeService(db).get_available_badges()

    @staticmethod
    def check_and_award_badges(user_id: int) -> List[Dict[str, Any]]:
        """POST /api/badges/check — vérification et attribution des badges mérités."""
        with sync_db_session() as db:
            return BadgeService(db).check_and_award_badges(user_id)

    @staticmethod
    def get_user_gamification_stats(user_id: int) -> Dict[str, Any]:
        """GET /api/badges/stats — statistiques de gamification (sans cache)."""
        with sync_db_session() as db:
            return BadgeService(db).get_user_gamification_stats(user_id)

    @staticmethod
    def set_pinned_badges(user_id: int, badge_ids: List[int]) -> PinBadgesResult:
        """PATCH /api/badges/pin — épingler 1-3 badges parmi ceux obtenus."""
        with sync_db_session() as db:
            pinned = BadgeService(db).set_pinned_badges(user_id, badge_ids)
            return PinBadgesResult(pinned_badge_ids=pinned)

    @staticmethod
    def get_badges_rarity_stats() -> Dict[str, Any]:
        """GET /api/badges/rarity — stats rareté par badge (sans cache)."""
        with sync_db_session() as db:
            return BadgeService(db).get_badges_rarity_stats()

    @staticmethod
    def get_badges_progress(user_id: int) -> Dict[str, Any]:
        """GET /api/challenges/badges/progress — progression vers les badges."""
        with sync_db_session() as db:
            return BadgeService(db).get_badges_progress(user_id)

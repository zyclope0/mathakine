"""
Service de gestion des badges et achievements pour Mathakine (B3.1 facade).

Délègue aux sous-services par responsabilité :
- badge_user_view_service : earned, available, gamification stats, pinned
- badge_award_service : check_and_award_badges
- badge_progress_service : get_badges_progress, get_closest_progress_notification
- badge_rarity_service : get_badges_rarity_stats
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.services.badge_award_service import BadgeAwardService
from app.services.badge_progress_service import (
    get_badges_progress as _get_badges_progress,
)
from app.services.badge_progress_service import (
    get_closest_progress_notification as _get_closest_progress_notification,
)
from app.services.badge_rarity_service import get_badges_rarity_stats as _get_rarity
from app.services.badge_user_view_service import (
    get_available_badges as _get_available_badges,
)
from app.services.badge_user_view_service import get_user_badges as _get_user_badges
from app.services.badge_user_view_service import (
    get_user_gamification_stats as _get_user_gamification_stats,
)
from app.services.badge_user_view_service import set_pinned_badges as _set_pinned_badges


class BadgeService:
    """Facade pour la gestion des badges et achievements."""

    def __init__(self, db: Session, *, auto_commit: bool = True):
        self.db = db
        self.auto_commit = auto_commit

    def get_user_badges(self, user_id: int) -> Dict[str, Any]:
        """Récupérer tous les badges d'un utilisateur."""
        return _get_user_badges(self.db, user_id)

    def get_available_badges(self) -> List[Dict[str, Any]]:
        """Récupérer tous les badges disponibles."""
        return _get_available_badges(self.db)

    def check_and_award_badges(
        self, user_id: int, attempt_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Vérifier et attribuer les badges mérités par un utilisateur."""
        return BadgeAwardService(
            self.db, auto_commit=self.auto_commit
        ).check_and_award_badges(user_id, attempt_data)

    def get_user_gamification_stats(self, user_id: int) -> Dict[str, Any]:
        """Statistiques gamification (attempts, badges par catégorie, performance)."""
        return _get_user_gamification_stats(self.db, user_id)

    def set_pinned_badges(self, user_id: int, badge_ids: List[int]) -> List[int]:
        """Épingler 1-3 badges. Seuls les badges obtenus peuvent être épinglés."""
        return _set_pinned_badges(
            self.db, user_id, badge_ids, auto_commit=self.auto_commit
        )

    def get_badges_progress(self, user_id: int) -> Dict[str, Any]:
        """Progression vers les badges (unlocked + in_progress)."""
        return _get_badges_progress(self.db, user_id)

    def get_closest_progress_notification(
        self, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Badge le plus proche du déblocage (progress >= 0.5)."""
        return _get_closest_progress_notification(self.db, user_id)

    def get_badges_rarity_stats(self) -> Dict[str, Any]:
        """Stats rareté par badge : unlock_count, unlock_percent, rarity_label."""
        return _get_rarity(self.db)

"""
Mise à jour gamification utilisateur après attribution de badges (B3.2).

Délègue au moteur unique ``GamificationService.apply_points`` + ledger.
"""

from typing import Any, Callable, Dict, List

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.services.gamification.exceptions import (
    GamificationError,
)
from app.services.gamification.gamification_service import GamificationService
from app.services.gamification.point_source import PointEventSourceType

logger = get_logger(__name__)


def update_user_gamification(
    db: Session,
    user_id: int,
    new_badges: List[Dict[str, Any]],
    *,
    flush_fn: Callable[[], None],
    rollback_fn: Callable[[], None],
    auto_commit: bool = True,
) -> None:
    """
    Pour chaque badge nouvellement attribué avec points > 0, applique le delta via le moteur unique.
    """
    try:
        for badge in new_badges:
            pts = int(badge.get("points_reward") or 0)
            if pts <= 0:
                continue
            GamificationService.apply_points(
                db,
                user_id,
                pts,
                PointEventSourceType.BADGE_AWARDED,
                source_id=badge.get("id"),
                details={
                    "code": badge.get("code"),
                    "name": badge.get("name"),
                },
            )
        flush_fn()
    except GamificationError as gamification_update_error:
        if not auto_commit:
            raise
        rollback_fn()
        logger.error(
            "Erreur domaine gamification (badges) user=%s: %s",
            user_id,
            gamification_update_error,
        )
    except Exception as gamification_update_error:
        if not auto_commit:
            raise
        rollback_fn()
        logger.error(
            "Erreur mise à jour gamification pour l'utilisateur %s: %s",
            user_id,
            gamification_update_error,
        )

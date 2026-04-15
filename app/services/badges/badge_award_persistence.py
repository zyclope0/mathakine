"""
Persistance de l'attribution des badges (B3.2).

Création de UserAchievement et flush/commit. Ne gère pas la gamification.
"""

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.achievement import Achievement, UserAchievement

logger = get_logger(__name__)


def award_badge(
    db: Session,
    user_id: int,
    badge: Achievement,
    *,
    flush_fn: Callable[[], None],
    rollback_fn: Callable[[], None],
    auto_commit: bool = True,
) -> Optional[Dict[str, Any]]:
    """Créer UserAchievement et retourner le dict badge pour l'API."""
    try:
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=badge.id,
            earned_at=datetime.now(timezone.utc),
            is_displayed=True,
        )
        db.add(user_achievement)
        flush_fn()
        return {
            "id": badge.id,
            "code": badge.code,
            "name": badge.name,
            "description": badge.description,
            "thematic_title": badge.star_wars_title,
            "star_wars_title": badge.star_wars_title,
            "difficulty": badge.difficulty,
            "points_reward": badge.points_reward,
            "earned_at": user_achievement.earned_at.isoformat(),
        }
    except SQLAlchemyError as badge_award_error:
        if not auto_commit:
            raise
        rollback_fn()
        logger.error(
            "Erreur lors de l'attribution du badge %s: %s",
            badge.code,
            badge_award_error,
        )
        return None

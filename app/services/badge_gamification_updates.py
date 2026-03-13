"""
Mise à jour gamification utilisateur après attribution de badges (B3.2).

Points, niveau, experience_points, jedi_rank.
"""

from typing import Any, Callable, Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.services.user_service import UserService

logger = get_logger(__name__)


def calculate_jedi_rank(level: int) -> str:
    """Calculer le rang Jedi basé sur le niveau."""
    if level < 5:
        return "youngling"
    elif level < 15:
        return "padawan"
    elif level < 30:
        return "knight"
    elif level < 50:
        return "master"
    else:
        return "grand_master"


def update_user_gamification(
    db: Session,
    user_id: int,
    new_badges: List[Dict[str, Any]],
    *,
    flush_fn: Callable[[], None],
    rollback_fn: Callable[[], None],
    auto_commit: bool = True,
) -> None:
    """Mettre à jour total_points, current_level, experience_points, jedi_rank."""
    try:
        total_points_gained = sum(badge["points_reward"] for badge in new_badges)
        user = UserService.get_user(db, user_id)
        if user:
            current_points = getattr(user, "total_points", 0) or 0
            new_total_points = current_points + total_points_gained
            new_level = max(1, new_total_points // 100 + 1)
            jedi_rank = calculate_jedi_rank(new_level)
            db.execute(
                text("""
                UPDATE users
                SET total_points = :total_points,
                    current_level = :current_level,
                    experience_points = :experience_points,
                    jedi_rank = :jedi_rank
                WHERE id = :user_id
            """),
                {
                    "total_points": new_total_points,
                    "current_level": new_level,
                    "experience_points": new_total_points % 100,
                    "jedi_rank": jedi_rank,
                    "user_id": user_id,
                },
            )
            flush_fn()
            logger.info(
                f"Gamification mise à jour pour l'utilisateur {user_id}: "
                f"{total_points_gained} points, niveau {new_level}, rang {jedi_rank}"
            )
    except Exception as gamification_update_error:
        if not auto_commit:
            raise
        rollback_fn()
        logger.error(
            f"Erreur mise à jour gamification pour l'utilisateur {user_id}: "
            f"{gamification_update_error}"
        )

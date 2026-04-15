"""
Stats rareté par badge (B3.1). unlock_count, unlock_percent, rarity_label.
"""

from typing import Any, Dict

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.user import User

logger = get_logger(__name__)


def get_badges_rarity_stats(db: Session) -> Dict[str, Any]:
    """
    Stats rareté par badge : unlock_count, unlock_percent, rarity_label.
    Preuve sociale (« X% ont débloqué »), indicateur rareté.
    """
    try:
        total_users = (
            db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 1
        )
        rows = db.execute(text("""
            SELECT ua.achievement_id, COUNT(DISTINCT ua.user_id) as unlock_count
            FROM user_achievements ua
            JOIN achievements a ON a.id = ua.achievement_id
            WHERE a.is_active = true
            GROUP BY ua.achievement_id
        """)).fetchall()
        by_badge = {}
        for row in rows:
            aid = row[0]
            count = row[1]
            pct = round((count / total_users) * 100, 1) if total_users else 0
            if pct < 5:
                rarity = "rare"
            elif pct < 20:
                rarity = "uncommon"
            else:
                rarity = "common"
            by_badge[str(aid)] = {
                "unlock_count": count,
                "unlock_percent": pct,
                "rarity": rarity,
            }
        return {"total_users": total_users, "by_badge": by_badge}
    except Exception as e:
        logger.error("Erreur get_badges_rarity_stats: %s", e)
        return {"total_users": 0, "by_badge": {}}

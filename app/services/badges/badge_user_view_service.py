"""
Vue utilisateur des badges : earned, available, gamification stats, pinned (B3.1).
"""

from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.achievement import Achievement, UserAchievement
from app.services.badges.badge_format_helpers import format_requirements_to_text
from app.services.users.user_service import UserService

logger = get_logger(__name__)


def get_user_badges(db: Session, user_id: int) -> Dict[str, Any]:
    """Récupérer tous les badges d'un utilisateur."""
    try:
        earned_badges = db.execute(
            text("""
                SELECT a.id, a.code, a.name, a.description, a.star_wars_title,
                       a.difficulty, a.points_reward, a.category,
                       ua.earned_at, ua.is_displayed
                FROM achievements a
                JOIN user_achievements ua ON a.id = ua.achievement_id
                WHERE ua.user_id = :user_id
                ORDER BY ua.earned_at DESC
            """),
            {"user_id": user_id},
        ).fetchall()

        user_stats = db.execute(
            text("""
                SELECT total_points, current_level, experience_points, jedi_rank,
                       COALESCE(current_streak, 0), COALESCE(best_streak, 0)
                FROM users
                WHERE id = :user_id
            """),
            {"user_id": user_id},
        ).fetchone()

        pinned: List[int] = []
        try:
            user = UserService.get_user(db, user_id)
            if user and hasattr(user, "pinned_badge_ids") and user.pinned_badge_ids:
                pinned = [
                    int(x) for x in user.pinned_badge_ids if isinstance(x, (int, float))
                ]
        except (SQLAlchemyError, TypeError, ValueError) as e:
            logger.warning(
                f"Fallback pinned_badge_ids: impossible de récupérer pour user_id={user_id} — {e}"
            )
            # pinned reste [] (fallback explicite)

        return {
            "earned_badges": [
                {
                    "id": badge[0],
                    "code": badge[1],
                    "name": badge[2],
                    "description": badge[3],
                    "star_wars_title": badge[4],
                    "difficulty": badge[5],
                    "points_reward": badge[6],
                    "category": badge[7],
                    "earned_at": badge[8].isoformat() if badge[8] else None,
                    "is_displayed": badge[9],
                }
                for badge in earned_badges
            ],
            "user_stats": (
                {
                    "total_points": user_stats[0] if user_stats else 0,
                    "current_level": user_stats[1] if user_stats else 1,
                    "experience_points": user_stats[2] if user_stats else 0,
                    "jedi_rank": user_stats[3] if user_stats else "youngling",
                    "pinned_badge_ids": pinned,
                    "current_streak": (
                        user_stats[4] if user_stats and len(user_stats) > 4 else 0
                    ),
                    "best_streak": (
                        user_stats[5] if user_stats and len(user_stats) > 5 else 0
                    ),
                }
                if user_stats
                else {
                    "total_points": 0,
                    "current_level": 1,
                    "experience_points": 0,
                    "jedi_rank": "youngling",
                    "pinned_badge_ids": [],
                    "current_streak": 0,
                    "best_streak": 0,
                }
            ),
        }

    except SQLAlchemyError as user_badges_error:
        logger.error(
            f"Erreur récupération badges utilisateur {user_id}: {user_badges_error}"
        )
        return {"earned_badges": [], "user_stats": {}}


# Bornes explicites pour le listing public /api/badges/available (D5).
AVAILABLE_BADGES_DEFAULT_LIMIT = 100
AVAILABLE_BADGES_MAX_LIMIT = 200


def get_available_badges(
    db: Session, *, limit: int = AVAILABLE_BADGES_DEFAULT_LIMIT
) -> List[Dict[str, Any]]:
    """Récupérer les badges disponibles, borné par limit (max AVAILABLE_BADGES_MAX_LIMIT)."""
    effective_limit = min(AVAILABLE_BADGES_MAX_LIMIT, max(1, limit))
    try:
        badges = (
            db.query(Achievement)
            .filter(Achievement.is_active == True)
            .order_by(Achievement.category, Achievement.difficulty)
            .limit(effective_limit)
            .all()
        )

        return [
            {
                "id": badge.id,
                "code": badge.code,
                "name": badge.name,
                "description": badge.description,
                "criteria_text": format_requirements_to_text(badge),
                "star_wars_title": badge.star_wars_title,
                "difficulty": badge.difficulty,
                "points_reward": badge.points_reward,
                "category": badge.category,
                "is_secret": badge.is_secret,
                "icon_url": badge.icon_url,
            }
            for badge in badges
        ]

    except SQLAlchemyError as available_badges_error:
        logger.error(
            f"Erreur récupération badges disponibles: {available_badges_error}"
        )
        return []


def get_user_gamification_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Statistiques gamification (attempts, badges par catégorie, performance)."""
    user_data = get_user_badges(db, user_id)
    earned_count = len(user_data.get("earned_badges", []))

    stats = db.execute(
        text("""
            SELECT
                COUNT(*) as total_attempts,
                COUNT(CASE WHEN is_correct THEN 1 END) as correct_attempts,
                AVG(time_spent) as avg_time_spent
            FROM attempts
            WHERE user_id = :user_id
        """),
        {"user_id": user_id},
    ).fetchone()

    badge_stats = db.execute(
        text("""
            SELECT a.category, COUNT(*) as count
            FROM achievements a
            JOIN user_achievements ua ON a.id = ua.achievement_id
            WHERE ua.user_id = :user_id
            GROUP BY a.category
        """),
        {"user_id": user_id},
    ).fetchall()

    by_category = {row[0]: row[1] for row in badge_stats}
    total = stats[0] if stats else 0
    correct = stats[1] if stats else 0
    avg_time = stats[2] if stats and stats[2] is not None else 0

    return {
        "user_stats": user_data.get("user_stats", {}),
        "badges_summary": {
            "total_badges": earned_count,
            "by_category": by_category,
        },
        "performance": {
            "total_attempts": total,
            "correct_attempts": correct,
            "success_rate": round((correct / total * 100) if total > 0 else 0, 1),
            "avg_time_spent": round(avg_time, 2) if avg_time else 0,
        },
    }


def set_pinned_badges(
    db: Session, user_id: int, badge_ids: List[int], *, auto_commit: bool = True
) -> List[int]:
    """Épingler 1-3 badges. Seuls les badges obtenus peuvent être épinglés."""
    MAX_PINNED = 3
    earned_ids = {
        r[0]
        for r in db.query(UserAchievement.achievement_id)
        .filter(UserAchievement.user_id == user_id)
        .all()
    }
    valid = [bid for bid in badge_ids[:MAX_PINNED] if bid in earned_ids]
    valid = list(dict.fromkeys(valid))[:MAX_PINNED]
    try:
        user = UserService.get_user(db, user_id)
        if user:
            user.pinned_badge_ids = valid
            if auto_commit:
                db.commit()
            else:
                db.flush()
    except SQLAlchemyError as e:
        if auto_commit:
            db.rollback()
        logger.error(f"Erreur set_pinned_badges: {e}")
        return []
    return valid

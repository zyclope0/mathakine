"""
Pré-chargement des stats utilisateur pour l'évaluation des badges (B3.1).

Évite les requêtes N+1 dans check_and_award_badges et get_badges_progress.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def build_stats_cache(db: Session, user_id: int) -> Dict[str, Any]:
    """Pré-charge les stats utilisateur pour éviter N+1 dans check_and_award_badges."""
    stats_cache: Dict[str, Any] = {}
    try:
        row = db.execute(
            text(
                "SELECT COUNT(*), COUNT(CASE WHEN is_correct THEN 1 END) FROM attempts WHERE user_id = :uid"
            ),
            {"uid": user_id},
        ).fetchone()
        if row:
            stats_cache["attempts_count"] = row[0] or 0
            stats_cache["attempts_total"] = row[0] or 0
            stats_cache["attempts_correct"] = row[1] or 0
        lca = db.execute(
            text(
                "SELECT COUNT(*) FROM logic_challenge_attempts WHERE user_id = :uid AND is_correct = true"
            ),
            {"uid": user_id},
        ).fetchone()
        if lca:
            stats_cache["logic_correct_count"] = lca[0] or 0
        all_types_rows = db.execute(
            text(
                "SELECT DISTINCT LOWER(exercise_type::text) FROM exercises "
                "WHERE is_active = true AND is_archived = false"
            )
        ).fetchall()
        stats_cache["exercise_types"] = [str(r[0]).lower() for r in all_types_rows]
        per_type = db.execute(
            text("""
                SELECT LOWER(e.exercise_type::text), COUNT(*)
                FROM attempts a JOIN exercises e ON a.exercise_id = e.id
                WHERE a.user_id = :uid AND a.is_correct = true
                GROUP BY LOWER(e.exercise_type::text)
            """),
            {"uid": user_id},
        ).fetchall()
        stats_cache["per_type_correct"] = {str(r[0]).lower(): r[1] for r in per_type}
        user_types_rows = db.execute(
            text("""
                SELECT DISTINCT LOWER(e.exercise_type::text) FROM attempts a
                JOIN exercises e ON a.exercise_id = e.id WHERE a.user_id = :uid
            """),
            {"uid": user_id},
        ).fetchall()
        stats_cache["user_exercise_types"] = {
            str(r[0]).lower() for r in user_types_rows
        }
        days_rows = db.execute(
            text("""
                SELECT DISTINCT DATE(created_at) as day FROM attempts
                WHERE user_id = :uid ORDER BY day DESC LIMIT 35
            """),
            {"uid": user_id},
        ).fetchall()
        stats_cache["activity_dates"] = [
            r[0] if hasattr(r, "__getitem__") else r.day for r in days_rows
        ]
        min_time = db.execute(
            text(
                "SELECT MIN(time_spent) FROM attempts WHERE user_id = :uid AND is_correct = true"
            ),
            {"uid": user_id},
        ).fetchone()
        stats_cache["min_fast_time"] = (
            float(min_time[0]) if min_time and min_time[0] is not None else None
        )
        today = datetime.now(timezone.utc).date()
        pd_row = db.execute(
            text("""
                SELECT COUNT(*) as total, COUNT(CASE WHEN is_correct THEN 1 END) as correct
                FROM attempts WHERE user_id = :uid AND DATE(created_at) = :today
            """),
            {"uid": user_id, "today": today},
        ).fetchone()
        stats_cache["perfect_day_today"] = (
            (pd_row[0] or 0, pd_row[1] or 0) if pd_row else (0, 0)
        )
        all_streak_rows = db.execute(
            text("""
                SELECT LOWER(e.exercise_type::text) as ex_type, a.is_correct
                FROM attempts a
                JOIN exercises e ON a.exercise_id = e.id
                WHERE a.user_id = :uid
                ORDER BY a.created_at DESC
                LIMIT 500
            """),
            {"uid": user_id},
        ).fetchall()
        if "consecutive_by_type" not in stats_cache:
            stats_cache["consecutive_by_type"] = {}
        for ex_t in stats_cache.get("exercise_types", []):
            streak = 0
            for row in all_streak_rows:
                if str(row[0]).lower() == ex_t:
                    if row[1]:
                        streak += 1
                    else:
                        break
            stats_cache["consecutive_by_type"][ex_t] = streak
    except (SQLAlchemyError, TypeError, ValueError):
        pass
    return stats_cache

"""
Service F07 — Courbe d'évolution temporelle (timeline progression).

Agrège les tentatives d'exercices par jour (UTC date-only) pour un utilisateur.
Remplit les jours vides avec attempts=0, success_rate_pct=0, avg_time_spent_s=null.
"""

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


VALID_PERIODS = frozenset({"7d", "30d"})
DEFAULT_PERIOD = "7d"


def get_progress_timeline(
    db: Session,
    user_id: int,
    period: str = "7d",
    *,
    now_fn: Optional[Callable[[], datetime]] = None,
) -> Dict[str, Any]:
    """
    Retourne la timeline de progression par jour pour un utilisateur.

    Args:
        db: Session SQLAlchemy
        user_id: ID de l'utilisateur
        period: "7d" ou "30d" (fallback 7d si invalide)

    Returns:
        Dict avec period, from, to, points[], summary
    """
    if period not in VALID_PERIODS:
        period = DEFAULT_PERIOD

    days = 7 if period == "7d" else 30
    now = (now_fn or (lambda: datetime.now(timezone.utc)))()
    to_date = now.date()
    from_date = to_date - timedelta(days=days - 1)

    # Récupérer les agrégats par jour (date UTC, date-only)
    result = db.execute(
        text("""
            SELECT
                (a.created_at AT TIME ZONE 'UTC')::date as day_date,
                COUNT(*) as attempts,
                SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) as correct,
                AVG(a.time_spent) FILTER (WHERE a.time_spent IS NOT NULL AND a.time_spent >= 0) as avg_time
            FROM attempts a
            JOIN exercises e ON e.id = a.exercise_id
            WHERE a.user_id = :user_id
              AND a.created_at >= :from_ts
              AND a.created_at < :to_ts_plus_one
            GROUP BY (a.created_at AT TIME ZONE 'UTC')::date
            ORDER BY day_date
        """),
        {
            "user_id": user_id,
            "from_ts": datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc),
            "to_ts_plus_one": datetime.combine(
                to_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc
            ),
        },
    )
    rows_by_day: Dict[date, Dict[str, Any]] = {}
    for row in result.fetchall():
        day_date = row[0]
        if isinstance(day_date, datetime):
            day_date = day_date.date()
        rows_by_day[day_date] = {
            "attempts": row[1] or 0,
            "correct": row[2] or 0,
            "avg_time": float(row[3]) if row[3] is not None else None,
        }

    # Récupérer by_type par jour
    by_type_result = db.execute(
        text("""
            SELECT
                (a.created_at AT TIME ZONE 'UTC')::date as day_date,
                LOWER(e.exercise_type::text) as ex_type,
                COUNT(*) as attempts,
                SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) as correct
            FROM attempts a
            JOIN exercises e ON e.id = a.exercise_id
            WHERE a.user_id = :user_id
              AND a.created_at >= :from_ts
              AND a.created_at < :to_ts_plus_one
            GROUP BY (a.created_at AT TIME ZONE 'UTC')::date, LOWER(e.exercise_type::text)
        """),
        {
            "user_id": user_id,
            "from_ts": datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc),
            "to_ts_plus_one": datetime.combine(
                to_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc
            ),
        },
    )
    by_type_by_day: Dict[date, Dict[str, Dict[str, Any]]] = defaultdict(
        lambda: defaultdict(lambda: {"attempts": 0, "correct": 0})
    )
    for row in by_type_result.fetchall():
        day_date = row[0]
        if isinstance(day_date, datetime):
            day_date = day_date.date()
        ex_type = row[1] or "unknown"
        by_type_by_day[day_date][ex_type] = {
            "attempts": row[2] or 0,
            "correct": row[3] or 0,
        }

    # Construire la série continue (sans trou)
    points: List[Dict[str, Any]] = []
    total_attempts = 0
    total_correct = 0

    current = from_date
    while current <= to_date:
        day_data = rows_by_day.get(current, {"attempts": 0, "correct": 0, "avg_time": None})
        attempts = day_data["attempts"]
        correct = day_data["correct"]
        avg_time = day_data.get("avg_time")

        success_rate_pct = round((correct / attempts) * 100, 1) if attempts > 0 else 0.0
        avg_time_spent_s = round(avg_time, 1) if avg_time is not None else None

        by_type: Dict[str, Dict[str, Any]] = {}
        for ex_type, data in by_type_by_day.get(current, {}).items():
            a, c = data["attempts"], data["correct"]
            by_type[ex_type] = {
                "attempts": a,
                "correct": c,
                "success_rate_pct": round((c / a) * 100, 1) if a > 0 else 0.0,
            }

        points.append(
            {
                "date": current.strftime("%Y-%m-%d"),
                "attempts": attempts,
                "correct": correct,
                "success_rate_pct": success_rate_pct,
                "avg_time_spent_s": avg_time_spent_s,
                "by_type": by_type,
            }
        )
        total_attempts += attempts
        total_correct += correct
        current += timedelta(days=1)

    overall_success_rate_pct = (
        round((total_correct / total_attempts) * 100, 1) if total_attempts > 0 else 0.0
    )

    return {
        "period": period,
        "from": from_date.strftime("%Y-%m-%d"),
        "to": to_date.strftime("%Y-%m-%d"),
        "points": points,
        "summary": {
            "total_attempts": total_attempts,
            "total_correct": total_correct,
            "overall_success_rate_pct": overall_success_rate_pct,
        },
    }

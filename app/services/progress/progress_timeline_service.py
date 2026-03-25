"""
Service F07 — Courbe d'évolution temporelle (timeline progression).

Agrège les tentatives d'exercices et de défis logiques par jour (UTC date-only).
Remplit les jours vides avec attempts=0, success_rate_pct=0, avg_time_spent_s=null.
"""

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

VALID_PERIODS = frozenset({"7d", "30d"})
DEFAULT_PERIOD = "7d"


def _to_int(value: Any) -> int:
    """Agrégats SQL (PostgreSQL) peuvent renvoyer Decimal — JSON exige int natif."""
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return int(value)
    return int(value)


def _to_float_optional(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


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

    _range_params = {
        "user_id": user_id,
        "from_ts": datetime.combine(
            from_date, datetime.min.time(), tzinfo=timezone.utc
        ),
        "to_ts_plus_one": datetime.combine(
            to_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc
        ),
    }

    # Agrégats par jour : exercices UNION ALL défis logiques, puis somme par jour
    result = db.execute(
        text("""
            SELECT u.day_date,
                   SUM(u.attempts) AS attempts,
                   SUM(u.correct) AS correct,
                   CASE
                       WHEN SUM(u.attempts_with_time) > 0
                       THEN SUM(u.time_sum) / SUM(u.attempts_with_time)::float
                       ELSE NULL
                   END AS avg_time
            FROM (
                SELECT
                    (a.created_at AT TIME ZONE 'UTC')::date AS day_date,
                    COUNT(*)::bigint AS attempts,
                    SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END)::bigint AS correct,
                    COALESCE(
                        SUM(a.time_spent) FILTER (
                            WHERE a.time_spent IS NOT NULL AND a.time_spent >= 0
                        ),
                        0.0
                    ) AS time_sum,
                    COUNT(*) FILTER (
                        WHERE a.time_spent IS NOT NULL AND a.time_spent >= 0
                    )::bigint AS attempts_with_time
                FROM attempts a
                JOIN exercises e ON e.id = a.exercise_id
                WHERE a.user_id = :user_id
                  AND a.created_at >= :from_ts
                  AND a.created_at < :to_ts_plus_one
                GROUP BY (a.created_at AT TIME ZONE 'UTC')::date
                UNION ALL
                SELECT
                    (lca.created_at AT TIME ZONE 'UTC')::date AS day_date,
                    COUNT(*)::bigint,
                    SUM(CASE WHEN lca.is_correct THEN 1 ELSE 0 END)::bigint,
                    COALESCE(
                        SUM(lca.time_spent) FILTER (
                            WHERE lca.time_spent IS NOT NULL
                              AND lca.time_spent >= 0
                        ),
                        0.0
                    ),
                    COUNT(*) FILTER (
                        WHERE lca.time_spent IS NOT NULL AND lca.time_spent >= 0
                    )::bigint
                FROM logic_challenge_attempts lca
                WHERE lca.user_id = :user_id
                  AND lca.created_at >= :from_ts
                  AND lca.created_at < :to_ts_plus_one
                GROUP BY (lca.created_at AT TIME ZONE 'UTC')::date
            ) u
            GROUP BY u.day_date
            ORDER BY u.day_date
        """),
        _range_params,
    )
    rows_by_day: Dict[date, Dict[str, Any]] = {}
    for row in result.fetchall():
        day_date = row[0]
        if isinstance(day_date, datetime):
            day_date = day_date.date()
        rows_by_day[day_date] = {
            "attempts": _to_int(row[1]),
            "correct": _to_int(row[2]),
            "avg_time": _to_float_optional(row[3]),
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
        _range_params,
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
            "attempts": _to_int(row[2]),
            "correct": _to_int(row[3]),
        }

    ch_by_type_result = db.execute(
        text("""
            SELECT
                (lca.created_at AT TIME ZONE 'UTC')::date as day_date,
                LOWER(lc.challenge_type::text) as ch_type,
                COUNT(*) as attempts,
                SUM(CASE WHEN lca.is_correct THEN 1 ELSE 0 END) as correct
            FROM logic_challenge_attempts lca
            JOIN logic_challenges lc ON lc.id = lca.challenge_id
            WHERE lca.user_id = :user_id
              AND lca.created_at >= :from_ts
              AND lca.created_at < :to_ts_plus_one
            GROUP BY (lca.created_at AT TIME ZONE 'UTC')::date,
                     LOWER(lc.challenge_type::text)
        """),
        _range_params,
    )
    for row in ch_by_type_result.fetchall():
        day_date = row[0]
        if isinstance(day_date, datetime):
            day_date = day_date.date()
        raw_type = (row[1] or "unknown").strip().lower()
        logic_key = f"logic_{raw_type}"
        prev = by_type_by_day[day_date].get(logic_key, {"attempts": 0, "correct": 0})
        by_type_by_day[day_date][logic_key] = {
            "attempts": _to_int(prev["attempts"]) + _to_int(row[2]),
            "correct": _to_int(prev["correct"]) + _to_int(row[3]),
        }

    # Construire la série continue (sans trou)
    points: List[Dict[str, Any]] = []
    total_attempts = 0
    total_correct = 0

    current = from_date
    while current <= to_date:
        day_data = rows_by_day.get(
            current, {"attempts": 0, "correct": 0, "avg_time": None}
        )
        attempts = _to_int(day_data["attempts"])
        correct = _to_int(day_data["correct"])
        avg_time = _to_float_optional(day_data.get("avg_time"))

        success_rate_pct = round((correct / attempts) * 100, 1) if attempts > 0 else 0.0
        avg_time_spent_s = round(avg_time, 1) if avg_time is not None else None

        by_type: Dict[str, Dict[str, Any]] = {}
        for ex_type, data in by_type_by_day.get(current, {}).items():
            a = _to_int(data["attempts"])
            c = _to_int(data["correct"])
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

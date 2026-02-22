"""
Moteur générique de vérification des badges — Lot C.

Registry de checkers par type de requirements.
Prépare le terrain pour B5 (défis logiques, mixte exercices+défis).

Types supportés:
- attempts_count
- success_rate (min_attempts + success_rate)
- consecutive (exercise_type + consecutive_correct)
- max_time
- consecutive_days
- perfect_day
- all_types (explorer)
- min_per_type (versatile)
- logic_attempts_count (B5)
- mixte (attempts_count + logic_attempts_count) (B5)
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.achievement import Achievement
from app.models.attempt import Attempt

logger = get_logger(__name__)

# Type: Callable[[Session, int, dict, Optional[dict], Optional[dict]], bool]
CheckerFn = Callable[
    [Session, int, Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]], bool
]


def _check_attempts_count(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    _attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie count(attempts) >= attempts_count."""
    target = req.get("attempts_count")
    if target is None:
        return False
    if stats_cache is not None and "attempts_count" in stats_cache:
        count = stats_cache["attempts_count"]
    else:
        count = db.query(func.count(Attempt.id)).filter(Attempt.user_id == user_id).scalar() or 0
    return count >= int(target)


def _check_logic_attempts_count(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    _attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie count(logic_challenge_attempts corrects) >= logic_attempts_count. B5."""
    from app.models.logic_challenge import LogicChallengeAttempt

    target = req.get("logic_attempts_count")
    if target is None:
        return False
    if stats_cache is not None and "logic_correct_count" in stats_cache:
        count = stats_cache["logic_correct_count"]
    else:
        count = (
            db.query(func.count(LogicChallengeAttempt.id))
            .filter(
                LogicChallengeAttempt.user_id == user_id,
                LogicChallengeAttempt.is_correct == True,
            )
            .scalar()
            or 0
        )
    return count >= int(target)


def _check_mixte(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    _attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie attempts_count ET logic_attempts_count. B5."""
    return _check_attempts_count(db, user_id, req, _attempt_data, stats_cache) and _check_logic_attempts_count(
        db, user_id, req, _attempt_data, stats_cache
    )


def _check_success_rate(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    _attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie min_attempts atteint ET success_rate >= taux."""
    target = req.get("min_attempts")
    rate = req.get("success_rate")
    if target is None or rate is None:
        return False
    if stats_cache is not None and "attempts_total" in stats_cache and "attempts_correct" in stats_cache:
        total, correct = stats_cache["attempts_total"], stats_cache["attempts_correct"]
    else:
        stats = db.execute(
            text("""
                SELECT COUNT(*) as total, COUNT(CASE WHEN is_correct THEN 1 END) as correct
                FROM attempts WHERE user_id = :user_id
            """),
            {"user_id": user_id},
        ).fetchone()
        total = stats[0] if stats else 0
        correct = stats[1] if stats else 0
    if total < int(target):
        return False
    success_pct = (correct / total * 100) if total else 0
    return success_pct >= float(rate)


def _check_consecutive(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    _attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie série consécutive de succès pour un type d'exercice."""
    ex_type = str(req.get("exercise_type", "addition")).lower()
    required = req.get("consecutive_correct")
    if required is None:
        return False
    if stats_cache is not None and "consecutive_by_type" in stats_cache and ex_type in stats_cache["consecutive_by_type"]:
        streak = stats_cache["consecutive_by_type"][ex_type]
        return streak >= int(required)
    rows = db.execute(
        text("""
            SELECT a.is_correct
            FROM attempts a
            JOIN exercises e ON a.exercise_id = e.id
            WHERE a.user_id = :user_id AND LOWER(e.exercise_type::text) = LOWER(:ex_type)
            ORDER BY a.created_at DESC
            LIMIT :limit
        """),
        {"user_id": user_id, "ex_type": ex_type, "limit": int(required) * 2},
    ).fetchall()
    if len(rows) < int(required):
        return False
    streak = 0
    for r in rows:
        if r[0]:
            streak += 1
            if streak >= int(required):
                return True
        else:
            break
    return False


def _check_max_time(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie au moins une tentative correcte en moins de max_time secondes."""
    max_t = req.get("max_time")
    if max_t is None:
        return False
    max_t = float(max_t)
    if attempt_data and attempt_data.get("time_spent", float("inf")) <= max_t:
        return True
    if stats_cache is not None and "min_fast_time" in stats_cache:
        min_t = stats_cache["min_fast_time"]
        return min_t is not None and min_t <= max_t
    fast = (
        db.query(Attempt)
        .filter(
            Attempt.user_id == user_id,
            Attempt.is_correct == True,
            Attempt.time_spent <= max_t,
        )
        .first()
    )
    return fast is not None


def _check_consecutive_days(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    _attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie X jours consécutifs d'activité (exercices)."""
    days = req.get("consecutive_days")
    if days is None:
        return False
    days = int(days)
    if stats_cache is not None and "activity_dates" in stats_cache:
        rows = [(d,) for d in stats_cache["activity_dates"][: days + 1]]
    else:
        rows = db.execute(
            text("""
                SELECT DISTINCT DATE(created_at) as day
                FROM attempts
                WHERE user_id = :user_id
                ORDER BY day DESC
                LIMIT :limit
            """),
            {"user_id": user_id, "limit": days + 1},
        ).fetchall()
    if len(rows) < days:
        return False
    today = datetime.now(timezone.utc).date()
    count = 0
    for i, r in enumerate(rows):
        d = r[0] if hasattr(r, "__getitem__") else r.day
        if d == today - timedelta(days=i):
            count += 1
        else:
            break
    return count >= days


def _check_perfect_day(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    _attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie journée parfaite : tous les exercices du jour réussis, au moins 3."""
    if stats_cache is not None and "perfect_day_today" in stats_cache:
        total, correct = stats_cache["perfect_day_today"]
    else:
        today = datetime.now(timezone.utc).date()
        row = db.execute(
            text("""
                SELECT COUNT(*) as total, COUNT(CASE WHEN is_correct THEN 1 END) as correct
                FROM attempts
                WHERE user_id = :user_id AND DATE(created_at) = :today
            """),
            {"user_id": user_id, "today": today},
        ).fetchone()
        total = row[0] if row else 0
        correct = row[1] if row else 0
    if total < 3:
        return False
    return total == correct


def _check_all_types(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    _attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie que l'utilisateur a essayé tous les types d'exercices."""
    if stats_cache is not None and "exercise_types" in stats_cache and "user_exercise_types" in stats_cache:
        all_set = set(stats_cache["exercise_types"])
        user_set = stats_cache["user_exercise_types"]
        return all_set.issubset(user_set)
    all_types = db.execute(
        text("SELECT DISTINCT exercise_type FROM exercises WHERE is_active = true AND is_archived = false")
    ).fetchall()
    if not all_types:
        return False
    all_set = {str(r[0]).lower() for r in all_types}
    user_types = db.execute(
        text("""
            SELECT DISTINCT LOWER(e.exercise_type::text)
            FROM attempts a
            JOIN exercises e ON a.exercise_id = e.id
            WHERE a.user_id = :user_id
        """),
        {"user_id": user_id},
    ).fetchall()
    user_set = {str(r[0]).lower() for r in user_types}
    return all_set.issubset(user_set)


def _check_comeback(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie si l'utilisateur revient après X jours sans activité (loss aversion)."""
    days = req.get("comeback_days")
    if days is None or attempt_data is None:
        return False
    days = int(days)
    created_str = attempt_data.get("created_at")
    if not created_str:
        return False
    try:
        current_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return False
    # Dernière tentative AVANT celle-ci
    prev = (
        db.query(Attempt)
        .filter(Attempt.user_id == user_id, Attempt.created_at < current_dt)
        .order_by(Attempt.created_at.desc())
        .first()
    )
    if not prev or not prev.created_at:
        return False
    delta = (current_dt - prev.created_at).days if hasattr(current_dt, "__sub__") else 0
    return delta >= days


def _check_min_per_type(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    _attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie au moins X exercices réussis par type."""
    min_count = req.get("min_per_type", req.get("min_count", 5))
    min_count = int(min_count)
    if stats_cache is not None and "exercise_types" in stats_cache and "per_type_correct" in stats_cache:
        types_list = stats_cache["exercise_types"]
        per_type = stats_cache["per_type_correct"]
        for ex_type in types_list:
            if per_type.get(ex_type, 0) < min_count:
                return False
        return True
    all_types = db.execute(
        text("SELECT DISTINCT exercise_type FROM exercises WHERE is_active = true AND is_archived = false")
    ).fetchall()
    if not all_types:
        return False
    for r in all_types:
        ex_type = str(r[0])
        cnt = db.execute(
            text("""
                SELECT COUNT(*)
                FROM attempts a
                JOIN exercises e ON a.exercise_id = e.id
                WHERE a.user_id = :user_id AND LOWER(e.exercise_type::text) = LOWER(:ex_type)
                AND a.is_correct = true
            """),
            {"user_id": user_id, "ex_type": ex_type},
        ).fetchone()
        if not cnt or cnt[0] < min_count:
            return False
    return True


# Ordre de détection : mixte en premier (clés les plus spécifiques), puis les autres
CHECKERS: Dict[str, CheckerFn] = {
    "comeback": _check_comeback,
    "mixte": _check_mixte,
    "logic_attempts_count": _check_logic_attempts_count,
    "attempts_count": _check_attempts_count,
    "success_rate": _check_success_rate,
    "consecutive": _check_consecutive,
    "max_time": _check_max_time,
    "consecutive_days": _check_consecutive_days,
    "perfect_day": _check_perfect_day,
    "all_types": _check_all_types,
    "min_per_type": _check_min_per_type,
}


def detect_requirement_type(req: Dict[str, Any]) -> Optional[str]:
    """
    Détecte le type de requirement à partir des clés JSON.
    Retourne None si le schéma n'est pas reconnu (fallback code).
    """
    if not req or not isinstance(req, dict):
        return None
    keys = set(k for k in req if req[k] is not None)

    # Mixte : attempts_count + logic_attempts_count
    if "attempts_count" in keys and "logic_attempts_count" in keys:
        return "mixte"

    # logic_attempts_count seul
    if "logic_attempts_count" in keys:
        return "logic_attempts_count"

    # attempts_count seul (pas de consecutive_correct, etc.)
    if "attempts_count" in keys and "consecutive_correct" not in keys and "success_rate" not in keys:
        return "attempts_count"

    # success_rate
    if "min_attempts" in keys and "success_rate" in keys:
        return "success_rate"

    # consecutive
    if "exercise_type" in keys or "consecutive_correct" in keys:
        return "consecutive"

    # max_time
    if "max_time" in keys:
        return "max_time"

    # consecutive_days
    if "consecutive_days" in keys:
        return "consecutive_days"

    # perfect_day
    if "perfect_day" in keys or keys == {"perfect_day"}:
        return "perfect_day"

    # all_types
    if "all_types" in keys:
        return "all_types"

    # min_per_type
    if "min_per_type" in keys or "min_count" in keys:
        return "min_per_type"

    # comeback_days
    if "comeback_days" in keys:
        return "comeback"

    return None


def check_requirements(
    db: Session,
    user_id: int,
    requirements: Dict[str, Any],
    attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> Optional[bool]:
    """
    Vérifie si l'utilisateur remplit les requirements.
    stats_cache: pré-fetch pour éviter N+1 quand appelé en boucle (check_and_award_badges).
    Retourne True/False si le type est reconnu, None pour fallback code.
    """
    req_type = detect_requirement_type(requirements)
    if req_type is None:
        return None
    checker = CHECKERS.get(req_type)
    if not checker:
        return None
    try:
        return checker(db, user_id, requirements, attempt_data, stats_cache)
    except Exception as e:
        logger.error(f"Erreur checker {req_type}: {e}")
        return False


# --- Progress getters (Lot C-2) ---
# Type: Callable[[Session, int, Dict, Optional[Dict]], Optional[tuple[float, int, int]]]
# stats_cache évite N+1 quand get_badges_progress pré-fetch les stats
ProgressFn = Callable[
    [Session, int, Dict[str, Any], Optional[Dict[str, Any]]], Optional[tuple[float, int, int]]
]


def _progress_attempts_count(
    db: Session, user_id: int, req: Dict[str, Any], cache: Optional[Dict[str, Any]] = None
) -> Optional[tuple[float, int, int]]:
    t = req.get("attempts_count")
    if t is None:
        return None
    t = int(t)
    if cache is not None and "attempts_count" in cache:
        c = cache["attempts_count"]
    else:
        c = db.query(func.count(Attempt.id)).filter(Attempt.user_id == user_id).scalar() or 0
    p = min(1.0, c / max(1, t))
    return (round(p, 2), c, t)


def _progress_logic_attempts_count(
    db: Session, user_id: int, req: Dict[str, Any], cache: Optional[Dict[str, Any]] = None
) -> Optional[tuple[float, int, int]]:
    from app.models.logic_challenge import LogicChallengeAttempt

    t = req.get("logic_attempts_count")
    if t is None:
        return None
    t = int(t)
    if cache is not None and "logic_correct_count" in cache:
        c = cache["logic_correct_count"]
    else:
        c = (
            db.query(func.count(LogicChallengeAttempt.id))
            .filter(LogicChallengeAttempt.user_id == user_id, LogicChallengeAttempt.is_correct == True)
            .scalar()
            or 0
        )
    p = min(1.0, c / max(1, t))
    return (round(p, 2), c, t)


def _progress_mixte(
    db: Session, user_id: int, req: Dict[str, Any], cache: Optional[Dict[str, Any]] = None
) -> Optional[tuple[float, int, int]]:
    p1 = _progress_attempts_count(db, user_id, req, cache)
    p2 = _progress_logic_attempts_count(db, user_id, req, cache)
    if not p1 or not p2:
        return None
    prog1, cur1, tgt1 = p1
    prog2, cur2, tgt2 = p2
    prog = min(prog1, prog2)
    if prog1 <= prog2:
        return (round(prog, 2), cur1, tgt1)
    return (round(prog, 2), cur2, tgt2)


def _progress_success_rate(
    db: Session, user_id: int, req: Dict[str, Any], cache: Optional[Dict[str, Any]] = None
) -> Optional[tuple[float, int, int]]:
    t = req.get("min_attempts")
    rate = req.get("success_rate")
    if t is None or rate is None:
        return None
    t = int(t)
    if cache is not None and "attempts_total" in cache and "attempts_correct" in cache:
        total = cache["attempts_total"]
        correct = cache["attempts_correct"]
    else:
        row = db.execute(
            text("SELECT COUNT(*), COUNT(CASE WHEN is_correct THEN 1 END) FROM attempts WHERE user_id = :user_id"),
            {"user_id": user_id},
        ).fetchone()
        total = row[0] if row else 0
        correct = row[1] if row else 0
    p = min(1.0, total / max(1, t)) if total else 0.0
    if total >= t and (correct / total * 100 >= float(rate) if total else False):
        p = 1.0
    return (round(p, 2), total, t)


def _progress_consecutive(
    db: Session, user_id: int, req: Dict[str, Any], cache: Optional[Dict[str, Any]] = None
) -> Optional[tuple[float, int, int]]:
    ex_type = str(req.get("exercise_type", "addition")).lower()
    t = req.get("consecutive_correct")
    if t is None:
        return None
    t = int(t)
    if cache is not None and "consecutive_by_type" in cache and ex_type in cache["consecutive_by_type"]:
        streak = cache["consecutive_by_type"][ex_type]
    else:
        rows = db.execute(
            text("""
                SELECT a.is_correct FROM attempts a
                JOIN exercises e ON a.exercise_id = e.id
                WHERE a.user_id = :user_id AND LOWER(e.exercise_type::text) = LOWER(:ex_type)
                ORDER BY a.created_at DESC LIMIT :limit
            """),
            {"user_id": user_id, "ex_type": ex_type, "limit": t * 3},
        ).fetchall()
        streak = 0
        for r in rows:
            if r[0]:
                streak += 1
            else:
                break
    p = min(1.0, streak / max(1, t))
    return (round(p, 2), streak, t)


def _progress_consecutive_days(
    db: Session, user_id: int, req: Dict[str, Any], cache: Optional[Dict[str, Any]] = None
) -> Optional[tuple[float, int, int]]:
    t = req.get("consecutive_days")
    if t is None:
        return None
    t = int(t)
    if cache is not None and "activity_dates" in cache:
        rows = [(d,) for d in cache["activity_dates"][: t + 1]]
    else:
        rows = db.execute(
            text("""
                SELECT DISTINCT DATE(created_at) as day FROM attempts
                WHERE user_id = :user_id ORDER BY day DESC LIMIT :limit
            """),
            {"user_id": user_id, "limit": t + 1},
        ).fetchall()
    if not rows:
        return (0.0, 0, t)
    today = datetime.now(timezone.utc).date()
    c = 0
    for i, r in enumerate(rows):
        d = r[0] if hasattr(r, "__getitem__") else r.day
        if d == today - timedelta(days=i):
            c += 1
        else:
            break
    p = min(1.0, c / max(1, t))
    return (round(p, 2), c, t)


def _progress_max_time(
    db: Session, user_id: int, req: Dict[str, Any], cache: Optional[Dict[str, Any]] = None
) -> Optional[tuple[float, int, int]]:
    max_t = req.get("max_time")
    if max_t is None:
        return None
    max_t = float(max_t)
    if cache is not None and "min_fast_time" in cache:
        has_fast = cache["min_fast_time"] is not None and cache["min_fast_time"] <= max_t
    else:
        fast = (
            db.query(Attempt)
            .filter(Attempt.user_id == user_id, Attempt.is_correct == True, Attempt.time_spent <= max_t)
            .first()
        )
        has_fast = fast is not None
    return (1.0, 1, 1) if has_fast else (0.0, 0, 1)


def _progress_perfect_day(
    db: Session, user_id: int, req: Dict[str, Any], cache: Optional[Dict[str, Any]] = None
) -> Optional[tuple[float, int, int]]:
    if cache is not None and "perfect_day_today" in cache:
        total, correct = cache["perfect_day_today"]
    else:
        today = datetime.now(timezone.utc).date()
        row = db.execute(
            text("""
                SELECT COUNT(*) as total, COUNT(CASE WHEN is_correct THEN 1 END) as correct
                FROM attempts WHERE user_id = :user_id AND DATE(created_at) = :today
            """),
            {"user_id": user_id, "today": today},
        ).fetchone()
        total = row[0] if row else 0
        correct = row[1] if row else 0
    if total < 3:
        return (0.0, 0, 1)
    return (1.0, 1, 1) if total == correct else (0.0, 0, 1)


def _progress_all_types(
    db: Session, user_id: int, req: Dict[str, Any], cache: Optional[Dict[str, Any]] = None
) -> Optional[tuple[float, int, int]]:
    if cache is not None and "exercise_types" in cache and "user_exercise_types" in cache:
        all_set = set(cache["exercise_types"])
        user_set = cache["user_exercise_types"]
    else:
        all_rows = db.execute(
            text("SELECT DISTINCT exercise_type FROM exercises WHERE is_active = true AND is_archived = false")
        ).fetchall()
        if not all_rows:
            return None
        all_set = {str(r[0]).lower() for r in all_rows}
        user_rows = db.execute(
            text("""
                SELECT DISTINCT LOWER(e.exercise_type::text) FROM attempts a
                JOIN exercises e ON a.exercise_id = e.id WHERE a.user_id = :user_id
            """),
            {"user_id": user_id},
        ).fetchall()
        user_set = {str(r[0]).lower() for r in user_rows}
    t = len(all_set)
    if t == 0:
        return None
    c = len(all_set & user_set)
    p = min(1.0, c / max(1, t))
    return (round(p, 2), c, t)


def _progress_comeback(
    _db: Session, _user_id: int, req: Dict[str, Any], _cache: Optional[Dict[str, Any]] = None
) -> Optional[tuple[float, int, int]]:
    """Comeback : pas de progression affichable (surprise)."""
    if "comeback_days" not in req:
        return None
    return (0.0, 0, 1)


def _progress_min_per_type(
    db: Session, user_id: int, req: Dict[str, Any], cache: Optional[Dict[str, Any]] = None
) -> Optional[tuple[float, int, int]]:
    min_count = int(req.get("min_per_type", req.get("min_count", 5)))
    if cache is not None and "exercise_types" in cache and "per_type_correct" in cache:
        types_list = cache["exercise_types"]
        per_type = cache["per_type_correct"]
        min_cur = min((per_type.get(t, 0) for t in types_list), default=0)
    else:
        all_rows = db.execute(
            text("SELECT DISTINCT exercise_type FROM exercises WHERE is_active = true AND is_archived = false")
        ).fetchall()
        if not all_rows:
            return None
        min_cur = float("inf")
        for r in all_rows:
            ex_type = str(r[0]).lower()
            cnt = db.execute(
                    text("""
                        SELECT COUNT(*) FROM attempts a
                        JOIN exercises e ON a.exercise_id = e.id
                        WHERE a.user_id = :user_id AND LOWER(e.exercise_type::text) = LOWER(:ex_type)
                        AND a.is_correct = true
                    """),
                    {"user_id": user_id, "ex_type": ex_type},
                ).fetchone()
            c = cnt[0] if cnt else 0
            min_cur = min(min_cur, c)
        min_cur = int(min_cur) if min_cur != float("inf") else 0
    t = min_count
    min_cur = int(min_cur) if isinstance(min_cur, float) else min_cur
    p = min(1.0, min_cur / max(1, t))
    return (round(p, 2), min_cur, t)


PROGRESS_GETTERS: Dict[str, ProgressFn] = {
    "comeback": _progress_comeback,
    "attempts_count": _progress_attempts_count,
    "logic_attempts_count": _progress_logic_attempts_count,
    "mixte": _progress_mixte,
    "success_rate": _progress_success_rate,
    "consecutive": _progress_consecutive,
    "consecutive_days": _progress_consecutive_days,
    "max_time": _progress_max_time,
    "perfect_day": _progress_perfect_day,
    "all_types": _progress_all_types,
    "min_per_type": _progress_min_per_type,
}


def get_requirement_progress(
    db: Session,
    user_id: int,
    requirements: Dict[str, Any],
    stats_cache: Optional[Dict[str, Any]] = None,
) -> Optional[tuple[float, int, int]]:
    """
    Calcule la progression vers un badge (progress, current, target).
    Retourne None si le type n'a pas de progresseur ou n'est pas reconnu.
    stats_cache: cache optionnel pour éviter N+1 (attempts_count, logic_correct_count, etc.)
    """
    req_type = detect_requirement_type(requirements)
    if req_type is None:
        return None
    getter = PROGRESS_GETTERS.get(req_type)
    if not getter:
        return None
    try:
        return getter(db, user_id, requirements, stats_cache)
    except Exception as e:
        logger.error(f"Erreur get_progress {req_type}: {e}")
        return None

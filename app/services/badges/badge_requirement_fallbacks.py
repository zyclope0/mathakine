"""
Fallback par code pour la vérification des badges (B3.2/B3.3).

Rétrocompatibilité : badges dont le requirement engine générique ne gère pas
encore le format. Évaluation par code de badge.

B3.3 : dispatch explicite code -> checker, familles de règles factorisées.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.models.achievement import Achievement
from app.models.attempt import Attempt
from app.services.badges.badge_requirement_volume import check_success_rate

# Type du checker : (db, user_id, requirements, attempt_data) -> bool
_CheckerFn = Callable[[Session, int, Dict[str, Any], Optional[Dict[str, Any]]], bool]


def check_badge_requirements_by_code(
    db: Session,
    user_id: int,
    badge: Achievement,
    requirements: Dict[str, Any],
    attempt_data: Dict[str, Any] = None,
) -> bool:
    """Fallback : vérification par code (rétrocompatibilité)."""
    checker = _CHECKERS.get(badge.code)
    if checker is None:
        return False
    return checker(db, user_id, requirements, attempt_data)


# ---------------------------------------------------------------------------
# Famille : attempts_count (seuil de tentatives)
# ---------------------------------------------------------------------------


def _make_attempts_count_checker(default_count: int) -> _CheckerFn:
    """Checker : count(attempts) >= attempts_count (défaut = default_count)."""

    def _check(
        db: Session,
        user_id: int,
        requirements: Dict[str, Any],
        attempt_data: Optional[Dict[str, Any]],
    ) -> bool:
        target = requirements.get("attempts_count", default_count)
        count = (
            db.query(func.count(Attempt.id)).filter(Attempt.user_id == user_id).scalar()
        )
        return (count or 0) >= target

    return _check


# ---------------------------------------------------------------------------
# Famille : consecutive_success (série correcte par type d'exercice)
# ---------------------------------------------------------------------------


def _make_consecutive_success_checker(
    exercise_type_default: str, streak_default: int
) -> _CheckerFn:
    """Checker : N réponses correctes consécutives pour un type d'exercice."""

    def _check(
        db: Session,
        user_id: int,
        requirements: Dict[str, Any],
        attempt_data: Optional[Dict[str, Any]],
    ) -> bool:
        ex_type = requirements.get("exercise_type", exercise_type_default)
        required = requirements.get("consecutive_correct", streak_default)
        return _check_consecutive_success(db, user_id, ex_type, required)

    return _check


def _check_consecutive_success(
    db: Session, user_id: int, exercise_type: str, required_streak: int
) -> bool:
    attempts = db.execute(
        text("""
            SELECT a.is_correct
            FROM attempts a
            JOIN exercises e ON a.exercise_id = e.id
            WHERE a.user_id = :user_id
            AND e.exercise_type = :exercise_type
            ORDER BY a.created_at DESC
            LIMIT :limit
        """),
        {
            "user_id": user_id,
            "exercise_type": exercise_type,
            "limit": required_streak * 2,
        },
    ).fetchall()
    if len(attempts) < required_streak:
        return False
    current_streak = 0
    for attempt in attempts:
        if attempt.is_correct:
            current_streak += 1
            if current_streak >= required_streak:
                return True
        else:
            break
    return False


# ---------------------------------------------------------------------------
# Famille : success_rate (taux de réussite + min tentatives)
# Délègue à badge_requirement_volume — source unique (G2/H3).
# ---------------------------------------------------------------------------


def _make_success_rate_checker(
    rate_default: float, min_attempts_default: int
) -> _CheckerFn:
    """Checker : success_rate >= X% avec au moins Y tentatives.
    Délègue à badge_requirement_volume.check_success_rate.
    """

    def _check(
        db: Session,
        user_id: int,
        requirements: Dict[str, Any],
        attempt_data: Optional[Dict[str, Any]],
    ) -> bool:
        req = {
            "min_attempts": requirements.get("min_attempts", min_attempts_default),
            "success_rate": requirements.get("success_rate", rate_default),
        }
        return check_success_rate(db, user_id, req, attempt_data, None)

    return _check


# ---------------------------------------------------------------------------
# Famille : consecutive_days (jours consécutifs d'activité)
# ---------------------------------------------------------------------------


def _make_consecutive_days_checker(days_default: int) -> _CheckerFn:
    """Checker : N jours consécutifs avec au moins une tentative."""

    def _check(
        db: Session,
        user_id: int,
        requirements: Dict[str, Any],
        attempt_data: Optional[Dict[str, Any]],
    ) -> bool:
        required = requirements.get("consecutive_days", days_default)
        return _check_consecutive_days(db, user_id, required)

    return _check


def _check_consecutive_days(db: Session, user_id: int, required_days: int) -> bool:
    days = db.execute(
        text("""
            SELECT DISTINCT DATE(created_at) as day
            FROM attempts
            WHERE user_id = :user_id
            ORDER BY day DESC
            LIMIT :limit
        """),
        {"user_id": user_id, "limit": required_days + 1},
    ).fetchall()
    if len(days) < required_days:
        return False
    today = datetime.now(timezone.utc).date()
    consecutive_count = 0
    for i, day_row in enumerate(days):
        day = day_row.day if hasattr(day_row, "day") else day_row[0]
        expected_date = today - timedelta(days=i)
        if day == expected_date:
            consecutive_count += 1
        else:
            break
    return consecutive_count >= required_days


# ---------------------------------------------------------------------------
# Famille : min_per_type (min correct par type d'exercice)
# ---------------------------------------------------------------------------


def _make_min_per_type_checker(min_default: int) -> _CheckerFn:
    """Checker : au moins N réponses correctes par type d'exercice actif."""

    def _check(
        db: Session,
        user_id: int,
        requirements: Dict[str, Any],
        attempt_data: Optional[Dict[str, Any]],
    ) -> bool:
        min_count = requirements.get("min_per_type", min_default)
        return _check_min_per_type(db, user_id, min_count)

    return _check


def _check_min_per_type(db: Session, user_id: int, min_count: int) -> bool:
    all_types = db.execute(text("""
            SELECT DISTINCT exercise_type
            FROM exercises
            WHERE is_active = true AND is_archived = false
        """)).fetchall()
    if not all_types:
        return False
    all_types_set = {
        str(row.exercise_type if hasattr(row, "exercise_type") else row[0]).lower()
        for row in all_types
    }
    per_type_rows = db.execute(
        text("""
            SELECT LOWER(e.exercise_type::text), COUNT(*) as count
            FROM attempts a
            JOIN exercises e ON a.exercise_id = e.id
            WHERE a.user_id = :user_id AND a.is_correct = true
            GROUP BY LOWER(e.exercise_type::text)
        """),
        {"user_id": user_id},
    ).fetchall()
    counts_by_type = {str(r[0]).lower(): r[1] for r in per_type_rows}
    for ex_type in all_types_set:
        if counts_by_type.get(ex_type, 0) < min_count:
            return False
    return True


# ---------------------------------------------------------------------------
# Checkers spécifiques (sans paramètres factorisables)
# ---------------------------------------------------------------------------


def _check_speed_demon(
    db: Session,
    user_id: int,
    requirements: Dict[str, Any],
    attempt_data: Optional[Dict[str, Any]],
) -> bool:
    """Badge speed_demon : au moins une tentative correcte en <= max_time secondes."""
    max_time = requirements.get("max_time", 5)
    if attempt_data and attempt_data.get("time_spent", float("inf")) <= max_time:
        return True
    fast_attempt = (
        db.query(Attempt)
        .filter(
            Attempt.user_id == user_id,
            Attempt.is_correct.is_(True),
            Attempt.time_spent <= max_time,
        )
        .first()
    )
    return fast_attempt is not None


def _check_perfect_day(
    db: Session,
    user_id: int,
    requirements: Dict[str, Any],
    attempt_data: Optional[Dict[str, Any]],
) -> bool:
    """Badge perfect_day : toutes les tentatives du jour correctes, >= 3."""
    today = datetime.now(timezone.utc).date()
    today_attempts = db.execute(
        text("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN is_correct THEN 1 END) as correct
            FROM attempts
            WHERE user_id = :user_id
            AND DATE(created_at) = :today
        """),
        {"user_id": user_id, "today": today},
    ).fetchone()
    if not today_attempts or today_attempts.total == 0:
        return False
    return today_attempts.correct == today_attempts.total and today_attempts.total >= 3


def _check_all_exercise_types(
    db: Session,
    user_id: int,
    requirements: Dict[str, Any],
    attempt_data: Optional[Dict[str, Any]],
) -> bool:
    """Badge explorer : avoir tenté au moins une fois chaque type d'exercice actif."""
    all_types = db.execute(text("""
            SELECT DISTINCT exercise_type
            FROM exercises
            WHERE is_active = true AND is_archived = false
        """)).fetchall()
    if not all_types:
        return False
    all_types_set = {
        row.exercise_type if hasattr(row, "exercise_type") else row[0]
        for row in all_types
    }
    user_types = db.execute(
        text("""
            SELECT DISTINCT e.exercise_type
            FROM attempts a
            JOIN exercises e ON a.exercise_id = e.id
            WHERE a.user_id = :user_id
        """),
        {"user_id": user_id},
    ).fetchall()
    user_types_set = {
        row.exercise_type if hasattr(row, "exercise_type") else row[0]
        for row in user_types
    }
    all_types_normalized = {str(t).lower() for t in all_types_set}
    user_types_normalized = {str(t).lower() for t in user_types_set}
    return all_types_normalized.issubset(user_types_normalized)


# ---------------------------------------------------------------------------
# Dispatch : code badge -> checker
# ---------------------------------------------------------------------------

_CHECKERS: Dict[str, _CheckerFn] = {
    # attempts_count
    "first_steps": _make_attempts_count_checker(1),
    "padawan_path": _make_attempts_count_checker(10),
    "knight_trial": _make_attempts_count_checker(50),
    "jedi_master": _make_attempts_count_checker(100),
    "grand_master": _make_attempts_count_checker(200),
    # consecutive_success
    "addition_master": _make_consecutive_success_checker("addition", 20),
    "subtraction_master": _make_consecutive_success_checker("soustraction", 15),
    "multiplication_master": _make_consecutive_success_checker("multiplication", 15),
    "division_master": _make_consecutive_success_checker("division", 15),
    # success_rate
    "expert": _make_success_rate_checker(80, 50),
    "perfectionist": _make_success_rate_checker(95, 30),
    # consecutive_days
    "perfect_week": _make_consecutive_days_checker(7),
    "perfect_month": _make_consecutive_days_checker(30),
    # min_per_type
    "versatile": _make_min_per_type_checker(5),
    # spécifiques
    "speed_demon": _check_speed_demon,
    "perfect_day": _check_perfect_day,
    "explorer": _check_all_exercise_types,
}

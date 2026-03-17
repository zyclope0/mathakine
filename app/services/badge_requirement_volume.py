"""
Cluster attempts/volume — Lot F2.

Requirements basés sur le nombre de tentatives (exercices ou défis logiques).
Logique partagée : count >= target, progression min(1, c/t).
"""

from typing import Any, Callable, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.attempt import Attempt

# Signatures alignées sur badge_requirement_engine
CheckerFn = Callable[
    [Session, int, Dict[str, Any], Optional[Dict[str, Any]], Optional[Dict[str, Any]]],
    bool,
]
ProgressFn = Callable[
    [Session, int, Dict[str, Any], Optional[Dict[str, Any]]],
    Optional[tuple[float, int, int]],
]


def _resolve_attempts_count(
    db: Session, user_id: int, cache: Optional[Dict[str, Any]]
) -> int:
    """Compte total des tentatives exercices pour un utilisateur."""
    if cache is not None and "attempts_count" in cache:
        return cache["attempts_count"]
    return (
        db.query(func.count(Attempt.id)).filter(Attempt.user_id == user_id).scalar()
        or 0
    )


def _resolve_logic_correct_count(
    db: Session, user_id: int, cache: Optional[Dict[str, Any]]
) -> int:
    """Compte des tentatives défis logiques correctes pour un utilisateur."""
    from app.models.logic_challenge import LogicChallengeAttempt

    if cache is not None and "logic_correct_count" in cache:
        return cache["logic_correct_count"]
    return (
        db.query(func.count(LogicChallengeAttempt.id))
        .filter(
            LogicChallengeAttempt.user_id == user_id,
            LogicChallengeAttempt.is_correct == True,
        )
        .scalar()
        or 0
    )


def _make_count_checker(
    target_key: str,
    cache_key: str,
    resolve_count: Callable[[Session, int, Optional[Dict[str, Any]]], int],
) -> CheckerFn:
    """Factory : vérifie count >= target avec cache ou DB."""

    def _check(
        db: Session,
        user_id: int,
        req: Dict[str, Any],
        _attempt_data: Optional[Dict[str, Any]] = None,
        stats_cache: Optional[Dict[str, Any]] = None,
    ) -> bool:
        target = req.get(target_key)
        if target is None:
            return False
        count = resolve_count(db, user_id, stats_cache)
        return count >= int(target)

    return _check


def _make_count_progress(
    target_key: str,
    resolve_count: Callable[[Session, int, Optional[Dict[str, Any]]], int],
) -> ProgressFn:
    """Factory : progression min(1, c/t) vers (p, current, target)."""

    def _progress(
        db: Session,
        user_id: int,
        req: Dict[str, Any],
        cache: Optional[Dict[str, Any]] = None,
    ) -> Optional[tuple[float, int, int]]:
        t = req.get(target_key)
        if t is None:
            return None
        t = int(t)
        c = resolve_count(db, user_id, cache)
        p = min(1.0, c / max(1, t))
        return (round(p, 2), c, t)

    return _progress


# Checkers — enregistrés dans badge_requirement_engine.CHECKERS
check_attempts_count = _make_count_checker(
    "attempts_count", "attempts_count", _resolve_attempts_count
)
check_logic_attempts_count = _make_count_checker(
    "logic_attempts_count", "logic_correct_count", _resolve_logic_correct_count
)


def check_mixte(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    _attempt_data: Optional[Dict[str, Any]] = None,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> bool:
    """Vérifie attempts_count ET logic_attempts_count. B5."""
    return check_attempts_count(
        db, user_id, req, _attempt_data, stats_cache
    ) and check_logic_attempts_count(db, user_id, req, _attempt_data, stats_cache)


# Progress getters — enregistrés dans badge_requirement_engine.PROGRESS_GETTERS
progress_attempts_count = _make_count_progress(
    "attempts_count", _resolve_attempts_count
)
progress_logic_attempts_count = _make_count_progress(
    "logic_attempts_count", _resolve_logic_correct_count
)


def progress_mixte(
    db: Session,
    user_id: int,
    req: Dict[str, Any],
    cache: Optional[Dict[str, Any]] = None,
) -> Optional[tuple[float, int, int]]:
    """Progression mixte : min des deux progressions."""
    p1 = progress_attempts_count(db, user_id, req, cache)
    p2 = progress_logic_attempts_count(db, user_id, req, cache)
    if not p1 or not p2:
        return None
    prog1, cur1, tgt1 = p1
    prog2, cur2, tgt2 = p2
    prog = min(prog1, prog2)
    if prog1 <= prog2:
        return (round(prog, 2), cur1, tgt1)
    return (round(prog, 2), cur2, tgt2)

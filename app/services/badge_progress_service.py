"""
Progression vers les badges : unlocked, in_progress, notification (B3.1).
"""

import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.achievement import Achievement, UserAchievement
from app.services.badge_format_helpers import format_requirements_to_text
from app.services.badge_requirement_engine import get_requirement_progress
from app.services.badge_stats_cache import build_stats_cache


def _get_badge_progress(
    db: Session,
    user_id: int,
    badge: Achievement,
    stats_cache: Optional[Dict[str, Any]] = None,
) -> tuple:
    """
    Calcule la progression vers un badge non débloqué.
    Returns: (progress 0.0-1.0, current_value, target_value)
    """
    if not badge.requirements:
        return (0.0, 0, 0)
    try:
        req = (
            json.loads(badge.requirements)
            if isinstance(badge.requirements, str)
            else badge.requirements
        )
    except (json.JSONDecodeError, TypeError):
        return (0.0, 0, 0)
    if not isinstance(req, dict):
        return (0.0, 0, 0)

    result = get_requirement_progress(db, user_id, req, stats_cache)
    if result is not None:
        return result
    return (0.0, 0, 0)


def _build_progress_detail_success_rate(
    req: Dict[str, Any], stats_cache: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Construit progress_detail pour badges success_rate (affichage %)."""
    if "min_attempts" not in req or "success_rate" not in req:
        return None
    total = stats_cache.get("attempts_total") or 0
    correct = stats_cache.get("attempts_correct") or 0
    rate_pct = round(correct / total * 100) if total else 0
    return {
        "type": "success_rate",
        "total": total,
        "correct": correct,
        "rate_pct": rate_pct,
        "min_attempts": int(req["min_attempts"]),
        "required_rate_pct": float(req["success_rate"]),
    }


def get_badges_progress(db: Session, user_id: int) -> Dict[str, Any]:
    """Progression vers les badges (unlocked + in_progress)."""
    earned_ids = {
        r[0]
        for r in db.query(UserAchievement.achievement_id)
        .filter(UserAchievement.user_id == user_id)
        .all()
    }
    all_badges = db.query(Achievement).filter(Achievement.is_active == True).all()
    stats_cache = build_stats_cache(db, user_id)

    unlocked = []
    in_progress = []
    for b in all_badges:
        if b.id in earned_ids:
            unlocked.append({"id": b.id, "code": b.code, "name": b.name})
        else:
            prog, cur, tgt = _get_badge_progress(db, user_id, b, stats_cache)
            item = {
                "id": b.id,
                "code": b.code,
                "name": b.name,
                "progress": prog,
                "current": cur,
                "target": tgt,
                "criteria_text": format_requirements_to_text(b),
                "is_secret": getattr(b, "is_secret", False),
            }
            # Détail enrichi pour success_rate (affichage %)
            try:
                req = (
                    json.loads(b.requirements)
                    if isinstance(b.requirements, str)
                    else (b.requirements or {})
                )
                if isinstance(req, dict):
                    detail = _build_progress_detail_success_rate(req, stats_cache)
                    if detail:
                        item["progress_detail"] = detail
            except (json.JSONDecodeError, TypeError):
                pass
            in_progress.append(item)
    return {"unlocked": unlocked, "in_progress": in_progress}


def get_closest_progress_notification(
    db: Session, user_id: int
) -> Optional[Dict[str, Any]]:
    """
    Retourne le badge le plus proche du déblocage (progress >= 0.5, target > 0).
    Exclut les badges secrets non débloqués.
    """
    data = get_badges_progress(db, user_id)
    earned_ids = {u["id"] for u in data.get("unlocked", [])}
    candidates = []
    for p in data.get("in_progress", []):
        if p.get("target", 0) <= 0:
            continue
        prog = p.get("progress", 0) or 0
        if prog < 0.5:
            continue
        if p.get("is_secret") and p["id"] not in earned_ids:
            continue
        remaining = max(0, (p.get("target", 0) or 0) - (p.get("current", 0) or 0))
        candidates.append((prog, {"name": p.get("name", ""), "remaining": remaining}))
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]

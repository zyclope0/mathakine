"""
Flux de création badge admin — Lot F3, F4.

Sépare explicitement :
1. préparation / normalisation d'entrée
2. validation métier
3. mutation / persistance
4. mapping (délégué à admin_content_service._achievement_to_detail)
"""

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.types import BadgeCreatePrepared, ValidationResult
from app.models.achievement import Achievement
from app.services.admin.admin_helpers import log_admin_action
from app.services.badges.badge_requirement_validation import validate_badge_requirements


def prepare_badge_create_data(data: Dict[str, Any]) -> BadgeCreatePrepared:
    """
    Étape 1 : préparation / normalisation d'entrée.
    Extrait et normalise les champs pour la création d'un badge.
    """
    code = (data.get("code") or "").strip().lower().replace(" ", "_")
    name = (data.get("name") or "").strip()
    return {
        "code": code,
        "name": name,
        "description": (data.get("description") or "").strip() or None,
        "icon_url": (data.get("icon_url") or "").strip() or None,
        "category": (data.get("category") or "").strip() or None,
        "difficulty": (data.get("difficulty") or "bronze").strip().lower() or "bronze",
        "points_reward": int(data.get("points_reward") or 0),
        "is_secret": bool(data.get("is_secret")),
        "requirements": data.get("requirements"),
        "star_wars_title": (data.get("star_wars_title") or "").strip() or None,
    }


def validate_badge_create_pre_persist(
    prepared: BadgeCreatePrepared, db: Session
) -> ValidationResult:
    """
    Étape 2 : validation métier.
    Retourne (error_message, status_code) ou (None, 0) si valide.
    """
    if not prepared.get("code"):
        return "Le code est obligatoire.", 400
    if not prepared.get("name"):
        return "Le nom est obligatoire.", 400

    ok, err = validate_badge_requirements(prepared.get("requirements"))
    if not ok:
        return err or "Requirements invalides.", 400

    existing = (
        db.query(Achievement).filter(Achievement.code == prepared["code"]).first()
    )
    if existing:
        return f"Le code '{prepared['code']}' existe déjà.", 409

    return None, 0


def persist_badge_create(
    db: Session,
    prepared: BadgeCreatePrepared,
    admin_user_id: Optional[int] = None,
) -> Achievement:
    """
    Étape 3 : mutation / persistance.
    Crée l'Achievement, log l'action admin, commit.
    """
    a = Achievement(
        code=prepared["code"],
        name=prepared["name"],
        description=prepared.get("description"),
        icon_url=prepared.get("icon_url"),
        category=prepared.get("category"),
        difficulty=prepared.get("difficulty"),
        points_reward=prepared.get("points_reward", 0),
        is_secret=prepared.get("is_secret", False),
        requirements=prepared.get("requirements"),
        star_wars_title=prepared.get("star_wars_title"),
        is_active=True,
    )
    db.add(a)
    db.flush()
    log_admin_action(
        db,
        admin_user_id,
        "badge_create",
        "achievement",
        a.id,
        {"code": a.code, "name": a.name},
    )
    db.commit()
    db.refresh(a)
    return a

"""
Service pour l'espace admin (rôle archiviste).
Orchestre les opérations métier admin sans dépendance Request.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import case, func, or_, union
from sqlalchemy.orm import Session

from app.models.admin_audit_log import AdminAuditLog
from app.models.achievement import Achievement, UserAchievement
from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.logic_challenge import (
    AgeGroup,
    LogicChallenge,
    LogicChallengeAttempt,
    LogicChallengeType,
)
from app.models.setting import Setting
from app.models.user import User, UserRole
from app.services.email_service import EmailService
from app.utils.email_verification import generate_verification_token

# Schéma des paramètres globaux (aligné avec admin_handlers_utils)
CONFIG_SCHEMA = {
    "maintenance_mode": {
        "type": "bool",
        "default": False,
        "category": "système",
        "label": "Mode maintenance",
    },
    "registration_enabled": {
        "type": "bool",
        "default": True,
        "category": "système",
        "label": "Inscriptions ouvertes",
    },
    "feature_ai_challenges_enabled": {
        "type": "bool",
        "default": True,
        "category": "features",
        "label": "Défis IA activés",
    },
    "feature_chat_enabled": {
        "type": "bool",
        "default": True,
        "category": "features",
        "label": "Chat IA activé",
    },
    "max_generations_per_user_per_hour": {
        "type": "int",
        "default": 20,
        "min": 1,
        "max": 100,
        "category": "limites",
        "label": "Générations max/user/heure",
    },
    "max_export_rows": {
        "type": "int",
        "default": 10000,
        "min": 100,
        "max": 100000,
        "category": "limites",
        "label": "Lignes max export CSV",
    },
}


def _parse_setting_value(value: Optional[str], schema: dict) -> Any:
    if value is None:
        return schema.get("default", "")
    stype = schema.get("type", "str")
    if stype == "bool":
        return value.lower() in ("true", "1", "yes", "on")
    if stype == "int":
        try:
            v = int(value)
            if "min" in schema and v < schema["min"]:
                return schema.get("default", 0)
            if "max" in schema and v > schema["max"]:
                return schema["max"]
            return v
        except ValueError:
            return schema.get("default", 0)
    return value


def _serialize_value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def _log_admin_action(
    db: Session,
    admin_user_id: Optional[int],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
) -> None:
    try:
        log = AdminAuditLog(
            admin_user_id=admin_user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
        )
        db.add(log)
    except Exception:
        pass


def _parse_json_safe(s: Optional[str]) -> Optional[Any]:
    if not s:
        return None
    try:
        return json.loads(s)
    except (TypeError, ValueError):
        return None


class AdminService:
    """Service pour les opérations admin."""

    @staticmethod
    def get_config_for_api(db: Session) -> List[Dict[str, Any]]:
        """Liste les paramètres globaux au format API."""
        rows = db.query(Setting).filter(Setting.key.in_(CONFIG_SCHEMA)).all()
        by_key = {r.key: r for r in rows}
        result = []
        for key, schema in CONFIG_SCHEMA.items():
            row = by_key.get(key)
            raw = row.value if row else None
            value = _parse_setting_value(raw, schema)
            result.append(
                {
                    "key": key,
                    "value": value,
                    "type": schema["type"],
                    "category": schema.get("category", ""),
                    "label": schema.get("label", key),
                    "min": schema.get("min"),
                    "max": schema.get("max"),
                }
            )
        return result

    @staticmethod
    def update_config(
        db: Session,
        settings_in: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> None:
        """Met à jour les paramètres globaux."""
        for key, value in settings_in.items():
            if key not in CONFIG_SCHEMA:
                continue
            schema = CONFIG_SCHEMA[key]
            str_val = _serialize_value(value)
            if schema["type"] == "int":
                try:
                    v = (
                        int(value)
                        if not isinstance(value, (bool, type(None)))
                        else schema["default"]
                    )
                    if "min" in schema and v < schema["min"]:
                        v = schema["min"]
                    if "max" in schema and v > schema["max"]:
                        v = schema["max"]
                    str_val = str(v)
                except (ValueError, TypeError):
                    str_val = str(schema.get("default", 0))
            elif schema["type"] == "bool":
                str_val = "true" if value in (True, "true", "1", 1) else "false"

            row = db.query(Setting).filter(Setting.key == key).first()
            if row:
                row.value = str_val
                row.updated_at = datetime.now(timezone.utc)
            else:
                db.add(
                    Setting(
                        key=key,
                        value=str_val,
                        category=schema.get("category"),
                        description=schema.get("label"),
                        is_system=True,
                        is_public=False,
                    )
                )
        _log_admin_action(
            db,
            admin_user_id,
            "config_update",
            "settings",
            None,
            {"updated_keys": list(settings_in.keys())},
        )
        db.commit()

    @staticmethod
    def get_overview_for_api(db: Session) -> Dict[str, int]:
        """KPIs globaux de la plateforme."""
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_exercises = (
            db.query(func.count(Exercise.id))
            .filter(Exercise.is_archived == False)
            .scalar()
            or 0
        )
        total_challenges = (
            db.query(func.count(LogicChallenge.id))
            .filter(LogicChallenge.is_archived == False)
            .scalar()
            or 0
        )
        total_attempts = db.query(func.count(Attempt.id)).scalar() or 0
        return {
            "total_users": total_users,
            "total_exercises": total_exercises,
            "total_challenges": total_challenges,
            "total_attempts": total_attempts,
        }

    @staticmethod
    def get_audit_log_for_api(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        action_filter: Optional[str] = None,
        resource_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Journal des actions admin."""
        q = db.query(AdminAuditLog).order_by(AdminAuditLog.created_at.desc())
        if action_filter:
            q = q.filter(AdminAuditLog.action == action_filter)
        if resource_filter:
            q = q.filter(AdminAuditLog.resource_type == resource_filter)
        total = q.count()
        logs = q.offset(skip).limit(limit).all()
        items = []
        for log in logs:
            admin_username = None
            if log.admin_user_id:
                u = db.query(User).filter(User.id == log.admin_user_id).first()
                admin_username = u.username if u else None
            items.append(
                {
                    "id": log.id,
                    "admin_user_id": log.admin_user_id,
                    "admin_username": admin_username,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "details": _parse_json_safe(log.details),
                    "created_at": (
                        log.created_at.isoformat() if log.created_at else None
                    ),
                }
            )
        return {"items": items, "total": total}

    @staticmethod
    def get_moderation_for_api(
        db: Session,
        *,
        mod_type: str = "all",
        skip: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Contenu généré par IA pour modération."""
        result = {
            "exercises": [],
            "challenges": [],
            "total_exercises": 0,
            "total_challenges": 0,
        }
        if mod_type in ("exercises", "all"):
            q_ex = db.query(Exercise).filter(Exercise.ai_generated == True)
            result["total_exercises"] = q_ex.count()
            rows_ex = (
                q_ex.order_by(Exercise.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            for e in rows_ex:
                result["exercises"].append(
                    {
                        "id": e.id,
                        "title": e.title,
                        "exercise_type": e.exercise_type or "",
                        "age_group": e.age_group or "",
                        "is_archived": e.is_archived,
                        "created_at": (
                            e.created_at.isoformat() if e.created_at else None
                        ),
                    }
                )
        if mod_type in ("challenges", "all"):
            q_ch = db.query(LogicChallenge)
            result["total_challenges"] = q_ch.count()
            rows_ch = (
                q_ch.order_by(LogicChallenge.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            for c in rows_ch:
                ct_val = (
                    c.challenge_type.value
                    if hasattr(c.challenge_type, "value")
                    else str(c.challenge_type)
                )
                ag_val = (
                    c.age_group.value
                    if hasattr(c.age_group, "value")
                    else str(c.age_group)
                )
                result["challenges"].append(
                    {
                        "id": c.id,
                        "title": c.title,
                        "challenge_type": ct_val,
                        "age_group": ag_val,
                        "is_archived": c.is_archived,
                        "created_at": (
                            c.created_at.isoformat() if c.created_at else None
                        ),
                    }
                )
        return result

    @staticmethod
    def get_reports_for_api(
        db: Session,
        *,
        period: str = "7d",
    ) -> Dict[str, Any]:
        """Rapports par période."""
        days = 7 if period == "7d" else 30
        since = datetime.now(timezone.utc) - timedelta(days=days)

        new_users = (
            db.query(func.count(User.id)).filter(User.created_at >= since).scalar() or 0
        )
        attempts_exercises = (
            db.query(
                func.count(Attempt.id).label("total"),
                func.sum(case((Attempt.is_correct == True, 1), else_=0)).label(
                    "correct"
                ),
            )
            .filter(Attempt.created_at >= since)
            .first()
        )
        total_attempts = attempts_exercises[0] or 0
        correct_attempts = attempts_exercises[1] or 0
        challenge_attempts_count = (
            db.query(func.count(LogicChallengeAttempt.id))
            .filter(LogicChallengeAttempt.created_at >= since)
            .scalar()
            or 0
        )
        challenge_correct = (
            db.query(func.count(LogicChallengeAttempt.id))
            .filter(
                LogicChallengeAttempt.created_at >= since,
                LogicChallengeAttempt.is_correct == True,
            )
            .scalar()
            or 0
        )
        q1 = db.query(Attempt.user_id).filter(Attempt.created_at >= since).distinct()
        q2 = (
            db.query(LogicChallengeAttempt.user_id)
            .filter(LogicChallengeAttempt.created_at >= since)
            .distinct()
        )
        u = union(q1, q2).subquery()
        active_users_count = db.query(func.count()).select_from(u).scalar() or 0
        total_attempts_all = total_attempts + challenge_attempts_count
        total_correct_all = correct_attempts + challenge_correct
        success_rate = (
            round((total_correct_all / total_attempts_all * 100), 1)
            if total_attempts_all > 0
            else 0.0
        )
        return {
            "period": period,
            "days": days,
            "new_users": new_users,
            "attempts_exercises": total_attempts,
            "attempts_challenges": challenge_attempts_count,
            "total_attempts": total_attempts_all,
            "success_rate": success_rate,
            "active_users": active_users_count,
        }

    # --- Users CRUD ---

    @staticmethod
    def list_users_for_admin(
        db: Session,
        *,
        search: str = "",
        role: str = "",
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Liste paginée des utilisateurs avec filtres."""
        limit = min(100, max(1, limit))
        skip = max(0, skip)
        q = db.query(User)
        if search:
            pattern = f"%{search}%"
            q = q.filter(
                or_(
                    User.username.ilike(pattern),
                    User.email.ilike(pattern),
                    User.full_name.ilike(pattern),
                )
            )
        role_map = {
            "padawan": UserRole.PADAWAN,
            "maitre": UserRole.MAITRE,
            "gardien": UserRole.GARDIEN,
            "archiviste": UserRole.ARCHIVISTE,
        }
        if role and role in role_map:
            q = q.filter(User.role == role_map[role])
        if is_active is not None:
            q = q.filter(User.is_active == is_active)
        total = q.count()
        users = q.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        items = [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role.value if u.role else "padawan",
                "is_active": u.is_active,
                "is_email_verified": u.is_email_verified,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
        return {"items": items, "total": total}

    @staticmethod
    def patch_user_for_admin(
        db: Session,
        *,
        user_id: int,
        admin_user_id: int,
        is_active: Optional[bool] = None,
        new_role: Optional[UserRole] = None,
        role_raw: Any = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """
        Met à jour is_active et/ou role d'un utilisateur.
        Returns: (result_dict, error_message, status_code)
        status_code 200 + result si ok, 400/404 + error sinon.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "Utilisateur non trouvé.", 404
        if is_active is not None:
            user.is_active = is_active
        if new_role is not None:
            user.role = new_role
        _log_admin_action(
            db,
            admin_user_id,
            "user_patch",
            "user",
            user_id,
            {"is_active": is_active, "role": role_raw},
        )
        db.commit()
        db.refresh(user)
        return (
            {
                "id": user.id,
                "username": user.username,
                "is_active": user.is_active,
                "role": user.role.value if user.role else "padawan",
            },
            None,
            200,
        )

    @staticmethod
    def send_reset_password_for_admin(
        db: Session, user_id: int
    ) -> Tuple[bool, Optional[str], int]:
        """
        Force l'envoi d'un email de réinitialisation de mot de passe.
        Returns: (success, error_message, status_code)
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "Utilisateur non trouvé.", 404
        if not user.is_active:
            return False, "Compte désactivé, impossible d'envoyer l'email.", 400
        reset_token = generate_verification_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        user.password_reset_token = reset_token
        user.password_reset_expires_at = expires_at
        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        frontend_url = os.getenv(
            "FRONTEND_URL", "https://mathakine-frontend.onrender.com"
        )
        email_sent = EmailService.send_password_reset_email(
            to_email=user.email,
            username=user.username,
            reset_token=reset_token,
            frontend_url=frontend_url,
        )
        if not email_sent:
            return False, "Impossible d'envoyer l'email. Réessayez plus tard.", 500
        return True, None, 200

    @staticmethod
    def resend_verification_for_admin(
        db: Session, user_id: int
    ) -> Tuple[bool, bool, Optional[str], int]:
        """
        Force l'envoi d'un email de vérification.
        Returns: (success, already_verified, error_message, status_code)
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, False, "Utilisateur non trouvé.", 404
        if user.is_email_verified:
            return True, True, None, 200  # already verified, no error
        verification_token = generate_verification_token()
        user.email_verification_token = verification_token
        user.email_verification_sent_at = datetime.now(timezone.utc)
        db.commit()
        frontend_url = os.getenv(
            "FRONTEND_URL", "https://mathakine-frontend.onrender.com"
        )
        email_sent = EmailService.send_verification_email(
            to_email=user.email,
            username=user.username,
            verification_token=verification_token,
            frontend_url=frontend_url,
        )
        if not email_sent:
            return (
                False,
                False,
                "Impossible d'envoyer l'email. Réessayez plus tard.",
                500,
            )
        return True, False, None, 200

    # --- Badges CRUD ---

    @staticmethod
    def _achievement_to_detail(a: Achievement) -> Dict[str, Any]:
        return {
            "id": a.id,
            "code": a.code or "",
            "name": a.name or "",
            "description": a.description or "",
            "icon_url": a.icon_url or "",
            "category": a.category or "",
            "difficulty": a.difficulty or "",
            "points_reward": a.points_reward or 0,
            "is_secret": a.is_secret or False,
            "requirements": a.requirements,
            "star_wars_title": a.star_wars_title or "",
            "is_active": a.is_active if a.is_active is not None else True,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }

    @staticmethod
    def _validate_badge_requirements(
        req: Optional[Dict],
    ) -> Tuple[bool, Optional[str]]:
        if req is None:
            return False, "requirements est requis"
        if not isinstance(req, dict):
            return False, "requirements doit être un objet JSON"
        if len(req) == 0:
            return False, "requirements doit contenir au moins une clé"
        if "attempts_count" in req:
            v = req.get("attempts_count")
            if not isinstance(v, (int, float)) or v < 1:
                return False, "attempts_count doit être un nombre >= 1"
            return True, None
        if "min_attempts" in req and "success_rate" in req:
            ma, sr = req.get("min_attempts"), req.get("success_rate")
            if not isinstance(ma, (int, float)) or ma < 1:
                return False, "min_attempts doit être un nombre >= 1"
            if not isinstance(sr, (int, float)) or sr < 0 or sr > 100:
                return False, "success_rate doit être entre 0 et 100"
            return True, None
        if "consecutive_correct" in req:
            cc = req.get("consecutive_correct")
            if not isinstance(cc, (int, float)) or cc < 1:
                return False, "consecutive_correct doit être un nombre >= 1"
            return True, None
        if "max_time" in req:
            mt = req.get("max_time")
            if not isinstance(mt, (int, float)) or mt < 0:
                return False, "max_time doit être un nombre >= 0"
            return True, None
        if "consecutive_days" in req:
            cd = req.get("consecutive_days")
            if not isinstance(cd, (int, float)) or cd < 1:
                return False, "consecutive_days doit être un nombre >= 1"
            return True, None
        if "logic_attempts_count" in req:
            lac = req.get("logic_attempts_count")
            if not isinstance(lac, (int, float)) or lac < 1:
                return False, "logic_attempts_count doit être un nombre >= 1"
            if "attempts_count" in req:
                ac = req.get("attempts_count")
                if not isinstance(ac, (int, float)) or ac < 1:
                    return False, "attempts_count doit être un nombre >= 1 (mixte)"
            return True, None
        if "comeback_days" in req:
            cd = req.get("comeback_days")
            if not isinstance(cd, (int, float)) or cd < 1:
                return False, "comeback_days doit être un nombre >= 1"
            return True, None
        return True, None

    @staticmethod
    def list_badges_for_admin(db: Session) -> Dict[str, Any]:
        badges = (
            db.query(Achievement).order_by(Achievement.category, Achievement.code).all()
        )
        counts = (
            db.query(UserAchievement.achievement_id, func.count(UserAchievement.id))
            .group_by(UserAchievement.achievement_id)
            .all()
        )
        count_map = {aid: c for aid, c in counts}
        items = []
        for a in badges:
            d = AdminService._achievement_to_detail(a)
            d["_user_count"] = count_map.get(a.id, 0)
            items.append(d)
        return {"success": True, "data": items}

    @staticmethod
    def create_badge_for_admin(
        db: Session,
        *,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        code = (data.get("code") or "").strip().lower().replace(" ", "_")
        name = (data.get("name") or "").strip()
        if not code:
            return None, "Le code est obligatoire.", 400
        if not name:
            return None, "Le nom est obligatoire.", 400
        requirements = data.get("requirements")
        ok, err = AdminService._validate_badge_requirements(requirements)
        if not ok:
            return None, err or "Requirements invalides.", 400
        existing = db.query(Achievement).filter(Achievement.code == code).first()
        if existing:
            return None, f"Le code '{code}' existe déjà.", 409
        a = Achievement(
            code=code,
            name=name,
            description=(data.get("description") or "").strip() or None,
            icon_url=(data.get("icon_url") or "").strip() or None,
            category=(data.get("category") or "").strip() or None,
            difficulty=(data.get("difficulty") or "bronze").strip().lower() or "bronze",
            points_reward=int(data.get("points_reward") or 0),
            is_secret=bool(data.get("is_secret")),
            requirements=requirements,
            star_wars_title=(data.get("star_wars_title") or "").strip() or None,
            is_active=True,
        )
        db.add(a)
        db.flush()
        _log_admin_action(
            db,
            admin_user_id,
            "badge_create",
            "achievement",
            a.id,
            {"code": a.code, "name": a.name},
        )
        db.commit()
        db.refresh(a)
        return AdminService._achievement_to_detail(a), None, 201

    @staticmethod
    def get_badge_for_admin(
        db: Session, badge_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        a = db.query(Achievement).filter(Achievement.id == badge_id).first()
        if not a:
            return None, "Badge non trouvé.", 404
        d = AdminService._achievement_to_detail(a)
        user_count = (
            db.query(func.count(UserAchievement.id))
            .filter(UserAchievement.achievement_id == badge_id)
            .scalar()
            or 0
        )
        d["_user_count"] = user_count
        return d, None, 200

    @staticmethod
    def put_badge_for_admin(
        db: Session,
        *,
        badge_id: int,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        a = db.query(Achievement).filter(Achievement.id == badge_id).first()
        if not a:
            return None, "Badge non trouvé.", 404
        if "requirements" in data:
            ok, err = AdminService._validate_badge_requirements(
                data.get("requirements")
            )
            if not ok:
                return None, err or "Requirements invalides.", 400
        str_fields = (
            "name",
            "description",
            "icon_url",
            "category",
            "difficulty",
            "star_wars_title",
        )
        for k, v in data.items():
            if k == "code":
                continue
            if k == "points_reward":
                a.points_reward = int(v) if v is not None else 0
            elif k in ("is_secret", "is_active"):
                setattr(a, k, v in (True, "true", "1", 1))
            elif k == "requirements":
                a.requirements = v
            elif k in str_fields and v is not None:
                setattr(a, k, (v or "").strip() or None)
        _log_admin_action(
            db,
            admin_user_id,
            "badge_update",
            "achievement",
            badge_id,
            {"fields": list(data.keys())},
        )
        db.commit()
        db.refresh(a)
        return AdminService._achievement_to_detail(a), None, 200

    @staticmethod
    def delete_badge_for_admin(
        db: Session,
        *,
        badge_id: int,
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        a = db.query(Achievement).filter(Achievement.id == badge_id).first()
        if not a:
            return None, "Badge non trouvé.", 404
        user_count = (
            db.query(func.count(UserAchievement.id))
            .filter(UserAchievement.achievement_id == badge_id)
            .scalar()
            or 0
        )
        a.is_active = False
        _log_admin_action(
            db,
            admin_user_id,
            "badge_delete",
            "achievement",
            badge_id,
            {"soft": True, "user_count": user_count},
        )
        db.commit()
        db.refresh(a)
        return (
            {
                "success": True,
                "id": a.id,
                "code": a.code,
                "name": a.name,
                "is_active": False,
                "message": "Badge désactivé (soft delete).",
            },
            None,
            200,
        )

    # --- Exercises CRUD ---

    @staticmethod
    def _exercise_to_detail(e: Exercise) -> Dict[str, Any]:
        return {
            "id": e.id,
            "title": e.title,
            "exercise_type": e.exercise_type or "",
            "difficulty": e.difficulty or "",
            "age_group": e.age_group or "",
            "tags": e.tags or "",
            "context_theme": e.context_theme or "",
            "complexity": e.complexity,
            "ai_generated": e.ai_generated or False,
            "question": e.question or "",
            "correct_answer": e.correct_answer or "",
            "choices": e.choices,
            "explanation": e.explanation or "",
            "hint": e.hint or "",
            "image_url": e.image_url or "",
            "audio_url": e.audio_url or "",
            "is_active": e.is_active,
            "is_archived": e.is_archived,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "updated_at": e.updated_at.isoformat() if e.updated_at else None,
        }

    @staticmethod
    def list_exercises_for_admin(
        db: Session,
        *,
        archived: Optional[bool] = None,
        exercise_type: Optional[str] = None,
        search: str = "",
        sort: str = "created_at",
        order: str = "desc",
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        sortable = {"title", "exercise_type", "difficulty", "age_group", "created_at"}
        if sort not in sortable:
            sort = "created_at"
        order_fn = "asc" if order == "asc" else "desc"
        sort_col = getattr(Exercise, sort, Exercise.created_at)
        order_by = getattr(sort_col, order_fn)()

        q = db.query(Exercise)
        if archived is not None:
            q = q.filter(Exercise.is_archived == archived)
        if exercise_type:
            q = q.filter(Exercise.exercise_type == exercise_type)
        if search:
            q = q.filter(Exercise.title.ilike(f"%{search}%"))
        total = q.count()
        exercises = q.order_by(order_by).offset(skip).limit(limit).all()
        ex_ids = [e.id for e in exercises]

        attempt_stats: Dict[int, Dict[str, int]] = {}
        if ex_ids:
            rows = (
                db.query(
                    Attempt.exercise_id,
                    func.count(Attempt.id).label("attempt_count"),
                    func.sum(case((Attempt.is_correct == True, 1), else_=0)).label(
                        "correct_count"
                    ),
                )
                .filter(Attempt.exercise_id.in_(ex_ids))
                .group_by(Attempt.exercise_id)
                .all()
            )
            for ex_id, a_count, c_count in rows:
                attempt_stats[ex_id] = {
                    "attempt_count": a_count or 0,
                    "correct_count": c_count or 0,
                }

        items = []
        for e in exercises:
            stats = attempt_stats.get(e.id, {"attempt_count": 0, "correct_count": 0})
            a_count = stats["attempt_count"]
            c_count = stats["correct_count"]
            success_rate = round((c_count / a_count * 100), 1) if a_count > 0 else 0.0
            items.append(
                {
                    "id": e.id,
                    "title": e.title,
                    "exercise_type": e.exercise_type,
                    "difficulty": e.difficulty,
                    "age_group": e.age_group,
                    "is_archived": e.is_archived,
                    "attempt_count": a_count,
                    "success_rate": success_rate,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
            )
        return {"items": items, "total": total}

    @staticmethod
    def create_exercise_for_admin(
        db: Session,
        *,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        title = (data.get("title") or "").strip()
        question = (data.get("question") or "").strip()
        correct_answer = (data.get("correct_answer") or "").strip()
        exercise_type = (data.get("exercise_type") or "DIVERS").strip().upper()
        difficulty = (data.get("difficulty") or "PADAWAN").strip()
        age_group = (data.get("age_group") or "9-11").strip()

        if not title:
            return None, "Le titre est obligatoire.", 400
        if not question:
            return None, "La question est obligatoire.", 400
        if not correct_answer:
            return None, "La réponse correcte est obligatoire.", 400

        ex = Exercise(
            title=title,
            exercise_type=exercise_type,
            difficulty=difficulty,
            age_group=age_group,
            question=question,
            correct_answer=correct_answer,
            choices=data.get("choices"),
            explanation=(data.get("explanation") or "").strip() or None,
            hint=(data.get("hint") or "").strip() or None,
            tags=(data.get("tags") or "").strip() or None,
            ai_generated=False,
        )
        db.add(ex)
        db.flush()
        _log_admin_action(
            db, admin_user_id, "exercise_create", "exercise", ex.id, {"title": ex.title}
        )
        db.commit()
        db.refresh(ex)
        return AdminService._exercise_to_detail(ex), None, 201

    @staticmethod
    def get_exercise_for_admin(
        db: Session, exercise_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not ex:
            return None, "Exercice non trouvé.", 404
        return AdminService._exercise_to_detail(ex), None, 200

    @staticmethod
    def put_exercise_for_admin(
        db: Session,
        *,
        exercise_id: int,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not ex:
            return None, "Exercice non trouvé.", 404
        allowed_str = {
            "title",
            "exercise_type",
            "difficulty",
            "age_group",
            "tags",
            "context_theme",
            "complexity",
            "question",
            "correct_answer",
            "explanation",
            "hint",
            "image_url",
            "audio_url",
        }
        allowed_bool = {"is_active", "is_archived"}
        allowed_json = {"choices"}
        for k, v in data.items():
            if k in allowed_str and v is not None:
                setattr(ex, k, str(v) if not isinstance(v, str) else v)
            elif k in allowed_bool and v is not None:
                setattr(ex, k, v in (True, "true", "1", 1))
            elif k in allowed_json:
                setattr(ex, k, v)
        _log_admin_action(
            db,
            admin_user_id,
            "exercise_update",
            "exercise",
            exercise_id,
            {"fields": list(data.keys())},
        )
        db.commit()
        db.refresh(ex)
        return AdminService._exercise_to_detail(ex), None, 200

    @staticmethod
    def duplicate_exercise_for_admin(
        db: Session,
        *,
        exercise_id: int,
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        orig = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not orig:
            return None, "Exercice non trouvé.", 404
        copy = Exercise(
            title=f"{orig.title} (copie)",
            exercise_type=orig.exercise_type,
            difficulty=orig.difficulty,
            age_group=orig.age_group,
            tags=orig.tags,
            context_theme=orig.context_theme,
            complexity=orig.complexity,
            ai_generated=orig.ai_generated,
            question=orig.question,
            correct_answer=orig.correct_answer,
            choices=orig.choices,
            explanation=orig.explanation,
            hint=orig.hint,
            image_url=orig.image_url,
            audio_url=orig.audio_url,
            is_active=orig.is_active,
            is_archived=False,
        )
        db.add(copy)
        db.flush()
        _log_admin_action(
            db,
            admin_user_id,
            "exercise_duplicate",
            "exercise",
            copy.id,
            {"from_id": exercise_id, "title": copy.title},
        )
        db.commit()
        db.refresh(copy)
        return AdminService._exercise_to_detail(copy), None, 201

    @staticmethod
    def patch_exercise_for_admin(
        db: Session,
        *,
        exercise_id: int,
        is_archived: bool,
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not ex:
            return None, "Exercice non trouvé.", 404
        ex.is_archived = is_archived
        _log_admin_action(
            db,
            admin_user_id,
            "exercise_archive",
            "exercise",
            exercise_id,
            {"is_archived": is_archived},
        )
        db.commit()
        db.refresh(ex)
        return (
            {"id": ex.id, "title": ex.title, "is_archived": ex.is_archived},
            None,
            200,
        )

    # --- Challenges CRUD ---

    @staticmethod
    def _challenge_to_detail(c: LogicChallenge) -> Dict[str, Any]:
        ct_val = (
            c.challenge_type.value
            if hasattr(c.challenge_type, "value")
            else str(c.challenge_type)
        )
        ag_val = (
            c.age_group.value if hasattr(c.age_group, "value") else str(c.age_group)
        )
        return {
            "id": c.id,
            "title": c.title,
            "description": c.description or "",
            "challenge_type": ct_val,
            "age_group": ag_val,
            "difficulty": c.difficulty or "",
            "content": c.content or "",
            "question": c.question or "",
            "solution": c.solution or "",
            "correct_answer": c.correct_answer or "",
            "choices": c.choices,
            "solution_explanation": c.solution_explanation or "",
            "visual_data": c.visual_data,
            "hints": c.hints,
            "image_url": c.image_url or "",
            "tags": c.tags or "",
            "is_active": c.is_active,
            "is_archived": c.is_archived,
            "difficulty_rating": c.difficulty_rating,
            "estimated_time_minutes": c.estimated_time_minutes,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }

    @staticmethod
    def list_challenges_for_admin(
        db: Session,
        *,
        archived: Optional[bool] = None,
        challenge_type: Optional[str] = None,
        search: str = "",
        sort: str = "created_at",
        order: str = "desc",
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        sortable = {"title", "challenge_type", "age_group", "created_at"}
        if sort not in sortable:
            sort = "created_at"
        order_fn = "asc" if order == "asc" else "desc"
        sort_col = getattr(LogicChallenge, sort, LogicChallenge.created_at)
        order_by = getattr(sort_col, order_fn)()

        q = db.query(LogicChallenge)
        if archived is not None:
            q = q.filter(LogicChallenge.is_archived == archived)
        if challenge_type:
            try:
                ct = LogicChallengeType(challenge_type)
                q = q.filter(LogicChallenge.challenge_type == ct)
            except ValueError:
                pass
        if search:
            pattern = f"%{search}%"
            q = q.filter(
                or_(
                    LogicChallenge.title.ilike(pattern),
                    LogicChallenge.description.ilike(pattern),
                )
            )
        total = q.count()
        challenges = q.order_by(order_by).offset(skip).limit(limit).all()
        ch_ids = [c.id for c in challenges]

        attempt_stats: Dict[int, Dict[str, int]] = {}
        if ch_ids:
            rows = (
                db.query(
                    LogicChallengeAttempt.challenge_id,
                    func.count(LogicChallengeAttempt.id).label("attempt_count"),
                    func.sum(
                        case((LogicChallengeAttempt.is_correct == True, 1), else_=0)
                    ).label("correct_count"),
                )
                .filter(LogicChallengeAttempt.challenge_id.in_(ch_ids))
                .group_by(LogicChallengeAttempt.challenge_id)
                .all()
            )
            for ch_id, a_count, c_count in rows:
                attempt_stats[ch_id] = {
                    "attempt_count": a_count or 0,
                    "correct_count": c_count or 0,
                }

        items = []
        for c in challenges:
            stats = attempt_stats.get(c.id, {"attempt_count": 0, "correct_count": 0})
            a_count = stats["attempt_count"]
            c_count = stats["correct_count"]
            success_rate = round((c_count / a_count * 100), 1) if a_count > 0 else 0.0
            ct_val = (
                c.challenge_type.value
                if hasattr(c.challenge_type, "value")
                else str(c.challenge_type)
            )
            ag_val = (
                c.age_group.value if hasattr(c.age_group, "value") else str(c.age_group)
            )
            items.append(
                {
                    "id": c.id,
                    "title": c.title,
                    "challenge_type": ct_val,
                    "age_group": ag_val,
                    "is_archived": c.is_archived,
                    "attempt_count": a_count,
                    "success_rate": success_rate,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
            )
        return {"items": items, "total": total}

    @staticmethod
    def create_challenge_for_admin(
        db: Session,
        *,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        title = (data.get("title") or "").strip()
        description = (data.get("description") or "").strip()
        challenge_type_raw = (data.get("challenge_type") or "puzzle").strip().lower()
        age_group_raw = (data.get("age_group") or "GROUP_10_12").strip()

        if not title:
            return None, "Le titre est obligatoire.", 400
        if not description:
            return None, "La description est obligatoire.", 400

        try:
            ct = LogicChallengeType(challenge_type_raw)
        except ValueError:
            ct = LogicChallengeType.PUZZLE
        try:
            ag = AgeGroup(age_group_raw)
        except ValueError:
            ag = AgeGroup.GROUP_10_12

        ch = LogicChallenge(
            title=title,
            description=description,
            challenge_type=ct,
            age_group=ag,
            question=(data.get("question") or "").strip() or None,
            content=(data.get("content") or "").strip() or None,
            solution=(data.get("solution") or "").strip() or None,
            correct_answer=(data.get("correct_answer") or "").strip() or None,
            solution_explanation=(data.get("solution_explanation") or "").strip()
            or None,
            visual_data=data.get("visual_data"),
            hints=data.get("hints"),
        )
        db.add(ch)
        db.flush()
        _log_admin_action(
            db,
            admin_user_id,
            "challenge_create",
            "challenge",
            ch.id,
            {"title": ch.title},
        )
        db.commit()
        db.refresh(ch)
        return AdminService._challenge_to_detail(ch), None, 201

    @staticmethod
    def get_challenge_for_admin(
        db: Session, challenge_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ch = db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        if not ch:
            return None, "Défi non trouvé.", 404
        return AdminService._challenge_to_detail(ch), None, 200

    @staticmethod
    def put_challenge_for_admin(
        db: Session,
        *,
        challenge_id: int,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ch = db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        if not ch:
            return None, "Défi non trouvé.", 404
        allowed_str = {
            "title",
            "description",
            "difficulty",
            "content",
            "question",
            "solution",
            "correct_answer",
            "solution_explanation",
            "image_url",
            "tags",
        }
        allowed_bool = {"is_active", "is_archived"}
        allowed_int = {"difficulty_rating", "estimated_time_minutes"}
        allowed_json = {"choices", "visual_data", "hints"}
        for k, v in data.items():
            if k in allowed_str and v is not None:
                setattr(ch, k, str(v) if not isinstance(v, str) else v)
            elif k in allowed_bool and v is not None:
                setattr(ch, k, v in (True, "true", "1", 1))
            elif k in allowed_int and v is not None:
                setattr(ch, k, int(v) if isinstance(v, (int, float)) else v)
            elif k in allowed_json:
                setattr(ch, k, v)
            elif k == "challenge_type" and v is not None:
                try:
                    setattr(ch, k, LogicChallengeType(str(v).lower()))
                except ValueError:
                    pass
            elif k == "age_group" and v is not None:
                try:
                    setattr(ch, k, AgeGroup(str(v).strip()))
                except ValueError:
                    pass
        _log_admin_action(
            db,
            admin_user_id,
            "challenge_update",
            "challenge",
            challenge_id,
            {"fields": list(data.keys())},
        )
        db.commit()
        db.refresh(ch)
        return AdminService._challenge_to_detail(ch), None, 200

    @staticmethod
    def duplicate_challenge_for_admin(
        db: Session,
        *,
        challenge_id: int,
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        orig = (
            db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        )
        if not orig:
            return None, "Défi non trouvé.", 404
        copy = LogicChallenge(
            title=f"{orig.title} (copie)",
            description=orig.description,
            challenge_type=orig.challenge_type,
            age_group=orig.age_group,
            difficulty=orig.difficulty,
            content=orig.content,
            question=orig.question,
            solution=orig.solution,
            correct_answer=orig.correct_answer,
            choices=orig.choices,
            solution_explanation=orig.solution_explanation,
            visual_data=orig.visual_data,
            hints=orig.hints,
            image_url=orig.image_url,
            tags=orig.tags,
            is_active=orig.is_active,
            is_archived=False,
            difficulty_rating=orig.difficulty_rating,
            estimated_time_minutes=orig.estimated_time_minutes,
        )
        db.add(copy)
        db.flush()
        _log_admin_action(
            db,
            admin_user_id,
            "challenge_duplicate",
            "challenge",
            copy.id,
            {"from_id": challenge_id, "title": copy.title},
        )
        db.commit()
        db.refresh(copy)
        return AdminService._challenge_to_detail(copy), None, 201

    @staticmethod
    def patch_challenge_for_admin(
        db: Session,
        *,
        challenge_id: int,
        is_archived: bool,
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ch = db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        if not ch:
            return None, "Défi non trouvé.", 404
        ch.is_archived = is_archived
        _log_admin_action(
            db,
            admin_user_id,
            "challenge_archive",
            "challenge",
            challenge_id,
            {"is_archived": is_archived},
        )
        db.commit()
        db.refresh(ch)
        return (
            {"id": ch.id, "title": ch.title, "is_archived": ch.is_archived},
            None,
            200,
        )

    # --- Export CSV ---

    @staticmethod
    def export_csv_data_for_admin(
        db: Session,
        *,
        export_type: str,
        period: str,
        admin_user_id: Optional[int] = None,
    ) -> Tuple[List[str], List[List[Any]]]:
        """
        Prépare les données pour un export CSV admin.
        Retourne (headers, rows_data).
        """
        since = None
        if period == "7d":
            since = datetime.now(timezone.utc) - timedelta(days=7)
        elif period == "30d":
            since = datetime.now(timezone.utc) - timedelta(days=30)

        MAX_ROWS = 10_000
        _log_admin_action(
            db,
            admin_user_id,
            "export_csv",
            None,
            None,
            {"type": export_type, "period": period},
        )
        db.commit()

        if export_type == "users":
            q = db.query(User)
            if since:
                q = q.filter(User.created_at >= since)
            rows = q.order_by(User.created_at.desc()).limit(MAX_ROWS).all()
            rows_data = [
                [
                    u.id,
                    u.username or "",
                    u.email or "",
                    u.full_name or "",
                    u.role.value if u.role else "",
                    u.is_active,
                    u.created_at.isoformat() if u.created_at else "",
                ]
                for u in rows
            ]
            headers = [
                "id",
                "username",
                "email",
                "full_name",
                "role",
                "is_active",
                "created_at",
            ]
        elif export_type == "exercises":
            q = db.query(Exercise)
            if since:
                q = q.filter(Exercise.created_at >= since)
            rows = q.order_by(Exercise.created_at.desc()).limit(MAX_ROWS).all()
            rows_data = [
                [
                    e.id,
                    (e.title or "").replace("\n", " "),
                    e.exercise_type or "",
                    e.difficulty or "",
                    e.age_group or "",
                    e.is_archived,
                    e.created_at.isoformat() if e.created_at else "",
                ]
                for e in rows
            ]
            headers = [
                "id",
                "title",
                "exercise_type",
                "difficulty",
                "age_group",
                "is_archived",
                "created_at",
            ]
        elif export_type == "attempts":
            q = db.query(Attempt)
            if since:
                q = q.filter(Attempt.created_at >= since)
            rows = q.order_by(Attempt.created_at.desc()).limit(MAX_ROWS).all()
            rows_data = [
                [
                    a.id,
                    a.user_id,
                    a.exercise_id,
                    a.is_correct,
                    a.time_spent or "",
                    a.created_at.isoformat() if a.created_at else "",
                ]
                for a in rows
            ]
            headers = [
                "id",
                "user_id",
                "exercise_id",
                "is_correct",
                "time_spent",
                "created_at",
            ]
        else:  # overview
            total_users = db.query(func.count(User.id)).scalar() or 0
            total_exercises = db.query(func.count(Exercise.id)).scalar() or 0
            total_challenges = db.query(func.count(LogicChallenge.id)).scalar() or 0
            total_attempts = db.query(func.count(Attempt.id)).scalar() or 0
            headers = ["metric", "value", "period"]
            rows_data = [
                ["total_users", total_users, period],
                ["total_exercises", total_exercises, period],
                ["total_challenges", total_challenges, period],
                ["total_attempts", total_attempts, period],
            ]
        return headers, rows_data

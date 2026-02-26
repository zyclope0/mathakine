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
from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt
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

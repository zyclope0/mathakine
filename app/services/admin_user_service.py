"""
Service admin pour la gestion des utilisateurs.

Extrait de AdminService.
Phase 3, item 3.3b — audit architecture 03/2026.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple, cast

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.types import AdminUserItemDict, AdminUserListDict
from app.models.user import User, UserRole
from app.services.admin_helpers import log_admin_action
from app.services.email_service import EmailService
from app.services.user_service import UserService
from app.utils.email_verification import generate_verification_token


class AdminUserService:
    """Opérations admin pour la gestion des utilisateurs."""

    ROLE_MAP = {
        "padawan": UserRole.PADAWAN,
        "maitre": UserRole.MAITRE,
        "gardien": UserRole.GARDIEN,
        "archiviste": UserRole.ARCHIVISTE,
    }

    @staticmethod
    def list_users_for_admin(
        db: Session,
        *,
        search: str = "",
        role: str = "",
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> AdminUserListDict:
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
        return {"items": cast(List[AdminUserItemDict], items), "total": total}

    @classmethod
    def validate_and_patch_user(
        cls,
        db: Session,
        *,
        user_id: int,
        admin_user_id: int,
        data: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        is_active = data.get("is_active")
        role_raw = data.get("role")

        if is_active is not None and not isinstance(is_active, bool):
            return None, "Le champ is_active doit être un booléen.", 400

        new_role = None
        if role_raw is not None:
            r = str(role_raw).strip().lower()
            if r not in cls.ROLE_MAP:
                return (
                    None,
                    "Rôle invalide. Valeurs: padawan, maitre, gardien, archiviste.",
                    400,
                )
            new_role = cls.ROLE_MAP[r]

        if is_active is None and new_role is None:
            return None, "Fournissez is_active et/ou role à modifier.", 400

        if user_id == admin_user_id:
            if is_active is False:
                return (
                    None,
                    "Vous ne pouvez pas désactiver votre propre compte.",
                    400,
                )
            if new_role is not None and new_role != UserRole.ARCHIVISTE:
                return (
                    None,
                    "Vous ne pouvez pas rétrograder votre propre rôle.",
                    400,
                )

        return cls.patch_user_for_admin(
            db,
            user_id=user_id,
            admin_user_id=admin_user_id,
            is_active=is_active,
            new_role=new_role,
            role_raw=role_raw,
        )

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
        user = UserService.get_user(db, user_id)
        if not user:
            return None, "Utilisateur non trouvé.", 404
        if is_active is not None:
            user.is_active = is_active
        if new_role is not None:
            user.role = new_role
        log_admin_action(
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
        user = UserService.get_user(db, user_id)
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
        email_sent = EmailService.send_password_reset_email(
            to_email=user.email,
            username=user.username,
            reset_token=reset_token,
            frontend_url=settings.FRONTEND_URL,
        )
        if not email_sent:
            return False, "Impossible d'envoyer l'email. Réessayez plus tard.", 500
        return True, None, 200

    @staticmethod
    def resend_verification_for_admin(
        db: Session, user_id: int
    ) -> Tuple[bool, bool, Optional[str], int]:
        user = UserService.get_user(db, user_id)
        if not user:
            return False, False, "Utilisateur non trouvé.", 404
        if user.is_email_verified:
            return True, True, None, 200
        verification_token = generate_verification_token()
        user.email_verification_token = verification_token
        user.email_verification_sent_at = datetime.now(timezone.utc)
        db.commit()
        email_sent = EmailService.send_verification_email(
            to_email=user.email,
            username=user.username,
            verification_token=verification_token,
            frontend_url=settings.FRONTEND_URL,
        )
        if not email_sent:
            return (
                False,
                False,
                "Impossible d'envoyer l'email. Réessayez plus tard.",
                500,
            )
        return True, False, None, 200

    @staticmethod
    def delete_user_for_admin(
        db: Session, user_id: int, admin_user_id: int
    ) -> Tuple[bool, Optional[str], int]:
        """
        Supprime définitivement un utilisateur (cascade sur toutes les données liées).
        Un admin ne peut pas supprimer son propre compte.

        Returns:
            (success, error_message, status_code)
        """
        if user_id == admin_user_id:
            return False, "Vous ne pouvez pas supprimer votre propre compte.", 400

        user = UserService.get_user(db, user_id)
        if not user:
            return False, "Utilisateur non trouvé.", 404

        log_admin_action(db, admin_user_id, "user_delete", "user", user_id, {"username": user.username})
        UserService.delete_user(db, user_id, auto_commit=True)
        return True, None, 200

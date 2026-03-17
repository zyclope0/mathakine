"""
Service d'orchestration pour la boundary session auth (Lot 4).

Responsabilité : login, refresh, validate-token, current-user, logout.
Pas d'accès DB direct dans les handlers — tout passe par ce service.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.security import decode_token
from app.services.auth_service import (
    _is_token_revoked_by_password_reset,
    authenticate_user_with_session,
    get_user_by_username,
    recover_refresh_token_from_access_token,
    refresh_access_token,
)
from app.utils.db_utils import sync_db_session

logger = get_logger(__name__)


def build_authenticated_user_payload(user) -> Dict[str, Any]:
    """
    Construit le payload utilisateur pour les réponses login/me.
    Déplacé du handler pour centraliser la logique métier.
    """
    from app.utils.unverified_access import get_unverified_access_scope

    access_scope = get_unverified_access_scope(user)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email if hasattr(user, "email") else None,
        "full_name": user.full_name if hasattr(user, "full_name") else None,
        "role": user.role.value if hasattr(user, "role") else None,
        "is_email_verified": (
            user.is_email_verified if hasattr(user, "is_email_verified") else False
        ),
        "access_scope": access_scope,
        "onboarding_completed_at": (
            user.onboarding_completed_at.isoformat()
            if getattr(user, "onboarding_completed_at", None)
            else None
        ),
        "grade_level": getattr(user, "grade_level", None),
        "grade_system": getattr(user, "grade_system", None),
        "preferred_difficulty": getattr(user, "preferred_difficulty", None),
        "learning_goal": getattr(user, "learning_goal", None),
        "practice_rhythm": getattr(user, "practice_rhythm", None),
    }


def perform_login(
    username: str,
    password: str,
    *,
    ip: Optional[str] = None,
    user_agent: str = "",
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Authentifie un utilisateur et prepare les donnees de login.
    Sync - execute via run_db_bound() depuis les handlers async.

    Returns:
        (user_payload, token_data) si succes - user_payload construit dans la session
        (None, None) si echec (credentials invalides)
    """
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    with sync_db_session() as db:
        user, token_data = authenticate_user_with_session(
            db,
            username,
            password,
            ip=ip,
            user_agent=user_agent,
            expires_at=expires_at,
        )
        if not user:
            return None, None
        # Construire le payload dans la session (evite User detache)
        user_payload = build_authenticated_user_payload(user)
    return user_payload, token_data


def recover_refresh_token_fallback(access_token: str) -> Optional[str]:
    """
    Recupere un refresh token a partir d'un access token (compatibilite historique).
    Utilise quand le client n'a plus que l'access_token en cookie.
    Sync - execute via run_db_bound() depuis les handlers async.
    """
    if not access_token or not access_token.strip():
        return None
    with sync_db_session() as db:
        return recover_refresh_token_from_access_token(db, access_token.strip())


def perform_refresh(
    refresh_token: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
    """
    Rafraichit un access token avec un refresh token valide.
    Sync - execute via run_db_bound() depuis les handlers async.

    Returns:
        (token_data, None, 200) si succes
        (None, error_message, status_code) si echec
    """
    with sync_db_session() as db:
        result = refresh_access_token(db, refresh_token)
        return result.token_data, result.error_message, result.status_code


def validate_access_token(token: str) -> Dict[str, Any]:
    """
    Valide un token d'acces JWT (type=access).
    Retourne le payload decode ou leve une exception.
    """
    payload = decode_token(token)
    return {"valid": True, "user_id": payload.get("sub")}


def get_current_user_payload(username: str, payload: dict) -> Optional[Dict[str, Any]]:
    """
    Recupere le payload utilisateur courant depuis la DB (sync).
    Sync - execute via run_db_bound() depuis la couche async auth.

    Args:
        username: sub du token JWT
        payload: payload decode du token (pour verification revocation)

    Returns:
        Dictionnaire user serialisable ou None si non trouve / revoque
    """
    with sync_db_session() as db:
        user = get_user_by_username(db, username)
        if user is None:
            return None
        if _is_token_revoked_by_password_reset(payload, user):
            return None
        from app.utils.unverified_access import get_unverified_access_scope

        access_scope = get_unverified_access_scope(user)
        is_email_verified = getattr(user, "is_email_verified", True)
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email if hasattr(user, "email") else None,
            "is_authenticated": True,
            "is_email_verified": is_email_verified,
            "access_scope": access_scope,
            "role": user.role.value if hasattr(user, "role") else None,
            "full_name": user.full_name if hasattr(user, "full_name") else None,
            "grade_level": user.grade_level if hasattr(user, "grade_level") else None,
            "grade_system": getattr(user, "grade_system", None),
            "learning_style": (
                user.learning_style if hasattr(user, "learning_style") else None
            ),
            "preferred_difficulty": (
                user.preferred_difficulty
                if hasattr(user, "preferred_difficulty")
                else None
            ),
            "onboarding_completed_at": (
                user.onboarding_completed_at.isoformat()
                if getattr(user, "onboarding_completed_at", None)
                else None
            ),
            "learning_goal": getattr(user, "learning_goal", None),
            "practice_rhythm": getattr(user, "practice_rhythm", None),
            "preferred_theme": (
                user.preferred_theme if hasattr(user, "preferred_theme") else None
            ),
            "accessibility_settings": (
                user.accessibility_settings
                if hasattr(user, "accessibility_settings")
                else None
            ),
            "created_at": (
                user.created_at.isoformat()
                if hasattr(user, "created_at") and user.created_at
                else None
            ),
            "total_points": (user.total_points if hasattr(user, "total_points") else 0),
            "current_level": (
                user.current_level if hasattr(user, "current_level") else 1
            ),
            "jedi_rank": (
                user.jedi_rank if hasattr(user, "jedi_rank") else "youngling"
            ),
        }

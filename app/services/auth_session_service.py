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
    authenticate_user_with_session,
    recover_refresh_token_from_access_token,
    refresh_access_token,
)
from app.utils.db_utils import db_session

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


async def perform_login(
    username: str,
    password: str,
    *,
    ip: Optional[str] = None,
    user_agent: str = "",
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Authentifie un utilisateur et prépare les données de login.

    Returns:
        (user_payload, token_data) si succès — user_payload construit dans la session
        (None, None) si échec (credentials invalides)
    """
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    async with db_session() as db:
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
        # Construire le payload dans la session (évite User détaché)
        user_payload = build_authenticated_user_payload(user)
    return user_payload, token_data


async def recover_refresh_token_fallback(access_token: str) -> Optional[str]:
    """
    Récupère un refresh token à partir d'un access token (compatibilité historique).
    Utilisé quand le client n'a plus que l'access_token en cookie.
    """
    if not access_token or not access_token.strip():
        return None
    async with db_session() as db:
        return recover_refresh_token_from_access_token(db, access_token.strip())


async def perform_refresh(
    refresh_token: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
    """
    Rafraîchit un access token avec un refresh token valide.

    Returns:
        (token_data, None, 200) si succès
        (None, error_message, status_code) si échec
    """
    async with db_session() as db:
        return refresh_access_token(db, refresh_token)


def validate_access_token(token: str) -> Dict[str, Any]:
    """
    Valide un token d'accès JWT (type=access).
    Retourne le payload décodé ou lève une exception.
    """
    payload = decode_token(token)
    return {"valid": True, "user_id": payload.get("sub")}

"""
Module d'authentification pour le backend Starlette.

Fournit les fonctions d'authentification utilisées par les handlers API,
ainsi que des décorateurs pour éliminer la duplication de code auth dans les handlers.
"""

import json
from functools import wraps

from starlette.responses import JSONResponse, StreamingResponse

from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.core.user_roles import serialize_user_role
from app.utils.error_handler import api_error_response

logger = get_logger(__name__)

from app.services.auth.auth_session_service import get_current_user_payload


async def get_current_user(request):  # noqa: C901
    """
    Récupère l'utilisateur actuellement authentifié depuis le cookie access_token.

    Args:
        request: Starlette Request object

    Returns:
        dict: Dictionnaire avec les informations de l'utilisateur ou None si non authentifié

    Example:
        {
            "id": 1,
            "username": "test_user",
            "email": "test@example.com",
            "is_authenticated": True
        }
    """
    try:
        # Essayer d'abord le cookie (comportement par défaut)
        access_token = request.cookies.get("access_token")

        # Si pas de cookie, essayer le header Authorization
        if not access_token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token = auth_header.replace("Bearer ", "")

        if not access_token:
            return None

        from starlette.exceptions import HTTPException

        from app.core.security import decode_token

        # Reutiliser le payload deja decode par AuthenticationMiddleware (evite double decode)
        payload = getattr(request.state, "auth_payload", None)
        if not payload or not payload.get("sub"):
            try:
                payload = decode_token(access_token)
            except HTTPException:
                return None
            except Exception as decode_error:
                logger.debug("Erreur lors du decodage du token: %s", decode_error)
                return None

        username = payload.get("sub")

        if not username:
            return None

        # Recuperer l'utilisateur depuis la DB via use case sync (threadpool)
        return await run_db_bound(get_current_user_payload, username, payload)

    except Exception as user_fetch_error:
        logger.error(
            "Erreur lors de la récupération de l'utilisateur: %s", user_fetch_error
        )
        return None


# ─── Décorateurs d'authentification ───────────────────────────────────────────
# Éliminent la duplication du code d'authentification dans les handlers.
#
# Usage:
#   @require_auth
#   async def my_handler(request):
#       current_user = request.state.user  # Garanti non-None
#
#   @optional_auth
#   async def my_handler(request):
#       current_user = request.state.user  # Peut être None
#
#   @require_auth_sse
#   async def my_stream_handler(request):
#       current_user = request.state.user  # Garanti non-None


def require_auth(handler):
    """Décorateur qui exige une authentification valide.

    Place l'utilisateur authentifié dans request.state.user.
    Retourne 401 JSON si non authentifié.
    """

    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return api_error_response(401, "Authentification requise")
        request.state.user = current_user
        return await handler(request, *args, **kwargs)

    return wrapper


def optional_auth(handler):
    """Décorateur qui tente l'authentification sans l'exiger.

    Place l'utilisateur dans request.state.user (None si non authentifié).
    Ne retourne jamais 401 - le handler décide quoi faire.
    """

    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        current_user = await get_current_user(request)
        if current_user and current_user.get("is_authenticated"):
            request.state.user = current_user
        else:
            request.state.user = None
        return await handler(request, *args, **kwargs)

    return wrapper


def require_role(role: str):
    """Décorateur qui exige un rôle spécifique (ex: admin pour l'espace admin).

    À combiner avec @require_auth. Place request.state.user.
    Retourne 403 si le rôle ne correspond pas.

    Usage:
        @require_auth
        @require_role("admin")
        async def admin_handler(request):
            ...
    """

    def decorator(handler):
        @wraps(handler)
        async def wrapper(request, *args, **kwargs):
            # S'assurer qu'on a l'utilisateur (require_auth ou get_current_user)
            current_user = getattr(request.state, "user", None)
            if not current_user:
                current_user = await get_current_user(request)
            if not current_user or not current_user.get("is_authenticated"):
                return api_error_response(401, "Authentification requise")
            current_role = serialize_user_role(current_user.get("role"))
            required_role = serialize_user_role(role)
            if current_role != required_role:
                return api_error_response(403, "Droits insuffisants")
            request.state.user = current_user
            return await handler(request, *args, **kwargs)

        return wrapper

    return decorator


# Alias pratique pour les routes admin
require_admin = require_role("admin")


def require_full_access(handler):
    """
    Décorateur qui exige access_scope="full".
    À utiliser APRES @require_auth. Bloque les utilisateurs non vérifiés
    après la période de grâce (45 min) — accès exercices uniquement.

    Retourne 403 si access_scope == "exercises_only".
    """

    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        current_user = getattr(request.state, "user", None)
        if not current_user:
            return api_error_response(401, "Authentification requise")
        scope = current_user.get("access_scope", "full")
        if scope == "exercises_only":
            return api_error_response(
                403, "Vérifiez votre adresse email pour accéder à cette fonctionnalité."
            )
        return await handler(request, *args, **kwargs)

    return wrapper


def require_auth_sse(handler):
    """Décorateur qui exige une authentification pour les endpoints SSE/streaming.

    Place l'utilisateur authentifié dans request.state.user.
    Retourne un flux SSE d'erreur si non authentifié (au lieu d'un JSON 401).
    """

    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):

            async def auth_error_generator():
                yield f"data: {json.dumps({'type': 'error', 'message': 'Authentification requise'})}\n\n"

            return StreamingResponse(
                auth_error_generator(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
            )
        request.state.user = current_user
        return await handler(request, *args, **kwargs)

    return wrapper

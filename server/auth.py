"""
Module d'authentification pour le backend Starlette.

Fournit les fonctions d'authentification utilisées par les handlers API,
ainsi que des décorateurs pour éliminer la duplication de code auth dans les handlers.
"""
import json
from functools import wraps

from starlette.responses import JSONResponse, StreamingResponse

from app.core.logging_config import get_logger

logger = get_logger(__name__)

from app.utils.db_utils import db_session


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

        from fastapi import HTTPException

        from app.core.security import decode_token
        from app.services.auth_service import get_user_by_username

        # Réutiliser le payload déjà décodé par AuthenticationMiddleware (évite double decode)
        payload = getattr(request.state, "auth_payload", None)
        if not payload or not payload.get("sub"):
            try:
                payload = decode_token(access_token)
            except HTTPException:
                return None
            except Exception as decode_error:
                logger.debug(f"Erreur lors du décodage du token: {decode_error}")
                return None

        username = payload.get("sub")
        
        if not username:
            return None
            
        # Récupérer l'utilisateur depuis la base de données
        async with db_session() as db:
            user = get_user_by_username(db, username)
            
            if user is None:
                return None
                
            # Retourner un dictionnaire sérialisable avec tous les champs profil
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email if hasattr(user, 'email') else None,
                "is_authenticated": True,
                "role": user.role.value if hasattr(user, 'role') else None,
                "full_name": user.full_name if hasattr(user, 'full_name') else None,
                "grade_level": user.grade_level if hasattr(user, 'grade_level') else None,
                "learning_style": user.learning_style if hasattr(user, 'learning_style') else None,
                "preferred_difficulty": user.preferred_difficulty if hasattr(user, 'preferred_difficulty') else None,
                "preferred_theme": user.preferred_theme if hasattr(user, 'preferred_theme') else None,
                "accessibility_settings": user.accessibility_settings if hasattr(user, 'accessibility_settings') else None,
                "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None,
                "total_points": user.total_points if hasattr(user, 'total_points') else 0,
                "current_level": user.current_level if hasattr(user, 'current_level') else 1,
                "jedi_rank": user.jedi_rank if hasattr(user, 'jedi_rank') else 'youngling',
            }
            
    except Exception as user_fetch_error:
        logger.error(f"Erreur lors de la récupération de l'utilisateur: {user_fetch_error}")
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
            return JSONResponse(
                {"error": "Authentification requise"},
                status_code=401
            )
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
    """Décorateur qui exige un rôle spécifique (ex: archiviste pour admin).
    
    À combiner avec @require_auth. Place request.state.user.
    Retourne 403 si le rôle ne correspond pas.
    
    Usage:
        @require_auth
        @require_role("archiviste")
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
                return JSONResponse(
                    {"error": "Authentification requise"},
                    status_code=401
                )
            if current_user.get("role") != role:
                return JSONResponse(
                    {"error": "Droits insuffisants"},
                    status_code=403
                )
            request.state.user = current_user
            return await handler(request, *args, **kwargs)
        return wrapper
    return decorator


# Alias pratique pour les routes admin
require_admin = require_role("archiviste")


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
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
        request.state.user = current_user
        return await handler(request, *args, **kwargs)
    return wrapper


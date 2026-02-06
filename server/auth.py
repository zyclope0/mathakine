"""
Module d'authentification pour le backend Starlette.

Fournit les fonctions d'authentification utilisées par les handlers API.
"""
from app.core.logging_config import get_logger

logger = get_logger(__name__)

from app.services.enhanced_server_adapter import EnhancedServerAdapter


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
            
        # Utiliser le service d'authentification pour décoder le token
        from fastapi import HTTPException

        from app.core.security import decode_token
        from app.services.auth_service import get_user_by_username

        # Décoder le token pour obtenir le nom d'utilisateur
        try:
            payload = decode_token(access_token)
        except HTTPException:
            # Token invalide ou expiré, retourner None silencieusement
            return None
        except Exception as decode_error:
            # Autre erreur de décodage
            logger.debug(f"Erreur lors du décodage du token: {decode_error}")
            return None
        
        username = payload.get("sub")
        
        if not username:
            return None
            
        # Récupérer l'utilisateur depuis la base de données
        db = EnhancedServerAdapter.get_db_session()
        try:
            user = get_user_by_username(db, username)
            
            if user is None:
                return None
                
            # Retourner un dictionnaire sérialisable
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email if hasattr(user, 'email') else None,
                "is_authenticated": True,
                "role": user.role.value if hasattr(user, 'role') else None
            }
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as user_fetch_error:
        logger.error(f"Erreur lors de la récupération de l'utilisateur: {user_fetch_error}")
        return None


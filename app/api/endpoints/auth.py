"""
Endpoints API pour l'authentification
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from app.api.deps import get_db_session, get_current_user
from app.schemas.user import UserLogin, Token, User, RefreshTokenRequest, RefreshTokenResponse
from app.services.auth_service import authenticate_user, create_user_token, refresh_access_token
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    user_login: UserLogin,
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Se connecter avec le nom d'utilisateur et le mot de passe.
    """
    logger.debug(f"Tentative de connexion reçue pour l'utilisateur: {user_login.username}")
    
    # Tenter d'authentifier l'utilisateur
    try:
        user = authenticate_user(db, user_login.username, user_login.password)
        if not user:
            logger.warning(f"Échec de connexion pour l'utilisateur: {user_login.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Créer les tokens d'accès et de rafraîchissement
        token_data = create_user_token(user)
        logger.info(f"Connexion réussie pour l'utilisateur: {user.username}")
        return token_data
    except HTTPException:
        # Re-lancer les HTTPException sans les modifier (401, 403, etc.)
        raise
    except Exception as e:
        # Ne transformer en 500 que les vraies erreurs non-HTTP
        logger.error(f"Erreur interne lors de la connexion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la connexion",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db_session)
) -> Any:
    """
    Rafraîchit le token d'accès en utilisant un refresh token valide.
    """
    try:
        new_token = refresh_access_token(db, request.refresh_token)
        return new_token
    except HTTPException:
        # Re-lancer les HTTPException sans les modifier (elles ont déjà le bon code de statut)
        raise
    except Exception as e:
        logger.error(f"Erreur lors du rafraîchissement du token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du rafraîchissement du token"
        )

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)) -> Any:
    """
    Se déconnecter et invalider le token.
    
    Note: Dans une implémentation JWT basique comme celle-ci, la déconnexion côté serveur
    est conceptuelle car les tokens JWT sont sans état. Le client doit simplement
    supprimer le token de son stockage.
    
    Pour une invalidation réelle du token, il faudrait implémenter une liste noire
    de tokens ou utiliser des tokens à courte durée de vie avec refresh tokens.
    """
    logger.info(f"Déconnexion de l'utilisateur: {current_user.username}")
    return {"detail": "Déconnecté avec succès"}


@router.get("/me", response_model=User)
def read_current_user(current_user: User = Depends(get_current_user)) -> Any:
    """
    Récupérer les informations de l'utilisateur actuellement connecté.
    """
    return current_user

"""
Endpoints API pour l'authentification
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from app.api.deps import get_db_session, get_current_user
from app.schemas.user import UserLogin, Token, User
from app.services.auth_service import authenticate_user, create_user_token
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
    # Tenter d'authentifier l'utilisateur
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        logger.warning(f"Échec de connexion pour l'utilisateur: {user_login.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer un token d'accès
    token_data = create_user_token(user)
    logger.info(f"Connexion réussie pour l'utilisateur: {user.username}")
    return token_data


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

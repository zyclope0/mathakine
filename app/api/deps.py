"""
Dépendances communes pour les API
"""
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.base import get_db
from typing import Generator, Optional
from jose import jwt, JWTError
from pydantic import ValidationError

from app.models.user import User, UserRole
from app.schemas.user import TokenData
from app.core.config import settings
from app.core.security import SECRET_KEY
from app.core.constants import SecurityConfig
from app.services.auth_service import get_user_by_username
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Endpoint d'authentification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db_session() -> Generator[Session, None, None]:
    """
    Dépendance pour obtenir une session de base de données.
    """
    db = get_db()
    try:
        yield from db
    finally:
        pass  # La fermeture est gérée dans get_db

def get_current_user(
    db: Session = Depends(get_db_session),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuel à partir du token JWT.
    
    Args:
        db: Session de base de données
        token: Token JWT
    
    Returns:
        Instance de l'utilisateur actuel
    
    Raises:
        HTTPException: Si le token est invalide ou l'utilisateur n'existe pas
    """
    try:
        # Décoder le token JWT
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM]
        )
        # Extraire les données du token
        token_data = TokenData(username=payload.get("sub"), role=payload.get("role"))
        if token_data.username is None:
            logger.warning("Token sans nom d'utilisateur")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError) as e:
        logger.warning(f"Erreur de validation du token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Récupérer l'utilisateur à partir du nom d'utilisateur dans le token
    user = get_user_by_username(db, token_data.username)
    if user is None:
        logger.warning(f"Utilisateur dans le token non trouvé: {token_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.warning(f"Tentative d'accès avec un compte inactif: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte utilisateur inactif",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuel actif.
    
    Args:
        current_user: Utilisateur actuel
    
    Returns:
        Instance de l'utilisateur actuel actif
    
    Raises:
        HTTPException: Si l'utilisateur n'est pas actif
    """
    if not current_user.is_active:
        logger.warning(f"Tentative d'accès avec un compte inactif: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compte utilisateur inactif"
        )
    return current_user

def get_current_maitre_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuel avec le rôle Maître.
    
    Args:
        current_user: Utilisateur actuel
    
    Returns:
        Instance de l'utilisateur actuel avec le rôle Maître
    
    Raises:
        HTTPException: Si l'utilisateur n'a pas le rôle Maître
    """
    if current_user.role != UserRole.MAITRE:
        logger.warning(f"Tentative d'accès à une fonctionnalité Maître par {current_user.username} (rôle: {current_user.role})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux Maîtres Jedi"
        )
    return current_user

def get_current_gardien_or_archiviste(current_user: User = Depends(get_current_user)) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuel avec le rôle Gardien ou Archiviste.
    
    Args:
        current_user: Utilisateur actuel
    
    Returns:
        Instance de l'utilisateur actuel avec le rôle Gardien ou Archiviste
    
    Raises:
        HTTPException: Si l'utilisateur n'a pas le rôle Gardien ou Archiviste
    """
    if current_user.role not in [UserRole.GARDIEN, UserRole.ARCHIVISTE]:
        logger.warning(f"Tentative d'accès à une fonctionnalité administrative par {current_user.username} (rôle: {current_user.role})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux Gardiens et Archivistes du Temple"
        )
    return current_user

def get_current_archiviste(current_user: User = Depends(get_current_user)) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuel avec le rôle Archiviste.
    
    Args:
        current_user: Utilisateur actuel
    
    Returns:
        Instance de l'utilisateur actuel avec le rôle Archiviste
    
    Raises:
        HTTPException: Si l'utilisateur n'a pas le rôle Archiviste
    """
    if current_user.role != UserRole.ARCHIVISTE:
        logger.warning(f"Tentative d'accès à une fonctionnalité Archiviste par {current_user.username} (rôle: {current_user.role})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux Archivistes du Temple"
        )
    return current_user

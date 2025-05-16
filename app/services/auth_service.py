"""
Service d'authentification pour gérer les utilisateurs et les connexions
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, TokenData
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Récupère un utilisateur par son nom d'utilisateur.
    
    Args:
        db: Session de base de données
        username: Nom d'utilisateur à rechercher
    
    Returns:
        Instance de User ou None si l'utilisateur n'existe pas
    """
    user = db.query(User).filter(User.username == username).first()
    logger.debug(f"Recherche utilisateur {username}: {'trouvé' if user else 'non trouvé'}")
    return user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Récupère un utilisateur par son email.
    
    Args:
        db: Session de base de données
        email: Email à rechercher
    
    Returns:
        Instance de User ou None si l'utilisateur n'existe pas
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Récupère un utilisateur par son ID.
    
    Args:
        db: Session de base de données
        user_id: ID de l'utilisateur à rechercher
    
    Returns:
        Instance de User ou None si l'utilisateur n'existe pas
    """
    return db.query(User).filter(User.id == user_id).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authentifie un utilisateur en vérifiant son nom d'utilisateur et mot de passe.
    
    Args:
        db: Session de base de données
        username: Nom d'utilisateur
        password: Mot de passe en clair
    
    Returns:
        Instance de User si l'authentification réussit, None sinon
    """
    logger.debug(f"Tentative d'authentification pour l'utilisateur: {username}")
    
    user = get_user_by_username(db, username)
    if not user:
        logger.warning(f"Utilisateur non trouvé: {username}")
        return None
        
    logger.debug(f"Utilisateur trouvé: {username}")
    logger.debug(f"Hash stocké: {user.hashed_password}")
    
    try:
        is_valid = verify_password(password, user.hashed_password)
        logger.debug(f"Résultat de la vérification du mot de passe: {is_valid}")
        
        if not is_valid:
            logger.warning(f"Mot de passe incorrect pour l'utilisateur: {username}")
            return None
            
        logger.info(f"Authentification réussie pour l'utilisateur: {username}")
        return user
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du mot de passe: {str(e)}")
        return None

def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Crée un nouvel utilisateur.
    
    Args:
        db: Session de base de données
        user_in: Données pour la création de l'utilisateur
    
    Returns:
        Instance du nouvel utilisateur créé
    
    Raises:
        HTTPException: Si un utilisateur avec le même nom ou email existe déjà
    """
    # Vérifier si un utilisateur avec le même nom existe déjà
    if get_user_by_username(db, user_in.username):
        logger.warning(f"Tentative de création d'un utilisateur avec un nom déjà utilisé: {user_in.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà utilisé"
        )
    
    # Vérifier si un utilisateur avec le même email existe déjà
    if get_user_by_email(db, user_in.email):
        logger.warning(f"Tentative de création d'un utilisateur avec un email déjà utilisé: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # Par défaut, les nouveaux utilisateurs sont des Padawans sauf spécification contraire
    role = user_in.role if user_in.role else UserRole.PADAWAN
    
    # Créer l'utilisateur avec les données fournies
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=role,
        grade_level=user_in.grade_level,
        learning_style=user_in.learning_style,
        preferred_difficulty=user_in.preferred_difficulty,
        preferred_theme=user_in.preferred_theme,
        accessibility_settings=user_in.accessibility_settings,
        is_active=True
    )
    
    # Ajouter l'utilisateur à la base de données
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Nouvel utilisateur créé: {user.username} (ID: {user.id})")
    return user

def create_user_token(user: User) -> dict:
    """
    Crée un token d'accès et un refresh token pour un utilisateur.
    
    Args:
        user: Instance de l'utilisateur
    
    Returns:
        Dictionnaire contenant le token d'accès, le refresh token et leur type
    """
    # Créer un access token avec une durée d'expiration courte
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Inclure le rôle de l'utilisateur dans les tokens
    additional_data = {"role": user.role, "type": "access"}
    refresh_data = {"role": user.role, "type": "refresh"}
    
    access_token = create_access_token(
        subject=user.username,
        expires_delta=access_token_expires,
        additional_data=additional_data
    )
    
    refresh_token = create_access_token(
        subject=user.username,
        expires_delta=refresh_token_expires,
        additional_data=refresh_data
    )
    
    logger.info(f"Tokens créés pour l'utilisateur: {user.username}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def refresh_access_token(db: Session, refresh_token: str) -> dict:
    """
    Crée un nouveau token d'accès à partir d'un refresh token valide.
    
    Args:
        db: Session de base de données
        refresh_token: Le refresh token à valider
    
    Returns:
        Nouveau token d'accès
        
    Raises:
        HTTPException: Si le refresh token est invalide ou expiré
    """
    try:
        # Vérifier et décoder le refresh token
        payload = decode_token(refresh_token)
        
        # Vérifier que c'est bien un refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
        
        # Récupérer l'utilisateur
        username = payload.get("sub")
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé"
            )
        
        # Créer un nouveau token d'accès
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        additional_data = {"role": user.role, "type": "access"}
        
        new_access_token = create_access_token(
            subject=user.username,
            expires_delta=access_token_expires,
            additional_data=additional_data
        )
        
        logger.info(f"Nouveau token d'accès créé pour l'utilisateur: {user.username}")
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du rafraîchissement du token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )

def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    """
    Met à jour les informations d'un utilisateur existant.
    
    Args:
        db: Session de base de données
        user: Instance de l'utilisateur à mettre à jour
        user_in: Données pour la mise à jour
    
    Returns:
        Instance de l'utilisateur mise à jour
    """
    # Mettre à jour le mot de passe si fourni
    if user_in.password:
        user.hashed_password = get_password_hash(user_in.password)
    
    # Mettre à jour les autres champs si fournis
    update_data = user_in.dict(exclude_unset=True, exclude={"password"})
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Utilisateur mis à jour: {user.username} (ID: {user.id})")
    return user 
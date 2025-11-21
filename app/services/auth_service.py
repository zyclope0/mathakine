"""
Service d'authentification pour gérer les utilisateurs et les connexions
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, TokenData
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.core.config import settings
from app.core.logging_config import get_logger
from app.utils.db_helpers import get_enum_value, adapt_enum_for_db

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
    except Exception as password_verification_error:
        logger.error(f"Erreur lors de la vérification du mot de passe: {str(password_verification_error)}")
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
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur est déjà utilisé"
        )
    
    # Vérifier si un utilisateur avec le même email existe déjà
    if get_user_by_email(db, user_in.email):
        logger.warning(f"Tentative de création d'un utilisateur avec un email déjà utilisé: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est déjà utilisé"
        )
    
    # Par défaut, les nouveaux utilisateurs sont des Padawans sauf spécification contraire
    if user_in.role:
        # Utiliser le rôle fourni (déjà une énumération grâce au schéma Pydantic)
        user_role = user_in.role
    else:
        # Rôle par défaut
        user_role = UserRole.PADAWAN
    
    # Créer l'utilisateur avec les données fournies
    current_time = datetime.now(timezone.utc)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_role,
        grade_level=user_in.grade_level,
        learning_style=user_in.learning_style,
        preferred_difficulty=user_in.preferred_difficulty,
        preferred_theme=user_in.preferred_theme,
        accessibility_settings=user_in.accessibility_settings,
        is_active=True,
        created_at=current_time,
        updated_at=current_time
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
    
    # Données pour les tokens - gérer le cas où role est string ou enum
    role_value = user.role if isinstance(user.role, str) else user.role.value
    token_data = {
        "sub": user.username, 
        "role": role_value
    }
    
    # Créer le token d'accès
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    # Données pour le token de rafraîchissement
    refresh_data = token_data.copy()
    refresh_data["type"] = "refresh"
    
    # Créer le token de rafraîchissement manuellement
    refresh_token = jwt.encode(
        {
            **refresh_data,
            "exp": datetime.now(timezone.utc) + refresh_token_expires
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    logger.info(f"Tokens créés pour l'utilisateur: {user.username}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id
    }

def refresh_access_token(db: Session, refresh_token: str) -> dict:
    """
    Rafraîchit un token d'accès JWT en utilisant un token de rafraîchissement valide.
    
    Args:
        db: Session de base de données
        refresh_token: Token de rafraîchissement à valider
    
    Returns:
        Dictionnaire contenant le nouveau token d'accès JWT et le type de token
        
    Raises:
        HTTPException: Si le token est invalide, expiré, ou si l'utilisateur n'existe plus
        RuntimeError: Si une erreur inattendue se produit
    """
    try:
        # Décoder le token sans vérifier l'expiration (pour pouvoir fournir un message spécifique)
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Vérifier que c'est bien un token de rafraîchissement
        token_type = payload.get("type")
        if token_type != "refresh":
            logger.warning(f"Tentative de rafraîchissement avec un token non-refresh: {token_type}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de rafraîchissement invalide"
            )
        
        # Extraire les informations utilisateur
        username = payload.get("sub")
        if not username:
            logger.warning("Tentative de rafraîchissement avec un token sans sujet")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
        
        # Vérifier que l'utilisateur existe toujours
        user = get_user_by_username(db, username)
        if not user:
            logger.warning(f"Tentative de rafraîchissement pour un utilisateur qui n'existe pas: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé"
            )
        
        # Vérifier que l'utilisateur est toujours actif
        if not user.is_active:
            logger.warning(f"Tentative de rafraîchissement pour un utilisateur inactif: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Compte utilisateur désactivé"
            )
        
        # Générer un nouveau token d'accès
        # Gérer le cas où role est string ou enum
        role_value = user.role if isinstance(user.role, str) else user.role.value
        access_token = create_access_token(
            data={"sub": user.username, "role": role_value}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except jwt.ExpiredSignatureError:
        logger.warning("Tentative de rafraîchissement avec un token expiré")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de rafraîchissement expiré"
        )
    except jwt.JWTError:
        logger.warning("Tentative de rafraîchissement avec un token JWT invalide")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )
    except HTTPException:
        # Re-lancer les HTTPException sans les modifier (elles ont déjà le bon code de statut)
        raise
    except RuntimeError:
        # Ne pas intercepter les RuntimeError pour permettre aux tests de les attraper
        logger.error("Erreur RuntimeError lors du rafraîchissement du token")
        raise
    except Exception as token_refresh_error:
        logger.error(f"Erreur lors du rafraîchissement du token: {str(token_refresh_error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
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
    update_data = user_in.model_dump(exclude_unset=True, exclude={"password"})
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Utilisateur mis à jour: {user.username} (ID: {user.id})")
    return user

def update_user_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
    """
    Met à jour le mot de passe d'un utilisateur après vérification du mot de passe actuel.
    
    Args:
        db: Session de base de données
        user: Instance de l'utilisateur
        current_password: Mot de passe actuel (pour vérification)
        new_password: Nouveau mot de passe
    
    Returns:
        True si la mise à jour a réussi, False sinon
        
    Raises:
        HTTPException: Si le mot de passe actuel est incorrect
    """
    # Vérifier le mot de passe actuel
    if not verify_password(current_password, user.hashed_password):
        logger.warning(f"Tentative de changement de mot de passe avec mot de passe actuel incorrect pour {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe actuel incorrect"
        )
    
    # Mettre à jour avec le nouveau mot de passe
    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.now(timezone.utc)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Mot de passe mis à jour pour l'utilisateur: {user.username}")
    return True 
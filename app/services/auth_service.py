"""
Service d'authentification pour gérer les utilisateurs et les connexions
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.core.types import TokenRefreshResponse, TokenResponse
from app.models.user import User, UserRole
from app.models.user_session import UserSession
from app.schemas.user import TokenData, UserCreate, UserUpdate
from app.utils.db_helpers import adapt_enum_for_db, get_enum_value
from app.utils.email_verification import (
    is_password_reset_token_expired,
    is_verification_token_expired,
)

logger = get_logger(__name__)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Délègue à UserService.get_user_by_username (source unique)."""
    from app.services.user_service import UserService

    return UserService.get_user_by_username(db, username)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Délègue à UserService.get_user_by_email (source unique)."""
    from app.services.user_service import UserService

    return UserService.get_user_by_email(db, email)


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Délègue à UserService.get_user (source unique)."""
    from app.services.user_service import UserService

    return UserService.get_user(db, user_id)


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

    if not user.is_active:
        logger.warning(f"Compte désactivé: {username}")
        return None

    logger.debug(f"Utilisateur trouvé: {username}")

    try:
        is_valid = verify_password(password, user.hashed_password)
        logger.debug(f"Résultat de la vérification du mot de passe: {is_valid}")

        if not is_valid:
            logger.warning(f"Mot de passe incorrect pour l'utilisateur: {username}")
            return None

        logger.info(f"Authentification réussie pour l'utilisateur: {username}")
        return user
    except Exception as password_verification_error:
        logger.error(
            f"Erreur lors de la vérification du mot de passe: {str(password_verification_error)}"
        )
        return None


def create_user(
    db: Session, user_in: UserCreate
) -> Tuple[Optional[User], Optional[str], int]:
    """
    Crée un nouvel utilisateur.

    Returns:
        (user, error_message, status_code)
        user si succès, sinon None + message + code HTTP.
    """
    if get_user_by_username(db, user_in.username):
        logger.warning(
            f"Tentative de création avec nom déjà utilisé: {user_in.username}"
        )
        return None, "Un compte avec ces informations existe déjà", 409

    if get_user_by_email(db, user_in.email):
        logger.warning(
            f"Tentative de création avec email déjà utilisé: {user_in.email}"
        )
        return None, "Un compte avec ces informations existe déjà", 409

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
        updated_at=current_time,
    )

    # Ajouter l'utilisateur à la base de données
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"Nouvel utilisateur créé: {user.username} (ID: {user.id})")
    return user, None, 201


def create_user_token(user: User) -> TokenResponse:
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
    token_data = {"sub": user.username, "role": role_value}

    # Créer le token d'accès
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )

    # Données pour le token de rafraîchissement
    refresh_data = token_data.copy()
    refresh_data["type"] = "refresh"

    # Créer le token de rafraîchissement manuellement
    refresh_token = jwt.encode(
        {**refresh_data, "exp": datetime.now(timezone.utc) + refresh_token_expires},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    # Vérifier que le refresh_token est bien créé
    if not refresh_token:
        logger.error(
            f"ERREUR: refresh_token non créé pour l'utilisateur: {user.username}"
        )
    else:
        logger.debug(
            f"Refresh token créé (longueur: {len(refresh_token)}) pour l'utilisateur: {user.username}"
        )

    logger.info(f"Tokens créés pour l'utilisateur: {user.username}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
    }


def refresh_access_token(
    db: Session, refresh_token: str
) -> Tuple[Optional[TokenRefreshResponse], Optional[str], int]:
    """
    Rafraîchit un token d'accès JWT en utilisant un token de rafraîchissement valide.

    Returns:
        (token_data, error_message, status_code)
    """
    try:
        logger.debug(
            f"Tentative de décodage du refresh_token (longueur: {len(refresh_token)})"
        )

        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": True},
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Tentative de rafraîchissement avec un token expiré")
            return None, "Token de rafraîchissement expiré", 401
        except JWTError as decode_error:
            logger.error(f"Erreur de décodage JWT: {str(decode_error)}")
            return None, "Token JWT invalide ou malformé", 401

        token_type = payload.get("type")
        logger.debug(f"Type de token décodé: {token_type}")
        if token_type != "refresh":
            logger.warning(
                f"Tentative de rafraîchissement avec un token non-refresh: {token_type}"
            )
            return None, f"Token de rafraîchissement invalide (type: {token_type})", 401

        username = payload.get("sub")
        if not username:
            logger.warning("Tentative de rafraîchissement avec un token sans sujet")
            return None, "Token invalide", 401

        user = get_user_by_username(db, username)
        if not user:
            logger.warning(
                f"Tentative de rafraîchissement pour un utilisateur qui n'existe pas: {username}"
            )
            return None, "Utilisateur non trouvé", 401

        if not user.is_active:
            logger.warning(
                f"Tentative de rafraîchissement pour un utilisateur inactif: {username}"
            )
            return None, "Compte utilisateur désactivé", 401

        new_token_data = create_user_token(user)
        return (
            {
                "access_token": new_token_data.get("access_token"),
                "refresh_token": new_token_data.get("refresh_token"),
                "token_type": "bearer",
            },
            None,
            200,
        )

    except RuntimeError:
        logger.error("Erreur RuntimeError lors du rafraîchissement du token")
        raise
    except Exception as token_refresh_error:
        logger.error(
            f"Erreur lors du rafraîchissement du token: {str(token_refresh_error)}"
        )
        return None, "Erreur interne du serveur", 500


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


def update_user_password(
    db: Session, user: User, current_password: str, new_password: str
) -> Tuple[bool, Optional[str]]:
    """
    Met à jour le mot de passe d'un utilisateur après vérification du mot de passe actuel.

    Returns:
        (True, None) si succès, (False, error_message) sinon.
    """
    if not verify_password(current_password, user.hashed_password):
        logger.warning(
            f"Tentative de changement de mot de passe avec mot de passe actuel incorrect pour {user.username}"
        )
        return False, "Mot de passe actuel incorrect"

    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.now(timezone.utc)

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"Mot de passe mis à jour pour l'utilisateur: {user.username}")
    return True, None


def verify_email_token(db: Session, token: str) -> Tuple[Optional[User], Optional[str]]:
    """
    Vérifie un token d'email et marque l'utilisateur comme vérifié si valide.

    Args:
        db: Session de base de données
        token: Token de vérification

    Returns:
        (user, error): user si succès, error parmi "invalid", "expired", "already_verified"
    """
    user = db.query(User).filter(User.email_verification_token == token).first()
    if not user:
        return None, "invalid"

    if is_verification_token_expired(user.email_verification_sent_at):
        return user, "expired"

    if user.is_email_verified:
        return user, "already_verified"

    user.is_email_verified = True
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    logger.info(f"Email vérifié pour l'utilisateur {user.username} ({user.email})")
    return user, None


def resend_verification_token(db: Session, user: User) -> str:
    """
    Génère et enregistre un nouveau token de vérification pour l'utilisateur.
    Returns: le token généré.
    """
    from app.utils.email_verification import generate_verification_token

    token = generate_verification_token()
    user.email_verification_token = token
    user.email_verification_sent_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return token


def create_session(
    db: Session,
    user_id: int,
    ip: Optional[str],
    user_agent: Optional[str],
    expires_at: datetime,
) -> UserSession:
    """Crée une entrée UserSession pour le suivi des sessions actives."""
    import secrets

    session_token = secrets.token_urlsafe(32)
    session_row = UserSession(
        user_id=user_id,
        session_token=session_token,
        device_info={"user_agent": (user_agent or "")[:500]} if user_agent else None,
        ip_address=ip,
        user_agent=(user_agent or "")[:2000] if user_agent else None,
        expires_at=expires_at,
    )
    db.add(session_row)
    db.commit()
    return session_row


def initiate_password_reset(db: Session, user: User) -> str:
    """
    Initialise la réinitialisation mot de passe : token + expiration.
    Returns: le token de réinitialisation.
    """
    from app.utils.email_verification import generate_verification_token

    token = generate_verification_token()
    user.password_reset_token = token
    user.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return token


def set_verification_token_for_new_user(db: Session, user: User, token: str) -> None:
    """Enregistre le token de vérification pour un nouvel utilisateur (register)."""
    user.email_verification_token = token
    user.email_verification_sent_at = datetime.now(timezone.utc)
    user.is_email_verified = False
    db.commit()
    db.refresh(user)


def reset_password_with_token(
    db: Session, token: str, new_password: str
) -> Tuple[Optional[User], Optional[str]]:
    """
    Réinitialise le mot de passe avec un token valide.

    Args:
        db: Session de base de données
        token: Token de réinitialisation
        new_password: Nouveau mot de passe (déjà validé par le handler)

    Returns:
        (user, error): user si succès, error parmi "invalid", "expired"
    """
    user = db.query(User).filter(User.password_reset_token == token).first()
    if not user:
        return None, "invalid"

    if is_password_reset_token_expired(user.password_reset_expires_at):
        return user, "expired"

    user.hashed_password = get_password_hash(new_password)
    user.password_reset_token = None
    user.password_reset_expires_at = None
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    logger.info(f"Mot de passe réinitialisé pour {user.username}")
    return user, None

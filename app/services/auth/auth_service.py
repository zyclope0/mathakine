"""
Service d'authentification pour gérer les utilisateurs et les connexions
"""

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional

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
from app.core.user_roles import (
    CanonicalUserRole,
    serialize_user_role,
    to_legacy_user_role_enum,
)
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.auth_result import (
    AuthenticateWithSessionResult,
    CreateUserResult,
    RefreshTokenResult,
    ResetPasswordTokenResult,
    UpdatePasswordResult,
    VerifyEmailTokenResult,
)
from app.schemas.user import TokenData, UserCreate, UserUpdate
from app.utils.email_verification import (
    is_password_reset_token_expired,
    is_verification_token_expired,
)

logger = get_logger(__name__)

# SEC-PII-LOGS-01: domain-separated HMAC prefixes so username vs email never collide.
_LOG_USERNAME_SALT = b"mathakine.auth.log.username\x1c"
_LOG_EMAIL_SALT = b"mathakine.auth.log.email\x1c"


def _mask_username_for_logs(username: str) -> str:
    """
    Pseudonyme stable pour les logs (HMAC-SHA256 tronqué, clé = SECRET_KEY).
    Ne pas utiliser pour affichage utilisateur : diagnostic support / corrélation uniquement.
    """
    if not username:
        return "user#(empty)"
    key = settings.SECRET_KEY.encode("utf-8")
    digest = hmac.new(
        key, _LOG_USERNAME_SALT + username.encode("utf-8"), hashlib.sha256
    ).hexdigest()[:12]
    return f"user#{digest}"


def _mask_email_for_logs(email: str) -> str:
    """Comme _mask_username_for_logs, pour les emails (normalisés en minuscules)."""
    if not email or not email.strip():
        return "email#(empty)"
    key = settings.SECRET_KEY.encode("utf-8")
    normalized = email.strip().lower()
    digest = hmac.new(
        key, _LOG_EMAIL_SALT + normalized.encode("utf-8"), hashlib.sha256
    ).hexdigest()[:12]
    return f"email#{digest}"


# AUTH-FALLBACK-02: grace window for refresh recovery from an expired access JWT only.
# Previously 7d — excessively long reuse surface; 1h balances legacy clients vs risk.
ACCESS_TOKEN_FALLBACK_MAX_AGE_SECONDS = 3600


def _is_token_revoked_by_password_reset(payload: dict, user: User) -> bool:
    """
    Vérifie si un token (access ou refresh) a été émis avant le dernier reset password.
    Si user.password_changed_at est défini et que le token a été émis avant, il est révoqué.
    """
    pwd_changed = getattr(user, "password_changed_at", None)
    if not pwd_changed:
        return False
    iat = payload.get("iat")
    if iat is None:
        return True
    try:
        token_issued_at = datetime.fromtimestamp(int(float(iat)), tz=timezone.utc)
        if pwd_changed.tzinfo is None:
            pwd_changed = pwd_changed.replace(tzinfo=timezone.utc)
        return token_issued_at < pwd_changed
    except (TypeError, ValueError, OSError):
        return True


def _flush_or_commit(db: Session, *, auto_commit: bool) -> None:
    """Persiste la transaction courante sans imposer un commit global."""
    if auto_commit:
        db.commit()
    else:
        db.flush()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Délègue à UserService.get_user_by_username (source unique)."""
    from app.services.users.user_service import UserService

    return UserService.get_user_by_username(db, username)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Délègue à UserService.get_user_by_email (source unique)."""
    from app.services.users.user_service import UserService

    return UserService.get_user_by_email(db, email)


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Délègue à UserService.get_user (source unique)."""
    from app.services.users.user_service import UserService

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
    logger.debug(
        "Tentative d'authentification user_alias={}",
        _mask_username_for_logs(username),
    )

    user = get_user_by_username(db, username)
    if not user:
        logger.warning(
            "Utilisateur non trouvé user_alias={}",
            _mask_username_for_logs(username),
        )
        return None

    if not user.is_active:
        logger.warning(
            "Compte désactivé user_id={} user_alias={}",
            user.id,
            _mask_username_for_logs(username),
        )
        return None

    logger.debug(
        "Utilisateur trouvé user_id={} user_alias={}",
        user.id,
        _mask_username_for_logs(username),
    )

    try:
        is_valid = verify_password(password, user.hashed_password)
        logger.debug("Résultat de la vérification du mot de passe: %s", is_valid)

        if not is_valid:
            logger.warning(
                "Mot de passe incorrect user_id={} user_alias={}",
                user.id,
                _mask_username_for_logs(username),
            )
            return None

        logger.info(
            "Authentification réussie user_id={} user_alias={}",
            user.id,
            _mask_username_for_logs(username),
        )
        return user
    except Exception as password_verification_error:
        logger.error(
            "Erreur lors de la vérification du mot de passe: %s",
            str(password_verification_error),
        )
        return None


def create_user(
    db: Session, user_in: UserCreate, *, auto_commit: bool = True
) -> CreateUserResult:
    """
    Crée un nouvel utilisateur.

    Returns:
        CreateUserResult avec user si succès, sinon error_message + status_code.
    """
    if get_user_by_username(db, user_in.username):
        logger.warning(
            "Tentative de création avec nom déjà utilisé user_alias={}",
            _mask_username_for_logs(user_in.username),
        )
        return CreateUserResult(
            user=None,
            error_message="Un compte avec ces informations existe déjà",
            status_code=409,
        )

    if get_user_by_email(db, user_in.email):
        logger.warning(
            "Tentative de création avec email déjà utilisé email_alias={}",
            _mask_email_for_logs(user_in.email),
        )
        return CreateUserResult(
            user=None,
            error_message="Un compte avec ces informations existe déjà",
            status_code=409,
        )

    # Par défaut, les nouveaux utilisateurs sont des apprenants.
    if user_in.role:
        user_role = to_legacy_user_role_enum(user_in.role)
    else:
        user_role = to_legacy_user_role_enum(CanonicalUserRole.APPRENANT)

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

    db.add(user)
    _flush_or_commit(db, auto_commit=auto_commit)
    db.refresh(user)

    logger.info(
        "Nouvel utilisateur créé user_id={} user_alias={}",
        user.id,
        _mask_username_for_logs(user.username),
    )
    return CreateUserResult(user=user, error_message=None, status_code=201)


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
    role_value = serialize_user_role(user.role)
    token_data = {"sub": user.username, "role": role_value}

    # Créer le token d'accès
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )

    # Données pour le token de rafraîchissement (iat pour révocation post-reset)
    now = datetime.now(timezone.utc)
    refresh_data = token_data.copy()
    refresh_data["type"] = "refresh"
    refresh_data["iat"] = int(now.timestamp())
    refresh_data["exp"] = int((now + refresh_token_expires).timestamp())

    refresh_token = jwt.encode(
        refresh_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    # Vérifier que le refresh_token est bien créé
    if not refresh_token:
        logger.error(
            "ERREUR: refresh_token non créé user_id={} user_alias={}",
            user.id,
            _mask_username_for_logs(user.username),
        )
    else:
        logger.debug(
            "Refresh token créé (longueur: {}) user_id={} user_alias={}",
            len(refresh_token),
            user.id,
            _mask_username_for_logs(user.username),
        )

    logger.info(
        "Tokens créés user_id={} user_alias={}",
        user.id,
        _mask_username_for_logs(user.username),
    )
    user_id = int(user.id) if user.id is not None else None
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user_id,
    }


def refresh_access_token(db: Session, refresh_token: str) -> RefreshTokenResult:
    """
    Rafraîchit un token d'accès JWT en utilisant un token de rafraîchissement valide.

    Returns:
        RefreshTokenResult avec token_data si succès, sinon error_message + status_code.
    """
    try:
        logger.debug(
            "Tentative de décodage du refresh_token (longueur: %s)", len(refresh_token)
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
            return RefreshTokenResult(
                token_data=None,
                error_message="Token de rafraîchissement expiré",
                status_code=401,
            )
        except JWTError as decode_error:
            logger.error("Erreur de décodage JWT: %s", str(decode_error))
            return RefreshTokenResult(
                token_data=None,
                error_message="Token JWT invalide ou malformé",
                status_code=401,
            )

        token_type = payload.get("type")
        logger.debug("Type de token décodé: %s", token_type)
        if token_type != "refresh":
            logger.warning(
                "Tentative de rafraîchissement avec un token non-refresh: %s",
                token_type,
            )
            return RefreshTokenResult(
                token_data=None,
                error_message=f"Token de rafraîchissement invalide (type: {token_type})",
                status_code=401,
            )

        username = payload.get("sub")
        if not username:
            logger.warning("Tentative de rafraîchissement avec un token sans sujet")
            return RefreshTokenResult(
                token_data=None, error_message="Token invalide", status_code=401
            )

        user = get_user_by_username(db, username)
        if not user:
            logger.warning(
                "Tentative de rafraîchissement pour un utilisateur inexistant user_alias={}",
                _mask_username_for_logs(str(username)),
            )
            return RefreshTokenResult(
                token_data=None,
                error_message="Utilisateur non trouvé",
                status_code=401,
            )

        if not user.is_active:
            logger.warning(
                "Tentative de rafraîchissement pour un utilisateur inactif user_id={} user_alias={}",
                user.id,
                _mask_username_for_logs(str(username)),
            )
            return RefreshTokenResult(
                token_data=None,
                error_message="Compte utilisateur désactivé",
                status_code=401,
            )

        if _is_token_revoked_by_password_reset(payload, user):
            logger.warning(
                "Refresh token rejeté (révoqué par reset password) user_id={} user_alias={}",
                user.id,
                _mask_username_for_logs(str(username)),
            )
            return RefreshTokenResult(
                token_data=None,
                error_message="Token de rafraîchissement expiré",
                status_code=401,
            )

        new_token_data = create_user_token(user)
        return RefreshTokenResult(
            token_data={
                "access_token": new_token_data["access_token"],
                "refresh_token": new_token_data["refresh_token"],
                "token_type": "bearer",
            },
            error_message=None,
            status_code=200,
        )

    except RuntimeError:
        logger.error("Erreur RuntimeError lors du rafraîchissement du token")
        raise
    except Exception as token_refresh_error:
        logger.error(
            "Erreur lors du rafraîchissement du token: %s", str(token_refresh_error)
        )
        return RefreshTokenResult(
            token_data=None,
            error_message="Erreur interne du serveur",
            status_code=500,
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
    _flush_or_commit(db, auto_commit=True)
    db.refresh(user)

    logger.info(
        "Utilisateur mis à jour user_id={} user_alias={}",
        user.id,
        _mask_username_for_logs(user.username),
    )
    return user


def update_user_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
    *,
    auto_commit: bool = True,
) -> UpdatePasswordResult:
    """
    Met à jour le mot de passe d'un utilisateur après vérification du mot de passe actuel.

    Returns:
        UpdatePasswordResult avec is_success et error_message.
    """
    if not verify_password(current_password, user.hashed_password):
        logger.warning(
            "Tentative de changement de mot de passe avec mot de passe actuel incorrect user_id={} user_alias={}",
            user.id,
            _mask_username_for_logs(user.username),
        )
        return UpdatePasswordResult(
            is_success=False, error_message="Mot de passe actuel incorrect"
        )

    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.now(timezone.utc)

    db.add(user)
    _flush_or_commit(db, auto_commit=auto_commit)
    db.refresh(user)

    logger.info(
        "Mot de passe mis à jour user_id={} user_alias={}",
        user.id,
        _mask_username_for_logs(user.username),
    )
    return UpdatePasswordResult(is_success=True, error_message=None)


def verify_email_token(
    db: Session, token: str, *, auto_commit: bool = True
) -> VerifyEmailTokenResult:
    """
    Vérifie un token d'email et marque l'utilisateur comme vérifié si valide.

    Args:
        db: Session de base de données
        token: Token de vérification

    Returns:
        VerifyEmailTokenResult avec user et error_code (None si succès).
    """
    user = db.query(User).filter(User.email_verification_token == token).first()
    if not user:
        return VerifyEmailTokenResult(user=None, error_code="invalid")

    if is_verification_token_expired(user.email_verification_sent_at):
        return VerifyEmailTokenResult(user=user, error_code="expired")

    if user.is_email_verified:
        return VerifyEmailTokenResult(user=user, error_code="already_verified")

    user.is_email_verified = True
    user.updated_at = datetime.now(timezone.utc)
    _flush_or_commit(db, auto_commit=auto_commit)
    db.refresh(user)
    logger.info(
        "Email vérifié user_id={} user_alias={}",
        user.id,
        _mask_username_for_logs(user.username),
    )
    return VerifyEmailTokenResult(user=user, error_code=None)


def resend_verification_token(
    db: Session, user: User, *, auto_commit: bool = True
) -> str:
    """
    Génère et enregistre un nouveau token de vérification pour l'utilisateur.
    Returns: le token généré.
    """
    from app.utils.email_verification import generate_verification_token

    token = generate_verification_token()
    user.email_verification_token = token
    user.email_verification_sent_at = datetime.now(timezone.utc)
    _flush_or_commit(db, auto_commit=auto_commit)
    db.refresh(user)
    return token


def create_session(
    db: Session,
    user_id: int,
    ip: Optional[str],
    user_agent: Optional[str],
    expires_at: datetime,
    *,
    auto_commit: bool = True,
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
    _flush_or_commit(db, auto_commit=auto_commit)
    db.refresh(session_row)
    return session_row


def initiate_password_reset(
    db: Session, user: User, *, auto_commit: bool = True
) -> str:
    """
    Initialise la réinitialisation mot de passe : token + expiration.
    Returns: le token de réinitialisation.
    """
    from app.utils.email_verification import generate_verification_token

    token = generate_verification_token()
    user.password_reset_token = token
    user.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    user.updated_at = datetime.now(timezone.utc)
    _flush_or_commit(db, auto_commit=auto_commit)
    db.refresh(user)
    return token


def set_verification_token_for_new_user(
    db: Session, user: User, token: str, *, auto_commit: bool = True
) -> None:
    """Enregistre le token de vérification pour un nouvel utilisateur (register)."""
    user.email_verification_token = token
    user.email_verification_sent_at = datetime.now(timezone.utc)
    user.is_email_verified = False
    _flush_or_commit(db, auto_commit=auto_commit)
    db.refresh(user)


def reset_password_with_token(
    db: Session, token: str, new_password: str, *, auto_commit: bool = True
) -> ResetPasswordTokenResult:
    """
    Réinitialise le mot de passe avec un token valide.

    Args:
        db: Session de base de données
        token: Token de réinitialisation
        new_password: Nouveau mot de passe (déjà validé par le handler)

    Returns:
        ResetPasswordTokenResult avec user et error_code (None si succès).
    """
    user = db.query(User).filter(User.password_reset_token == token).first()
    if not user:
        return ResetPasswordTokenResult(user=None, error_code="invalid")

    if is_password_reset_token_expired(user.password_reset_expires_at):
        return ResetPasswordTokenResult(user=user, error_code="expired")

    now = datetime.now(timezone.utc)
    user.hashed_password = get_password_hash(new_password)
    user.password_reset_token = None
    user.password_reset_expires_at = None
    user.password_changed_at = now
    user.updated_at = now
    # Révoquer toutes les sessions via la relation (évite StaleDataError du bulk delete)
    for s in list(user.user_sessions):
        db.delete(s)
    _flush_or_commit(db, auto_commit=auto_commit)
    db.refresh(user)
    logger.info(
        "Mot de passe réinitialisé user_id={} user_alias={}",
        user.id,
        _mask_username_for_logs(user.username),
    )
    return ResetPasswordTokenResult(user=user, error_code=None)


def create_registered_user_with_verification(
    db: Session, user_in: UserCreate, verification_token: str
) -> CreateUserResult:
    """
    Crée un utilisateur et son token de vérification en un seul commit.
    """
    result = create_user(db, user_in, auto_commit=False)
    if not result.is_success:
        return result

    set_verification_token_for_new_user(
        db,
        result.user,
        verification_token,
        auto_commit=False,
    )
    db.commit()
    db.refresh(result.user)
    return CreateUserResult(user=result.user, error_message=None, status_code=201)


def authenticate_user_with_session(
    db: Session,
    username: str,
    password: str,
    *,
    ip: Optional[str],
    user_agent: Optional[str],
    expires_at: datetime,
) -> AuthenticateWithSessionResult:
    """
    Authentifie un utilisateur, crée sa session et commit une seule fois.
    """
    user = authenticate_user(db, username, password)
    if not user:
        return AuthenticateWithSessionResult()

    token_data = create_user_token(user)
    create_session(
        db,
        user.id,
        ip,
        user_agent,
        expires_at,
        auto_commit=False,
    )
    db.commit()
    return AuthenticateWithSessionResult(user=user, token_data=token_data)


def recover_refresh_token_from_access_token(
    db: Session,
    access_token: str,
    *,
    max_age_seconds: int = ACCESS_TOKEN_FALLBACK_MAX_AGE_SECONDS,
) -> Optional[str]:
    """
    Récupère un refresh token pour un utilisateur existant à partir d'un access token.

    Utilisé comme chemin de compatibilité quand seul l'access_token historique est
    encore présent côté client. Le token peut être expiré, mais seulement depuis
    au plus ``max_age_seconds`` (défaut : ``ACCESS_TOKEN_FALLBACK_MAX_AGE_SECONDS``).
    """
    try:
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )
    except JWTError:
        logger.debug("Fallback refresh refusé: access_token invalide")
        return None

    # AUTH-FALLBACK-02: only accept access tokens — reject refresh tokens to
    # prevent type-confusion bypass (a refresh token would otherwise mint new
    # tokens without going through the standard refresh_access_token path).
    if payload.get("type") != "access":
        logger.warning("Fallback refresh refusé: type de token invalide (%s)", payload.get("type"))
        return None

    exp = payload.get("exp")
    username = payload.get("sub")
    if exp is None or not username:
        logger.warning("Fallback refresh refusé: claims exp/sub manquants")
        return None

    age_seconds = datetime.now(timezone.utc).timestamp() - exp
    # Reject tokens that have not yet expired — they should use the normal
    # auth flow, not the expired-access-token recovery path.
    if age_seconds < 0:
        logger.warning("Fallback refresh refusé: access_token pas encore expiré")
        return None
    if age_seconds > max_age_seconds:
        logger.warning(
            "Fallback refresh refusé: access_token expiré depuis plus de {} secondes",
            max_age_seconds,
        )
        return None

    user = get_user_by_username(db, username)
    if not user or not user.is_active:
        logger.warning(
            "Fallback refresh refusé: utilisateur introuvable ou inactif user_alias={}",
            _mask_username_for_logs(str(username)),
        )
        return None

    if _is_token_revoked_by_password_reset(payload, user):
        logger.warning(
            "Fallback refresh refusé: access_token révoqué par reset password user_id={} user_alias={}",
            user.id,
            _mask_username_for_logs(str(username)),
        )
        return None

    token_data = create_user_token(user)
    return token_data.get("refresh_token")

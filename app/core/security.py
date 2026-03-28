"""
Utilitaires de sécurité pour l'authentification
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import bcrypt
from jose import JWTError, jwt
from starlette.exceptions import HTTPException

from app.core.config import settings
from app.core.constants import SecurityConfig
from app.core.logging_config import get_logger

# Obtenir un logger nommé pour ce module
logger = get_logger(__name__)

# Clé secrète pour la signature des tokens (à mettre en variable d'environnement en production)
SECRET_KEY = settings.SECRET_KEY


def decode_token(token: str) -> dict:
    """
    Décode et vérifie un token JWT d'accès (type=access).
    Rejette les refresh tokens pour éviter leur réutilisation comme access.

    Args:
        token: Le token JWT à décoder (access token uniquement)

    Returns:
        Le contenu décodé du token

    Raises:
        HTTPException: Si le token est invalide, expiré ou n'est pas un access token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
        if payload.get("type") != "access":
            logger.debug(
                "Token rejeté: type attendu 'access', reçu %s", payload.get("type")
            )
            raise HTTPException(status_code=401, detail="Token invalide ou expiré")
        return payload
    except HTTPException:
        raise
    except JWTError as jwt_decode_error:
        # Logger en debug plutôt qu'en error car c'est normal si le token est invalide/expiré
        error_msg = str(jwt_decode_error)
        if "Signature verification failed" in error_msg:
            logger.debug(f"Signature verification failed (token invalide ou expiré)")
        else:
            logger.debug(f"Erreur lors du décodage du token: {error_msg}")
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT d'accès

    Args:
        data: Données à inclure dans le token
        expires_delta: Délai d'expiration du token

    Returns:
        Token encodé
    """
    to_encode = data.copy()

    # Convertir les objets enum en valeurs de chaîne
    for key, value in to_encode.items():
        if hasattr(value, "value"):
            to_encode[key] = value.value

    # Calculer l'expiration et l'émission
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Ajouter exp, iat (révocation post-reset) et type — iat en timestamp pour JWT
    to_encode.update({"exp": expire, "iat": int(now.timestamp()), "type": "access"})

    # Encoder le token
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe en clair correspond à sa version hachée.

    Args:
        plain_password: Mot de passe en clair
        hashed_password: Mot de passe haché à comparer

    Returns:
        True si les mots de passe correspondent, False sinon
    """
    logger.debug("Vérification du mot de passe")

    try:
        # S'assurer que le mot de passe est une chaîne UTF-8 valide
        if not isinstance(plain_password, str):
            plain_password = str(plain_password)

        # Limiter la longueur à 72 bytes pour bcrypt (sécurité)
        password_bytes = plain_password.encode("utf-8")
        if len(password_bytes) > 72:
            logger.warning(
                f"Mot de passe trop long ({len(password_bytes)} bytes), tronqué à 72 bytes"
            )
            plain_password = password_bytes[:72].decode("utf-8", errors="ignore")

        # Utiliser bcrypt directement au lieu de passlib pour éviter les warnings de compatibilité
        # Convertir le hash en bytes si c'est une string
        if isinstance(hashed_password, str):
            hashed_password_bytes = hashed_password.encode("utf-8")
        else:
            hashed_password_bytes = hashed_password

        result = bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password_bytes)
        logger.debug(f"Résultat de la vérification: {result}")
        return result
    except Exception as password_verification_error:
        logger.error(
            f"Erreur lors de la vérification du mot de passe: {str(password_verification_error)}"
        )
        raise


def get_password_hash(password: str) -> str:
    """
    Crée un hash sécurisé d'un mot de passe.

    Args:
        password: Mot de passe en clair

    Returns:
        Version hachée du mot de passe
    """
    logger.debug(f"Génération du hash pour le mot de passe")
    try:
        # Utiliser bcrypt directement au lieu de passlib pour éviter les warnings de compatibilité
        # Générer un salt et hasher le mot de passe
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
        hashed = hashed_bytes.decode("utf-8")
        logger.debug("Hash mot de passe généré")
        return hashed
    except Exception as password_hashing_error:
        logger.error(
            f"Erreur lors de la génération du hash: {str(password_hashing_error)}"
        )
        raise


def get_cookie_config() -> Tuple[str, bool]:
    """Source unique pour la politique SameSite/Secure des cookies auth.

    Returns:
        (samesite, secure) — "none"/True en prod, "lax"/False en dev.
    """
    is_production = (
        os.getenv("NODE_ENV") == "production"
        or os.getenv("ENVIRONMENT") == "production"
        or os.getenv("MATH_TRAINER_PROFILE") == "prod"
    )
    return ("none" if is_production else "lax", is_production)


# --------------------------------------------------------------------------- #
# Diagnostic state token (C1 - integrity)                                      #
# --------------------------------------------------------------------------- #

DIAGNOSTIC_STATE_PURPOSE = "diagnostic_state"
DIAGNOSTIC_STATE_EXPIRY_MINUTES = 60


def sign_diagnostic_state(state: dict) -> str:
    """
    Signe un état diagnostic pour garantir son intégrité.
    Utilisé par le flux /start, /question, /answer, /complete.

    Returns:
        Token JWT signé contenant l'état.
    """
    from datetime import timedelta

    to_encode = {
        "purpose": DIAGNOSTIC_STATE_PURPOSE,
        "state": state,
    }
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=DIAGNOSTIC_STATE_EXPIRY_MINUTES
    )
    to_encode["exp"] = expire
    to_encode["iat"] = int(datetime.now(timezone.utc).timestamp())
    return jwt.encode(to_encode, SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)


def verify_diagnostic_state(token: str) -> Optional[dict]:
    """
    Vérifie et décode un token d'état diagnostic.

    Returns:
        Le dict state contenu dans le token, ou None si invalide.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
        if payload.get("purpose") != DIAGNOSTIC_STATE_PURPOSE:
            return None
        return payload.get("state")
    except JWTError:
        return None


def validate_password_strength(password: str) -> Optional[str]:
    """Valide la force d'un mot de passe. Source unique pour handlers et schemas.

    Returns:
        None si valide, sinon le message d'erreur (str).
    """
    if not password or len(password) < 8:
        return "Le mot de passe doit contenir au moins 8 caractères"
    if not any(c.isdigit() for c in password):
        return "Le mot de passe doit contenir au moins un chiffre"
    if not any(c.isupper() for c in password):
        return "Le mot de passe doit contenir au moins une majuscule"
    return None

"""
Utilitaires de sécurité pour l'authentification
"""
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, Optional, Union

import bcrypt
from fastapi import HTTPException
from jose import JWTError, jwt

from app.core.config import settings
from app.core.constants import SecurityConfig
from app.core.logging_config import get_logger

# Obtenir un logger nommé pour ce module
logger = get_logger(__name__)

# Clé secrète pour la signature des tokens (à mettre en variable d'environnement en production)
SECRET_KEY = settings.SECRET_KEY

def decode_token(token: str) -> dict:
    """
    Décode et vérifie un token JWT.
    
    Args:
        token: Le token JWT à décoder
        
    Returns:
        Le contenu décodé du token
        
    Raises:
        HTTPException: Si le token est invalide ou expiré
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
        return payload
    except JWTError as jwt_decode_error:
        # Logger en debug plutôt qu'en error car c'est normal si le token est invalide/expiré
        error_msg = str(jwt_decode_error)
        if "Signature verification failed" in error_msg:
            logger.debug(f"Signature verification failed (token invalide ou expiré)")
        else:
            logger.debug(f"Erreur lors du décodage du token: {error_msg}")
        raise HTTPException(
            status_code=401,
            detail="Token invalide ou expiré"
        )

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
        if hasattr(value, 'value'):
            to_encode[key] = value.value
    
    # Calculer l'expiration
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Ajouter l'expiration et le type de token
    to_encode.update({"exp": expire, "type": "access"})
    
    # Encoder le token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
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
    logger.debug(f"Vérification du mot de passe")
    logger.debug(f"Mot de passe en clair: {plain_password}")
    logger.debug(f"Hash à comparer: {hashed_password}")
    
    try:
        # S'assurer que le mot de passe est une chaîne UTF-8 valide
        if not isinstance(plain_password, str):
            plain_password = str(plain_password)
        
        # Limiter la longueur à 72 bytes pour bcrypt (sécurité)
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            logger.warning(f"Mot de passe trop long ({len(password_bytes)} bytes), tronqué à 72 bytes")
            plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
        
        # Utiliser bcrypt directement au lieu de passlib pour éviter les warnings de compatibilité
        # Convertir le hash en bytes si c'est une string
        if isinstance(hashed_password, str):
            hashed_password_bytes = hashed_password.encode('utf-8')
        else:
            hashed_password_bytes = hashed_password
        
        result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_bytes)
        logger.debug(f"Résultat de la vérification: {result}")
        return result
    except Exception as password_verification_error:
        logger.error(f"Erreur lors de la vérification du mot de passe: {str(password_verification_error)}")
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
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
        hashed = hashed_bytes.decode('utf-8')
        logger.debug(f"Hash généré: {hashed}")
        return hashed
    except Exception as password_hashing_error:
        logger.error(f"Erreur lors de la génération du hash: {str(password_hashing_error)}")
        raise 
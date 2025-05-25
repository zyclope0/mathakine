"""
Utilitaires de sécurité pour l'authentification
"""
from datetime import datetime, timedelta, UTC, timezone
from typing import Optional, Union, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.constants import SecurityConfig
from app.core.config import settings
from app.core.logging_config import get_logger
from fastapi import HTTPException

# Obtenir un logger nommé pour ce module
logger = get_logger(__name__)

# Contexte pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    except JWTError as e:
        logger.error(f"Erreur lors du décodage du token: {str(e)}")
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
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Résultat de la vérification: {result}")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du mot de passe: {str(e)}")
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
        hashed = pwd_context.hash(password)
        logger.debug(f"Hash généré: {hashed}")
        return hashed
    except Exception as e:
        logger.error(f"Erreur lors de la génération du hash: {str(e)}")
        raise 
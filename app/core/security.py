"""
Utilitaires de sécurité pour l'authentification
"""
from datetime import datetime, timedelta, UTC
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

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None,
    additional_data: Optional[dict] = None
) -> str:
    """
    Crée un token JWT (Cristal d'Identité) pour l'utilisateur.
    
    Args:
        subject: Sujet du token (généralement username)
        expires_delta: Durée de validité du token
        additional_data: Données supplémentaires à inclure dans le token
    
    Returns:
        Token JWT encodé
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Créer les données à encoder dans le token
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Ajouter des données supplémentaires si fournies
    if additional_data:
        to_encode.update(additional_data)
    
    # Encoder le token avec la clé secrète et l'algorithme spécifié
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)
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
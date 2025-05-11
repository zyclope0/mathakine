"""
Utilitaires de sécurité pour l'authentification
"""
from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from passlib.context import CryptContext
from app.core.constants import SecurityConfig
from app.core.config import settings
from app.core.logging_config import get_logger

# Obtenir un logger nommé pour ce module
logger = get_logger(__name__)

# Contexte pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clé secrète pour la signature des tokens (à mettre en variable d'environnement en production)
SECRET_KEY = settings.SECRET_KEY

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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    
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
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Crée un hash sécurisé d'un mot de passe.
    
    Args:
        password: Mot de passe en clair
    
    Returns:
        Version hachée du mot de passe
    """
    return pwd_context.hash(password) 
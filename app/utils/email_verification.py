"""
Utilitaires pour la vérification d'email
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)


def generate_verification_token() -> str:
    """
    Génère un token de vérification sécurisé.
    
    Returns:
        Token de vérification (32 caractères aléatoires)
    """
    return secrets.token_urlsafe(32)


def is_verification_token_expired(sent_at: Optional[datetime]) -> bool:
    """
    Vérifie si un token de vérification a expiré.
    
    Args:
        sent_at: Date d'envoi du token
    
    Returns:
        True si le token a expiré (plus de 24 heures), False sinon
    """
    if not sent_at:
        return True
    
    expiration_time = sent_at + timedelta(hours=24)
    return datetime.now(timezone.utc) > expiration_time


def create_verification_link(token: str, frontend_url: Optional[str] = None) -> str:
    """
    Crée un lien de vérification d'email.
    
    Args:
        token: Token de vérification
        frontend_url: URL du frontend (optionnel)
    
    Returns:
        Lien de vérification complet
    """
    import os
    if not frontend_url:
        frontend_url = os.getenv("FRONTEND_URL", "https://mathakine-frontend.onrender.com")
    
    return f"{frontend_url}/verify-email?token={token}"


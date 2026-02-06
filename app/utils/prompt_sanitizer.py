"""
Module de sanitization des prompts utilisateurs.
Protection contre l'injection de prompts malveillants.
"""
import re
from typing import Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)


def sanitize_user_prompt(prompt: str, max_length: int = 500) -> str:
    """
    Sanitize user prompt to prevent injection attacks.
    
    Args:
        prompt: Prompt utilisateur brut
        max_length: Longueur maximale autorisée
        
    Returns:
        Prompt sanitized
    """
    if not prompt:
        return ""
    
    # Limiter la longueur
    original_length = len(prompt)
    prompt = prompt[:max_length]
    
    if original_length > max_length:
        logger.warning(f"Prompt tronqué de {original_length} à {max_length} caractères")
    
    # Patterns dangereux à supprimer (tentatives d'injection)
    dangerous_patterns = [
        # Tentatives de contournement d'instructions
        r'ignore\s+(previous|above|all|all\s+previous)\s+instructions?',
        r'forget\s+(everything|all|previous)',
        r'disregard\s+(previous|above|all)',
        r'you\s+are\s+now',
        r'new\s+instructions?',
        r'override\s+(previous|system)',
        
        # Tentatives de changement de rôle
        r'act\s+as\s+if\s+you\s+are',
        r'pretend\s+to\s+be',
        r'you\s+must\s+now',
        
        # Tentatives de manipulation
        r'do\s+not\s+follow',
        r'ignore\s+the\s+system',
        r'bypass\s+(safety|security|rules)',
        
        # Tentatives de fuite d'informations
        r'show\s+me\s+your\s+(prompt|instructions|system)',
        r'repeat\s+your\s+(prompt|instructions)',
        r'what\s+are\s+your\s+(instructions|rules)',
    ]
    
    # Supprimer les patterns dangereux
    sanitized_prompt = prompt
    removed_patterns = []
    
    for pattern in dangerous_patterns:
        matches = re.findall(pattern, sanitized_prompt, flags=re.IGNORECASE)
        if matches:
            removed_patterns.extend(matches)
            sanitized_prompt = re.sub(pattern, '', sanitized_prompt, flags=re.IGNORECASE)
    
    if removed_patterns:
        logger.warning(f"Patterns dangereux détectés et supprimés: {removed_patterns}")
    
    # Nettoyer les espaces multiples
    sanitized_prompt = re.sub(r'\s+', ' ', sanitized_prompt)
    sanitized_prompt = sanitized_prompt.strip()
    
    return sanitized_prompt


def validate_prompt_safety(prompt: str) -> tuple[bool, Optional[str]]:
    """
    Valide la sécurité d'un prompt.
    
    Returns:
        Tuple (is_safe, reason) où reason est None si safe, sinon message d'erreur
    """
    if not prompt:
        return True, None
    
    # Vérifier la longueur
    if len(prompt) > 1000:
        return False, "Prompt trop long (max 1000 caractères)"
    
    # Vérifier les patterns dangereux (avant sanitization)
    dangerous_patterns = [
        r'ignore\s+(previous|above|all)',
        r'forget\s+everything',
        r'you\s+are\s+now',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, prompt, flags=re.IGNORECASE):
            return False, f"Pattern dangereux détecté: {pattern}"
    
    return True, None


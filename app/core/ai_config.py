"""
Configuration centralisée pour la génération IA.
Best practice : Paramètres adaptatifs selon le type de challenge.
"""
from typing import Dict, Optional

from loguru import logger

from app.core.config import settings


class AIConfig:
    """Configuration centralisée pour la génération IA."""
    
    # Modèles par type de challenge (peut être étendu)
    MODEL_MAP: Dict[str, str] = {
        'pattern': settings.OPENAI_MODEL,      # Modèle par défaut pour patterns simples
        'sequence': settings.OPENAI_MODEL,
        'puzzle': settings.OPENAI_MODEL,       # Peut être upgradé vers gpt-4o si nécessaire
        'graph': settings.OPENAI_MODEL,
        'spatial': settings.OPENAI_MODEL,
        'visual': settings.OPENAI_MODEL,
        'riddle': settings.OPENAI_MODEL,
        'deduction': settings.OPENAI_MODEL,
    }
    
    # Températures adaptatives selon le type
    TEMPERATURE_MAP: Dict[str, float] = {
        'pattern': 0.3,      # Basse pour patterns logiques stricts
        'sequence': 0.4,     # Moyenne-basse pour séquences
        'puzzle': 0.6,       # Moyenne pour puzzles créatifs
        'graph': 0.5,        # Moyenne pour graphes
        'spatial': 0.7,      # Plus créatif pour spatial
        'visual': 0.7,       # Créatif pour visuel
        'riddle': 0.8,       # Créatif pour énigmes
        'deduction': 0.4,    # Basse pour déduction logique
    }
    
    # Max tokens adaptatif selon le type
    MAX_TOKENS_MAP: Dict[str, int] = {
        'pattern': 2000,     # Patterns avec visual_data
        'sequence': 2000,    # Séquences avec visual_data
        'puzzle': 2500,      # Puzzles plus complexes
        'graph': 2500,       # Graphes avec visual_data détaillé
        'spatial': 3000,     # Spatial avec descriptions détaillées
        'visual': 3000,      # Visual avec descriptions
        'riddle': 2500,      # Énigmes avec contexte
        'deduction': 3000,   # Déduction avec explications détaillées
    }
    
    # Timeouts
    DEFAULT_TIMEOUT: float = 60.0  # 60 secondes par défaut
    MAX_TIMEOUT: float = 120.0     # Maximum 2 minutes
    
    # Retry configuration
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_MULTIPLIER: float = 1.0
    RETRY_MIN_WAIT: float = 2.0
    RETRY_MAX_WAIT: float = 10.0
    
    @classmethod
    def get_model(cls, challenge_type: str) -> str:
        """Retourne le modèle à utiliser pour un type de challenge."""
        return cls.MODEL_MAP.get(challenge_type.lower(), settings.OPENAI_MODEL)
    
    @classmethod
    def get_temperature(cls, challenge_type: str) -> float:
        """Retourne la température à utiliser pour un type de challenge."""
        return cls.TEMPERATURE_MAP.get(challenge_type.lower(), 0.6)
    
    @classmethod
    def get_max_tokens(cls, challenge_type: str) -> int:
        """Retourne le max_tokens à utiliser pour un type de challenge."""
        return cls.MAX_TOKENS_MAP.get(challenge_type.lower(), 2000)
    
    @classmethod
    def get_timeout(cls, challenge_type: Optional[str] = None) -> float:
        """Retourne le timeout à utiliser."""
        # Timeout plus long pour types complexes
        if challenge_type in ['spatial', 'visual', 'deduction']:
            return cls.MAX_TIMEOUT
        return cls.DEFAULT_TIMEOUT
    
    @classmethod
    def get_openai_params(cls, challenge_type: str) -> Dict:
        """Retourne les paramètres OpenAI complets pour un type de challenge."""
        return {
            "model": cls.get_model(challenge_type),
            "temperature": cls.get_temperature(challenge_type),
            "max_tokens": cls.get_max_tokens(challenge_type),
            "timeout": cls.get_timeout(challenge_type),
        }


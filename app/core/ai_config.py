"""
Configuration centralisée pour la génération IA.
Best practice : Paramètres adaptatifs selon le type de challenge.

GPT-5.2 utilise de nouveaux paramètres :
- reasoning.effort : none, low, medium, high, xhigh (contrôle la profondeur de raisonnement)
- text.verbosity : low, medium, high (contrôle la longueur de réponse)
- temperature n'est supporté QUE si reasoning.effort = none
"""
from typing import Dict, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)

from app.core.config import settings


class AIConfig:
    """Configuration centralisée pour la génération IA."""
    
    # Modèle plus capable pour défis nécessitant du raisonnement logique/spatial
    # GPT-5.1 : bon raisonnement logique, 400K contexte, $1.25/M input
    # GPT-5-mini : bon rapport qualité/prix pour tâches simples, $0.25/M input
    ADVANCED_MODEL: str = "gpt-5.1"      # Modèle avancé pour défis complexes
    BASIC_MODEL: str = "gpt-5-mini"      # Modèle économique pour tâches simples
    
    # Modèles par type de challenge
    # Note: SPATIAL a été fusionné dans VISUAL
    MODEL_MAP: Dict[str, str] = {
        'pattern': ADVANCED_MODEL,             # Patterns nécessitent raisonnement logique
        'sequence': BASIC_MODEL,               # Séquences simples OK avec mini
        'puzzle': BASIC_MODEL,                 # Puzzles OK avec mini + bonne validation
        'graph': ADVANCED_MODEL,               # Graphes nécessitent cohérence stricte
        'visual': ADVANCED_MODEL,              # Visual (inclut spatial) NÉCESSITE raisonnement avancé
        'riddle': BASIC_MODEL,                 # Énigmes textuelles OK avec mini
        'deduction': ADVANCED_MODEL,           # Déduction nécessite logique stricte
        'coding': ADVANCED_MODEL,              # Cryptographie nécessite raisonnement pour cohérence
    }
    
    # GPT-5.2 Reasoning Effort : contrôle la profondeur de raisonnement
    # none = rapide, low/medium = équilibré, high/xhigh = raisonnement profond
    REASONING_EFFORT_MAP: Dict[str, str] = {
        'pattern': 'high',       # Raisonnement profond pour patterns logiques
        'sequence': 'low',       # Léger pour séquences simples
        'puzzle': 'medium',      # Moyen pour puzzles
        'graph': 'high',         # Profond pour cohérence des graphes
        'visual': 'high',        # PROFOND - formes/couleurs/symétrie
        'riddle': 'medium',      # Moyen pour énigmes
        'deduction': 'high',     # Profond pour déduction logique
        'coding': 'high',        # PROFOND - cryptographie nécessite cohérence stricte
    }
    
    # GPT-5.2 Verbosity : contrôle la longueur de réponse
    # low = concis (bon pour JSON), medium = équilibré, high = détaillé
    VERBOSITY_MAP: Dict[str, str] = {
        'pattern': 'low',        # JSON concis
        'sequence': 'low',       # JSON concis
        'puzzle': 'low',         # JSON concis
        'graph': 'low',          # JSON concis
        'visual': 'low',         # JSON concis
        'riddle': 'medium',      # Un peu plus de contexte
        'deduction': 'medium',   # Explications détaillées
        'coding': 'low',         # JSON concis pour cryptographie
    }
    
    # Températures - UNIQUEMENT utilisées si reasoning.effort = none
    # Pour GPT-5.2 avec reasoning activé, ces valeurs sont ignorées
    TEMPERATURE_MAP: Dict[str, float] = {
        'pattern': 0.2,
        'sequence': 0.3,
        'puzzle': 0.5,
        'graph': 0.3,
        'visual': 0.3,
        'riddle': 0.7,
        'deduction': 0.3,
        'coding': 0.3,           # Température basse pour cohérence cryptographique
    }
    
    # Max tokens adaptatif selon le type
    # GPT-5 avec reasoning peut consommer beaucoup de tokens - augmenter les limites
    # Note: avec reasoning=high, le modèle utilise plus de tokens pour "réfléchir"
    MAX_TOKENS_MAP: Dict[str, int] = {
        'pattern': 6000,     # Patterns avec visual_data
        'sequence': 4000,    # Séquences avec visual_data
        'puzzle': 5000,      # Puzzles avec hints détaillés
        'graph': 6000,       # Graphes avec visual_data détaillé
        'visual': 8000,      # Visual (inclut spatial) avec descriptions détaillées
        'riddle': 5000,      # Énigmes avec contexte
        'deduction': 8000,   # Déduction avec règles et explications détaillées
        'coding': 6000,      # Cryptographie avec message encodé et clé
    }
    
    # Timeouts - plus longs pour GPT-5 avec reasoning
    DEFAULT_TIMEOUT: float = 90.0   # 90 secondes par défaut
    MAX_TIMEOUT: float = 180.0      # Maximum 3 minutes
    
    # Retry configuration
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_MULTIPLIER: float = 1.0
    RETRY_MIN_WAIT: float = 2.0
    RETRY_MAX_WAIT: float = 10.0
    
    @classmethod
    def is_o1_model(cls, model: str) -> bool:
        """Vérifie si le modèle est o1/o1-mini (raisonnement natif, pas de response_format JSON)."""
        return model and model.lower().startswith("o1")

    @classmethod
    def get_model(cls, challenge_type: str) -> str:
        """Retourne le modèle à utiliser pour un type de challenge."""
        if settings.OPENAI_MODEL_REASONING:
            return settings.OPENAI_MODEL_REASONING
        return cls.MODEL_MAP.get(challenge_type.lower(), settings.OPENAI_MODEL)
    
    @classmethod
    def get_reasoning_effort(cls, challenge_type: str) -> str:
        """Retourne le niveau de raisonnement pour GPT-5.2."""
        return cls.REASONING_EFFORT_MAP.get(challenge_type.lower(), 'medium')
    
    @classmethod
    def get_verbosity(cls, challenge_type: str) -> str:
        """Retourne le niveau de verbosité pour GPT-5.2."""
        return cls.VERBOSITY_MAP.get(challenge_type.lower(), 'low')
    
    @classmethod
    def get_temperature(cls, challenge_type: str) -> float:
        """Retourne la température (utilisée seulement si reasoning.effort = none)."""
        return cls.TEMPERATURE_MAP.get(challenge_type.lower(), 0.6)
    
    @classmethod
    def get_max_tokens(cls, challenge_type: str) -> int:
        """Retourne le max_tokens à utiliser pour un type de challenge."""
        return cls.MAX_TOKENS_MAP.get(challenge_type.lower(), 2000)
    
    @classmethod
    def get_timeout(cls, challenge_type: Optional[str] = None) -> float:
        """Retourne le timeout à utiliser."""
        # Timeout plus long pour types complexes avec raisonnement profond
        if challenge_type in ['visual', 'deduction', 'pattern', 'graph', 'coding']:
            return cls.MAX_TIMEOUT
        return cls.DEFAULT_TIMEOUT
    
    @classmethod
    def is_gpt5_model(cls, model: str) -> bool:
        """Vérifie si le modèle est un GPT-5.x."""
        return model.startswith('gpt-5')
    
    @classmethod
    def get_openai_params(cls, challenge_type: str) -> Dict:
        """Retourne les paramètres OpenAI complets pour un type de challenge."""
        model = cls.get_model(challenge_type)
        reasoning_effort = cls.get_reasoning_effort(challenge_type)

        params = {
            "model": model,
            "max_tokens": cls.get_max_tokens(challenge_type),
            "timeout": cls.get_timeout(challenge_type),
        }

        # o1/o1-mini : raisonnement natif, pas de reasoning_effort/verbosity
        if cls.is_o1_model(model):
            # o1 n'accepte pas response_format json_object -> géré dans le handler
            pass
        elif cls.is_gpt5_model(model):
            params["reasoning_effort"] = reasoning_effort
            params["verbosity"] = cls.get_verbosity(challenge_type)
            if reasoning_effort == "none":
                params["temperature"] = cls.get_temperature(challenge_type)
        else:
            params["temperature"] = cls.get_temperature(challenge_type)

        return params


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


class AIConfig:
    """Configuration centralisée pour la génération IA."""

    # Résolution modèle **défis** (stream) : ``challenge_ai_model_policy.resolve_challenge_ai_model``.
    # Fallback stream vide (o-series) : ``resolve_challenge_ai_fallback_model``.

    # Reasoning Effort : contrôle la profondeur (o-series, GPT-5.x)
    # low = rapide/économique, medium = équilibré, high = raisonnement profond
    # Pas de high partout : sequence/puzzle/riddle/graph/coding suffisent avec low/medium.
    # Chess est volontairement borné : la qualité vient d'une position tactique simple,
    # pas d'une recherche ouverte coûteuse que le LLM ne peut pas prouver comme un moteur.
    REASONING_EFFORT_MAP: Dict[str, str] = {
        "pattern": "high",  # Patterns logiques complexes
        "sequence": "low",  # Séquences simples
        "puzzle": "low",  # Puzzles OK en low
        "graph": "medium",  # Graphes : medium suffit
        "visual": "high",  # Visual (formes/couleurs/symétrie) demande profond
        "riddle": "low",  # Énigmes textuelles simples
        "deduction": "high",  # Déduction logique stricte
        "coding": "medium",  # Cryptographie : medium pour cohérence
        "chess": "low",  # Échecs : positions courtes, budget borné
        "probability": "low",  # Probabilités : low suffit
    }

    # Les modèles o-series consomment le budget de sortie avec leur raisonnement caché.
    # Cette matrice privilégie un JSON complet au premier passage. Les validations et
    # réparations ciblées portent la qualité, plutôt qu'un raisonnement "high" coûteux
    # qui peut produire une réponse visible vide ou tronquée.
    O_SERIES_REASONING_EFFORT_BY_TYPE: Dict[str, str] = {
        "pattern": "medium",
        "sequence": "low",
        "puzzle": "low",
        "graph": "medium",
        "visual": "medium",
        "riddle": "low",
        "deduction": "medium",
        "coding": "medium",
        "chess": "low",
        "probability": "low",
    }

    # GPT-5.2 Verbosity : contrôle la longueur de réponse
    # low = concis (bon pour JSON), medium = équilibré, high = détaillé
    VERBOSITY_MAP: Dict[str, str] = {
        "pattern": "low",  # JSON concis
        "sequence": "low",  # JSON concis
        "puzzle": "low",  # JSON concis
        "graph": "low",  # JSON concis
        "visual": "low",  # JSON concis
        "riddle": "medium",  # Un peu plus de contexte
        "deduction": "medium",  # Explications détaillées
        "coding": "low",  # JSON concis pour cryptographie
        "chess": "low",  # JSON concis (board 8x8)
        "probability": "low",  # JSON concis
    }

    # Températures - UNIQUEMENT utilisées si reasoning.effort = none
    # Pour GPT-5.2 avec reasoning activé, ces valeurs sont ignorées
    TEMPERATURE_MAP: Dict[str, float] = {
        "pattern": 0.2,
        "sequence": 0.3,
        "puzzle": 0.5,
        "graph": 0.3,
        "visual": 0.3,
        "riddle": 0.7,
        "deduction": 0.3,
        "coding": 0.3,  # Température basse pour cohérence cryptographique
        "chess": 0.3,  # Positions tactiques cohérentes
        "probability": 0.4,  # Légère variété
    }

    # Max tokens adaptatif selon le type
    # GPT-5 avec reasoning peut consommer beaucoup de tokens - augmenter les limites
    # Note: avec reasoning=high, le modèle utilise plus de tokens pour "réfléchir"
    MAX_TOKENS_MAP: Dict[str, int] = {
        "pattern": 6000,  # Patterns avec visual_data
        "sequence": 4000,  # Séquences avec visual_data
        "puzzle": 6500,  # Puzzles ordonnés : marge anti-troncature JSON
        "graph": 6000,  # Graphes avec visual_data détaillé
        "visual": 8000,  # Visual (inclut spatial) avec descriptions détaillées
        "riddle": 5000,  # Énigmes avec contexte
        "deduction": 8000,  # Déduction avec règles et explications détaillées
        "coding": 6000,  # Cryptographie avec message encodé et clé
        "chess": 6000,  # board 8x8 + ligne tactique courte ; évite les runs >5 min
        "probability": 4000,  # Probabilités simples
    }

    # Timeouts - plus longs pour GPT-5 avec reasoning
    DEFAULT_TIMEOUT: float = 90.0  # 90 secondes par défaut
    MAX_TIMEOUT: float = 180.0  # Maximum 3 minutes
    TIMEOUT_MAP: Dict[str, float] = {
        "chess": 90.0,
    }

    # Retry configuration
    MAX_RETRIES: int = 3
    MAX_RETRIES_BY_TYPE: Dict[str, int] = {
        "chess": 1,
    }
    RETRY_BACKOFF_MULTIPLIER: float = 1.0
    RETRY_MIN_WAIT: float = 2.0
    RETRY_MAX_WAIT: float = 10.0

    @classmethod
    def is_o1_model(cls, model: str) -> bool:
        """Vérifie si le modèle est o1/o1-mini (pas de response_format JSON, pas de reasoning_effort)."""
        return model and model.lower().startswith("o1")

    @classmethod
    def is_o_series_reasoning_model(cls, model: str) -> bool:
        """Vérifie si le modèle est une famille o-series avec ``reasoning_effort``."""
        if not model:
            return False
        normalized = model.lower()
        return normalized.startswith("o3") or normalized.startswith("o4")

    @classmethod
    def is_o3_model(cls, model: str) -> bool:
        """Alias historique : la branche couvre désormais les modèles o3 et o4."""
        return cls.is_o_series_reasoning_model(model)

    @classmethod
    def get_model(cls, challenge_type: str) -> str:
        """
        Modèle OpenAI pour la génération d'un défi.

        Délègue à :func:`app.services.challenges.challenge_ai_model_policy.resolve_challenge_ai_model`
        (hiérarchie explicite : override défis > legacy ``OPENAI_MODEL_REASONING`` > carte par type > ``o4-mini``).
        """
        from app.services.challenges.challenge_ai_model_policy import (
            resolve_challenge_ai_model,
        )

        return resolve_challenge_ai_model(challenge_type)

    @classmethod
    def get_reasoning_effort(cls, challenge_type: str) -> str:
        """Retourne le niveau de raisonnement pour GPT-5.2."""
        return cls.REASONING_EFFORT_MAP.get(challenge_type.lower(), "medium")

    @classmethod
    def get_o_series_reasoning_effort(cls, challenge_type: str) -> str:
        """Retourne le niveau de raisonnement borné pour les modèles o-series."""
        type_key = (challenge_type or "").strip().lower()
        return cls.O_SERIES_REASONING_EFFORT_BY_TYPE.get(
            type_key,
            cls.get_reasoning_effort(type_key),
        )

    @classmethod
    def get_verbosity(cls, challenge_type: str) -> str:
        """Retourne le niveau de verbosité pour GPT-5.2."""
        return cls.VERBOSITY_MAP.get(challenge_type.lower(), "low")

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
        type_key = (challenge_type or "").strip().lower()
        if type_key in cls.TIMEOUT_MAP:
            return cls.TIMEOUT_MAP[type_key]

        # Timeout plus long pour types complexes avec raisonnement profond
        if type_key in [
            "visual",
            "deduction",
            "pattern",
            "graph",
            "coding",
        ]:
            return cls.MAX_TIMEOUT
        return cls.DEFAULT_TIMEOUT

    @classmethod
    def get_max_retries(cls, challenge_type: Optional[str] = None) -> int:
        """Retourne le nombre d'essais OpenAI autorisé pour ce type."""
        type_key = (challenge_type or "").strip().lower()
        return cls.MAX_RETRIES_BY_TYPE.get(type_key, cls.MAX_RETRIES)

    @classmethod
    def is_gpt5_model(cls, model: str) -> bool:
        """Vérifie si le modèle est un GPT-5.x (gpt-5-mini, gpt-5.4, gpt5-nano, etc.)."""
        if not model:
            return False
        m = model.lower()
        return m.startswith("gpt-5") or m.startswith("gpt5")

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

        # o1/o1-mini : raisonnement natif, pas de reasoning_effort/verbosity, pas de response_format
        if cls.is_o1_model(model):
            # o1 n'accepte pas response_format json_object -> géré dans le handler
            pass
        # o-series reasoning : reasoning_effort + structured output supportés
        elif cls.is_o_series_reasoning_model(model):
            params["reasoning_effort"] = cls.get_o_series_reasoning_effort(
                challenge_type
            )
            # verbosity non supporté par o3 Chat Completions
        elif cls.is_gpt5_model(model):
            params["reasoning_effort"] = reasoning_effort
            params["verbosity"] = cls.get_verbosity(challenge_type)
            if reasoning_effort == "none":
                params["temperature"] = cls.get_temperature(challenge_type)
        else:
            params["temperature"] = cls.get_temperature(challenge_type)

        return params

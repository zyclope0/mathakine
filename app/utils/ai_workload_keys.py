"""
Clés d'observabilité IA partagées entre trackers, admin read-only et chat.

Les trackers runtime historiques utilisaient un nom de paramètre ``challenge_type``
qui sert désormais de **clé métrique** pour plusieurs workloads :

- ``assistant_chat`` / ``assistant_chat:simple`` / ``assistant_chat:complex``
- ``exercise_ai:<type>``
- clés canoniques des défis IA (types API en minuscules, ex. ``pattern``, ``sequence``)

Ce module centralise la classification pour éviter les heuristiques dispersées.

IA12 : rétention mémoire des trackers runtime — constantes partagées (TTL + cap par clé).
"""

from __future__ import annotations

from typing import Any, Dict, Final

from app.core.constants_challenge import CHALLENGE_TYPES_API
from app.core.logging_config import get_logger

logger = get_logger(__name__)

WORKLOAD_ASSISTANT_CHAT: Final[str] = "assistant_chat"
WORKLOAD_EXERCISES_AI: Final[str] = "exercises_ai"
WORKLOAD_CHALLENGES_AI: Final[str] = "challenges_ai"
WORKLOAD_UNKNOWN: Final[str] = "unknown"

EXERCISE_AI_PREFIX: Final[str] = "exercise_ai:"
ASSISTANT_CHAT_PREFIX: Final[str] = "assistant_chat"

# Fenêtre de conservation en mémoire process (indépendante du paramètre admin ``days``).
RUNTIME_AI_METRICS_RETENTION_DAYS: Final[int] = 90
# Plafond d'événements par clé métrique après purge TTL (évite listes infinies).
RUNTIME_AI_METRICS_MAX_EVENTS_PER_KEY: Final[int] = 2000

# Types de défi connus (API) — seules clés non préfixées classées ``challenges_ai``.
CHALLENGE_AI_METRIC_KEYS: Final[frozenset[str]] = frozenset(CHALLENGE_TYPES_API)


def normalize_ai_metric_key(metric_key: str | None) -> str:
    """Normalise une clé métrique runtime IA."""
    return (metric_key or "").strip().lower()


def is_challenge_ai_metric_key(normalized_key: str) -> bool:
    """Vrai si la clé (déjà normalisée) est un type de défi IA reconnu."""
    return normalized_key in CHALLENGE_AI_METRIC_KEYS


def classify_ai_workload_key(metric_key: str | None) -> str:
    """
    Classe une clé runtime vers un workload stable pour l'admin et les agrégats.

    Règle fail-closed (IA12) :
    - ``exercise_ai:*`` -> ``exercises_ai``
    - ``assistant_chat`` / ``assistant_chat:*`` -> ``assistant_chat``
    - clé dans :data:`CHALLENGE_AI_METRIC_KEYS` (types défis API) -> ``challenges_ai``
    - toute autre clé non vide -> ``unknown`` (log warning ; plus d'attribution silencieuse aux défis)
    - vide -> ``unknown``
    """
    normalized = normalize_ai_metric_key(metric_key)
    if not normalized:
        return WORKLOAD_UNKNOWN
    if normalized.startswith(EXERCISE_AI_PREFIX):
        return WORKLOAD_EXERCISES_AI
    if normalized == ASSISTANT_CHAT_PREFIX or normalized.startswith(
        f"{ASSISTANT_CHAT_PREFIX}:"
    ):
        return WORKLOAD_ASSISTANT_CHAT
    if is_challenge_ai_metric_key(normalized):
        return WORKLOAD_CHALLENGES_AI
    logger.warning(
        f"Clé métrique IA non reconnue pour agrégat workload: {metric_key!r} → bucket « unknown » (IA12). "
        "Attendu: exercise_ai:*, assistant_chat*, ou un type défi dans CHALLENGE_TYPES_API."
    )
    return WORKLOAD_UNKNOWN


def runtime_ai_metrics_retention_meta() -> Dict[str, Any]:
    """Métadonnées affichables côté admin (honnêteté sur la fenêtre in-process)."""
    return {
        "max_age_days": RUNTIME_AI_METRICS_RETENTION_DAYS,
        "max_events_per_key": RUNTIME_AI_METRICS_MAX_EVENTS_PER_KEY,
        "disclaimer_fr": (
            "Données runtime en mémoire process : au-delà de la fenêtre indiquée, "
            "les événements sont purgés. Les coûts sont des estimations (grilles indicatives), "
            "pas une vérité comptable."
        ),
    }

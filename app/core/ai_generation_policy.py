"""
Politique applicative typée : génération IA exercices (flux SSE OpenAI).

Vue multi-workloads : :mod:`app.core.app_model_policy` documente l'index et délègue ici pour ``exercises_ai``.

Source de vérité métier par défaut : constantes de ce module (ex. modèle par défaut ``o4-mini``).
Les variables d'environnement ne font qu'**override** opérationnel, sans remplacer la policy.

Hiérarchie de résolution du modèle (aujourd'hui) :
1. ``OPENAI_MODEL_EXERCISES_OVERRIDE`` (ops / déploiement)
2. sinon ``OPENAI_MODEL_EXERCISES`` (legacy, déprécié — même sémantique d'override)
3. sinon défaut applicatif : :data:`DEFAULT_EXERCISES_AI_MODEL`

Futur (non implémenté ici) : ``resolve_exercise_ai_model_for_user`` pourra composer
abonnement / quotas avant de retourner un modèle autorisé.

**Allowlist** : seuls les identifiants dans :data:`EXERCISES_AI_ALLOWED_MODEL_IDS` sont
acceptés (override env ou défaut). Aucun routage silencieux vers une famille « chat »
pour une chaîne arbitraire.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Final, List, Optional

from app.core.config import settings


class ExerciseAIModelNotAllowedError(ValueError):
    """Modèle demandé absent de l'allowlist exercices IA (typo ou ID non pris en charge)."""


# ---------------------------------------------------------------------------
# Allowlist explicite (identifiants OpenAI normalisés en minuscules)
# ---------------------------------------------------------------------------

EXERCISES_AI_ALLOWED_MODEL_IDS: Final[frozenset[str]] = frozenset(
    {
        "o1",
        "o1-mini",
        "o3",
        "o3-mini",
        "o4-mini",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        "gpt-5",
        "gpt-5-mini",
        "gpt-5-nano",
        "gpt-5.1",
        "gpt-5.2",
        "gpt-5.3",
        "gpt-5.4",
        "gpt5-nano",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    }
)

# ---------------------------------------------------------------------------
# Défaut et paramètres par type d'exercice (clés API = minuscules)
# ---------------------------------------------------------------------------

DEFAULT_EXERCISES_AI_MODEL: Final[str] = "o4-mini"

_REASONING_EFFORT_DEFAULT: Final[str] = "medium"
_O_SERIES_REASONING_EFFORT_MAX: Final[str] = "medium"
_MAX_COMPLETION_TOKENS_DEFAULT: Final[int] = 4000

# Compense le fait que les familles o-series (o3 / o4-mini) consomment une part
# significative de ``max_completion_tokens`` en reasoning tokens cachés avant
# d'émettre la moindre sortie visible. Mesuré empiriquement post-migration
# o4-mini : ratio output/reasoning tombé ~70/30 → ~40/60. Sans bump, un JSON qui
# tenait en 2800 tokens sur o3 est tronqué sur o4-mini. Fail-open : s'applique
# uniquement aux familles identifiées ``O_SERIES`` (pas O1, GPT5, CHAT_CLASSIC).
_O_SERIES_COMPLETION_TOKENS_MULTIPLIER: Final[float] = 1.4

REASONING_EFFORT_BY_EXERCISE_TYPE: Final[Dict[str, str]] = {
    "addition": "low",
    "soustraction": "low",
    "multiplication": "low",
    "division": "low",
    "geometrie": "medium",
    "fractions": "medium",
    "texte": "medium",
    "mixte": "high",
    "divers": "medium",
}

MAX_COMPLETION_TOKENS_BY_EXERCISE_TYPE: Final[Dict[str, int]] = {
    "addition": 2800,
    "soustraction": 2800,
    "multiplication": 2800,
    "division": 2800,
    "geometrie": 3200,
    "fractions": 4500,
    "texte": 4500,
    # o-series compte les tokens de raisonnement dans max_completion_tokens ;
    # MIXTE GRAND_MAITRE a besoin d'une marge visible suffisante pour fermer le JSON.
    "mixte": 6500,
    "divers": 4500,
}

# Verbosity GPT-5.x pour JSON exercice, calibrée par type.
# ``low`` force la concision : OK pour opérations simples (JSON court) ; pour les
# types pédagogiquement plus riches (fractions, texte, mixte, geometrie),
# ``low`` rabote l'explication et le hint, d'où ``medium``. ``high`` jamais :
# produit des JSON trop longs qui se font tronquer avant clôture.
_EXERCISE_IA_GPT5_VERBOSITY_DEFAULT: Final[str] = "low"
VERBOSITY_BY_EXERCISE_TYPE_GPT5: Final[Dict[str, str]] = {
    "addition": "low",
    "soustraction": "low",
    "multiplication": "low",
    "division": "low",
    "divers": "low",
    "fractions": "medium",
    "geometrie": "medium",
    "texte": "medium",
    "mixte": "medium",
}


class ExerciseAIModelFamily(str, Enum):
    """Famille de modèle pour le routage des paramètres Chat Completions (exercices IA)."""

    O1 = "o1"
    O_SERIES = "o_series"
    # Alias historique conservé pour les tests/outils qui parlent encore de famille "o3".
    O3 = "o_series"
    GPT5 = "gpt5"
    CHAT_CLASSIC = "chat_classic"


@dataclass(frozen=True)
class ModelFamilyCapabilities:
    """
    Matrice de capacités (une ligne par famille).

    Toutes les branches utilisent ``max_completion_tokens`` côté client exercices IA.
    """

    supports_response_format_json_object: bool
    supports_reasoning_effort: bool
    supports_verbosity: bool
    supports_temperature: bool


MODEL_FAMILY_CAPABILITIES: Final[
    Dict[ExerciseAIModelFamily, ModelFamilyCapabilities]
] = {
    ExerciseAIModelFamily.O1: ModelFamilyCapabilities(
        supports_response_format_json_object=False,
        supports_reasoning_effort=False,
        supports_verbosity=False,
        supports_temperature=False,
    ),
    ExerciseAIModelFamily.O_SERIES: ModelFamilyCapabilities(
        supports_response_format_json_object=True,
        supports_reasoning_effort=True,
        supports_verbosity=False,
        supports_temperature=False,
    ),
    ExerciseAIModelFamily.GPT5: ModelFamilyCapabilities(
        supports_response_format_json_object=True,
        supports_reasoning_effort=True,
        supports_verbosity=True,
        supports_temperature=True,
    ),
    ExerciseAIModelFamily.CHAT_CLASSIC: ModelFamilyCapabilities(
        supports_response_format_json_object=True,
        supports_reasoning_effort=False,
        supports_verbosity=False,
        supports_temperature=True,
    ),
}


def normalize_exercise_ai_model_id(model_id: str) -> str:
    """Normalise l'identifiant modèle (strip + minuscules) pour allowlist et appels API."""
    return (model_id or "").strip().lower()


def assert_exercise_ai_model_allowed(normalized_id: str) -> None:
    """
    Vérifie que l'identifiant figure dans l'allowlist.
    Lève :class:`ExerciseAIModelNotAllowedError` sinon (échec précoce, avant OpenAI).
    """
    if not normalized_id:
        raise ValueError("Identifiant de modèle vide.")
    if normalized_id not in EXERCISES_AI_ALLOWED_MODEL_IDS:
        raise ExerciseAIModelNotAllowedError(
            f"Modèle non autorisé pour le flux exercices IA: {normalized_id!r}. "
            "Vérifiez la typo ou étendez EXERCISES_AI_ALLOWED_MODEL_IDS dans "
            "app.core.ai_generation_policy."
        )


def _infer_family_for_allowed_model(normalized_id: str) -> ExerciseAIModelFamily:
    """
    Famille OpenAI pour un ID **déjà** allowlisté.
    Ne doit pas servir de filet pour un ID arbitraire.
    """
    if normalized_id.startswith("o1"):
        return ExerciseAIModelFamily.O1
    if normalized_id.startswith("o3") or normalized_id.startswith("o4"):
        return ExerciseAIModelFamily.O_SERIES
    if normalized_id.startswith("gpt-5") or normalized_id.startswith("gpt5"):
        return ExerciseAIModelFamily.GPT5
    if normalized_id.startswith("gpt-4") or normalized_id.startswith("gpt-3.5"):
        return ExerciseAIModelFamily.CHAT_CLASSIC
    raise ValueError(
        f"Modèle allowlisté mais famille indéterminée: {normalized_id!r}. "
        "Complétez _infer_family_for_allowed_model."
    )


def classify_exercise_ai_model_family(model_id: str) -> ExerciseAIModelFamily:
    """Allowlist + inférence de famille (aucun fallback silencieux vers chat classique)."""
    normalized = normalize_exercise_ai_model_id(model_id)
    assert_exercise_ai_model_allowed(normalized)
    return _infer_family_for_allowed_model(normalized)


def get_model_family_capabilities(
    family: ExerciseAIModelFamily,
) -> ModelFamilyCapabilities:
    """Retourne la ligne de la matrice de capacités pour une famille."""
    return MODEL_FAMILY_CAPABILITIES[family]


def resolve_exercise_ai_model() -> str:
    """
    Modèle effectif pour le flux SSE exercices IA (identifiant normalisé minuscules).

    Override env d'abord, puis défaut applicatif ``o4-mini``.
    ``o1`` / ``o1-mini`` uniquement si présents dans l'allowlist et choisis via override.
    Lève :class:`ExerciseAIModelNotAllowedError` si l'override n'est pas allowlisté.
    """
    override_raw = settings.OPENAI_MODEL_EXERCISES_OVERRIDE.strip()
    if not override_raw:
        override_raw = settings.OPENAI_MODEL_EXERCISES.strip()
    chosen = (
        normalize_exercise_ai_model_id(override_raw)
        if override_raw
        else DEFAULT_EXERCISES_AI_MODEL
    )
    classify_exercise_ai_model_family(chosen)
    return chosen


def resolve_exercise_ai_model_for_user(
    user_id: Optional[int],
    exercise_type: str,
) -> str:
    """
    Point d'extension futur (abonnement / paliers).

    Aujourd'hui : ignore ``user_id`` et ``exercise_type`` pour la résolution modèle ;
    délègue à :func:`resolve_exercise_ai_model`.
    """
    _ = user_id
    _ = exercise_type
    return resolve_exercise_ai_model()


def reasoning_effort_for_exercise_type(exercise_type: str) -> str:
    """Niveau ``reasoning_effort`` pour familles qui le supportent (o-series, gpt-5.x)."""
    key = (exercise_type or "").strip().lower()
    return REASONING_EFFORT_BY_EXERCISE_TYPE.get(key, _REASONING_EFFORT_DEFAULT)


def o_series_reasoning_effort_for_exercise_type(exercise_type: str) -> str:
    """
    Effort effectif pour o-series.

    ``high`` peut consommer tout le budget de sortie en raisonnement caché sur des JSON courts.
    On borne donc o-series à ``medium`` et on laisse les familles GPT-5 conserver la valeur brute.
    """
    effort = reasoning_effort_for_exercise_type(exercise_type)
    if effort == "high":
        return _O_SERIES_REASONING_EFFORT_MAX
    return effort


def verbosity_for_exercise_type_gpt5(exercise_type: str) -> str:
    """Verbosity GPT-5 à utiliser pour ce type d'exercice.

    Retourne ``low`` pour les types concis (opérations directes), ``medium``
    pour les types où l'explication/hint doivent rester lisibles (fractions,
    geometrie, texte, mixte). Fallback : ``low``.
    """
    key = (exercise_type or "").strip().lower()
    return VERBOSITY_BY_EXERCISE_TYPE_GPT5.get(key, _EXERCISE_IA_GPT5_VERBOSITY_DEFAULT)


def max_completion_tokens_for_exercise_type(
    exercise_type: str,
    model: Optional[str] = None,
) -> int:
    """Plafond ``max_completion_tokens`` pour la réponse JSON exercice.

    Si ``model`` est fourni et appartient à la famille o-series (o3/o4), un
    multiplicateur est appliqué pour compenser les reasoning tokens cachés qui
    comptent dans ``max_completion_tokens``. Sinon, base inchangée (fail-open
    pour modèle inconnu).
    """
    key = (exercise_type or "").strip().lower()
    base = MAX_COMPLETION_TOKENS_BY_EXERCISE_TYPE.get(
        key, _MAX_COMPLETION_TOKENS_DEFAULT
    )
    if not model:
        return base
    try:
        family = classify_exercise_ai_model_family(model)
    except (ValueError, ExerciseAIModelNotAllowedError):
        return base
    if family is ExerciseAIModelFamily.O_SERIES:
        return int(base * _O_SERIES_COMPLETION_TOKENS_MULTIPLIER)
    return base


def build_exercise_ai_stream_kwargs(
    *,
    model: str,
    exercise_type: str,
    system_content: str,
    user_content: str,
) -> Dict[str, Any]:
    """
    Construit les kwargs pour ``AsyncOpenAI.chat.completions.create`` (stream).

    Le comportement par famille est aligné sur :data:`MODEL_FAMILY_CAPABILITIES`
    (assertions dans les tests pour éviter dérive).
    """
    family = classify_exercise_ai_model_family(model)
    max_out = max_completion_tokens_for_exercise_type(exercise_type, model=model)
    effort = reasoning_effort_for_exercise_type(exercise_type)

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]

    base: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": True,
        "stream_options": {"include_usage": True},
        "max_completion_tokens": max_out,
    }

    if family is ExerciseAIModelFamily.O1:
        return base

    if family is ExerciseAIModelFamily.O_SERIES:
        base["response_format"] = {"type": "json_object"}
        base["reasoning_effort"] = o_series_reasoning_effort_for_exercise_type(
            exercise_type
        )
        return base

    if family is ExerciseAIModelFamily.GPT5:
        base["response_format"] = {"type": "json_object"}
        base["reasoning_effort"] = effort
        base["verbosity"] = verbosity_for_exercise_type_gpt5(exercise_type)
        if effort == "none":
            base["temperature"] = 0.7
        return base

    base["response_format"] = {"type": "json_object"}
    base["temperature"] = 0.7
    return base

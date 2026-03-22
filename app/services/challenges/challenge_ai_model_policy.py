"""
Politique modèle pour la génération IA des **défis** (flux SSE challenges).

Index gouvernance workloads : :mod:`app.core.app_model_policy` (assistant, delegation exercices/defis).

Source de vérité par défaut : :data:`DEFAULT_CHALLENGES_AI_MODEL` (``o3``).
Les variables d'environnement ne font qu'**override** opérationnel.

Hiérarchie de résolution — **modèle principal** (stream, du plus prioritaire au plus faible) :

1. ``OPENAI_MODEL_CHALLENGES_OVERRIDE`` — override ops explicite pour le pipeline défis.
2. ``OPENAI_MODEL_REASONING`` — **legacy** ; même rôle historique (défis uniquement dans la doc produit).
   Conservé pour ne pas casser les déploiements existants.
3. :data:`CHALLENGE_MODEL_BY_TYPE` — aujourd'hui ``o3`` pour chaque type (carte réellement utilisée
   lorsque aucun override global n'est défini).
4. :data:`DEFAULT_CHALLENGES_AI_MODEL` si le type est inconnu.

**Fallback** (appel HTTP non stream **uniquement** si le stream principal est o3/o3-mini et renvoie un
contenu vide) : :func:`resolve_challenge_ai_fallback_model` —
``OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE`` > :data:`DEFAULT_CHALLENGE_STREAM_FALLBACK_MODEL`.
Ce chemin est **indépendant** du choix du modèle principal : un override global ``gpt-4o`` ne déclenche
pas ce fallback (branche inactive hors famille o3).

La matrice de **capacités** par famille (o1 / o3 / gpt-5.x / chat) reste dans
:class:`app.core.ai_config.AIConfig` via :meth:`AIConfig.get_openai_params`.
"""

from __future__ import annotations

from typing import Dict, Final

from app.core.ai_generation_policy import (
    EXERCISES_AI_ALLOWED_MODEL_IDS,
    ExerciseAIModelNotAllowedError,
    normalize_exercise_ai_model_id,
)
from app.core.config import settings

DEFAULT_CHALLENGES_AI_MODEL: Final[str] = "o3"

# Secours si le stream o3/o3-mini ne renvoie aucun contenu : modèle chat JSON (allowlist).
DEFAULT_CHALLENGE_STREAM_FALLBACK_MODEL: Final[str] = "gpt-4o-mini"

# Carte par type : utilisée uniquement si aucun override global (étapes 1–2 vides).
# Produit actuel : homogène ``o3`` pour tous les types (lisible, gouvernable).
CHALLENGE_MODEL_BY_TYPE: Final[Dict[str, str]] = {
    "pattern": "o3",
    "sequence": "o3",
    "puzzle": "o3",
    "graph": "o3",
    "visual": "o3",
    "riddle": "o3",
    "deduction": "o3",
    "coding": "o3",
    "chess": "o3",
    "probability": "o3",
}

CHALLENGES_AI_ALLOWED_MODEL_IDS: Final[frozenset[str]] = EXERCISES_AI_ALLOWED_MODEL_IDS


def assert_challenge_ai_model_allowed(normalized_id: str) -> None:
    """Lève une erreur typée si l'ID n'est pas autorisé (échec avant appel OpenAI)."""
    if not normalized_id:
        raise ValueError("Identifiant de modèle vide pour le flux défis IA.")
    if normalized_id not in CHALLENGES_AI_ALLOWED_MODEL_IDS:
        raise ExerciseAIModelNotAllowedError(
            f"Modèle non autorisé pour le flux défis IA: {normalized_id!r}. "
            "Vérifiez la typo ou étendez EXERCISES_AI_ALLOWED_MODEL_IDS dans "
            "app.core.ai_generation_policy (allowlist partagée exercices/défis)."
        )


def resolve_challenge_ai_model(challenge_type: str) -> str:
    """
    Identifiant OpenAI effectif pour un défi (normalisé minuscules).

    Override global (ops) > override legacy > carte par type > défaut ``o3``.
    """
    override = (settings.OPENAI_MODEL_CHALLENGES_OVERRIDE or "").strip()
    if not override:
        override = (settings.OPENAI_MODEL_REASONING or "").strip()

    if override:
        chosen = normalize_exercise_ai_model_id(override)
        assert_challenge_ai_model_allowed(chosen)
        return chosen

    key = (challenge_type or "").strip().lower()
    chosen = CHALLENGE_MODEL_BY_TYPE.get(key, DEFAULT_CHALLENGES_AI_MODEL)
    chosen = normalize_exercise_ai_model_id(chosen)
    assert_challenge_ai_model_allowed(chosen)
    return chosen


def resolve_challenge_ai_fallback_model(challenge_type: str) -> str:
    """
    Modèle utilisé pour le **second appel** (non stream) lorsque le premier stream
    (famille o3) est vide.

    Hiérarchie : ``OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE`` >
    :data:`DEFAULT_CHALLENGE_STREAM_FALLBACK_MODEL`.

    ``challenge_type`` est réservé à une future carte par type ; aujourd'hui il n'influence pas le choix.
    """
    _ = challenge_type
    raw = (settings.OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE or "").strip()
    if raw:
        chosen = normalize_exercise_ai_model_id(raw)
        assert_challenge_ai_model_allowed(chosen)
        return chosen
    chosen = normalize_exercise_ai_model_id(DEFAULT_CHALLENGE_STREAM_FALLBACK_MODEL)
    assert_challenge_ai_model_allowed(chosen)
    return chosen

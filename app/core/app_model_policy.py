"""
Gouvernance centralisÃ©e des modÃ¨les OpenAI par **workload** (lot IA10).

Source de vÃ©ritÃ© produit : constantes typÃ©es de ce module + fonctions ``resolve_*``.
Les variables ``.env`` ne font quâ€™**override** ou **compat legacy bornÃ©e**, jamais la vÃ©ritÃ©
principale si une policy explicite existe.

Workloads distinguÃ©s (pas de variable globale silencieuse qui Ã©crase tout) :

- ``assistant_chat`` â€” assistant MaÃ®tre Kine (REST + SSE).
- ``exercises_ai`` â€” gÃ©nÃ©ration SSE exercices (dÃ©lÃ¨gue :mod:`app.core.ai_generation_policy`).
- ``challenges_ai`` â€” gÃ©nÃ©ration SSE dÃ©fis (dÃ©lÃ¨gue ``challenge_ai_model_policy``).

HiÃ©rarchie **assistant_chat** (du plus prioritaire au plus faible) :

1. ``OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE`` â€” override ops dÃ©diÃ© au chat.
2. ``OPENAI_MODEL`` â€” **legacy** ; utilisÃ© seulement si non vide, allowlistÃ©, et **jamais**
   ``gpt-3.5-turbo`` (ignorÃ© avec avertissement log â†’ poursuite vers dÃ©fauts).
3. Palier utilisateur (stub futur) : ``user_tier == "premium"`` â†’ modÃ¨le premium explicite.
4. DÃ©faut produit : :data:`DEFAULT_ASSISTANT_CHAT_MODEL` (``gpt-5-mini``).

ModÃ¨le **premium** (abonnement / futur seam, testable mais non activÃ© par dÃ©faut) :
:data:`PREMIUM_ASSISTANT_CHAT_MODEL` = ``gpt-5.4``.

**Fallback cheap** documentÃ© (retry / routage Ã©conomie futur, pas le dÃ©faut nominal) :
:data:`CHEAP_ASSISTANT_CHAT_FALLBACK_MODEL` = ``gpt-4o-mini``.

**IA10b â€” fail-closed** : :data:`ASSISTANT_CHAT_ALLOWED_MODEL_IDS` est volontairement limitÃ©e aux
modÃ¨les **compatibles avec le runtime chat actuel** (Chat Completions, kwargs dÃ©jÃ  cÃ¢blÃ©s dans
``chat_service``). Les familles **o1** / **o3** ne sont **pas** autorisÃ©es pour lâ€™assistant : elles
restent rÃ©servÃ©es aux workloads **exercises_ai** / **challenges_ai** (dÃ©faut **o3** en policy
dÃ©diÃ©e). Un override ops vers ``o3`` / ``o1`` **Ã©choue tÃ´t** (:func:`assert_assistant_chat_model_allowed`).

Les workloads pÃ©dagogiques structurÃ©s **exercises_ai** / **challenges_ai** restent sur **o3**
par dÃ©faut applicatif ; toute promotion vers GPT-5 hors preuve harness reste hors scope.
"""

from __future__ import annotations

from enum import Enum
from typing import Final, Optional

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AIWorkload(str, Enum):
    """Identifiants stables pour documentation, tests et futurs seams."""

    ASSISTANT_CHAT = "assistant_chat"
    EXERCISES_AI = "exercises_ai"
    CHALLENGES_AI = "challenges_ai"


# ---------------------------------------------------------------------------
# Assistant chat â€” dÃ©fauts produit (mars 2026)
# ---------------------------------------------------------------------------

DEFAULT_ASSISTANT_CHAT_MODEL: Final[str] = "gpt-5-mini"
PREMIUM_ASSISTANT_CHAT_MODEL: Final[str] = "gpt-5.4"
CHEAP_ASSISTANT_CHAT_FALLBACK_MODEL: Final[str] = "gpt-4o-mini"

# Allowlist chat (IA10b fail-closed) : uniquement modÃ¨les alignÃ©s sur le runtime assistant actuel.
# Pas d'o1/o3 ici â€” rÃ©servÃ©s aux flux exercises_ai / challenges_ai.
ASSISTANT_CHAT_ALLOWED_MODEL_IDS: Final[frozenset[str]] = frozenset(
    {
        "gpt-5-mini",
        "gpt-5.4",
        "gpt-4o-mini",
        "gpt-4o",
    }
)

_DEPRECATED_ASSISTANT_LEGACY_MODEL: Final[str] = "gpt-3.5-turbo"


def normalize_openai_model_id(model_id: str) -> str:
    return (model_id or "").strip().lower()


def assert_assistant_chat_model_allowed(normalized_id: str) -> None:
    if not normalized_id:
        raise ValueError("ModÃ¨le assistant_chat vide.")
    if normalized_id not in ASSISTANT_CHAT_ALLOWED_MODEL_IDS:
        raise ValueError(
            f"ModÃ¨le non autorisÃ© pour assistant_chat (allowlist fail-closed IA10b): {normalized_id!r}. "
            "Familles o1/o3 rÃ©servÃ©es aux workloads pÃ©dagogiques ; override ops autorisÃ©: "
            "gpt-5-mini, gpt-5.4, gpt-4o-mini, gpt-4o."
        )


def controlled_cheap_fallback_model_for_assistant_chat() -> str:
    """Fallback cheap explicite (retry / routage Ã©conomie) â€” jamais le dÃ©faut nominal."""
    assert_assistant_chat_model_allowed(CHEAP_ASSISTANT_CHAT_FALLBACK_MODEL)
    return CHEAP_ASSISTANT_CHAT_FALLBACK_MODEL


def resolve_assistant_chat_model(
    *,
    user_tier: Optional[str] = None,
) -> str:
    """
    ModÃ¨le effectif pour les appels Chat Completions de l'assistant (hors DALL-E).

    ``user_tier`` : ``\"standard\"`` (dÃ©faut) ou ``\"premium\"`` (stub seam abonnement ;
    mÃªme comportement que standard tant que le produit n'active pas le palier).
    """
    override = (settings.OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE or "").strip()
    if override:
        mid = normalize_openai_model_id(override)
        assert_assistant_chat_model_allowed(mid)
        return mid

    legacy = (settings.OPENAI_MODEL or "").strip()
    if legacy:
        mid = normalize_openai_model_id(legacy)
        if mid == _DEPRECATED_ASSISTANT_LEGACY_MODEL:
            logger.warning(
                "OPENAI_MODEL=%s ignoré pour assistant_chat (legacy non supporté, IA10). Utiliser OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE ou retirer gpt-3.5-turbo.",
                legacy,
            )
        elif mid in ASSISTANT_CHAT_ALLOWED_MODEL_IDS:
            logger.debug(
                "assistant_chat: utilisation de OPENAI_MODEL (legacy documenté)=%s", mid
            )
            return mid
        else:
            logger.warning(
                "OPENAI_MODEL=%s ignoré pour assistant_chat (hors allowlist IA10).",
                legacy,
            )

    tier = (user_tier or "standard").strip().lower()
    if tier == "premium":
        assert_assistant_chat_model_allowed(PREMIUM_ASSISTANT_CHAT_MODEL)
        return PREMIUM_ASSISTANT_CHAT_MODEL

    assert_assistant_chat_model_allowed(DEFAULT_ASSISTANT_CHAT_MODEL)
    return DEFAULT_ASSISTANT_CHAT_MODEL


def resolve_assistant_chat_model_for_user(
    user_id: Optional[int],
    *,
    user_tier: Optional[str] = None,
) -> str:
    """
    Point d'extension futur (compte / abonnement).

    Aujourd'hui : ``user_id`` ignorÃ© ; dÃ©lÃ¨gue Ã  :func:`resolve_assistant_chat_model`.
    """
    _ = user_id
    return resolve_assistant_chat_model(user_tier=user_tier)


# ---------------------------------------------------------------------------
# DÃ©lÃ©gation explicite â€” vÃ©ritÃ© mÃ©tier reste dans les modules existants
# ---------------------------------------------------------------------------


def resolve_exercises_ai_model_public() -> str:
    """Exercices IA SSE : dÃ©faut ``o3``, overrides dans ``ai_generation_policy``."""
    from app.core.ai_generation_policy import resolve_exercise_ai_model

    return resolve_exercise_ai_model()


def resolve_challenges_ai_model_public(challenge_type: str) -> str:
    """DÃ©fis IA SSE : dÃ©faut ``o3``, overrides dans ``challenge_ai_model_policy``."""
    from app.services.challenges.challenge_ai_model_policy import (
        resolve_challenge_ai_model,
    )

    return resolve_challenge_ai_model(challenge_type)


def resolve_challenges_ai_fallback_public(challenge_type: str) -> str:
    """Fallback stream vide (famille o3) : policy ``challenge_ai_model_policy``."""
    from app.services.challenges.challenge_ai_model_policy import (
        resolve_challenge_ai_fallback_model,
    )

    return resolve_challenge_ai_fallback_model(challenge_type)

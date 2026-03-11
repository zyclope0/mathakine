"""
Service de préparation du flux SSE IA pour défis (LOT 3 boundary).

Extrait du handler la validation, normalisation et préparation métier
pour generate_challenge_stream. Le handler reste fin : lecture request, appel service, StreamingResponse.
"""

from typing import Optional, Tuple

import app.core.constants as constants
from app.core.config import settings
from app.core.logging_config import get_logger
from app.schemas.logic_challenge import GenerateChallengeStreamQuery
from app.utils.enum_mapping import age_group_exercise_from_api
from app.utils.prompt_sanitizer import sanitize_user_prompt, validate_prompt_safety

logger = get_logger(__name__)

VALID_CHALLENGE_TYPES = [
    "sequence",
    "pattern",
    "visual",
    "puzzle",
    "graph",
    "riddle",
    "deduction",
    "chess",
    "coding",
    "probability",
]


def prepare_stream_context(
    *,
    challenge_type_raw: str = "sequence",
    age_group_raw: str = "10-12",
    prompt_raw: str = "",
    user_id: Optional[int] = None,
    accept_language: str = "fr",
) -> Tuple[Optional[GenerateChallengeStreamQuery], Optional[str]]:
    """
    Prépare le contexte métier pour la génération IA streaming.

    Returns:
        (query, None) en succès
        (None, error_message) en erreur (pour SSE error response)
    """
    # Validation et sanitization du prompt
    is_safe, safety_reason = validate_prompt_safety(prompt_raw)
    if not is_safe:
        logger.warning(f"Prompt utilisateur rejeté pour sécurité: {safety_reason}")
        return None, f"Prompt invalide: {safety_reason}"

    prompt = sanitize_user_prompt(prompt_raw)

    # Normalisation challenge_type
    challenge_type = challenge_type_raw.lower()
    if challenge_type not in VALID_CHALLENGE_TYPES:
        logger.warning(
            f"Type de challenge invalide: {challenge_type_raw}, utilisation de 'sequence' par défaut"
        )
        challenge_type = "sequence"

    # Résolution age_group
    age_group = (
        age_group_exercise_from_api(age_group_raw) or constants.AgeGroups.GROUP_6_8
    )

    # Rate limiting (contexte utilisateur)
    if user_id:
        from app.utils.rate_limiter import rate_limiter

        allowed, rate_limit_reason = rate_limiter.check_rate_limit(
            user_id=user_id, max_per_hour=10, max_per_day=50
        )
        if not allowed:
            logger.warning(
                f"Rate limit atteint pour utilisateur {user_id}: {rate_limit_reason}"
            )
            return None, f"Limite de génération atteinte: {rate_limit_reason}"

    # Vérification clé OpenAI
    if not settings.OPENAI_API_KEY:
        return None, "OpenAI API key non configurée"

    # Résolution locale
    from app.utils.translation import parse_accept_language

    locale = parse_accept_language(accept_language) or "fr"

    return (
        GenerateChallengeStreamQuery(
            challenge_type=challenge_type,
            age_group=age_group,
            prompt=prompt,
            user_id=user_id,
            locale=locale,
        ),
        None,
    )

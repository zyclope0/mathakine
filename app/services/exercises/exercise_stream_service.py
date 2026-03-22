"""
Service de préparation du flux SSE pour la génération d'exercices IA (Lot 3).

Responsabilité : validation prompt, normalisation params, préparation contexte.
Le handler ne fait que lecture request, appel service, construction StreamingResponse.
"""

from typing import Optional, Tuple

from app.core.config import settings
from app.core.logging_config import get_logger
from app.schemas.exercise import (
    GenerateExerciseStreamContext,
    GenerateExerciseStreamQuery,
)
from app.utils.prompt_sanitizer import sanitize_user_prompt, validate_prompt_safety
from app.utils.rate_limit import check_exercise_ai_generation_rate_limit
from app.utils.translation import parse_accept_language

logger = get_logger(__name__)


def prepare_stream_context(
    query: GenerateExerciseStreamQuery,
    user_id: Optional[int],
    accept_language: Optional[str],
) -> Tuple[Optional[GenerateExerciseStreamContext], Optional[str]]:
    """
    Valide et prépare le contexte pour le flux SSE.

    Returns:
        (context, None) si succès
        (None, error_message) si erreur (à passer à sse_error_response)
    """
    is_safe, safety_reason = validate_prompt_safety(query.prompt)
    if not is_safe:
        return None, f"Prompt invalide: {safety_reason}"

    prompt = sanitize_user_prompt(query.prompt)

    from app.utils.exercise_generator_validators import (
        normalize_and_validate_exercise_params,
    )

    age_group_raw = query.age_group or "6-8"
    exercise_type, age_group, derived_difficulty = (
        normalize_and_validate_exercise_params(query.exercise_type, age_group_raw)
    )

    if not settings.OPENAI_API_KEY:
        return None, "OpenAI API key non configurée"

    if user_id is not None:
        allowed, rate_msg = check_exercise_ai_generation_rate_limit(user_id)
        if not allowed:
            logger.warning(
                "Rate limit exercices IA atteint pour utilisateur %s: %s",
                user_id,
                rate_msg,
            )
            return None, rate_msg or "Limite de generation d'exercices IA atteinte."

    locale = parse_accept_language(accept_language) or "fr"

    return (
        GenerateExerciseStreamContext(
            exercise_type=exercise_type,
            age_group=age_group,
            derived_difficulty=derived_difficulty,
            prompt=prompt,
            locale=locale,
            user_id=user_id,
        ),
        None,
    )

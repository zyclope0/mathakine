"""
Service de préparation du flux SSE pour la génération d'exercices IA (Lot 3).

Responsabilité : validation prompt, normalisation params, préparation contexte.
Le handler ne fait que lecture request, appel service, construction StreamingResponse.
"""

from typing import Optional, Tuple

from app.core.config import settings
from app.schemas.exercise import (
    GenerateExerciseStreamContext,
    GenerateExerciseStreamQuery,
)
from app.utils.prompt_sanitizer import sanitize_user_prompt, validate_prompt_safety
from app.utils.translation import parse_accept_language


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

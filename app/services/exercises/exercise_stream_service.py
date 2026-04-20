"""
Service de préparation du flux SSE pour la génération d'exercices IA (Lot 3).

Responsabilité : validation prompt, normalisation params, préparation contexte.
Le handler ne fait que lecture request, appel service, construction StreamingResponse.
"""

from typing import Optional, Tuple

from app.core.config import settings
from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.repositories.exercise_repository import ExerciseRepository
from app.schemas.exercise import (
    GenerateExerciseStreamContext,
    GenerateExerciseStreamQuery,
)
from app.services.exercises.adaptive_difficulty_service import (
    AdaptiveGenerationContext,
    resolve_adaptive_context,
)
from app.utils.exercise_generator_validators import (
    normalize_and_validate_exercise_params,
    normalize_exercise_type,
)
from app.utils.prompt_sanitizer import sanitize_user_prompt, validate_prompt_safety
from app.utils.rate_limit import check_exercise_ai_generation_rate_limit
from app.utils.translation import parse_accept_language

logger = get_logger(__name__)


def _resolve_stream_adaptive_context(
    exercise_type: str,
    user_id: Optional[int],
) -> Optional[AdaptiveGenerationContext]:
    """Résout le contexte adaptatif du stream IA quand l'age_group est omis."""
    if user_id is None:
        return None
    try:
        with sync_db_session() as db:
            user = ExerciseRepository.get_user_by_id(db, user_id)
            if user is None:
                return None
            return resolve_adaptive_context(db, user, exercise_type)
    except Exception as err:  # noqa: BLE001 - fail-open vers le fallback historique
        logger.warning(
            "[ExerciseAIStream] adaptive context resolution failed user_id={} type={}: {}",
            user_id,
            exercise_type,
            err,
        )
        return None


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

    normalized_type = normalize_exercise_type(query.exercise_type)

    if not settings.OPENAI_API_KEY:
        return None, "OpenAI API key non configurée"

    if user_id is not None:
        allowed, rate_msg = check_exercise_ai_generation_rate_limit(user_id)
        if not allowed:
            logger.warning(
                "Rate limit exercices IA atteint pour utilisateur {}: {}",
                user_id,
                rate_msg,
            )
            return None, rate_msg or "Limite de generation d'exercices IA atteinte."

    adaptive_ctx: Optional[AdaptiveGenerationContext] = None
    if query.age_group:
        age_group_raw = query.age_group
    else:
        adaptive_ctx = _resolve_stream_adaptive_context(normalized_type, user_id)
        age_group_raw = adaptive_ctx.age_group if adaptive_ctx is not None else "6-8"

    exercise_type, age_group, derived_difficulty = (
        normalize_and_validate_exercise_params(normalized_type, age_group_raw)
    )

    locale = parse_accept_language(accept_language) or "fr"

    return (
        GenerateExerciseStreamContext(
            exercise_type=exercise_type,
            age_group=age_group,
            derived_difficulty=derived_difficulty,
            pedagogical_band=(
                adaptive_ctx.pedagogical_band if adaptive_ctx is not None else None
            ),
            mastery_source=(
                adaptive_ctx.mastery_source if adaptive_ctx is not None else None
            ),
            prompt=prompt,
            locale=locale,
            user_id=user_id,
        ),
        None,
    )

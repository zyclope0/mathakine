"""
Service applicatif pour la génération d'exercices (LOT A5).
Orchestration : résolution adaptive, normalisation, génération AI/simple, persistance.
Modèle runtime : sync, exécuté via run_db_bound() depuis les handlers.
"""

from typing import Any, Dict, Optional

from app.core.db_boundary import sync_db_session
from app.core.difficulty_tier import (
    build_exercise_generation_profile,
    clamp_difficulty_for_type,
)
from app.core.logging_config import get_logger
from app.generators.exercise_generator import (
    ensure_explanation,
    generate_ai_exercise,
    generate_simple_exercise,
)
from app.repositories.exercise_repository import ExerciseRepository
from app.schemas.exercise import GenerateExerciseResult
from app.services.exercises.adaptive_difficulty_service import (
    AdaptiveGenerationContext,
    resolve_adaptive_context,
    resolve_adaptive_difficulty,
)
from app.utils.exercise_generator_validators import (
    normalize_and_validate_exercise_params,
    normalize_exercise_type,
)

logger = get_logger(__name__)


def _resolve_age_group_adaptive_sync(
    user_id: int,
    exercise_type_raw: Optional[str],
    age_group_raw: Optional[str],
) -> Optional[str]:
    """
    Résout age_group de façon adaptative si l'utilisateur existe et qu'aucun
    age_group n'est fourni. Sync, exécuté dans run_db_bound.
    """
    if age_group_raw:
        return age_group_raw
    try:
        resolved_type = normalize_exercise_type(exercise_type_raw or "ADDITION")
        with sync_db_session() as db:
            user = ExerciseRepository.get_user_by_id(db, user_id)
            if user:
                return resolve_adaptive_difficulty(db, user, resolved_type)
    except Exception as err:
        logger.warning("[AdaptiveDifficulty] Résolution échouée, fallback: %s", err)
    return age_group_raw


def _resolve_adaptive_context_sync(
    user_id: int,
    exercise_type_raw: Optional[str],
    age_group_raw: Optional[str],
) -> Optional[AdaptiveGenerationContext]:
    """
    Résout le contexte adaptatif complet (age_group + pedagogical_band).

    Uniquement déclenché quand ``user_id`` est fourni ET qu'``age_group_raw``
    est absent (sinon la tranche d'âge est imposée explicitement).
    Retourne ``None`` si l'utilisateur n'est pas trouvé ou en cas d'erreur.
    """
    if age_group_raw:
        return None  # Explicit age_group → no adaptive context needed
    try:
        resolved_type = normalize_exercise_type(exercise_type_raw or "ADDITION")
        with sync_db_session() as db:
            user = ExerciseRepository.get_user_by_id(db, user_id)
            if user:
                return resolve_adaptive_context(db, user, resolved_type)
    except Exception as err:
        logger.warning(
            "[AdaptiveDifficulty] Résolution contexte échouée, fallback: %s", err
        )
    return None


def _parse_use_ai(use_ai: Any) -> bool:
    """Parse le paramètre use_ai (bool ou string)."""
    if isinstance(use_ai, bool):
        return use_ai
    if isinstance(use_ai, str):
        return use_ai.lower() in ("true", "1", "yes", "y")
    return False


class AgeGroupRequiredError(Exception):
    """Levée quand age_group est requis (API) mais non fourni ni résolu."""

    pass


def _resolve_effective_difficulty(
    exercise_type: str,
    derived_difficulty: str,
    user_id: Optional[int],
) -> str:
    """Applique le clamp type x difficulte sans modifier l'axe age_group."""
    effective_difficulty, reason = clamp_difficulty_for_type(
        exercise_type, derived_difficulty
    )
    if reason is None:
        return effective_difficulty

    logger.info(
        "[ExerciseGeneration] type_difficulty_clamp user_id={} exercise_type={} "
        "requested={} effective={} reason={}",
        user_id,
        exercise_type,
        derived_difficulty,
        effective_difficulty,
        reason,
    )
    return effective_difficulty


def generate_exercise_sync(
    exercise_type_raw: str,
    age_group_raw: Optional[str],
    use_ai: Any = False,
    adaptive: bool = True,
    save: bool = True,
    user_id: Optional[int] = None,
    locale: str = "fr",
    require_age_group: bool = False,
) -> GenerateExerciseResult:
    """
    Génère un exercice (AI ou simple), optionnellement persisté.
    Sync, exécuté via run_db_bound() depuis les handlers.
    """
    # Résolution adaptive — chemin enrichi (second axe F42) quand user_id fourni
    adaptive_ctx = None
    if adaptive and user_id:
        adaptive_ctx = _resolve_adaptive_context_sync(
            user_id, exercise_type_raw, age_group_raw
        )
        if adaptive_ctx is not None:
            age_group_raw = adaptive_ctx.age_group
        else:
            # Fallback: simple age_group resolution (legacy path)
            age_group_raw = _resolve_age_group_adaptive_sync(
                user_id, exercise_type_raw, age_group_raw
            )

    if require_age_group and not age_group_raw:
        raise AgeGroupRequiredError("Le paramètre 'age_group' est requis")

    # Normalisation et validation
    exercise_type, age_group, derived_difficulty = (
        normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
    )
    effective_difficulty = _resolve_effective_difficulty(
        exercise_type, derived_difficulty, user_id
    )

    # Resolve the pedagogical band: use mastery-driven band when available,
    # otherwise fall back to the legacy derivation (age_group → difficulty → band).
    pedagogical_band_override = (
        adaptive_ctx.pedagogical_band if adaptive_ctx is not None else None
    )

    # Build F42 profile before generation so both paths have it available.
    f42_profile = build_exercise_generation_profile(
        exercise_type,
        age_group,
        effective_difficulty,
        pedagogical_band_override=pedagogical_band_override,
    )
    logger.debug(
        "F42 profile: tier=%s band=%s source=%s",
        f42_profile["difficulty_tier"],
        f42_profile["pedagogical_band"],
        getattr(adaptive_ctx, "mastery_source", "legacy"),
    )

    # Génération — bande pédagogique injectée dans les générateurs locaux
    ai_generated = _parse_use_ai(use_ai)
    if ai_generated:
        exercise_dict = generate_ai_exercise(
            exercise_type,
            age_group,
            difficulty_override=effective_difficulty,
            pedagogical_band_override=pedagogical_band_override,
        )
    else:
        exercise_dict = generate_simple_exercise(
            exercise_type,
            age_group,
            difficulty_override=effective_difficulty,
            pedagogical_band_override=pedagogical_band_override,
        )

    # Ensure the F42 tier is propagated even if generators set it to None.
    if exercise_dict.get("difficulty_tier") is None and f42_profile["difficulty_tier"]:
        exercise_dict["difficulty_tier"] = f42_profile["difficulty_tier"]

    exercise_dict = ensure_explanation(exercise_dict)
    logger.debug("Explication générée: %s", exercise_dict.get("explanation", ""))

    # Persistance conditionnelle
    if save:
        try:
            with sync_db_session() as db:
                created = ExerciseRepository.persist_generated_exercise(
                    db=db,
                    exercise_type=exercise_dict["exercise_type"],
                    age_group=exercise_dict["age_group"],
                    difficulty=exercise_dict["difficulty"],
                    difficulty_tier=exercise_dict.get("difficulty_tier"),
                    title=exercise_dict["title"],
                    question=exercise_dict["question"],
                    correct_answer=exercise_dict["correct_answer"],
                    choices=exercise_dict.get("choices") or [],
                    explanation=exercise_dict.get("explanation") or "",
                    hint=exercise_dict.get("hint"),
                    tags=exercise_dict.get("tags", "generated"),
                    ai_generated=ai_generated,
                )
                if created and created.get("id"):
                    exercise_dict["id"] = created["id"]
                    logger.info("Exercice sauvegardé avec ID=%s", created["id"])
                else:
                    raise ValueError("Persistance exercice échouée (aucun id retourné)")
        except Exception as save_err:
            logger.warning("Erreur lors de la sauvegarde: %s", save_err)
            raise

    return GenerateExerciseResult.model_validate(exercise_dict)

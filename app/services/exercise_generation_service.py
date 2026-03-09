"""
Service applicatif pour la génération d'exercices.
Orchestration : résolution adaptive, normalisation, génération AI/simple, persistance.
"""

from typing import Any, Dict, Optional

from app.core.logging_config import get_logger
from app.schemas.exercise import GenerateExerciseResult
from app.repositories.exercise_repository import ExerciseRepository
from app.services.adaptive_difficulty_service import resolve_adaptive_difficulty
from app.utils.db_utils import db_session
from app.generators.exercise_generator import (
    ensure_explanation,
    generate_ai_exercise,
    generate_simple_exercise,
)
from app.utils.exercise_generator_validators import (
    normalize_and_validate_exercise_params,
    normalize_exercise_type,
)

logger = get_logger(__name__)


async def _resolve_age_group_adaptive(
    user_id: int,
    exercise_type_raw: Optional[str],
    age_group_raw: Optional[str],
) -> Optional[str]:
    """
    Résout age_group de façon adaptative si l'utilisateur existe et qu'aucun
    age_group n'est fourni.
    """
    if age_group_raw:
        return age_group_raw
    try:
        resolved_type = normalize_exercise_type(exercise_type_raw or "ADDITION")
        async with db_session() as db:
            user = ExerciseRepository.get_user_by_id(db, user_id)
            if user:
                return resolve_adaptive_difficulty(db, user, resolved_type)
    except Exception as err:
        logger.warning(f"[AdaptiveDifficulty] Résolution échouée, fallback: {err}")
    return age_group_raw


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


async def generate_exercise(
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

    Args:
        exercise_type_raw: Type brut (ex: "addition")
        age_group_raw: Groupe d'âge brut (optionnel si adaptive)
        use_ai: Utiliser la génération IA
        adaptive: Résoudre age_group de façon adaptative
        save: Persister en base
        user_id: ID utilisateur (pour adaptive)
        locale: Locale (pour persistance, non utilisée actuellement)
        require_age_group: Si True (API), lève AgeGroupRequiredError si non fourni

    Returns:
        GenerateExerciseResult conforme au contrat de sortie
    """
    # Résolution adaptive
    if adaptive and user_id:
        age_group_raw = await _resolve_age_group_adaptive(
            user_id, exercise_type_raw, age_group_raw
        )

    if require_age_group and not age_group_raw:
        raise AgeGroupRequiredError("Le paramètre 'age_group' est requis")

    # Normalisation et validation
    exercise_type, age_group, derived_difficulty = (
        normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
    )

    # Génération
    ai_generated = _parse_use_ai(use_ai)
    if ai_generated:
        exercise_dict = generate_ai_exercise(exercise_type, age_group)
    else:
        exercise_dict = generate_simple_exercise(exercise_type, age_group)

    exercise_dict = ensure_explanation(exercise_dict)
    logger.debug(f"Explication générée: {exercise_dict.get('explanation', '')}")

    # Persistance conditionnelle
    if save:
        try:
            async with db_session() as db:
                created = ExerciseRepository.persist_generated_exercise(
                    db=db,
                    exercise_type=exercise_dict["exercise_type"],
                    age_group=exercise_dict["age_group"],
                    difficulty=exercise_dict["difficulty"],
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
                    logger.info(f"Exercice sauvegardé avec ID={created['id']}")
                else:
                    raise ValueError("Persistance exercice échouée (aucun id retourné)")
        except Exception as save_err:
            logger.warning(f"Erreur lors de la sauvegarde: {save_err}")
            raise

    return GenerateExerciseResult.model_validate(exercise_dict)

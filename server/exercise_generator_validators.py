"""
Validation et normalisation des paramètres pour la génération d'exercices.

Extrait de exercise_generator.py (PR découpage) — fonctions pures sans dépendance DB/HTTP.
"""
from typing import Optional

from app.core.constants import (
    AgeGroups,
    DifficultyLevels,
    ExerciseTypes,
    normalize_age_group,
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def normalize_exercise_type(exercise_type) -> str:
    """Normalise le type d'exercice vers une valeur ExerciseTypes."""
    if not exercise_type:
        return ExerciseTypes.ADDITION

    exercise_type_lower = exercise_type.lower()

    for type_key, aliases in ExerciseTypes.TYPE_ALIASES.items():
        if exercise_type_lower in aliases:
            return type_key

    exercise_type_upper = exercise_type.upper()
    if exercise_type_upper in ExerciseTypes.ALL_TYPES:
        return exercise_type_upper

    logger.info(
        f"⚠️ Type d'exercice non reconnu: {exercise_type}, utilisation de ADDITION par défaut"
    )
    return ExerciseTypes.ADDITION


def normalize_difficulty(difficulty) -> str:
    """Normalise le niveau de difficulté vers une valeur DifficultyLevels."""
    if not difficulty:
        return DifficultyLevels.PADAWAN

    difficulty_lower = difficulty.lower()

    for level_key, aliases in DifficultyLevels.LEVEL_ALIASES.items():
        if difficulty_lower in aliases:
            return level_key

    difficulty_upper = difficulty.upper()
    if difficulty_upper in DifficultyLevels.ALL_LEVELS:
        return difficulty_upper

    logger.info(
        f"⚠️ Niveau de difficulté non reconnu: {difficulty}, utilisation de PADAWAN par défaut"
    )
    return DifficultyLevels.PADAWAN


def normalize_and_validate_exercise_params(
    exercise_type_raw: Optional[str], age_group_raw: Optional[str]
) -> tuple[str, str, str]:
    """
    Normalise et valide les paramètres d'exercice (type et groupe d'âge).
    Retourne (exercise_type, age_group, derived_difficulty).
    """
    from app.core.constants import get_difficulty_from_age_group as _get_difficulty

    exercise_type = normalize_exercise_type(exercise_type_raw)
    age_group = normalize_age_group(age_group_raw)
    derived_difficulty = _get_difficulty(age_group)

    if exercise_type not in ExerciseTypes.ALL_TYPES:
        logger.info(
            f"⚠️ Type normalisé invalide: {exercise_type}, utilisation de ADDITION par défaut"
        )
        exercise_type = ExerciseTypes.ADDITION

    if age_group not in AgeGroups.ALL_GROUPS:
        logger.info(
            f"⚠️ Groupe d'âge non reconnu: {age_group_raw}, utilisation de {AgeGroups.GROUP_6_8} par défaut"
        )
        age_group = AgeGroups.GROUP_6_8
        derived_difficulty = _get_difficulty(age_group)

    return exercise_type, age_group, derived_difficulty


# Réexport pour compatibilité (exercise_generator utilisait sa propre impl)
from app.core.constants import get_difficulty_from_age_group

__all__ = [
    "normalize_exercise_type",
    "normalize_difficulty",
    "normalize_and_validate_exercise_params",
    "get_difficulty_from_age_group",
]

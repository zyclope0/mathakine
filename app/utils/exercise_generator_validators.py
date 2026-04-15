"""
Validation et normalisation des paramètres pour la génération d'exercices.

Fonctions pures sans dépendance DB/HTTP — couche applicative.
"""

from typing import Optional

from app.core.constants import (
    AgeGroups,
    DifficultyLevels,
    ExerciseTypes,
    get_difficulty_from_age_group,
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
        "⚠️ Type d'exercice non reconnu: %s, utilisation de ADDITION par défaut",
        exercise_type,
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
        "⚠️ Niveau de difficulté non reconnu: %s, utilisation de PADAWAN par défaut",
        difficulty,
    )
    return DifficultyLevels.PADAWAN


def normalize_and_validate_exercise_params(
    exercise_type_raw: Optional[str], age_group_raw: Optional[str]
) -> tuple[str, str, str]:
    """
    Normalise et valide les paramètres d'exercice (type et groupe d'âge).
    Retourne (exercise_type, age_group, derived_difficulty).
    """
    exercise_type = normalize_exercise_type(exercise_type_raw)
    age_group = normalize_age_group(age_group_raw)
    derived_difficulty = get_difficulty_from_age_group(age_group)

    if exercise_type not in ExerciseTypes.ALL_TYPES:
        logger.info(
            "⚠️ Type normalisé invalide: %s, utilisation de ADDITION par défaut",
            exercise_type,
        )
        exercise_type = ExerciseTypes.ADDITION

    if age_group not in AgeGroups.ALL_GROUPS:
        logger.info(
            "⚠️ Groupe d'âge non reconnu: %s, utilisation de %s par défaut",
            age_group_raw,
            AgeGroups.GROUP_6_8,
        )
        age_group = AgeGroups.GROUP_6_8
        derived_difficulty = get_difficulty_from_age_group(age_group)

    return exercise_type, age_group, derived_difficulty


__all__ = [
    "normalize_exercise_type",
    "normalize_difficulty",
    "normalize_and_validate_exercise_params",
    "get_difficulty_from_age_group",
]

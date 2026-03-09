"""
Réexport depuis app — compatibilité couche HTTP.
"""

from app.utils.exercise_generator_validators import (
    get_difficulty_from_age_group,
    normalize_and_validate_exercise_params,
    normalize_difficulty,
    normalize_exercise_type,
)

__all__ = [
    "get_difficulty_from_age_group",
    "normalize_and_validate_exercise_params",
    "normalize_difficulty",
    "normalize_exercise_type",
]

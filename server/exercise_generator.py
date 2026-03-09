"""
Réexport depuis app — compatibilité couche HTTP.
"""

from app.generators.exercise_generator import (
    ensure_explanation,
    generate_ai_exercise,
    generate_simple_exercise,
)
from app.utils.exercise_generator_validators import (
    normalize_and_validate_exercise_params,
)

__all__ = [
    "ensure_explanation",
    "generate_ai_exercise",
    "generate_simple_exercise",
    "normalize_and_validate_exercise_params",
]

"""
Réexport depuis app — compatibilité couche HTTP.
"""

from app.utils.exercise_generator_helpers import (
    apply_test_title,
    build_base_exercise_data,
    default_addition_fallback,
    generate_smart_choices,
    init_exercise_context,
)

__all__ = [
    "apply_test_title",
    "build_base_exercise_data",
    "default_addition_fallback",
    "generate_smart_choices",
    "init_exercise_context",
]

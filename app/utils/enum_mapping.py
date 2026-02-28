"""
Couche unique pour les conversions enum ↔ string API.

Objectif : aucune conversion inline (.upper(), .lower(), cast) dans les handlers.
Les handlers importent depuis ce module au lieu de manipuler les enums directement.

Utilisation :
  - from_api_str : string brute (query/body) → valeur normalisée pour le service
  - to_api_str  : valeur enum/DB → string pour la réponse JSON
"""

from typing import Optional, Union

from app.core.constants import AgeGroups, DifficultyLevels, ExerciseTypes
from app.models.exercise import DifficultyLevel, ExerciseType

# Import différé pour éviter cycles
# from server.exercise_generator_validators import normalize_exercise_type, normalize_age_group
# from app.services.challenge_service import normalize_age_group_for_db, normalize_age_group_for_frontend


# -----------------------------------------------------------------------------
# Exercices (ExerciseType, DifficultyLevel, age_group format "6-8")
# -----------------------------------------------------------------------------


def exercise_type_from_api(value: Optional[str]) -> Optional[str]:
    """
    String API (addition, ADDITION, etc.) → valeur normalisée (ADDITION).
    Retourne None si value est vide/None.
    """
    if not value or not str(value).strip():
        return None
    from server.exercise_generator_validators import normalize_exercise_type

    return normalize_exercise_type(value)


def exercise_type_to_api(value: Union[ExerciseType, str, None]) -> str:
    """Enum ou string DB → string API (ADDITION)."""
    if value is None:
        return ExerciseTypes.ADDITION
    if isinstance(value, ExerciseType):
        return value.value
    return str(value).upper() if str(value).strip() else ExerciseTypes.ADDITION


def difficulty_from_api(value: Optional[str]) -> Optional[str]:
    """
    String API (padawan, PADAWAN, etc.) → valeur normalisée (PADAWAN).
    Retourne None si value est vide/None.
    """
    if not value or not str(value).strip():
        return None
    from server.exercise_generator_validators import normalize_difficulty

    return normalize_difficulty(value)


def difficulty_to_api(value: Union[DifficultyLevel, str, None]) -> str:
    """Enum ou string DB → string API (PADAWAN)."""
    if value is None:
        return DifficultyLevels.PADAWAN
    if isinstance(value, DifficultyLevel):
        return value.value
    return str(value).upper() if str(value).strip() else DifficultyLevels.PADAWAN


def age_group_exercise_from_api(value: Optional[str]) -> Optional[str]:
    """
    String API (6-8, 9-11, etc.) → valeur normalisée pour exercices.
    Retourne None si value est vide/None.
    """
    if not value or not str(value).strip():
        return None
    from app.core.constants import normalize_age_group

    return normalize_age_group(value)


def age_group_exercise_to_api(value: Union[str, None]) -> str:
    """Groupe d'âge exercice → string API (6-8, 9-11)."""
    if not value:
        return AgeGroups.GROUP_9_11
    return str(value)


# -----------------------------------------------------------------------------
# Challenges (LogicChallengeType, AgeGroup DB)
# -----------------------------------------------------------------------------


def challenge_type_from_api(value: Optional[str]) -> Optional[str]:
    """String API → type challenge normalisé (sequence, pattern, etc.)."""
    if not value or not str(value).strip():
        return None
    import app.core.constants as constants

    return constants.normalize_challenge_type(value) if value else None


def challenge_type_to_api(value) -> str:
    """Enum LogicChallengeType ou string → string API (sequence)."""
    if value is None:
        return "sequence"
    return str(value).lower() if hasattr(value, "lower") else str(value).lower()


def age_group_challenge_from_api(value: Optional[str]):
    """
    String API (6-8, 9-11, etc.) → AgeGroup enum pour la DB.
    Retourne None si value est vide/None.
    """
    if not value or not str(value).strip():
        return None
    from app.services.challenge_service import normalize_age_group_for_db

    return normalize_age_group_for_db(value)


def age_group_challenge_to_api(value) -> str:
    """AgeGroup enum → string API (6-8, 9-11, adulte, tous-ages)."""
    if value is None:
        return "tous-ages"
    from app.services.challenge_service import normalize_age_group_for_frontend

    return normalize_age_group_for_frontend(value)

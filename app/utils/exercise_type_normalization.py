"""
Normalisation des types d'exercice pour comparaisons métier robustes.

Convention canonique (lecture tolérante des données historiques) :
    - Comparer deux types via une clé en **minuscules**, sans espaces en bordure.
    - Les valeurs stockées peuvent être ``ExerciseType.ADDITION`` ("ADDITION"),
      ``"addition"``, ``"Addition"``, etc. — toutes se mappent sur la même clé.

Ne pas utiliser pour la persistance : uniquement pour matching / filtrage logique.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


def normalize_exercise_type_key(value: Any) -> str:
    """
    Retourne la clé canonique pour comparer des types d'exercice.

    Args:
        value: ``ExerciseType``, chaîne brute issue de Progress/Exercise, etc.

    Returns:
        Chaîne minuscule strip ; chaîne vide si valeur absente ou non convertible.
    """
    if value is None:
        return ""
    if isinstance(value, Enum):
        return str(value.value).lower().strip()
    s = str(value).strip()
    if not s:
        return ""
    return s.lower()

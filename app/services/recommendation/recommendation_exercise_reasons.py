"""
R6 — Codes de raison stables pour recommandations exercice (i18n côté client).

``reason`` reste un court libellé EN de secours pour les clients sans ``reason_code``.
"""

from __future__ import annotations

from typing import Any, Dict, Union

# Clés stables — alignées sur le préfixe reco.exercise.* (points → _ côté next-intl)
REASON_EXERCISE_IMPROVEMENT = "reco.exercise.improvement"
REASON_EXERCISE_PROGRESSION = "reco.exercise.progression"
REASON_EXERCISE_MAINTENANCE = "reco.exercise.maintenance"
REASON_EXERCISE_DISCOVERY = "reco.exercise.discovery"
REASON_EXERCISE_FALLBACK = "reco.exercise.fallback"


def difficulty_i18n_key(diff: Union[str, Any, None]) -> str:
    """Valeur normalisée pour clés i18n (ex. initie, padawan)."""
    if diff is None:
        return ""
    s = getattr(diff, "value", diff)
    s = str(s)
    if "." in s:
        s = s.rsplit(".", 1)[-1]
    return s.lower()


def params_improvement(
    exercise_type_key: str, success_rate: int, target_difficulty: Any
) -> Dict[str, Any]:
    return {
        "exercise_type": exercise_type_key,
        "success_rate": int(success_rate),
        "target_difficulty": difficulty_i18n_key(target_difficulty),
    }


def english_improvement(exercise_type_key: str, success_rate: int) -> str:
    return (
        f"Keep working on {exercise_type_key} ({success_rate}% recent success); "
        "stay at the suggested level."
    )


def params_progression(
    exercise_type_key: str, success_rate: int, next_difficulty: Any
) -> Dict[str, Any]:
    return {
        "exercise_type": exercise_type_key,
        "success_rate": int(success_rate),
        "next_difficulty": difficulty_i18n_key(next_difficulty),
    }


def english_progression(
    exercise_type_key: str, success_rate: int, next_difficulty: Any
) -> str:
    nd = difficulty_i18n_key(next_difficulty) or str(next_difficulty)
    return (
        f"Strong results in {exercise_type_key} ({success_rate}% success). "
        f"Try the {nd} level next."
    )


def params_maintenance(
    exercise_type_key: str, target_difficulty: Any
) -> Dict[str, Any]:
    return {
        "exercise_type": exercise_type_key,
        "target_difficulty": difficulty_i18n_key(target_difficulty),
    }


def english_maintenance(exercise_type_key: str) -> str:
    return f"Refresh your skills in {exercise_type_key} at your current level."


def params_discovery(exercise_type_key: str, target_difficulty: Any) -> Dict[str, Any]:
    return {
        "exercise_type": exercise_type_key,
        "target_difficulty": difficulty_i18n_key(target_difficulty),
    }


def english_discovery(exercise_type_key: str) -> str:
    return f"Try a new exercise type: {exercise_type_key}."


def params_fallback() -> Dict[str, Any]:
    return {}


def english_fallback() -> str:
    return "Continue your learning with these picks."

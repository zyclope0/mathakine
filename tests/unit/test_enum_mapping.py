"""Tests unitaires pour app.utils.enum_mapping."""

import pytest

from app.utils.enum_mapping import (
    age_group_challenge_from_api,
    age_group_challenge_to_api,
    challenge_type_from_api,
    challenge_type_to_api,
    difficulty_from_api,
    difficulty_to_api,
    exercise_type_from_api,
    exercise_type_to_api,
)


def test_exercise_type_from_api():
    """from_api : strings variées → valeur normalisée ADDITION."""
    assert exercise_type_from_api("addition") == "ADDITION"
    assert exercise_type_from_api("ADDITION") == "ADDITION"
    assert exercise_type_from_api("  add  ") == "ADDITION"
    assert exercise_type_from_api(None) is None
    assert exercise_type_from_api("") is None


def test_exercise_type_to_api():
    """to_api : enum/str → string API."""
    from app.models.exercise import ExerciseType

    assert exercise_type_to_api(ExerciseType.ADDITION) == "ADDITION"
    assert exercise_type_to_api("ADDITION") == "ADDITION"
    assert exercise_type_to_api(None) == "ADDITION"  # default


def test_difficulty_from_api():
    """from_api : padawan, PADAWAN → PADAWAN."""
    assert difficulty_from_api("padawan") == "PADAWAN"
    assert difficulty_from_api("PADAWAN") == "PADAWAN"
    assert difficulty_from_api(None) is None


def test_difficulty_to_api():
    """to_api : enum/str → string API."""
    from app.models.exercise import DifficultyLevel

    assert difficulty_to_api(DifficultyLevel.PADAWAN) == "PADAWAN"
    assert difficulty_to_api("PADAWAN") == "PADAWAN"


def test_challenge_type_from_api():
    """from_api : sequence, pattern → normalisé (MAJUSCULE pour DB)."""
    assert challenge_type_from_api("sequence") == "SEQUENCE"
    assert challenge_type_from_api("  pattern  ") == "PATTERN"
    assert challenge_type_from_api(None) is None


def test_challenge_type_to_api():
    """to_api : enum ou str → lowercase."""
    assert challenge_type_to_api("sequence") == "sequence"
    assert challenge_type_to_api(None) == "sequence"  # default


def test_age_group_challenge_roundtrip():
    """from_api puis to_api : 6-8 → AgeGroup → 6-8."""
    ag = age_group_challenge_from_api("6-8")
    assert ag is not None
    assert age_group_challenge_to_api(ag) == "6-8"

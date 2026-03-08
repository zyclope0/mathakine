"""
Tests de caractérisation pour exercise_generator.

Valident le comportement de generate_simple_exercise et generate_ai_exercise
AVANT toute extraction de helpers communs.

Phase 3, item 3.4a — audit architecture 03/2026.
"""

import random

import pytest

from server.exercise_generator import (
    ensure_explanation,
    generate_ai_exercise,
    generate_simple_exercise,
)


def _assert_valid_exercise(ex, *, expected_type=None, ai_generated=None):
    """Assertions structurelles communes à tout exercice généré."""
    assert isinstance(ex, dict), "Le résultat doit être un dict"
    for key in (
        "exercise_type",
        "age_group",
        "difficulty",
        "title",
        "question",
        "correct_answer",
        "choices",
        "explanation",
    ):
        assert key in ex, f"Clé manquante: {key}"

    assert isinstance(ex["choices"], list), "choices doit être une liste"
    assert len(ex["choices"]) >= 2, "Au moins 2 choix requis"

    choices_str = [str(c) for c in ex["choices"]]
    assert (
        str(ex["correct_answer"]) in choices_str
    ), f"correct_answer '{ex['correct_answer']}' absent de choices {choices_str}"

    assert ex["title"], "Le titre ne doit pas être vide"
    assert ex["question"], "La question ne doit pas être vide"

    if expected_type:
        assert ex["exercise_type"] == expected_type
    if ai_generated is not None:
        assert ex.get("ai_generated") == ai_generated


# ── generate_simple_exercise ──────────────────────────────────────────────


class TestGenerateSimpleExercise:
    """Tests couvrant tous les types pour generate_simple_exercise."""

    def test_addition(self):
        random.seed(42)
        ex = generate_simple_exercise("ADDITION", "9-11")
        _assert_valid_exercise(ex, expected_type="ADDITION", ai_generated=False)

    def test_soustraction(self):
        random.seed(42)
        ex = generate_simple_exercise("SOUSTRACTION", "9-11")
        _assert_valid_exercise(ex, expected_type="SOUSTRACTION", ai_generated=False)

    def test_multiplication(self):
        random.seed(42)
        ex = generate_simple_exercise("MULTIPLICATION", "9-11")
        _assert_valid_exercise(ex, expected_type="MULTIPLICATION", ai_generated=False)

    def test_division(self):
        random.seed(42)
        ex = generate_simple_exercise("DIVISION", "9-11")
        _assert_valid_exercise(ex, expected_type="DIVISION", ai_generated=False)

    def test_fractions(self):
        random.seed(42)
        ex = generate_simple_exercise("FRACTIONS", "12-14")
        _assert_valid_exercise(ex, expected_type="FRACTIONS", ai_generated=False)

    def test_geometrie(self):
        random.seed(42)
        ex = generate_simple_exercise("GEOMETRIE", "12-14")
        _assert_valid_exercise(ex, expected_type="GEOMETRIE", ai_generated=False)

    def test_mixte(self):
        random.seed(42)
        ex = generate_simple_exercise("MIXTE", "12-14")
        _assert_valid_exercise(ex, expected_type="MIXTE", ai_generated=False)

    def test_texte(self):
        random.seed(42)
        ex = generate_simple_exercise("TEXTE", "9-11")
        _assert_valid_exercise(ex, expected_type="TEXTE", ai_generated=False)

    def test_divers(self):
        random.seed(42)
        ex = generate_simple_exercise("DIVERS", "9-11")
        _assert_valid_exercise(ex, expected_type="DIVERS", ai_generated=False)

    def test_unknown_type_falls_back(self):
        random.seed(42)
        ex = generate_simple_exercise("UNKNOWN_TYPE", "9-11")
        _assert_valid_exercise(ex, ai_generated=False)

    def test_young_age_group(self):
        random.seed(42)
        ex = generate_simple_exercise("ADDITION", "6-8")
        _assert_valid_exercise(ex, expected_type="ADDITION", ai_generated=False)

    def test_adult_age_group(self):
        random.seed(42)
        ex = generate_simple_exercise("MULTIPLICATION", "adulte")
        _assert_valid_exercise(ex, expected_type="MULTIPLICATION", ai_generated=False)


# ── generate_ai_exercise ─────────────────────────────────────────────────


class TestGenerateAiExercise:
    """Tests couvrant tous les types pour generate_ai_exercise."""

    def test_addition(self):
        random.seed(42)
        ex = generate_ai_exercise("ADDITION", "9-11")
        _assert_valid_exercise(ex, expected_type="ADDITION", ai_generated=True)

    def test_soustraction(self):
        random.seed(42)
        ex = generate_ai_exercise("SOUSTRACTION", "9-11")
        _assert_valid_exercise(ex, expected_type="SOUSTRACTION", ai_generated=True)

    def test_multiplication(self):
        random.seed(42)
        ex = generate_ai_exercise("MULTIPLICATION", "9-11")
        _assert_valid_exercise(ex, expected_type="MULTIPLICATION", ai_generated=True)

    def test_division(self):
        random.seed(42)
        ex = generate_ai_exercise("DIVISION", "9-11")
        _assert_valid_exercise(ex, expected_type="DIVISION", ai_generated=True)

    def test_fractions(self):
        random.seed(42)
        ex = generate_ai_exercise("FRACTIONS", "12-14")
        _assert_valid_exercise(ex, expected_type="FRACTIONS", ai_generated=True)

    def test_geometrie(self):
        random.seed(42)
        ex = generate_ai_exercise("GEOMETRIE", "12-14")
        _assert_valid_exercise(ex, expected_type="GEOMETRIE", ai_generated=True)

    def test_mixte(self):
        random.seed(42)
        ex = generate_ai_exercise("MIXTE", "12-14")
        _assert_valid_exercise(ex, expected_type="MIXTE", ai_generated=True)

    def test_texte(self):
        random.seed(42)
        ex = generate_ai_exercise("TEXTE", "9-11")
        _assert_valid_exercise(ex, expected_type="TEXTE", ai_generated=True)

    def test_divers(self):
        random.seed(42)
        ex = generate_ai_exercise("DIVERS", "9-11")
        _assert_valid_exercise(ex, expected_type="DIVERS", ai_generated=True)

    def test_unknown_type_falls_back(self):
        random.seed(42)
        ex = generate_ai_exercise("UNKNOWN_TYPE", "9-11")
        _assert_valid_exercise(ex, ai_generated=True)


# ── ensure_explanation ────────────────────────────────────────────────────


class TestEnsureExplanation:
    def test_adds_explanation_if_missing(self):
        ex = {"exercise_type": "ADDITION", "correct_answer": "42"}
        result = ensure_explanation(ex)
        assert result.get("explanation"), "Doit ajouter une explication"

    def test_keeps_existing_explanation(self):
        ex = {
            "exercise_type": "ADDITION",
            "correct_answer": "42",
            "explanation": "Custom explanation.",
        }
        result = ensure_explanation(ex)
        assert result["explanation"] == "Custom explanation."

    def test_replaces_empty_explanation(self):
        ex = {
            "exercise_type": "MULTIPLICATION",
            "correct_answer": "10",
            "explanation": "",
        }
        result = ensure_explanation(ex)
        assert result["explanation"] != ""

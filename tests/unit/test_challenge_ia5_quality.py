"""IA5 — difficulté, distracteurs (choices), validateur DEDUCTION."""

from __future__ import annotations

import pytest

from app.services.challenges.challenge_answer_quality import validate_challenge_choices
from app.services.challenges.challenge_difficulty_policy import (
    calibrate_challenge_difficulty,
    estimate_structure_signals,
    title_suggests_rule_leak,
    validate_difficulty_structural_coherence,
    validate_title_difficulty_coherence,
)
from app.services.challenges.challenge_validator import (
    validate_challenge_logic,
    validate_deduction_challenge,
)


def test_title_suggests_rule_leak_detects_explicit_pattern() -> None:
    assert title_suggests_rule_leak("Le cycle ×3 puis +1")
    assert not title_suggests_rule_leak("Le mystère des cases")


def test_validate_title_difficulty_coherence_errors_when_high_rating() -> None:
    err = validate_title_difficulty_coherence("Suite ×2 à chaque pas", 4.5)
    assert err and "titre" in err[0].lower()


def test_validate_difficulty_pattern_single_question_cell() -> None:
    vd = {"grid": [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "?"]]}
    err = validate_difficulty_structural_coherence("PATTERN", vd, 4.2)
    assert err


def test_validate_difficulty_sequence_pattern_vs_rating() -> None:
    vd = {"sequence": [1, 2, 3], "pattern": "n+1"}
    err = validate_difficulty_structural_coherence("SEQUENCE", vd, 4.5)
    assert err


def test_validate_challenge_choices_min_three_and_no_duplicates() -> None:
    assert not validate_challenge_choices("SEQUENCE", "10", None)
    assert validate_challenge_choices("SEQUENCE", "10", ["10", "11"])
    dup_err = validate_challenge_choices("SEQUENCE", "10", ["10", "10", "11"])
    assert dup_err and "doublon" in dup_err[0].lower()
    assert not validate_challenge_choices("SEQUENCE", "10", ["8", "9", "10", "11"])


def test_validate_challenge_choices_correct_must_match() -> None:
    assert validate_challenge_choices("PROBABILITY", "1/2", ["1/3", "1/4", "2/3"])


def test_validate_deduction_challenge_happy_path() -> None:
    vd = {
        "type": "logic_grid",
        "entities": {
            "personnes": ["Alice", "Bob"],
            "boisson": ["thé", "café"],
        },
        "clues": ["Alice ne boit pas le café", "Bob aime le thé"],
        "description": "test",
    }
    ca = "Alice:thé,Bob:café"
    assert not validate_deduction_challenge(vd, ca, "explanation")


def test_validate_deduction_challenge_rejects_duplicate_secondary_category() -> None:
    """Même boisson pour deux personnes : bijection colonne 2 interdite."""
    vd = {
        "type": "logic_grid",
        "entities": {
            "personnes": ["Alice", "Bob"],
            "boisson": ["thé", "café"],
        },
        "clues": ["c1", "c2"],
        "description": "test",
    }
    err = validate_deduction_challenge(vd, "Alice:thé,Bob:thé", "")
    assert err and any("one-to-one" in e or "bijection" in e.lower() for e in err)


def test_validate_deduction_challenge_rejects_duplicate_tertiary_category() -> None:
    """Même ville pour deux personnes : bijection sur la 3e colonne interdite."""
    vd = {
        "type": "logic_grid",
        "entities": {
            "personnes": ["Alice", "Bob"],
            "boisson": ["thé", "café"],
            "ville": ["Paris", "Lyon"],
        },
        "clues": ["c1", "c2"],
        "description": "test",
    }
    err = validate_deduction_challenge(vd, "Alice:thé:Paris,Bob:café:Paris", "")
    assert err and any("one-to-one" in e for e in err)


def test_validate_deduction_challenge_wrong_type() -> None:
    vd = {"type": "other", "entities": {"a": [1], "b": [2]}, "clues": ["x", "y"]}
    err = validate_deduction_challenge(vd, "1:2", "")
    assert any("logic_grid" in e for e in err)


def test_validate_deduction_challenge_bad_association_count() -> None:
    vd = {
        "type": "logic_grid",
        "entities": {"p": ["A", "B"], "x": [1, 2], "y": [3, 4]},
        "clues": ["c1", "c2"],
    }
    err = validate_deduction_challenge(vd, "A:1,B:2", "")
    assert err


def test_validate_challenge_logic_runs_deduction_validator() -> None:
    data = {
        "challenge_type": "DEDUCTION",
        "title": "Grille",
        "difficulty_rating": 3.0,
        "correct_answer": "A:1",
        "solution_explanation": "ok",
        "visual_data": {
            "type": "logic_grid",
            "entities": {"p": ["A", "B"], "x": [1, 2]},
            "clues": ["c1", "c2"],
        },
    }
    ok, errors = validate_challenge_logic(data)
    assert not ok
    assert any("DEDUCTION" in e for e in errors)


def test_calibrate_challenge_difficulty_caps_on_title_leak() -> None:
    # Reste dans la bande autour de la baseline 9-11 (2.5) pour ne pas être écrasé avant les caps
    final, meta = calibrate_challenge_difficulty(
        challenge_type="sequence",
        age_group="9-11",
        visual_data={"sequence": [1, 2, 3]},
        title="La suite ×2 magique",
        ai_difficulty=3.2,
    )
    assert final <= 3.0
    assert "title_rule_leak_cap_3_0" in meta.get("caps_applied", [])


def test_estimate_structure_signals_includes_rule_visibility() -> None:
    sig = estimate_structure_signals(
        "sequence",
        {"sequence": [1, 2, 3], "pattern": "n+1"},
        "Sans indice",
    )
    assert sig.rule_visibility == "partial"

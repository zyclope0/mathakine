"""IA5 - difficulty, distractors, and deduction validator."""

from __future__ import annotations

from app.services.challenges.challenge_answer_quality import validate_challenge_choices
from app.services.challenges.challenge_difficulty_policy import (
    calibrate_challenge_difficulty,
    estimate_structure_signals,
    sanitize_leaky_title,
    title_suggests_rule_leak,
    validate_difficulty_structural_coherence,
    validate_title_difficulty_coherence,
)
from app.services.challenges.challenge_validator import (
    auto_correct_challenge,
    validate_challenge_logic,
    validate_deduction_challenge,
)


def test_title_suggests_rule_leak_detects_explicit_pattern() -> None:
    assert title_suggests_rule_leak("Le cycle x3 puis +1")
    assert title_suggests_rule_leak("Bits a l'envers !")
    assert not title_suggests_rule_leak("Le mystere des cases")


def test_sanitize_leaky_title_for_high_difficulty_coding() -> None:
    assert (
        sanitize_leaky_title("coding", "Bits a l'envers !", 4.0)
        == "Le message sous scellés"
    )


def test_validate_title_difficulty_coherence_errors_when_high_rating() -> None:
    err = validate_title_difficulty_coherence("Suite x2 a chaque pas", 4.5)
    assert err and "titre" in err[0].lower()


def test_validate_difficulty_pattern_single_question_cell() -> None:
    vd = {"grid": [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "?"]]}
    err = validate_difficulty_structural_coherence("PATTERN", vd, 4.2)
    assert err


def test_validate_difficulty_sequence_pattern_vs_rating() -> None:
    vd = {"sequence": [1, 2, 3], "pattern": "n+1"}
    err = validate_difficulty_structural_coherence("SEQUENCE", vd, 4.5)
    assert err


def test_validate_difficulty_sequence_short_single_unknown_vs_rating() -> None:
    vd = {"sequence": [3, 8, 19, 40, 75, "?"]}
    err = validate_difficulty_structural_coherence("SEQUENCE", vd, 4.0)
    assert err and "suite courte" in err[0].lower()


def test_validate_difficulty_sequence_simple_arithmetic_vs_rating() -> None:
    vd = {"sequence": [5, 10, 15, 20, 25, "?"]}
    err = validate_difficulty_structural_coherence("SEQUENCE", vd, 4.2)
    assert err and "arithm" in err[0].lower()


def test_validate_difficulty_coding_binary_short_payload_vs_rating() -> None:
    vd = {
        "type": "binary",
        "encoded_message": "10100010 10101010 01001010 10100010 11010010 10000010",
    }
    err = validate_difficulty_structural_coherence("CODING", vd, 4.0)
    assert err and "binary" in err[0].lower()


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
            "boisson": ["the", "cafe"],
        },
        "clues": ["Alice ne boit pas le cafe", "Bob aime le the"],
        "description": "test",
    }
    ca = "Alice:the,Bob:cafe"
    assert not validate_deduction_challenge(vd, ca, "explanation")


def test_validate_deduction_challenge_rejects_duplicate_secondary_category() -> None:
    vd = {
        "type": "logic_grid",
        "entities": {
            "personnes": ["Alice", "Bob"],
            "boisson": ["the", "cafe"],
        },
        "clues": ["c1", "c2"],
        "description": "test",
    }
    err = validate_deduction_challenge(vd, "Alice:the,Bob:the", "")
    assert err and any("one-to-one" in e or "bijection" in e.lower() for e in err)


def test_validate_deduction_challenge_rejects_duplicate_tertiary_category() -> None:
    vd = {
        "type": "logic_grid",
        "entities": {
            "personnes": ["Alice", "Bob"],
            "boisson": ["the", "cafe"],
            "ville": ["Paris", "Lyon"],
        },
        "clues": ["c1", "c2"],
        "description": "test",
    }
    err = validate_deduction_challenge(vd, "Alice:the:Paris,Bob:cafe:Paris", "")
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
    final, meta = calibrate_challenge_difficulty(
        challenge_type="sequence",
        age_group="9-11",
        visual_data={"sequence": [1, 2, 3]},
        title="La suite x2 magique",
        ai_difficulty=3.2,
    )
    assert final <= 3.0
    assert "title_rule_leak_cap_3_0" in meta.get("caps_applied", [])


def test_calibrate_challenge_difficulty_caps_short_binary_coding() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="coding",
        age_group="15-17",
        visual_data={
            "type": "binary",
            "encoded_message": "10100010 10101010 01001010 10100010 11010010 10000010",
        },
        title="Le mot du laboratoire",
        ai_difficulty=4.0,
    )
    assert final <= 3.2
    assert "coding_binary_short_payload_cap_3_2" in meta.get("caps_applied", [])


def test_estimate_structure_signals_includes_rule_visibility() -> None:
    sig = estimate_structure_signals(
        "sequence",
        {"sequence": [1, 2, 3], "pattern": "n+1"},
        "Sans indice",
    )
    assert sig.rule_visibility == "partial"


def test_auto_correct_challenge_sanitizes_leaky_high_difficulty_title() -> None:
    corrected = auto_correct_challenge(
        {
            "challenge_type": "CODING",
            "title": "Bits a l'envers !",
            "difficulty_rating": 4.0,
            "visual_data": {
                "type": "binary",
                "encoded_message": "10100010 10101010 01001010 10100010 11010010 10000010",
            },
        }
    )
    assert corrected["title"] == "Le message sous scellés"

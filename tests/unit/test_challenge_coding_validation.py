"""
Tests de non-régression pour challenge_coding_validation (I5).
"""

from app.services.challenges.challenge_coding_validation import (
    validate_coding_challenge,
)


def test_coding_empty_visual_data():
    err = validate_coding_challenge({}, "x", "")
    assert any("visual_data est vide" in e for e in err)


def test_coding_rejects_sequence_misclassified():
    err = validate_coding_challenge(
        {"sequence": [1, 2, 3], "type": "algorithm"},
        "4",
        "explanation",
    )
    assert any("SEQUENCE" in e and "CODING" in e for e in err)


def test_coding_rejects_shapes_misclassified():
    err = validate_coding_challenge({"shapes": ["a"]}, "x", "")
    assert any("VISUAL" in e for e in err)


def test_coding_valid_caesar_minimal():
    err = validate_coding_challenge(
        {
            "type": "caesar",
            "encoded_message": "ABC",
            "shift": 3,
        },
        "DEF",
        "rot3",
    )
    assert err == []


def test_coding_substitution_accepts_deducible_string_partial_key():
    err = validate_coding_challenge(
        {
            "type": "substitution",
            "rule_type": "keyword",
            "encoded_message": "KGTCEKGTDLS DS TCE JGMBUGBE NO TCE UMDVERSE",
            "partial_key": "GALIEO??????????????????????",
        },
        "MATHEMATICS IS THE LANGUAGE OF THE UNIVERSE",
        "keyword cipher",
    )

    assert err == []


def test_coding_substitution_string_partial_key_requires_enough_signal():
    err = validate_coding_challenge(
        {
            "type": "substitution",
            "rule_type": "keyword",
            "encoded_message": "ABC",
            "partial_key": "A?????????????????????????",
        },
        "XYZ",
        "keyword cipher",
    )

    assert any("partial_key" in e for e in err)


def test_coding_maze_invalid_path():
    maze = [["S", "."], ["#", "E"]]
    err = validate_coding_challenge(
        {
            "maze": maze,
            "start": [0, 0],
            "end": [1, 1],
        },
        "INVALID",
        "",
    )
    assert any("MAZE" in e or "ne mène pas" in e for e in err)

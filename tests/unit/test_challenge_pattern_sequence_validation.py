from app.services.challenges.challenge_pattern_sequence_validation import (
    validate_pattern_challenge,
)
from app.services.challenges.challenge_validation_analysis import analyze_pattern


def _staircase_numeric_grid() -> list[list[str]]:
    return [
        ["3", "5", "8", "12", "17"],
        ["4", "7", "11", "16", "?"],
        ["6", "10", "15", "?", "?"],
        ["9", "14", "?", "27", "35"],
        ["?", "22", "29", "37", "46"],
    ]


def test_validate_pattern_numeric_multi_cell_grid_accepts_proven_answer() -> None:
    errors = validate_pattern_challenge(
        {"grid": _staircase_numeric_grid()},
        "22, 21, 28, 20, 16",
        "",
    )

    assert errors == []


def test_validate_pattern_numeric_multi_cell_grid_rejects_wrong_answer() -> None:
    errors = validate_pattern_challenge(
        {"grid": _staircase_numeric_grid()},
        "22, 21, 99, 20, 16",
        "",
    )

    assert errors
    assert any("Pattern multi-cellules incoherent" in error for error in errors)


def test_validate_pattern_numeric_multi_cell_grid_rejects_unverifiable_answer() -> None:
    errors = validate_pattern_challenge(
        {"grid": [["2", "?", "8"], ["3", "?", "12"]]},
        "5, 6",
        "",
    )

    assert errors
    assert any("non verifiable" in error for error in errors)


def test_analyze_pattern_does_not_invent_answer_from_two_numeric_points() -> None:
    assert analyze_pattern([["2", "?", "8"]], 0, 1) is None

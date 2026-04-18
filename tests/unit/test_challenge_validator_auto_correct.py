"""Garde-fous auto_correct_challenge et validation PATTERN."""

from __future__ import annotations

from unittest.mock import patch

from app.services.challenges.challenge_pattern_sequence_validation import (
    validate_pattern_challenge,
)
from app.services.challenges.challenge_validator import auto_correct_challenge


def test_auto_correct_pattern_analyze_pattern_none_does_not_raise() -> None:
    """Pas d'appel .upper() sur None quand analyze_pattern echoue."""
    challenge_data = {
        "challenge_type": "PATTERN",
        "visual_data": {"grid": [["X", "O"], ["O", "?"]]},
        "correct_answer": "X",
        "solution_explanation": "Explication initiale",
    }
    with (
        patch(
            "app.services.challenges.challenge_validator.compute_pattern_answers_multi",
            return_value=None,
        ),
        patch(
            "app.services.challenges.challenge_validator.find_question_position_in_grid",
            return_value=(1, 1),
        ),
        patch(
            "app.services.challenges.challenge_validator.analyze_pattern",
            return_value=None,
        ),
    ):
        out = auto_correct_challenge(challenge_data)

    assert out["correct_answer"] == "X"
    assert out["solution_explanation"] == "Explication initiale"


def test_auto_correct_pattern_single_question_uses_single_branch() -> None:
    """Une seule '?' ne doit pas passer par la correction multi-cellules."""
    challenge_data = {
        "challenge_type": "PATTERN",
        "visual_data": {"grid": [["2", "4"], ["8", "?"]]},
        "correct_answer": "ancien",
        "solution_explanation": "Explication initiale",
    }
    with (
        patch(
            "app.services.challenges.challenge_validator.compute_pattern_answers_multi",
            return_value="WRONG_MULTI",
        ) as multi_mock,
        patch(
            "app.services.challenges.challenge_validator.find_question_position_in_grid",
            return_value=(1, 1),
        ),
        patch(
            "app.services.challenges.challenge_validator.analyze_pattern",
            return_value="16",
        ) as analyze_mock,
    ):
        out = auto_correct_challenge(challenge_data)

    multi_mock.assert_not_called()
    analyze_mock.assert_called_once_with([["2", "4"], ["8", "?"]], 1, 1)
    assert out["correct_answer"] == "16"


def test_validate_pattern_single_question_skips_multi_validation() -> None:
    """Une seule '?' doit suivre la validation simple, pas la branche multi."""
    visual_data = {"grid": [["2", "4"], ["8", "?"]]}
    with (
        patch(
            "app.services.challenges.challenge_pattern_sequence_validation.compute_pattern_answers_multi",
            return_value="WRONG_MULTI",
        ) as multi_mock,
        patch(
            "app.services.challenges.challenge_pattern_sequence_validation.find_question_position_in_grid",
            return_value=(1, 1),
        ),
        patch(
            "app.services.challenges.challenge_pattern_sequence_validation.analyze_pattern",
            return_value="16",
        ) as analyze_mock,
    ):
        errors = validate_pattern_challenge(visual_data, "16", "Explication")

    multi_mock.assert_not_called()
    analyze_mock.assert_called_once_with([["2", "4"], ["8", "?"]], 1, 1)
    assert errors == []


def test_validate_pattern_numeric_grid_accepts_row_progression() -> None:
    """Une grille numérique cohérente ne doit pas être rejetée par une heuristique miroir."""
    visual_data = {
        "grid": [
            ["2", "4", "8", "16"],
            ["3", "6", "12", "24"],
            ["5", "10", "20", "40"],
            ["7", "14", "28", "?"],
        ]
    }
    errors = validate_pattern_challenge(visual_data, "56", "Explication")
    assert errors == []

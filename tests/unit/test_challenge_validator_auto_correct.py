"""Garde-fous auto_correct_challenge (NPE si analyze_pattern retourne None)."""

from __future__ import annotations

from unittest.mock import patch

from app.services.challenges.challenge_validator import auto_correct_challenge


def test_auto_correct_pattern_analyze_pattern_none_does_not_raise() -> None:
    """B6: pas d'appel .upper() sur None quand analyze_pattern échoue."""
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

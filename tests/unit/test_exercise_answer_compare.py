"""Tests unitaires directs pour app.utils.exercise_answer_compare."""

import pytest

from app.utils.exercise_answer_compare import answers_equivalent_numeric_tolerant


@pytest.mark.parametrize(
    "selected,correct,expected",
    [
        ("45%", "45", True),
        ("45 %", "45", True),
        ("45", "45%", True),
        ("100", "100%", True),
        ("12,5%", "12.5", True),
        ("3,5", "3.5", True),
        ("3.5", "3,5", True),
        ("1/2", "0.5", True),
        ("0.5", "1/2", True),
        ("2/4", "1/2", True),
        ("1/2", "1/2", True),
        ("0100", "100", False),
        ("0.50", "0.5", False),
        ("42", "43", False),
        ("10 km", "10", False),
    ],
)
def test_answers_equivalent_numeric_tolerant(
    selected: str, correct: str, expected: bool
) -> None:
    assert answers_equivalent_numeric_tolerant(selected, correct) is expected

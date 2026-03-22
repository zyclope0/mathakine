"""
Tests unitaires pour la validation des differents formats de reponses aux exercices.

Exercent la vraie logique metier de exercise_attempt_service._check_answer_correct
via submit_answer, en mockant uniquement le repository et les dependances (badges, streak, daily).
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.models.exercise import ExerciseType
from app.services.exercises.exercise_attempt_service import (
    submit_answer as svc_submit_answer,
)


def _exercise_dict(correct_answer, exercise_type="ADDITION", explanation=""):
    """Dict simulant le retour de get_exercise_for_submit_validation."""
    return {
        "id": 1,
        "exercise_type": exercise_type,
        "difficulty": "INITIE",
        "choices": [],
        "question": "Question test",
        "explanation": explanation or "",
        "correct_answer": correct_answer,
    }


def _mock_attempt(attempt_id=1):
    """Mock Attempt pour create_attempt."""
    a = MagicMock()
    a.id = attempt_id
    a.created_at = datetime(2026, 3, 6, 12, 0, 0)
    return a


def _run_submit(exercise_type, correct_answer, selected_answer, expected_result):
    """Execute submit_answer avec mocks repo/deps, verifie is_correct."""
    ex_dict = _exercise_dict(correct_answer, exercise_type)
    mock_db = MagicMock()
    mock_db.begin_nested.side_effect = [
        MagicMock(is_active=True),
        MagicMock(is_active=True),
        MagicMock(is_active=True),
    ]
    mock_attempt = _mock_attempt()

    with (
        patch(
            "app.services.exercises.exercise_attempt_service.get_exercise_for_submit_validation",
            return_value=ex_dict,
        ),
        patch(
            "app.services.exercises.exercise_attempt_service.create_attempt",
            return_value=mock_attempt,
        ),
        patch(
            "app.services.exercises.exercise_attempt_service.update_progress_after_attempt"
        ),
        patch(
            "app.services.badges.badge_service.BadgeService",
        ) as BadgeCls,
        patch("app.services.progress.streak_service.update_user_streak"),
        patch(
            "app.services.progress.daily_challenge_service.record_exercise_completed"
        ),
    ):
        badge_inst = MagicMock()
        badge_inst.check_and_award_badges.return_value = []
        badge_inst.get_closest_progress_notification.return_value = None
        BadgeCls.return_value = badge_inst

        result = svc_submit_answer(
            mock_db,
            exercise_id=1,
            user_id=1,
            selected_answer=selected_answer,
            time_spent=10.0,
        )

    assert (
        result.is_correct == expected_result
    ), f"'{selected_answer}' vs '{correct_answer}' (type={exercise_type}): attendu {expected_result}, obtenu {result.is_correct}"
    assert result.correct_answer == correct_answer


# --- Comparaison texte / normalisation ---


@pytest.mark.parametrize(
    "exercise_type,answer,correct_answer,expected_result",
    [
        # Types numeriques : comparaison stricte APRES strip()
        (ExerciseType.ADDITION.value, "42", "42", True),
        (ExerciseType.ADDITION.value, " 42", "42", True),
        (ExerciseType.ADDITION.value, "42 ", "42", True),
        (ExerciseType.MULTIPLICATION.value, "100", "100", True),
        (ExerciseType.MULTIPLICATION.value, "0100", "100", False),
        (ExerciseType.DIVISION.value, "3.5", "3.5", True),
        (ExerciseType.DIVISION.value, "3,5", "3.5", True),
        # Types textuels : lower() + strip()
        (ExerciseType.TEXTE.value, "Paris", "Paris", True),
        (ExerciseType.TEXTE.value, "paris", "Paris", True),
        (ExerciseType.TEXTE.value, " Paris", "Paris", True),
        (ExerciseType.TEXTE.value, "Paris ", "Paris", True),
        (ExerciseType.MIXTE.value, "Force", "Force", True),
        (ExerciseType.MIXTE.value, "force", "Force", True),
        (ExerciseType.MIXTE.value, " Force ", "Force", True),
    ],
)
def test_answer_validation_formats(
    exercise_type, answer, correct_answer, expected_result, db_session
):
    """Teste la validation des reponses selon type d'exercice (vraie logique metier)."""
    _run_submit(exercise_type, correct_answer, answer, expected_result)


# --- Fractions / formats mathematiques ---


@pytest.mark.parametrize(
    "answer,correct,expected",
    [
        ("1/2", "1/2", True),
        ("1/2", "0.5", True),
        ("0.5", "1/2", True),
        ("0.5", "0.5", True),
        ("0.50", "0.5", False),
        ("0,5", "0.5", True),
    ],
)
def test_fraction_answer_validation(answer, correct, expected, db_session):
    """Fractions : équivalence fraction/décimal et virgule décimale FR."""
    _run_submit(ExerciseType.FRACTIONS.value, correct, answer, expected)


# --- Unites / formats avec suffixes ---


@pytest.mark.parametrize(
    "answer,correct,expected",
    [
        ("10", "10", True),
        ("10", "10 km", False),
        ("10 km", "10 km", True),
        ("10km", "10 km", False),
    ],
)
def test_unit_answer_validation(answer, correct, expected, db_session):
    """Teste la validation des reponses avec unites de mesure (comparaison stricte)."""
    _run_submit(ExerciseType.GEOMETRIE.value, correct, answer, expected)


# --- Handler : validation payload (reponse vide) ---


@pytest.mark.asyncio
async def test_empty_answer_validation(db_session):
    """Teste qu'une reponse vide est rejetee par SubmitAnswerRequest (422)."""
    import json
    from contextlib import asynccontextmanager
    from unittest.mock import AsyncMock, patch

    from server.handlers.exercise_handlers import submit_answer
    from tests.unit.test_utils import create_mock_request

    @asynccontextmanager
    async def _mock_db():
        yield MagicMock()

    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": "padawan",
        "is_authenticated": True,
    }

    mock_request = create_mock_request(
        json_data={"selected_answer": "", "time_spent": 5.0},
        path_params={"exercise_id": "1"},
    )
    mock_request.headers = {"Accept-Language": "fr"}

    with patch("server.auth.get_current_user", AsyncMock(return_value=mock_user)):
        response = await submit_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 422
    assert "detail" in result

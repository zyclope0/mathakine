"""
Tests unitaires pour la validation des differents formats de reponses aux exercices.

Le handler submit_answer utilise:
- @require_auth (server.auth.get_current_user)
- SQLAlchemy query chain direct pour charger l'exercice
- ExerciseService.record_attempt pour enregistrer
- Comparaison stricte pour types numeriques, insensible a la casse pour TEXTE/MIXTE
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.exercise import DifficultyLevel, ExerciseType
from app.utils.db_helpers import get_enum_value
from server.handlers.exercise_handlers import submit_answer
from tests.unit.test_utils import create_mock_request


def _mock_auth_user():
    """Mock utilisateur authentifie."""
    return {
        "id": 1,
        "username": "test_user",
        "role": "padawan",
        "is_authenticated": True,
    }


def _patch_auth(mock_user):
    """Patch le decorateur @require_auth."""
    return patch("server.auth.get_current_user", AsyncMock(return_value=mock_user))


def _mock_exercise_row(correct_answer, exercise_type="ADDITION"):
    """Mock du resultat SQLAlchemy query pour un exercice."""
    row = MagicMock()
    row.id = 1
    row.question = "Question test"
    row.correct_answer = correct_answer
    row.choices = []
    row.explanation = "Explication test"
    row.exercise_type_str = exercise_type
    row.difficulty_str = "INITIE"
    return row


def _mock_attempt(user_answer, is_correct):
    """Mock de l'objet Attempt retourne par record_attempt."""
    attempt = MagicMock()
    attempt.id = 123
    attempt.user_id = 1
    attempt.exercise_id = 1
    attempt.user_answer = user_answer
    attempt.is_correct = is_correct
    attempt.time_spent = 10.0
    attempt.created_at = None
    return attempt


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exercise_type,answer,correct_answer,expected_result",
    [
        # Types numeriques : comparaison stricte APRES strip()
        # Le handler fait: str(answer).strip() == str(correct).strip()
        (ExerciseType.ADDITION.value, "42", "42", True),
        (ExerciseType.ADDITION.value, " 42", "42", True),  # strip enleve les espaces
        (ExerciseType.ADDITION.value, "42 ", "42", True),  # strip enleve les espaces
        (ExerciseType.MULTIPLICATION.value, "100", "100", True),
        (
            ExerciseType.MULTIPLICATION.value,
            "0100",
            "100",
            False,
        ),  # strings differentes
        (ExerciseType.DIVISION.value, "3.5", "3.5", True),
        (ExerciseType.DIVISION.value, "3,5", "3.5", False),  # virgule != point
        # Types textuels : lower() + strip()
        (ExerciseType.TEXTE.value, "Paris", "Paris", True),
        (ExerciseType.TEXTE.value, "paris", "Paris", True),  # insensible casse
        (ExerciseType.TEXTE.value, " Paris", "Paris", True),  # strip
        (ExerciseType.TEXTE.value, "Paris ", "Paris", True),  # strip
        (ExerciseType.MIXTE.value, "Force", "Force", True),
        (ExerciseType.MIXTE.value, "force", "Force", True),  # insensible casse
        (ExerciseType.MIXTE.value, " Force ", "Force", True),  # strip
    ],
)
async def test_answer_validation_formats(
    exercise_type, answer, correct_answer, expected_result, db_session
):
    """Teste la validation des reponses selon type d'exercice."""
    mock_user = _mock_auth_user()
    mock_request = create_mock_request(
        json_data={"selected_answer": answer, "time_spent": 10.0},
        path_params={"exercise_id": "1"},
    )
    mock_request.headers = {"Accept-Language": "fr"}

    # Mock query chain: exercise lookup
    mock_db_ex = MagicMock()
    mock_db_ex.query.return_value.filter.return_value.first.return_value = (
        _mock_exercise_row(correct_answer, exercise_type.upper())
    )

    # Mock attempt recording
    mock_db_att = MagicMock()
    attempt_obj = _mock_attempt(answer, expected_result)

    # Mock badges
    mock_db_badges = MagicMock()

    with patch(
        "app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session",
        side_effect=[mock_db_ex, mock_db_att, mock_db_badges],
    ):
        with patch(
            "app.services.exercise_service.ExerciseService.record_attempt",
            return_value=attempt_obj,
        ):
            with _patch_auth(mock_user):
                response = await submit_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 200, f"Status {response.status_code}: {result}"
    assert (
        result["is_correct"] == expected_result
    ), f"Validation de '{answer}' pour type {exercise_type}: attendu {expected_result}, obtenu {result['is_correct']}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "answer,correct,expected",
    [
        ("1/2", "1/2", True),
        ("1/2", "0.5", False),
        ("0.5", "0.5", True),
        ("0.50", "0.5", False),
        ("0,5", "0.5", False),
    ],
)
async def test_fraction_answer_validation(answer, correct, expected, db_session):
    """Teste la validation pour les exercices de fractions."""
    mock_user = _mock_auth_user()
    mock_request = create_mock_request(
        json_data={"selected_answer": answer, "time_spent": 10.0},
        path_params={"exercise_id": "1"},
    )
    mock_request.headers = {"Accept-Language": "fr"}

    mock_db_ex = MagicMock()
    mock_db_ex.query.return_value.filter.return_value.first.return_value = (
        _mock_exercise_row(correct, "FRACTIONS")
    )

    mock_db_att = MagicMock()
    attempt_obj = _mock_attempt(answer, expected)
    mock_db_badges = MagicMock()

    with patch(
        "app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session",
        side_effect=[mock_db_ex, mock_db_att, mock_db_badges],
    ):
        with patch(
            "app.services.exercise_service.ExerciseService.record_attempt",
            return_value=attempt_obj,
        ):
            with _patch_auth(mock_user):
                response = await submit_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 200
    assert (
        result["is_correct"] == expected
    ), f"Fraction: '{answer}' vs '{correct}': attendu {expected}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "answer,correct,expected",
    [
        ("10", "10", True),
        ("10", "10 km", False),
        ("10 km", "10 km", True),
        ("10km", "10 km", False),
    ],
)
async def test_unit_answer_validation(answer, correct, expected, db_session):
    """Teste la validation des reponses avec unites de mesure."""
    mock_user = _mock_auth_user()
    mock_request = create_mock_request(
        json_data={"selected_answer": answer, "time_spent": 12.0},
        path_params={"exercise_id": "1"},
    )
    mock_request.headers = {"Accept-Language": "fr"}

    mock_db_ex = MagicMock()
    mock_db_ex.query.return_value.filter.return_value.first.return_value = (
        _mock_exercise_row(correct, "DIVERS")
    )

    mock_db_att = MagicMock()
    attempt_obj = _mock_attempt(answer, expected)
    mock_db_badges = MagicMock()

    with patch(
        "app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session",
        side_effect=[mock_db_ex, mock_db_att, mock_db_badges],
    ):
        with patch(
            "app.services.exercise_service.ExerciseService.record_attempt",
            return_value=attempt_obj,
        ):
            with _patch_auth(mock_user):
                response = await submit_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 200
    assert result["is_correct"] == expected


@pytest.mark.asyncio
async def test_empty_answer_validation(db_session):
    """Teste qu'une reponse vide est traitee comme incorrecte."""
    mock_user = _mock_auth_user()
    mock_request = create_mock_request(
        json_data={"selected_answer": "", "time_spent": 5.0},
        path_params={"exercise_id": "1"},
    )
    mock_request.headers = {"Accept-Language": "fr"}

    mock_db_ex = MagicMock()
    mock_db_ex.query.return_value.filter.return_value.first.return_value = (
        _mock_exercise_row("4", "ADDITION")
    )

    mock_db_att = MagicMock()
    attempt_obj = _mock_attempt("", False)
    mock_db_badges = MagicMock()

    with patch(
        "app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session",
        side_effect=[mock_db_ex, mock_db_att, mock_db_badges],
    ):
        with patch(
            "app.services.exercise_service.ExerciseService.record_attempt",
            return_value=attempt_obj,
        ):
            with _patch_auth(mock_user):
                response = await submit_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    # SubmitAnswerRequest : answer vide → 422 (min_length=1)
    assert response.status_code == 422
    assert "detail" in result

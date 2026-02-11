"""
Tests unitaires pour la validation des reponses aux exercices.

Le handler submit_answer utilise:
- @require_auth decorator (server.auth.get_current_user)
- SQLAlchemy query chain pour charger l'exercice
- ExerciseService.record_attempt pour enregistrer la tentative
- request.path_params['exercise_id'] pour l'ID exercice
"""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock

from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.user import UserRole
from app.utils.db_helpers import get_enum_value
from server.handlers.exercise_handlers import submit_answer
from tests.unit.test_utils import create_mock_request


def _mock_user(db_session=None, role=UserRole.PADAWAN):
    """Helper: cree un mock d'utilisateur authentifie."""
    return {
        "id": 1,
        "username": "test_user",
        "role": role.value if hasattr(role, 'value') else str(role),
        "is_authenticated": True
    }


def _patch_auth(mock_user):
    """Patch server.auth.get_current_user (appele par @require_auth)."""
    return patch('server.auth.get_current_user', AsyncMock(return_value=mock_user))


def _mock_exercise_row(exercise_id=1, correct_answer="8", exercise_type="ADDITION",
                       difficulty="INITIE", question="5 + 3 = ?",
                       explanation="Explication", choices=None):
    """Cree un mock qui simule le resultat de db.query(...).filter(...).first()."""
    row = MagicMock()
    row.id = exercise_id
    row.question = question
    row.correct_answer = correct_answer
    row.choices = choices or ["6", "7", "8", "9"]
    row.explanation = explanation
    row.exercise_type_str = exercise_type
    row.difficulty_str = difficulty
    return row


def _mock_attempt_obj(attempt_id=1, user_id=1, exercise_id=1,
                      user_answer="8", is_correct=True, time_spent=10.0):
    """Cree un mock d'objet Attempt retourne par ExerciseService.record_attempt."""
    attempt = MagicMock()
    attempt.id = attempt_id
    attempt.user_id = user_id
    attempt.exercise_id = exercise_id
    attempt.user_answer = user_answer
    attempt.is_correct = is_correct
    attempt.time_spent = time_spent
    attempt.created_at = None
    return attempt


@pytest.mark.asyncio
async def test_submit_correct_answer(db_session):
    """Teste la soumission d'une reponse correcte a un exercice."""
    mock_user = _mock_user(db_session)
    mock_request = create_mock_request(
        json_data={"selected_answer": "8", "time_spent": 15.5},
        path_params={"exercise_id": "1"}
    )
    # Mock headers pour Accept-Language
    mock_request.headers = {"Accept-Language": "fr"}

    # Mock pour le query chain SQLAlchemy (exercise lookup)
    mock_db_ex = MagicMock()
    exercise_row = _mock_exercise_row(correct_answer="8", exercise_type="ADDITION")
    mock_db_ex.query.return_value.filter.return_value.first.return_value = exercise_row

    # Mock pour le record_attempt
    mock_db_att = MagicMock()
    attempt_obj = _mock_attempt_obj(is_correct=True, user_answer="8")

    # Mock pour badges
    mock_db_badges = MagicMock()

    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session',
               side_effect=[mock_db_ex, mock_db_att, mock_db_badges]):
        with patch('app.services.exercise_service.ExerciseService.record_attempt', return_value=attempt_obj):
            with _patch_auth(mock_user):
                response = await submit_answer(mock_request)

    result = json.loads(response.body.decode('utf-8'))
    assert response.status_code == 200
    assert result["is_correct"] is True
    assert "correct_answer" in result


@pytest.mark.asyncio
async def test_submit_incorrect_answer(db_session):
    """Teste la soumission d'une reponse incorrecte a un exercice."""
    mock_user = _mock_user(db_session)
    mock_request = create_mock_request(
        json_data={"selected_answer": "36", "time_spent": 25.0},
        path_params={"exercise_id": "1"}
    )
    mock_request.headers = {"Accept-Language": "fr"}

    mock_db_ex = MagicMock()
    exercise_row = _mock_exercise_row(correct_answer="42", exercise_type="MULTIPLICATION")
    mock_db_ex.query.return_value.filter.return_value.first.return_value = exercise_row

    mock_db_att = MagicMock()
    attempt_obj = _mock_attempt_obj(is_correct=False, user_answer="36")

    mock_db_badges = MagicMock()

    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session',
               side_effect=[mock_db_ex, mock_db_att, mock_db_badges]):
        with patch('app.services.exercise_service.ExerciseService.record_attempt', return_value=attempt_obj):
            with _patch_auth(mock_user):
                response = await submit_answer(mock_request)

    result = json.loads(response.body.decode('utf-8'))
    assert response.status_code == 200
    assert result["is_correct"] is False
    assert result["correct_answer"] == "42"


@pytest.mark.asyncio
async def test_submit_answer_nonexistent_exercise(db_session):
    """Teste la soumission d'une reponse a un exercice inexistant."""
    mock_user = _mock_user(db_session)
    mock_request = create_mock_request(
        json_data={"selected_answer": "42", "time_spent": 10.0},
        path_params={"exercise_id": "999"}
    )
    mock_request.headers = {"Accept-Language": "fr"}

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session', return_value=mock_db):
        with _patch_auth(mock_user):
            response = await submit_answer(mock_request)

    result = json.loads(response.body.decode('utf-8'))
    assert response.status_code == 404
    assert "error" in result


@pytest.mark.asyncio
async def test_submit_answer_missing_answer(db_session):
    """Teste la soumission sans reponse selectionnee."""
    mock_user = _mock_user(db_session)
    mock_request = create_mock_request(
        json_data={"time_spent": 10.0},
        path_params={"exercise_id": "1"}
    )
    mock_request.headers = {"Accept-Language": "fr"}

    with _patch_auth(mock_user):
        response = await submit_answer(mock_request)

    result = json.loads(response.body.decode('utf-8'))
    assert response.status_code == 400
    assert "error" in result


@pytest.mark.asyncio
async def test_submit_answer_unauthenticated():
    """Teste la soumission d'une reponse sans authentification."""
    mock_request = create_mock_request(
        json_data={"selected_answer": "8", "time_spent": 10.0},
        path_params={"exercise_id": "1"}
    )
    mock_request.headers = {"Accept-Language": "fr"}

    mock_unauthenticated = {"is_authenticated": False}
    with _patch_auth(mock_unauthenticated):
        response = await submit_answer(mock_request)

    result = json.loads(response.body.decode('utf-8'))
    assert response.status_code == 401
    assert "error" in result


@pytest.mark.asyncio
async def test_submit_answer_internal_error(db_session):
    """Teste la gestion des erreurs internes du serveur."""
    mock_user = _mock_user(db_session)
    mock_request = create_mock_request(
        json_data={"selected_answer": "8", "time_spent": 10.0},
        path_params={"exercise_id": "1"}
    )
    mock_request.headers = {"Accept-Language": "fr"}

    def raise_error(*args, **kwargs):
        raise Exception("Erreur interne")

    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session', side_effect=raise_error):
        with _patch_auth(mock_user):
            response = await submit_answer(mock_request)

    result = json.loads(response.body.decode('utf-8'))
    assert response.status_code == 500
    assert "error" in result

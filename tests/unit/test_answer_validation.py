"""
Tests unitaires pour la validation des reponses aux exercices.

- Tests service-level : exercent la vraie logique metier de validation
  (exercise_attempt_service.submit_answer) via mocks repo/dependances uniquement.
- Tests handler : validation payload (SubmitAnswerRequest), auth, mapping erreurs.
"""

import json
from contextlib import asynccontextmanager
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import ExerciseNotFoundError
from app.models.user import UserRole
from app.services.exercises.exercise_attempt_service import (
    submit_answer as svc_submit_answer,
)
from app.utils.db_helpers import get_enum_value
from server.handlers.exercise_handlers import submit_answer
from tests.unit.test_utils import create_mock_request


def _mock_db_session():
    """Async context manager mock pour db_session (legacy)."""

    @asynccontextmanager
    async def _cm():
        yield MagicMock()

    return _cm()


def _mock_sync_db_session():
    """Sync context manager mock pour sync_db_session (LOT A4)."""

    from contextlib import contextmanager

    @contextmanager
    def _cm():
        yield MagicMock()

    return _cm()


def _mock_user(db_session=None, role=UserRole.PADAWAN):
    """Helper: cree un mock d'utilisateur authentifie."""
    return {
        "id": 1,
        "username": "test_user",
        "role": role.value if hasattr(role, "value") else str(role),
        "is_authenticated": True,
    }


def _patch_auth(mock_user):
    """Patch server.auth.get_current_user (appele par @require_auth)."""
    return patch("server.auth.get_current_user", AsyncMock(return_value=mock_user))


def _exercise_dict(correct_answer, exercise_type="ADDITION", explanation=""):
    """Dict simulant le retour de get_exercise_for_submit_validation."""
    return {
        "id": 1,
        "exercise_type": exercise_type,
        "difficulty": "INITIE",
        "choices": ["6", "7", "8", "9"],
        "question": "5 + 3 = ?",
        "explanation": explanation or "Explication",
        "correct_answer": correct_answer,
    }


def _mock_attempt(attempt_id=1, created_at=None):
    """Mock Attempt pour create_attempt."""
    a = MagicMock()
    a.id = attempt_id
    a.created_at = created_at or datetime(2026, 3, 6, 12, 0, 0)
    return a


# --- Tests service-level : vraie logique de validation ---


def test_service_submit_correct_answer(db_session):
    """Service : reponse correcte -> is_correct=True."""
    ex_dict = _exercise_dict("8", "ADDITION")
    mock_db = MagicMock()
    mock_db.begin_nested.side_effect = [
        MagicMock(is_active=True),
        MagicMock(is_active=True),
        MagicMock(is_active=True),
    ]
    mock_attempt = _mock_attempt(attempt_id=42)

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
            "app.services.exercises.exercise_attempt_service.GamificationService.apply_points",
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
            mock_db, exercise_id=1, user_id=1, selected_answer="8", time_spent=15.5
        )

    assert result.is_correct is True
    assert result.correct_answer == "8"
    assert result.attempt_id == 42


def test_service_submit_incorrect_answer(db_session):
    """Service : reponse incorrecte -> is_correct=False."""
    ex_dict = _exercise_dict("42", "ADDITION")
    mock_db = MagicMock()
    mock_db.begin_nested.side_effect = [
        MagicMock(is_active=True),
        MagicMock(is_active=True),
        MagicMock(is_active=True),
    ]
    mock_attempt = _mock_attempt(attempt_id=1)

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
            selected_answer="36",
            time_spent=25.0,
        )

    assert result.is_correct is False
    assert result.correct_answer == "42"


def test_service_submit_exercise_not_found(db_session):
    """Service : exercice inexistant -> ExerciseNotFoundError."""
    with patch(
        "app.services.exercises.exercise_attempt_service.get_exercise_for_submit_validation",
        return_value=None,
    ):
        with pytest.raises(ExerciseNotFoundError):
            svc_submit_answer(
                MagicMock(),
                exercise_id=999999,
                user_id=1,
                selected_answer="4",
            )


# --- Tests handler : validation payload, auth, mapping erreurs ---


@pytest.mark.asyncio
async def test_submit_answer_missing_answer(db_session):
    """Teste la soumission sans reponse selectionnee -> 422 (SubmitAnswerRequest)."""
    mock_user = _mock_user(db_session)
    mock_request = create_mock_request(
        json_data={"time_spent": 10.0}, path_params={"exercise_id": "1"}
    )
    mock_request.headers = {"Accept-Language": "fr"}

    with _patch_auth(mock_user):
        response = await submit_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 422
    assert "detail" in result


@pytest.mark.asyncio
async def test_submit_answer_unauthenticated():
    """Teste la soumission d'une reponse sans authentification."""
    mock_request = create_mock_request(
        json_data={"selected_answer": "8", "time_spent": 10.0},
        path_params={"exercise_id": "1"},
    )
    mock_request.headers = {"Accept-Language": "fr"}

    mock_unauthenticated = {"is_authenticated": False}
    with _patch_auth(mock_unauthenticated):
        response = await submit_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 401
    assert "error" in result


async def _run_db_bound_direct(func, *args, **kwargs):
    """Execute func(*args, **kwargs) in caller thread (pour tests LOT A4)."""
    return func(*args, **kwargs)


@pytest.mark.asyncio
async def test_submit_answer_nonexistent_exercise(db_session):
    """Handler : exercice inexistant -> 404 (mapping ExerciseNotFoundError)."""
    mock_user = _mock_user(db_session)
    mock_request = create_mock_request(
        json_data={"selected_answer": "42", "time_spent": 10.0},
        path_params={"exercise_id": "999"},
    )
    mock_request.headers = {"Accept-Language": "fr"}

    with (
        patch(
            "server.handlers.exercise_handlers.run_db_bound",
            side_effect=_run_db_bound_direct,
        ),
        patch(
            "app.utils.db_utils.sync_db_session",
            new=_mock_sync_db_session,
        ),
        patch(
            "server.handlers.exercise_handlers.submit_answer_sync",
            side_effect=ExerciseNotFoundError(),
        ),
        _patch_auth(mock_user),
    ):
        response = await submit_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 404
    assert "error" in result


@pytest.mark.asyncio
async def test_submit_answer_internal_error(db_session):
    """Handler : erreur interne du service -> 500."""
    mock_user = _mock_user(db_session)
    mock_request = create_mock_request(
        json_data={"selected_answer": "8", "time_spent": 10.0},
        path_params={"exercise_id": "1"},
    )
    mock_request.headers = {"Accept-Language": "fr"}

    with (
        patch(
            "server.handlers.exercise_handlers.run_db_bound",
            side_effect=_run_db_bound_direct,
        ),
        patch(
            "app.utils.db_utils.sync_db_session",
            new=_mock_sync_db_session,
        ),
        patch(
            "server.handlers.exercise_handlers.submit_answer_sync",
            side_effect=Exception("Erreur interne"),
        ),
        _patch_auth(mock_user),
    ):
        response = await submit_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 500
    assert "error" in result


@pytest.mark.asyncio
async def test_submit_answer_invalid_exercise_id_returns_400(db_session):
    """Handler : exercise_id non numérique -> 400 (ValueError/TypeError)."""
    mock_user = _mock_user(db_session)
    mock_request = create_mock_request(
        json_data={"selected_answer": "8", "time_spent": 10.0},
        path_params={"exercise_id": "not-a-number"},
    )
    mock_request.headers = {"Accept-Language": "fr"}

    with _patch_auth(mock_user):
        response = await submit_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 400
    assert "error" in result


@pytest.mark.asyncio
async def test_submit_answer_sqlalchemy_error_returns_500(db_session):
    """Handler : erreur DB du service -> 500 (ne pas masquer en 404)."""
    mock_user = _mock_user(db_session)
    mock_request = create_mock_request(
        json_data={"selected_answer": "8", "time_spent": 10.0},
        path_params={"exercise_id": "1"},
    )
    mock_request.headers = {"Accept-Language": "fr"}

    with (
        patch(
            "server.handlers.exercise_handlers.run_db_bound",
            side_effect=_run_db_bound_direct,
        ),
        patch(
            "app.utils.db_utils.sync_db_session",
            new=_mock_sync_db_session,
        ),
        patch(
            "server.handlers.exercise_handlers.submit_answer_sync",
            side_effect=SQLAlchemyError("connection reset"),
        ),
        _patch_auth(mock_user),
    ):
        response = await submit_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 500
    assert "error" in result


@pytest.mark.asyncio
async def test_submit_challenge_sqlalchemy_error_returns_500(db_session):
    """Handler défi : erreur DB -> 500 via capture_internal_error_response."""
    from server.handlers.challenge_handlers import submit_challenge_answer

    mock_user = {
        **_mock_user(db_session),
        "access_scope": "full",
    }
    mock_request = create_mock_request(
        json_data={
            "user_solution": "42",
            "time_spent": 1.0,
            "hints_used_count": 0,
        },
        path_params={"challenge_id": "1"},
    )

    with (
        patch("server.auth.get_current_user", AsyncMock(return_value=mock_user)),
        patch(
            "server.handlers.challenge_handlers.run_db_bound",
            side_effect=_run_db_bound_direct,
        ),
        patch(
            "server.handlers.challenge_handlers.submit_challenge_attempt",
            side_effect=SQLAlchemyError("db fail"),
        ),
    ):
        response = await submit_challenge_answer(mock_request)

    result = json.loads(response.body.decode("utf-8"))
    assert response.status_code == 500
    assert "error" in result

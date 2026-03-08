"""
Tests unitaires pour les helpers de server.handlers.exercise_handlers.
"""

from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch

import pytest

from server.handlers.exercise_handlers import _resolve_adaptive_age_group_if_needed
from tests.unit.test_utils import create_mock_request


def _make_request_with_user(user_id: int = 1):
    """Crée une requête mock avec un utilisateur authentifié."""
    req = create_mock_request()
    req.state = MagicMock()
    req.state.user = {"id": user_id, "username": "test"}
    return req


def _make_request_without_user():
    """Crée une requête mock sans utilisateur authentifié."""
    req = create_mock_request()
    req.state = MagicMock()
    req.state.user = None
    return req


# ---------------------------------------------------------------------------
# Tests _resolve_adaptive_age_group_if_needed — pas de résolution
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_adaptive_age_group_adaptive_false_returns_unchanged():
    """adaptive=False → retourne age_group_raw inchangé."""
    req = _make_request_with_user()
    result = await _resolve_adaptive_age_group_if_needed(
        req, "addition", None, adaptive=False
    )
    assert result is None


@pytest.mark.asyncio
async def test_resolve_adaptive_age_group_no_user_returns_unchanged():
    """Pas d'utilisateur authentifié → retourne age_group_raw inchangé."""
    req = _make_request_without_user()
    result = await _resolve_adaptive_age_group_if_needed(
        req, "addition", None, adaptive=True
    )
    assert result is None


@pytest.mark.asyncio
async def test_resolve_adaptive_age_group_already_provided_returns_unchanged():
    """age_group_raw déjà fourni → pas de résolution, retour inchangé."""
    req = _make_request_with_user()
    result = await _resolve_adaptive_age_group_if_needed(
        req, "addition", "GROUP_12_14", adaptive=True
    )
    assert result == "GROUP_12_14"


# ---------------------------------------------------------------------------
# Tests _resolve_adaptive_age_group_if_needed — résolution adaptative
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_adaptive_age_group_resolves_when_eligible():
    """adaptive=True, user auth, pas d'age_group → appelle resolve_adaptive_difficulty."""
    req = _make_request_with_user()

    @asynccontextmanager
    async def mock_db_cm():
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        yield mock_db

    with (
        patch(
            "server.handlers.exercise_handlers.db_session", return_value=mock_db_cm()
        ),
        patch(
            "app.services.adaptive_difficulty_service.resolve_adaptive_difficulty",
            return_value="GROUP_9_11",
        ),
        patch(
            "server.exercise_generator_validators.normalize_exercise_type",
            return_value="ADDITION",
        ),
    ):
        result = await _resolve_adaptive_age_group_if_needed(
            req, "addition", None, adaptive=True
        )

    assert result == "GROUP_9_11"


@pytest.mark.asyncio
async def test_resolve_adaptive_age_group_exercise_type_none_fallback_addition():
    """exercise_type_raw=None → fallback vers ADDITION pour normalize_exercise_type."""
    req = _make_request_with_user()

    @asynccontextmanager
    async def mock_db_cm():
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        yield mock_db

    with (
        patch(
            "server.handlers.exercise_handlers.db_session", return_value=mock_db_cm()
        ),
        patch(
            "app.services.adaptive_difficulty_service.resolve_adaptive_difficulty",
            return_value="GROUP_12_14",
        ),
        patch(
            "server.exercise_generator_validators.normalize_exercise_type",
            return_value="ADDITION",
        ) as mock_norm,
    ):
        result = await _resolve_adaptive_age_group_if_needed(
            req, None, None, adaptive=True
        )

    assert result == "GROUP_12_14"
    mock_norm.assert_called_once_with("ADDITION")


# ---------------------------------------------------------------------------
# Tests _resolve_adaptive_age_group_if_needed — exception / fallback
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_adaptive_age_group_exception_returns_original():
    """Exception lors de la résolution → retourne age_group_raw (None), log warning."""
    req = _make_request_with_user()

    @asynccontextmanager
    async def mock_db_cm():
        yield MagicMock()

    with (
        patch(
            "server.handlers.exercise_handlers.db_session", return_value=mock_db_cm()
        ),
        patch(
            "app.services.adaptive_difficulty_service.resolve_adaptive_difficulty",
            side_effect=RuntimeError("DB error"),
        ),
        patch(
            "server.handlers.exercise_handlers.logger",
        ) as mock_logger,
    ):
        result = await _resolve_adaptive_age_group_if_needed(
            req, "addition", None, adaptive=True
        )

    assert result is None
    mock_logger.warning.assert_called_once()
    assert "Résolution échouée" in mock_logger.warning.call_args[0][0]

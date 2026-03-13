"""
Tests unitaires pour les helpers de server.handlers.exercise_handlers.
Lot 1/A5 : la résolution adaptive est dans exercise_generation_service (sync).
"""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

from app.services.exercise_generation_service import (
    AgeGroupRequiredError,
    generate_exercise_sync,
)

# ---------------------------------------------------------------------------
# Tests exercise_generation_service — résolution adaptive
# ---------------------------------------------------------------------------


def test_generate_exercise_sync_adaptive_false_uses_provided_age_group():
    """adaptive=False → utilise age_group fourni, pas de résolution DB."""
    with patch(
        "app.services.exercise_generation_service.generate_simple_exercise",
        return_value={
            "title": "Test",
            "exercise_type": "ADDITION",
            "age_group": "6-8",
            "difficulty": "INITIE",
            "question": "1+1?",
            "correct_answer": "2",
            "choices": ["2", "3", "4"],
            "explanation": "Test",
        },
    ):
        result = generate_exercise_sync(
            exercise_type_raw="addition",
            age_group_raw="6-8",
            adaptive=False,
            save=False,
        )
    assert result.age_group == "6-8"


def test_generate_exercise_sync_require_age_group_raises_when_missing():
    """require_age_group=True et pas d'age_group → AgeGroupRequiredError."""
    with pytest.raises(AgeGroupRequiredError) as exc_info:
        generate_exercise_sync(
            exercise_type_raw="addition",
            age_group_raw=None,
            adaptive=False,
            save=False,
            user_id=None,
            require_age_group=True,
        )
    assert "age_group" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Tests exercise_generation_service — succès résolution adaptive
# ---------------------------------------------------------------------------


def _mock_sync_db_session_with_user():
    """Context manager mock pour sync_db_session (user présent)."""

    @contextmanager
    def _cm():
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        yield mock_db

    return _cm()


def test_generate_exercise_sync_adaptive_success_resolves_age_group():
    """adaptive=True, user auth, pas d'age_group → appelle resolve_adaptive_difficulty, utilise résultat."""
    mock_exercise = {
        "title": "Test",
        "exercise_type": "ADDITION",
        "age_group": "9-11",
        "difficulty": "PADAWAN",
        "question": "2+2?",
        "correct_answer": "4",
        "choices": ["4", "5", "6"],
        "explanation": "Test",
    }

    with (
        patch(
            "app.services.exercise_generation_service.sync_db_session",
            new=_mock_sync_db_session_with_user,
        ),
        patch(
            "app.services.exercise_generation_service.resolve_adaptive_difficulty",
            return_value="9-11",
        ),
        patch(
            "app.services.exercise_generation_service.generate_simple_exercise",
            return_value=mock_exercise,
        ),
    ):
        result = generate_exercise_sync(
            exercise_type_raw="addition",
            age_group_raw=None,
            adaptive=True,
            save=False,
            user_id=1,
        )

    assert result.age_group == "9-11"
    assert result.exercise_type == "ADDITION"


# ---------------------------------------------------------------------------
# Tests exercise_generation_service — fallback sur erreur adaptive
# ---------------------------------------------------------------------------


def test_generate_exercise_sync_adaptive_exception_fallback_to_raw():
    """Exception lors de resolve_adaptive_difficulty → fallback age_group_raw (None → default via normalize)."""
    mock_exercise = {
        "title": "Test",
        "exercise_type": "ADDITION",
        "age_group": "6-8",
        "difficulty": "INITIE",
        "question": "1+1?",
        "correct_answer": "2",
        "choices": ["2", "3", "4"],
        "explanation": "Test",
    }

    with (
        patch(
            "app.services.exercise_generation_service.sync_db_session",
            new=_mock_sync_db_session_with_user,
        ),
        patch(
            "app.services.exercise_generation_service.resolve_adaptive_difficulty",
            side_effect=RuntimeError("DB error"),
        ),
        patch(
            "app.services.exercise_generation_service.generate_simple_exercise",
            return_value=mock_exercise,
        ),
    ):
        result = generate_exercise_sync(
            exercise_type_raw="addition",
            age_group_raw=None,
            adaptive=True,
            save=False,
            user_id=1,
        )

    # Fallback: pas de crash, on obtient un exercice (age_group du mock ou default normalize)
    assert result.age_group is not None
    assert result.question == "1+1?"


def test_generate_exercise_sync_exercise_type_raw_none_fallback_to_addition():
    """exercise_type_raw=None → normalisation vers ADDITION par défaut."""
    mock_exercise = {
        "title": "Test",
        "exercise_type": "ADDITION",
        "age_group": "6-8",
        "difficulty": "INITIE",
        "question": "1+1?",
        "correct_answer": "2",
        "choices": ["2", "3", "4"],
        "explanation": "Test",
    }

    with patch(
        "app.services.exercise_generation_service.generate_simple_exercise",
        return_value=mock_exercise,
    ):
        result = generate_exercise_sync(
            exercise_type_raw=None,
            age_group_raw="6-8",
            adaptive=False,
            save=False,
        )

    assert result.exercise_type == "ADDITION"

"""
Tests unitaires pour les helpers de server.handlers.exercise_handlers.
Lot 1 : la résolution adaptive a été déplacée dans exercise_generation_service.
"""

from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch

import pytest

from app.services.exercise_generation_service import (
    AgeGroupRequiredError,
    generate_exercise as svc_generate_exercise,
)

# ---------------------------------------------------------------------------
# Tests exercise_generation_service — résolution adaptive
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_exercise_adaptive_false_uses_provided_age_group():
    """adaptive=False → utilise age_group fourni, pas de résolution DB."""
    with (
        patch(
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
        ),
        patch(
            "app.services.exercise_generation_service.db_session",
        ) as mock_db,
    ):
        mock_db.return_value.__aenter__ = MagicMock(return_value=MagicMock())
        mock_db.return_value.__aexit__ = MagicMock(return_value=None)
        result = await svc_generate_exercise(
            exercise_type_raw="addition",
            age_group_raw="6-8",
            adaptive=False,
            save=False,
        )
    assert result.age_group == "6-8"


@pytest.mark.asyncio
async def test_generate_exercise_require_age_group_raises_when_missing():
    """require_age_group=True et pas d'age_group → AgeGroupRequiredError."""
    with pytest.raises(AgeGroupRequiredError) as exc_info:
        await svc_generate_exercise(
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


@pytest.mark.asyncio
async def test_generate_exercise_adaptive_success_resolves_age_group():
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

    @asynccontextmanager
    async def mock_db_cm():
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        yield mock_db

    with (
        patch(
            "app.services.exercise_generation_service.db_session",
            return_value=mock_db_cm(),
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
        result = await svc_generate_exercise(
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


@pytest.mark.asyncio
async def test_generate_exercise_adaptive_exception_fallback_to_raw():
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

    @asynccontextmanager
    async def mock_db_cm():
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        yield mock_db

    with (
        patch(
            "app.services.exercise_generation_service.db_session",
            return_value=mock_db_cm(),
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
        result = await svc_generate_exercise(
            exercise_type_raw="addition",
            age_group_raw=None,
            adaptive=True,
            save=False,
            user_id=1,
        )

    # Fallback: pas de crash, on obtient un exercice (age_group du mock ou default normalize)
    assert result.age_group is not None
    assert result.question == "1+1?"


@pytest.mark.asyncio
async def test_generate_exercise_exercise_type_raw_none_fallback_to_addition():
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
        result = await svc_generate_exercise(
            exercise_type_raw=None,
            age_group_raw="6-8",
            adaptive=False,
            save=False,
        )

    assert result.exercise_type == "ADDITION"

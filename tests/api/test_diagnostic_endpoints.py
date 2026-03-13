"""Tests des endpoints API pour le diagnostic adaptatif (F03)."""

import pytest

from app.db.base import Base, engine
from app.models.diagnostic_result import DiagnosticResult


@pytest.fixture(autouse=True)
def ensure_diagnostic_results_table(db_session):
    """Garantit que la table diagnostic_results existe."""
    Base.metadata.create_all(bind=engine, tables=[DiagnosticResult.__table__])
    yield


def _minimal_complete_session():
    """Session minimale valide pour /complete (au moins un type avec total > 0)."""
    from app.core.constants import ExerciseTypes

    return {
        "triggered_from": "onboarding",
        "questions_asked": 1,
        "started_at": "2026-03-06T12:00:00+00:00",
        "types": {
            ExerciseTypes.ADDITION: {
                "level_ordinal": 1,
                "correct": 1,
                "total": 1,
                "consecutive_errors": 0,
                "done": False,
                "last_error_level": None,
            },
            ExerciseTypes.SOUSTRACTION: {
                "level_ordinal": 1,
                "correct": 0,
                "total": 0,
                "consecutive_errors": 0,
                "done": False,
                "last_error_level": None,
            },
            ExerciseTypes.MULTIPLICATION: {
                "level_ordinal": 1,
                "correct": 0,
                "total": 0,
                "consecutive_errors": 0,
                "done": False,
                "last_error_level": None,
            },
            ExerciseTypes.DIVISION: {
                "level_ordinal": 1,
                "correct": 0,
                "total": 0,
                "consecutive_errors": 0,
                "done": False,
                "last_error_level": None,
            },
        },
        "type_rotation_index": 0,
    }


async def test_get_diagnostic_status_unauthorized(client):
    """GET /api/diagnostic/status sans auth doit retourner 401."""
    response = await client.get("/api/diagnostic/status")
    assert response.status_code == 401


async def test_get_diagnostic_status_empty(padawan_client):
    """GET /api/diagnostic/status sans diagnostic complete retourne has_completed=false."""
    client = padawan_client["client"]
    response = await client.get("/api/diagnostic/status")
    assert response.status_code == 200
    data = response.json()
    assert data.get("has_completed") is False
    assert data.get("latest") is None


async def test_diagnostic_complete_then_status(padawan_client):
    """POST /api/diagnostic/complete puis GET /api/diagnostic/status verifie le wiring."""
    client = padawan_client["client"]
    session = _minimal_complete_session()

    complete_resp = await client.post(
        "/api/diagnostic/complete",
        json={"session": session, "duration_seconds": 42},
    )
    assert complete_resp.status_code == 201
    complete_data = complete_resp.json()
    assert complete_data.get("success") is True
    result = complete_data.get("result")
    assert result is not None
    assert "id" in result
    assert "completed_at" in result
    assert "scores" in result
    assert "addition" in result["scores"]

    status_resp = await client.get("/api/diagnostic/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data.get("has_completed") is True
    assert status_data.get("latest") is not None
    assert status_data["latest"]["id"] == result["id"]

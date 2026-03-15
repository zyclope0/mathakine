"""Tests des endpoints API pour le diagnostic adaptatif (F03)."""

from unittest.mock import patch

import pytest
from jose import jwt

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


async def test_diagnostic_question_rejects_invalid_state_token(padawan_client):
    """POST /api/diagnostic/question rejette un state_token invalide."""
    client = padawan_client["client"]
    resp = await client.post(
        "/api/diagnostic/question",
        json={"state_token": "invalid_token"},
    )
    assert resp.status_code == 401
    assert (
        "invalide" in resp.json().get("error", "").lower()
        or "expire" in resp.json().get("error", "").lower()
    )


async def test_diagnostic_complete_rejects_invalid_state_token(padawan_client):
    """POST /api/diagnostic/complete rejette un state_token invalide."""
    client = padawan_client["client"]
    resp = await client.post(
        "/api/diagnostic/complete",
        json={"state_token": "invalid_token", "duration_seconds": 42},
    )
    assert resp.status_code == 401


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
    import app.services.diagnostic_service as diagnostic_svc

    client = padawan_client["client"]
    session = _minimal_complete_session()
    state = {"session": session, "pending": None}
    state_token = diagnostic_svc.sign_state_token(state)

    complete_resp = await client.post(
        "/api/diagnostic/complete",
        json={"state_token": state_token, "duration_seconds": 42},
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


async def test_diagnostic_question_does_not_expose_correct_answer(padawan_client):
    """POST /api/diagnostic/question n'expose pas correct_answer dans la reponse publique."""
    client = padawan_client["client"]

    start_resp = await client.post(
        "/api/diagnostic/start", json={"triggered_from": "onboarding"}
    )
    assert start_resp.status_code == 200
    state_token = start_resp.json().get("state_token")
    assert state_token is not None

    with patch(
        "app.generators.exercise_generator.generate_ai_exercise",
        return_value={
            "question": "Combien font 2+2?",
            "choices": [],
            "correct_answer": "4",
            "explanation": "",
            "hint": "",
        },
    ):
        q_resp = await client.post(
            "/api/diagnostic/question", json={"state_token": state_token}
        )
    assert q_resp.status_code == 200
    q_data = q_resp.json()
    assert q_data.get("done") is False
    question = q_data.get("question")
    assert question is not None
    assert "correct_answer" not in question
    claims = jwt.get_unverified_claims(q_data["state_token"])
    assert claims["state"].get("pending_ref")
    assert "pending" not in claims["state"]


async def test_diagnostic_full_flow_with_state_token(padawan_client):
    """Flux complet start -> question -> answer -> complete avec state_token."""
    client = padawan_client["client"]
    known_answer = "42"

    start_resp = await client.post(
        "/api/diagnostic/start", json={"triggered_from": "onboarding"}
    )
    assert start_resp.status_code == 200
    state_token = start_resp.json().get("state_token")
    assert state_token is not None

    with patch(
        "app.generators.exercise_generator.generate_ai_exercise",
        return_value={
            "question": "Quelle est la reponse?",
            "choices": [],
            "correct_answer": known_answer,
            "explanation": "",
            "hint": "",
        },
    ):
        q_resp = await client.post(
            "/api/diagnostic/question", json={"state_token": state_token}
        )
    assert q_resp.status_code == 200
    q_data = q_resp.json()
    if q_data.get("done"):
        pytest.skip("Session terminee sans question (generateur peut echouer)")
    next_token = q_data.get("state_token")
    assert next_token is not None
    assert "correct_answer" not in q_data.get("question", {})

    answer_resp = await client.post(
        "/api/diagnostic/answer",
        json={"state_token": next_token, "user_answer": known_answer},
    )
    assert answer_resp.status_code == 200
    answer_data = answer_resp.json()
    assert answer_data.get("is_correct") is True
    complete_token = answer_data.get("state_token")
    assert complete_token is not None

    complete_resp = await client.post(
        "/api/diagnostic/complete",
        json={"state_token": complete_token, "duration_seconds": 10},
    )
    assert complete_resp.status_code == 201
    assert complete_resp.json().get("success") is True


async def test_diagnostic_answer_ignores_client_correct_answer(padawan_client):
    """Le backend utilise le correct_answer du token, pas celui du client."""
    import app.services.diagnostic_service as diagnostic_svc

    client = padawan_client["client"]
    session = _minimal_complete_session()
    session["questions_asked"] = 0
    for t in session["types"]:
        session["types"][t]["done"] = False
        session["types"][t]["total"] = 0
    pending_ref = diagnostic_svc.store_pending_state(
        {"exercise_type": "ADDITION", "correct_answer": "42"}
    )
    state = {"session": session, "pending_ref": pending_ref}
    state_token = diagnostic_svc.sign_state_token(state)

    answer_resp = await client.post(
        "/api/diagnostic/answer",
        json={
            "state_token": state_token,
            "user_answer": "42",
            "correct_answer": "999",
        },
    )
    assert answer_resp.status_code == 200
    data = answer_resp.json()
    assert data["is_correct"] is True

"""Tests des endpoints API pour les retours utilisateur (feedback)."""

import pytest


@pytest.fixture(autouse=True)
def ensure_feedback_reports_table(db_session):
    """Garantit que la table feedback_reports existe (migration ou create_tables)."""
    from app.db.base import Base, engine
    from app.models.feedback_report import FeedbackReport

    Base.metadata.create_all(bind=engine, tables=[FeedbackReport.__table__])
    yield


async def test_submit_feedback(padawan_client):
    """Soumettre un retour en étant authentifié."""
    client = padawan_client["client"]
    payload = {
        "feedback_type": "exercise",
        "description": "La question 3 était incorrecte.",
        "page_url": "http://test/exercises/42",
        "exercise_id": 42,
    }

    response = await client.post("/api/feedback", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data.get("success") is True
    assert "id" in data
    assert "message" in data


async def test_submit_feedback_invalid_type(padawan_client):
    """feedback_type invalide doit retourner 400."""
    client = padawan_client["client"]
    payload = {
        "feedback_type": "invalid_type",
        "description": "Test",
    }

    response = await client.post("/api/feedback", json=payload)

    assert response.status_code == 400
    assert "error" in response.json()


async def test_submit_feedback_unauthorized(client):
    """Soumission sans authentification doit retourner 401."""
    payload = {
        "feedback_type": "ui",
        "description": "Bug graphique",
    }

    response = await client.post("/api/feedback", json=payload)

    assert response.status_code == 401


async def test_admin_list_feedback(archiviste_client, padawan_client):
    """Admin peut lister les retours après en avoir créé un."""
    # Soumettre un retour avec padawan
    padawan = padawan_client["client"]
    await padawan.post(
        "/api/feedback",
        json={
            "feedback_type": "challenge",
            "description": "Défi incohérent",
            "challenge_id": 1,
        },
    )

    # Admin liste les retours
    admin = archiviste_client["client"]
    response = await admin.get("/api/admin/feedback")

    assert response.status_code == 200
    data = response.json()
    assert "feedback" in data
    assert isinstance(data["feedback"], list)
    # Au moins le retour soumis
    if len(data["feedback"]) > 0:
        first = data["feedback"][0]
        assert "feedback_type" in first
        assert "created_at" in first
        assert first["feedback_type"] == "challenge"


async def test_admin_feedback_forbidden_as_padawan(padawan_client):
    """Un padawan ne peut pas accéder à l'API admin feedback."""
    client = padawan_client["client"]

    response = await client.get("/api/admin/feedback")

    assert response.status_code == 403


async def test_feedback_context_fields_persisted_for_admin(
    padawan_client, archiviste_client
):
    """POST avec contexte optionnel : champs persistés ; user_role issu du serveur (canonique)."""
    padawan = padawan_client["client"]
    marker = "A1 feedback context fields marker"
    await padawan.post(
        "/api/feedback",
        json={
            "feedback_type": "ui",
            "description": marker,
            "page_url": "http://test/ui",
            "active_theme": " aurora ",
            "ni_state": "ON",
            "component_id": " ExerciseCard ",
        },
    )

    admin = archiviste_client["client"]
    response = await admin.get("/api/admin/feedback")
    assert response.status_code == 200
    items = response.json()["feedback"]
    match = next((x for x in items if x.get("description") == marker), None)
    assert match is not None
    assert match["user_role"] == "apprenant"
    assert match["active_theme"] == "aurora"
    assert match["ni_state"] == "on"
    assert match["component_id"] == "ExerciseCard"


async def test_feedback_invalid_ni_state_stored_as_none(
    padawan_client, archiviste_client
):
    """ni_state hors on/off est normalisé en None côté serveur."""
    padawan = padawan_client["client"]
    marker = "A1 ni_state invalid marker"
    await padawan.post(
        "/api/feedback",
        json={
            "feedback_type": "other",
            "description": marker,
            "ni_state": "maybe",
        },
    )

    admin = archiviste_client["client"]
    response = await admin.get("/api/admin/feedback")
    assert response.status_code == 200
    items = response.json()["feedback"]
    match = next((x for x in items if x.get("description") == marker), None)
    assert match is not None
    assert match["ni_state"] is None

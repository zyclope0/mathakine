"""Tests des endpoints API pour les retours utilisateur (feedback)."""

import pytest


@pytest.fixture(autouse=True)
def ensure_feedback_reports_table(db_session):
    """Garantit que la table feedback_reports existe (migration ou create_tables)."""
    from app.db.base import Base, engine
    from app.models.feedback_report import FeedbackReport

    Base.metadata.create_all(bind=engine, tables=[FeedbackReport.__table__])
    yield


async def test_submit_feedback(apprenant_client):
    """Soumettre un retour en étant authentifié."""
    client = apprenant_client["client"]
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


async def test_submit_feedback_invalid_type(apprenant_client):
    """feedback_type invalide doit retourner 400."""
    client = apprenant_client["client"]
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


async def test_admin_list_feedback(admin_client, apprenant_client):
    """Admin peut lister les retours après en avoir créé un."""
    # Soumettre un retour avec un compte apprenant
    learner = apprenant_client["client"]
    await learner.post(
        "/api/feedback",
        json={
            "feedback_type": "challenge",
            "description": "Défi incohérent",
            "challenge_id": 1,
        },
    )

    # Admin liste les retours
    admin = admin_client["client"]
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


async def test_admin_feedback_forbidden_as_apprenant(apprenant_client):
    """Un apprenant ne peut pas accéder à l'API admin feedback."""
    client = apprenant_client["client"]

    response = await client.get("/api/admin/feedback")

    assert response.status_code == 403


async def test_feedback_context_fields_persisted_for_admin(
    apprenant_client, admin_client
):
    """POST avec contexte optionnel : champs persistés ; user_role issu du serveur (canonique)."""
    learner = apprenant_client["client"]
    marker = "A1 feedback context fields marker"
    await learner.post(
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

    admin = admin_client["client"]
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
    apprenant_client, admin_client
):
    """ni_state hors on/off est normalisé en None côté serveur."""
    learner = apprenant_client["client"]
    marker = "A1 ni_state invalid marker"
    await learner.post(
        "/api/feedback",
        json={
            "feedback_type": "other",
            "description": marker,
            "ni_state": "maybe",
        },
    )

    admin = admin_client["client"]
    response = await admin.get("/api/admin/feedback")
    assert response.status_code == 200
    items = response.json()["feedback"]
    match = next((x for x in items if x.get("description") == marker), None)
    assert match is not None
    assert match["ni_state"] is None


async def test_admin_patch_feedback_status_read(apprenant_client, admin_client):
    """Admin peut passer un retour au statut read."""
    learner = apprenant_client["client"]
    r = await learner.post(
        "/api/feedback",
        json={"feedback_type": "other", "description": "A3c patch read"},
    )
    assert r.status_code == 201
    fid = r.json()["id"]

    admin = admin_client["client"]
    resp = await admin.patch(f"/api/admin/feedback/{fid}", json={"status": "read"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == fid
    assert data["status"] == "read"


async def test_admin_patch_feedback_status_resolved(apprenant_client, admin_client):
    """Admin peut passer un retour au statut resolved."""
    learner = apprenant_client["client"]
    r = await learner.post(
        "/api/feedback",
        json={"feedback_type": "other", "description": "A3c patch resolved"},
    )
    assert r.status_code == 201
    fid = r.json()["id"]

    admin = admin_client["client"]
    resp = await admin.patch(f"/api/admin/feedback/{fid}", json={"status": "resolved"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == fid
    assert data["status"] == "resolved"


async def test_admin_patch_feedback_status_back_to_new(apprenant_client, admin_client):
    """Admin peut repasser un retour au statut new."""
    learner = apprenant_client["client"]
    r = await learner.post(
        "/api/feedback",
        json={"feedback_type": "other", "description": "A3c patch new"},
    )
    assert r.status_code == 201
    fid = r.json()["id"]

    admin = admin_client["client"]
    r1 = await admin.patch(f"/api/admin/feedback/{fid}", json={"status": "read"})
    assert r1.status_code == 200
    r2 = await admin.patch(f"/api/admin/feedback/{fid}", json={"status": "new"})
    assert r2.status_code == 200
    assert r2.json() == {"id": fid, "status": "new"}


async def test_admin_patch_feedback_invalid_status(admin_client, apprenant_client):
    """Statut inconnu -> 400."""
    learner = apprenant_client["client"]
    r = await learner.post(
        "/api/feedback",
        json={"feedback_type": "other", "description": "A3c patch invalid"},
    )
    assert r.status_code == 201
    fid = r.json()["id"]

    admin = admin_client["client"]
    resp = await admin.patch(f"/api/admin/feedback/{fid}", json={"status": "not_a_status"})
    assert resp.status_code == 400


async def test_admin_patch_feedback_forbidden_apprenant(apprenant_client):
    """Patch admin feedback interdit pour un apprenant -> 403."""
    learner = apprenant_client["client"]
    r = await learner.post(
        "/api/feedback",
        json={"feedback_type": "other", "description": "A3c patch 403"},
    )
    assert r.status_code == 201
    fid = r.json()["id"]

    resp = await learner.patch(f"/api/admin/feedback/{fid}", json={"status": "read"})
    assert resp.status_code == 403


async def test_admin_delete_feedback(apprenant_client, admin_client):
    """Admin peut supprimer un retour."""
    learner = apprenant_client["client"]
    r = await learner.post(
        "/api/feedback",
        json={"feedback_type": "other", "description": "A3d delete ok"},
    )
    assert r.status_code == 201
    fid = r.json()["id"]

    admin = admin_client["client"]
    resp = await admin.delete(f"/api/admin/feedback/{fid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True
    assert data.get("id") == fid

    list_resp = await admin.get("/api/admin/feedback")
    assert list_resp.status_code == 200
    ids = [item["id"] for item in list_resp.json()["feedback"]]
    assert fid not in ids


async def test_admin_delete_feedback_not_found(admin_client):
    """Suppression d'un retour inexistant -> 404."""
    admin = admin_client["client"]
    resp = await admin.delete("/api/admin/feedback/999999999")
    assert resp.status_code == 404


async def test_admin_delete_feedback_forbidden_apprenant(apprenant_client):
    """DELETE admin feedback interdit pour un apprenant -> 403."""
    learner = apprenant_client["client"]
    r = await learner.post(
        "/api/feedback",
        json={"feedback_type": "other", "description": "A3d delete 403"},
    )
    assert r.status_code == 201
    fid = r.json()["id"]

    resp = await learner.delete(f"/api/admin/feedback/{fid}")
    assert resp.status_code == 403

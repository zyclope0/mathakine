"""
Tests des endpoints API admin content (LOT 6).
Exercises, challenges, export — preuve minimale pour les mutations.
"""

import pytest


@pytest.mark.asyncio
async def test_admin_exercises_post_nominal(archiviste_client):
    """POST /api/admin/exercises — création d'un exercice."""
    client = archiviste_client["client"]
    payload = {
        "title": "Exercice admin LOT6",
        "question": "Combien font 3+2?",
        "correct_answer": "5",
        "exercise_type": "addition",
        "difficulty": "initie",
        "age_group": "6-8",
    }
    response = await client.post("/api/admin/exercises", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data.get("title") == payload["title"]
    assert data.get("question") == payload["question"]
    assert data.get("correct_answer") == payload["correct_answer"]
    assert "id" in data


@pytest.mark.asyncio
async def test_admin_exercises_duplicate_nominal(archiviste_client):
    """POST /api/admin/exercises/{exercise_id}/duplicate — crée une copie."""
    client = archiviste_client["client"]
    # Créer un exercice source
    create_payload = {
        "title": "Exercice à dupliquer LOT6.1",
        "question": "Combien font 3+2?",
        "correct_answer": "5",
        "exercise_type": "addition",
        "difficulty": "initie",
        "age_group": "6-8",
    }
    create_resp = await client.post("/api/admin/exercises", json=create_payload)
    assert create_resp.status_code == 201
    exercise_id = create_resp.json()["id"]

    # Dupliquer
    dup_resp = await client.post(f"/api/admin/exercises/{exercise_id}/duplicate")
    assert dup_resp.status_code == 201
    data = dup_resp.json()
    assert data.get("id") != exercise_id
    assert "(copie)" in (data.get("title") or "")
    assert data.get("question") == create_payload["question"]
    assert data.get("correct_answer") == create_payload["correct_answer"]


@pytest.mark.asyncio
async def test_admin_exercises_put_nominal(archiviste_client):
    """PUT /api/admin/exercises/{exercise_id} — mise à jour complète."""
    client = archiviste_client["client"]
    # Créer un exercice
    create_payload = {
        "title": "Exercice à modifier LOT6.1",
        "question": "Question initiale",
        "correct_answer": "42",
        "exercise_type": "addition",
        "difficulty": "initie",
        "age_group": "6-8",
    }
    create_resp = await client.post("/api/admin/exercises", json=create_payload)
    assert create_resp.status_code == 201
    exercise_id = create_resp.json()["id"]

    # Mettre à jour
    put_payload = {"title": "Titre modifié", "question": "Question modifiée"}
    put_resp = await client.put(f"/api/admin/exercises/{exercise_id}", json=put_payload)
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data.get("id") == exercise_id
    assert data.get("title") == put_payload["title"]
    assert data.get("question") == put_payload["question"]


@pytest.mark.asyncio
async def test_admin_exercises_patch_nominal(archiviste_client):
    """PATCH /api/admin/exercises/{exercise_id} — toggle is_archived."""
    client = archiviste_client["client"]
    # Créer un exercice
    create_payload = {
        "title": "Exercice à archiver LOT6.1",
        "question": "Combien font 1+1?",
        "correct_answer": "2",
        "exercise_type": "addition",
        "difficulty": "initie",
        "age_group": "6-8",
    }
    create_resp = await client.post("/api/admin/exercises", json=create_payload)
    assert create_resp.status_code == 201
    exercise_id = create_resp.json()["id"]

    # Archiver
    patch_resp = await client.patch(
        f"/api/admin/exercises/{exercise_id}", json={"is_archived": True}
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data.get("id") == exercise_id
    assert data.get("is_archived") is True


@pytest.mark.asyncio
async def test_admin_challenges_post_nominal(archiviste_client):
    """POST /api/admin/challenges — création d'un défi."""
    client = archiviste_client["client"]
    payload = {
        "title": "Défi admin LOT6",
        "description": "Description du défi de test admin.",
    }
    response = await client.post("/api/admin/challenges", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data.get("title") == payload["title"]
    assert data.get("description") == payload["description"]
    assert "id" in data


@pytest.mark.asyncio
async def test_admin_challenges_duplicate_nominal(archiviste_client):
    """POST /api/admin/challenges/{challenge_id}/duplicate — crée une copie."""
    client = archiviste_client["client"]
    create_payload = {
        "title": "Défi à dupliquer LOT6.2",
        "description": "Description du défi à dupliquer.",
    }
    create_resp = await client.post("/api/admin/challenges", json=create_payload)
    assert create_resp.status_code == 201
    challenge_id = create_resp.json()["id"]

    dup_resp = await client.post(f"/api/admin/challenges/{challenge_id}/duplicate")
    assert dup_resp.status_code == 201
    data = dup_resp.json()
    assert data.get("id") != challenge_id
    assert "(copie)" in (data.get("title") or "")
    assert data.get("description") == create_payload["description"]


@pytest.mark.asyncio
async def test_admin_challenges_put_nominal(archiviste_client):
    """PUT /api/admin/challenges/{challenge_id} — mise à jour complète."""
    client = archiviste_client["client"]
    create_payload = {
        "title": "Défi à modifier LOT6.2",
        "description": "Description initiale.",
    }
    create_resp = await client.post("/api/admin/challenges", json=create_payload)
    assert create_resp.status_code == 201
    challenge_id = create_resp.json()["id"]

    put_payload = {
        "title": "Titre modifié LOT6.2",
        "description": "Description modifiée.",
    }
    put_resp = await client.put(
        f"/api/admin/challenges/{challenge_id}", json=put_payload
    )
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data.get("id") == challenge_id
    assert data.get("title") == put_payload["title"]
    assert data.get("description") == put_payload["description"]


@pytest.mark.asyncio
async def test_admin_challenges_patch_nominal(archiviste_client):
    """PATCH /api/admin/challenges/{challenge_id} — toggle is_archived."""
    client = archiviste_client["client"]
    create_payload = {
        "title": "Défi à archiver LOT6.2",
        "description": "Description pour archivage.",
    }
    create_resp = await client.post("/api/admin/challenges", json=create_payload)
    assert create_resp.status_code == 201
    challenge_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/admin/challenges/{challenge_id}",
        json={"is_archived": True},
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data.get("id") == challenge_id
    assert data.get("is_archived") is True


@pytest.mark.asyncio
async def test_admin_export_overview(archiviste_client):
    """GET /api/admin/export?type=overview — export CSV overview."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/export?type=overview&period=all")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    content = response.text
    assert "metric" in content or "value" in content or "total" in content.lower()

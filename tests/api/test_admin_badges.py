"""
Tests des endpoints API admin badges (Lot B-3).
Soft delete, validation requirements, réactivation.
"""

import uuid

import pytest


def _unique_code():
    return f"test_b3_{uuid.uuid4().hex[:12]}"


@pytest.mark.asyncio
async def test_admin_badges_list(archiviste_client):
    """GET /api/admin/badges — liste tous les badges."""
    client = archiviste_client["client"]
    response = await client.get("/api/admin/badges")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_admin_badges_create_valid(archiviste_client, db_session):
    """POST /api/admin/badges — création avec schéma attempts_count valide."""
    client = archiviste_client["client"]
    payload = {
        "code": _unique_code(),
        "name": "Badge test B-3",
        "description": "Test validation",
        "category": "progression",
        "difficulty": "bronze",
        "points_reward": 5,
        "requirements": {"attempts_count": 10},
    }
    response = await client.post("/api/admin/badges", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data.get("code") == payload["code"]
    assert data.get("name") == payload["name"]
    assert data.get("requirements") == payload["requirements"]


@pytest.mark.asyncio
async def test_admin_badges_create_invalid_requirements(archiviste_client):
    """POST /api/admin/badges — rejet si requirements invalide."""
    client = archiviste_client["client"]
    payload = {
        "code": _unique_code(),
        "name": "Badge invalide",
        "requirements": {"attempts_count": 0},
    }
    response = await client.post("/api/admin/badges", json=payload)
    assert response.status_code == 400
    assert "attempts_count" in response.json().get("error", "").lower() or ""


@pytest.mark.asyncio
async def test_admin_badges_create_missing_requirements(archiviste_client):
    """POST /api/admin/badges — rejet si requirements manquant."""
    client = archiviste_client["client"]
    payload = {
        "code": _unique_code(),
        "name": "Sans requirements",
    }
    response = await client.post("/api/admin/badges", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_admin_badges_soft_delete_and_reactivate(archiviste_client, db_session):
    """DELETE soft delete puis PUT is_active réactivation."""
    client = archiviste_client["client"]
    # Créer un badge
    create_payload = {
        "code": _unique_code(),
        "name": "À désactiver puis réactiver",
        "requirements": {"attempts_count": 1},
    }
    create_resp = await client.post("/api/admin/badges", json=create_payload)
    assert create_resp.status_code == 201
    badge_id = create_resp.json()["id"]

    # Soft delete
    del_resp = await client.delete(f"/api/admin/badges/{badge_id}")
    assert del_resp.status_code == 200
    assert del_resp.json().get("is_active") is False

    # Vérifier qu'il est inactif
    get_resp = await client.get(f"/api/admin/badges/{badge_id}")
    assert get_resp.status_code == 200
    assert get_resp.json().get("is_active") is False

    # Réactiver via PUT
    put_resp = await client.put(
        f"/api/admin/badges/{badge_id}", json={"is_active": True}
    )
    assert put_resp.status_code == 200
    assert put_resp.json().get("is_active") is True

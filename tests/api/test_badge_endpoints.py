"""
Tests des endpoints API badges utilisateur/public (LOT 7).
Preuve minimale pour chaque endpoint badge hors admin.
"""

import pytest


@pytest.mark.asyncio
async def test_get_badges_user_200(padawan_client):
    """GET /api/badges/user — 200 avec structure attendue."""
    client = padawan_client["client"]
    response = await client.get("/api/badges/user")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "data" in data
    assert "earned_badges" in data["data"]
    assert "user_stats" in data["data"]


@pytest.mark.asyncio
async def test_get_badges_available_200(client):
    """GET /api/badges/available — public, 200."""
    response = await client.get("/api/badges/available")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert isinstance(data.get("data"), list)


@pytest.mark.asyncio
async def test_post_badges_check_200(padawan_client):
    """POST /api/badges/check — 200 avec enveloppe attendue."""
    client = padawan_client["client"]
    response = await client.post("/api/badges/check")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "new_badges" in data
    assert "badges_earned" in data
    assert "message" in data


@pytest.mark.asyncio
async def test_get_badges_stats_200(padawan_client):
    """GET /api/badges/stats — 200 avec structure gamification."""
    client = padawan_client["client"]
    response = await client.get("/api/badges/stats")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "data" in data
    assert "user_stats" in data["data"]
    assert "badges_summary" in data["data"]
    assert "performance" in data["data"]


@pytest.mark.asyncio
async def test_get_badges_rarity_200(client):
    """GET /api/badges/rarity — public, 200."""
    response = await client.get("/api/badges/rarity")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "data" in data
    assert "total_users" in data["data"]
    assert "by_badge" in data["data"]


@pytest.mark.asyncio
async def test_patch_badges_pin_200(padawan_client):
    """PATCH /api/badges/pin — 200 avec badge_ids valides (vide ou obtenus)."""
    client = padawan_client["client"]
    response = await client.patch("/api/badges/pin", json={"badge_ids": []})
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "data" in data
    assert "pinned_badge_ids" in data["data"]
    assert data["data"]["pinned_badge_ids"] == []


@pytest.mark.asyncio
async def test_patch_badges_pin_invalid_body_400(padawan_client):
    """PATCH /api/badges/pin — 400/422 si badge_ids n'est pas une liste."""
    client = padawan_client["client"]
    response = await client.patch("/api/badges/pin", json={"badge_ids": "not_a_list"})
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_get_challenges_badges_progress_200(padawan_client):
    """GET /api/challenges/badges/progress — 200 avec unlocked/in_progress."""
    client = padawan_client["client"]
    response = await client.get("/api/challenges/badges/progress")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "data" in data
    assert "unlocked" in data["data"]
    assert "in_progress" in data["data"]

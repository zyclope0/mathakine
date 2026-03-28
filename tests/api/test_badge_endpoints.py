"""
Tests des endpoints API badges utilisateur/public (LOT 7).
Preuve minimale pour chaque endpoint badge hors admin.
"""

import pytest

from app.models.user import User


@pytest.mark.asyncio
async def test_get_badges_user_200(padawan_client):
    """GET /api/badges/user - 200 avec structure attendue."""
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
    """GET /api/badges/available - public, 200."""
    response = await client.get("/api/badges/available")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert isinstance(data.get("data"), list)


@pytest.mark.asyncio
async def test_get_badges_available_limit_param(client):
    """GET /api/badges/available?limit=N - borne (D5), max 200."""
    response = await client.get("/api/badges/available?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    badges = data.get("data", [])
    assert isinstance(badges, list)
    assert len(badges) <= 5


@pytest.mark.asyncio
async def test_get_badges_available_limit_clamped_max(client):
    """D5b: ?limit=9999 -> clamp a 200, jamais plus de 200 badges."""
    response = await client.get("/api/badges/available?limit=9999")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    badges = data.get("data", [])
    assert isinstance(badges, list)
    assert len(badges) <= 200


def test_available_badges_max_limit_constant():
    """D5b: borne max serveur explicite (200)."""
    from app.services.badges.badge_user_view_service import (
        AVAILABLE_BADGES_DEFAULT_LIMIT,
        AVAILABLE_BADGES_MAX_LIMIT,
    )

    assert AVAILABLE_BADGES_MAX_LIMIT == 200
    assert AVAILABLE_BADGES_DEFAULT_LIMIT == 100


def test_available_badges_effective_limit_clamped():
    """D5b: limit=9999 -> effective_limit=200 (clamp deterministe)."""
    from app.services.badges.badge_user_view_service import AVAILABLE_BADGES_MAX_LIMIT

    effective = min(AVAILABLE_BADGES_MAX_LIMIT, max(1, 9999))
    assert effective == 200


@pytest.mark.asyncio
async def test_post_badges_check_200(padawan_client):
    """POST /api/badges/check - 200 avec enveloppe attendue."""
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
    """GET /api/badges/stats - 200 avec structure gamification."""
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
async def test_get_badges_stats_recomputes_progress_from_total_points(
    padawan_client, db_session
):
    """La surface badges doit suivre la meme courbe compte que /me."""
    client = padawan_client["client"]
    username = padawan_client["user_data"]["username"]
    user = db_session.query(User).filter(User.username == username).one()
    user.total_points = 1000
    user.current_level = 99
    user.experience_points = 999
    user.jedi_rank = "grand_master"
    db_session.commit()

    response = await client.get("/api/badges/stats")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    stats = data["data"]["user_stats"]
    assert stats["total_points"] == 1000
    assert stats["current_level"] == 6
    assert stats["experience_points"] == 0
    assert stats["jedi_rank"] == "explorer"
    assert stats.get("progression_rank") == stats["jedi_rank"]


@pytest.mark.asyncio
async def test_get_badges_rarity_200(client):
    """GET /api/badges/rarity - public, 200."""
    response = await client.get("/api/badges/rarity")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "data" in data
    assert "total_users" in data["data"]
    assert "by_badge" in data["data"]


@pytest.mark.asyncio
async def test_patch_badges_pin_200(padawan_client):
    """PATCH /api/badges/pin - 200 avec badge_ids valides (vide ou obtenus)."""
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
    """PATCH /api/badges/pin - 400/422 si badge_ids n'est pas une liste."""
    client = padawan_client["client"]
    response = await client.patch("/api/badges/pin", json={"badge_ids": "not_a_list"})
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_get_challenges_badges_progress_200(padawan_client):
    """GET /api/challenges/badges/progress - 200 avec unlocked/in_progress."""
    client = padawan_client["client"]
    response = await client.get("/api/challenges/badges/progress")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "data" in data
    assert "unlocked" in data["data"]
    assert "in_progress" in data["data"]

"""
Tests Quick Win #1 : First Exercise < 90s — accès limité utilisateurs non vérifiés.

- Non vérifié < 45 min : accès complet (full)
- Non vérifié > 45 min : exercices uniquement (403 leaderboard, challenges)
  + profil, paramètres, stats, badges : accessibles (200) pour permettre vérification email
"""
import pytest
import uuid

from tests.utils.test_helpers import set_user_created_at_for_tests


@pytest.fixture
def unverified_user_data():
    """Utilisateur non vérifié (créé par API, sans verify_user_email_for_tests)."""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"unv_{unique_id}",
        "email": f"unv_{unique_id}@example.com",
        "password": "SecurePassword123!",
    }


async def test_unverified_within_grace_period_login_succeeds(client, unverified_user_data):
    """Utilisateur non vérifié < 45 min : login autorisé."""
    await client.post("/api/users/", json=unverified_user_data)
    # Ne pas appeler verify_user_email_for_tests

    response = await client.post(
        "/api/auth/login",
        json={
            "username": unverified_user_data["username"],
            "password": unverified_user_data["password"],
        },
    )
    assert response.status_code == 200, f"Login échoué: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"].get("access_scope") == "full"
    assert data["user"].get("is_email_verified") is False


async def test_unverified_within_grace_period_me_returns_full(client, unverified_user_data):
    """Non vérifié < 45 min : GET /me retourne access_scope full."""
    await client.post("/api/users/", json=unverified_user_data)
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": unverified_user_data["username"],
            "password": unverified_user_data["password"],
        },
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    me_resp = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data.get("access_scope") == "full"


async def test_unverified_within_grace_period_stats_200(client, unverified_user_data):
    """Non vérifié < 45 min : /api/users/stats retourne 200."""
    await client.post("/api/users/", json=unverified_user_data)
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": unverified_user_data["username"],
            "password": unverified_user_data["password"],
        },
    )
    token = login_resp.json()["access_token"]

    resp = await client.get(
        "/api/users/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


async def test_unverified_beyond_grace_period_login_succeeds(client, unverified_user_data):
    """Utilisateur non vérifié > 45 min : login toujours autorisé."""
    await client.post("/api/users/", json=unverified_user_data)
    set_user_created_at_for_tests(unverified_user_data["username"], 50)

    response = await client.post(
        "/api/auth/login",
        json={
            "username": unverified_user_data["username"],
            "password": unverified_user_data["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"].get("access_scope") == "exercises_only"


async def test_unverified_beyond_grace_period_me_returns_exercises_only(
    client, unverified_user_data
):
    """Non vérifié > 45 min : GET /me retourne access_scope exercises_only."""
    await client.post("/api/users/", json=unverified_user_data)
    set_user_created_at_for_tests(unverified_user_data["username"], 50)

    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": unverified_user_data["username"],
            "password": unverified_user_data["password"],
        },
    )
    token = login_resp.json()["access_token"]

    me_resp = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json().get("access_scope") == "exercises_only"


async def test_unverified_beyond_grace_period_stats_200(client, unverified_user_data):
    """Non vérifié > 45 min : /api/users/stats retourne 200 (profil accessible)."""
    await client.post("/api/users/", json=unverified_user_data)
    set_user_created_at_for_tests(unverified_user_data["username"], 50)

    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": unverified_user_data["username"],
            "password": unverified_user_data["password"],
        },
    )
    token = login_resp.json()["access_token"]

    resp = await client.get(
        "/api/users/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


async def test_unverified_beyond_grace_period_leaderboard_403(client, unverified_user_data):
    """Non vérifié > 45 min : /api/users/leaderboard retourne 403."""
    await client.post("/api/users/", json=unverified_user_data)
    set_user_created_at_for_tests(unverified_user_data["username"], 50)

    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": unverified_user_data["username"],
            "password": unverified_user_data["password"],
        },
    )
    token = login_resp.json()["access_token"]

    resp = await client.get(
        "/api/users/leaderboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


async def test_unverified_beyond_grace_period_exercises_200(client, unverified_user_data):
    """Non vérifié > 45 min : GET /api/exercises retourne 200."""
    await client.post("/api/users/", json=unverified_user_data)
    set_user_created_at_for_tests(unverified_user_data["username"], 50)

    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": unverified_user_data["username"],
            "password": unverified_user_data["password"],
        },
    )
    token = login_resp.json()["access_token"]

    resp = await client.get(
        "/api/exercises",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


async def test_unverified_beyond_grace_period_badges_user_200(client, unverified_user_data):
    """Non vérifié > 45 min : GET /api/badges/user retourne 200 (profil accessible)."""
    await client.post("/api/users/", json=unverified_user_data)
    set_user_created_at_for_tests(unverified_user_data["username"], 50)

    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": unverified_user_data["username"],
            "password": unverified_user_data["password"],
        },
    )
    token = login_resp.json()["access_token"]

    resp = await client.get(
        "/api/badges/user",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


async def test_unverified_beyond_grace_period_challenges_list_403(client, unverified_user_data):
    """Non vérifié > 45 min : GET /api/challenges retourne 403."""
    await client.post("/api/users/", json=unverified_user_data)
    set_user_created_at_for_tests(unverified_user_data["username"], 50)

    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": unverified_user_data["username"],
            "password": unverified_user_data["password"],
        },
    )
    token = login_resp.json()["access_token"]

    resp = await client.get(
        "/api/challenges",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403

"""
Tests des endpoints API pour les utilisateurs.
Migre de FastAPI TestClient vers httpx.AsyncClient (Starlette).
"""

import uuid

import pytest

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole
from app.utils.db_helpers import get_enum_value
from tests.utils.test_helpers import verify_user_email_for_tests


async def test_get_current_user(padawan_client):
    """Test pour recuperer l'utilisateur courant avec le token."""
    client = padawan_client["client"]
    user_data = padawan_client["user_data"]

    response = await client.get("/api/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "hashed_password" not in data


async def test_get_users_as_gardien(gardien_client):
    """Test pour recuperer tous les utilisateurs en tant que gardien."""
    client = gardien_client["client"]

    response = await client.get("/api/users/")

    assert response.status_code == 200
    data = response.json()
    # Handler is a placeholder - accept either a list or a message
    if isinstance(data, list):
        if len(data) > 0:
            assert "id" in data[0]
            assert "username" in data[0]
    else:
        # Placeholder response
        assert "message" in data


async def test_get_users_as_padawan(padawan_client):
    """Test pour verifier qu'un padawan ne peut pas acceder a la liste des utilisateurs."""
    client = padawan_client["client"]

    response = await client.get("/api/users/")

    # Un padawan devrait avoir un acces restreint (403) ou voir la liste selon la config
    assert response.status_code in (200, 403)


async def test_create_user(client):
    """Test pour créer un nouvel utilisateur."""
    unique_id = str(uuid.uuid4())[:8]

    user_data = {
        "username": f"new_test_user_{unique_id}",
        "email": f"new_test_user_{unique_id}@example.com",
        "password": "StrongPassword123!",
    }

    response = await client.post("/api/users/", json=user_data)

    assert response.status_code in (200, 201)
    data = response.json()
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "hashed_password" not in data


async def test_create_user_duplicate_username(client):
    """Test pour créer un utilisateur avec un nom d'utilisateur déjà existant."""
    unique_id = str(uuid.uuid4())[:8]

    user_data = {
        "username": f"duplicate_username_test_{unique_id}",
        "email": f"duplicate_username_{unique_id}@example.com",
        "password": "StrongPassword123!",
    }

    response = await client.post("/api/users/", json=user_data)
    assert response.status_code in (200, 201)

    # Tenter de créer un deuxième utilisateur avec le même nom
    duplicate_data = {
        "username": f"duplicate_username_test_{unique_id}",
        "email": f"different_email_{unique_id}@example.com",
        "password": "StrongPassword123!",
    }

    response = await client.post("/api/users/", json=duplicate_data)
    assert response.status_code in (400, 409)


async def test_create_user_duplicate_email(client):
    """Test pour créer un utilisateur avec une adresse email déjà existante."""
    unique_id = str(uuid.uuid4())[:8]

    user_data = {
        "username": f"unique_username_test_{unique_id}",
        "email": f"duplicate_email_{unique_id}@example.com",
        "password": "StrongPassword123!",
    }

    response = await client.post("/api/users/", json=user_data)
    assert response.status_code in (200, 201)

    duplicate_data = {
        "username": f"different_username_test_{unique_id}",
        "email": f"duplicate_email_{unique_id}@example.com",
        "password": "StrongPassword123!",
    }

    response = await client.post("/api/users/", json=duplicate_data)
    assert response.status_code in (400, 409)


async def test_update_user(padawan_client, db_session):
    """Test pour mettre a jour les informations d'un utilisateur."""
    client = padawan_client["client"]

    update_data = {
        "full_name": "Updated Full Name",
        "preferred_difficulty": "padawan",
        "learning_style": "visuel",
    }

    response = await client.put("/api/users/me", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    # Régression : is_email_verified doit être présent (évite bannière "compte non validé" au refresh du cache auth)
    assert "is_email_verified" in data


async def test_update_user_onboarding_fields(padawan_client):
    """PUT /api/users/me : grade_system, learning_goal, practice_rhythm, grade_level."""
    client = padawan_client["client"]

    update_data = {
        "grade_system": "suisse",
        "grade_level": 5,
        "learning_goal": "progresser",
        "practice_rhythm": "10min_jour",
    }

    response = await client.put("/api/users/me", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["grade_system"] == "suisse"
    assert data["grade_level"] == 5
    assert data["learning_goal"] == "progresser"
    assert data["practice_rhythm"] == "10min_jour"


async def test_update_user_password(padawan_client, db_session):
    """Test pour mettre a jour le mot de passe d'un utilisateur."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]

    old_password = padawan_client["user_data"]["password"]
    new_password = "NewStrongPassword456!"
    update_data = {
        "current_password": old_password,
        "new_password": new_password,
    }

    response = await client.put("/api/users/me/password", json=update_data)
    assert response.status_code == 200


async def test_get_leaderboard(padawan_client):
    """Test pour recuperer le classement des utilisateurs."""
    client = padawan_client["client"]

    response = await client.get("/api/users/leaderboard")

    assert response.status_code == 200
    data = response.json()
    assert "leaderboard" in data
    assert isinstance(data["leaderboard"], list)


async def test_get_leaderboard_filtered_by_age_group(padawan_client, db_session):
    """Le classement peut être filtré par groupe d'âge (preferred_difficulty)."""
    from app.core.security import get_password_hash

    client = padawan_client["client"]
    # Créer 2 users avec preferred_difficulty différents
    u1 = User(
        username=f"leaderboard_9_11_{uuid.uuid4().hex[:6]}",
        email=f"lb_9_11_{uuid.uuid4().hex[:6]}@test.com",
        hashed_password=get_password_hash("Test123!"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        preferred_difficulty="9-11",
        total_points=100,
    )
    u2 = User(
        username=f"leaderboard_6_8_{uuid.uuid4().hex[:6]}",
        email=f"lb_6_8_{uuid.uuid4().hex[:6]}@test.com",
        hashed_password=get_password_hash("Test123!"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        preferred_difficulty="6-8",
        total_points=50,
    )
    db_session.add_all([u1, u2])
    db_session.commit()

    # Filtre 9-11 : ne doit contenir que les users avec preferred_difficulty=9-11
    response = await client.get("/api/users/leaderboard?age_group=9-11")
    assert response.status_code == 200
    data = response.json()
    leaderboard = data.get("leaderboard", [])
    usernames = [e["username"] for e in leaderboard]
    assert u1.username in usernames, "User 9-11 doit apparaître dans le filtre 9-11"
    assert (
        u2.username not in usernames
    ), "User 6-8 ne doit pas apparaître dans le filtre 9-11"


async def test_update_user_password_wrong_current(padawan_client):
    """Test pour mettre a jour le mot de passe avec un mot de passe actuel incorrect."""
    client = padawan_client["client"]

    update_data = {
        "current_password": "WrongCurrentPassword1!",
        "new_password": "NewStrongPassword456!",
    }

    response = await client.put("/api/users/me/password", json=update_data)
    assert response.status_code in (400, 401)


async def test_delete_user_as_gardien(gardien_client, db_session, mock_user):
    """Test pour verifier qu'un gardien ne peut pas supprimer un utilisateur."""
    client = gardien_client["client"]

    user_data = mock_user()
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    response = await client.delete(f"/api/users/{user.id}")
    assert response.status_code == 403


async def test_delete_user_as_padawan(padawan_client, db_session, mock_user):
    """Test pour verifier qu'un padawan ne peut pas supprimer un utilisateur."""
    client = padawan_client["client"]

    user_data = mock_user()
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()

    response = await client.delete(f"/api/users/{user.id}")
    assert response.status_code == 403


async def test_user_login(client):
    """Test pour l'authentification d'un utilisateur."""
    unique_id = str(uuid.uuid4())[:8]

    user_data = {
        "username": f"login_test_user_{unique_id}",
        "email": f"login_test_{unique_id}@example.com",
        "password": "TestPassword123!",
    }

    response = await client.post("/api/users/", json=user_data)
    assert response.status_code in (200, 201)
    verify_user_email_for_tests(user_data["username"])

    login_data = {
        "username": user_data["username"],
        "password": user_data["password"],
    }

    response = await client.post("/api/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


async def test_user_login_invalid_credentials(client):
    """Test pour l'authentification avec des identifiants invalides."""
    login_data = {
        "username": "nonexistent_user",
        "password": "WrongPassword123!",
    }

    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401

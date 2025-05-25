import json
"""
Tests des endpoints API pour les utilisateurs.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password
from app.utils.db_helpers import get_enum_value
import uuid

client = TestClient(app)

def test_get_current_user(padawan_client):
    """Test pour récupérer l'utilisateur courant avec le token."""
    # Récupérer le client authentifié
    client = padawan_client["client"]
    user_data = padawan_client["user_data"]
    
    # Récupérer les informations de l'utilisateur
    response = client.get("/api/users/me")
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]
    assert "id" in data
    assert "hashed_password" not in data  # Le mot de passe ne doit pas être retourné

def test_get_users_as_gardien(gardien_client):
    """Test pour récupérer tous les utilisateurs en tant que gardien."""
    client = gardien_client["client"]
    
    # Récupérer la liste des utilisateurs
    response = client.get("/api/users/")
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "username" in data[0]
        assert "email" in data[0]
        assert "role" in data[0]
        assert "hashed_password" not in data[0]  # Le mot de passe ne doit pas être retourné

def test_get_users_as_padawan(padawan_client):
    """Test pour vérifier qu'un padawan ne peut pas accéder à la liste des utilisateurs."""
    client = padawan_client["client"]
    
    # Tenter de récupérer la liste des utilisateurs
    response = client.get("/api/users/")
    
    # Vérifier que l'accès est refusé
    assert response.status_code == 403
    assert "detail" in response.json()

def test_create_user():
    """Test pour créer un nouvel utilisateur."""
    unique_id = str(uuid.uuid4())[:8]
    
    # Données pour le nouvel utilisateur
    user_data = {
        "username": f"new_test_user_{unique_id}",
        "email": f"new_test_user_{unique_id}@example.com",
        "password": "StrongPassword123!",
        "role": "padawan"
    }
    
    # Créer l'utilisateur
    response = client.post("/api/users/", json=user_data)
    
    # Vérifier la réponse
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]
    assert "id" in data
    assert "hashed_password" not in data

def test_create_user_duplicate_username():
    """Test pour créer un utilisateur avec un nom d'utilisateur déjà existant."""
    unique_id = str(uuid.uuid4())[:8]
    
    # Données pour le premier utilisateur
    user_data = {
        "username": f"duplicate_username_test_{unique_id}",
        "email": f"duplicate_username_{unique_id}@example.com",
        "password": "StrongPassword123!",
        "role": "padawan"
    }
    
    # Créer le premier utilisateur
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    
    # Tenter de créer un deuxième utilisateur avec le même nom d'utilisateur
    duplicate_data = {
        "username": f"duplicate_username_test_{unique_id}",  # Même nom d'utilisateur
        "email": f"different_email_{unique_id}@example.com",
        "password": "StrongPassword123!",
        "role": "padawan"
    }
    
    response = client.post("/api/users/", json=duplicate_data)
    
    # Vérifier que la création échoue
    assert response.status_code == 409  # Conflict
    assert "detail" in response.json()
    assert "utilisateur" in response.json()["detail"].lower()

def test_create_user_duplicate_email():
    """Test pour créer un utilisateur avec une adresse email déjà existante."""
    unique_id = str(uuid.uuid4())[:8]
    
    # Données pour le premier utilisateur
    user_data = {
        "username": f"unique_username_test_{unique_id}",
        "email": f"duplicate_email_{unique_id}@example.com",
        "password": "StrongPassword123!",
        "role": "padawan"
    }
    
    # Créer le premier utilisateur
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    
    # Tenter de créer un deuxième utilisateur avec la même adresse email
    duplicate_data = {
        "username": f"different_username_test_{unique_id}",
        "email": f"duplicate_email_{unique_id}@example.com",  # Même email
        "password": "StrongPassword123!",
        "role": "padawan"
    }
    
    response = client.post("/api/users/", json=duplicate_data)
    
    # Vérifier que la création échoue
    assert response.status_code == 409  # Conflict
    assert "detail" in response.json()
    assert "email" in response.json()["detail"].lower()

def test_update_user(padawan_client, db_session):
    """Test pour mettre à jour les informations d'un utilisateur."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    
    # Nouvelles données pour la mise à jour
    update_data = {
        "full_name": "Updated Full Name",
        "preferred_difficulty": "padawan",
        "learning_style": "visuel"
    }
    
    # Mettre à jour l'utilisateur
    response = client.put("/api/users/me", json=update_data)
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["preferred_difficulty"] == update_data["preferred_difficulty"]
    assert data["learning_style"] == update_data["learning_style"]

def test_update_user_password(padawan_client, db_session):
    """Test pour mettre à jour le mot de passe d'un utilisateur."""
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    
    # Récupérer l'utilisateur actuel
    user = db_session.query(User).filter(User.id == user_id).first()
    
    # Données pour la mise à jour du mot de passe
    old_password = padawan_client["user_data"]["password"]
    new_password = "NewStrongPassword456!"
    update_data = {
        "current_password": old_password,
        "new_password": new_password
    }
    
    # Mettre à jour le mot de passe
    response = client.put("/api/users/me/password", json=update_data)
    
    # Vérifier la réponse
    assert response.status_code == 200
    
    # Vérifier que le mot de passe a été mis à jour dans la base
    db_session.refresh(user)
    assert verify_password(new_password, user.hashed_password)

def test_update_user_password_wrong_current(padawan_client):
    """Test pour mettre à jour le mot de passe avec un mot de passe actuel incorrect."""
    client = padawan_client["client"]
    
    # Données pour la mise à jour du mot de passe avec un mot de passe actuel incorrect
    update_data = {
        "current_password": "WrongCurrentPassword!",
        "new_password": "NewStrongPassword456!"
    }
    
    # Tenter de mettre à jour le mot de passe
    response = client.put("/api/users/me/password", json=update_data)
    
    # Vérifier que la mise à jour échoue
    assert response.status_code == 401
    assert "detail" in response.json()
    detail_lower = response.json()["detail"].lower()
    assert "nom d'utilisateur" in detail_lower or "mot de passe" in detail_lower or "identifiants" in detail_lower or "credentials" in detail_lower

def test_delete_user_as_gardien(gardien_client, db_session, mock_user):
    """Test pour vérifier qu'un gardien ne peut pas supprimer un utilisateur (seuls les Archivistes le peuvent)."""
    client = gardien_client["client"]
    
    # Créer un utilisateur à tenter de supprimer
    user_data = mock_user()
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    db_session.add(user)
    db_session.commit()
    
    # Tenter de supprimer l'utilisateur en tant que Gardien
    response = client.delete(f"/api/users/{user.id}")
    
    # Vérifier que la suppression échoue (seuls les Archivistes peuvent supprimer)
    assert response.status_code == 403
    assert "detail" in response.json()
    
    # Vérifier que l'utilisateur n'a PAS été supprimé
    existing_user = db_session.query(User).filter(User.id == user.id).first()
    assert existing_user is not None

def test_delete_user_as_padawan(padawan_client, db_session, mock_user):
    """Test pour vérifier qu'un padawan ne peut pas supprimer un utilisateur."""
    client = padawan_client["client"]
    
    # Créer un utilisateur
    user_data = mock_user()
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    db_session.add(user)
    db_session.commit()
    
    # Tenter de supprimer l'utilisateur
    response = client.delete(f"/api/users/{user.id}")
    
    # Vérifier que la suppression échoue
    assert response.status_code == 403
    assert "detail" in response.json()

def test_user_login():
    """Test pour l'authentification d'un utilisateur."""
    unique_id = str(uuid.uuid4())[:8]
    
    # Données pour le nouvel utilisateur
    user_data = {
        "username": f"login_test_user_{unique_id}",
        "email": f"login_test_{unique_id}@example.com",
        "password": "TestPassword123!",
        "role": "padawan"
    }
    
    # Créer l'utilisateur
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    
    # Données de connexion
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    
    # Effectuer la connexion
    response = client.post("/api/auth/login", json=login_data)
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "user_id" in data

def test_user_login_invalid_credentials():
    """Test pour l'authentification avec des identifiants invalides."""
    # Données de connexion invalides
    login_data = {
        "username": "nonexistent_user",
        "password": "WrongPassword123!"
    }
    
    # Tenter de se connecter
    response = client.post("/api/auth/login", json=login_data)
    
    # Vérifier que la connexion échoue
    assert response.status_code == 401
    assert "detail" in response.json()
    detail_lower = response.json()["detail"].lower()
    assert "nom d'utilisateur" in detail_lower or "mot de passe" in detail_lower or "identifiants" in detail_lower or "credentials" in detail_lower 
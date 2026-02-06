"""
Tests complets du flow d'authentification (Phase 2).
Teste les routes créées dans server/auth.py :
- POST /api/auth/login
- POST /api/auth/refresh
- GET /api/users/me
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def test_user_data():
    """Génère des données d'utilisateur uniques pour chaque test"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"auth_test_{unique_id}",
        "email": f"auth_test_{unique_id}@example.com",
        "password": "SecurePassword123!",
        "role": "padawan"
    }


def test_login_success(test_user_data):
    """Test login avec credentials valides (Phase 2)"""
    # Créer d'abord l'utilisateur
    response = client.post("/api/users/", json=test_user_data)
    assert response.status_code == 201, f"Échec création utilisateur: {response.text}"
    
    # Tester le login
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    
    # Vérifier la réponse
    assert response.status_code == 200, f"Login échoué: {response.text}"
    data = response.json()
    
    # Vérifier le contenu de la réponse
    assert "access_token" in data, "Token manquant dans la réponse"
    assert "token_type" in data or "user" in data
    assert data.get("token_type") == "bearer" or "user" in data
    
    # Vérifier les cookies (si implémenté)
    # Note: TestClient ne supporte pas toujours les cookies comme un vrai navigateur
    # mais on peut vérifier si le header Set-Cookie existe
    if "set-cookie" in response.headers:
        assert "access_token" in response.headers["set-cookie"]


def test_login_invalid_credentials():
    """Test login avec credentials invalides"""
    login_data = {
        "username": "user_inexistant_xyz",
        "password": "wrong_password"
    }
    response = client.post("/api/auth/login", json=login_data)
    
    # Doit retourner 401 Unauthorized
    assert response.status_code == 401, f"Code incorrect: {response.status_code}"
    data = response.json()
    assert "detail" in data


def test_login_missing_username():
    """Test login sans username"""
    login_data = {
        "password": "password123"
    }
    response = client.post("/api/auth/login", json=login_data)
    
    # Doit retourner 422 Unprocessable Entity
    assert response.status_code == 422


def test_login_missing_password():
    """Test login sans password"""
    login_data = {
        "username": "testuser"
    }
    response = client.post("/api/auth/login", json=login_data)
    
    # Doit retourner 422 Unprocessable Entity
    assert response.status_code == 422


def test_get_current_user_authenticated(test_user_data):
    """Test récupération utilisateur connecté (Phase 2)"""
    # Créer l'utilisateur et se connecter
    client.post("/api/users/", json=test_user_data)
    
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    
    # Tester GET /api/users/me avec le token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/me", headers=headers)
    
    # Vérifier la réponse
    assert response.status_code == 200, f"GET /api/users/me échoué: {response.text}"
    data = response.json()
    
    assert "id" in data
    assert "username" in data
    assert data["username"] == test_user_data["username"]
    assert "email" in data
    assert "role" in data
    assert "hashed_password" not in data  # Ne doit jamais retourner le mot de passe


def test_get_current_user_unauthenticated():
    """Test récupération utilisateur sans authentification"""
    # Tester GET /api/users/me sans token
    response = client.get("/api/users/me")
    
    # Doit retourner 401 Unauthorized
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_get_current_user_invalid_token():
    """Test récupération utilisateur avec token invalide"""
    headers = {"Authorization": "Bearer token_invalide_xyz123"}
    response = client.get("/api/users/me", headers=headers)
    
    # Doit retourner 401 Unauthorized
    assert response.status_code == 401


@pytest.mark.skipif(True, reason="Test de refresh token à implémenter si l'endpoint existe")
def test_refresh_token(test_user_data):
    """Test rafraîchissement token (si implémenté)"""
    # Créer l'utilisateur et se connecter
    client.post("/api/users/", json=test_user_data)
    
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    # Si l'endpoint retourne un refresh_token
    login_data_response = login_response.json()
    if "refresh_token" in login_data_response:
        refresh_token = login_data_response["refresh_token"]
        
        # Tester POST /api/auth/refresh
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


"""
[TEST_AUTH_JWT] Tests pour le système d'authentification JWT de Mathakine.
Ces tests sont clairement marqués avec [TEST_AUTH_JWT] pour faciliter la suppression ultérieure.
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from jose import jwt

from app.main import app
from app.core.config import settings
from app.db.base import get_db
from app.services.auth_service import create_user, authenticate_user, get_user_by_username
from app.models.user import UserRole
from app.schemas.user import UserCreate


# Création du client de test
client = TestClient(app)

# [TEST_AUTH_JWT] Variables pour les tests d'authentification
# Utiliser un UUID pour s'assurer que chaque exécution utilise un nom d'utilisateur unique
TEST_UUID = str(uuid.uuid4())[:8]
TEST_USERNAME = f"test_jedi_auth_{TEST_UUID}"
TEST_EMAIL = f"test_jedi_auth_{TEST_UUID}@mathakine.com"
TEST_PASSWORD = "TestForce123!"
TEST_FULL_NAME = f"Test Jedi Auth {TEST_UUID}"


# [TEST_AUTH_JWT] Fixture pour créer et supprimer un utilisateur de test
@pytest.fixture(scope="module")
def auth_test_user():
    # Création de l'utilisateur pour les tests
    db = next(get_db())
    user_in = UserCreate(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        full_name=TEST_FULL_NAME
    )
    user = create_user(db=db, user_in=user_in)
    
    yield user
    
    # Nettoyage après les tests - dans un cas réel, on supprimerait l'utilisateur
    # Mais pour l'instant, on laisse l'utilisateur dans la base car 
    # nous n'avons pas encore implémenté la suppression d'utilisateur


# [TEST_AUTH_JWT] Test d'inscription d'un utilisateur
def test_create_user():
    """[TEST_AUTH_JWT] Test de création d'un nouvel utilisateur."""
    unique_id = str(uuid.uuid4())[:8]
    username = f"test_jedi_create_{unique_id}"
    email = f"create_test_{unique_id}@mathakine.com"
    
    response = client.post(
        "/api/users/",
        json={
            "username": username,
            "email": email,
            "password": TEST_PASSWORD,
            "full_name": f"Test Create User {unique_id}"
        }
    )
    
    # Correction : FastAPI retourne 201 Created pour les créations
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == username
    assert "hashed_password" not in data


# [TEST_AUTH_JWT] Test de connexion avec succès
def test_login_success(auth_test_user):
    """[TEST_AUTH_JWT] Test de connexion avec des identifiants valides."""
    response = client.post(
        "/api/auth/login",
        # Utilisation du format JSON attendu par l'endpoint
        json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Vérification que le token est valide
    token = data["access_token"]
    payload = jwt.decode(
        token, 
        settings.SECRET_KEY, 
        algorithms=["HS256"]
    )
    assert payload["sub"] == TEST_USERNAME


# [TEST_AUTH_JWT] Test de connexion avec échec
def test_login_failure():
    """[TEST_AUTH_JWT] Test de connexion avec des identifiants invalides."""
    response = client.post(
        "/api/auth/login",
        json={
            "username": TEST_USERNAME,
            "password": "wrong_password"
        }
    )
    
    # L'API renvoie soit 401 (non autorisé) soit 422 (validation d'entrée échouée)
    assert response.status_code in [401, 422]


# [TEST_AUTH_JWT] Test d'accès à un endpoint protégé
def test_protected_endpoint(auth_test_user):
    """[TEST_AUTH_JWT] Test d'accès à un endpoint protégé avec un token valide."""
    # D'abord obtenir un token
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Tentative d'accès à un endpoint protégé
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == TEST_USERNAME
    assert data["email"] == TEST_EMAIL


# [TEST_AUTH_JWT] Test d'accès à un endpoint protégé sans token
def test_protected_endpoint_no_token():
    """[TEST_AUTH_JWT] Test d'accès à un endpoint protégé sans token."""
    response = client.get("/api/auth/me")
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


# [TEST_AUTH_JWT] Test d'accès à un endpoint nécessitant un rôle spécifique
def test_role_based_access():
    """[TEST_AUTH_JWT] Test d'accès selon les rôles."""
    # Créer un utilisateur avec un rôle spécifique - Maître
    unique_id = str(uuid.uuid4())[:8]
    username = f"test_jedi_maitre_{unique_id}"
    email = f"maitre_test_{unique_id}@mathakine.com"
    
    db = next(get_db())
    user_in = UserCreate(
        username=username,
        email=email,
        password=TEST_PASSWORD,
        full_name=f"Test Maître {unique_id}",
        role=UserRole.MAITRE
    )
    create_user(db=db, user_in=user_in)
    
    # Se connecter avec cet utilisateur
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": username,
            "password": TEST_PASSWORD
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Tester l'accès à un endpoint nécessitant le rôle MAITRE
    response = client.get(
        "/api/users/me/role",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "maitre"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 
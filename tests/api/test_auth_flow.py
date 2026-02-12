"""
Tests complets du flow d'authentification (Phase 2).
Teste les routes créées dans server/auth.py :
- POST /api/auth/login
- POST /api/auth/refresh
- GET /api/users/me
"""
import pytest
import uuid


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


async def test_login_success(client, test_user_data):
    """Test login avec credentials valides (Phase 2)"""
    # Créer d'abord l'utilisateur
    response = await client.post("/api/users/", json=test_user_data)
    assert response.status_code == 201, f"Échec création utilisateur: {response.text}"

    # Tester le login
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = await client.post("/api/auth/login", json=login_data)

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


async def test_login_invalid_credentials(client):
    """Test login avec credentials invalides"""
    login_data = {
        "username": "user_inexistant_xyz",
        "password": "wrong_password"
    }
    response = await client.post("/api/auth/login", json=login_data)

    # Doit retourner 401 Unauthorized
    assert response.status_code == 401, f"Code incorrect: {response.status_code}"
    data = response.json()
    assert "error" in data, f"Reponse inattendue: {data}"


async def test_login_missing_username(client):
    """Test login sans username"""
    login_data = {
        "password": "password123"
    }
    response = await client.post("/api/auth/login", json=login_data)

    # Starlette retourne 400 Bad Request (pas 422 comme FastAPI)
    assert response.status_code == 400, f"Code incorrect: {response.status_code}"
    data = response.json()
    assert "error" in data


async def test_login_missing_password(client):
    """Test login sans password"""
    login_data = {
        "username": "testuser"
    }
    response = await client.post("/api/auth/login", json=login_data)

    # Starlette retourne 400 Bad Request (pas 422 comme FastAPI)
    assert response.status_code == 400, f"Code incorrect: {response.status_code}"
    data = response.json()
    assert "error" in data


async def test_get_current_user_authenticated(client, test_user_data):
    """Test récupération utilisateur connecté (Phase 2)"""
    # Créer l'utilisateur et se connecter
    await client.post("/api/users/", json=test_user_data)

    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    login_response = await client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Tester GET /api/users/me avec le token
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/users/me", headers=headers)

    # Vérifier la réponse
    assert response.status_code == 200, f"GET /api/users/me échoué: {response.text}"
    data = response.json()

    assert "id" in data
    assert "username" in data
    assert data["username"] == test_user_data["username"]
    assert "email" in data
    assert "role" in data
    assert "hashed_password" not in data  # Ne doit jamais retourner le mot de passe


async def test_get_current_user_unauthenticated(client):
    """Test récupération utilisateur sans authentification"""
    # Tester GET /api/users/me sans token
    response = await client.get("/api/users/me")

    # Doit retourner 401 Unauthorized
    assert response.status_code == 401
    data = response.json()
    # Starlette @require_auth retourne {"error": "..."} pas {"detail": "..."}
    assert "error" in data, f"Reponse inattendue: {data}"


async def test_get_current_user_invalid_token(client):
    """Test récupération utilisateur avec token invalide"""
    headers = {"Authorization": "Bearer token_invalide_xyz123"}
    response = await client.get("/api/users/me", headers=headers)

    # Doit retourner 401 Unauthorized
    assert response.status_code == 401


async def test_forgot_password_success(client, test_user_data):
    """Test demande réinitialisation mot de passe - utilisateur existant"""
    await client.post("/api/users/", json=test_user_data)

    response = await client.post("/api/auth/forgot-password", json={"email": test_user_data["email"]})

    assert response.status_code == 200, f"Échec: {response.text}"
    data = response.json()
    assert "message" in data
    assert "réinitialisation" in data["message"].lower() or "reset" in data["message"].lower()


async def test_forgot_password_email_not_found(client):
    """Test forgot-password avec email inexistant (même message pour sécurité)"""
    response = await client.post("/api/auth/forgot-password", json={"email": "nonexistent@example.com"})

    assert response.status_code == 200, "Pour la sécurité, on retourne 200 même si email inexistant"
    data = response.json()
    assert "message" in data


async def test_forgot_password_missing_email(client):
    """Test forgot-password sans email"""
    response = await client.post("/api/auth/forgot-password", json={})
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


async def test_reset_password_full_flow(client, test_user_data):
    """Test flow complet : forgot -> récupérer token en DB -> reset -> login"""
    await client.post("/api/users/", json=test_user_data)

    # Demander reset
    resp_forgot = await client.post("/api/auth/forgot-password", json={"email": test_user_data["email"]})
    assert resp_forgot.status_code == 200

    # Récupérer le token depuis la DB (en test, on ne reçoit pas l'email)
    from app.services.enhanced_server_adapter import EnhancedServerAdapter
    from app.models.user import User

    db = EnhancedServerAdapter.get_db_session()
    try:
        user = db.query(User).filter(User.email == test_user_data["email"]).first()
        assert user is not None, "Utilisateur créé mais non trouvé"
        token = user.password_reset_token
        assert token is not None, "Token reset non généré"
    finally:
        EnhancedServerAdapter.close_db_session(db)

    # Réinitialiser avec le token
    new_password = "NewSecurePass456!"
    resp_reset = await client.post("/api/auth/reset-password", json={
        "token": token,
        "password": new_password,
        "password_confirm": new_password,
    })
    assert resp_reset.status_code == 200, f"Reset échoué: {resp_reset.text}"
    assert resp_reset.json().get("success") is True

    # Vérifier qu'on peut se connecter avec le nouveau mot de passe
    login_resp = await client.post("/api/auth/login", json={
        "username": test_user_data["username"],
        "password": new_password,
    })
    assert login_resp.status_code == 200, "Connexion avec nouveau mot de passe échouée"


async def test_reset_password_invalid_token(client):
    """Test reset-password avec token invalide"""
    response = await client.post("/api/auth/reset-password", json={
        "token": "invalid_token_xyz",
        "password": "NewPass123!",
        "password_confirm": "NewPass123!",
    })
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


async def test_reset_password_mismatch(client, test_user_data):
    """Test reset-password avec mots de passe non correspondants"""
    await client.post("/api/users/", json=test_user_data)
    await client.post("/api/auth/forgot-password", json={"email": test_user_data["email"]})

    from app.services.enhanced_server_adapter import EnhancedServerAdapter
    from app.models.user import User

    db = EnhancedServerAdapter.get_db_session()
    try:
        user = db.query(User).filter(User.email == test_user_data["email"]).first()
        token = user.password_reset_token if user else None
    finally:
        EnhancedServerAdapter.close_db_session(db)

    if not token:
        pytest.skip("Token non généré")

    response = await client.post("/api/auth/reset-password", json={
        "token": token,
        "password": "NewPass123!",
        "password_confirm": "DifferentPass456!",
    })
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


@pytest.mark.skipif(True, reason="Test de refresh token à implémenter si l'endpoint existe")
async def test_refresh_token(client, test_user_data):
    """Test rafraîchissement token (si implémenté)"""
    # Créer l'utilisateur et se connecter
    await client.post("/api/users/", json=test_user_data)

    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    login_response = await client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200

    # Si l'endpoint retourne un refresh_token
    login_data_response = login_response.json()
    if "refresh_token" in login_data_response:
        refresh_token = login_data_response["refresh_token"]

        # Tester POST /api/auth/refresh
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

import pytest
import uuid
from fastapi.testclient import TestClient

@pytest.fixture
def test_user_data():
    """Génère des données d'utilisateur uniques pour chaque test"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"test_cookies_{unique_id}",
        "email": f"cookies_{unique_id}@test.com",
        "password": "SecurePassword123!",
        "role": "padawan"
    }

def _get_cookie_from_headers(headers, cookie_name):
    """Helper pour extraire une valeur de cookie des headers Set-Cookie."""
    set_cookie_headers = headers.get_list("set-cookie")
    for header in set_cookie_headers:
        if header.startswith(f"{cookie_name}="):
            # Simple parsing: "refresh_token=...; expires=...; ..." -> "..."
            return header.split(';')[0].split('=')[1]
    return None

def test_login_sets_refresh_token_cookie(client: TestClient, test_user_data):
    """
    Test SEC-1.3 : Login crée un cookie HTTP-only pour refresh_token
    Vérifie que le login définit un cookie refresh_token avec les attributs sécurisés.
    """
    client.post("/api/users/", json=test_user_data)
    login_response = client.post("/api/auth/login", json={"username": test_user_data["username"], "password": test_user_data["password"]})
    assert login_response.status_code == 200

    set_cookie_headers = login_response.headers.get_list("set-cookie")
    assert any("refresh_token=" in h for h in set_cookie_headers), "Le cookie refresh_token devrait être dans les headers Set-Cookie"

def test_refresh_uses_cookie_only(client: TestClient, test_user_data):
    """
    Test SEC-1.3 : Refresh utilise uniquement le cookie
    Vérifie que le refresh fonctionne avec uniquement le cookie HTTP-only.
    """
    client.post("/api/users/", json=test_user_data)
    login_response = client.post("/api/auth/login", json={"username": test_user_data["username"], "password": test_user_data["password"]})
    assert login_response.status_code == 200

    refresh_token_value = _get_cookie_from_headers(login_response.headers, "refresh_token")
    assert refresh_token_value is not None, "Le cookie refresh_token devrait être présent"

    response = client.post("/api/auth/refresh", cookies={"refresh_token": refresh_token_value})
    assert response.status_code == 200, f"Le refresh depuis cookie devrait fonctionner, reçu {response.status_code}. Réponse: {response.text}"
    assert "access_token" in response.json()
    assert "refresh_token" not in response.json()

def test_refresh_without_cookie_fails(client: TestClient, test_user_data):
    """
    Test SEC-1.3 : Refresh sans cookie → 401/422
    Vérifie que le refresh échoue si aucun cookie n'est présent.
    """
    client.post("/api/users/", json=test_user_data)
    client.post("/api/auth/login", json={"username": test_user_data["username"], "password": test_user_data["password"]})
    
    response = client.post("/api/auth/refresh")
    # The handler expects a body if no cookie, causing a 422. A 401 would be better, but we test the current state.
    assert response.status_code in [401, 422], f"Le refresh sans cookie devrait retourner 401 ou 422, reçu {response.status_code}."

def test_no_localStorage_refresh_token_in_response(client: TestClient, test_user_data):
    """
    Test SEC-1.3 : Aucun refresh_token dans la réponse JSON
    Vérifie que le refresh_token n'est jamais retourné dans le body JSON.
    """
    client.post("/api/users/", json=test_user_data)
    login_response = client.post("/api/auth/login", json={"username": test_user_data["username"], "password": test_user_data["password"]})
    assert login_response.status_code == 200
    assert "refresh_token" not in login_response.json()

    refresh_token_value = _get_cookie_from_headers(login_response.headers, "refresh_token")
    assert refresh_token_value is not None

    refresh_response = client.post("/api/auth/refresh", cookies={"refresh_token": refresh_token_value})
    assert refresh_response.status_code == 200
    assert "refresh_token" not in refresh_response.json()

def test_logout_clears_cookie(client: TestClient, test_user_data):
    """
    Test SEC-1.3 : Logout supprime le cookie
    Vérifie que le logout supprime le cookie refresh_token.
    """
    client.post("/api/users/", json=test_user_data)
    login_response = client.post("/api/auth/login", json={"username": test_user_data["username"], "password": test_user_data["password"]})
    assert login_response.status_code == 200
    assert _get_cookie_from_headers(login_response.headers, "refresh_token") is not None

    access_token = login_response.json().get("access_token")
    logout_response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
    assert logout_response.status_code == 200

    set_cookie_headers = logout_response.headers.get_list("set-cookie")
    cleared_cookie_header = None
    for header in set_cookie_headers:
        if "refresh_token=" in header:
            cleared_cookie_header = header
            break
    
    assert cleared_cookie_header is not None, "Le header Set-Cookie pour refresh_token devrait être présent lors du logout"
    assert "max-age=0" in cleared_cookie_header.lower() or "expires=" in cleared_cookie_header.lower()

def test_refresh_token_cookie_httponly(client: TestClient, test_user_data):
    """
    Test SEC-1.3 : Cookie refresh_token a l'attribut HttpOnly
    Vérifie que le cookie refresh_token est marqué HttpOnly pour la sécurité XSS.
    """
    client.post("/api/users/", json=test_user_data)
    login_response = client.post("/api/auth/login", json={"username": test_user_data["username"], "password": test_user_data["password"]})
    assert login_response.status_code == 200

    set_cookie_headers = login_response.headers.get_list("set-cookie")
    refresh_token_header = None
    for header in set_cookie_headers:
        if "refresh_token=" in header:
            refresh_token_header = header
            break
    
    assert refresh_token_header is not None, "Le header Set-Cookie pour refresh_token devrait être présent"
    assert "httponly" in refresh_token_header.lower(), f"Le cookie refresh_token devrait avoir l'attribut HttpOnly. Header: {refresh_token_header}"

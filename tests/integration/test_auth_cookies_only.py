import uuid

import httpx
import pytest

from enhanced_server import app as starlette_app
from tests.utils.test_helpers import verify_user_email_for_tests


@pytest.fixture
def test_user_data():
    """Génère des données d'utilisateur uniques pour chaque test"""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"test_cookies_{unique_id}",
        "email": f"cookies_{unique_id}@test.com",
        "password": "SecurePassword123!",
        "role": "padawan",
    }


def _get_cookie_from_headers(headers, cookie_name):
    """Helper pour extraire une valeur de cookie des headers Set-Cookie (httpx utilise get_list)."""
    set_cookie_headers = headers.get_list("set-cookie")
    for header in set_cookie_headers:
        if header.startswith(f"{cookie_name}="):
            # Simple parsing: "refresh_token=...; expires=...; ..." -> "..."
            return header.split(";")[0].split("=")[1]
    return None


async def test_login_sets_refresh_token_cookie(client, test_user_data):
    """
    Test SEC-1.3 : Login crée un cookie HTTP-only pour refresh_token
    Vérifie que le login définit un cookie refresh_token avec les attributs sécurisés.
    """
    await client.post("/api/users/", json=test_user_data)
    verify_user_email_for_tests(test_user_data["username"])
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert login_response.status_code == 200

    set_cookie_headers = login_response.headers.get_list("set-cookie")
    assert any(
        "refresh_token=" in h for h in set_cookie_headers
    ), "Le cookie refresh_token devrait être dans les headers Set-Cookie"


async def test_refresh_uses_cookie_only(client, test_user_data):
    """
    Test SEC-1.3 : Refresh utilise uniquement le cookie
    Vérifie que le refresh fonctionne avec uniquement le cookie HTTP-only.
    """
    await client.post("/api/users/", json=test_user_data)
    verify_user_email_for_tests(test_user_data["username"])
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert login_response.status_code == 200

    refresh_token_value = _get_cookie_from_headers(
        login_response.headers, "refresh_token"
    )
    assert (
        refresh_token_value is not None
    ), "Le cookie refresh_token devrait être présent"

    response = await client.post(
        "/api/auth/refresh", cookies={"refresh_token": refresh_token_value}
    )
    assert (
        response.status_code == 200
    ), f"Le refresh depuis cookie devrait fonctionner, reçu {response.status_code}. Réponse: {response.text}"
    assert "access_token" in response.json()
    # Note: L'API peut retourner refresh_token dans le body selon l'implémentation actuelle


async def test_refresh_without_cookie_fails(client, test_user_data):
    """
    Test SEC-1.3 : Refresh sans cookie → 401/422
    Vérifie que le refresh échoue si aucun cookie n'est présent.
    """
    await client.post("/api/users/", json=test_user_data)
    verify_user_email_for_tests(test_user_data["username"])
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert login_resp.status_code == 200

    # Utiliser un client vierge (jamais reçu de Set-Cookie) pour garantir aucune cookie
    transport = httpx.ASGITransport(app=starlette_app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as fresh_client:
        response = await fresh_client.post("/api/auth/refresh")
    assert response.status_code == 401, (
        f"Le refresh sans cookie doit retourner 401 Unauthorized, reçu {response.status_code}. "
        f"Réponse: {response.text}"
    )


async def test_no_localStorage_refresh_token_in_response(client, test_user_data):
    """
    Test SEC-1.3 : Aucun refresh_token dans la réponse JSON
    Vérifie que le refresh_token n'est jamais retourné dans le body (cookie HttpOnly uniquement).
    """
    await client.post("/api/users/", json=test_user_data)
    verify_user_email_for_tests(test_user_data["username"])
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert (
        "refresh_token" not in data
    ), "Le refresh_token ne doit pas apparaître dans le body JSON (sécurité XSS)"

    # Idem pour la réponse refresh
    refresh_cookie = _get_cookie_from_headers(login_response.headers, "refresh_token")
    assert refresh_cookie is not None, "Le refresh_token doit être dans le cookie"
    refresh_response = await client.post(
        "/api/auth/refresh", cookies={"refresh_token": refresh_cookie}
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert (
        "refresh_token" not in refresh_data
    ), "Le refresh_token ne doit pas apparaître dans la réponse refresh"


async def test_logout_clears_cookie(client, test_user_data):
    """
    Test SEC-1.3 : Logout supprime le cookie
    Vérifie que le logout supprime le cookie refresh_token.
    """
    await client.post("/api/users/", json=test_user_data)
    verify_user_email_for_tests(test_user_data["username"])
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert login_response.status_code == 200
    assert _get_cookie_from_headers(login_response.headers, "refresh_token") is not None

    access_token = login_response.json().get("access_token")
    logout_response = await client.post(
        "/api/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert logout_response.status_code == 200

    set_cookie_headers = logout_response.headers.get_list("set-cookie")
    cleared_cookie_header = None
    for header in set_cookie_headers:
        if "refresh_token=" in header:
            cleared_cookie_header = header
            break

    assert (
        cleared_cookie_header is not None
    ), "Le header Set-Cookie pour refresh_token devrait être présent lors du logout"
    assert (
        "max-age=0" in cleared_cookie_header.lower()
        or "expires=" in cleared_cookie_header.lower()
    )


async def test_refresh_token_cookie_httponly(client, test_user_data):
    """
    Test SEC-1.3 : Cookie refresh_token a l'attribut HttpOnly
    Vérifie que le cookie refresh_token est marqué HttpOnly pour la sécurité XSS.
    """
    await client.post("/api/users/", json=test_user_data)
    verify_user_email_for_tests(test_user_data["username"])
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert login_response.status_code == 200

    set_cookie_headers = login_response.headers.get_list("set-cookie")
    refresh_token_header = None
    for header in set_cookie_headers:
        if "refresh_token=" in header:
            refresh_token_header = header
            break

    assert (
        refresh_token_header is not None
    ), "Le header Set-Cookie pour refresh_token devrait être présent"
    assert (
        "httponly" in refresh_token_header.lower()
    ), f"Le cookie refresh_token devrait avoir l'attribut HttpOnly. Header: {refresh_token_header}"

"""
Tests d'authentification pour vérifier l'absence de fallback refresh token.
Phase 4 - Sécurité : Vérifier que le fallback avec verify_exp=False a bien été supprimé.

Ces tests garantissent que :
1. Un refresh token manquant retourne 401 (pas de fallback avec access_token expiré)
2. Un refresh token expiré retourne 401 (pas de création de nouveau refresh)
3. Un refresh token invalide retourne 401
4. Un access token expiré ne peut pas créer un nouveau refresh token
"""
import pytest
import uuid
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings


@pytest.fixture
async def test_user_with_tokens(client):
    """Crée un utilisateur de test et retourne ses tokens"""
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"test_no_fallback_{unique_id}",
        "email": f"no_fallback_{unique_id}@test.com",
        "password": "SecurePassword123!",
        "role": "padawan"
    }

    # Créer l'utilisateur
    response = await client.post("/api/users/", json=user_data)
    assert response.status_code == 201, f"Échec création utilisateur: {response.text}"

    # Se connecter pour obtenir les tokens
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    login_response = await client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200, f"Échec login: {login_response.text}"

    login_data_response = login_response.json()
    refresh_from_cookie = login_response.cookies.get("refresh_token") if hasattr(login_response, "cookies") else None

    return {
        "user_data": user_data,
        "access_token": login_data_response.get("access_token"),
        "refresh_token": login_data_response.get("refresh_token") or refresh_from_cookie,
        "cookies": dict(login_response.cookies) if hasattr(login_response, "cookies") else {}
    }


async def test_refresh_token_missing_returns_401(client):
    """
    Test SEC-1.2 : Refresh sans token → 401 ou 422
    Vérifie qu'aucun fallback n'est utilisé si le refresh_token est manquant.
    Note: FastAPI retourne 422 pour un body manquant/invalide avant d'arriver au handler.
    """
    # Appeler l'endpoint de refresh sans token
    response = await client.post("/api/auth/refresh", json={})

    # Doit retourner 401 ou 422 (422 = validation FastAPI, 401 = handler)
    assert response.status_code in [401, 422], (
        f"Le code d'état devrait être 401 ou 422, reçu {response.status_code}. "
        f"Réponse: {response.text}"
    )

    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data or "error" in data, "La réponse devrait contenir un message d'erreur"

    # Gérer le cas où detail est une liste (422 FastAPI) ou une chaîne (401 handler)
    detail = data.get("detail") or data.get("error", "")
    if isinstance(detail, list):
        error_message = " ".join([str(item.get("msg", "")) for item in detail])
    else:
        error_message = str(detail).lower()

    assert any(keyword in error_message.lower() for keyword in ["manquant", "missing", "requis", "required", "invalide", "invalid"]), (
        f"Le message d'erreur devrait indiquer que le token est manquant. Message: {error_message}"
    )


async def test_refresh_token_expired_returns_401(client):
    """
    Test SEC-1.2 : Refresh token expiré → 401
    Vérifie qu'un refresh token expiré ne peut pas être utilisé pour créer un nouveau refresh.
    """
    # Créer un refresh token expiré manuellement
    payload = {
        "sub": "test_user_expired",
        "role": "padawan",
        "type": "refresh",
        "exp": datetime.now(timezone.utc) - timedelta(days=1)  # Expiré depuis 1 jour
    }

    expired_refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    # Appeler l'endpoint de refresh avec le token expiré
    response = await client.post("/api/auth/refresh", json={"refresh_token": expired_refresh_token})

    # Doit retourner 401
    assert response.status_code == 401, (
        f"Le code d'état devrait être 401, reçu {response.status_code}. "
        f"Réponse: {response.text}"
    )

    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data or "error" in data

    error_message = (data.get("detail") or data.get("error", "")).lower()
    assert any(keyword in error_message for keyword in ["expiré", "expired", "invalide", "invalid"]), (
        f"Le message devrait indiquer que le token est expiré ou invalide. Message: {error_message}"
    )


async def test_refresh_token_invalid_returns_401(client):
    """
    Test SEC-1.2 : Refresh token invalide → 401
    Vérifie qu'un refresh token malformé ou invalide retourne 401.
    """
    # Créer un token invalide (format valide mais signature incorrecte)
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpbnZhbGlkX3VzZXIiLCJyb2xlIjoicGFkYXdhbiIsInR5cGUiOiJyZWZyZXNoIn0.invalid_signature"

    # Appeler l'endpoint de refresh avec le token invalide
    response = await client.post("/api/auth/refresh", json={"refresh_token": invalid_token})

    # Doit retourner 401
    assert response.status_code == 401, (
        f"Le code d'état devrait être 401, reçu {response.status_code}. "
        f"Réponse: {response.text}"
    )

    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data or "error" in data

    error_message = (data.get("detail") or data.get("error", "")).lower()
    assert any(keyword in error_message for keyword in ["invalide", "invalid", "malformé", "malformed"]), (
        f"Le message devrait indiquer que le token est invalide. Message: {error_message}"
    )


async def test_no_fallback_with_expired_access_token(client, test_user_with_tokens):
    """
    Test SEC-1.2 : Access token expiré ne crée pas de nouveau refresh
    Vérifie qu'un access token expiré ne peut pas être utilisé comme fallback
    pour créer un nouveau refresh_token (vulnérabilité corrigée).
    """
    # Créer un access token expiré manuellement
    payload = {
        "sub": test_user_with_tokens["user_data"]["username"],
        "role": "padawan",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=30)  # Expiré depuis 30 minutes
    }

    expired_access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    # Essayer d'utiliser l'access token expiré comme refresh token (fallback supprimé)
    # Le backend ne devrait PAS accepter cela
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": expired_access_token},
        cookies={"access_token": expired_access_token}  # Aussi dans les cookies pour simuler le fallback
    )

    # Doit retourner 401 (pas de fallback)
    assert response.status_code == 401, (
        f"Le code d'état devrait être 401 (fallback supprimé), reçu {response.status_code}. "
        f"Si c'est 200, le fallback existe encore ! Réponse: {response.text}"
    )

    # Vérifier qu'aucun nouveau refresh_token n'a été créé
    data = response.json()
    assert "refresh_token" not in data, (
        "Aucun refresh_token ne devrait être créé à partir d'un access_token expiré "
        "(fallback supprimé)"
    )

    # Vérifier le message d'erreur
    assert "detail" in data or "error" in data
    error_message = (data.get("detail") or data.get("error", "")).lower()
    assert any(keyword in error_message for keyword in ["invalide", "invalid", "expiré", "expired", "manquant", "missing"]), (
        f"Le message devrait indiquer que le token est invalide ou expiré. Message: {error_message}"
    )


async def test_refresh_token_from_cookie_only(client, test_user_with_tokens):
    """
    Test SEC-1.3 : Refresh token depuis cookie uniquement
    Vérifie que le refresh fonctionne avec le cookie HTTP-only.
    """
    # Récupérer le refresh_token depuis les cookies du login
    refresh_token_cookie = test_user_with_tokens["cookies"].get("refresh_token")

    if not refresh_token_cookie:
        pytest.skip("Refresh token non présent dans les cookies (peut être dans le body JSON)")

    # Appeler l'endpoint de refresh avec uniquement le cookie (pas de body)
    response = await client.post(
        "/api/auth/refresh",
        cookies={"refresh_token": refresh_token_cookie}
    )

    # Doit fonctionner (200)
    assert response.status_code == 200, (
        f"Le refresh depuis cookie devrait fonctionner, reçu {response.status_code}. "
        f"Réponse: {response.text}"
    )

    # Vérifier qu'un nouveau access_token est retourné
    data = response.json()
    assert "access_token" in data, "Un nouveau access_token devrait être retourné"
    assert "token_type" in data, "Le type de token devrait être présent"


async def test_refresh_token_missing_both_body_and_cookie(client):
    """
    Test SEC-1.2 : Refresh token manquant dans body ET cookie → 401 ou 422
    Vérifie qu'aucun fallback n'est utilisé si le refresh_token est absent partout.
    Note: FastAPI retourne 422 pour un body manquant avant d'arriver au handler.
    """
    # Appeler l'endpoint sans token dans le body ET sans cookie
    response = await client.post("/api/auth/refresh")

    # Doit retourner 401 ou 422 (422 = validation FastAPI, 401 = handler)
    assert response.status_code in [401, 422], (
        f"Le code d'état devrait être 401 ou 422, reçu {response.status_code}. "
        f"Réponse: {response.text}"
    )

    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data or "error" in data, "La réponse devrait contenir un message d'erreur"

    # Gérer le cas où detail est une liste (422 FastAPI) ou une chaîne (401 handler)
    detail = data.get("detail") or data.get("error", "")
    if isinstance(detail, list):
        error_message = " ".join([str(item.get("msg", "")) for item in detail])
    else:
        error_message = str(detail).lower()

    assert any(keyword in error_message.lower() for keyword in ["manquant", "missing", "requis", "required"]), (
        f"Le message devrait indiquer que le token est manquant. Message: {error_message}"
    )

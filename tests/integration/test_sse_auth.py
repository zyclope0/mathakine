"""
Tests d'authentification pour les endpoints SSE (Server-Sent Events).
Phase 4 - Sécurité : Vérifier que les endpoints SSE nécessitent une authentification.

IA6 : corps JSON en POST (plus de paramètres de génération dans l'URL).

Ces tests garantissent que :
1. SSE sans authentification → 401 ou flux d'erreur SSE
2. SSE avec token valide → 200 (stream fonctionne)
3. Plusieurs connexions SSE simultanées fonctionnent
"""

import asyncio
import uuid

import pytest

from tests.utils.test_helpers import verify_user_email_for_tests

CHALLENGE_STREAM_JSON = {
    "challenge_type": "sequence",
    "age_group": "9-11",
    "prompt": "",
}
EXERCISE_STREAM_JSON = {"exercise_type": "addition", "age_group": "6-8", "prompt": ""}


@pytest.fixture
async def authenticated_user(client):
    """Crée un utilisateur authentifié et retourne ses tokens"""
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"test_sse_{unique_id}",
        "email": f"sse_{unique_id}@test.com",
        "password": "SecurePassword123!",
        "role": "padawan",
    }

    # Créer l'utilisateur
    response = await client.post("/api/users/", json=user_data)
    assert response.status_code == 201, f"Échec création utilisateur: {response.text}"
    verify_user_email_for_tests(user_data["username"])

    # Se connecter
    login_data = {"username": user_data["username"], "password": user_data["password"]}
    login_response = await client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200, f"Échec login: {login_response.text}"

    login_data_response = login_response.json()

    return {
        "user_data": user_data,
        "access_token": login_data_response.get("access_token"),
        "cookies": dict(login_response.cookies),
    }


async def test_sse_requires_authentication(client):
    """
    Test SEC-4.3 : SSE sans auth → 401
    Vérifie que l'endpoint SSE de génération de challenges nécessite une authentification.
    """
    response = await client.post(
        "/api/challenges/generate-ai-stream",
        json=CHALLENGE_STREAM_JSON,
    )

    if response.status_code == 401:
        assert True, "SSE correctement protégé par authentification (401)"
    else:
        assert (
            response.status_code == 200
        ), f"Le code d'état devrait être 200 (stream) ou 401, reçu {response.status_code}"

        content = response.text
        assert (
            "error" in content.lower()
            or "non authentifié" in content.lower()
            or "unauthorized" in content.lower()
        ), f"Le stream devrait contenir une erreur d'authentification. Contenu: {content[:200]}"


async def test_sse_with_valid_token(client, authenticated_user):
    """
    Test SEC-4.3 : SSE avec token valide → 200
    Vérifie que l'endpoint SSE fonctionne avec un token valide.
    """
    access_token = authenticated_user["access_token"]
    assert access_token is not None, "Le token d'accès devrait être présent"

    response = await client.post(
        "/api/challenges/generate-ai-stream",
        json=CHALLENGE_STREAM_JSON,
        headers={"Authorization": f"Bearer {access_token}"},
        cookies=authenticated_user["cookies"],
    )

    assert response.status_code == 200, (
        f"Le SSE avec token valide devrait retourner 200, reçu {response.status_code}. "
        f"Réponse: {response.text[:500]}"
    )

    content_type = response.headers.get("content-type", "")
    assert (
        "text/event-stream" in content_type or "event-stream" in content_type.lower()
    ), f"Le Content-Type devrait être text/event-stream, reçu {content_type}"


async def test_sse_with_cookie_auth(client, authenticated_user):
    """
    Test SEC-4.3 : SSE avec authentification par cookie
    Vérifie que l'endpoint SSE fonctionne avec les cookies HTTP-only.
    """
    response = await client.post(
        "/api/challenges/generate-ai-stream",
        json=CHALLENGE_STREAM_JSON,
        cookies=authenticated_user["cookies"],
    )

    assert response.status_code == 200, (
        f"Le SSE avec cookie devrait retourner 200, reçu {response.status_code}. "
        f"Réponse: {response.text[:500]}"
    )


async def test_sse_with_invalid_token(client):
    """
    Test SEC-4.3 : SSE avec token invalide → 401 ou erreur
    Vérifie que l'endpoint SSE rejette un token invalide.
    """
    invalid_token = "invalid_token_xyz123"

    response = await client.post(
        "/api/challenges/generate-ai-stream",
        json=CHALLENGE_STREAM_JSON,
        headers={"Authorization": f"Bearer {invalid_token}"},
    )

    if response.status_code == 401:
        assert True, "SSE correctement protégé (401 avec token invalide)"
    else:
        assert (
            response.status_code == 200
        ), f"Le code d'état devrait être 200 (stream) ou 401, reçu {response.status_code}"
        content = response.text
        assert (
            "error" in content.lower()
            or "invalide" in content.lower()
            or "invalid" in content.lower()
        ), f"Le stream devrait contenir une erreur. Contenu: {content[:200]}"


async def test_sse_exercises_requires_auth(client):
    """
    Test SEC-4.3 : SSE exercices nécessite authentification
    Vérifie que l'endpoint SSE de génération d'exercices nécessite aussi une authentification.
    """
    response = await client.post(
        "/api/exercises/generate-ai-stream",
        json=EXERCISE_STREAM_JSON,
    )

    if response.status_code == 401:
        assert True, "SSE exercices correctement protégé par authentification (401)"
    else:
        assert (
            response.status_code == 200
        ), f"Le code d'état devrait être 200 (stream) ou 401, reçu {response.status_code}"
        content = response.text
        assert (
            "error" in content.lower()
            or "non authentifié" in content.lower()
            or "unauthorized" in content.lower()
        ), f"Le stream devrait contenir une erreur d'authentification. Contenu: {content[:200]}"


async def test_sse_exercises_with_valid_token(client, authenticated_user):
    """
    Test SEC-4.3 : SSE exercices avec token valide → 200
    Vérifie que l'endpoint SSE d'exercices fonctionne avec un token valide.
    """
    access_token = authenticated_user["access_token"]

    response = await client.post(
        "/api/exercises/generate-ai-stream",
        json=EXERCISE_STREAM_JSON,
        headers={"Authorization": f"Bearer {access_token}"},
        cookies=authenticated_user["cookies"],
    )

    assert (
        response.status_code == 200
    ), f"Le SSE exercices avec token valide devrait retourner 200, reçu {response.status_code}"

    content_type = response.headers.get("content-type", "")
    assert (
        "text/event-stream" in content_type or "event-stream" in content_type.lower()
    ), f"Le Content-Type devrait être text/event-stream, reçu {content_type}"


async def test_sse_multiple_connections(client, authenticated_user):
    """
    Test SEC-4.3 : Plusieurs connexions SSE simultanées
    Vérifie que plusieurs connexions SSE simultanées fonctionnent correctement.
    Utilise asyncio.gather pour lancer 3 requêtes SSE en parallèle.
    """
    url = "/api/challenges/generate-ai-stream"
    headers = {"Authorization": f"Bearer {authenticated_user['access_token']}"}
    cookies = authenticated_user.get("cookies") or {}

    async def open_sse_and_verify():
        async with client.stream(
            "POST",
            url,
            json=CHALLENGE_STREAM_JSON,
            headers=headers,
            cookies=cookies,
        ) as resp:
            chunks = []
            async for chunk in resp.aiter_bytes():
                chunks.append(chunk)
                if len(chunks) >= 1:
                    break
            return resp.status_code, resp.headers.get("content-type", "")

    results = await asyncio.gather(
        open_sse_and_verify(),
        open_sse_and_verify(),
        open_sse_and_verify(),
    )

    for status, content_type in results:
        assert status == 200, f"Attendu 200, reçu {status}"
        assert (
            "text/event-stream" in (content_type or "")
            or "event-stream" in (content_type or "").lower()
        ), f"Content-Type attendu text/event-stream, reçu: {content_type}"

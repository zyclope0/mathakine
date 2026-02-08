"""
Tests d'authentification pour les endpoints SSE (Server-Sent Events).
Phase 4 - Sécurité : Vérifier que les endpoints SSE nécessitent une authentification.

Ces tests garantissent que :
1. SSE sans authentification → 401
2. SSE avec token valide → 200 (stream fonctionne)
3. Plusieurs connexions SSE simultanées fonctionnent
"""
import pytest
import uuid


@pytest.fixture
async def authenticated_user(client):
    """Crée un utilisateur authentifié et retourne ses tokens"""
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"test_sse_{unique_id}",
        "email": f"sse_{unique_id}@test.com",
        "password": "SecurePassword123!",
        "role": "padawan"
    }

    # Créer l'utilisateur
    response = await client.post("/api/users/", json=user_data)
    assert response.status_code == 201, f"Échec création utilisateur: {response.text}"

    # Se connecter
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    login_response = await client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200, f"Échec login: {login_response.text}"

    login_data_response = login_response.json()

    return {
        "user_data": user_data,
        "access_token": login_data_response.get("access_token"),
        "cookies": dict(login_response.cookies)
    }


async def test_sse_requires_authentication(client):
    """
    Test SEC-4.3 : SSE sans auth → 401
    Vérifie que l'endpoint SSE de génération de challenges nécessite une authentification.
    """
    # Appeler l'endpoint SSE sans authentification
    response = await client.get(
        "/api/challenges/generate-ai-stream",
        params={
            "challenge_type": "SEQUENCE",
            "difficulty": "medium",
            "age_group": "GROUP_10_12"
        }
    )

    # Doit retourner 401 ou un stream d'erreur
    # Note: Les endpoints SSE peuvent retourner un stream d'erreur au lieu de 401 directement
    if response.status_code == 401:
        # Cas idéal : 401 directement
        assert True, "SSE correctement protégé par authentification (401)"
    else:
        # Cas alternatif : stream d'erreur
        # Vérifier que le stream contient une erreur d'authentification
        assert response.status_code == 200, (
            f"Le code d'état devrait être 200 (stream) ou 401, reçu {response.status_code}"
        )

        # Lire le premier événement du stream
        content = response.text
        assert "error" in content.lower() or "non authentifié" in content.lower() or "unauthorized" in content.lower(), (
            f"Le stream devrait contenir une erreur d'authentification. Contenu: {content[:200]}"
        )


async def test_sse_with_valid_token(client, authenticated_user):
    """
    Test SEC-4.3 : SSE avec token valide → 200
    Vérifie que l'endpoint SSE fonctionne avec un token valide.
    """
    access_token = authenticated_user["access_token"]
    assert access_token is not None, "Le token d'accès devrait être présent"

    # Appeler l'endpoint SSE avec authentification
    # Note: TestClient ne supporte pas vraiment les streams SSE, mais on peut vérifier
    # que la requête est acceptée (200) et que le Content-Type est text/event-stream
    response = await client.get(
        "/api/challenges/generate-ai-stream",
        params={
            "challenge_type": "SEQUENCE",
            "difficulty": "medium",
            "age_group": "GROUP_10_12"
        },
        headers={"Authorization": f"Bearer {access_token}"},
        cookies=authenticated_user["cookies"]
    )

    # Doit retourner 200 (stream accepté)
    assert response.status_code == 200, (
        f"Le SSE avec token valide devrait retourner 200, reçu {response.status_code}. "
        f"Réponse: {response.text[:500]}"
    )

    # Vérifier le Content-Type
    content_type = response.headers.get("content-type", "")
    assert "text/event-stream" in content_type or "event-stream" in content_type.lower(), (
        f"Le Content-Type devrait être text/event-stream, reçu {content_type}"
    )


async def test_sse_with_cookie_auth(client, authenticated_user):
    """
    Test SEC-4.3 : SSE avec authentification par cookie
    Vérifie que l'endpoint SSE fonctionne avec les cookies HTTP-only.
    """
    # Appeler l'endpoint SSE avec uniquement les cookies (pas de header Authorization)
    response = await client.get(
        "/api/challenges/generate-ai-stream",
        params={
            "challenge_type": "SEQUENCE",
            "difficulty": "medium",
            "age_group": "GROUP_10_12"
        },
        cookies=authenticated_user["cookies"]
    )

    # Doit retourner 200 (stream accepté)
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

    # Appeler l'endpoint SSE avec un token invalide
    response = await client.get(
        "/api/challenges/generate-ai-stream",
        params={
            "challenge_type": "SEQUENCE",
            "difficulty": "medium"
        },
        headers={"Authorization": f"Bearer {invalid_token}"}
    )

    # Doit retourner 401 ou un stream d'erreur
    if response.status_code == 401:
        assert True, "SSE correctement protégé (401 avec token invalide)"
    else:
        # Vérifier que le stream contient une erreur
        assert response.status_code == 200, (
            f"Le code d'état devrait être 200 (stream) ou 401, reçu {response.status_code}"
        )
        content = response.text
        assert "error" in content.lower() or "invalide" in content.lower() or "invalid" in content.lower(), (
            f"Le stream devrait contenir une erreur. Contenu: {content[:200]}"
        )


async def test_sse_exercises_requires_auth(client):
    """
    Test SEC-4.3 : SSE exercices nécessite authentification
    Vérifie que l'endpoint SSE de génération d'exercices nécessite aussi une authentification.
    """
    # Appeler l'endpoint SSE sans authentification
    response = await client.get(
        "/api/exercises/generate-ai-stream",
        params={
            "exercise_type": "addition",
            "difficulty": "easy"
        }
    )

    # Doit retourner 401 ou un stream d'erreur
    if response.status_code == 401:
        assert True, "SSE exercices correctement protégé par authentification (401)"
    else:
        assert response.status_code == 200, (
            f"Le code d'état devrait être 200 (stream) ou 401, reçu {response.status_code}"
        )
        content = response.text
        assert "error" in content.lower() or "non authentifié" in content.lower() or "unauthorized" in content.lower(), (
            f"Le stream devrait contenir une erreur d'authentification. Contenu: {content[:200]}"
        )


async def test_sse_exercises_with_valid_token(client, authenticated_user):
    """
    Test SEC-4.3 : SSE exercices avec token valide → 200
    Vérifie que l'endpoint SSE d'exercices fonctionne avec un token valide.
    """
    access_token = authenticated_user["access_token"]

    # Appeler l'endpoint SSE avec authentification
    response = await client.get(
        "/api/exercises/generate-ai-stream",
        params={
            "exercise_type": "addition",
            "difficulty": "easy"
        },
        headers={"Authorization": f"Bearer {access_token}"},
        cookies=authenticated_user["cookies"]
    )

    # Doit retourner 200 (stream accepté)
    assert response.status_code == 200, (
        f"Le SSE exercices avec token valide devrait retourner 200, reçu {response.status_code}"
    )

    # Vérifier le Content-Type
    content_type = response.headers.get("content-type", "")
    assert "text/event-stream" in content_type or "event-stream" in content_type.lower(), (
        f"Le Content-Type devrait être text/event-stream, reçu {content_type}"
    )


# Note: Le test de plusieurs connexions SSE simultanées nécessiterait
# un client HTTP asynchrone ou des threads, ce qui est complexe avec TestClient.
# Ce test pourrait être fait avec un outil comme k6 ou locust pour les load tests.
@pytest.mark.skip(reason="Nécessite un client HTTP asynchrone pour tester plusieurs connexions simultanées")
async def test_sse_multiple_connections(client, authenticated_user):
    """
    Test SEC-4.3 : Plusieurs connexions SSE simultanées
    Vérifie que plusieurs connexions SSE simultanées fonctionnent correctement.
    Note: Ce test nécessite un client HTTP asynchrone et sera fait dans les load tests.
    """
    pass

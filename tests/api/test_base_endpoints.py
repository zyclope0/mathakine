"""
Tests des endpoints de base de l'API Starlette.
Verifie la sante de l'application, le routage et les reponses d'erreur.

Routes testees :
- GET /health
- GET /robots.txt
- GET /api/exercises (route publique, whitelist deny-by-default)
- GET /api/challenges (requiert auth → 401)
- GET /nonexistent (404)
- GET /api/auth/login (methode GET non autorisee → 405)
"""

import pytest


async def test_health_endpoint(client):
    """GET /health — health check pour Render et load balancers (stable)."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.text.strip() == "ok"


async def test_request_id_header(client):
    """X-Request-ID — corrélation logs/Sentry (RequestIdMiddleware)."""
    response = await client.get("/health")
    rid = response.headers.get("X-Request-ID")
    assert rid is not None
    assert len(rid) >= 8  # UUID court ou header client


async def test_robots_txt(client):
    """GET /robots.txt — évite les 404 des crawlers (stable)."""
    response = await client.get("/robots.txt")
    assert response.status_code == 200
    content = response.text
    assert "User-agent" in content or "user-agent" in content.lower()
    assert "Disallow" in content or "disallow" in content.lower()


async def test_csrf_token_endpoint(client):
    """GET /api/auth/csrf — retourne un token CSRF (stable, pas d'auth)."""
    response = await client.get("/api/auth/csrf")
    assert response.status_code == 200
    data = response.json()
    assert "csrf_token" in data
    assert isinstance(data["csrf_token"], str)
    assert len(data["csrf_token"]) > 0


async def test_nonexistent_endpoint(client):
    """Test qu'un endpoint inexistant retourne 404 avec le schéma d'erreur unifié."""
    response = await client.get("/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert data.get("code") == "NOT_FOUND"
    assert "message" in data
    assert data.get("path") == "/nonexistent"


async def test_exercises_public_without_auth(client):
    """GET /api/exercises — route publique (whitelist deny-by-default), accessible sans token."""
    response = await client.get("/api/exercises")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data or "exercises" in data
    assert "total" in data


async def test_challenges_requires_auth(client):
    """Test que /api/challenges requiert une authentification (401)."""
    response = await client.get("/api/challenges")
    assert response.status_code == 401
    data = response.json()
    assert "error" in data


async def test_api_auth_login_get_not_allowed(client):
    """Test que GET /api/auth/login est refusé (405 ou 401 selon middleware deny-by-default)."""
    response = await client.get("/api/auth/login")
    # 401 : middleware bloque (whitelist POST only) ; 405 : route atteinte, méthode non autorisée
    assert response.status_code in (401, 405)


async def test_api_auth_login_post_missing_body(client):
    """Test que POST /api/auth/login sans body retourne une erreur."""
    response = await client.post("/api/auth/login")
    # Starlette retourne 400 (JSON invalide) ou 500
    assert response.status_code in (400, 422, 500)


async def test_api_users_post_endpoint_exists(client):
    """Test que POST /api/users/ est accessible (creation de compte public)."""
    # Envoyer un body invalide pour verifier que la route existe
    response = await client.post("/api/users/", json={})
    # Doit retourner une erreur de validation, pas 404
    assert response.status_code != 404, "La route /api/users/ devrait exister"
    # 400 ou 500 attendu (champs manquants)
    assert response.status_code in (400, 422, 500)

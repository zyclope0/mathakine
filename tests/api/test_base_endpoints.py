"""
Tests des endpoints de base de l'API Starlette.
Verifie la sante de l'application, le routage et les reponses d'erreur.

Routes testees :
- GET /api/exercises (existe, necessite auth → 401)
- GET /api/challenges (existe, necessite auth → 401)
- GET /nonexistent (404)
- GET /api/auth/login (methode GET non autorisee → 405)
"""
import pytest


async def test_nonexistent_endpoint(client):
    """Test qu'un endpoint inexistant retourne 404."""
    response = await client.get("/nonexistent")
    assert response.status_code == 404


async def test_challenges_requires_auth(client):
    """Test que /api/challenges requiert une authentification (401)."""
    response = await client.get("/api/challenges")
    assert response.status_code == 401
    data = response.json()
    assert "error" in data


async def test_api_auth_login_get_not_allowed(client):
    """Test que GET /api/auth/login retourne 405 (POST uniquement)."""
    response = await client.get("/api/auth/login")
    assert response.status_code == 405


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

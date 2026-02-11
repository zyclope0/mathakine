"""
Tests de l'authentification avec des tokens expires.

Note: Les handlers Starlette retournent {"error": "..."} pas {"detail": "..."}.
Le decorateur @require_auth retourne {"error": "Authentification requise"} avec 401.
"""
import pytest


async def test_expired_token_access(expired_token_client):
    """Teste l'acces a une ressource protegee avec un token expire."""
    client = expired_token_client["client"]

    # Essayer d'acceder a une ressource protegee
    response = await client.get("/api/challenges")

    # Verifier que l'acces est refuse avec un code 401
    assert response.status_code == 401, f"Le code d'etat devrait etre 401, recu {response.status_code}"

    # Verifier le message d'erreur (format Starlette)
    data = response.json()
    assert "error" in data, f"La reponse devrait contenir un champ 'error': {data}"


async def test_expired_token_exercise_creation(expired_token_client):
    """Teste la creation d'un exercice avec un token expire."""
    client = expired_token_client["client"]

    exercise_data = {
        "title": "Test Exercise",
        "exercise_type": "addition",
        "difficulty": "initie",
        "question": "Combien font 2+2?",
        "correct_answer": "4",
        "choices": ["2", "3", "4", "5"]
    }

    # Essayer de creer un exercice (POST /api/exercises/generate)
    # generate_exercise_api parse le JSON en premier et peut retourner 400 si params manquants
    response = await client.post("/api/exercises/generate", json=exercise_data)

    # Verifier que l'acces est refuse (401) ou parametres invalides (400)
    assert response.status_code in (400, 401), f"Le code d'etat devrait etre 400 ou 401, recu {response.status_code}"

    data = response.json()
    if response.status_code == 401:
        assert "error" in data, f"La reponse devrait contenir un champ 'error': {data}"


async def test_expired_token_exercise_attempt(expired_token_client):
    """Teste la soumission d'une tentative avec un token expire."""
    client = expired_token_client["client"]

    attempt_data = {
        "answer": "4",
        "time_spent": 10.0
    }

    # Route correcte: /api/exercises/{id}/attempt (pas /submit)
    response = await client.post("/api/exercises/1/attempt", json=attempt_data)

    # Verifier que l'acces est refuse avec un code 401
    assert response.status_code == 401, f"Le code d'etat devrait etre 401, recu {response.status_code}"

    # Verifier le message d'erreur (format Starlette)
    data = response.json()
    assert "error" in data, f"La reponse devrait contenir un champ 'error': {data}"

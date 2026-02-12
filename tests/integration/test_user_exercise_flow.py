import json
"""
Tests d'intégration pour le flux d'utilisateur-exercice
"""
import pytest
import uuid
from datetime import datetime, timezone
import logging

from tests.utils.test_helpers import verify_user_email_for_tests

logger = logging.getLogger(__name__)


async def test_user_exercise_flow(client):
    """Test du flux complet utilisateur-exercice"""
    # Générer des identifiants uniques pour éviter les conflits
    unique_id = uuid.uuid4().hex[:8]

    # 1. Création d'un utilisateur
    user_data = {
        "username": f"test_flow_user_{unique_id}",
        "email": f"padawan_{unique_id}@jedi.com",
        "password": "Force123Jedi",
        "role": "padawan"
    }

    try:
        response = await client.post("/api/users/", json=user_data)
        assert response.status_code == 201, f"Erreur lors de la création de l'utilisateur: {response.text}"
        verify_user_email_for_tests(user_data["username"])
        user_response = response.json()
        assert "id" in user_response, "L'ID de l'utilisateur est manquant dans la réponse"
        user_id = user_response["id"]

        # 2. Authentification de l'utilisateur
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200, f"Erreur d'authentification: {response.text}"
        token_response = response.json()
        assert "access_token" in token_response, "Le token d'accès est manquant dans la réponse"

        # 3. Création d'un exercice via POST /api/exercises/generate (endpoint disponible)
        headers = {"Authorization": f"Bearer {token_response['access_token']}"}
        generate_data = {
            "exercise_type": "addition",
            "age_group": "6-8",
            "save": True
        }
        response = await client.post("/api/exercises/generate", json=generate_data, headers=headers)
        assert response.status_code in [200, 201], f"Erreur lors de la génération de l'exercice: {response.text}"
        exercise_response = response.json()
        assert "id" in exercise_response, "L'ID de l'exercice est manquant dans la réponse"
        exercise_id = exercise_response["id"]

        # 4. Soumission d'une tentative pour l'exercice (answer/selected_answer requis)
        attempt_data = {
            "answer": exercise_response.get("correct_answer", "5"),
            "time_spent": 15
        }
        response = await client.post(f"/api/exercises/{exercise_id}/attempt", json=attempt_data, headers=headers)
        assert response.status_code == 200, f"Erreur lors de la soumission de la tentative: {response.text}"
        attempt_response = response.json()
        assert attempt_response["is_correct"] is True, "La tentative devrait être correcte"

        # 5. Vérification des statistiques de l'utilisateur (stats du user connecté)
        response = await client.get("/api/users/stats", headers=headers)
        assert response.status_code == 200, f"Erreur lors de la récupération des statistiques: {response.text}"
        stats_response = response.json()
        # L'API retourne total_exercises (exercices tentés) ou total_attempts selon le format
        total_key = next(
            (k for k in ["total_exercises", "total_attempts", "total_exercises_attempted"] if k in stats_response),
            None
        )
        assert total_key, f"Les statistiques de tentatives sont manquantes: {list(stats_response.keys())}"
        assert stats_response[total_key] >= 1, "Le nombre de tentatives devrait être d'au moins 1"

    except AssertionError as ae:
        pytest.fail(f"Test échoué: {str(ae)}")
    except Exception as e:
        pytest.fail(f"Exception non gérée: {str(e)}")


async def test_invalid_exercise_attempt(client):
    """Test d'une tentative invalide sur un exercice"""
    # Générer des identifiants uniques pour éviter les conflits
    unique_id = uuid.uuid4().hex[:8]

    try:
        # Création d'un utilisateur
        user_data = {
            "username": f"test_invalid_user_{unique_id}",
            "email": f"padawan2_{unique_id}@jedi.com",
            "password": "Force123Jedi",
            "role": "padawan"
        }
        response = await client.post("/api/users/", json=user_data)
        assert response.status_code == 201, f"Erreur lors de la création de l'utilisateur: {response.text}"
        verify_user_email_for_tests(user_data["username"])
        user_response = response.json()
        user_id = user_response["id"]

        # Authentification de l'utilisateur
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200, f"Erreur d'authentification: {response.text}"
        token_response = response.json()

        # Tentative d'accès à un exercice inexistant (answer/selected_answer requis)
        headers = {"Authorization": f"Bearer {token_response['access_token']}"}
        attempt_data = {
            "answer": "42",
            "time_spent": 30
        }
        response = await client.post("/api/exercises/99999/attempt", json=attempt_data, headers=headers)
        assert response.status_code == 404, f"Une tentative sur un exercice inexistant devrait retourner 404, mais a retourné {response.status_code}: {response.text}"

        # Création d'un exercice via POST /api/exercises/generate
        generate_data = {
            "exercise_type": "addition",
            "age_group": "6-8",
            "save": True
        }
        response = await client.post("/api/exercises/generate", json=generate_data, headers=headers)
        assert response.status_code in [200, 201], f"Erreur lors de la génération de l'exercice: {response.text}"
        exercise_id = response.json()["id"]

        # Maintenant soumettre une réponse incorrecte (answer requis)
        bad_attempt_data = {
            "answer": "5",  # Réponse incorrecte (correct_answer est 4)
            "time_spent": 10
        }
        response = await client.post(f"/api/exercises/{exercise_id}/attempt", json=bad_attempt_data, headers=headers)
        assert response.status_code == 200, f"Erreur lors de la soumission de la tentative incorrecte: {response.text}"
        result = response.json()
        assert result["is_correct"] is False, "La tentative avec une réponse incorrecte devrait être marquée comme incorrecte"

    except AssertionError as ae:
        pytest.fail(f"Test échoué: {str(ae)}")
    except Exception as e:
        pytest.fail(f"Exception non gérée: {str(e)}")

import json
"""
Tests d'intégration pour le flux d'utilisateur-exercice
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db_helpers import get_enum_value
import uuid
from datetime import datetime, timezone
import logging

client = TestClient(app)
logger = logging.getLogger(__name__)


def test_user_exercise_flow():
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
        response = client.post("/api/users/", json=user_data)
        assert response.status_code == 201, f"Erreur lors de la création de l'utilisateur: {response.text}"
        user_response = response.json()
        assert "id" in user_response, "L'ID de l'utilisateur est manquant dans la réponse"
        user_id = user_response["id"]

        # 2. Authentification de l'utilisateur
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200, f"Erreur d'authentification: {response.text}"
        token_response = response.json()
        assert "access_token" in token_response, "Le token d'accès est manquant dans la réponse"
        
        # 3. Création d'un exercice
        headers = {"Authorization": f"Bearer {token_response['access_token']}"}
        current_time = datetime.now(timezone.utc).isoformat()
        exercise_data = {
            "title": f"Test Flow Exercise {unique_id}",
            "exercise_type": "addition",
            "difficulty": "initie",
            "question": "2 + 3 = ?",
            "correct_answer": "5",
            "choices": ["3", "4", "5", "6"]
        }
        
        # Simplifier les données d'exercice pour éviter les champs non nécessaires
        # Dans le cas où le service attendrait uniquement les champs requis
        response = client.post("/api/exercises/", json=exercise_data, headers=headers)
        # Afficher le corps de la réponse en cas d'échec
        if response.status_code not in [200, 201]:
            logger.error(f"Erreur de création d'exercice: {response.text}")
            # Tester une version alternative des données d'exercice
            exercise_data_alt = {
                "title": f"Test Flow Exercise {unique_id}",
                "exercise_type": "addition",
                "difficulty": "initie",
                "question": "2 + 3 = ?",
                "correct_answer": "5",
                "choices": ["3", "4", "5", "6"],
                "creator_id": user_id
            }
            response = client.post("/api/exercises/", json=exercise_data_alt, headers=headers)
            
        assert response.status_code in [200, 201], f"Erreur lors de la création de l'exercice: {response.text}"
        exercise_response = response.json()
        assert "id" in exercise_response, "L'ID de l'exercice est manquant dans la réponse"
        exercise_id = exercise_response["id"]
        
        # 4. Soumission d'une tentative pour l'exercice
        attempt_data = {
            "user_answer": "5",
            "time_spent": 15
        }
        response = client.post(f"/api/exercises/{exercise_id}/attempt", json=attempt_data, headers=headers)
        assert response.status_code == 200, f"Erreur lors de la soumission de la tentative: {response.text}"
        attempt_response = response.json()
        assert attempt_response["is_correct"] is True, "La tentative devrait être correcte"
        
        # 5. Vérification des statistiques de l'utilisateur
        response = client.get(f"/api/users/{user_id}/stats", headers=headers)
        assert response.status_code == 200, f"Erreur lors de la récupération des statistiques: {response.text}"
        stats_response = response.json()
        assert "total_exercises_attempted" in stats_response, "Les statistiques de tentatives sont manquantes"
        assert stats_response["total_exercises_attempted"] >= 1, "Le nombre de tentatives devrait être d'au moins 1"
        
    except AssertionError as ae:
        pytest.fail(f"Test échoué: {str(ae)}")
    except Exception as e:
        pytest.fail(f"Exception non gérée: {str(e)}")


def test_invalid_exercise_attempt():
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
        response = client.post("/api/users/", json=user_data)
        assert response.status_code == 201, f"Erreur lors de la création de l'utilisateur: {response.text}"
        user_response = response.json()
        user_id = user_response["id"]
        
        # Authentification de l'utilisateur
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200, f"Erreur d'authentification: {response.text}"
        token_response = response.json()
        
        # Tentative d'accès à un exercice inexistant
        headers = {"Authorization": f"Bearer {token_response['access_token']}"}
        attempt_data = {
            "user_answer": "42",
            "time_spent": 30
        }
        response = client.post("/api/exercises/99999/attempt", json=attempt_data, headers=headers)
        assert response.status_code == 404, f"Une tentative sur un exercice inexistant devrait retourner 404, mais a retourné {response.status_code}: {response.text}"
        
        # Création d'un exercice pour test
        exercise_data = {
            "title": f"Invalid Test Exercise {unique_id}",
            "exercise_type": "addition",
            "difficulty": "initie",
            "question": "2 + 2 = ?",
            "correct_answer": "4",
            "choices": ["3", "4", "5", "6"]
        }
        
        response = client.post("/api/exercises/", json=exercise_data, headers=headers)
        # Afficher le corps de la réponse en cas d'échec
        if response.status_code not in [200, 201]:
            logger.error(f"Erreur de création d'exercice: {response.text}")
            # Tenter avec l'ID utilisateur
            exercise_data["creator_id"] = user_id
            response = client.post("/api/exercises/", json=exercise_data, headers=headers)
            
        assert response.status_code in [200, 201], f"Erreur lors de la création de l'exercice: {response.text}"
        exercise_id = response.json()["id"]
        
        # Maintenant soumettre une réponse incorrecte
        bad_attempt_data = {
            "user_answer": "5",  # Réponse incorrecte
            "time_spent": 10
        }
        response = client.post(f"/api/exercises/{exercise_id}/attempt", json=bad_attempt_data, headers=headers)
        assert response.status_code == 200, f"Erreur lors de la soumission de la tentative incorrecte: {response.text}"
        result = response.json()
        assert result["is_correct"] is False, "La tentative avec une réponse incorrecte devrait être marquée comme incorrecte"
        
    except AssertionError as ae:
        pytest.fail(f"Test échoué: {str(ae)}")
    except Exception as e:
        pytest.fail(f"Exception non gérée: {str(e)}")

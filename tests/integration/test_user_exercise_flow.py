import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.exercise import Exercise
from app.models.attempt import Attempt
from datetime import datetime

client = TestClient(app)

def test_user_exercise_flow():
    """Test du flux complet utilisateur-exercice"""
    # 1. Création d'un utilisateur
    user_data = {
        "username": "test_padawan",
        "email": "padawan@jedi.com",
        "password": "Force123Jedi",
        "role": "padawan"
    }
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # 2. Authentification
    auth_data = {
        "username": "test_padawan",
        "password": "Force123Jedi"
    }
    response = client.post("/api/auth/login", json=auth_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Récupération des exercices disponibles
    response = client.get("/api/exercises/", headers=headers)
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) > 0
    
    # 4. Sélection d'un exercice
    exercise_id = exercises[0]["id"]
    response = client.get(f"/api/exercises/{exercise_id}", headers=headers)
    assert response.status_code == 200
    exercise = response.json()
    
    # 5. Soumission d'une réponse correcte
    answer_data = {
        "user_answer": exercise["correct_answer"]
    }
    response = client.post(
        f"/api/exercises/{exercise_id}/attempt",
        json=answer_data,
        headers=headers
    )
    assert response.status_code == 200
    attempt = response.json()
    assert attempt["is_correct"] is True
    
    # 6. Vérification de la progression
    response = client.get(f"/api/users/{user_id}/progress", headers=headers)
    assert response.status_code == 200
    progress = response.json()
    assert progress["total_attempts"] > 0
    assert progress["correct_attempts"] > 0
    
    # 7. Déconnexion
    response = client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 200
    
    # 8. Suppression du compte
    response = client.delete(f"/api/users/{user_id}", headers=headers)
    assert response.status_code == 204

def test_invalid_exercise_attempt():
    """Test d'une tentative invalide sur un exercice"""
    # Création d'un utilisateur
    user_data = {
        "username": "test_padawan2",
        "email": "padawan2@jedi.com",
        "password": "Force123Jedi",
        "role": "padawan"
    }
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Authentification
    auth_data = {
        "username": "test_padawan2",
        "password": "Force123Jedi"
    }
    response = client.post("/api/auth/login", json=auth_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Récupération d'un exercice
    response = client.get("/api/exercises/", headers=headers)
    assert response.status_code == 200
    exercise_id = response.json()[0]["id"]
    
    # Tentative avec une réponse incorrecte
    answer_data = {
        "user_answer": 999999  # Réponse clairement incorrecte
    }
    response = client.post(
        f"/api/exercises/{exercise_id}/attempt",
        json=answer_data,
        headers=headers
    )
    assert response.status_code == 200
    attempt = response.json()
    assert attempt["is_correct"] is False
    
    # Nettoyage
    response = client.delete(f"/api/users/{user_id}", headers=headers)
    assert response.status_code == 204 
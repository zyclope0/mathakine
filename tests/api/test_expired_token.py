import json
"""
Tests de l'authentification avec des tokens expirés.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db_helpers import get_enum_value

client = TestClient(app)

def test_expired_token_access(expired_token_client):
    """Teste l'accès à une ressource protégée avec un token expiré."""
    # Récupérer le client avec le token expiré
    client = expired_token_client["client"]
    
    # Essayer d'accéder à une ressource protégée
    response = client.get("/api/exercises/")
    
    # Vérifier que l'accès est refusé avec un code 401
    assert response.status_code == 401, f"Le code d'état devrait être 401, reçu {response.status_code}"
    
    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data, "La réponse devrait contenir des détails sur l'erreur"
    assert "expiré" in data["detail"].lower() or "expired" in data["detail"].lower(), "Le message devrait indiquer que le token est expiré"

def test_expired_token_exercise_creation(expired_token_client):
    """Teste la création d'un exercice avec un token expiré."""
    # Récupérer le client avec le token expiré
    client = expired_token_client["client"]
    
    # Données pour la création d'un exercice
    exercise_data = {
        "title": "Test Exercise",
        "exercise_type": "addition",
        "difficulty": "initie",
        "question": "Combien font 2+2?",
        "correct_answer": "4",
        "choices": ["2", "3", "4", "5"]
    }
    
    # Essayer de créer un exercice
    response = client.post("/api/exercises/", json=exercise_data)
    
    # Vérifier que l'accès est refusé avec un code 401
    assert response.status_code == 401, f"Le code d'état devrait être 401, reçu {response.status_code}"
    
    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data, "La réponse devrait contenir des détails sur l'erreur"
    assert any(keyword in data["detail"].lower() for keyword in ["expiré", "expired", "invalide", "invalid"]), "Le message devrait indiquer que le token est expiré ou invalide"

def test_expired_token_exercise_attempt(expired_token_client):
    """Teste la soumission d'une tentative avec un token expiré."""
    # Récupérer le client avec le token expiré
    client = expired_token_client["client"]
    
    # Données pour la soumission d'une tentative
    attempt_data = {
        "exercise_id": 1,
        "selected_answer": "4",
        "time_spent": 10.0
    }
    
    # Essayer de soumettre une tentative
    response = client.post("/api/exercises/1/submit", json=attempt_data)
    
    # Vérifier que l'accès est refusé avec un code 401
    assert response.status_code == 401, f"Le code d'état devrait être 401, reçu {response.status_code}"
    
    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data, "La réponse devrait contenir des détails sur l'erreur"
    assert any(keyword in data["detail"].lower() for keyword in ["expiré", "expired", "invalide", "invalid"]), "Le message devrait indiquer que le token est expiré ou invalide" 
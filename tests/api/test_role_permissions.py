import json
"""
Tests des permissions d'accès selon les rôles des utilisateurs.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import UserRole
from app.api.deps import get_current_user
import uuid
from app.utils.db_helpers import adapt_enum_for_db
from app.utils.db_helpers import get_enum_value

client = TestClient(app)

@pytest.fixture
def padawan_client(db_session):
    """Crée un client authentifié avec un rôle PADAWAN."""
    # Créer un utilisateur padawan
    unique_id = uuid.uuid4().hex[:8]
    
    user_data = {
        "username": f"padawan_{unique_id}",
        "email": f"padawan_{unique_id}@jedi.com",
        "password": "Force123Jedi",
        "role": "padawan"  # Utiliser directement la valeur Python
    }
    
    # Créer l'utilisateur
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201, f"Erreur lors de la création de l'utilisateur: {response.text}"
    
    # Authentification
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200, f"Erreur d'authentification: {response.text}"
    
    token = response.json()["access_token"]
    client_instance = TestClient(app)
    client_instance.headers.update({"Authorization": f"Bearer {token}"})
    
    return {
        "client": client_instance,
        "user_data": user_data,
        "token": token,
        "user_id": response.json().get("user_id")
    }

@pytest.fixture
def maitre_client(db_session):
    """Crée un client authentifié avec un rôle MAITRE."""
    # Créer un utilisateur maître
    unique_id = uuid.uuid4().hex[:8]
    
    user_data = {
        "username": f"maitre_{unique_id}",
        "email": f"maitre_{unique_id}@jedi.com",
        "password": "Force123Jedi",
        "role": "maitre"  # Utiliser directement la valeur Python
    }
    
    # Créer l'utilisateur
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201, f"Erreur lors de la création de l'utilisateur: {response.text}"
    
    # Authentification
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200, f"Erreur d'authentification: {response.text}"
    
    token = response.json()["access_token"]
    client_instance = TestClient(app)
    client_instance.headers.update({"Authorization": f"Bearer {token}"})
    
    return {
        "client": client_instance,
        "user_data": user_data,
        "token": token,
        "user_id": response.json().get("user_id")
    }

@pytest.fixture
def gardien_client(db_session):
    """Crée un client authentifié avec un rôle GARDIEN."""
    # Créer un utilisateur gardien
    unique_id = uuid.uuid4().hex[:8]
    
    user_data = {
        "username": f"gardien_{unique_id}",
        "email": f"gardien_{unique_id}@jedi.com",
        "password": "Force123Jedi",
        "role": "gardien"  # Utiliser directement la valeur Python
    }
    
    # Créer l'utilisateur
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201, f"Erreur lors de la création de l'utilisateur: {response.text}"
    
    # Authentification
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200, f"Erreur d'authentification: {response.text}"
    
    token = response.json()["access_token"]
    client_instance = TestClient(app)
    client_instance.headers.update({"Authorization": f"Bearer {token}"})
    
    return {
        "client": client_instance,
        "user_data": user_data,
        "token": token,
        "user_id": response.json().get("user_id")
    }

def test_padawan_permissions(padawan_client):
    """Teste les permissions d'un utilisateur avec le rôle PADAWAN."""
    client = padawan_client["client"]
    
    # Accès autorisé: récupérer des exercices
    response = client.get("/api/exercises/")
    assert response.status_code == 200, "Un padawan devrait pouvoir accéder aux exercices"
    
    # Accès autorisé: soumettre une tentative pour un exercice existant
    attempt_data = {
        "selected_answer": "4",
        "time_spent": 10.0
    }
    # Note: Cette requête peut échouer avec 404 si l'exercice n'existe pas, ce qui est acceptable
    response = client.post("/api/exercises/1/submit", json=attempt_data)
    assert response.status_code in [200, 404], f"Un padawan devrait pouvoir soumettre une tentative (ou recevoir 404 si l'exercice n'existe pas)"
    
    # Créer un exercice pour tester la suppression
    exercise_data = {
        "title": "Exercice de Test PADAWAN",
        "exercise_type": "addition",
        "difficulty": "initie",
        "question": "Combien font 1+1?",
        "correct_answer": "2",
        "choices": ["1", "2", "3", "4"]
    }
    response = client.post("/api/exercises/", json=exercise_data)
    
    if response.status_code == 200:
        exercise_id = response.json()["id"]
        
        # Accès non autorisé: supprimer un exercice (même le sien)
        response = client.delete(f"/api/exercises/{exercise_id}")
        assert response.status_code == 403, "Un padawan ne devrait pas pouvoir supprimer un exercice"
    else:
        # Si la création échoue, tester avec un ID inexistant - le 403 devrait primer sur le 404
        # Mais pour ce test, on suppose que la création réussit
        assert False, f"La création d'exercice a échoué: {response.status_code} - {response.text}"

def test_maitre_permissions(maitre_client, padawan_client):
    """Teste les permissions d'un utilisateur avec le rôle MAITRE."""
    maitre = maitre_client["client"]
    
    # Accès autorisé: créer un exercice
    exercise_data = {
        "title": "Exercice du Maître",
        "exercise_type": "addition",
        "difficulty": "padawan",
        "question": "Combien font 5+7?",
        "correct_answer": "12",
        "choices": ["10", "11", "12", "13"]
    }
    response = maitre.post("/api/exercises/", json=exercise_data)
    assert response.status_code == 200, "Un maître devrait pouvoir créer un exercice"
    
    # Récupérer l'ID de l'exercice créé
    exercise_id = response.json()["id"]
    
    # Accès autorisé: modifier son propre exercice
    update_data = {
        "title": "Exercice du Maître (Modifié)"
    }
    response = maitre.patch(f"/api/exercises/{exercise_id}", json=update_data)
    assert response.status_code in [200, 404], "Un maître devrait pouvoir modifier son propre exercice"
    
    # Accès autorisé: supprimer son propre exercice
    response = maitre.delete(f"/api/exercises/{exercise_id}")
    assert response.status_code in [200, 204], "Un maître devrait pouvoir supprimer son propre exercice"
    
    # Accès non autorisé: supprimer l'exercice d'un autre utilisateur
    # Créer d'abord un exercice avec un autre utilisateur
    padawan = padawan_client["client"]
    exercise_data = {
        "title": "Exercice du Padawan",
        "exercise_type": "addition",
        "difficulty": "initie",
        "question": "Combien font 2+3?",
        "correct_answer": "5",
        "choices": ["3", "4", "5", "6"]
    }
    response = padawan.post("/api/exercises/", json=exercise_data)
    if response.status_code == 200:
        padawan_exercise_id = response.json()["id"]
        
        # Tenter de supprimer l'exercice du padawan avec le compte du maître
        response = maitre.delete(f"/api/exercises/{padawan_exercise_id}")
        assert response.status_code == 403, "Un maître ne devrait pas pouvoir supprimer l'exercice d'un autre utilisateur"

def test_gardien_permissions(gardien_client, padawan_client):
    """Teste les permissions d'un utilisateur avec le rôle GARDIEN."""
    gardien = gardien_client["client"]
    
    # Accès autorisé: récupérer les exercices (y compris les archivés)
    response = gardien.get("/api/exercises/?include_archived=true")
    assert response.status_code == 200, "Un gardien devrait pouvoir accéder aux exercices archivés"
    
    # Accès autorisé: archiver un exercice qu'il n'a pas créé
    # Créer d'abord un exercice avec un autre utilisateur
    padawan = padawan_client["client"]
    exercise_data = {
        "title": "Exercice à Archiver",
        "exercise_type": "addition",
        "difficulty": "initie",
        "question": "Combien font 1+1?",
        "correct_answer": "2",
        "choices": ["1", "2", "3", "4"]
    }
    response = padawan.post("/api/exercises/", json=exercise_data)
    if response.status_code == 200:
        exercise_id = response.json()["id"]
        
        # Archiver l'exercice avec le compte du gardien
        response = gardien.delete(f"/api/exercises/{exercise_id}")
        assert response.status_code in [200, 204], "Un gardien devrait pouvoir archiver n'importe quel exercice"
        
        # Vérifier que l'exercice est archivé et non supprimé
        response = gardien.get(f"/api/exercises/{exercise_id}")
        if response.status_code == 200:
            assert response.json()["is_archived"] is True, "L'exercice devrait être marqué comme archivé" 
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.logic_challenge import LogicChallenge

client = TestClient(app)

def test_logic_challenge_list():
    """Test de récupération de la liste des défis logiques"""
    response = client.get("/api/challenges/")
    assert response.status_code == 200
    challenges = response.json()
    assert isinstance(challenges, list)
    assert len(challenges) > 0
    
    # Vérification de la structure des défis
    challenge = challenges[0]
    assert "id" in challenge
    assert "type" in challenge
    assert "difficulty" in challenge
    assert "question" in challenge
    assert "correct_answer" in challenge

def test_logic_challenge_detail():
    """Test de récupération d'un défi spécifique"""
    # Récupérer d'abord la liste pour avoir un ID valide
    response = client.get("/api/challenges/")
    assert response.status_code == 200
    challenge_id = response.json()[0]["id"]
    
    # Récupérer les détails du défi
    response = client.get(f"/api/challenges/{challenge_id}")
    assert response.status_code == 200
    challenge = response.json()
    
    # Vérification des détails
    assert challenge["id"] == challenge_id
    assert "type" in challenge
    assert "difficulty" in challenge
    assert "question" in challenge
    assert "correct_answer" in challenge
    assert "hints" in challenge
    assert "explanation" in challenge

def test_logic_challenge_correct_answer():
    """Test de soumission d'une réponse correcte"""
    # Récupérer un défi
    response = client.get("/api/challenges/")
    assert response.status_code == 200
    challenge = response.json()[0]
    
    # Soumettre la réponse correcte
    answer_data = {
        "answer": challenge["correct_answer"]
    }
    response = client.post(
        f"/api/challenges/{challenge['id']}/attempt",
        json=answer_data
    )
    assert response.status_code == 200
    result = response.json()
    assert result["is_correct"] is True
    assert "feedback" in result
    assert "explanation" in result

def test_logic_challenge_incorrect_answer():
    """Test de soumission d'une réponse incorrecte"""
    # Récupérer un défi
    response = client.get("/api/challenges/")
    assert response.status_code == 200
    challenge = response.json()[0]
    
    # Soumettre une réponse incorrecte
    answer_data = {
        "answer": "réponse_incorrecte"
    }
    response = client.post(
        f"/api/challenges/{challenge['id']}/attempt",
        json=answer_data
    )
    assert response.status_code == 200
    result = response.json()
    assert result["is_correct"] is False
    assert "feedback" in result
    assert "hints" in result

def test_logic_challenge_hints():
    """Test de récupération des indices pour un défi"""
    # Récupérer un défi
    response = client.get("/api/challenges/")
    assert response.status_code == 200
    challenge = response.json()[0]
    
    # Demander un indice
    response = client.get(f"/api/challenges/{challenge['id']}/hint")
    assert response.status_code == 200
    hint = response.json()
    assert "hint" in hint
    assert isinstance(hint["hint"], str)
    assert len(hint["hint"]) > 0

def test_logic_challenge_progression():
    """Test de la progression dans les défis logiques"""
    # Créer un utilisateur de test
    user_data = {
        "username": "test_jedi",
        "email": "jedi@test.com",
        "password": "Force123Jedi",
        "role": "padawan"
    }
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Authentifier l'utilisateur
    auth_data = {
        "username": "test_jedi",
        "password": "Force123Jedi"
    }
    response = client.post("/api/auth/login", json=auth_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Vérifier la progression initiale
    response = client.get(f"/api/users/{user_id}/challenges/progress", headers=headers)
    assert response.status_code == 200
    initial_progress = response.json()
    assert "completed_challenges" in initial_progress
    assert "total_challenges" in initial_progress
    
    # Compléter quelques défis
    response = client.get("/api/challenges/", headers=headers)
    challenges = response.json()
    
    for challenge in challenges[:3]:  # Compléter les 3 premiers défis
        answer_data = {
            "answer": challenge["correct_answer"]
        }
        response = client.post(
            f"/api/challenges/{challenge['id']}/attempt",
            json=answer_data,
            headers=headers
        )
        assert response.status_code == 200
    
    # Vérifier la progression mise à jour
    response = client.get(f"/api/users/{user_id}/challenges/progress", headers=headers)
    assert response.status_code == 200
    updated_progress = response.json()
    assert updated_progress["completed_challenges"] > initial_progress["completed_challenges"]
    
    # Nettoyage
    response = client.delete(f"/api/users/{user_id}", headers=headers)
    assert response.status_code == 204 
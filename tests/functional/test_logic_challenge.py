"""
Tests fonctionnels pour les défis logiques
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

# Créer le client de test en dehors des fonctions de test
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
    assert "challenge_type" in challenge
    assert "age_group" in challenge
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
    assert "challenge_type" in challenge
    assert "description" in challenge
    assert "correct_answer" in challenge


def test_logic_challenge_correct_answer(auth_client):
    """Test de soumission d'une réponse correcte"""
    # Récupérer un défi
    client = auth_client["client"]
    response = client.get("/api/challenges/")
    assert response.status_code == 200
    challenge = response.json()[0]
    
    # Soumettre la réponse correcte (auth déjà incluse dans le client)
    answer_data = {
        "answer": challenge["correct_answer"]
    }
    response = client.post(
        f"/api/challenges/{challenge['id']}/attempt",
        json=answer_data
    )
    
    # Si le test ne peut pas s'exécuter, on passe mais on ne l'ignore pas
    if response.status_code != 200:
        pytest.fail(f"Échec du test: {response.text}")
        
    result = response.json()
    assert result["is_correct"] is True
    assert "feedback" in result


def test_logic_challenge_incorrect_answer(auth_client):
    """Test de soumission d'une réponse incorrecte"""
    # Récupérer un défi
    client = auth_client["client"]
    response = client.get("/api/challenges/")
    assert response.status_code == 200
    challenge = response.json()[0]
    
    # Soumettre une réponse incorrecte (auth déjà incluse dans le client)
    answer_data = {
        "answer": "réponse_incorrecte"
    }
    response = client.post(
        f"/api/challenges/{challenge['id']}/attempt",
        json=answer_data
    )
    
    # Si le test ne peut pas s'exécuter, on échoue mais on ne l'ignore pas
    if response.status_code != 200:
        pytest.fail(f"Échec du test: {response.text}")
        
    result = response.json()
    assert result["is_correct"] is False
    assert "feedback" in result


def test_logic_challenge_hints(auth_client):
    """Test de récupération des indices pour un défi"""
    # Récupérer un défi
    client = auth_client["client"]
    response = client.get("/api/challenges/")
    assert response.status_code == 200
    challenge = response.json()[0]
    
    # Demander un indice (auth déjà incluse dans le client)
    response = client.get(f"/api/challenges/{challenge['id']}/hint")
    
    # Si le test ne peut pas s'exécuter, on échoue mais on ne l'ignore pas
    if response.status_code != 200:
        pytest.fail(f"Échec du test: {response.text}")
        
    hint_data = response.json()
    assert "hint" in hint_data


def test_logic_challenge_progression(auth_client):
    """Test de la progression dans les défis logiques"""
    client = auth_client["client"]
    user_id = auth_client.get("user_id")
    
    # Si pas d'user_id, on essaie d'obtenir l'ID d'une autre façon
    if not user_id:
        response = client.get("/api/users/me")
        if response.status_code == 200:
            user_id = response.json().get("id")
        else:
            pytest.skip("Impossible de déterminer l'ID utilisateur")
    
    # Récupérer la liste des défis
    response = client.get("/api/challenges/")
    assert response.status_code == 200
    challenges = response.json()
    
    # Choisir un défi et faire une tentative
    challenge = challenges[0]
    response = client.post(
        f"/api/challenges/{challenge['id']}/attempt",
        json={"answer": challenge["correct_answer"]}
    )
    
    # Si la tentative échoue, on échoue mais on n'ignore pas le test
    if response.status_code != 200:
        pytest.fail(f"Échec de la tentative de défi: {response.text}")
    
    # Vérifier les statistiques
    response = client.get(f"/api/users/{user_id}/stats")
    
    # Si on ne peut pas vérifier les stats, on échoue mais on n'ignore pas le test
    if response.status_code != 200:
        pytest.fail(f"Échec de récupération des statistiques: {response.text}")
        
    stats = response.json()
    assert "logic_challenge_stats" in stats

"""
Tests des endpoints API pour les défis logiques.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.logic_challenge import LogicChallengeType, AgeGroup
from tests.fixtures.model_fixtures import test_logic_challenge, test_logic_challenges

client = TestClient(app)




def test_get_logic_challenges():
    """Test de l'endpoint pour récupérer tous les défis logiques."""
    response = client.get("/api/challenges/")
    assert response.status_code == 200
    data = response.json()

    # Vérifier que c'est une liste
    assert isinstance(data, list)

    # Vérifier qu'il y a au moins un défi
    assert len(data) > 0

    # Vérifier les champs requis
    first_challenge = data[0]
    assert "id" in first_challenge
    assert "type" in first_challenge or "challenge_type" in first_challenge
    assert "difficulty" in first_challenge
    assert "question" in first_challenge or "description" in first_challenge
    assert "correct_answer" in first_challenge




def test_get_logic_challenge_by_id():
    """Test de l'endpoint pour récupérer un défi logique par ID."""
    # Tester avec un ID connu (1)
    response = client.get("/api/challenges/1")
    assert response.status_code == 200
    challenge = response.json()

    # Vérifier les champs
    assert challenge["id"] == 1
    assert "challenge_type" in challenge or "type" in challenge
    assert "description" in challenge or "question" in challenge
    assert "correct_answer" in challenge
    assert "solution_explanation" in challenge or "explanation" in challenge




def test_get_nonexistent_challenge():
    """Test de l'endpoint pour récupérer un défi logique inexistant."""
    # Tester avec un ID très grand (probablement inexistant)
    response = client.get("/api/challenges/9999")
    assert response.status_code == 404




def test_challenge_attempt_correct():
    """Test de la soumission d'une tentative correcte pour un défi logique."""
    challenge_id = 1

    # Récupérer d'abord le défi pour connaître la réponse correcte
    response = client.get(f"/api/challenges/{challenge_id}")
    assert response.status_code == 200
    challenge = response.json()
    correct_answer = challenge["correct_answer"]

    # Soumettre la réponse correcte
    attempt_data = {"answer": correct_answer}
    response = client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)
    assert response.status_code == 200

    # Vérifier la réponse
    result = response.json()
    assert result["is_correct"] is True
    assert "feedback" in result
    assert "explanation" in result
    assert result["hints"] is None  # Pas d'indice nécessaire pour une réponse correcte




def test_challenge_attempt_incorrect():
    """Test de la soumission d'une tentative incorrecte pour un défi logique."""
    challenge_id = 1

    # Récupérer d'abord le défi pour s'assurer de soumettre une mauvaise réponse
    response = client.get(f"/api/challenges/{challenge_id}")
    assert response.status_code == 200
    challenge = response.json()
    correct_answer = challenge["correct_answer"]
    incorrect_answer = "WRONG_ANSWER"  # Une valeur qui n'est certainement pas la bonne

    # S'assurer que notre réponse est différente de la bonne
    if incorrect_answer == correct_answer:
        incorrect_answer = "DIFFERENT_WRONG_ANSWER"

    # Soumettre la réponse incorrecte
    attempt_data = {"answer": incorrect_answer}
    response = client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)
    assert response.status_code == 200

    # Vérifier la réponse
    result = response.json()
    assert result["is_correct"] is False
    assert "feedback" in result
    assert result["explanation"] is None  # Pas d'explication pour une réponse incorrecte
    assert result["hints"] is not None  # Des indices devraient être fournis




def test_get_challenge_hint():
    """Test de l'endpoint pour récupérer un indice pour un défi logique."""
    challenge_id = 1

    # Récupérer le premier niveau d'indice
    response = client.get(f"/api/challenges/{challenge_id}/hint", params={"level": 1})
    assert response.status_code == 200
    hint_data = response.json()

    # Vérifier que l'indice est présent
    assert "hint" in hint_data
    assert hint_data["hint"] is not None
    assert isinstance(hint_data["hint"], str)

    # Récupérer un niveau d'indice non disponible (généralement > 3)
    response = client.get(f"/api/challenges/{challenge_id}/hint", params={"level": 99})
    assert response.status_code == 400  # Bad Request attendu




def test_filter_challenges_by_type():
    """Test du filtrage des défis par type."""
    # Récupérer les défis de type SEQUENCE
    response = client.get("/api/challenges/", params={"challenge_type": "sequence"})
    assert response.status_code == 200
    challenges = response.json()

    # Vérifier que tous les défis retournés sont de type SEQUENCE
    for challenge in challenges:
        challenge_type = challenge.get("type") or challenge.get("challenge_type")
        assert challenge_type.lower() == "sequence"

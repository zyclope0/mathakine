import json
"""
Tests des endpoints API pour les défis logiques.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.logic_challenge import LogicChallengeType, AgeGroup
from app.models.user import User, UserRole
from app.api.deps import get_current_user
from app.utils.db_helpers import get_enum_value
from tests.fixtures.model_fixtures import test_logic_challenge, test_logic_challenges

client = TestClient(app)

@pytest.fixture
def test_authenticated_user(db_session):
    """
    Crée un utilisateur de test authentifié pour les tests qui nécessitent l'authentification.
    Override la dépendance get_current_user pour simuler un utilisateur authentifié.
    """
    # Créer un utilisateur de test
    user = User(
        id=999,
        username="test_padawan",
        email="test_padawan@example.com",
        hashed_password="hashed_password",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    
    # Override la dépendance pour simuler un utilisateur authentifié
    def override_get_current_user():
        return user
    
    # Sauvegarder la dépendance originale
    original_dependency = app.dependency_overrides.get(get_current_user)
    
    # Remplacer par notre override
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Fournir l'utilisateur au test
    yield user
    
    # Restaurer la dépendance originale après le test
    if original_dependency:
        app.dependency_overrides[get_current_user] = original_dependency
    else:
        del app.dependency_overrides[get_current_user]


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
    assert "age_group" in first_challenge
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


def test_challenge_attempt_correct(test_authenticated_user):
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


def test_challenge_attempt_incorrect(test_authenticated_user):
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


def test_get_challenge_hint(test_authenticated_user):
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
    assert response.status_code == 422  # Validation error attendu (Unprocessable Entity)


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


def test_challenge_attempt_missing_data(test_authenticated_user):
    """Test de la soumission d'une tentative sans données pour un défi logique."""
    challenge_id = 1
    
    # Soumettre une tentative sans données
    attempt_data = {}  # Données vides, manque le champ 'answer'
    response = client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)
    
    # Devrait retourner 422 Unprocessable Entity
    assert response.status_code == 422, f"Le code d'état devrait être 422, reçu {response.status_code}"
    
    # Vérifier que l'erreur mentionne le champ manquant
    data = response.json()
    assert "detail" in data, "La réponse devrait contenir des détails sur l'erreur"
    validation_errors = data["detail"]
    assert any("answer" in str(error) for error in validation_errors), "L'erreur devrait mentionner le champ 'answer' manquant"


def test_challenge_attempt_nonexistent_challenge(test_authenticated_user):
    """Test de la soumission d'une tentative pour un défi inexistant."""
    # Utiliser un ID de défi qui n'existe probablement pas
    challenge_id = 9999
    
    attempt_data = {"answer": "Une réponse quelconque"}
    response = client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)
    
    # Devrait retourner 404 Not Found
    assert response.status_code == 404, f"Le code d'état devrait être 404, reçu {response.status_code}"
    
    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data, "La réponse devrait contenir des détails sur l'erreur"
    error_message = data["detail"].lower()
    assert ("not found" in error_message or 
            "introuvable" in error_message or 
            "non trouvé" in error_message or
            "non trouve" in error_message), f"Le message devrait indiquer que le défi n'existe pas. Message reçu: {data['detail']}"


def test_challenge_hint_invalid_level(test_authenticated_user):
    """Test de la récupération d'un indice avec un niveau invalide."""
    challenge_id = 1
    
    # Tester avec un niveau d'indice négatif
    response = client.get(f"/api/challenges/{challenge_id}/hint", params={"level": -1})
    
    # Devrait retourner 422 Unprocessable Entity
    assert response.status_code == 422, f"Le code d'état devrait être 422, reçu {response.status_code}"
    
    # Vérifier que l'erreur mentionne le problème avec le niveau
    data = response.json()
    assert "detail" in data, "La réponse devrait contenir des détails sur l'erreur"
    validation_errors = data["detail"]
    assert any("level" in str(error) for error in validation_errors), "L'erreur devrait mentionner le problème avec le champ 'level'"


def test_challenge_attempt_unauthenticated():
    """Test de la soumission d'une tentative sans authentification."""
    challenge_id = 1
    
    # S'assurer qu'il n'y a pas d'authentification
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    
    # Soumettre une tentative
    attempt_data = {"answer": "Une réponse quelconque"}
    response = client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)
    
    # Devrait retourner 401 Unauthorized
    assert response.status_code == 401, f"Le code d'état devrait être 401, reçu {response.status_code}"
    
    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data, "La réponse devrait contenir des détails sur l'erreur"
    error_message = data["detail"].lower()
    assert ("authentication" in error_message or 
            "authentification" in error_message or
            "not authenticated" in error_message or
            "non authentifié" in error_message), f"Le message devrait indiquer un problème d'authentification. Message reçu: {data['detail']}"


def test_challenge_with_centralized_fixtures(padawan_client, mock_request, mock_api_response):
    """Test d'un défi logique en utilisant les fixtures centralisées."""
    # Récupérer le client authentifié
    client = padawan_client["client"]
    
    # Récupérer un défi existant
    response = client.get("/api/challenges/1")
    assert response.status_code == 200, "Impossible de récupérer le défi logique"
    challenge = response.json()
    challenge_id = challenge["id"]
    
    # Tester la soumission d'une réponse en utilisant mock_request
    # Simuler une requête qui sera utilisée pour des tests unitaires
    request = mock_request(
        authenticated=True,
        role="padawan",
        json_data={"answer": challenge["correct_answer"]},
        path_params={"challenge_id": challenge_id}
    )
    
    # Simuler une réponse d'API (utile pour les mocks de tests)
    success_response = mock_api_response(
        status_code=200,
        data={
            "is_correct": True,
            "feedback": "Excellente réponse, jeune Padawan!",
            "explanation": challenge.get("solution_explanation", ""),
            "hints": None
        }
    )
    
    # Test réel avec le client
    attempt_data = {"answer": challenge["correct_answer"]}
    response = client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)
    
    # Vérifier que la tentative a réussi
    assert response.status_code == 200, f"Le code d'état devrait être 200, reçu {response.status_code}"
    
    # Vérifier la réponse
    result = response.json()
    assert result["is_correct"] is True, "La réponse devrait être marquée comme correcte"
    assert "feedback" in result, "La réponse devrait contenir un feedback"
    assert "explanation" in result, "La réponse devrait contenir une explication"

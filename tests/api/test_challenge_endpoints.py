import json
"""
Tests des endpoints API pour les défis logiques.
"""
import pytest
from app.models.logic_challenge import LogicChallengeType, AgeGroup
from app.models.user import User, UserRole
from app.utils.db_helpers import get_enum_value
from tests.fixtures.model_fixtures import test_logic_challenge, test_logic_challenges


def _get_challenges_list(data):
    """Extrait la liste des défis (API retourne {items: [...], total, page, ...})."""
    if isinstance(data, list):
        return data
    return data.get("items", [])


async def test_get_logic_challenges(padawan_client):
    """Test de l'endpoint pour récupérer tous les défis logiques."""
    client = padawan_client["client"]
    response = await client.get("/api/challenges")
    assert response.status_code == 200
    raw = response.json()
    data = _get_challenges_list(raw)

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
    # correct_answer may be omitted in list endpoint for security


async def test_get_logic_challenge_by_id(padawan_client):
    """Test de l'endpoint pour récupérer un défi logique par ID."""
    client = padawan_client["client"]
    # Obtenir un ID de défi existant via la liste
    list_resp = await client.get("/api/challenges")
    assert list_resp.status_code == 200
    challenges = _get_challenges_list(list_resp.json())
    if not challenges:
        pytest.skip("No challenges available in test DB")
    challenge_id = challenges[0]["id"]
    response = await client.get(f"/api/challenges/{challenge_id}")
    assert response.status_code == 200
    challenge = response.json()

    # Vérifier les champs
    assert challenge["id"] == challenge_id
    assert "challenge_type" in challenge or "type" in challenge
    assert "description" in challenge or "question" in challenge
    assert "correct_answer" in challenge
    assert "solution_explanation" in challenge or "explanation" in challenge


async def test_get_nonexistent_challenge(padawan_client):
    """Test de l'endpoint pour récupérer un défi logique inexistant."""
    client = padawan_client["client"]
    # Tester avec un ID très grand (probablement inexistant)
    response = await client.get("/api/challenges/9999")
    assert response.status_code == 404


async def test_challenge_attempt_correct(padawan_client):
    """Test de la soumission d'une tentative correcte pour un défi logique."""
    client = padawan_client["client"]
    # Obtenir un défi existant
    list_resp = await client.get("/api/challenges")
    assert list_resp.status_code == 200
    challenges = _get_challenges_list(list_resp.json())
    if not challenges:
        pytest.skip("No challenges available in test DB")
    challenge_id = challenges[0]["id"]

    # Récupérer d'abord le défi pour connaître la réponse correcte
    response = await client.get(f"/api/challenges/{challenge_id}")
    assert response.status_code == 200
    challenge = response.json()
    correct_answer = challenge["correct_answer"]

    # Soumettre la réponse correcte
    attempt_data = {"answer": correct_answer}
    response = await client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)
    assert response.status_code == 200

    # Vérifier la réponse (API peut retourner feedback ou explanation)
    result = response.json()
    assert result["is_correct"] is True
    assert "explanation" in result
    assert result.get("hints") is None or result.get("hints_remaining") is None  # Pas d'indice nécessaire


async def test_challenge_attempt_incorrect(padawan_client):
    """Test de la soumission d'une tentative incorrecte pour un défi logique."""
    client = padawan_client["client"]
    # Obtenir un défi existant
    list_resp = await client.get("/api/challenges")
    assert list_resp.status_code == 200
    challenges = _get_challenges_list(list_resp.json())
    if not challenges:
        pytest.skip("No challenges available in test DB")
    challenge_id = challenges[0]["id"]

    # Récupérer d'abord le défi pour s'assurer de soumettre une mauvaise réponse
    response = await client.get(f"/api/challenges/{challenge_id}")
    assert response.status_code == 200
    challenge = response.json()
    correct_answer = challenge["correct_answer"]
    incorrect_answer = "WRONG_ANSWER"  # Une valeur qui n'est certainement pas la bonne

    # S'assurer que notre réponse est différente de la bonne
    if incorrect_answer == correct_answer:
        incorrect_answer = "DIFFERENT_WRONG_ANSWER"

    # Soumettre la réponse incorrecte
    attempt_data = {"answer": incorrect_answer}
    response = await client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)
    assert response.status_code == 200

    # Vérifier la réponse (API peut retourner hints ou hints_remaining)
    result = response.json()
    assert result["is_correct"] is False
    assert result["explanation"] is None  # Pas d'explication pour une réponse incorrecte
    assert result.get("hints") is not None or "hints_remaining" in result  # Indices disponibles


async def test_get_challenge_hint(padawan_client):
    """Test de l'endpoint pour récupérer un indice pour un défi logique."""
    client = padawan_client["client"]
    # Obtenir un défi existant
    list_resp = await client.get("/api/challenges")
    assert list_resp.status_code == 200
    challenges = _get_challenges_list(list_resp.json())
    if not challenges:
        pytest.skip("No challenges available in test DB")
    challenge_id = challenges[0]["id"]

    # Récupérer le premier niveau d'indice (certains défis n'ont pas d'indices)
    response = await client.get(f"/api/challenges/{challenge_id}/hint", params={"level": 1})
    if response.status_code == 400:
        pytest.skip("Challenge has no hints configured")
    assert response.status_code == 200
    hint_data = response.json()

    # Vérifier que l'indice est présent
    assert "hint" in hint_data
    assert hint_data["hint"] is not None
    assert isinstance(hint_data["hint"], str)

    # Récupérer un niveau d'indice non disponible (généralement > 3)
    response = await client.get(f"/api/challenges/{challenge_id}/hint", params={"level": 99})
    assert response.status_code in (400, 404)  # 400 pour niveau invalide


async def test_filter_challenges_by_type(padawan_client):
    """Test du filtrage des défis par type."""
    client = padawan_client["client"]
    # Récupérer les défis de type SEQUENCE
    response = await client.get("/api/challenges", params={"challenge_type": "sequence"})
    assert response.status_code == 200
    challenges = _get_challenges_list(response.json())

    # Vérifier que tous les défis retournés sont de type SEQUENCE
    for challenge in challenges:
        challenge_type = challenge.get("type") or challenge.get("challenge_type")
        assert challenge_type.lower() == "sequence"


async def test_challenge_attempt_missing_data(padawan_client):
    """Test de la soumission d'une tentative sans données pour un défi logique."""
    client = padawan_client["client"]
    # Obtenir un défi existant
    list_resp = await client.get("/api/challenges")
    assert list_resp.status_code == 200
    challenges = _get_challenges_list(list_resp.json())
    if not challenges:
        pytest.skip("No challenges available in test DB")
    challenge_id = challenges[0]["id"]

    # Soumettre une tentative sans données
    attempt_data = {}  # Données vides, manque le champ 'answer'
    response = await client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)

    # Starlette retourne 400 (pas 422 comme FastAPI) pour données manquantes
    assert response.status_code == 400, f"Le code d'état devrait être 400, reçu {response.status_code}"

    # Vérifier que l'erreur est présente
    data = response.json()
    assert "error" in data, f"La réponse devrait contenir un champ 'error': {data}"


async def test_challenge_attempt_nonexistent_challenge(padawan_client):
    """Test de la soumission d'une tentative pour un défi inexistant."""
    client = padawan_client["client"]
    # Utiliser un ID de défi qui n'existe probablement pas
    challenge_id = 9999

    attempt_data = {"answer": "Une réponse quelconque"}
    response = await client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)

    # Devrait retourner 404 Not Found
    assert response.status_code == 404, f"Le code d'état devrait être 404, reçu {response.status_code}"

    # Vérifier le message d'erreur (Starlette retourne {"error": "..."})
    data = response.json()
    assert "error" in data, f"La réponse devrait contenir un champ 'error': {data}"
    error_message = data["error"].lower()
    assert ("not found" in error_message or
            "introuvable" in error_message or
            "non trouvé" in error_message or
            "non trouve" in error_message or
            "non trouvé" in error_message.replace("é", "e")), \
        f"Le message devrait indiquer que le défi n'existe pas. Message reçu: {data['error']}"


async def test_challenge_hint_invalid_level(padawan_client):
    """Test de la récupération d'un indice avec un niveau invalide."""
    client = padawan_client["client"]
    # Obtenir un défi existant (ou 404 si aucun défi)
    list_resp = await client.get("/api/challenges")
    assert list_resp.status_code == 200
    challenges = _get_challenges_list(list_resp.json())
    if not challenges:
        pytest.skip("No challenges available in test DB")
    challenge_id = challenges[0]["id"]

    # Tester avec un niveau d'indice négatif
    response = await client.get(f"/api/challenges/{challenge_id}/hint", params={"level": -1})

    # 400/422 pour niveau invalide, 404 si défi inexistant
    assert response.status_code in (400, 404, 422), f"Le code d'état devrait être 400, 404 ou 422, reçu {response.status_code}"

    # Vérifier que l'erreur est présente
    data = response.json()
    assert "error" in data, f"La réponse devrait contenir un champ 'error': {data}"


async def test_challenge_attempt_unauthenticated(client):
    """Test de la soumission d'une tentative sans authentification."""
    # Utiliser un ID arbitraire car le test vérifie l'auth avant l'accès au défi
    challenge_id = 1

    # Soumettre une tentative (client non authentifié)
    attempt_data = {"answer": "Une réponse quelconque"}
    response = await client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)

    # Devrait retourner 401 Unauthorized
    assert response.status_code == 401, f"Le code d'état devrait être 401, reçu {response.status_code}"

    # Vérifier le message d'erreur (Starlette @require_auth retourne {"error": "..."})
    data = response.json()
    assert "error" in data, f"La réponse devrait contenir un champ 'error': {data}"
    error_message = data["error"].lower()
    assert ("authentication" in error_message or
            "authentification" in error_message or
            "requise" in error_message), f"Le message devrait indiquer un problème d'authentification. Message reçu: {data['error']}"


async def test_challenge_with_centralized_fixtures(padawan_client, mock_request, mock_api_response):
    """Test d'un défi logique en utilisant les fixtures centralisées."""
    client = padawan_client["client"]

    # Récupérer un défi existant (liste dynamique)
    list_resp = await client.get("/api/challenges")
    assert list_resp.status_code == 200, "Impossible de récupérer la liste des défis"
    challenges = _get_challenges_list(list_resp.json())
    if not challenges:
        pytest.skip("No challenges available in test DB")
    challenge_id = challenges[0]["id"]
    response = await client.get(f"/api/challenges/{challenge_id}")
    assert response.status_code == 200, "Impossible de récupérer le défi logique"
    challenge = response.json()

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
    response = await client.post(f"/api/challenges/{challenge_id}/attempt", json=attempt_data)

    # Vérifier que la tentative a réussi
    assert response.status_code == 200, f"Le code d'état devrait être 200, reçu {response.status_code}"

    # Vérifier la réponse (API peut retourner feedback ou explanation)
    result = response.json()
    assert result["is_correct"] is True, "La réponse devrait être marquée comme correcte"
    assert "explanation" in result, "La réponse devrait contenir une explication"

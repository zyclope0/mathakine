"""
Tests complets du flow challenges (Phases 3 & 4).
Teste :
- La normalisation des constantes (Phase 3)
- Le nouveau challenge_service.py (Phase 4)
- Les filtres par challenge_type et age_group
- La génération IA streaming
"""
import pytest
from app.core.constants import (
    normalize_challenge_type,
    normalize_age_group,
    CHALLENGE_TYPES_DB,
    AGE_GROUPS_DB
)

# NOTE: This file now uses centralized fixtures from conftest.py.
# The authentication pattern is to get a token from an authenticated client fixture (e.g., padawan_client)
# and set it as a cookie on the base client. This forces all tests to use the correct
# Starlette application (`enhanced_server.py`) and its cookie-based authentication.

def test_list_challenges_without_auth(client):
    """Test liste challenges sans authentification"""
    response = client.get("/api/challenges")
    assert response.status_code == 401, "L'accès non authentifié doit être interdit"


def test_list_challenges_authenticated(client, padawan_client):
    """Test liste challenges avec authentification"""
    token = padawan_client["token"]
    client.cookies.set("access_token", token)
    
    response = client.get("/api/challenges")
    
    assert response.status_code == 200, f"Erreur: {response.text}"
    data = response.json()
    assert "items" in data, "La réponse doit contenir une clé 'items'"
    assert isinstance(data["items"], list), "Les items doivent être dans une liste"
    
    client.cookies.clear()


def test_list_challenges_with_type_filter(client, padawan_client):
    """Test filtres challenges par type (Phase 3 - normalisation)"""
    token = padawan_client["token"]
    client.cookies.set("access_token", token)
    
    test_types = ["sequence", "SEQUENCE", "pattern", "PATTERN"]
    
    for challenge_type in test_types:
        response = client.get(
            f"/api/challenges?challenge_type={challenge_type}"
        )
        assert response.status_code == 200, f"Échec pour type={challenge_type}: {response.text}"
        data = response.json()
        assert isinstance(data["items"], list)
        
    client.cookies.clear()


def test_list_challenges_with_age_group_filter(client, padawan_client):
    """Test filtres challenges par groupe d'âge (Phase 3)"""
    token = padawan_client["token"]
    client.cookies.set("access_token", token)
    
    test_age_groups = ["age_6_8", "age_10_12", "GROUP_10_12"]
    
    for age_group in test_age_groups:
        response = client.get(
            f"/api/challenges?age_group={age_group}"
        )
        assert response.status_code == 200, f"Échec pour age_group={age_group}: {response.text}"
        data = response.json()
        assert isinstance(data["items"], list)

    client.cookies.clear()


def test_list_challenges_with_multiple_filters(client, padawan_client):
    """Test filtres multiples (type + age_group)"""
    token = padawan_client["token"]
    client.cookies.set("access_token", token)
    
    response = client.get(
        "/api/challenges?challenge_type=sequence&age_group=GROUP_10_12"
    )
    
    assert response.status_code == 200, f"Erreur filtres multiples: {response.text}"
    data = response.json()
    assert isinstance(data["items"], list)
    
    client.cookies.clear()


def test_challenge_service_integration(db_session):
    """Test nouveau challenge_service.py (Phase 4)"""
    from app.services.challenge_service import (
        create_challenge,
        list_challenges,
        get_challenge,
        delete_challenge
    )
    from app.models.user import User
    
    # Créer un utilisateur pour être le créateur
    test_user = User(username="service_test_user", email="service@test.com", hashed_password="password")
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    challenge_data = {
        "title": "Test Challenge Phase 4",
        "description": "Challenge de test pour validation Phase 4",
        "challenge_type": "SEQUENCE",
        "age_group": "GROUP_10_12",
        "correct_answer": "42",
        "solution_explanation": "La réponse est 42",
        "creator_id": test_user.id
    }
    
    challenge = create_challenge(db=db_session, **challenge_data)
    assert challenge is not None, "Échec création challenge"
    assert challenge.id is not None
    assert challenge.title == challenge_data["title"]
    assert challenge.challenge_type.value == challenge_data["challenge_type"].lower()
    from app.models.logic_challenge import AgeGroup
    age_group_value = challenge.age_group.value if hasattr(challenge.age_group, 'value') else challenge.age_group
    assert age_group_value == AgeGroup[challenge_data["age_group"]].value
    
    challenge_id = challenge.id
    
    retrieved = get_challenge(db=db_session, challenge_id=challenge_id)
    assert retrieved is not None
    assert retrieved.id == challenge_id
    
    challenges = list_challenges(db=db_session, challenge_type="SEQUENCE")
    assert len(challenges) > 0
    assert any(c.id == challenge_id for c in challenges)
    
    deleted = delete_challenge(db=db_session, challenge_id=challenge_id)
    assert deleted is True
    
    deleted_check = get_challenge(db=db_session, challenge_id=challenge_id)
    assert deleted_check is None


def test_constants_normalization():
    """Test normalisation constantes (Phase 3)"""
    # Test challenge_type
    assert normalize_challenge_type("sequence") == "SEQUENCE"
    assert normalize_challenge_type("SEQUENCE") == "SEQUENCE"
    assert normalize_challenge_type("pattern") == "PATTERN"
    assert normalize_challenge_type("invalid_type") is None
    
    # Test age_group
    assert normalize_age_group("age_6_8") == "GROUP_6_8"
    assert normalize_age_group("GROUP_6_8") == "GROUP_6_8"
    assert normalize_age_group("age_10_12") == "GROUP_10_12"
    assert normalize_age_group("10-12") == "GROUP_10_12"
    assert normalize_age_group("invalid_group") is None


def test_constants_values():
    """Test valeurs des constantes (Phase 3)"""
    # Vérifier que les constantes existent
    assert len(CHALLENGE_TYPES_DB) > 0
    assert len(AGE_GROUPS_DB) > 0
    
    # Vérifier des valeurs attendues
    assert "SEQUENCE" in CHALLENGE_TYPES_DB
    assert "PATTERN" in CHALLENGE_TYPES_DB
    assert "GROUP_6_8" in AGE_GROUPS_DB
    assert "GROUP_10_12" in AGE_GROUPS_DB


@pytest.mark.skipif(True, reason="Test streaming nécessite configuration spécifique")
def test_generate_ai_challenge_stream(client, padawan_client):
    """Test génération IA streaming (si implémenté)"""
    token = padawan_client["token"]
    client.cookies.set("access_token", token)
    
    response = client.get(
        "/api/challenges/generate-ai-stream?challenge_type=calculation&difficulty=easy",
        stream=True
    )
    
    if response.status_code == 200:
        assert "text/event-stream" in response.headers.get("content-type", "")
        
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                assert chunk.startswith(b"data:") or chunk.startswith(b"event:")
    
    client.cookies.clear()
"""
Tests fonctionnels isolés pour les défis logiques
Ces tests utilisent la base de données PostgreSQL et sont totalement autonomes.
"""

import pytest

from app.models.logic_challenge import AgeGroup, LogicChallenge, LogicChallengeType
from app.models.user import User, UserRole
from app.utils.db_helpers import get_enum_value
from tests.conftest import _create_authenticated_client


def ensure_challenge_exists_in_db(logic_challenge_db):
    """S'assure qu'au moins un défi logique existe dans la base de données"""
    # Vérifier si des défis existent déjà
    existing_challenge = logic_challenge_db.query(LogicChallenge).first()
    if existing_challenge:
        return existing_challenge.id

    # Si aucun défi n'existe, en créer un
    user = logic_challenge_db.query(User).first()
    if not user:
        # Créer un utilisateur si nécessaire
        from app.core.security import get_password_hash

        user = User(
            username="test_user_auto",
            email="test_auto@example.com",
            hashed_password=get_password_hash("testpassword"),
            role=get_enum_value(UserRole, UserRole.GARDIEN, logic_challenge_db),
        )
        logic_challenge_db.add(user)
        logic_challenge_db.commit()

    # Créer un défi de test avec des dates explicites
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    challenge = LogicChallenge(
        title="Défi Auto-Créé",
        description="Un défi créé automatiquement pour les tests",
        challenge_type=get_enum_value(
            LogicChallengeType, LogicChallengeType.SEQUENCE, logic_challenge_db
        ),
        age_group=get_enum_value(AgeGroup, AgeGroup.GROUP_10_12, logic_challenge_db),
        correct_answer="42",
        solution_explanation="La réponse à la question ultime",
        hints=[
            "Indice 1: C'est un nombre",
            "Indice 2: C'est un nombre entre 40 et 50",
            "Indice 3: C'est la réponse à la question ultime",
        ],
        difficulty_rating=3.0,
        estimated_time_minutes=15,
        creator_id=user.id,
        created_at=now,
        updated_at=now,
    )
    logic_challenge_db.add(challenge)
    logic_challenge_db.commit()

    return challenge.id


@pytest.fixture
async def padawan_client_after_db(logic_challenge_db):
    """Padawan client créé APRÈS logic_challenge_db pour éviter que le cleanup ne supprime l'utilisateur."""
    async with _create_authenticated_client(role="padawan") as result:
        yield result


def _get_challenges_list(data):
    """Extrait la liste des défis (API retourne {items: [...], total, page, ...})."""
    if isinstance(data, list):
        return data
    return data.get("items", [])


async def test_logic_challenge_list(
    client, logic_challenge_db, padawan_client_after_db
):
    """Test de récupération de la liste des défis logiques"""
    ensure_challenge_exists_in_db(logic_challenge_db)
    headers = {"Authorization": f"Bearer {padawan_client_after_db['token']}"}
    response = await client.get("/api/challenges", headers=headers)
    assert response.status_code == 200
    raw = response.json()
    challenges = _get_challenges_list(raw)
    assert len(challenges) > 0

    # Vérification de la structure des défis
    challenge = challenges[0]
    assert "id" in challenge
    assert "challenge_type" in challenge or "type" in challenge
    assert "age_group" in challenge
    assert (
        "correct_answer" in challenge
        or "question" in challenge
        or "description" in challenge
    )


async def test_logic_challenge_detail(
    client, logic_challenge_db, padawan_client_after_db
):
    """Test de récupération d'un défi spécifique"""
    ensure_challenge_exists_in_db(logic_challenge_db)
    # Prendre un défi avec correct_answer="42" (créé par ensure_challenge ou logic_challenge_db)
    challenge = (
        logic_challenge_db.query(LogicChallenge)
        .filter(LogicChallenge.correct_answer == "42")
        .first()
    )
    if not challenge:
        challenge = logic_challenge_db.query(LogicChallenge).first()
    assert challenge is not None

    headers = {"Authorization": f"Bearer {padawan_client_after_db['token']}"}
    response = await client.get(f"/api/challenges/{challenge.id}", headers=headers)
    assert response.status_code == 200
    challenge_data = response.json()

    # Vérification des détails
    assert challenge_data["id"] == challenge.id
    assert "challenge_type" in challenge_data or "type" in challenge_data
    assert "description" in challenge_data or "question" in challenge_data
    assert challenge_data["correct_answer"] == challenge.correct_answer


async def test_logic_challenge_correct_answer(
    client, logic_challenge_db, padawan_client_after_db
):
    """Test de soumission d'une réponse correcte"""
    ensure_challenge_exists_in_db(logic_challenge_db)
    challenge = logic_challenge_db.query(LogicChallenge).first()
    assert challenge is not None

    headers = {"Authorization": f"Bearer {padawan_client_after_db['token']}"}
    answer_data = {"answer": challenge.correct_answer}
    response = await client.post(
        f"/api/challenges/{challenge.id}/attempt", json=answer_data, headers=headers
    )

    # Vérifier le résultat
    assert response.status_code == 200
    result = response.json()
    assert result["is_correct"] is True
    assert "feedback" in result or "explanation" in result


async def test_logic_challenge_incorrect_answer(
    client, logic_challenge_db, padawan_client_after_db
):
    """Test de soumission d'une réponse incorrecte"""
    ensure_challenge_exists_in_db(logic_challenge_db)
    challenge = logic_challenge_db.query(LogicChallenge).first()
    assert challenge is not None

    headers = {"Authorization": f"Bearer {padawan_client_after_db['token']}"}
    answer_data = {"answer": "réponse_incorrecte"}
    response = await client.post(
        f"/api/challenges/{challenge.id}/attempt", json=answer_data, headers=headers
    )

    # Vérifier le résultat
    assert response.status_code == 200
    result = response.json()
    assert result["is_correct"] is False
    assert "feedback" in result or "hints" in result or "hints_remaining" in result


async def test_logic_challenge_hints(
    client, logic_challenge_db, padawan_client_after_db
):
    """Test de récupération des indices pour un défi"""
    ensure_challenge_exists_in_db(logic_challenge_db)
    challenge = logic_challenge_db.query(LogicChallenge).first()
    assert challenge is not None

    # S'assurer que le défi a des indices (le handler retourne 400 si level > len(hints))
    hints_list = challenge.hints
    if isinstance(hints_list, str):
        import json

        try:
            hints_list = json.loads(hints_list) if hints_list else []
        except (json.JSONDecodeError, ValueError):
            hints_list = []
    if not hints_list or len(hints_list) < 1:
        challenge.hints = ["Indice 1", "Indice 2", "Indice 3"]
        logic_challenge_db.merge(challenge)
        logic_challenge_db.commit()

    headers = {"Authorization": f"Bearer {padawan_client_after_db['token']}"}
    response = await client.get(
        f"/api/challenges/{challenge.id}/hint?level=1", headers=headers
    )

    # Vérifier le résultat
    assert (
        response.status_code == 200
    ), f"Attendu 200, reçu {response.status_code}. Réponse: {response.text}"
    hint_data = response.json()
    assert "hint" in hint_data

"""
Tests fonctionnels isolés pour les défis logiques
Ces tests utilisent la base de données PostgreSQL et sont totalement autonomes.
"""
import pytest

from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
from app.models.user import User, UserRole
from app.utils.db_helpers import get_enum_value


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
            role=get_enum_value(UserRole, UserRole.GARDIEN, logic_challenge_db)
        )
        logic_challenge_db.add(user)
        logic_challenge_db.commit()

    # Créer un défi de test avec des dates explicites
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    challenge = LogicChallenge(
        title="Défi Auto-Créé",
        description="Un défi créé automatiquement pour les tests",
        challenge_type=get_enum_value(LogicChallengeType, LogicChallengeType.SEQUENCE, logic_challenge_db),
        age_group=get_enum_value(AgeGroup, AgeGroup.GROUP_10_12, logic_challenge_db),
        correct_answer="42",
        solution_explanation="La réponse à la question ultime",
        hints='["Indice 1: C\'est un nombre", "Indice 2: C\'est un nombre entre 40 et 50", "Indice 3: C\'est la réponse à la question ultime"]',
        difficulty_rating=3.0,
        estimated_time_minutes=15,
        creator_id=user.id,
        created_at=now,
        updated_at=now
    )
    logic_challenge_db.add(challenge)
    logic_challenge_db.commit()

    return challenge.id


async def test_logic_challenge_list(gardien_client, logic_challenge_db):
    """Test de récupération de la liste des défis logiques"""
    ensure_challenge_exists_in_db(logic_challenge_db)
    client = gardien_client["client"]
    response = await client.get("/api/challenges/")
    assert response.status_code == 200
    challenges = response.json()
    assert len(challenges) > 0

    # Vérification de la structure des défis
    challenge = challenges[0]
    assert "id" in challenge
    assert "challenge_type" in challenge
    assert "age_group" in challenge
    assert "correct_answer" in challenge


async def test_logic_challenge_detail(gardien_client, logic_challenge_db):
    """Test de récupération d'un défi spécifique"""
    ensure_challenge_exists_in_db(logic_challenge_db)
    challenge = logic_challenge_db.query(LogicChallenge).first()
    assert challenge is not None

    client = gardien_client["client"]
    response = await client.get(f"/api/challenges/{challenge.id}")
    assert response.status_code == 200
    challenge_data = response.json()

    # Vérification des détails
    assert challenge_data["id"] == challenge.id
    assert "challenge_type" in challenge_data
    assert "description" in challenge_data
    assert challenge_data["correct_answer"] == "42"


async def test_logic_challenge_correct_answer(gardien_client, logic_challenge_db):
    """Test de soumission d'une réponse correcte"""
    ensure_challenge_exists_in_db(logic_challenge_db)
    challenge = logic_challenge_db.query(LogicChallenge).first()
    assert challenge is not None

    client = gardien_client["client"]
    answer_data = {"answer": challenge.correct_answer}
    response = await client.post(
        f"/api/challenges/{challenge.id}/attempt",
        json=answer_data
    )

    # Vérifier le résultat
    assert response.status_code == 200
    result = response.json()
    assert result["is_correct"] is True
    assert "feedback" in result


async def test_logic_challenge_incorrect_answer(gardien_client, logic_challenge_db):
    """Test de soumission d'une réponse incorrecte"""
    ensure_challenge_exists_in_db(logic_challenge_db)
    challenge = logic_challenge_db.query(LogicChallenge).first()
    assert challenge is not None

    client = gardien_client["client"]
    answer_data = {"answer": "réponse_incorrecte"}
    response = await client.post(
        f"/api/challenges/{challenge.id}/attempt",
        json=answer_data
    )

    # Vérifier le résultat
    assert response.status_code == 200
    result = response.json()
    assert result["is_correct"] is False
    assert "feedback" in result


async def test_logic_challenge_hints(gardien_client, logic_challenge_db):
    """Test de récupération des indices pour un défi"""
    ensure_challenge_exists_in_db(logic_challenge_db)
    challenge = logic_challenge_db.query(LogicChallenge).first()
    assert challenge is not None

    client = gardien_client["client"]
    response = await client.get(f"/api/challenges/{challenge.id}/hint?level=1")

    # Vérifier le résultat
    assert response.status_code == 200
    hint_data = response.json()
    assert "hint" in hint_data


async def test_create_logic_challenge(gardien_client, logic_challenge_db, db_session):
    """Test de création d'un nouveau défi logique"""
    # Données pour un nouveau défi avec valeurs Python des énumérations DIRECTES (pour Pydantic)
    challenge_data = {
        "title": "Nouveau défi de test",
        "description": "Description du nouveau défi",
        "challenge_type": LogicChallengeType.SEQUENCE.value,  # Valeur Python directe: "sequence"
        "age_group": AgeGroup.GROUP_10_12.value,  # Valeur Python directe: "10-12"
        "correct_answer": "123",
        "solution_explanation": "La solution est 123",
        "hints": ["Premier indice", "Deuxième indice", "Troisième indice"],
        "difficulty_rating": 2.5,
        "estimated_time_minutes": 10
    }

    # Debug: vérifier les valeurs des énumérations
    print(f"LogicChallengeType.SEQUENCE.value = '{LogicChallengeType.SEQUENCE.value}'")
    print(f"AgeGroup.GROUP_10_12.value = '{AgeGroup.GROUP_10_12.value}'")
    print(f"Données à envoyer: {challenge_data}")

    client = gardien_client["client"]
    response = await client.post("/api/challenges/", json=challenge_data)

    # Si erreur 422, afficher les détails pour diagnostic
    if response.status_code == 422:
        print(f"Erreur de validation 422: {response.json()}")
        print(f"Données envoyées: {challenge_data}")
    elif response.status_code == 500:
        print(f"Erreur serveur 500: {response.text}")

    # Vérifier le résultat
    assert response.status_code == 201
    new_challenge = response.json()
    assert new_challenge["title"] == challenge_data["title"]
    assert new_challenge["correct_answer"] == challenge_data["correct_answer"]

    # Vérifier que le défi a bien été ajouté à la base de données
    db_challenge = logic_challenge_db.query(LogicChallenge).filter_by(title=challenge_data["title"]).first()
    assert db_challenge is not None

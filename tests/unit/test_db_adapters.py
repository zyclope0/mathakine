"""
Tests unitaires pour les adaptateurs de base de données.
Cet exemple montre comment utiliser les fixtures adaptatives pour gérer
les différences entre SQLite et PostgreSQL.
"""
import unittest
from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy.orm import Session
import uuid

from app.models.user import User, UserRole
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
from app.services.logic_challenge_service import LogicChallengeService
from app.services.user_service import UserService
from app.utils.db_helpers import get_enum_value

def test_create_logic_challenge_with_adapted_enums(db_session: Session, logic_challenge_data):
    """
    Test de création d'un défi logique avec des valeurs d'enum adaptées.
    Cette approche fonctionne avec SQLite et PostgreSQL.
    """
    # Créer un défi logique avec les données adaptées
    challenge = LogicChallenge(**logic_challenge_data)
    db_session.add(challenge)
    db_session.commit()
    
    # Vérifier que le défi a été créé correctement
    retrieved_challenge = LogicChallengeService.get_challenge(db_session, challenge.id)
    
    assert retrieved_challenge is not None
    assert retrieved_challenge.title == logic_challenge_data["title"]
    assert retrieved_challenge.challenge_type == LogicChallengeType.SEQUENCE.value
    assert retrieved_challenge.age_group == AgeGroup.GROUP_10_12.value

def test_create_user_with_adapted_role(db_session: Session, user_data):
    """
    Test de création d'un utilisateur avec un rôle adapté selon la base de données.
    """
    # Créer un utilisateur avec le rôle adapté
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    
    # Vérifier que l'utilisateur a été créé correctement
    retrieved_user = UserService.get_user(db_session, user.id)
    
    assert retrieved_user is not None
    assert retrieved_user.username == user_data["username"]
    assert retrieved_user.role == UserRole.MAITRE

def test_complex_query_with_enum_filters(db_session: Session, logic_challenge_data, db_enum_values):
    """
    Test de requête avec filtrage sur des valeurs d'enum adaptées.
    """
    # Générer un ID unique pour ce test
    unique_id = uuid.uuid4().hex[:8]
    
    # Créer plusieurs défis logiques avec des titres uniques
    challenge1_data = logic_challenge_data.copy()
    challenge1_data["title"] = f"Sequence Challenge {unique_id}"
    challenge1 = LogicChallenge(**challenge1_data)
    
    # Créer un second défi avec un type différent
    challenge2_data = logic_challenge_data.copy()
    challenge2_data["title"] = f"Puzzle Challenge {unique_id}"
    challenge2_data["challenge_type"] = get_enum_value(LogicChallengeType, LogicChallengeType.PUZZLE.value, db_session)
    challenge2 = LogicChallenge(**challenge2_data)
    
    db_session.add_all([challenge1, challenge2])
    db_session.commit()
    
    # Stocker les IDs pour filtrage
    created_ids = [challenge1.id, challenge2.id]
    
    # Récupérer tous les défis et filtrer par nos IDs créés
    all_challenges = LogicChallengeService.list_challenges(db_session)
    
    # Filtrer par type et IDs créés dans ce test
    sequence_challenges = [
        c for c in all_challenges 
        if c.id in created_ids and c.challenge_type == LogicChallengeType.SEQUENCE.value
    ]
    
    puzzle_challenges = [
        c for c in all_challenges 
        if c.id in created_ids and c.challenge_type == LogicChallengeType.PUZZLE.value
    ]
    
    # Vérifier le filtrage
    assert len(sequence_challenges) == 1
    assert sequence_challenges[0].title == f"Sequence Challenge {unique_id}"
    
    assert len(puzzle_challenges) == 1
    assert puzzle_challenges[0].title == f"Puzzle Challenge {unique_id}"

def test_conditional_test_based_on_db_engine(db_session: Session, db_enum_values):
    """
    Exemple de test conditionnel qui s'adapte au moteur de base de données.
    """
    if db_enum_values.get("engine") == "postgresql":
        # Logique de test spécifique à PostgreSQL
        pytest.skip("Ce test est désactivé pour PostgreSQL")
    else:
        # Logique de test pour SQLite ou autres moteurs
        # Ici on pourrait tester des comportements spécifiques à SQLite
        assert db_enum_values["engine"] != "postgresql"
        
        # Exemple: SQLite tolère des valeurs qui ne font pas partie de l'enum
        challenge = LogicChallenge(
            title="SQLite Flexible Test",
            description="Test de la flexibilité de SQLite",
            challenge_type="non_existent_type",  # SQLite acceptera cette valeur
            age_group="invalid_age_group",       # SQLite acceptera cette valeur
            correct_answer="42",
            solution_explanation="Explication de test"
        )
        
        db_session.add(challenge)
        db_session.commit()
        
        # Vérifier que SQLite a accepté les valeurs
        retrieved = LogicChallengeService.get_challenge(db_session, challenge.id)
        assert retrieved.challenge_type == "non_existent_type"
        assert retrieved.age_group == "invalid_age_group"

def get_enum_value(enum_class, value, db_session):
    """
    Fonction d'aide pour obtenir la valeur correcte d'une énumération selon le moteur de base de données.
    Cette fonction ne devrait pas requêter directement l'enum_class mais plutôt comparer avec les valeurs.
    """
    # Vérifier si la valeur est déjà dans le format attendu
    if isinstance(value, str):
        return value
        
    # Sinon, retourner la valeur de l'énumération
    return value.value

def test_create_logic_challenge_with_adapted_enums_new(db_session: Session):
    """
    Test de création d'un défi logique avec des valeurs d'enum adaptées.
    Cette approche fonctionne avec SQLite et PostgreSQL.
    """
    # Créer un défi logique avec des valeurs enum adaptées
    challenge_data = {
        "title": "Test Adaptation Enum",
        "challenge_type": get_enum_value(LogicChallengeType, LogicChallengeType.SEQUENCE.value, db_session),
        "age_group": get_enum_value(AgeGroup, AgeGroup.GROUP_10_12.value, db_session),
        "description": "Test d'adaptation des enums",
        "correct_answer": "42",
        "solution_explanation": "La réponse à la grande question"
    }
    challenge = LogicChallenge(**challenge_data)
    db_session.add(challenge)
    db_session.commit()
    
    # Vérifier que le défi a été créé correctement
    retrieved_challenge = LogicChallengeService.get_challenge(db_session, challenge.id)
    
    assert retrieved_challenge is not None
    assert retrieved_challenge.title == challenge_data["title"]
    assert retrieved_challenge.challenge_type == LogicChallengeType.SEQUENCE.value
    assert retrieved_challenge.age_group == AgeGroup.GROUP_10_12.value 
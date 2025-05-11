"""
Tests unitaires pour les services de l'application.
Ce module teste les différents services métier de l'application.
"""
import pytest
from datetime import datetime
from sqlalchemy import text
from app.services.db_init_service import (
    create_tables,
    create_test_users,
    create_test_exercises,
    create_test_attempts,
    create_test_logic_challenges,
    populate_test_data,
    initialize_database
)
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallenge, LogicChallengeType




def test_create_test_users(empty_db_session):
    """Teste la création des utilisateurs de test."""
    # Appel de la fonction à tester
    create_test_users(empty_db_session)
    empty_db_session.commit()

    # Vérification que des utilisateurs ont été créés
    users = empty_db_session.query(User).all()
    assert len(users) > 0

    # Vérification des rôles
    roles = [user.role for user in users]
    assert UserRole.MAITRE in roles
    assert UserRole.PADAWAN in roles

    # Vérification d'un utilisateur Maître spécifique
    yoda = empty_db_session.query(User).filter(User.username == "maitre_yoda").first()
    assert yoda is not None
    assert yoda.role == UserRole.MAITRE
    assert yoda.email == "yoda@jedi-temple.sw"




def test_create_test_exercises(empty_db_session):
    """Teste la création des exercices de test."""
    # Créer d'abord un utilisateur Maître (créateur des exercices)
    create_test_users(empty_db_session)
    empty_db_session.commit()

    # Appel de la fonction à tester
    create_test_exercises(empty_db_session)
    empty_db_session.commit()

    # Vérification que des exercices ont été créés
    exercises = empty_db_session.query(Exercise).all()
    assert len(exercises) > 0

    # Vérification des types d'exercices
    exercise_types = [ex.exercise_type for ex in exercises]
    assert ExerciseType.ADDITION in exercise_types

    # Vérification des niveaux de difficulté
    difficulties = [ex.difficulty for ex in exercises]
    assert DifficultyLevel.INITIE in difficulties




def test_create_test_attempts(empty_db_session):
    """Teste la création des tentatives de test."""
    # Créer d'abord des utilisateurs et des exercices
    create_test_users(empty_db_session)
    create_test_exercises(empty_db_session)
    empty_db_session.commit()

    # Appel de la fonction à tester
    create_test_attempts(empty_db_session)
    empty_db_session.commit()

    # Vérification que des tentatives ont été créées
    attempts = empty_db_session.query(Attempt).all()
    assert len(attempts) > 0

    # Vérification des champs obligatoires de chaque tentative
    for attempt in attempts:
        assert attempt.id is not None
        assert attempt.user_id is not None
        assert attempt.exercise_id is not None
        assert attempt.is_correct in [True, False]
        assert attempt.attempt_number > 0




def test_create_test_logic_challenges(empty_db_session):
    """Teste la création des défis logiques de test."""
    # Créer d'abord des utilisateurs
    create_test_users(empty_db_session)
    empty_db_session.commit()

    # Appel de la fonction à tester
    create_test_logic_challenges(empty_db_session)
    empty_db_session.commit()

    # Vérification que des défis logiques ont été créés
    challenges = empty_db_session.query(LogicChallenge).all()
    assert len(challenges) > 0

    # Vérification des types de défis
    challenge_types = [ch.challenge_type for ch in challenges]
    assert LogicChallengeType.SEQUENCE in challenge_types

    # Vérification des champs obligatoires
    for challenge in challenges:
        assert challenge.title is not None
        assert challenge.description is not None
        assert challenge.correct_answer is not None




def test_populate_test_data(monkeypatch, empty_db_session):
    """Teste la fonction principale de remplissage de données de test."""
    # Mock pour éviter l'utilisation de get_db() et manipuler directement notre session de test


    def mock_get_db():
        yield empty_db_session

    monkeypatch.setattr("app.services.db_init_service.get_db", mock_get_db)

    # Appel de la fonction à tester
    populate_test_data()

    # Vérifications
    users = empty_db_session.query(User).all()
    exercises = empty_db_session.query(Exercise).all()
    attempts = empty_db_session.query(Attempt).all()
    challenges = empty_db_session.query(LogicChallenge).all()

    assert len(users) > 0
    assert len(exercises) > 0
    assert len(attempts) > 0
    assert len(challenges) > 0




def test_postgres_sequences(db_engine):
    """Teste que les séquences PostgreSQL sont correctement configurées."""
    # Ce test est exécuté uniquement si nous utilisons PostgreSQL
    db_url = db_engine.url.render_as_string(hide_password=False)

    if not db_url.startswith("postgresql"):
        pytest.skip("Ce test nécessite une base de données PostgreSQL")

    # Vérification des séquences pour les tables principales
    tables_to_check = ["users", "exercises", "attempts", "logic_challenges"]

    with db_engine.connect() as connection:
        for table in tables_to_check:
            # Vérifier si la séquence existe
            result = connection.execute(text(f"""
                SELECT pg_get_serial_sequence('{table}', 'id')
            """))
            sequence_name = result.scalar()

            assert sequence_name is not None, f"La séquence pour la table {table} n'existe pas"

            # Vérifier que la valeur de la séquence est cohérente
            result = connection.execute(text(f"""
                SELECT setval('{sequence_name}', (SELECT COALESCE(MAX(id), 0) FROM {table}), true)
            """))

            # Validation réussie si nous arrivons ici sans erreur

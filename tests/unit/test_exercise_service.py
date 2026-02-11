"""
Tests unitaires pour le service de gestion des exercices (ExerciseService).
"""
import pytest
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import MagicMock, patch
import time

from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.user import User, UserRole
from app.models.logic_challenge import LogicChallenge
from app.services.exercise_service import ExerciseService
from app.utils.db_helpers import get_enum_value, adapt_enum_for_db


def test_get_exercise(db_session):
    """Teste la récupération d'un exercice par son ID."""
    # Créer un exercice de test
    exercise = Exercise(
        title="Test Get Exercise",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        age_group="6-8",
        question="1+1=?",
        correct_answer="2"
    )
    db_session.add(exercise)
    db_session.commit()
    
    # Récupérer l'exercice via le service
    retrieved_exercise = ExerciseService.get_exercise(db_session, exercise.id)
    
    # Vérifications
    assert retrieved_exercise is not None
    assert retrieved_exercise.id == exercise.id
    assert retrieved_exercise.title == "Test Get Exercise"
    assert retrieved_exercise.exercise_type == ExerciseType.ADDITION.value
    assert retrieved_exercise.difficulty == DifficultyLevel.INITIE.value
    assert retrieved_exercise.question == "1+1=?"
    assert retrieved_exercise.correct_answer == "2"


def test_get_nonexistent_exercise(db_session):
    """Teste la récupération d'un exercice qui n'existe pas."""
    # Utiliser un ID qui n'existe pas
    nonexistent_id = 9999
    
    # Tenter de récupérer l'exercice
    exercise = ExerciseService.get_exercise(db_session, nonexistent_id)
    
    # Vérifier que None est retourné
    assert exercise is None


def test_list_exercises(db_session):
    """Teste la liste des exercices avec différents filtres."""
    # STRATÉGIE : Utiliser des identifiants uniques pour éviter les conflits
    unique_id = str(uuid.uuid4())[:8]
    
    # Compter les exercices avant nos ajouts
    initial_count = len(ExerciseService.list_exercises(db_session))
    
    # Créer des exercices de test avec des titres uniques
    exercises = [
        Exercise(
            title=f"Test Addition Initié {unique_id}",
            exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
            difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
            age_group="6-8",
            question="1+1=?",
            correct_answer="2",
            is_archived=False
        ),
        Exercise(
            title=f"Test Soustraction Padawan {unique_id}",
            exercise_type=get_enum_value(ExerciseType, ExerciseType.SOUSTRACTION.value, db_session),
            difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session),
            age_group="9-11",
            question="5-2=?",
            correct_answer="3",
            is_archived=False
        ),
        Exercise(
            title=f"Test Multiplication Chevalier {unique_id}",
            exercise_type=get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION.value, db_session),
            difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.CHEVALIER.value, db_session),
            age_group="12-14",
            question="5*5=?",
            correct_answer="25",
            is_archived=False
        ),
        Exercise(
            title=f"Test Addition Archivée {unique_id}",
            exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
            difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
            age_group="6-8",
            question="2+2=?",
            correct_answer="4",
            is_archived=True
        )
    ]
    
    for exercise in exercises:
        db_session.add(exercise)
    db_session.commit()
    
    # Tester la liste sans filtres - vérifier qu'on a 3 exercices de plus (non archivés)
    all_exercises = ExerciseService.list_exercises(db_session)
    final_count = len(all_exercises)
    assert final_count == initial_count + 3, f"Attendu {initial_count + 3}, obtenu {final_count}"
    
    # Filtrer nos exercices spécifiquement pour les tests détaillés
    our_exercises = [ex for ex in all_exercises if unique_id in ex.title]
    assert len(our_exercises) == 3  # L'exercice archivé ne devrait pas être inclus
    
    # Vérifier que les exercices attendus sont présents
    expected_titles = [f"Test Addition Initié {unique_id}", f"Test Soustraction Padawan {unique_id}", f"Test Multiplication Chevalier {unique_id}"]
    actual_titles = [ex.title for ex in our_exercises]
    for title in expected_titles:
        assert title in actual_titles
    
    # Tester avec filtre par type
    addition_exercises = ExerciseService.list_exercises(db_session, exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session))
    our_addition_exercises = [ex for ex in addition_exercises if unique_id in ex.title]
    assert len(our_addition_exercises) == 1
    assert our_addition_exercises[0].title == f"Test Addition Initié {unique_id}"
    
    # Tester avec filtre par difficulté
    padawan_exercises = ExerciseService.list_exercises(db_session, difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session))
    our_padawan_exercises = [ex for ex in padawan_exercises if unique_id in ex.title]
    assert len(our_padawan_exercises) == 1
    assert our_padawan_exercises[0].title == f"Test Soustraction Padawan {unique_id}"
    
    # Tester avec limite et offset
    limited_exercises = ExerciseService.list_exercises(db_session, limit=1)
    assert len(limited_exercises) == 1
    
    offset_exercises = ExerciseService.list_exercises(db_session, offset=1, limit=1)
    assert len(offset_exercises) == 1
    assert offset_exercises[0].id != limited_exercises[0].id


def test_create_exercise(db_session):
    """Teste la création d'un exercice."""
    # Données pour l'exercice
    exercise_data = {
        "title": "Test Create Exercise",
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.DIVISION.value, db_session),
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.MAITRE.value, db_session),
        "age_group": "15-17",
        "question": "10/2=?",
        "correct_answer": "5",
        "is_active": True
    }
    
    # Créer l'exercice via le service
    exercise = ExerciseService.create_exercise(db_session, exercise_data)
    
    # Vérifications
    assert exercise is not None
    assert exercise.id is not None
    assert exercise.title == "Test Create Exercise"
    assert exercise.exercise_type == ExerciseType.DIVISION.value
    assert exercise.difficulty == DifficultyLevel.MAITRE.value
    assert exercise.question == "10/2=?"
    assert exercise.correct_answer == "5"
    assert exercise.is_active is True
    assert exercise.is_archived is False  # Valeur par défaut


def test_update_exercise(db_session):
    """Teste la mise à jour d'un exercice."""
    # Créer un exercice initial
    exercise = Exercise(
        title="Test Original Title",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        age_group="6-8",
        question="Original question",
        correct_answer="Original answer"
    )
    db_session.add(exercise)
    db_session.commit()
    
    # Données de mise à jour
    update_data = {
        "title": "Test Updated Title",
        "question": "Updated question",
        "correct_answer": "Updated answer",
        "explanation": "Added explanation"
    }
    
    # Mettre à jour l'exercice via le service
    result = ExerciseService.update_exercise(db_session, exercise.id, update_data)
    
    # Vérifier que la mise à jour a réussi
    assert result is True
    
    # Récupérer l'exercice mis à jour
    updated_exercise = ExerciseService.get_exercise(db_session, exercise.id)
    
    # Vérifier les changements
    assert updated_exercise.title == "Test Updated Title"
    assert updated_exercise.question == "Updated question"
    assert updated_exercise.correct_answer == "Updated answer"
    assert updated_exercise.explanation == "Added explanation"
    # S'assurer que les champs non modifiés sont préservés
    assert updated_exercise.exercise_type == ExerciseType.ADDITION.value
    assert updated_exercise.difficulty == DifficultyLevel.INITIE.value


def test_update_nonexistent_exercise(db_session):
    """Teste la mise à jour d'un exercice qui n'existe pas."""
    # Utiliser un ID qui n'existe pas
    nonexistent_id = 9999
    
    # Tenter de mettre à jour l'exercice
    result = ExerciseService.update_exercise(db_session, nonexistent_id, {"title": "New Title"})
    
    # Vérifier que la mise à jour a échoué
    assert result is False


def test_archive_exercise(db_session):
    """Teste l'archivage d'un exercice."""
    # Créer un exercice initial
    exercise = Exercise(
        title="Test Exercise to Archive",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.CHEVALIER.value, db_session),
        age_group="12-14",
        question="Question to archive",
        correct_answer="Answer to archive",
        is_archived=False
    )
    db_session.add(exercise)
    db_session.commit()
    
    # Archiver l'exercice via le service
    result = ExerciseService.archive_exercise(db_session, exercise.id)
    
    # Vérifier que l'archivage a réussi
    assert result is True
    
    # Récupérer l'exercice et vérifier qu'il est archivé
    archived_exercise = db_session.query(Exercise).filter_by(id=exercise.id).first()
    assert archived_exercise.is_archived is True
    
    # Vérifier que l'exercice n'apparaît plus dans la liste des exercices actifs
    active_exercises = ExerciseService.list_exercises(db_session)
    assert archived_exercise not in active_exercises


def test_archive_nonexistent_exercise(db_session):
    """Teste l'archivage d'un exercice qui n'existe pas."""
    # Utiliser un ID qui n'existe pas
    nonexistent_id = 9999
    
    # Tenter d'archiver l'exercice
    result = ExerciseService.archive_exercise(db_session, nonexistent_id)
    
    # Vérifier que l'archivage a échoué
    assert result is False


def test_delete_exercise(db_session):
    """Teste la suppression physique d'un exercice."""
    # Créer un exercice initial
    exercise = Exercise(
        title="Test Exercise to Delete",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.DIVISION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session),
        age_group="9-11",
        question="10 ÷ 2 = ?",
        correct_answer="5"
    )
    db_session.add(exercise)
    db_session.commit()
    
    # Supprimer l'exercice via le service
    result = ExerciseService.delete_exercise(db_session, exercise.id)
    
    # Vérifier que la suppression a réussi
    assert result is True
    
    # Vérifier que l'exercice n'existe plus
    deleted_exercise = db_session.query(Exercise).filter_by(id=exercise.id).first()
    assert deleted_exercise is None


def test_delete_nonexistent_exercise(db_session):
    """Teste la suppression d'un exercice qui n'existe pas."""
    # Utiliser un ID qui n'existe pas
    nonexistent_id = 9999
    
    # Tenter de supprimer l'exercice
    result = ExerciseService.delete_exercise(db_session, nonexistent_id)
    
    # Vérifier que la suppression a échoué
    assert result is False


def test_delete_exercise_cascade(db_session):
    """Teste la suppression en cascade d'un exercice avec des tentatives."""
    # Créer un utilisateur avec un email unique pour éviter les contraintes
    unique_email = f"cascade_test_{int(time.time() * 1000)}@example.com"
    user = User(
        username=f"cascade_test_user_{int(time.time() * 1000)}",
        email=unique_email,
        hashed_password="hashed_password",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    db_session.add(user)
    db_session.commit()
    
    exercise = Exercise(
        title="Test Exercise with Attempts",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        age_group="6-8",
        question="5 + 5 = ?",
        correct_answer="10"
    )
    db_session.add(exercise)
    db_session.commit()
    
    # Créer des tentatives liées à l'exercice
    attempts = [
        Attempt(
            user_id=user.id,
            exercise_id=exercise.id,
            user_answer="10",
            is_correct=True,
            time_spent=5.0
        ),
        Attempt(
            user_id=user.id,
            exercise_id=exercise.id,
            user_answer="11",
            is_correct=False,
            time_spent=7.0
        )
    ]
    
    for attempt in attempts:
        db_session.add(attempt)
    db_session.commit()
    
    # Vérifier que les tentatives existent
    attempt_count = db_session.query(Attempt).filter_by(exercise_id=exercise.id).count()
    assert attempt_count == 2
    
    # Supprimer l'exercice via le service
    result = ExerciseService.delete_exercise(db_session, exercise.id)
    
    # Vérifier que la suppression a réussi
    assert result is True
    
    # Vérifier que l'exercice n'existe plus
    deleted_exercise = db_session.query(Exercise).filter_by(id=exercise.id).first()
    assert deleted_exercise is None
    
    # Vérifier que les tentatives ont également été supprimées (cascade)
    remaining_attempts = db_session.query(Attempt).filter_by(exercise_id=exercise.id).count()
    assert remaining_attempts == 0


def test_get_exercise_attempts(db_session):
    """Teste la récupération des tentatives pour un exercice."""
    # Utiliser un timestamp pour avoir des identifiants uniques
    timestamp = str(int(time.time() * 1000))
    
    # Créer un utilisateur avec des identifiants uniques
    user = User(
        username=f"test_attempts_user_{timestamp}",
        email=f"attempts_{timestamp}@example.com",
        hashed_password="test_password",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    db_session.add(user)
    db_session.flush()
    
    # Créer un exercice
    exercise = Exercise(
        title="Test Attempts Exercise",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.DIVISION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session),
        age_group="9-11",
        question="10/2=?",
        correct_answer="5"
    )
    db_session.add(exercise)
    db_session.flush()
    
    # Créer des tentatives pour cet exercice
    attempts = [
        Attempt(
            user_id=user.id,
            exercise_id=exercise.id,
            user_answer="3",
            is_correct=False
        ),
        Attempt(
            user_id=user.id,
            exercise_id=exercise.id,
            user_answer="4",
            is_correct=False
        ),
        Attempt(
            user_id=user.id,
            exercise_id=exercise.id,
            user_answer="5",
            is_correct=True
        )
    ]
    
    for attempt in attempts:
        db_session.add(attempt)
    db_session.commit()
    
    # Récupérer les tentatives via le service
    retrieved_attempts = ExerciseService.get_exercise_attempts(db_session, exercise.id)
    
    # Vérifications
    assert len(retrieved_attempts) == 3
    answers = [a.user_answer for a in retrieved_attempts]
    assert "3" in answers
    assert "4" in answers
    assert "5" in answers


def test_record_attempt(db_session):
    """Teste l'enregistrement d'une tentative pour un exercice."""
    # Utiliser un timestamp pour avoir des identifiants uniques
    timestamp = str(int(time.time() * 1000))
    
    # Créer un utilisateur avec des identifiants uniques
    user = User(
        username=f"test_record_user_{timestamp}",
        email=f"record_{timestamp}@example.com",
        hashed_password="test_password",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    db_session.add(user)
    
    # Créer un exercice
    exercise = Exercise(
        title="Test Record Exercise",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        age_group="6-8",
        question="2+2=?",
        correct_answer="4"
    )
    db_session.add(exercise)
    db_session.commit()
    
    # Données pour la tentative
    attempt_data = {
        "user_id": user.id,
        "exercise_id": exercise.id,
        "user_answer": "4",
        "is_correct": True,
        "time_spent": 12.5,
        "attempt_number": 1
    }
    
    # Enregistrer la tentative via le service
    attempt = ExerciseService.record_attempt(db_session, attempt_data)
    
    # Vérifications
    assert attempt is not None
    assert attempt.id is not None
    assert attempt.user_id == user.id
    assert attempt.exercise_id == exercise.id
    assert attempt.user_answer == "4"
    assert attempt.is_correct is True
    assert attempt.time_spent == 12.5
    assert attempt.attempt_number == 1


def test_record_attempt_nonexistent_exercise(db_session):
    """Teste l'enregistrement d'une tentative pour un exercice qui n'existe pas."""
    # Créer un utilisateur avec un email unique
    unique_id = uuid.uuid4().hex[:8]
    user = User(
        username=f"nonexistent_exercise_user_{unique_id}",
        email=f"nonexistent_exercise_{unique_id}@example.com",
        hashed_password="hashed_password",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    db_session.add(user)
    db_session.commit()
    
    # Données pour la tentative avec un exercice inexistant
    attempt_data = {
        "user_id": user.id,
        "exercise_id": 9999,  # ID inexistant
        "user_answer": "42",
        "is_correct": False,
        "time_spent": 30.0,
        "attempt_number": 1
    }
    
    # Tenter d'enregistrer la tentative
    attempt = ExerciseService.record_attempt(db_session, attempt_data)
    
    # Vérifier que l'enregistrement a échoué
    assert attempt is None


def test_list_exercises_with_exception():
    """Teste la liste des exercices avec une exception."""
    # Créer un mock pour la session
    mock_db = MagicMock()
    
    # Configurer le mock pour lever une exception
    mock_db.query.side_effect = SQLAlchemyError("Test d'erreur")
    
    # Appeler la méthode et vérifier qu'elle gère l'exception
    result = ExerciseService.list_exercises(mock_db)
    
    # Vérifier que le résultat est une liste vide
    assert result == []


@patch('app.utils.db_helpers.adapt_enum_for_db')
@patch('app.services.exercise_service.DatabaseAdapter')
def test_list_exercises_with_mock(mock_db_adapter, mock_adapt_enum):
    """
    Teste la liste des exercices avec des mocks pour éviter les problèmes 
    de compatibilité entre SQLite et PostgreSQL.
    """
    # Configurer le mock pour adapt_enum_for_db
    mock_adapt_enum.side_effect = lambda enum_name, value, db: f"ADAPTED_{value}"
    
    # Créer un mock pour la session
    mock_session = MagicMock()
    
    # Créer des mocks pour les exercices
    mock_exercises = []
    
    # Exercice 1: Addition de niveau Initié
    mock_exercise1 = MagicMock()
    mock_exercise1.id = 1
    mock_exercise1.title = "Addition Initié"
    mock_exercise1.exercise_type = "ADAPTED_ADDITION"
    mock_exercise1.difficulty = "ADAPTED_INITIE"
    mock_exercise1.question = "1+1=?"
    mock_exercise1.correct_answer = "2"
    mock_exercise1.is_archived = False
    mock_exercises.append(mock_exercise1)
    
    # Exercice 2: Soustraction de niveau Padawan
    mock_exercise2 = MagicMock()
    mock_exercise2.id = 2
    mock_exercise2.title = "Soustraction Padawan"
    mock_exercise2.exercise_type = "ADAPTED_SOUSTRACTION"
    mock_exercise2.difficulty = "ADAPTED_PADAWAN"
    mock_exercise2.question = "5-2=?"
    mock_exercise2.correct_answer = "3"
    mock_exercise2.is_archived = False
    mock_exercises.append(mock_exercise2)
    
    # Configurer le comportement du mock DatabaseAdapter.query
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = mock_exercises
    
    # 1. Tester sans filtres
    result = ExerciseService.list_exercises(mock_session)
    
    # Vérifier que la requête a été appelée correctement
    mock_session.query.assert_called_once()
    # La méthode list_exercises fait 1 appel filter par défaut:
    # 1. filter(Exercise.is_archived == False)
    assert mock_query.filter.call_count == 1
    
    # Vérifier les résultats
    assert len(result) == 2
    assert result[0].title == "Addition Initié"
    assert result[1].title == "Soustraction Padawan"
    
    # Réinitialiser les mocks pour le prochain test
    mock_session.reset_mock()
    mock_query.reset_mock()
    
    # 2. Tester avec filtre par type d'exercice
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_exercise1]
    
    result_by_type = ExerciseService.list_exercises(mock_session, exercise_type="ADDITION")
    
    # Vérifier que les filtres ont été appelés correctement
    assert mock_session.query.call_count == 1
    # Avec un filtre par type, on a 2 appels filter:
    # 1. filter(Exercise.is_archived == False)
    # 2. filter(Exercise.exercise_type == exercise_type)
    assert mock_query.filter.call_count == 2
    
    # Vérifier les résultats
    assert len(result_by_type) == 1
    assert result_by_type[0].title == "Addition Initié"


def test_record_attempt_with_exception():
    """Teste l'enregistrement d'une tentative avec une exception."""
    # Créer un mock pour la session
    mock_db = MagicMock()
    
    # Configurer le mock pour lever une exception
    mock_db.query.side_effect = SQLAlchemyError("Test d'erreur")
    
    # Données de tentative
    attempt_data = {
        "exercise_id": 1,
        "user_id": 1,
        "user_answer": "42",
        "is_correct": True
    }
    
    # Appeler la méthode et vérifier qu'elle gère l'exception
    result = ExerciseService.record_attempt(mock_db, attempt_data)
    
    # Vérifier que le résultat est None
    assert result is None


@patch('app.utils.db_helpers.adapt_enum_for_db')
@patch('app.services.exercise_service.DatabaseAdapter.create')
def test_create_exercise_with_mock(mock_db_create, mock_adapt_enum):
    """
    Teste la création d'un exercice avec des mocks pour éviter les problèmes 
    de compatibilité entre SQLite et PostgreSQL.
    """
    # Configurer le mock pour adapt_enum_for_db
    mock_adapt_enum.side_effect = lambda enum_name, value, db: f"ADAPTED_{value}"
    
    # Créer un mock pour la session
    mock_session = MagicMock()
    
    # Créer un mock pour l'exercice créé
    mock_exercise = MagicMock()
    mock_exercise.id = 1
    mock_exercise.title = "Test Create Exercise"
    mock_exercise.exercise_type = "ADAPTED_DIVISION"
    mock_exercise.difficulty = "ADAPTED_MAITRE"
    mock_exercise.question = "10/2=?"
    mock_exercise.correct_answer = "5"
    mock_exercise.is_active = True
    mock_exercise.is_archived = False
    
    # Configurer le mock DatabaseAdapter.create pour retourner l'exercice
    mock_db_create.return_value = mock_exercise
    
    # Données pour l'exercice
    exercise_data = {
        "title": "Test Create Exercise",
        "exercise_type": "DIVISION",
        "difficulty": "MAITRE",
        "question": "10/2=?",
        "correct_answer": "5",
        "is_active": True
    }
    
    # Créer l'exercice via le service
    exercise = ExerciseService.create_exercise(mock_session, exercise_data)
    
    # Vérifier que DatabaseAdapter.create a été appelé avec les bons arguments
    mock_db_create.assert_called_once_with(mock_session, Exercise, exercise_data)
    
    # Vérifications
    assert exercise is not None
    assert exercise.id == 1
    assert exercise.title == "Test Create Exercise"
    assert exercise.exercise_type == "ADAPTED_DIVISION"
    assert exercise.difficulty == "ADAPTED_MAITRE"
    assert exercise.question == "10/2=?"
    assert exercise.correct_answer == "5"
    assert exercise.is_active is True
    assert exercise.is_archived is False


@patch('app.utils.db_helpers.adapt_enum_for_db')
@patch('app.services.exercise_service.ExerciseService.get_exercise')
@patch('app.services.exercise_service.TransactionManager.transaction')
def test_record_attempt_with_mock(mock_transaction, mock_get_exercise, mock_adapt_enum):
    """
    Teste l'enregistrement d'une tentative avec des mocks pour éviter les problèmes 
    de compatibilité entre SQLite et PostgreSQL.
    """
    # Configurer le mock pour adapt_enum_for_db
    mock_adapt_enum.side_effect = lambda enum_name, value, db: f"ADAPTED_{value}"
    
    # Créer un mock pour la session
    mock_session = MagicMock()
    mock_transaction_ctx = MagicMock()
    mock_transaction.return_value = mock_transaction_ctx
    mock_transaction_ctx.__enter__.return_value = mock_session
    
    # Créer un mock pour l'exercice
    mock_exercise = MagicMock()
    mock_exercise.id = 1
    mock_exercise.title = "Exercise pour tentative"
    mock_exercise.exercise_type = "ADAPTED_ADDITION"
    mock_exercise.difficulty = "ADAPTED_INITIE"
    mock_exercise.question = "2+2=?"
    mock_exercise.correct_answer = "4"
    
    # Configurer le mock get_exercise pour retourner l'exercice
    mock_get_exercise.return_value = mock_exercise
    
    # Créer un mock pour la tentative créée
    mock_attempt = MagicMock()
    mock_attempt.id = 1
    mock_attempt.user_id = 1
    mock_attempt.exercise_id = 1
    mock_attempt.user_answer = "4"
    mock_attempt.is_correct = True
    mock_attempt.time_spent = 12.5
    
    # Simuler l'ajout à la session
    def side_effect_add(attempt):
        # Simuler la génération d'un ID et le retour de l'objet
        attempt.id = 1
        return None
    
    mock_session.add.side_effect = side_effect_add
    mock_session.flush.return_value = None
    
    # Données pour la tentative
    attempt_data = {
        "user_id": 1,
        "exercise_id": 1,
        "user_answer": "4",
        "is_correct": True,
        "time_spent": 12.5
    }
    
    # Enregistrer la tentative via le service
    attempt = ExerciseService.record_attempt(mock_session, attempt_data)
    
    # Vérifier que get_exercise a été appelé avec les bons arguments
    mock_get_exercise.assert_called_once_with(mock_session, 1)
    
    # Vérifier que session.add a été appelé
    mock_session.add.assert_called_once()
    
    # Vérifier que flush a été appelé
    mock_session.flush.assert_called_once()
    
    # Vérifications sur la tentative
    assert attempt is not None
    assert attempt.user_id == 1
    assert attempt.exercise_id == 1
    assert attempt.user_answer == "4"
    assert attempt.is_correct is True
    assert attempt.time_spent == 12.5 
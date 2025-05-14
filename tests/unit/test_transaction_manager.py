"""
Tests du gestionnaire de transactions et des suppressions en cascade.
"""
import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.db.transaction import TransactionManager
from app.db.adapter import DatabaseAdapter
from app.services.exercise_service import ExerciseService
from app.services.user_service import UserService
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt


def test_transaction_manager_commit(db_session):
    """Teste que le gestionnaire de transaction valide les modifications"""
    # Créer un utilisateur de test
    user_data = {
        "username": "test_commit",
        "email": "test_commit@example.com",
        "hashed_password": "hashed_password",
        "role": UserRole.PADAWAN
    }
    
    # Utiliser le gestionnaire de transaction
    with TransactionManager.transaction(db_session) as session:
        user = User(**user_data)
        session.add(user)
    
    # Vérifier que l'utilisateur a été créé (commit implicite)
    created_user = db_session.query(User).filter_by(username="test_commit").first()
    assert created_user is not None
    assert created_user.email == "test_commit@example.com"


def test_transaction_manager_rollback(db_session):
    """Teste que le gestionnaire de transaction effectue un rollback en cas d'erreur"""
    # Créer un utilisateur de test initial
    initial_user = User(
        username="initial_user",
        email="initial@example.com",
        hashed_password="hashed_password",
        role=UserRole.PADAWAN
    )
    db_session.add(initial_user)
    db_session.commit()
    
    initial_count = db_session.query(User).count()
    
    # Simuler une erreur pendant la transaction
    try:
        with TransactionManager.transaction(db_session) as session:
            user = User(
                username="will_rollback",
                email="will_rollback@example.com",
                hashed_password="hashed_password",
                role=UserRole.PADAWAN
            )
            session.add(user)
            
            # Provoquer une erreur
            raise ValueError("Test d'erreur pour forcer un rollback")
    except ValueError:
        pass
    
    # Vérifier que l'utilisateur n'a pas été créé (rollback implicite)
    final_count = db_session.query(User).count()
    assert final_count == initial_count
    assert db_session.query(User).filter_by(username="will_rollback").first() is None


def test_safe_delete_cascade(db_session):
    """Teste que la méthode safe_delete supprime correctement en cascade"""
    # Créer des données de test liées
    user = User(
        username="cascade_test",
        email="cascade@example.com",
        hashed_password="hashed_password", 
        role=UserRole.MAITRE
    )
    db_session.add(user)
    db_session.flush()
    
    exercise = Exercise(
        title="Test Exercise",
        creator_id=user.id,
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.PADAWAN,
        question="2 + 2 = ?",
        correct_answer="4"
    )
    db_session.add(exercise)
    db_session.flush()
    
    attempt = Attempt(
        user_id=user.id,
        exercise_id=exercise.id,
        answer="4",
        is_correct=True,
        time_spent=10.5
    )
    db_session.add(attempt)
    db_session.commit()
    
    # Vérifier que les objets existent
    assert db_session.query(User).filter_by(id=user.id).first() is not None
    assert db_session.query(Exercise).filter_by(id=exercise.id).first() is not None
    assert db_session.query(Attempt).filter_by(id=attempt.id).first() is not None
    
    # Supprimer l'utilisateur avec safe_delete
    result = TransactionManager.safe_delete(db_session, user)
    
    # Vérifier que la suppression a réussi
    assert result is True
    
    # Vérifier que l'utilisateur et ses dépendances ont été supprimés
    assert db_session.query(User).filter_by(id=user.id).first() is None
    assert db_session.query(Exercise).filter_by(id=exercise.id).first() is None
    assert db_session.query(Attempt).filter_by(id=attempt.id).first() is None


def test_safe_archive(db_session):
    """Teste que la méthode safe_archive marque correctement les objets comme archivés"""
    # Créer un exercice de test
    exercise = Exercise(
        title="Archive Test",
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.PADAWAN,
        question="3 + 3 = ?",
        correct_answer="6"
    )
    db_session.add(exercise)
    db_session.commit()
    
    # Vérifier que l'exercice n'est pas archivé par défaut
    assert exercise.is_archived is False
    
    # Archiver l'exercice
    result = TransactionManager.safe_archive(db_session, exercise)
    
    # Vérifier que l'archivage a réussi
    assert result is True
    
    # Rafraîchir l'objet depuis la base de données
    db_session.refresh(exercise)
    
    # Vérifier que l'exercice est maintenant archivé
    assert exercise.is_archived is True


def test_database_adapter_integration(db_session):
    """Teste l'intégration entre l'adaptateur de base de données et le gestionnaire de transaction"""
    # Créer un exercice de test
    exercise_data = {
        "title": "Adapter Test",
        "exercise_type": ExerciseType.MULTIPLICATION,
        "difficulty": DifficultyLevel.CHEVALIER,
        "question": "5 × 5 = ?",
        "correct_answer": "25"
    }
    
    # Utiliser l'adaptateur pour créer l'exercice
    exercise = DatabaseAdapter.create(db_session, Exercise, exercise_data)
    
    # Vérifier que l'exercice a été créé
    assert exercise is not None
    assert exercise.title == "Adapter Test"
    
    # Utiliser l'adaptateur pour mettre à jour l'exercice
    update_result = DatabaseAdapter.update(db_session, exercise, {"title": "Updated Title"})
    
    # Vérifier que la mise à jour a réussi
    assert update_result is True
    db_session.refresh(exercise)
    assert exercise.title == "Updated Title"
    
    # Utiliser l'adaptateur pour archiver l'exercice
    archive_result = DatabaseAdapter.archive(db_session, exercise)
    
    # Vérifier que l'archivage a réussi
    assert archive_result is True
    db_session.refresh(exercise)
    assert exercise.is_archived is True


def test_service_integration(db_session):
    """Teste l'intégration entre les services et le gestionnaire de transaction"""
    # Créer un utilisateur de test via le service
    user_data = {
        "username": "service_test",
        "email": "service@example.com",
        "hashed_password": "hashed_password",
        "role": UserRole.PADAWAN
    }
    user = UserService.create_user(db_session, user_data)
    
    # Vérifier que l'utilisateur a été créé
    assert user is not None
    assert user.username == "service_test"
    
    # Créer un exercice lié à cet utilisateur
    exercise_data = {
        "title": "Service Integration Test",
        "creator_id": user.id,
        "exercise_type": ExerciseType.DIVISION,
        "difficulty": DifficultyLevel.MAITRE,
        "question": "10 ÷ 2 = ?",
        "correct_answer": "5"
    }
    exercise = ExerciseService.create_exercise(db_session, exercise_data)
    
    # Vérifier que l'exercice a été créé
    assert exercise is not None
    assert exercise.title == "Service Integration Test"
    
    # Enregistrer une tentative
    attempt_data = {
        "user_id": user.id,
        "exercise_id": exercise.id,
        "answer": "5",
        "is_correct": True,
        "time_spent": 8.2
    }
    attempt = ExerciseService.record_attempt(db_session, attempt_data)
    
    # Vérifier que la tentative a été enregistrée
    assert attempt is not None
    assert attempt.is_correct is True
    
    # Supprimer l'utilisateur et vérifier les suppressions en cascade
    delete_result = UserService.delete_user(db_session, user.id)
    
    # Vérifier que la suppression a réussi
    assert delete_result is True
    
    # Vérifier que l'utilisateur et ses dépendances ont été supprimés
    assert db_session.query(User).filter_by(id=user.id).first() is None
    assert db_session.query(Exercise).filter_by(id=exercise.id).first() is None
    assert db_session.query(Attempt).filter_by(id=attempt.id).first() is None 
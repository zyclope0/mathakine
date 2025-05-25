#!/usr/bin/env python
"""
Test pour l'adaptateur EnhancedServerAdapter.
Vérifie que l'adaptateur fonctionne correctement avec le système de transaction.
"""
import sys
import os
import json
from datetime import datetime, timezone
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

# Ajouter le répertoire parent au path pour importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.user import User, UserRole
from app.db.transaction import TransactionManager
from app.core.constants import ExerciseTypes, DifficultyLevels
from app.services import ExerciseService, UserService, LogicChallengeService
from app.utils.db_helpers import get_enum_value, adapt_enum_for_db

from loguru import logger


def test_enhanced_server_adapter(db_session):
    """Test l'adaptateur EnhancedServerAdapter avec le système de transaction"""
    logger.info("Test de l'adaptateur EnhancedServerAdapter")

    # Obtenir une session de base de données
    db = EnhancedServerAdapter.get_db_session()

    try:
        # Préparation: Créer un utilisateur test si nécessaire
        logger.info("Préparation: Création d'un utilisateur test")
        from sqlalchemy.orm import Session
        from app.db.transaction import TransactionManager
        
        # Vérifier si l'utilisateur test existe déjà
        with TransactionManager.transaction(db) as session:
            test_user = session.query(User).filter(User.username == "test_user").first()
            if not test_user:
                # Créer un utilisateur test
                test_user = User(
                    username="test_user",
                    email="test@example.com",
                    hashed_password="test_password_hashed",
                    role=get_enum_value(UserRole, UserRole.PADAWAN.value, session)  # Adapter pour PostgreSQL
                )
                session.add(test_user)
        
        # S'assurer que l'utilisateur est créé
        user_id = test_user.id
        logger.info(f"Utilisateur test créé/trouvé avec ID {user_id}")
        
        # Test 1: Créer un exercice
        logger.info("Test 1: Création d'un exercice")
        exercise_data = {
            "title": "Test Exercise",
            "exercise_type": get_enum_value(ExerciseType, ExerciseType.ADDITION, db_session),
            "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE, db_session),
            "question": "Combien font 2 + 3 ?",
            "correct_answer": "5",
            "explanation": "2 + 3 = 5"
        }
        
        exercise = EnhancedServerAdapter.create_exercise(db, exercise_data)
        assert exercise is not None, "L'exercice n'a pas été créé"
        logger.info(f"Exercice créé avec ID {exercise['id']}")
        
        # Test 2: Récupérer l'exercice
        logger.info("Test 2: Récupération de l'exercice")
        retrieved_exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise['id'])
        assert retrieved_exercise is not None, "L'exercice n'a pas été récupéré"
        assert retrieved_exercise['title'] == "Test Exercise", "Le titre de l'exercice est incorrect"
        assert retrieved_exercise['exercise_type'] == ExerciseType.ADDITION.value, "Le type de l'exercice est incorrect"
        assert retrieved_exercise['difficulty'] == DifficultyLevel.INITIE.value, "La difficulté de l'exercice est incorrecte"
        logger.info("Exercice récupéré avec succès")
        
        # Test 3: Lister les exercices
        logger.info("Test 3: Liste des exercices")
        exercises = EnhancedServerAdapter.list_exercises(db, 
                                                      exercise_type="addition",
                                                      difficulty="initie")
        assert len(exercises) > 0, "Aucun exercice n'a été trouvé"
        logger.info(f"{len(exercises)} exercices trouvés")
        
        # Test 4: Enregistrer une tentative
        logger.info("Test 4: Enregistrement d'une tentative")
        attempt_data = {
            "user_id": user_id,  # Utiliser l'ID de l'utilisateur créé
            "exercise_id": exercise['id'],
            "user_answer": "3",
            "is_correct": True,
            "time_spent": 5.2
        }
        
        attempt = EnhancedServerAdapter.record_attempt(db, attempt_data)
        assert attempt is not None, "La tentative n'a pas été enregistrée"
        logger.info(f"Tentative enregistrée avec ID {attempt['id']}")
        
        # Test 5: Archiver l'exercice
        logger.info("Test 5: Archivage de l'exercice")
        success = EnhancedServerAdapter.archive_exercise(db, exercise['id'])
        assert success, "L'exercice n'a pas été archivé"
        
        # Vérifier que l'exercice est bien archivé
        archived_exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise['id'])
        assert archived_exercise['is_archived'], "L'exercice n'est pas marqué comme archivé"
        logger.info("Exercice archivé avec succès")
        
        logger.info("Tous les tests ont réussi !")
        
    finally:
        # Fermer la session dans tous les cas
        EnhancedServerAdapter.close_db_session(db)


def test_get_db_session():
    """Teste la méthode qui obtient une session de base de données"""
    # Tester que get_db_session retourne une session valide
    with patch('app.services.enhanced_server_adapter.SessionLocal') as mock_session_local:
        # Configure le mock
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        # Appeler la méthode
        result = EnhancedServerAdapter.get_db_session()
        
        # Vérifier le résultat
        assert result == mock_session
        mock_session_local.assert_called_once()


def test_close_db_session():
    """Teste la méthode qui ferme une session de base de données"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Appeler la méthode
    EnhancedServerAdapter.close_db_session(mock_session)
    
    # Vérifier que la méthode close a été appelée
    mock_session.close.assert_called_once()


def test_get_exercise_by_id(db_session):
    """Teste la récupération d'un exercice par son ID"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour l'exercice
    mock_exercise = MagicMock(spec=Exercise)
    mock_exercise.id = 1
    mock_exercise.title = "Test Exercise"
    mock_exercise.creator_id = 2
    mock_exercise.exercise_type = ExerciseType.ADDITION.value
    mock_exercise.difficulty = DifficultyLevel.INITIE.value
    mock_exercise.tags = "test,math"
    mock_exercise.question = "1+1=?"
    mock_exercise.correct_answer = "2"
    mock_exercise.choices = ["1", "2", "3", "4"]
    mock_exercise.explanation = "One plus one equals two"
    mock_exercise.hint = "Think simple"
    mock_exercise.image_url = None
    mock_exercise.audio_url = None
    mock_exercise.is_active = True
    mock_exercise.is_archived = False
    mock_exercise.view_count = 10
    mock_exercise.created_at = datetime.now(timezone.utc)
    mock_exercise.updated_at = None
    
    # Simuler le comportement du service
    with patch('app.services.enhanced_server_adapter.ExerciseService.get_exercise', return_value=mock_exercise) as mock_get_exercise:
        # Appeler la méthode
        result = EnhancedServerAdapter.get_exercise_by_id(mock_session, 1)
        
        # Vérifier le résultat
        assert result is not None
        assert result['id'] == 1
        assert result['title'] == "Test Exercise"
        assert result['exercise_type'] == ExerciseType.ADDITION.value
        assert result['difficulty'] == DifficultyLevel.INITIE.value
        
        # Vérifier que la méthode du service a été appelée
        mock_get_exercise.assert_called_once_with(mock_session, 1)


def test_get_exercise_by_id_not_found():
    """Teste la récupération d'un exercice qui n'existe pas"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Simuler le comportement du service - l'exercice n'existe pas
    with patch('app.services.enhanced_server_adapter.ExerciseService.get_exercise', return_value=None) as mock_get_exercise:
        # Appeler la méthode
        result = EnhancedServerAdapter.get_exercise_by_id(mock_session, 999)
        
        # Vérifier le résultat
        assert result is None
        
        # Vérifier que la méthode du service a été appelée
        mock_get_exercise.assert_called_once_with(mock_session, 999)


def test_list_exercises(db_session):
    """Teste la liste des exercices avec filtrage"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer des mocks pour les exercices
    mock_exercise1 = MagicMock(spec=Exercise)
    mock_exercise1.id = 1
    mock_exercise1.title = "Addition"
    mock_exercise1.creator_id = 2
    mock_exercise1.exercise_type = ExerciseType.ADDITION.value
    mock_exercise1.difficulty = DifficultyLevel.INITIE.value
    mock_exercise1.question = "1+1=?"
    mock_exercise1.correct_answer = "2"
    mock_exercise1.choices = ["1", "2", "3", "4"]
    mock_exercise1.is_active = True
    mock_exercise1.is_archived = False
    
    mock_exercise2 = MagicMock(spec=Exercise)
    mock_exercise2.id = 2
    mock_exercise2.title = "Multiplication"
    mock_exercise2.creator_id = 2
    mock_exercise2.exercise_type = ExerciseType.MULTIPLICATION.value
    mock_exercise2.difficulty = DifficultyLevel.PADAWAN.value
    mock_exercise2.question = "2*2=?"
    mock_exercise2.correct_answer = "4"
    mock_exercise2.choices = ["2", "3", "4", "5"]
    mock_exercise2.is_active = True
    mock_exercise2.is_archived = False
    
    # Simuler le comportement du service
    with patch('app.services.enhanced_server_adapter.ExerciseService.list_exercises', 
                return_value=[mock_exercise1, mock_exercise2]) as mock_list_exercises:
        # Appeler la méthode
        result = EnhancedServerAdapter.list_exercises(
            mock_session, 
            exercise_type=None, 
            difficulty=None, 
            limit=10
        )
        
        # Vérifier le résultat
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[0]['title'] == "Addition"
        assert result[0]['exercise_type'] == ExerciseType.ADDITION.value
        assert result[1]['id'] == 2
        assert result[1]['title'] == "Multiplication"
        assert result[1]['exercise_type'] == ExerciseType.MULTIPLICATION.value
        
        # Vérifier que la méthode du service a été appelée
        mock_list_exercises.assert_called_once_with(
            mock_session, 
            exercise_type=None, 
            difficulty=None, 
            limit=10
        )


def test_create_exercise(db_session):
    """Teste la création d'un exercice"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour l'exercice
    mock_exercise = MagicMock(spec=Exercise)
    mock_exercise.id = 1
    mock_exercise.title = "New Exercise"
    mock_exercise.creator_id = 2
    mock_exercise.exercise_type = ExerciseType.ADDITION.value
    mock_exercise.difficulty = DifficultyLevel.INITIE.value
    mock_exercise.question = "1+1=?"
    mock_exercise.correct_answer = "2"
    mock_exercise.choices = ["1", "2", "3", "4"]
    mock_exercise.is_active = True
    mock_exercise.is_archived = False
    
    # Données d'entrée
    exercise_data = {
        'title': "New Exercise",
        'creator_id': 2,
        'exercise_type': ExerciseType.ADDITION.value,
        'difficulty': DifficultyLevel.INITIE.value,
        'question': "1+1=?",
        'correct_answer': "2",
        'choices': ["1", "2", "3", "4"]
    }
    
    # Simuler le comportement du service
    with patch('app.services.enhanced_server_adapter.ExerciseService.create_exercise', 
                return_value=mock_exercise) as mock_create_exercise:
        # Appeler la méthode
        result = EnhancedServerAdapter.create_exercise(mock_session, exercise_data)
        
        # Vérifier le résultat
        assert result is not None
        assert result['id'] == 1
        assert result['title'] == "New Exercise"
        assert result['exercise_type'] == ExerciseType.ADDITION.value
        
        # Vérifier que la méthode du service a été appelée
        mock_create_exercise.assert_called_once_with(mock_session, exercise_data)


def test_create_generated_exercise(db_session):
    """Teste la création d'un exercice généré"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour l'exercice
    mock_exercise = MagicMock(spec=Exercise)
    mock_exercise.id = 1
    mock_exercise.title = "Generated Exercise"
    mock_exercise.creator_id = None
    mock_exercise.exercise_type = ExerciseType.ADDITION.value
    mock_exercise.difficulty = DifficultyLevel.INITIE.value
    mock_exercise.question = "1+1=?"
    mock_exercise.correct_answer = "2"
    mock_exercise.choices = ["1", "2", "3", "4"]
    mock_exercise.explanation = "Basic addition"
    mock_exercise.is_active = True
    mock_exercise.is_archived = False
    mock_exercise.ai_generated = True
    
    # Simuler le comportement du service
    with patch('app.services.enhanced_server_adapter.ExerciseService.create_exercise', 
                return_value=mock_exercise) as mock_create_exercise:
        # Appeler la méthode
        result = EnhancedServerAdapter.create_generated_exercise(
            mock_session,
            exercise_type="addition",
            difficulty="initie",
            title="Generated Exercise",
            question="1+1=?",
            correct_answer="2",
            choices=["1", "2", "3", "4"],
            explanation="Basic addition",
            ai_generated=True
        )
        
        # Vérifier le résultat
        assert result is not None
        assert result['id'] == 1
        assert result['title'] == "Generated Exercise"
        assert result['exercise_type'] == ExerciseType.ADDITION.value
        
        # Vérifier que la méthode du service a été appelée avec les bons arguments
        mock_create_exercise.assert_called_once()
        # Vérifier les arguments du call
        call_args = mock_create_exercise.call_args[0][1]  # Premier arg est la session, second est le dict
        assert call_args['title'] == "Generated Exercise"
        assert call_args['exercise_type'] == "addition"
        assert call_args['difficulty'] == "initie"
        assert call_args['question'] == "1+1=?"
        assert call_args['correct_answer'] == "2"
        assert call_args['choices'] == ["1", "2", "3", "4"]
        assert call_args['explanation'] == "Basic addition"
        assert call_args['ai_generated'] == True


def test_update_exercise():
    """Teste la mise à jour d'un exercice"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Données d'entrée
    exercise_data = {
        'title': "Updated Exercise",
        'question': "Updated question?",
        'correct_answer': "Updated answer"
    }
    
    # Simuler le comportement du service - mise à jour réussie
    with patch('app.services.enhanced_server_adapter.ExerciseService.update_exercise', 
                return_value=True) as mock_update_exercise:
        # Appeler la méthode
        result = EnhancedServerAdapter.update_exercise(mock_session, 1, exercise_data)
        
        # Vérifier le résultat
        assert result is True
        
        # Vérifier que la méthode du service a été appelée
        mock_update_exercise.assert_called_once_with(mock_session, 1, exercise_data)


def test_archive_exercise():
    """Teste l'archivage d'un exercice"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Simuler le comportement du service - archivage réussi
    with patch('app.services.enhanced_server_adapter.ExerciseService.archive_exercise', 
                return_value=True) as mock_archive_exercise:
        # Appeler la méthode
        result = EnhancedServerAdapter.archive_exercise(mock_session, 1)
        
        # Vérifier le résultat
        assert result is True
        
        # Vérifier que la méthode du service a été appelée
        mock_archive_exercise.assert_called_once_with(mock_session, 1)


def test_record_attempt():
    """Teste l'enregistrement d'une tentative d'exercice"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour la tentative
    mock_attempt = MagicMock(spec=Attempt)
    mock_attempt.id = 1
    mock_attempt.user_id = 2
    mock_attempt.exercise_id = 3
    mock_attempt.user_answer = "2"
    mock_attempt.is_correct = True
    mock_attempt.time_spent = 10.5
    mock_attempt.attempt_number = 1
    mock_attempt.created_at = datetime.now(timezone.utc)
    
    # Données d'entrée
    attempt_data = {
        'user_id': 2,
        'exercise_id': 3,
        'user_answer': "2",
        'time_spent': 10.5
    }
    
    # Simuler le comportement du service
    with patch('app.services.enhanced_server_adapter.ExerciseService.record_attempt', 
                return_value=mock_attempt) as mock_record_attempt:
        # Appeler la méthode
        result = EnhancedServerAdapter.record_attempt(mock_session, attempt_data)
        
        # Vérifier le résultat
        assert result is not None
        assert result['id'] == 1
        assert result['user_id'] == 2
        assert result['exercise_id'] == 3
        assert result['user_answer'] == "2"
        assert result['is_correct'] == True
        
        # Vérifier que la méthode du service a été appelée
        mock_record_attempt.assert_called_once_with(mock_session, attempt_data)


def test_get_user_stats():
    """Teste la récupération des statistiques d'un utilisateur"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Données simulées de retour
    user_stats = {
        'total_exercises': 50,
        'completed_exercises': 30,
        'success_rate': 0.8,
        'types': {
            'addition': {'total': 20, 'correct': 18},
            'multiplication': {'total': 15, 'correct': 10}
        },
        'difficulties': {
            'initie': {'total': 15, 'correct': 14},
            'padawan': {'total': 20, 'correct': 15}
        }
    }
    
    # Simuler le comportement du service
    with patch('app.services.enhanced_server_adapter.UserService.get_user_stats', 
                return_value=user_stats) as mock_get_user_stats:
        # Appeler la méthode
        result = EnhancedServerAdapter.get_user_stats(mock_session, 1)
        
        # Vérifier le résultat
        assert result is not None
        assert result['total_exercises'] == 50
        assert result['completed_exercises'] == 30
        assert result['success_rate'] == 0.8
        assert 'addition' in result['types']
        assert 'initie' in result['difficulties']
        
        # Vérifier que la méthode du service a été appelée
        mock_get_user_stats.assert_called_once_with(mock_session, 1)


def test_execute_raw_query():
    """Teste l'exécution d'une requête SQL brute"""
    # Créer un adaptateur avec un mock pour la méthode execute_query
    adapter = EnhancedServerAdapter()
    
    # Créer des données de test
    mock_results = [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"}
    ]
    
    # Patcher la méthode execute_query du DatabaseAdapter
    with patch('app.db.adapter.DatabaseAdapter.execute_query', return_value=mock_results):
        # Requête test
        test_query = "SELECT id, name FROM items WHERE category = %s"
        test_params = ('test',)
        
        # Exécuter la requête
        results = adapter.execute_raw_query(test_query, test_params)
        
        # Vérifications
        assert len(results) == 2
        assert results[0]['id'] == 1
        assert results[0]['name'] == "Item 1"
        assert results[1]['id'] == 2
        assert results[1]['name'] == "Item 2"


if __name__ == "__main__":
    logger.info("Début des tests de l'adaptateur EnhancedServerAdapter")
    test_enhanced_server_adapter()
    logger.info("Fin des tests") 
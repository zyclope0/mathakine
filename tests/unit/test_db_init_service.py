import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
import app.services.db_init_service as db_init_service
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup

@pytest.fixture
def mock_db_session():
    """Fixture pour créer un mock de session de base de données"""
    mock_session = MagicMock(spec=Session)
    return mock_session

def test_create_tables():
    """Test la création des tables"""
    with patch('app.services.db_init_service.Base.metadata.create_all') as mock_create_all:
        db_init_service.create_tables()
        mock_create_all.assert_called_once()

def test_create_test_users(mock_db_session):
    """Test la création des utilisateurs de test"""
    # Simuler qu'aucun utilisateur n'existe
    mock_db_session.query().count.return_value = 0
    
    # Appeler la fonction de création d'utilisateurs
    with patch('app.services.db_init_service.User') as mock_user:
        db_init_service.create_test_users(mock_db_session)
        
        # Vérifier que add_all est appelé
        mock_db_session.add_all.assert_called_once()
        
        # Vérifier que flush est appelé
        mock_db_session.flush.assert_called_once()

def test_create_test_exercises(mock_db_session):
    """Test la création des exercices de test"""
    # Simuler qu'aucun exercice n'existe
    mock_db_session.query().count.return_value = 0
    
    # Simuler que l'utilisateur Yoda existe
    mock_yoda = MagicMock()
    mock_yoda.id = 1
    mock_db_session.query().filter().first.return_value = mock_yoda
    
    # Appeler la fonction de création d'exercices
    with patch('app.services.db_init_service.Exercise') as mock_exercise:
        db_init_service.create_test_exercises(mock_db_session)
        
        # Vérifier que add_all est appelé
        mock_db_session.add_all.assert_called_once()
        
        # Vérifier que flush est appelé
        mock_db_session.flush.assert_called_once()

def test_create_test_logic_challenges(mock_db_session):
    """Test la création des défis logiques de test"""
    # Simuler qu'aucun défi logique n'existe
    mock_db_session.query().count.return_value = 0
    
    # Simuler que l'utilisateur Yoda existe
    mock_yoda = MagicMock()
    mock_yoda.id = 1
    mock_db_session.query().filter().first.return_value = mock_yoda
    
    # Appeler la fonction de création de défis logiques
    with patch('app.services.db_init_service.LogicChallenge') as mock_challenge:
        db_init_service.create_test_logic_challenges(mock_db_session)
        
        # Vérifier que add_all est appelé
        mock_db_session.add_all.assert_called_once()
        
        # Vérifier que flush est appelé
        mock_db_session.flush.assert_called_once()

def test_create_test_attempts(mock_db_session):
    """Test la création des tentatives de test"""
    # Simuler qu'aucune tentative n'existe
    mock_db_session.query().count.return_value = 0
    
    # Simuler que l'utilisateur Padawan existe
    mock_padawan = MagicMock()
    mock_padawan.id = 2
    
    # Simuler que les exercices existent
    mock_exercise = MagicMock()
    mock_exercise.id = 1
    mock_exercise.correct_answer = "4"
    mock_exercise.choices = ["2", "3", "4", "5"]
    
    # Configurer les retours des requêtes
    mock_db_session.query().filter().first.return_value = mock_padawan
    mock_db_session.query().all.return_value = [mock_exercise]
    
    # Appeler la fonction de création de tentatives
    with patch('app.services.db_init_service.Attempt') as mock_attempt:
        db_init_service.create_test_attempts(mock_db_session)
        
        # Vérifier que add_all est appelé
        mock_db_session.add_all.assert_called_once()
        
        # Vérifier que flush est appelé
        mock_db_session.flush.assert_called_once()

def test_initialize_database():
    """Test l'initialisation complète de la base de données"""
    # Patcher les fonctions du module
    with patch('app.services.db_init_service.create_tables') as mock_create_tables, \
         patch('app.services.db_init_service.populate_test_data') as mock_populate_test_data:
        
        # Appeler la fonction d'initialisation
        db_init_service.initialize_database()
        
        # Vérifier que chaque fonction est appelée
        mock_create_tables.assert_called_once()
        mock_populate_test_data.assert_called_once() 
"""
Tests unitaires pour la validation des réponses aux exercices.
Ce fichier contient des tests généraux pour la fonctionnalité de soumission de réponses.
Pour les tests spécifiques aux différents formats de réponses, voir test_answer_validation_formats.py.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import asyncio

from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.user import User, UserRole
from app.services.exercise_service import ExerciseService
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.utils.db_helpers import get_enum_value
from server.handlers.exercise_handlers import submit_answer
from tests.unit.test_utils import create_mock_request


@pytest.mark.asyncio
async def test_submit_correct_answer(db_session):
    """Teste la soumission d'une réponse correcte à un exercice."""
    # Créer un mock d'exercice
    mock_exercise = {
        "id": 1,
        "question": "5 + 3 = ?",
        "correct_answer": "8",
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        "explanation": "L'addition de 5 et 3 est égale à 8"
    }
    
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Préparer un mock pour record_attempt
    mock_attempt = {
        "id": 1,
        "is_correct": True,
        "user_answer": "8",
        "user_id": 1,
        "exercise_id": 1,
        "time_spent": 15.5
    }
    
    # Préparer les données de requête
    request_data = {
        "exercise_id": 1,
        "selected_answer": "8",
        "time_spent": 15.5
    }
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        "is_authenticated": True
    }
    
    # Créer une requête mock
    mock_request = create_mock_request(request_data)
    
    # Exécuter la fonction avec nos mocks
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session', return_value=mock_db):
        with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_exercise_by_id', return_value=mock_exercise):
            with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.record_attempt', return_value=mock_attempt):
                with patch('server.handlers.exercise_handlers.get_current_user', return_value=mock_user):
                    response = await submit_answer(mock_request)
    
    # Analyser la réponse JSON directement à partir du body
    result_json = json.loads(response.body.decode('utf-8'))
    
    # Vérifications
    assert response.status_code == 200
    assert result_json["is_correct"] is True
    assert "correct_answer" in result_json
    assert "explanation" in result_json


@pytest.mark.asyncio
async def test_submit_incorrect_answer(db_session):
    """Teste la soumission d'une réponse incorrecte à un exercice."""
    # Créer un mock d'exercice
    mock_exercise = {
        "id": 1,
        "question": "7 × 6 = ?",
        "correct_answer": "42",
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION.value, db_session),
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session),
        "explanation": "La multiplication de 7 par 6 est égale à 42"
    }
    
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Préparer un mock pour record_attempt
    mock_attempt = {
        "id": 2,
        "is_correct": False,
        "user_answer": "36",
        "user_id": 1,
        "exercise_id": 1,
        "time_spent": 25.0
    }
    
    # Préparer les données de requête
    request_data = {
        "exercise_id": 1,
        "selected_answer": "36",
        "time_spent": 25.0
    }
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        "is_authenticated": True
    }
    
    # Créer une requête mock
    mock_request = create_mock_request(request_data)
    
    # Exécuter la fonction avec nos mocks
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session', return_value=mock_db):
        with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_exercise_by_id', return_value=mock_exercise):
            with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.record_attempt', return_value=mock_attempt):
                with patch('server.handlers.exercise_handlers.get_current_user', return_value=mock_user):
                    response = await submit_answer(mock_request)
    
    # Analyser la réponse JSON directement à partir du body
    result_json = json.loads(response.body.decode('utf-8'))
    
    # Vérifications
    assert response.status_code == 200
    assert result_json["is_correct"] is False
    assert result_json["correct_answer"] == "42"
    assert "explanation" in result_json


@pytest.mark.asyncio
async def test_submit_answer_nonexistent_exercise(db_session):
    """Teste la soumission d'une réponse à un exercice inexistant."""
    # Créer un mock de session de base de données qui retourne None (exercice non trouvé)
    mock_db = MagicMock()
    
    # Préparer les données de requête
    request_data = {
        "exercise_id": 999,  # ID inexistant
        "selected_answer": "42",
        "time_spent": 10.0
    }
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        "is_authenticated": True
    }
    
    # Créer une requête mock
    mock_request = create_mock_request(request_data)
    
    # Exécuter la fonction avec nos mocks
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session', return_value=mock_db):
        with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_exercise_by_id', return_value=None):
            with patch('server.handlers.exercise_handlers.get_current_user', return_value=mock_user):
                response = await submit_answer(mock_request)
    
    # Analyser la réponse JSON directement à partir du body
    result_json = json.loads(response.body.decode('utf-8'))
    
    # Vérifications
    assert response.status_code == 404
    assert "error" in result_json


@pytest.mark.asyncio
async def test_submit_answer_missing_parameters(db_session):
    """Teste la soumission d'une réponse avec des paramètres manquants."""
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        "is_authenticated": True
    }
    
    # Cas 1: ID d'exercice manquant
    request_data_1 = {
        "selected_answer": "42",
        "time_spent": 10.0
    }
    
    # Créer une requête mock
    mock_request_1 = create_mock_request(request_data_1)
    
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session', return_value=mock_db):
        with patch('server.handlers.exercise_handlers.get_current_user', return_value=mock_user):
            response_1 = await submit_answer(mock_request_1)
    
    # Cas 2: Réponse manquante
    request_data_2 = {
        "exercise_id": 1,
        "time_spent": 10.0
    }
    
    # Créer une requête mock
    mock_request_2 = create_mock_request(request_data_2)
    
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session', return_value=mock_db):
        with patch('server.handlers.exercise_handlers.get_current_user', return_value=mock_user):
            response_2 = await submit_answer(mock_request_2)
    
    # Vérifications
    result_json_1 = json.loads(response_1.body.decode('utf-8'))
    result_json_2 = json.loads(response_2.body.decode('utf-8'))
    
    assert response_1.status_code == 400
    assert "error" in result_json_1
    assert response_2.status_code == 400
    assert "error" in result_json_2


@pytest.mark.asyncio
async def test_submit_answer_unauthenticated(db_session):
    """Teste la soumission d'une réponse sans authentification."""
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Préparer les données de requête
    request_data = {
        "exercise_id": 1,
        "selected_answer": "8",
        "time_spent": 10.0
    }
    
    # Créer une requête mock
    mock_request = create_mock_request(request_data)
    
    # Simuler un utilisateur non authentifié
    mock_user = None
    
    # Exécuter la fonction avec nos mocks
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session', return_value=mock_db):
        with patch('server.handlers.exercise_handlers.get_current_user', return_value=mock_user):
            response = await submit_answer(mock_request)
    
    # Analyser la réponse JSON directement à partir du body
    result_json = json.loads(response.body.decode('utf-8'))
    
    # Vérifications
    assert response.status_code == 401
    assert "error" in result_json


@pytest.mark.asyncio
async def test_submit_answer_with_attempt_error(db_session):
    """Teste la gestion des erreurs lors de l'enregistrement d'une tentative."""
    # Créer un mock d'exercice
    mock_exercise = {
        "id": 1,
        "question": "5 + 3 = ?",
        "correct_answer": "8",
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        "explanation": "L'addition de 5 et 3 est égale à 8"
    }
    
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Définir record_attempt pour qu'il lève une exception
    def mock_record_attempt_error(*args, db_session, **kwargs):
        raise Exception("Erreur lors de l'enregistrement de la tentative")
    
    # Préparer les données de requête
    request_data = {
        "exercise_id": 1,
        "selected_answer": "8",
        "time_spent": 10.0
    }
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        "is_authenticated": True
    }
    
    # Créer une requête mock
    mock_request = create_mock_request(request_data)
    
    # Exécuter la fonction avec nos mocks
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session', return_value=mock_db):
        with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_exercise_by_id', return_value=mock_exercise):
            with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.record_attempt', side_effect=mock_record_attempt_error):
                with patch('server.handlers.exercise_handlers.get_current_user', return_value=mock_user):
                    response = await submit_answer(mock_request)
    
    # Analyser la réponse JSON directement à partir du body
    result_json = json.loads(response.body.decode('utf-8'))
    
    # Vérifications
    assert response.status_code == 500
    assert "error" in result_json


@pytest.mark.asyncio
async def test_submit_answer_internal_server_error(db_session):
    """Teste la gestion des erreurs internes du serveur."""
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Préparer les données de requête
    request_data = {
        "exercise_id": 1,
        "selected_answer": "8",
        "time_spent": 10.0
    }
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        "is_authenticated": True
    }
    
    # Simuler une erreur interne inattendue
    def mock_get_db_session_error(*args, **kwargs):
        raise Exception("Erreur interne du serveur inattendue")
    
    # Créer une requête mock
    mock_request = create_mock_request(request_data)
    
    # Exécuter la fonction avec nos mocks
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.get_db_session', side_effect=mock_get_db_session_error):
        with patch('server.handlers.exercise_handlers.get_current_user', return_value=mock_user):
            response = await submit_answer(mock_request)
    
    # Analyser la réponse JSON directement à partir du body
    result_json = json.loads(response.body.decode('utf-8'))
    
    # Vérifications
    assert response.status_code == 500
    assert "error" in result_json 
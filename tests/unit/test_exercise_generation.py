"""
Tests unitaires pour la génération d'exercices.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import asyncio
from fastapi.responses import JSONResponse

from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.services.exercise_service import ExerciseService
from app.utils.db_helpers import get_enum_value
from server.handlers.exercise_handlers import generate_exercise
from tests.unit.test_utils import create_mock_request


@pytest.mark.asyncio
async def test_generate_addition_exercise_initie_async(db_session):
    """Teste la génération d'un exercice d'addition pour le niveau Initié."""
    # Simuler un exercice créé
    mock_exercise = {
        "id": 1,
        "title": "Addition d'Initié",
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        "question": "3 + 4 = ?",
        "correct_answer": "7",
        "choices": ["5", "6", "7", "8"]
    }
    
    # Mock pour les méthodes de EnhancedServerAdapter
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.create_generated_exercise', return_value=mock_exercise):
        # Préparer les paramètres de requête
        query_params = {
            "type": get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
            "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)
        }
        
        # Créer une requête mockée
        mock_request = create_mock_request(query_params=query_params)
        
        # Appeler le handler
        response = await generate_exercise(mock_request)
        
        # Vérifier la redirection
        assert response.status_code == 303
        assert response.headers["location"] == "/exercises?generated=true"


@pytest.mark.asyncio
async def test_generate_multiplication_exercise_chevalier(db_session):
    """Teste la génération d'un exercice de multiplication pour le niveau Chevalier."""
    # Simuler un exercice créé
    mock_exercise = {
        "id": 2,
        "title": "Multiplication de Chevalier",
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION.value, db_session),
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.CHEVALIER.value, db_session),
        "question": "12 × 8 = ?",
        "correct_answer": "96",
        "choices": ["86", "92", "96", "106"]
    }
    
    # Mock pour les méthodes de EnhancedServerAdapter
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.create_generated_exercise', return_value=mock_exercise):
        # Préparer les paramètres de requête
        query_params = {
            "type": get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION.value, db_session),
            "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.CHEVALIER.value, db_session)
        }
        
        # Créer une requête mockée
        mock_request = create_mock_request(query_params=query_params)
        
        # Appeler le handler
        response = await generate_exercise(mock_request)
        
        # Vérifier la redirection
        assert response.status_code == 303
        assert response.headers["location"] == "/exercises?generated=true"


@pytest.mark.asyncio
async def test_generate_division_exercise_padawan(db_session):
    """Teste la génération d'un exercice de division pour le niveau Padawan."""
    # Simuler un exercice créé
    mock_exercise = {
        "id": 3,
        "title": "Division de Padawan",
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.DIVISION.value, db_session),
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session),
        "question": "45 ÷ 9 = ?",
        "correct_answer": "5",
        "choices": ["3", "4", "5", "6"]
    }
    
    # Mock pour les méthodes de EnhancedServerAdapter
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.create_generated_exercise', return_value=mock_exercise):
        # Préparer les paramètres de requête
        query_params = {
            "type": get_enum_value(ExerciseType, ExerciseType.DIVISION.value, db_session),
            "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session)
        }
        
        # Créer une requête mockée
        mock_request = create_mock_request(query_params=query_params)
        
        # Appeler le handler
        response = await generate_exercise(mock_request)
        
        # Vérifier la redirection
        assert response.status_code == 303
        assert response.headers["location"] == "/exercises?generated=true"


@pytest.mark.asyncio
async def test_generate_exercise_invalid_type(db_session):
    """Teste la génération d'un exercice avec un type invalide."""
    # La fonction real traite les types invalides en les remplaçant par un type par défaut
    # et retourne toujours une redirection vers la page d'exercices
    
    # Simuler un exercice créé avec un type par défaut
    mock_exercise = {
        "id": 5,
        "title": "Exercice mathématique",
        "exercise_type": "invalid_type",  # Le type est normalisé mais stocké tel quel
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        "question": "Calcule 4 + 9",
        "correct_answer": "13",
        "choices": ["13", "12", "14", "15"]
    }
    
    # Mock pour les méthodes de EnhancedServerAdapter
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.create_generated_exercise', return_value=mock_exercise):
        # Préparer les paramètres de requête
        query_params = {
            "type": "INVALID_TYPE",
            "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)
        }
        
        # Créer une requête mockée
        mock_request = create_mock_request(query_params=query_params)
        
        # Appeler le handler
        response = await generate_exercise(mock_request)
        
        # Vérifier la redirection (c'est le comportement attendu même avec un type invalide)
        assert response.status_code == 303
        assert response.headers["location"] == "/exercises?generated=true"


@pytest.mark.asyncio
async def test_generate_exercise_invalid_difficulty(db_session):
    """Teste la génération d'un exercice avec une difficulté invalide."""
    # La fonction real traite les difficultés invalides en les remplaçant par une difficulté par défaut
    # et retourne toujours une redirection vers la page d'exercices
    
    # Simuler un exercice créé avec une difficulté par défaut
    mock_exercise = {
        "id": 6,
        "title": "Addition galactique",
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        "difficulty": "invalid_difficulty",  # La difficulté est normalisée mais stockée telle quelle
        "question": "Calcule 34 + 34",
        "correct_answer": "68",
        "choices": ["68", "72", "65", "1156"]
    }
    
    # Mock pour les méthodes de EnhancedServerAdapter
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.create_generated_exercise', return_value=mock_exercise):
        # Préparer les paramètres de requête
        query_params = {
            "type": get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
            "difficulty": "INVALID_DIFFICULTY"
        }
        
        # Créer une requête mockée
        mock_request = create_mock_request(query_params=query_params)
        
        # Appeler le handler
        response = await generate_exercise(mock_request)
        
        # Vérifier la redirection (c'est le comportement attendu même avec une difficulté invalide)
        assert response.status_code == 303
        assert response.headers["location"] == "/exercises?generated=true"


@pytest.mark.asyncio
async def test_generate_exercise_missing_parameters(db_session):
    """Teste la génération d'un exercice avec des paramètres manquants."""
    # La fonction real traite les paramètres manquants en utilisant des valeurs par défaut
    # et retourne toujours une redirection vers la page d'exercices
    
    # Simuler un exercice créé avec des valeurs par défaut
    mock_exercise = {
        "id": 7,
        "title": "Addition galactique",
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),  # Type par défaut en cas de paramètre manquant
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),  # Difficulté par défaut
        "question": "Calcule 6 + 7",
        "correct_answer": "13",
        "choices": ["13", "14", "12", "42"]
    }
    
    # Mock pour les méthodes de EnhancedServerAdapter
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.create_generated_exercise', return_value=mock_exercise):
        # Cas 1: Type manquant
        # Préparer les paramètres de requête
        query_params_1 = {
            "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)
        }
        
        # Créer une requête mockée
        mock_request_1 = create_mock_request(query_params=query_params_1)
        
        # Appeler le handler
        response_1 = await generate_exercise(mock_request_1)
        
        # Vérifier la redirection (c'est le comportement attendu même avec un type manquant)
        assert response_1.status_code == 303
        assert response_1.headers["location"] == "/exercises?generated=true"
        
        # Cas 2: Difficulté manquante
        # Préparer les paramètres de requête
        query_params_2 = {
            "type": get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session)
        }
        
        # Créer une requête mockée
        mock_request_2 = create_mock_request(query_params=query_params_2)
        
        # Appeler le handler
        response_2 = await generate_exercise(mock_request_2)
        
        # Vérifier la redirection (c'est le comportement attendu même avec une difficulté manquante)
        assert response_2.status_code == 303
        assert response_2.headers["location"] == "/exercises?generated=true"


@pytest.mark.asyncio
async def test_generate_exercise_service_error(db_session):
    """Teste la gestion des erreurs de service lors de la génération d'exercice."""
    # Simuler un exercice avec erreur de service
    mock_response = JSONResponse(
        {"error": "Erreur de service"},
        status_code=500
    )
    
    # Mock pour simuler une erreur lors de la création de l'exercice
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.create_generated_exercise', side_effect=Exception("Erreur simulée du service")):
        # Préparer les paramètres de requête
        query_params = {
            "type": get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
            "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)
        }
        
        # Créer une requête mockée
        mock_request = create_mock_request(query_params=query_params)
        
        # Appeler le handler avec app.state.templates pour éviter les erreurs
        mock_request.app = MagicMock()
        mock_request.app.state.templates = MagicMock()
        mock_request.app.state.templates.TemplateResponse.return_value = mock_response
        
        # Appeler le handler
        response = await generate_exercise(mock_request)
        
        # Vérifier que nous avons une erreur de service
        assert response.status_code == 500
        assert "error" in json.loads(response.body)


@pytest.mark.asyncio
async def test_generate_mixed_exercise_maitre_async(db_session):
    """Teste la génération d'un exercice mixte pour le niveau Maître."""
    # Simuler un exercice créé
    mock_exercise = {
        "id": 4,
        "title": "Exercice Mixte de Maître",
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.MIXTE.value, db_session),
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.MAITRE.value, db_session),
        "question": "(125 + 75) × 4 ÷ 2 = ?",
        "correct_answer": "400",
        "choices": ["380", "400", "420", "450"],
        "explanation": "On calcule d'abord 125 + 75 = 200, puis 200 × 4 = 800, et enfin 800 ÷ 2 = 400."
    }
    
    # Mock pour les méthodes de EnhancedServerAdapter
    with patch('app.services.enhanced_server_adapter.EnhancedServerAdapter.create_generated_exercise', return_value=mock_exercise):
        # Préparer les paramètres de requête
        query_params = {
            "type": get_enum_value(ExerciseType, ExerciseType.MIXTE.value, db_session),
            "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.MAITRE.value, db_session)
        }
        
        # Créer une requête mockée
        mock_request = create_mock_request(query_params=query_params)
        
        # Appeler le handler
        response = await generate_exercise(mock_request)
        
        # Vérifier la redirection
        assert response.status_code == 303
        assert response.headers["location"] == "/exercises?generated=true"
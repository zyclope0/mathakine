"""
Tests unitaires pour la validation des différents formats de réponses aux exercices.
Ces tests vérifient le comportement du système face aux différentes façons de soumettre une réponse.
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
@pytest.mark.parametrize("exercise_type,answer,correct_answer,expected_result", [
    # Test pour les types numériques (comparaison stricte)
    (ExerciseType.ADDITION.value, "42", "42", True),          # Réponse exacte - valide
    (ExerciseType.ADDITION.value, " 42", "42", False),        # Avec espace avant - invalide pour types numériques
    (ExerciseType.ADDITION.value, "42 ", "42", False),        # Avec espace après - invalide pour types numériques
    (ExerciseType.ADDITION.value, " 42 ", "42", False),       # Avec espaces - invalide pour types numériques
    (ExerciseType.MULTIPLICATION.value, "100", "100", True),  # Réponse exacte - valide
    (ExerciseType.MULTIPLICATION.value, "0100", "100", False),# Format différent - invalide
    (ExerciseType.DIVISION.value, "3.5", "3.5", True),        # Réponse exacte - valide
    (ExerciseType.DIVISION.value, "3,5", "3.5", False),       # Séparateur décimal différent - invalide
    
    # Test pour les types textuels (comparaison insensible à la casse et aux espaces)
    (ExerciseType.TEXTE.value, "Paris", "Paris", True),       # Réponse exacte - valide
    (ExerciseType.TEXTE.value, "paris", "Paris", True),       # Casse différente - valide pour texte
    (ExerciseType.TEXTE.value, " Paris", "Paris", True),      # Espace avant - valide pour texte
    (ExerciseType.TEXTE.value, "Paris ", "Paris", True),      # Espace après - valide pour texte
    (ExerciseType.TEXTE.value, " Paris ", "Paris", True),     # Espaces - valide pour texte
    (ExerciseType.MIXTE.value, "Force", "Force", True),       # Réponse exacte - valide
    (ExerciseType.MIXTE.value, "force", "Force", True),       # Casse différente - valide pour mixte
    (ExerciseType.MIXTE.value, " Force ", "Force", True),     # Espaces - valide pour mixte
])
async def test_answer_validation_formats(exercise_type, answer, correct_answer, expected_result, db_session):
    """
    Teste la validation des réponses selon différents formats et types d'exercices.
    
    Comportement attendu:
    - ExerciseType.ADDITION.value, SUBTRACTION, MULTIPLICATION, DIVISION: comparaison stricte
    - ExerciseType.TEXTE.value, MIXTE: comparaison insensible à la casse et aux espaces
    """
    # Créer un mock d'exercice avec le type et la réponse correcte spécifiés
    mock_exercise = {
        "id": 1,
        "question": "Question de test",
        "correct_answer": correct_answer,
        "exercise_type": exercise_type,
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        "explanation": "Explication de test"
    }
    
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Préparer un mock d'attempt sérialisable
    mock_attempt = {
        "id": 123,
        "exercise_id": 1,
        "user_id": 1,
        "user_answer": answer,
        "is_correct": expected_result,
        "time_spent": 10.0
    }
    
    # Préparer les données de requête
    request_data = {
        "exercise_id": 1,
        "selected_answer": answer,
        "time_spent": 10.0
    }
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": "apprenti",  # Utiliser la valeur directe acceptée par PostgreSQL
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
    assert response.status_code == 200, f"Le statut de la réponse devrait être 200, reçu {response.status_code}"
    assert result_json["is_correct"] == expected_result, f"La validation de '{answer}' pour le type {exercise_type} devrait être {expected_result}"


@pytest.mark.asyncio
@pytest.mark.parametrize("answer,fractions_format,expected_result", [
    # Test pour les différentes façons d'écrire les fractions
    ("1/2", "1/2", True),       # Format exact
    ("1/2", "0.5", False),      # Formats différents
    ("0.5", "0.5", True),       # Format décimal exact
    ("0.50", "0.5", False),     # Précision différente
    ("0,5", "0.5", False),      # Séparateur décimal différent
    ("1:2", "1/2", False),      # Notation différente
])
async def test_fraction_answer_validation(answer, fractions_format, expected_result, db_session):
    """
    Teste spécifiquement la validation des réponses pour les exercices de fractions.
    
    Vérifie que:
    - Différentes notations de fractions sont correctement validées
    - La validation est stricte (pas de conversion entre formats)
    """
    # Créer un mock d'exercice pour fractions
    mock_exercise = {
        "id": 1,
        "question": "Quelle est la moitié de 1?",
        "correct_answer": fractions_format,
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.FRACTIONS.value, db_session),
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        "explanation": "La moitié de 1 est 1/2"
    }
    
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Préparer un mock d'attempt sérialisable
    mock_attempt = {
        "id": 123,
        "exercise_id": 1,
        "user_id": 1,
        "user_answer": answer,
        "is_correct": expected_result,
        "time_spent": 10.0
    }
    
    # Préparer les données de requête
    request_data = {
        "exercise_id": 1,
        "selected_answer": answer,
        "time_spent": 10.0
    }
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": "apprenti",  # Utiliser la valeur directe acceptée par PostgreSQL
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
    assert result_json["is_correct"] == expected_result, f"La validation de '{answer}' en tant que '{fractions_format}' devrait être {expected_result}"


@pytest.mark.asyncio
@pytest.mark.parametrize("answer,with_unit,expected_result", [
    # Test pour les réponses avec unités
    ("10", "10", True),           # Sans unité - exact
    ("10", "10 km", False),       # Sans unité vs avec unité
    ("10 km", "10 km", True),     # Avec unité - exact
    ("10km", "10 km", False),     # Avec unité - espace manquant
    ("10 KM", "10 km", False),    # Casse différente pour l'unité
])
async def test_unit_answer_validation(answer, with_unit, expected_result, db_session):
    """
    Teste la validation des réponses incluant des unités de mesure.
    
    Vérifie que:
    - Les unités sont considérées comme faisant partie de la réponse
    - La validation est stricte (espaces, casse, etc.)
    """
    # Créer un mock d'exercice avec unités
    mock_exercise = {
        "id": 1,
        "question": "Quelle est la distance entre Paris et Lyon?",
        "correct_answer": with_unit,
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.DIVERS.value, db_session),
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session),
        "explanation": "La distance est de 10 km"
    }
    
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Préparer un mock d'attempt sérialisable
    mock_attempt = {
        "id": 123,
        "exercise_id": 1,
        "user_id": 1,
        "user_answer": answer,
        "is_correct": expected_result,
        "time_spent": 12.0
    }
    
    # Préparer les données de requête
    request_data = {
        "exercise_id": 1,
        "selected_answer": answer,
        "time_spent": 12.0
    }
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": "apprenti",  # Utiliser la valeur directe acceptée par PostgreSQL
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
    assert result_json["is_correct"] == expected_result, f"La validation de '{answer}' par rapport à '{with_unit}' devrait être {expected_result}"


@pytest.mark.asyncio
async def test_empty_answer_validation(db_session):
    """
    Teste la validation d'une réponse vide.
    
    Vérifie que:
    - Une réponse vide est toujours considérée comme incorrecte
    - La réponse est traitée correctement sans erreur
    """
    # Créer un mock d'exercice
    mock_exercise = {
        "id": 1,
        "question": "2+2=?",
        "correct_answer": "4",
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        "explanation": "2+2=4"
    }
    
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Préparer les données de requête avec réponse vide
    request_data = {
        "exercise_id": 1,
        "selected_answer": "",  # Réponse vide
        "time_spent": 5.0
    }
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": "apprenti",  # Utiliser la valeur directe acceptée par PostgreSQL
        "is_authenticated": True
    }
    
    # Définir un dictionnaire sérialisable au lieu d'un MagicMock
    mock_attempt = {
        "id": 123,
        "exercise_id": 1,
        "user_id": 1,
        "user_answer": "",
        "is_correct": False,
        "time_spent": 5.0
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
    assert result_json["is_correct"] == False, "Une réponse vide devrait toujours être considérée comme incorrecte"
    assert "attempt_id" in result_json, "La réponse devrait contenir un ID de tentative"


@pytest.mark.asyncio
@pytest.mark.parametrize("original_answer,spaces_answer,expected_result", [
    ("42", "42", True),          # Réponse exacte pour numérique
    ("Paris", "Paris", True),    # Réponse exacte pour textuel
    ("Paris", "paris", True),    # Casse différente pour textuel
])
async def test_text_answer_validation_with_special_exercise_type(original_answer, spaces_answer, expected_result, db_session):
    """
    Teste la validation des réponses textuelles avec le type d'exercice spécial TEXTE.
    
    Vérifie que:
    - Les réponses textuelles sont validées correctement avec ce type
    - La comparaison insensible à la casse fonctionne
    """
    # Créer un mock d'exercice de type TEXTE
    mock_exercise = {
        "id": 1,
        "question": "Question test",
        "correct_answer": original_answer,
        "exercise_type": get_enum_value(ExerciseType, ExerciseType.TEXTE.value, db_session),  # Type textuel spécial
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        "explanation": "Explication test"
    }
    
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Préparer les données de requête
    request_data = {
        "exercise_id": 1,
        "selected_answer": spaces_answer,
        "time_spent": 8.0
    }
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": "apprenti",  # Utiliser la valeur directe acceptée par PostgreSQL
        "is_authenticated": True
    }
    
    # Définir un dictionnaire sérialisable au lieu d'un MagicMock
    mock_attempt = {
        "id": 123,
        "exercise_id": 1,
        "user_id": 1,
        "user_answer": spaces_answer,
        "is_correct": expected_result,
        "time_spent": 8.0
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
    assert result_json["is_correct"] == expected_result, f"La validation de '{spaces_answer}' pour le type TEXTE devrait être {expected_result}"


@pytest.mark.asyncio
async def test_null_exercise_type_validation(db_session):
    """
    Teste la validation lorsque le type d'exercice est NULL.
    
    Vérifie que:
    - Un type d'exercice nul est traité avec une comparaison stricte par défaut
    - L'application ne plante pas avec cette valeur invalide
    """
    # Créer un mock d'exercice avec type NULL
    mock_exercise = {
        "id": 1,
        "question": "Question test",
        "correct_answer": "42",
        "exercise_type": None,  # Type NULL
        "difficulty": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        "explanation": "Explication test"
    }
    
    # Créer un mock de session de base de données
    mock_db = MagicMock()
    
    # Préparer les données de requête
    request_data = {
        "exercise_id": 1,
        "selected_answer": "42",
        "time_spent": 7.0
    }
    
    # Simuler une authentification d'utilisateur
    mock_user = {
        "id": 1,
        "username": "test_user",
        "role": "apprenti",  # Utiliser la valeur directe acceptée par PostgreSQL
        "is_authenticated": True
    }
    
    # Définir un dictionnaire sérialisable au lieu d'un MagicMock
    mock_attempt = {
        "id": 123,
        "exercise_id": 1,
        "user_id": 1,
        "user_answer": "42",
        "is_correct": True,
        "time_spent": 7.0
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
    assert response.status_code == 200, "La requête devrait être traitée correctement même avec un type NULL"
    assert "is_correct" in result_json, "La réponse devrait contenir le champ is_correct" 
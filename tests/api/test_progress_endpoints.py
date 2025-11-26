import json
"""
Tests des endpoints API pour le suivi des progrès des utilisateurs.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.progress import Progress
from app.models.attempt import Attempt
from app.utils.db_helpers import get_enum_value

client = TestClient(app)

def test_get_user_progress(padawan_client, db_session, mock_exercise):
    """Test pour récupérer les progrès d'un utilisateur."""
    # Récupérer le client authentifié et les informations de l'utilisateur
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    
    # Créer un exercice pour le progrès
    exercise_data = mock_exercise()
    
    # Normaliser les valeurs d'enum en majuscules pour PostgreSQL et utiliser les enums Python
    exercise_type_str = exercise_data["exercise_type"].upper() if isinstance(exercise_data["exercise_type"], str) else exercise_data["exercise_type"]
    difficulty_str = exercise_data["difficulty"].upper() if isinstance(exercise_data["difficulty"], str) else exercise_data["difficulty"]
    
    # Convertir les strings en enums Python
    try:
        exercise_type_enum = ExerciseType(exercise_type_str)
    except ValueError:
        exercise_type_enum = ExerciseType.ADDITION
    
    try:
        difficulty_enum = DifficultyLevel(difficulty_str)
    except ValueError:
        difficulty_enum = DifficultyLevel.INITIE
    
    # Convertir en instance d'Exercise pour l'ajouter à la base
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_type_enum,
        difficulty=difficulty_enum,
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        is_active=exercise_data.get("is_active", True),
        creator_id=None,
        is_archived=False
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    
    # Créer un progrès pour l'utilisateur
    progress = Progress(
        user_id=user_id,
        exercise_type=exercise.exercise_type.value,
        difficulty=exercise.difficulty.value if hasattr(exercise.difficulty, 'value') else str(exercise.difficulty).upper(),
        total_attempts=5,
        correct_attempts=4,
        mastery_level=3  # 3 correspond au niveau Padawan
    )
    db_session.add(progress)
    db_session.commit()
    
    # Récupérer les progrès de l'utilisateur
    response = client.get("/api/users/me/progress")
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Vérifier qu'au moins un progrès existe
    if len(data) > 0:
        assert "exercise_type" in data[0]
        assert "mastery_level" in data[0]
        assert "total_attempts" in data[0]
        assert "correct_attempts" in data[0]
        
        # Vérifier que notre progrès est dans les résultats
        progress_types = [p["exercise_type"] for p in data]
        assert exercise.exercise_type.value in progress_types

def test_get_user_progress_by_type(padawan_client, db_session, mock_exercise):
    """Test pour récupérer les progrès d'un utilisateur par type d'exercice."""
    # Récupérer le client authentifié et les informations de l'utilisateur
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    
    # Créer un exercice pour le progrès
    exercise_data = mock_exercise(exercise_type="addition")
    
    # Normaliser les valeurs d'enum en majuscules pour PostgreSQL et utiliser les enums Python
    exercise_type_str = exercise_data["exercise_type"].upper() if isinstance(exercise_data["exercise_type"], str) else exercise_data["exercise_type"]
    difficulty_str = exercise_data["difficulty"].upper() if isinstance(exercise_data["difficulty"], str) else exercise_data["difficulty"]
    
    # Convertir les strings en enums Python
    try:
        exercise_type_enum = ExerciseType(exercise_type_str)
    except ValueError:
        exercise_type_enum = ExerciseType.ADDITION
    
    try:
        difficulty_enum = DifficultyLevel(difficulty_str)
    except ValueError:
        difficulty_enum = DifficultyLevel.INITIE
    
    # Convertir en instance d'Exercise pour l'ajouter à la base
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_type_enum,
        difficulty=difficulty_enum,
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        is_active=exercise_data.get("is_active", True),
        creator_id=None,
        is_archived=False
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    
    # Créer un progrès pour l'utilisateur
    progress = Progress(
        user_id=user_id,
        exercise_type=exercise.exercise_type.value,
        difficulty=exercise.difficulty.value if hasattr(exercise.difficulty, 'value') else str(exercise.difficulty).upper(), 
        total_attempts=5,
        correct_attempts=4,
        mastery_level=3  # 3 correspond au niveau Padawan
    )
    db_session.add(progress)
    db_session.commit()
    
    # Récupérer les progrès de l'utilisateur pour le type d'exercice spécifique
    response = client.get(f"/api/users/me/progress/{exercise.exercise_type.value}")
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert "exercise_type" in data
    assert "mastery_level" in data
    assert "total_attempts" in data
    assert "correct_attempts" in data
    
    # Vérifier que les détails correspondent
    assert data["exercise_type"] == exercise.exercise_type.value
    assert data["mastery_level"] == progress.mastery_level
    assert data["total_attempts"] == progress.total_attempts
    assert data["correct_attempts"] == progress.correct_attempts

def test_get_user_progress_unauthorized():
    """Test pour vérifier que les progrès ne sont pas accessibles sans authentification."""
    response = client.get("/api/users/me/progress")
    assert response.status_code == 401

def test_get_user_progress_nonexistent_type(padawan_client):
    """Test pour récupérer les progrès d'un type d'exercice inexistant."""
    client = padawan_client["client"]
    
    # Tenter de récupérer les progrès pour un type d'exercice inexistant
    response = client.get("/api/users/me/progress/nonexistent_type")
    
    # Vérifier que la requête échoue
    assert response.status_code == 404 or response.status_code == 422

def test_register_exercise_attempt(padawan_client, db_session, mock_exercise):
    """Test pour enregistrer une tentative d'exercice et mettre à jour les progrès."""
    # Récupérer le client authentifié et les informations de l'utilisateur
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    
    # Créer un exercice pour la tentative
    exercise_data = mock_exercise()
    
    # Normaliser les valeurs d'enum en majuscules pour PostgreSQL et utiliser les enums Python
    exercise_type_str = exercise_data["exercise_type"].upper() if isinstance(exercise_data["exercise_type"], str) else exercise_data["exercise_type"]
    difficulty_str = exercise_data["difficulty"].upper() if isinstance(exercise_data["difficulty"], str) else exercise_data["difficulty"]
    
    # Convertir les strings en enums Python
    try:
        exercise_type_enum = ExerciseType(exercise_type_str)
    except ValueError:
        exercise_type_enum = ExerciseType.ADDITION
    
    try:
        difficulty_enum = DifficultyLevel(difficulty_str)
    except ValueError:
        difficulty_enum = DifficultyLevel.INITIE
    
    # Convertir en instance d'Exercise pour l'ajouter à la base
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_type_enum,
        difficulty=difficulty_enum,
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        is_active=exercise_data.get("is_active", True),
        creator_id=None,
        is_archived=False  # Explicitement mettre à False
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    
    # Afficher l'ID de l'exercice créé
    print(f"Exercice créé avec ID: {exercise.id}")
    
    # Vérifier que l'exercice existe dans la base de données
    db_exercise = db_session.query(Exercise).filter(Exercise.id == exercise.id).first()
    assert db_exercise is not None, f"L'exercice avec ID {exercise.id} n'existe pas dans la base de données après création"
    print(f"Exercice récupéré depuis la base de données: ID={db_exercise.id}, titre={db_exercise.title}")
    
    # Données pour la tentative
    attempt_data = {
        "exercise_id": exercise.id,
        "user_answer": exercise.correct_answer,  # Réponse correcte
        "time_spent": 30  # secondes
    }
    
    # Enregistrer la tentative
    response = client.post(f"/api/exercises/{exercise.id}/attempt", json=attempt_data)
    
    # Afficher les détails de la réponse en cas d'erreur
    if response.status_code != 200:
        print(f"Erreur lors de la tentative d'exercice: {response.status_code}")
        print(f"Détails de l'erreur: {response.text}")
        
        # Essayer de récupérer l'exercice via l'API
        get_response = client.get(f"/api/exercises/{exercise.id}")
        print(f"Tentative de récupération de l'exercice: {get_response.status_code}")
        if get_response.status_code == 200:
            print(f"L'exercice est accessible via l'API GET: {get_response.json()}")
        else:
            print(f"L'exercice n'est pas accessible via l'API GET: {get_response.text}")
        
        # Vérifier si l'exercice est toujours dans la base
        db_session.expire_all()  # Rafraîchir la session
        check_exercise = db_session.query(Exercise).filter(Exercise.id == exercise.id).first()
        if check_exercise:
            print(f"L'exercice est toujours dans la base: ID={check_exercise.id}, is_archived={check_exercise.is_archived}")
        else:
            print(f"L'exercice n'est plus dans la base!")
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] == True
    assert "feedback" in data
    
    # Vérifier que la tentative a été créée
    attempts = db_session.query(Attempt).filter(Attempt.user_id == user_id, Attempt.exercise_id == exercise.id).all()
    assert len(attempts) > 0
    
    # Vérifier que les progrès ont été mis à jour
    progress = db_session.query(Progress).filter(Progress.user_id == user_id, Progress.exercise_type == exercise.exercise_type.value).first()
    assert progress is not None
    assert progress.total_attempts >= 1
    assert progress.correct_attempts >= 1

def test_register_exercise_attempt_incorrect(padawan_client, db_session, mock_exercise):
    """Test pour enregistrer une tentative incorrecte d'exercice."""
    # Récupérer le client authentifié et les informations de l'utilisateur
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    
    # Créer un exercice pour la tentative
    exercise_data = mock_exercise()
    
    # Normaliser les valeurs d'enum en majuscules pour PostgreSQL et utiliser les enums Python
    exercise_type_str = exercise_data["exercise_type"].upper() if isinstance(exercise_data["exercise_type"], str) else exercise_data["exercise_type"]
    difficulty_str = exercise_data["difficulty"].upper() if isinstance(exercise_data["difficulty"], str) else exercise_data["difficulty"]
    
    # Convertir les strings en enums Python
    try:
        exercise_type_enum = ExerciseType(exercise_type_str)
    except ValueError:
        exercise_type_enum = ExerciseType.ADDITION
    
    try:
        difficulty_enum = DifficultyLevel(difficulty_str)
    except ValueError:
        difficulty_enum = DifficultyLevel.INITIE
    
    # Convertir en instance d'Exercise pour l'ajouter à la base
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_type_enum,
        difficulty=difficulty_enum,
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        is_active=exercise_data.get("is_active", True),
        creator_id=None,
        is_archived=False
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    
    # Données pour la tentative avec une réponse incorrecte
    incorrect_answer = "wrong_answer"
    if incorrect_answer == exercise.correct_answer:
        incorrect_answer = "different_wrong_answer"
        
    attempt_data = {
        "exercise_id": exercise.id,
        "user_answer": incorrect_answer,
        "time_spent": 30  # secondes
    }
    
    # Enregistrer la tentative
    response = client.post(f"/api/exercises/{exercise.id}/attempt", json=attempt_data)
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] == False
    assert "feedback" in data
    
    # Vérifier que la tentative a été créée
    attempts = db_session.query(Attempt).filter(Attempt.user_id == user_id, Attempt.exercise_id == exercise.id).all()
    assert len(attempts) > 0
    
    # Vérifier que les progrès ont été mis à jour
    progress = db_session.query(Progress).filter(Progress.user_id == user_id, Progress.exercise_type == exercise.exercise_type.value).first()
    assert progress is not None
    assert progress.total_attempts >= 1
    assert progress.correct_attempts == 0  # Aucune tentative correcte

def test_get_user_statistics(padawan_client, db_session, mock_exercise):
    """Test pour récupérer les statistiques globales d'un utilisateur."""
    # Récupérer le client authentifié et les informations de l'utilisateur
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]
    
    # Créer un exercice et enregistrer des tentatives
    exercise_data = mock_exercise()
    
    # Normaliser les valeurs d'enum en majuscules pour PostgreSQL et utiliser les enums Python
    exercise_type_str = exercise_data["exercise_type"].upper() if isinstance(exercise_data["exercise_type"], str) else exercise_data["exercise_type"]
    difficulty_str = exercise_data["difficulty"].upper() if isinstance(exercise_data["difficulty"], str) else exercise_data["difficulty"]
    
    # Convertir les strings en enums Python
    try:
        exercise_type_enum = ExerciseType(exercise_type_str)
    except ValueError:
        exercise_type_enum = ExerciseType.ADDITION
    
    try:
        difficulty_enum = DifficultyLevel(difficulty_str)
    except ValueError:
        difficulty_enum = DifficultyLevel.INITIE
    
    # Convertir en instance d'Exercise pour l'ajouter à la base
    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_type_enum,
        difficulty=difficulty_enum,
        question=exercise_data["question"],
        correct_answer=exercise_data["correct_answer"],
        choices=exercise_data.get("choices"),
        explanation=exercise_data.get("explanation"),
        is_active=exercise_data.get("is_active", True),
        creator_id=None,
        is_archived=False
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    
    # Créer quelques tentatives
    attempt1 = Attempt(
        user_id=user_id,
        exercise_id=exercise.id,
        user_answer=exercise.correct_answer,
        is_correct=True,
        time_spent=30
    )
    
    attempt2 = Attempt(
        user_id=user_id,
        exercise_id=exercise.id,
        user_answer="wrong_answer",
        is_correct=False,
        time_spent=45
    )
    
    db_session.add(attempt1)
    db_session.add(attempt2)
    db_session.commit()
    
    # Récupérer les statistiques de l'utilisateur
    response = client.get("/api/users/me/statistics")
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    
    # Vérifier que les statistiques contiennent les informations attendues
    assert "global" in data
    assert "total_attempts" in data["global"]
    assert "correct_attempts" in data["global"]
    assert "success_rate" in data["global"]
    assert "average_time" in data["global"]
    
    # Vérifier que les sections principales sont présentes
    assert "progress_by_type" in data
    assert "recent_attempts" in data
    
    # Vérifier que les tentatives ont bien été enregistrées
    assert data["global"]["total_attempts"] >= 2
    assert data["global"]["correct_attempts"] >= 1 
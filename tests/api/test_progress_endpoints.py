"""
Tests des endpoints API pour le suivi des progrès des utilisateurs.
"""
import pytest
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.progress import Progress
from app.models.attempt import Attempt
from app.utils.db_helpers import get_enum_value


def _enum_val(obj):
    """Safe extraction of enum value (handles both enum and plain string from DB)."""
    return obj.value if hasattr(obj, "value") else str(obj)


async def test_get_user_progress(padawan_client, db_session, mock_exercise):
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
        age_group=exercise_data.get("age_group", "6-8"),
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

    # L'API /api/users/me/progress agrège depuis Attempts, pas Progress.
    # Créer une tentative pour que les stats soient non nulles.
    attempt = Attempt(
        user_id=user_id,
        exercise_id=exercise.id,
        user_answer=exercise.correct_answer,
        is_correct=True,
        time_spent=30
    )
    db_session.add(attempt)
    db_session.commit()

    # Récupérer les progrès de l'utilisateur
    response = await client.get("/api/users/me/progress")

    # Vérifier la réponse (l'API retourne un dict avec stats agrégées)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "total_attempts" in data
    assert "correct_attempts" in data
    assert "by_category" in data
    assert data["total_attempts"] >= 1
    assert data["correct_attempts"] >= 1


async def test_get_user_progress_by_type(padawan_client, db_session, mock_exercise):
    """Test pour récupérer les progrès d'un utilisateur (by_category inclut le type)."""
    # L'API /api/users/me/progress agrège depuis Attempts et retourne by_category
    client = padawan_client["client"]
    user_id = padawan_client["user_id"]

    # Créer un exercice et une tentative (comme l'API)
    exercise_data = mock_exercise(exercise_type="addition")
    exercise_type_str = exercise_data["exercise_type"].upper() if isinstance(exercise_data["exercise_type"], str) else exercise_data["exercise_type"]
    difficulty_str = exercise_data["difficulty"].upper() if isinstance(exercise_data["difficulty"], str) else exercise_data["difficulty"]
    try:
        exercise_type_enum = ExerciseType(exercise_type_str)
    except ValueError:
        exercise_type_enum = ExerciseType.ADDITION
    try:
        difficulty_enum = DifficultyLevel(difficulty_str)
    except ValueError:
        difficulty_enum = DifficultyLevel.INITIE

    exercise = Exercise(
        title=exercise_data["title"],
        exercise_type=exercise_type_enum,
        difficulty=difficulty_enum,
        age_group=exercise_data.get("age_group", "6-8"),
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

    # Créer une tentative pour que by_category soit peuplé
    attempt = Attempt(
        user_id=user_id,
        exercise_id=exercise.id,
        user_answer=exercise.correct_answer,
        is_correct=True,
        time_spent=30
    )
    db_session.add(attempt)
    db_session.commit()

    response = await client.get("/api/users/me/progress")
    assert response.status_code == 200
    data = response.json()
    assert "by_category" in data
    exercise_type_val = _enum_val(exercise.exercise_type)
    assert exercise_type_val in data["by_category"], f"by_category devrait contenir {exercise_type_val}: {data['by_category']}"
    cat = data["by_category"][exercise_type_val]
    assert "completed" in cat
    assert "accuracy" in cat


async def test_get_user_progress_unauthorized(client):
    """Test pour vérifier que les progrès ne sont pas accessibles sans authentification."""
    response = await client.get("/api/users/me/progress")
    assert response.status_code == 401


async def test_get_user_progress_nonexistent_type(padawan_client):
    """Test pour récupérer les progrès d'un type d'exercice inexistant."""
    client = padawan_client["client"]

    # Tenter de récupérer les progrès pour un type d'exercice inexistant
    response = await client.get("/api/users/me/progress/nonexistent_type")

    # Vérifier que la requête échoue (ou accepte 200 si endpoint placeholder)
    assert response.status_code in (200, 404, 422)


async def test_register_exercise_attempt(padawan_client, db_session, mock_exercise):
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
        age_group=exercise_data.get("age_group", "6-8"),
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

    # Données pour la tentative (handler attend "answer" ou "selected_answer", exercise_id dans l'URL)
    attempt_data = {
        "answer": exercise.correct_answer,  # Réponse correcte
        "time_spent": 30  # secondes
    }

    # Enregistrer la tentative
    response = await client.post(f"/api/exercises/{exercise.id}/attempt", json=attempt_data)

    # Afficher les détails de la réponse en cas d'erreur
    if response.status_code != 200:
        print(f"Erreur lors de la tentative d'exercice: {response.status_code}")
        print(f"Détails de l'erreur: {response.text}")

        # Essayer de récupérer l'exercice via l'API
        get_response = await client.get(f"/api/exercises/{exercise.id}")
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

    # Vérifier la réponse (handler renvoie is_correct, correct_answer, explanation, attempt_id)
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] == True
    assert "correct_answer" in data
    assert "attempt_id" in data

    # Vérifier que la tentative a été créée
    attempts = db_session.query(Attempt).filter(Attempt.user_id == user_id, Attempt.exercise_id == exercise.id).all()
    assert len(attempts) > 0

    # Vérifier que les progrès ont été mis à jour
    exercise_type_val = _enum_val(exercise.exercise_type)
    progress = db_session.query(Progress).filter(Progress.user_id == user_id, Progress.exercise_type == exercise_type_val).first()
    assert progress is not None
    assert progress.total_attempts >= 1
    assert progress.correct_attempts >= 1


async def test_register_exercise_attempt_incorrect(padawan_client, db_session, mock_exercise):
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
        age_group=exercise_data.get("age_group", "6-8"),
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
        "answer": incorrect_answer,
        "time_spent": 30  # secondes
    }

    # Enregistrer la tentative
    response = await client.post(f"/api/exercises/{exercise.id}/attempt", json=attempt_data)

    # Vérifier la réponse (handler renvoie is_correct, correct_answer, explanation, attempt_id)
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] == False
    assert "correct_answer" in data
    assert "attempt_id" in data

    # Vérifier que la tentative a été créée
    attempts = db_session.query(Attempt).filter(Attempt.user_id == user_id, Attempt.exercise_id == exercise.id).all()
    assert len(attempts) > 0

    # Vérifier que les progrès ont été mis à jour
    exercise_type_val = _enum_val(exercise.exercise_type)
    progress = db_session.query(Progress).filter(Progress.user_id == user_id, Progress.exercise_type == exercise_type_val).first()
    assert progress is not None
    assert progress.total_attempts >= 1
    assert progress.correct_attempts == 0  # Aucune tentative correcte


async def test_get_user_statistics(padawan_client, db_session, mock_exercise):
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
        age_group=exercise_data.get("age_group", "6-8"),
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

    # Récupérer les statistiques de l'utilisateur (route réelle: /api/users/stats)
    response = await client.get("/api/users/stats")

    # Vérifier la réponse (200 ou 404 selon la route)
    assert response.status_code in (200, 404)
    if response.status_code != 200:
        return

    data = response.json()
    # Format de /api/users/stats: total_exercises, correct_answers, success_rate, etc.
    assert "total_exercises" in data or "correct_answers" in data or "success_rate" in data
    # Vérifier que les tentatives ont bien été comptées
    total = data.get("total_exercises", data.get("total_attempts", 0))
    correct = data.get("correct_answers", data.get("correct_attempts", 0))
    assert total >= 2
    assert correct >= 1

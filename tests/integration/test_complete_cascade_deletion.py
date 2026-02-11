"""
Tests d'intégration pour vérifier que le système de suppression en cascade
fonctionne correctement pour toutes les relations entre les modèles.
"""
import pytest
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup, LogicChallengeAttempt
from app.utils.db_helpers import get_enum_value

async def test_complete_user_deletion_cascade(db_session):
    """
    Teste la suppression complète d'un utilisateur avec toutes ses relations connectées.
    
    Ce test vérifie que toutes les entités liées à un utilisateur sont correctement supprimées
    lorsque l'utilisateur est supprimé, conformément aux configurations de cascade.
    """
    # Générer un identifiant unique pour éviter les conflits avec d'autres tests
    unique_id = uuid.uuid4().hex[:8]
    
    # 1. Créer un utilisateur de test
    user = User(
        username=f"cascade_test_{unique_id}",
        email=f"cascade_{unique_id}@example.com",
        hashed_password="test_password",
        role=get_enum_value(UserRole, UserRole.PADAWAN)
    )
    db_session.add(user)
    db_session.flush()
    
    # 2. Créer des exercices créés par cet utilisateur
    exercise1 = Exercise(
        title=f"Test Exercise by user {unique_id} - 1",
        creator_id=user.id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE),
        age_group="6-8",
        question="1+1=?",
        correct_answer="2"
    )
    
    exercise2 = Exercise(
        title=f"Test Exercise by user {unique_id} - 2",
        creator_id=user.id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN),
        age_group="9-11",
        question="5×5=?",
        correct_answer="25"
    )
    
    db_session.add_all([exercise1, exercise2])
    db_session.flush()
    
    # 3. Créer des tentatives pour ces exercices
    attempt1 = Attempt(
        user_id=user.id,
        exercise_id=exercise1.id,
        user_answer="2",
        is_correct=True,
        time_spent=5.0
    )
    
    attempt2 = Attempt(
        user_id=user.id,
        exercise_id=exercise2.id,
        user_answer="20",
        is_correct=False,
        time_spent=8.0
    )
    
    db_session.add_all([attempt1, attempt2])
    db_session.flush()
    
    # 4. Créer des progrès pour cet utilisateur
    progress1 = Progress(
        user_id=user.id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE),
        total_attempts=10,
        correct_attempts=8
    )
    
    progress2 = Progress(
        user_id=user.id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN),
        total_attempts=5,
        correct_attempts=3
    )
    
    db_session.add_all([progress1, progress2])
    db_session.flush()
    
    # 5. Créer des recommandations pour cet utilisateur
    recommendation1 = Recommendation(
        user_id=user.id,
        exercise_id=exercise1.id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE),
        priority=8,
        reason="Recommandation de test 1"
    )
    
    recommendation2 = Recommendation(
        user_id=user.id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.SOUSTRACTION),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN),
        priority=5,
        reason="Recommandation de test 2"
    )
    
    db_session.add_all([recommendation1, recommendation2])
    db_session.flush()
    
    # 6. Créer un défi logique créé par cet utilisateur
    challenge = LogicChallenge(
        title=f"Test Challenge by user {unique_id}",
        creator_id=user.id,
        challenge_type=get_enum_value(LogicChallengeType, LogicChallengeType.PATTERN),
        age_group=get_enum_value(AgeGroup, AgeGroup.GROUP_13_15),
        description="Description du défi de test",
        content="Contenu du défi de test",
        question="Question du défi de test?", 
        correct_answer="Solution test",
        solution="Solution technique",
        solution_explanation="Explication de la solution"
    )
    
    db_session.add(challenge)
    db_session.flush()
    
    # 7. Créer une tentative de défi logique
    challenge_attempt = LogicChallengeAttempt(
        user_id=user.id,
        challenge_id=challenge.id,
        user_solution="Tentative de solution",
        is_correct=False,
        hints_used=1
    )
    
    db_session.add(challenge_attempt)
    db_session.commit()
    
    # Sauvegarder les IDs pour vérification
    user_id = user.id
    exercise_ids = [exercise1.id, exercise2.id]
    attempt_ids = [attempt1.id, attempt2.id]
    progress_ids = [progress1.id, progress2.id]
    recommendation_ids = [recommendation1.id, recommendation2.id]
    challenge_id = challenge.id
    challenge_attempt_id = challenge_attempt.id
    
    # Vérifier que toutes les entités existent avant la suppression
    assert db_session.query(User).filter(User.id == user_id).count() == 1
    assert db_session.query(Exercise).filter(Exercise.id.in_(exercise_ids)).count() == 2
    assert db_session.query(Attempt).filter(Attempt.id.in_(attempt_ids)).count() == 2
    assert db_session.query(Progress).filter(Progress.id.in_(progress_ids)).count() == 2
    assert db_session.query(Recommendation).filter(Recommendation.id.in_(recommendation_ids)).count() == 2
    assert db_session.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).count() == 1
    assert db_session.query(LogicChallengeAttempt).filter(LogicChallengeAttempt.id == challenge_attempt_id).count() == 1
    
    # Supprimer l'utilisateur - toutes les entités liées doivent être supprimées en cascade
    db_session.delete(user)
    db_session.commit()
    
    # Vérifier que l'utilisateur a été supprimé
    assert db_session.query(User).filter(User.id == user_id).count() == 0
    
    # Vérifier que les exercices créés par l'utilisateur ont été supprimés
    assert db_session.query(Exercise).filter(Exercise.id.in_(exercise_ids)).count() == 0
    
    # Vérifier que les tentatives de l'utilisateur ont été supprimées
    assert db_session.query(Attempt).filter(Attempt.id.in_(attempt_ids)).count() == 0
    
    # Vérifier que les progrès de l'utilisateur ont été supprimés
    assert db_session.query(Progress).filter(Progress.id.in_(progress_ids)).count() == 0
    
    # Vérifier que les recommandations de l'utilisateur ont été supprimées
    assert db_session.query(Recommendation).filter(Recommendation.id.in_(recommendation_ids)).count() == 0
    
    # Vérifier que le défi logique créé par l'utilisateur a été supprimé
    assert db_session.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).count() == 0
    
    # Vérifier que la tentative de défi logique de l'utilisateur a été supprimée
    assert db_session.query(LogicChallengeAttempt).filter(LogicChallengeAttempt.id == challenge_attempt_id).count() == 0


async def test_exercise_deletion_cascade(db_session):
    """
    Teste la suppression d'un exercice avec toutes ses relations connectées.
    
    Ce test vérifie que toutes les entités liées à un exercice sont correctement supprimées
    lorsque l'exercice est supprimé, mais pas celles qui devraient être préservées.
    """
    # Générer un identifiant unique pour éviter les conflits avec d'autres tests
    unique_id = uuid.uuid4().hex[:8]
    
    # 1. Créer un utilisateur de test (qui ne doit PAS être supprimé)
    user = User(
        username=f"test_exercise_cascade_{unique_id}",
        email=f"test_ex_cascade_{unique_id}@example.com",
        hashed_password="test_password",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    db_session.add(user)
    db_session.flush()
    
    # 2. Créer un exercice
    exercise = Exercise(
        title=f"Cascade test exercise {unique_id}",
        creator_id=user.id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.DIVISION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.CHEVALIER.value, db_session),
        age_group="12-14",
        question="10÷2=?",
        correct_answer="5"
    )
    
    db_session.add(exercise)
    db_session.flush()
    
    # 3. Créer des tentatives pour cet exercice
    attempts = []
    for i in range(3):
        attempt = Attempt(
            user_id=user.id,
            exercise_id=exercise.id,
            user_answer=str(4 + i),  # Réponses: 4, 5, 6
            is_correct=(i == 1),     # Seule la deuxième tentative est correcte
            time_spent=5.0 + i
        )
        attempts.append(attempt)
    
    db_session.add_all(attempts)
    db_session.flush()
    
    # 4. Créer une recommandation pour cet exercice
    recommendation = Recommendation(
        user_id=user.id,
        exercise_id=exercise.id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.DIVISION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.CHEVALIER.value, db_session),
        priority=7,
        reason="Recommandation pour l'exercice test"
    )
    
    db_session.add(recommendation)
    db_session.commit()
    
    # Sauvegarder les IDs pour vérification
    user_id = user.id
    exercise_id = exercise.id
    attempt_ids = [a.id for a in attempts]
    recommendation_id = recommendation.id
    
    # Vérifier que toutes les entités existent avant la suppression
    assert db_session.query(User).filter(User.id == user_id).count() == 1
    assert db_session.query(Exercise).filter(Exercise.id == exercise_id).count() == 1
    assert db_session.query(Attempt).filter(Attempt.id.in_(attempt_ids)).count() == 3
    assert db_session.query(Recommendation).filter(Recommendation.id == recommendation_id).count() == 1
    
    # Supprimer l'exercice - les tentatives doivent être supprimées, mais pas l'utilisateur
    db_session.delete(exercise)
    db_session.commit()
    
    # Vérifier que l'exercice a été supprimé
    assert db_session.query(Exercise).filter(Exercise.id == exercise_id).count() == 0
    
    # Vérifier que les tentatives pour cet exercice ont été supprimées
    assert db_session.query(Attempt).filter(Attempt.id.in_(attempt_ids)).count() == 0
    
    # Vérifier que la recommandation a été mise à jour (exercise_id = NULL)
    recommendation = db_session.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    assert recommendation is not None
    assert recommendation.exercise_id is None
    
    # Vérifier que l'utilisateur existe toujours
    assert db_session.query(User).filter(User.id == user_id).count() == 1


async def test_multi_level_cascade(db_session):
    """
    Teste la suppression en cascade sur plusieurs niveaux.
    
    Ce test vérifie que toutes les entités sont correctement supprimées
    lorsqu'une entité parent est supprimée, même avec plusieurs niveaux de relations.
    """
    # Générer un identifiant unique pour éviter les conflits avec d'autres tests
    unique_id = uuid.uuid4().hex[:8]
    
    # Structure hiérarchique à tester:
    # User 1
    # ├── User 2 (créé virtuellement par User 1)
    # │   └── Exercise 2 (créé par User 2)
    # │       └── Attempt 2 (par User 2 sur Exercise 2)
    # ├── Exercise 1 (créé par User 1)
    # │   ├── Attempt 1A (par User 1 sur Exercise 1)
    # │   └── Attempt 1B (par User 2 sur Exercise 1)
    # └── Recommendation 1 (pour User 1)
    
    # 1. Créer les utilisateurs
    user1 = User(
        username=f"test_parent_user_{unique_id}",
        email=f"test_parent_{unique_id}@example.com",
        hashed_password="test_password",
        role=get_enum_value(UserRole, UserRole.MAITRE.value, db_session)
    )
    
    user2 = User(
        username=f"test_child_user_{unique_id}",
        email=f"test_child_{unique_id}@example.com",
        hashed_password="test_password",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    
    db_session.add_all([user1, user2])
    db_session.flush()
    
    # 2. Créer les exercices
    exercise1 = Exercise(
        title=f"Test Parent exercise {unique_id}",
        creator_id=user1.id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.MAITRE.value, db_session),
        age_group="15-17",
        question="99+1=?",
        correct_answer="100"
    )
    
    exercise2 = Exercise(
        title=f"Test Child exercise {unique_id}",
        creator_id=user2.id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.SOUSTRACTION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session),
        age_group="9-11",
        question="10-5=?",
        correct_answer="5"
    )
    
    db_session.add_all([exercise1, exercise2])
    db_session.flush()
    
    # 3. Créer les tentatives
    attempt1a = Attempt(
        user_id=user1.id,
        exercise_id=exercise1.id,
        user_answer="100",
        is_correct=True,
        time_spent=3.0
    )
    
    attempt1b = Attempt(
        user_id=user2.id,
        exercise_id=exercise1.id,
        user_answer="100",
        is_correct=True,
        time_spent=4.0
    )
    
    attempt2 = Attempt(
        user_id=user2.id,
        exercise_id=exercise2.id,
        user_answer="5",
        is_correct=True,
        time_spent=2.0
    )
    
    db_session.add_all([attempt1a, attempt1b, attempt2])
    db_session.flush()
    
    # 4. Créer la recommandation
    recommendation1 = Recommendation(
        user_id=user1.id,
        exercise_id=exercise1.id,
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.MAITRE.value, db_session),
        priority=9,
        reason="Recommandation multi-niveau"
    )
    
    db_session.add(recommendation1)
    db_session.commit()
    
    # Sauvegarder les IDs pour vérification
    user1_id = user1.id
    user2_id = user2.id
    exercise1_id = exercise1.id
    exercise2_id = exercise2.id
    attempt1a_id = attempt1a.id
    attempt1b_id = attempt1b.id
    attempt2_id = attempt2.id
    recommendation1_id = recommendation1.id
    
    # Vérifier que toutes les entités existent avant la suppression
    assert db_session.query(User).filter(User.id.in_([user1_id, user2_id])).count() == 2
    assert db_session.query(Exercise).filter(Exercise.id.in_([exercise1_id, exercise2_id])).count() == 2
    assert db_session.query(Attempt).filter(Attempt.id.in_([attempt1a_id, attempt1b_id, attempt2_id])).count() == 3
    assert db_session.query(Recommendation).filter(Recommendation.id == recommendation1_id).count() == 1
    
    # Supprimer l'utilisateur parent - tout ce qui lui est lié doit être supprimé
    db_session.delete(user1)
    db_session.commit()
    
    # Vérifier que l'utilisateur parent a été supprimé
    assert db_session.query(User).filter(User.id == user1_id).count() == 0
    
    # Vérifier que l'exercice créé par l'utilisateur parent a été supprimé
    assert db_session.query(Exercise).filter(Exercise.id == exercise1_id).count() == 0
    
    # Vérifier que les tentatives de l'utilisateur parent ont été supprimées
    assert db_session.query(Attempt).filter(Attempt.id == attempt1a_id).count() == 0
    
    # Vérifier que les recommandations de l'utilisateur parent ont été supprimées
    assert db_session.query(Recommendation).filter(Recommendation.id == recommendation1_id).count() == 0
    
    # Vérifier que la tentative de l'utilisateur enfant sur l'exercice parent a été supprimée
    # (car l'exercice a été supprimé, pas l'utilisateur)
    assert db_session.query(Attempt).filter(Attempt.id == attempt1b_id).count() == 0
    
    # Vérifier que l'utilisateur enfant existe toujours
    assert db_session.query(User).filter(User.id == user2_id).count() == 1
    
    # Vérifier que l'exercice créé par l'utilisateur enfant existe toujours
    assert db_session.query(Exercise).filter(Exercise.id == exercise2_id).count() == 1
    
    # Vérifier que la tentative de l'utilisateur enfant sur son propre exercice existe toujours
    assert db_session.query(Attempt).filter(Attempt.id == attempt2_id).count() == 1 
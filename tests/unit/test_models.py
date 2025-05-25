import pytest
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.recommendation import Recommendation
from app.utils.db_helpers import get_enum_value
from datetime import datetime
from tests.utils.test_helpers import unique_username, unique_email



def test_user_model():
    """Test du modèle User."""
    # Créer un utilisateur avec des valeurs uniques
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="hashed_password",
        role=UserRole.PADAWAN.value
    )
    
    # Vérifier les attributs
    assert user.username is not None
    assert user.email is not None
    assert user.hashed_password == "hashed_password"
    assert user.role == UserRole.PADAWAN.value



def test_exercise_model():
    """Test de création et validation d'un modèle exercice"""
    exercise = Exercise(
        title="Test Exercise",
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
        question="2 + 2 = ?",
        correct_answer="4",
        created_at=datetime.now()
    )

    assert exercise.exercise_type == ExerciseType.ADDITION
    assert exercise.difficulty == DifficultyLevel.INITIE
    assert exercise.question == "2 + 2 = ?"
    assert exercise.correct_answer == "4"
    assert isinstance(exercise.created_at, datetime)



def test_attempt_model():
    """Test de création et validation d'un modèle tentative"""
    user = User(username=unique_username(), email=unique_email(), hashed_password="test_password"
        , role=UserRole.PADAWAN)
    exercise = Exercise(
        title="Test Exercise",
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
        question="2 + 2 = ?",
        correct_answer="4"
    )

    attempt = Attempt(
        user=user,
        exercise=exercise,
        user_answer="4",
        is_correct=True,
        created_at=datetime.now()
    )

    assert attempt.user == user
    assert attempt.exercise == exercise
    assert attempt.user_answer == "4"
    assert attempt.is_correct is True
    assert isinstance(attempt.created_at, datetime)



def test_user_attempt_relationship():
    """Test de la relation entre User et Attempt."""
    user = User(username=unique_username(), email=unique_email(), hashed_password="test_password")
    exercise = Exercise(
        title="Test Exercise",
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
        question="2 + 2 = ?",
        correct_answer="4"
    )

    attempt1 = Attempt(user=user, exercise=exercise, user_answer="4", is_correct=True)
    attempt2 = Attempt(user=user, exercise=exercise, user_answer="5", is_correct=False)

    user.attempts = [attempt1, attempt2]

    assert len(user.attempts) == 2
    assert user.attempts[0].is_correct is True
    assert user.attempts[1].is_correct is False



def test_exercise_attempt_relationship():
    """Test de la relation entre exercice et tentatives"""
    user = User(username=unique_username(), email=unique_email(), hashed_password="test_password"
        , role=UserRole.PADAWAN)
    exercise = Exercise(
        title="Test Exercise",
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
        question="2 + 2 = ?",
        correct_answer="4"
    )

    attempt1 = Attempt(user=user, exercise=exercise, user_answer="4", is_correct=True)
    attempt2 = Attempt(user=user, exercise=exercise, user_answer="5", is_correct=False)

    exercise.attempts = [attempt1, attempt2]

    assert len(exercise.attempts) == 2
    assert exercise.attempts[0].is_correct is True
    assert exercise.attempts[1].is_correct is False


def test_recommendation_model():
    """Test de création et validation d'un modèle recommandation"""
    user = User(username=unique_username(), email=unique_email(), hashed_password="test_password"
        , role=UserRole.PADAWAN)
    exercise = Exercise(
        title="Recommended Exercise",
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
        question="3 + 3 = ?",
        correct_answer="6"
    )
    
    recommendation = Recommendation(
        user=user,
        exercise=exercise,
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
        priority=8,
        reason="Pour renforcer vos compétences en addition",
        created_at=datetime.now(),
        is_completed=False,
        shown_count=0,
        clicked_count=0
    )
    
    assert recommendation.user == user
    assert recommendation.exercise == exercise
    assert recommendation.exercise_type == ExerciseType.ADDITION
    assert recommendation.difficulty == DifficultyLevel.INITIE
    assert recommendation.priority == 8
    assert recommendation.reason == "Pour renforcer vos compétences en addition"
    assert isinstance(recommendation.created_at, datetime)
    assert recommendation.is_completed is False
    assert recommendation.shown_count == 0
    assert recommendation.clicked_count == 0


def test_user_recommendation_relationship():
    """Test de la relation entre User et Recommendation."""
    user = User(username=unique_username(), email=unique_email(), hashed_password="test_password")
    exercise = Exercise(
        title="Rec Exercise",
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
        question="5 + 5 = ?",
        correct_answer="10"
    )
    
    rec1 = Recommendation(
        user=user,
        exercise=exercise,
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
        priority=8,
        reason="Recommendation 1"
    )
    rec2 = Recommendation(
        user=user,
        exercise_type=ExerciseType.MULTIPLICATION,
        difficulty=DifficultyLevel.PADAWAN,
        priority=5,
        reason="Recommendation 2"
    )
    
    user.recommendations = [rec1, rec2]
    
    assert len(user.recommendations) == 2
    assert user.recommendations[0].reason == "Recommendation 1"
    assert user.recommendations[1].reason == "Recommendation 2"
    assert user.recommendations[0].exercise == exercise
    assert user.recommendations[1].exercise is None


def test_user_progress_relationship():
    """Test de la relation entre User et Progress."""
    user = User(username=unique_username(), email=unique_email(), hashed_password="test_password")

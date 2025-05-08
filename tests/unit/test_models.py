import pytest
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from datetime import datetime

def test_user_model():
    """Test de création et validation d'un modèle utilisateur"""
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password="test_password",
        role=UserRole.PADAWAN,
        created_at=datetime.now()
    )
    
    assert user.username == "test_user"
    assert user.email == "test@example.com"
    assert user.role == UserRole.PADAWAN
    assert isinstance(user.created_at, datetime)

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
    user = User(username="test_user", email="test@example.com", hashed_password="test_password", role=UserRole.PADAWAN)
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
    """Test de la relation entre utilisateur et tentatives"""
    user = User(username="test_user", email="test@example.com", hashed_password="test_password", role=UserRole.PADAWAN)
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
    user = User(username="test_user", email="test@example.com", hashed_password="test_password", role=UserRole.PADAWAN)
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
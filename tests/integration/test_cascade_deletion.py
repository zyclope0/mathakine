"""
Tests d'intégration pour vérifier que les suppressions en cascade fonctionnent correctement.
"""
import pytest
import uuid
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt, LogicChallengeType, AgeGroup


def generate_unique_username():
    """Génère un nom d'utilisateur unique pour les tests"""
    return f"test_user_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def setup_exercise_with_attempts(db_session):
    """Crée un exercice avec des tentatives pour tester la suppression en cascade"""
    # Créer un exercice
    exercise = Exercise(
        title="Test Cascade Exercise",
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
        question="Combien font 2+2?",
        correct_answer="4",
        choices=["2", "3", "4", "5"]
    )
    db_session.add(exercise)
    db_session.flush()  # Pour obtenir l'ID de l'exercice
    
    # Créer un utilisateur
    user = User(
        username=generate_unique_username(),
        email=f"cascade_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="test_password",
        role=UserRole.PADAWAN
    )
    db_session.add(user)
    db_session.flush()  # Pour obtenir l'ID de l'utilisateur
    
    # Créer des tentatives associées
    attempt1 = Attempt(
        user_id=user.id,
        exercise_id=exercise.id,
        user_answer="4",
        is_correct=True
    )
    attempt2 = Attempt(
        user_id=user.id,
        exercise_id=exercise.id,
        user_answer="5",
        is_correct=False
    )
    db_session.add(attempt1)
    db_session.add(attempt2)
    db_session.commit()
    
    return {
        "exercise_id": exercise.id,
        "user_id": user.id,
        "attempt_ids": [attempt1.id, attempt2.id]
    }


def test_exercise_cascade_deletion(db_session, setup_exercise_with_attempts):
    """Teste que la suppression d'un exercice supprime également ses tentatives"""
    data = setup_exercise_with_attempts
    exercise_id = data["exercise_id"]
    attempt_ids = data["attempt_ids"]
    
    # Vérifier que l'exercice et les tentatives existent
    exercise = db_session.query(Exercise).filter(Exercise.id == exercise_id).first()
    assert exercise is not None
    
    attempts = db_session.query(Attempt).filter(Attempt.exercise_id == exercise_id).all()
    assert len(attempts) == 2
    
    # Supprimer l'exercice
    db_session.delete(exercise)
    db_session.commit()
    
    # Vérifier que les tentatives ont également été supprimées
    attempts = db_session.query(Attempt).filter(Attempt.exercise_id == exercise_id).all()
    assert len(attempts) == 0
    
    for attempt_id in attempt_ids:
        attempt = db_session.query(Attempt).filter(Attempt.id == attempt_id).first()
        assert attempt is None


@pytest.fixture
def setup_logic_challenge_with_attempts(db_session):
    """Crée un défi logique avec des tentatives pour tester la suppression en cascade"""
    # Créer un défi logique
    challenge = LogicChallenge(
        title="Test Cascade Challenge",
        challenge_type=LogicChallengeType.SEQUENCE,
        age_group=AgeGroup.GROUP_10_12,
        description="Test de suppression en cascade",
        correct_answer="42",
        solution_explanation="La réponse est 42"
    )
    db_session.add(challenge)
    db_session.flush()  # Pour obtenir l'ID du défi
    
    # Créer un utilisateur
    user = User(
        username=generate_unique_username(),
        email=f"lc_cascade_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="test_password",
        role=UserRole.PADAWAN
    )
    db_session.add(user)
    db_session.flush()  # Pour obtenir l'ID de l'utilisateur
    
    # Créer des tentatives associées
    attempt1 = LogicChallengeAttempt(
        user_id=user.id,
        challenge_id=challenge.id,
        user_answer="42",
        is_correct=True
    )
    attempt2 = LogicChallengeAttempt(
        user_id=user.id,
        challenge_id=challenge.id,
        user_answer="41",
        is_correct=False
    )
    db_session.add(attempt1)
    db_session.add(attempt2)
    db_session.commit()
    
    return {
        "challenge_id": challenge.id,
        "user_id": user.id,
        "attempt_ids": [attempt1.id, attempt2.id]
    }


def test_logic_challenge_cascade_deletion(db_session, setup_logic_challenge_with_attempts):
    """Teste que la suppression d'un défi logique supprime également ses tentatives"""
    data = setup_logic_challenge_with_attempts
    challenge_id = data["challenge_id"]
    attempt_ids = data["attempt_ids"]
    
    # Vérifier que le défi et les tentatives existent
    challenge = db_session.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
    assert challenge is not None
    
    attempts = db_session.query(LogicChallengeAttempt).filter(LogicChallengeAttempt.challenge_id == challenge_id).all()
    assert len(attempts) == 2
    
    # Supprimer le défi
    db_session.delete(challenge)
    db_session.commit()
    
    # Vérifier que les tentatives ont également été supprimées
    attempts = db_session.query(LogicChallengeAttempt).filter(LogicChallengeAttempt.challenge_id == challenge_id).all()
    assert len(attempts) == 0
    
    for attempt_id in attempt_ids:
        attempt = db_session.query(LogicChallengeAttempt).filter(LogicChallengeAttempt.id == attempt_id).first()
        assert attempt is None


def test_user_cascade_deletion(db_session):
    """Teste que la suppression d'un utilisateur supprime également ses tentatives"""
    # Créer un utilisateur spécifique pour ce test
    user = User(
        username=generate_unique_username(),
        email=f"user_cascade_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="test_password",
        role=UserRole.PADAWAN
    )
    db_session.add(user)
    db_session.flush()
    
    # Créer un exercice
    exercise = Exercise(
        title="Test User Cascade Exercise",
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
        question="Combien font 5+5?",
        correct_answer="10",
        choices=["8", "9", "10", "11"]
    )
    db_session.add(exercise)
    db_session.flush()
    
    # Créer un défi logique
    challenge = LogicChallenge(
        title="Test User Cascade Challenge",
        challenge_type=LogicChallengeType.SEQUENCE,
        age_group=AgeGroup.GROUP_10_12,
        description="Test de suppression en cascade utilisateur",
        correct_answer="42",
        solution_explanation="La réponse est 42"
    )
    db_session.add(challenge)
    db_session.flush()
    
    # Créer des tentatives d'exercice associées
    ex_attempt1 = Attempt(
        user_id=user.id,
        exercise_id=exercise.id,
        user_answer="10",
        is_correct=True
    )
    ex_attempt2 = Attempt(
        user_id=user.id,
        exercise_id=exercise.id,
        user_answer="9",
        is_correct=False
    )
    db_session.add(ex_attempt1)
    db_session.add(ex_attempt2)
    
    # Créer des tentatives de défi logique associées
    lc_attempt1 = LogicChallengeAttempt(
        user_id=user.id,
        challenge_id=challenge.id,
        user_answer="42",
        is_correct=True
    )
    lc_attempt2 = LogicChallengeAttempt(
        user_id=user.id,
        challenge_id=challenge.id,
        user_answer="41",
        is_correct=False
    )
    db_session.add(lc_attempt1)
    db_session.add(lc_attempt2)
    db_session.commit()
    
    user_id = user.id
    ex_attempt_ids = [ex_attempt1.id, ex_attempt2.id]
    lc_attempt_ids = [lc_attempt1.id, lc_attempt2.id]
    
    # Vérifier que l'utilisateur et les tentatives existent
    user = db_session.query(User).filter(User.id == user_id).first()
    assert user is not None
    
    ex_attempts = db_session.query(Attempt).filter(Attempt.user_id == user_id).all()
    assert len(ex_attempts) == 2
    
    lc_attempts = db_session.query(LogicChallengeAttempt).filter(LogicChallengeAttempt.user_id == user_id).all()
    assert len(lc_attempts) == 2
    
    # Supprimer l'utilisateur
    db_session.delete(user)
    db_session.commit()
    
    # Vérifier que les tentatives ont également été supprimées
    ex_attempts = db_session.query(Attempt).filter(Attempt.user_id == user_id).all()
    assert len(ex_attempts) == 0
    
    lc_attempts = db_session.query(LogicChallengeAttempt).filter(LogicChallengeAttempt.user_id == user_id).all()
    assert len(lc_attempts) == 0
    
    for attempt_id in ex_attempt_ids:
        attempt = db_session.query(Attempt).filter(Attempt.id == attempt_id).first()
        assert attempt is None
        
    for attempt_id in lc_attempt_ids:
        attempt = db_session.query(LogicChallengeAttempt).filter(LogicChallengeAttempt.id == attempt_id).first()
        assert attempt is None 
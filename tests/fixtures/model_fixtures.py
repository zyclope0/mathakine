"""
Fixtures pour les modèles de données à utiliser dans les tests.
Ce module centralise la création d'instances de modèles pour les tests,
évitant ainsi la duplication de code et facilitant la maintenance.
"""
import pytest
from datetime import datetime, timedelta
import random
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup


@pytest.fixture


def test_user():
    """Crée un utilisateur de test."""
    return User(
        username="test_user",
        email="test@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"\
            ,  # "password"
        role=UserRole.PADAWAN,
        full_name="Test User",
        grade_level=5,
        created_at=datetime.now()
    )


@pytest.fixture


def test_maitre_user():
    """Crée un utilisateur de type MAITRE pour les tests."""
    return User(
        username="test_maitre",
        email="maitre@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"\
            ,  # "password"
        role=UserRole.MAITRE,
        full_name="Test Maitre",
        grade_level=10,
        created_at=datetime.now()
    )


@pytest.fixture


def test_exercise():
    """Crée un exercice de test."""
    return Exercise(
        title="Test Exercise",
        exercise_type=ExerciseType.ADDITION,
        difficulty=DifficultyLevel.INITIE,
        question="2 + 2 = ?",
        correct_answer="4",
        choices=["2", "3", "4", "5"],
        explanation="C'est une addition simple: 2 + 2 = 4",
        created_at=datetime.now()
    )


@pytest.fixture


def test_exercises():
    """Crée une liste d'exercices de test variés."""
    return [
        Exercise(
            title="Addition simple",
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.INITIE,
            question="2 + 2 = ?",
            correct_answer="4",
            choices=["2", "3", "4", "5"],
            explanation="C'est une addition simple: 2 + 2 = 4",
            created_at=datetime.now() - timedelta(days=3)
        ),
        Exercise(
            title="Multiplication",
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.PADAWAN,
            question="5 × 6 = ?",
            correct_answer="30",
            choices=["24", "30", "36", "40"],
            explanation="5 × 6 = 30",
            created_at=datetime.now() - timedelta(days=2)
        ),
        Exercise(
            title="Soustraction",
            exercise_type=ExerciseType.SOUSTRACTION,
            difficulty=DifficultyLevel.INITIE,
            question="10 - 7 = ?",
            correct_answer="3",
            choices=["2", "3", "4", "7"],
            explanation="10 - 7 = 3",
            created_at=datetime.now() - timedelta(days=1)
        ),
        Exercise(
            title="Division",
            exercise_type=ExerciseType.DIVISION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="20 ÷ 4 = ?",
            correct_answer="5",
            choices=["4", "5", "6", "10"],
            explanation="20 ÷ 4 = 5",
            created_at=datetime.now()
        )
    ]


@pytest.fixture


def test_attempt(test_user, test_exercise):
    """Crée une tentative de test pour un utilisateur et un exercice."""
    return Attempt(
        user=test_user,
        exercise=test_exercise,
        user_answer="4",
        is_correct=True,
        time_spent=10,  # 10 secondes
        attempt_number=1,
        hints_used=0,
        created_at=datetime.now()
    )


@pytest.fixture


def test_attempts(test_user, test_exercises):
    """Crée des tentatives de test variées pour un utilisateur et plusieurs exercices."""
    attempts = []

    # Tentative réussie pour le premier exercice
    attempts.append(Attempt(
        user=test_user,
        exercise=test_exercises[0],
        user_answer=test_exercises[0].correct_answer,
        is_correct=True,
        time_spent=random.randint(5, 15),
        attempt_number=1,
        hints_used=0,
        created_at=datetime.now() - timedelta(days=3, hours=1)
    ))

    # Tentative échouée puis réussie pour le deuxième exercice
    attempts.append(Attempt(
        user=test_user,
        exercise=test_exercises[1],
        user_answer="24",  # Mauvaise réponse
        is_correct=False,
        time_spent=random.randint(5, 10),
        attempt_number=1,
        hints_used=1,
        created_at=datetime.now() - timedelta(days=2, hours=2)
    ))

    attempts.append(Attempt(
        user=test_user,
        exercise=test_exercises[1],
        user_answer=test_exercises[1].correct_answer,
        is_correct=True,
        time_spent=random.randint(3, 8),
        attempt_number=2,
        hints_used=1,
        created_at=datetime.now() - timedelta(days=2, hours=1)
    ))

    # Tentative réussie pour le troisième exercice
    attempts.append(Attempt(
        user=test_user,
        exercise=test_exercises[2],
        user_answer=test_exercises[2].correct_answer,
        is_correct=True,
        time_spent=random.randint(3, 8),
        attempt_number=1,
        hints_used=0,
        created_at=datetime.now() - timedelta(days=1, hours=1)
    ))

    return attempts


@pytest.fixture


def test_logic_challenge():
    """Crée un défi logique de test."""
    return LogicChallenge(
        title="Test Logic Challenge",
        challenge_type=LogicChallengeType.SEQUENCE,
        description="Trouvez le prochain nombre dans la séquence: 2, 4, 8, 16, ...",
        correct_answer="32",
        age_group=AgeGroup.GROUP_10_12,
        solution_explanation="La séquence double à chaque étape (×2)",
        hint_level1="Observez comment chaque nombre est lié au précédent",
        hint_level2="C'est une progression géométrique",
        hint_level3="Multipliez par 2",
        difficulty_rating=2.0,
        estimated_time_minutes=5,
        created_at=datetime.now()
    )


@pytest.fixture


def test_logic_challenges():
    """Crée une liste de défis logiques de test variés."""
    return [
        LogicChallenge(
            title="Suite logique",
            challenge_type=LogicChallengeType.SEQUENCE,
            description="Trouvez le prochain nombre dans la séquence: 2, 4, 8, 16, ...",
            correct_answer="32",
            age_group=AgeGroup.GROUP_10_12,
            solution_explanation="La séquence double à chaque étape (×2)",
            hint_level1="Observez comment chaque nombre est lié au précédent",
            hint_level2="C'est une progression géométrique",
            hint_level3="Multipliez par 2",
            difficulty_rating=2.0,
            estimated_time_minutes=5,
            created_at=datetime.now() - timedelta(days=3)
        ),
        LogicChallenge(
            title="Énigme mathématique",
            challenge_type=LogicChallengeType.PUZZLE,
            description="Si un crayon coûte 1 crédit et un cahier coûte 5 crédits\
                , combien coûtent 2 crayons et 3 cahiers?",
            correct_answer="17",
            age_group=AgeGroup.GROUP_7_9,
            solution_explanation="2 crayons = 2 × 1 = 2 crédits, 3 cahiers = 3 × 5\
                = 15 crédits. Total = 2 + 15 = 17 crédits.",
            hint_level1="Calculez d'abord le coût total des crayons",
            hint_level2="Ensuite, calculez le coût total des cahiers",
            hint_level3="Additionnez les deux résultats",
            difficulty_rating=1.5,
            estimated_time_minutes=3,
            created_at=datetime.now() - timedelta(days=2)
        ),
        LogicChallenge(
            title="Problème de logique",
            challenge_type=LogicChallengeType.LOGIC,
            description="Si tous les Jedi sont sages, et que Yoda est un Jedi, alors quelle affirmation est vraie?",
            correct_answer="Yoda est sage",
            age_group=AgeGroup.GROUP_10_12,
            solution_explanation="C'est un syllogisme: si A implique B, et X est A, alors X est B.",
            hint_level1="Utilisez le raisonnement déductif",
            hint_level2="C'est un exemple de syllogisme",
            hint_level3="Si tous les A sont B, et X est A, alors X est...",
            difficulty_rating=2.5,
            estimated_time_minutes=7,
            created_at=datetime.now() - timedelta(days=1)
        )
    ]

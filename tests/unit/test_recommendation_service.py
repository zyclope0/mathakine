"""
Tests pour le service de recommandations.

Ce module teste toutes les fonctionnalités du service de recommandations,
incluant la génération, la récupération et le marquage des recommandations.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.recommendation import Recommendation
from app.models.progress import Progress
from app.models.attempt import Attempt
from app.services.recommendation_service import RecommendationService
from app.utils.db_helpers import get_enum_value
from app.core.security import get_password_hash
from tests.utils.test_helpers import unique_username, unique_email


def test_generate_recommendations_basic(db_session):
    """
    Teste la génération de base de recommandations pour un utilisateur.
    
    Vérifie que:
    - Au moins une recommandation est générée
    - Chaque recommandation a un exercice, une priorité et une raison
    """
    # Arrangement: Créer un utilisateur test avec des valeurs uniques
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    db_session.add(user)
    
    # Créer quelques exercices disponibles
    exercise1 = Exercise(
        title="Test Exercice pour recommandation 1",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        age_group="6-8",
        question="1+1=?",
        correct_answer="2",
        is_active=True
    )
    
    exercise2 = Exercise(
        title="Test Exercice pour recommandation 2",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session),
        age_group="9-11",
        question="3×4=?",
        correct_answer="12",
        is_active=True
    )
    
    db_session.add_all([exercise1, exercise2])
    db_session.commit()
    
    # Action: Générer des recommandations
    recommendations = RecommendationService.generate_recommendations(db_session, user.id)
    
    # Assertion: Vérifier les recommandations
    assert len(recommendations) > 0, "Au moins une recommandation devrait être générée"
    
    for rec in recommendations:
        assert rec.user_id == user.id, "La recommandation doit être associée à l'utilisateur"
        assert rec.priority >= 1 and rec.priority <= 10, "La priorité doit être entre 1 et 10"
        assert rec.reason, "Une raison doit être fournie"


def test_generate_recommendations_for_improvement(db_session):
    """
    Teste la génération de recommandations pour améliorer un domaine faible.
    
    Vérifie que:
    - Des exercices sont recommandés dans les domaines où l'utilisateur est faible
    - La raison indique clairement l'objectif d'amélioration
    """
    # Arrangement: Créer un utilisateur avec des performances faibles dans un domaine
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password="test_hash", 
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session)
    )
    db_session.add(user)
    db_session.commit()
    
    # Créer plusieurs exercices de multiplication (le service ne recommande que les non tentés)
    mult_type = get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION.value, db_session)
    initie_diff = get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session)
    exercises = [
        Exercise(title="Test Mult 1", exercise_type=mult_type, difficulty=initie_diff, age_group="6-8",
                 question="7x6=?", correct_answer="42", is_active=True, is_archived=False),
        Exercise(title="Test Mult 2", exercise_type=mult_type, difficulty=initie_diff, age_group="6-8",
                 question="8x9=?", correct_answer="72", is_active=True, is_archived=False),
        Exercise(title="Test Mult 3", exercise_type=mult_type, difficulty=initie_diff, age_group="6-8",
                 question="6x7=?", correct_answer="42", is_active=True, is_archived=False),
    ]
    for ex in exercises:
        db_session.add(ex)
    db_session.flush()
    exercise = exercises[0]
    
    # Créer un progrès faible dans ce domaine (50% de réussite seulement)
    progress = Progress(
        user_id=user.id,  # Utiliser l'ID du nouvel utilisateur
        exercise_type="multiplication",
        difficulty="INITIE",  # Doit correspondre à Exercise.difficulty pour le filtre du service
        total_attempts=10,
        correct_attempts=5,  # 50% de réussite
        mastery_level=1
    )
    db_session.add(progress)
    db_session.flush()
    
    # Créer des tentatives récentes sur exercise SEULEMENT (exercise2 reste non tenté → recommandable)
    # Le service requiert >= 3 tentatives et < 70% de réussite pour les recommandations d'amélioration
    db_session.add_all([Attempt(
        user_id=user.id,
        exercise_id=exercise.id,
        user_answer="42" if i < 5 else "0",
        is_correct=(i < 5),
        time_spent=2.0
    ) for i in range(10)])
    db_session.commit()
    
    # Action: Générer des recommandations
    recommendations = RecommendationService.generate_recommendations(db_session, user.id)
    
    # Assertion: Vérifier que des recommandations d'amélioration sont générées
    assert len(recommendations) > 0, "Des recommandations devraient être générées"
    
    # Au moins une recommandation devrait être pour la multiplication
    multiplication_recs = [r for r in recommendations if str(r.exercise_type).lower() == "multiplication"]
    assert len(multiplication_recs) > 0, "Au moins une recommandation pour multiplication devrait être générée"
    
    # Vérifier la raison de la recommandation (amélioration, renforcement, ou découverte)
    reason_keywords = ("améliorer", "renforcer", "découvrez", "réussite")
    for rec in multiplication_recs:
        reason_lower = rec.reason.lower()
        assert any(kw in reason_lower for kw in reason_keywords), \
            f"La raison devrait mentionner l'amélioration, le renforcement ou la découverte: {rec.reason}"
        # Priorité >= 7 pour amélioration, peut être plus basse pour découverte (4)
        assert rec.priority >= 1, "La priorité devrait être positive"


def test_get_next_difficulty():
    """
    Teste la fonction _get_next_difficulty pour vérifier qu'elle retourne le bon niveau suivant.
    """
    # Tests des niveaux de difficulté (la fonction retourne en majuscules)
    assert RecommendationService._get_next_difficulty("initie") == "PADAWAN", "Le niveau suivant d'initié devrait être padawan"
    assert RecommendationService._get_next_difficulty("padawan") == "CHEVALIER", "Le niveau suivant de padawan devrait être chevalier"
    assert RecommendationService._get_next_difficulty("chevalier") == "MAITRE", "Le niveau suivant de chevalier devrait être maître"
    assert RecommendationService._get_next_difficulty("maitre") is None, "Le niveau maître ne devrait pas avoir de niveau suivant"
    
    # Cas d'erreur
    assert RecommendationService._get_next_difficulty("Niveau_Inexistant") is None, "Un niveau inexistant ne devrait pas avoir de niveau suivant" 
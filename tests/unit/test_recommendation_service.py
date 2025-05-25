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
        title="Exercice pour recommandation 1",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        question="1+1=?",
        correct_answer="2",
        is_active=True
    )
    
    exercise2 = Exercise(
        title="Exercice pour recommandation 2",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN.value, db_session),
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
    
    # Créer un exercice dans le domaine à améliorer
    exercise = Exercise(
        title="Exercice de multiplication",
        exercise_type=get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION.value, db_session),
        difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
        question="7x6=?",
        correct_answer="42",
        is_active=True
    )
    db_session.add(exercise)
    
    # Créer un progrès faible dans ce domaine (50% de réussite seulement)
    progress = Progress(
        user_id=user.id,  # Utiliser l'ID du nouvel utilisateur
        exercise_type="multiplication",
        difficulty="initie",
        total_attempts=10,
        correct_attempts=5,  # 50% de réussite
        mastery_level=1
    )
    db_session.add(progress)
    db_session.commit()
    
    # Action: Générer des recommandations
    recommendations = RecommendationService.generate_recommendations(db_session, user.id)
    
    # Assertion: Vérifier que des recommandations d'amélioration sont générées
    assert len(recommendations) > 0, "Des recommandations devraient être générées"
    
    # Au moins une recommandation devrait être pour la multiplication
    multiplication_recs = [r for r in recommendations if r.exercise_type == "multiplication"]
    assert len(multiplication_recs) > 0, "Au moins une recommandation pour multiplication devrait être générée"
    
    # Vérifier la raison de la recommandation
    for rec in multiplication_recs:
        assert "améliorer" in rec.reason.lower() or "renforcer" in rec.reason.lower(), \
            "La raison devrait mentionner l'amélioration ou le renforcement"
        assert rec.priority >= 7, "La priorité devrait être élevée (>=7) pour les domaines à améliorer"


def test_get_next_difficulty():
    """
    Teste la fonction _get_next_difficulty pour vérifier qu'elle retourne le bon niveau suivant.
    """
    # Tests des niveaux de difficulté
    assert RecommendationService._get_next_difficulty("initie") == "padawan", "Le niveau suivant d'initié devrait être padawan"
    assert RecommendationService._get_next_difficulty("padawan") == "chevalier", "Le niveau suivant de padawan devrait être chevalier"
    assert RecommendationService._get_next_difficulty("chevalier") == "maitre", "Le niveau suivant de chevalier devrait être maître"
    assert RecommendationService._get_next_difficulty("maitre") is None, "Le niveau maître ne devrait pas avoir de niveau suivant"
    
    # Cas d'erreur
    assert RecommendationService._get_next_difficulty("Niveau_Inexistant") is None, "Un niveau inexistant ne devrait pas avoir de niveau suivant" 
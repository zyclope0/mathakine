"""
Tests des relations de suppression en cascade entre les modèles.
"""
import pytest
from sqlalchemy import inspect
from app.models.user import User
from app.models.exercise import Exercise 
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt


def test_exercise_cascade_relationship():
    """Vérifie que la relation cascade est correctement configurée dans le modèle Exercise"""
    # Récupérer la relation "attempts" du modèle Exercise
    relationship = inspect(Exercise).relationships.get('attempts')
    
    # Vérifier que la cascade est bien configurée
    assert relationship is not None
    assert 'delete' in relationship.cascade
    assert 'delete-orphan' in relationship.cascade


def test_user_cascade_relationships():
    """Vérifie que les relations cascade sont correctement configurées dans le modèle User"""
    # Récupérer les relations du modèle User
    relationships = {
        'created_exercises': inspect(User).relationships.get('created_exercises'),
        'attempts': inspect(User).relationships.get('attempts'),
        'progress_records': inspect(User).relationships.get('progress_records'),
        'created_logic_challenges': inspect(User).relationships.get('created_logic_challenges'),
        'logic_challenge_attempts': inspect(User).relationships.get('logic_challenge_attempts')
    }
    
    # Vérifier que chaque relation a la cascade correctement configurée
    for name, relationship in relationships.items():
        assert relationship is not None, f"Relation {name} non trouvée"
        assert 'delete' in relationship.cascade, f"Cascade 'delete' manquante pour {name}"
        assert 'delete-orphan' in relationship.cascade, f"Cascade 'delete-orphan' manquante pour {name}"


def test_logic_challenge_cascade_relationship():
    """Vérifie que la relation cascade est correctement configurée dans le modèle LogicChallenge"""
    # Récupérer la relation "attempts" du modèle LogicChallenge
    relationship = inspect(LogicChallenge).relationships.get('attempts')
    
    # Vérifier que la cascade est bien configurée
    assert relationship is not None
    assert 'delete' in relationship.cascade
    assert 'delete-orphan' in relationship.cascade 
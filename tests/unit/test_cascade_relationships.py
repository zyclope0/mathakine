"""
Tests des relations de suppression en cascade entre les modèles.
"""

import pytest
from sqlalchemy import inspect

from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt
from app.models.recommendation import Recommendation
from app.models.user import User
from app.utils.db_helpers import get_enum_value


def test_exercise_cascade_relationship():
    """Vérifie que la relation cascade est correctement configurée dans le modèle Exercise"""
    # Récupérer la relation "attempts" du modèle Exercise
    relationship = inspect(Exercise).relationships.get("attempts")

    # Vérifier que la cascade est bien configurée
    assert relationship is not None
    assert "delete" in relationship.cascade
    assert "delete-orphan" in relationship.cascade


def test_user_cascade_relationships():
    """Vérifie que les relations cascade sont correctement configurées dans le modèle User"""
    # Récupérer les relations du modèle User
    relationships = {
        "created_exercises": inspect(User).relationships.get("created_exercises"),
        "attempts": inspect(User).relationships.get("attempts"),
        "progress_records": inspect(User).relationships.get("progress_records"),
        "recommendations": inspect(User).relationships.get("recommendations"),
        "created_logic_challenges": inspect(User).relationships.get(
            "created_logic_challenges"
        ),
        "logic_challenge_attempts": inspect(User).relationships.get(
            "logic_challenge_attempts"
        ),
    }

    # Vérifier que chaque relation a la cascade correctement configurée
    for name, relationship in relationships.items():
        assert relationship is not None, f"Relation {name} non trouvée"
        assert (
            "delete" in relationship.cascade
        ), f"Cascade 'delete' manquante pour {name}"
        assert (
            "delete-orphan" in relationship.cascade
        ), f"Cascade 'delete-orphan' manquante pour {name}"


def test_logic_challenge_cascade_relationship():
    """Vérifie que la relation cascade est correctement configurée dans le modèle LogicChallenge"""
    # Récupérer la relation "attempts" du modèle LogicChallenge
    relationship = inspect(LogicChallenge).relationships.get("attempts")

    # Vérifier que la cascade est bien configurée
    assert relationship is not None
    assert "delete" in relationship.cascade
    assert "delete-orphan" in relationship.cascade


def test_recommendation_exercise_relationship():
    """Vérifie que la relation entre Recommendation et Exercise est correctement configurée"""
    # Récupérer la relation "exercise" du modèle Recommendation
    relationship = inspect(Recommendation).relationships.get("exercise")

    # Vérifier que la relation est configurée correctement (sans cascade de suppression)
    assert relationship is not None
    # La relation ne doit pas supprimer l'exercice si la recommandation est supprimée
    assert "delete" not in relationship.cascade
    assert "delete-orphan" not in relationship.cascade

"""
Services métier pour Mathakine.
Ce module contient tous les services métier qui encapsulent la logique d'accès aux données
et utilisent le gestionnaire de transactions pour assurer la cohérence des opérations.
"""

from app.services.exercise_service import ExerciseService
from app.services.logic_challenge_service import LogicChallengeService
from app.services.user_service import UserService

__all__ = [
    "ExerciseService",
    "LogicChallengeService",
    "UserService",
]

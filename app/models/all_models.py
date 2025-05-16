"""
Module regroupant tous les modèles de données pour Mathakine.
À importer pour réaliser les opérations de base de données.
"""

from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.models.setting import Setting
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt, LogicChallengeType\
    , AgeGroup
from app.models.recommendation import Recommendation

# Export all models
__all__ = [
    "User",
    "UserRole",
    "Exercise",
    "ExerciseType",
    "DifficultyLevel",
    "Attempt",
    "Progress",
    "Setting",
    "LogicChallenge",
    "LogicChallengeAttempt",
    "LogicChallengeType",
    "AgeGroup",
    "Recommendation"
]

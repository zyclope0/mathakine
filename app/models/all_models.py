"""
Module regroupant tous les modèles de données pour Mathakine.
À importer pour réaliser les opérations de base de données.
"""

from app.models.achievement import Achievement, UserAchievement
from app.models.admin_audit_log import AdminAuditLog
from app.models.attempt import Attempt
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.logic_challenge import (
    AgeGroup,
    LogicChallenge,
    LogicChallengeAttempt,
    LogicChallengeType,
)
from app.models.notification import Notification
from app.models.progress import Progress
from app.models.feedback_report import FeedbackReport
from app.models.recommendation import Recommendation
from app.models.setting import Setting
from app.models.user import User, UserRole
from app.models.user_session import UserSession

# Export all models
__all__ = [
    "AdminAuditLog",
    "User",
    "UserRole",
    "Exercise",
    "ExerciseType",
    "FeedbackReport",
    "DifficultyLevel",
    "Attempt",
    "Progress",
    "Setting",
    "LogicChallenge",
    "LogicChallengeAttempt",
    "LogicChallengeType",
    "AgeGroup",
    "Recommendation",
    "Achievement",
    "UserAchievement",
    "Notification",
    "UserSession",
]

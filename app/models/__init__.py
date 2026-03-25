# Models module for Mathakine
# Core data structures for the Star Wars-themed math learning application

# Legacy tables (requis pour Base.metadata complet)
import app.models.legacy_tables  # noqa: F401
from app.models.achievement import Achievement, UserAchievement
from app.models.admin_audit_log import AdminAuditLog
from app.models.ai_eval_harness_run import AiEvalHarnessCaseResult, AiEvalHarnessRun
from app.models.attempt import Attempt
from app.models.challenge_progress import ChallengeProgress
from app.models.daily_challenge import DailyChallenge
from app.models.diagnostic_result import DiagnosticResult
from app.models.edtech_event import EdTechEvent
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.feedback_report import FeedbackReport
from app.models.logic_challenge import (
    AgeGroup,
    LogicChallenge,
    LogicChallengeAttempt,
    LogicChallengeType,
)
from app.models.notification import Notification
from app.models.point_event import PointEvent
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.models.setting import Setting
from app.models.user import User, UserRole
from app.models.user_session import UserSession

__all__ = [
    "AdminAuditLog",
    "AiEvalHarnessCaseResult",
    "AiEvalHarnessRun",
    "DailyChallenge",
    "DiagnosticResult",
    "EdTechEvent",
    "User",
    "UserRole",
    "Exercise",
    "ExerciseType",
    "FeedbackReport",
    "DifficultyLevel",
    "Attempt",
    "ChallengeProgress",
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
    "PointEvent",
    "UserSession",
]

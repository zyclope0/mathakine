"""
Module regroupant tous les schémas Pydantic pour la validation de l'API Mathakine.
À importer pour valider les données entrantes et sortantes.
"""

from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserInDB, User, UserLogin, Token, TokenData
)
from app.schemas.exercise import (
    ExerciseBase, ExerciseCreate, ExerciseUpdate, ExerciseInDB, Exercise, ExerciseStats
)
from app.schemas.attempt import (
    AttemptBase, AttemptCreate, AttemptUpdate, AttemptInDB, Attempt, AttemptBatch, AttemptStats
)
from app.schemas.progress import (
    ProgressBase, ProgressCreate, ProgressUpdate, ProgressInDB, Progress, UserProgressSummary
)
from app.schemas.setting import (
    SettingBase, SettingCreate, SettingUpdate, SettingInDB, Setting, SettingValueResponse, SettingBatch
)
from app.schemas.logic_challenge import (
    LogicChallengeBase, LogicChallengeCreate, LogicChallengeUpdate, LogicChallengeInDB, LogicChallenge,
    LogicChallengeAttemptBase, LogicChallengeAttemptCreate, LogicChallengeAttemptUpdate, 
    LogicChallengeAttemptInDB, LogicChallengeAttempt, LogicChallengeStats
)
from app.schemas.common import (
    Response, ListResponse, ErrorResponse, StatusCode, ErrorCode, PageInfo, ValidationError, HealthCheck
)

# Export all schemas
__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserInDB", "User", "UserLogin", "Token", "TokenData",
    
    # Exercise schemas
    "ExerciseBase", "ExerciseCreate", "ExerciseUpdate", "ExerciseInDB", "Exercise", "ExerciseStats",
    
    # Attempt schemas
    "AttemptBase", "AttemptCreate", "AttemptUpdate", "AttemptInDB", "Attempt", "AttemptBatch", "AttemptStats",
    
    # Progress schemas
    "ProgressBase", "ProgressCreate", "ProgressUpdate", "ProgressInDB", "Progress", "UserProgressSummary",
    
    # Setting schemas
    "SettingBase", "SettingCreate", "SettingUpdate", "SettingInDB", "Setting", "SettingValueResponse", "SettingBatch",
    
    # Logic Challenge schemas
    "LogicChallengeBase", "LogicChallengeCreate", "LogicChallengeUpdate", "LogicChallengeInDB", "LogicChallenge",
    "LogicChallengeAttemptBase", "LogicChallengeAttemptCreate", "LogicChallengeAttemptUpdate", 
    "LogicChallengeAttemptInDB", "LogicChallengeAttempt", "LogicChallengeStats",
    
    # Common response schemas
    "Response", "ListResponse", "ErrorResponse", "StatusCode", "ErrorCode", "PageInfo", "ValidationError", "HealthCheck"
] 
"""
Module regroupant tous les schémas Pydantic pour la validation de l'API Mathakine.
À importer pour valider les données entrantes et sortantes.
"""

from app.schemas.attempt import (Attempt, AttemptBase, AttemptBatch,
                                 AttemptCreate, AttemptInDB, AttemptStats,
                                 AttemptUpdate)
from app.schemas.common import (ErrorCode, ErrorResponse, HealthCheck,
                                ListResponse, PageInfo, Response, StatusCode,
                                ValidationError)
from app.schemas.exercise import (Exercise, ExerciseBase, ExerciseCreate,
                                  ExerciseInDB, ExerciseStats, ExerciseUpdate)
from app.schemas.logic_challenge import (LogicChallenge, LogicChallengeAttempt,
                                         LogicChallengeAttemptBase,
                                         LogicChallengeAttemptCreate,
                                         LogicChallengeAttemptInDB,
                                         LogicChallengeAttemptUpdate,
                                         LogicChallengeBase,
                                         LogicChallengeCreate,
                                         LogicChallengeInDB,
                                         LogicChallengeStats,
                                         LogicChallengeUpdate)
from app.schemas.progress import (Progress, ProgressBase, ProgressCreate,
                                  ProgressInDB, ProgressUpdate,
                                  UserProgressSummary)
from app.schemas.user import (Token, TokenData, User, UserBase, UserCreate,
                              UserInDB, UserLogin, UserUpdate)
from app.schemas.user_session import (UserSession, UserSessionBase,
                                      UserSessionInDB, UserSessionRevoke)

# Export all schemas
__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserInDB", "User", "UserLogin", "Token", "TokenData",
    
    # User Session schemas
    "UserSessionBase", "UserSessionInDB", "UserSession", "UserSessionRevoke",

    # Exercise schemas
    "ExerciseBase", "ExerciseCreate", "ExerciseUpdate", "ExerciseInDB", "Exercise", "ExerciseStats",

    # Attempt schemas
    "AttemptBase", "AttemptCreate", "AttemptUpdate", "AttemptInDB", "Attempt", "AttemptBatch"\
        , "AttemptStats",

    # Progress schemas
    "ProgressBase", "ProgressCreate", "ProgressUpdate", "ProgressInDB", "Progress"\
        , "UserProgressSummary",

    # Logic Challenge schemas
    "LogicChallengeBase", "LogicChallengeCreate", "LogicChallengeUpdate", "LogicChallengeInDB"\
        , "LogicChallenge",
    "LogicChallengeAttemptBase", "LogicChallengeAttemptCreate", "LogicChallengeAttemptUpdate",
    "LogicChallengeAttemptInDB", "LogicChallengeAttempt", "LogicChallengeStats",

    # Common response schemas
    "Response", "ListResponse", "ErrorResponse", "StatusCode", "ErrorCode", "PageInfo"\
        , "ValidationError", "HealthCheck"
]

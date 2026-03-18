"""
Domaine Auth — services d'authentification (Lot B1).
"""

from app.services.auth.auth_recovery_service import (
    AuthRecoveryError,
    ForgotPasswordResult,
    ResendVerificationResult,
    VerifyEmailResult,
)
from app.services.auth.auth_service import (
    create_registered_user_with_verification,
    create_session,
)
from app.services.auth.auth_session_service import (
    get_current_user_payload,
    perform_login,
    perform_refresh,
)

__all__ = [
    "AuthRecoveryError",
    "ForgotPasswordResult",
    "ResendVerificationResult",
    "VerifyEmailResult",
    "create_registered_user_with_verification",
    "create_session",
    "get_current_user_payload",
    "perform_login",
    "perform_refresh",
]

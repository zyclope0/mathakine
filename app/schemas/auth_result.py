"""
Contrats explicites pour auth_service (Lot E1, F1, F1b).

Remplace les tuples faibles (user, error) par des types typés.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Optional

if TYPE_CHECKING:
    from app.models.user import User

from app.core.types import TokenRefreshResponse


@dataclass(frozen=False)
class VerifyEmailTokenResult:
    """Résultat de verify_email_token. Remplace tuple (user, error)."""

    user: Optional[User] = None
    error_code: Optional[Literal["invalid", "expired", "already_verified"]] = None

    @property
    def is_success(self) -> bool:
        return self.error_code is None


@dataclass(frozen=False)
class ResetPasswordTokenResult:
    """Résultat de reset_password_with_token. Remplace tuple (user, error)."""

    user: Optional[User] = None
    error_code: Optional[Literal["invalid", "expired"]] = None

    @property
    def is_success(self) -> bool:
        return self.error_code is None


@dataclass(frozen=False)
class CreateUserResult:
    """Résultat de create_user (F1). Remplace tuple (user, error_message, status_code)."""

    user: Optional[User] = None
    error_message: Optional[str] = None
    status_code: int = 201

    @property
    def is_success(self) -> bool:
        return self.error_message is None


@dataclass(frozen=False)
class RefreshTokenResult:
    """Résultat de refresh_access_token (F1, F1b). Contrat explicite sur token_data."""

    token_data: Optional[TokenRefreshResponse] = None
    error_message: Optional[str] = None
    status_code: int = 200

    @property
    def is_success(self) -> bool:
        return self.error_message is None


@dataclass(frozen=False)
class UpdatePasswordResult:
    """Résultat de update_user_password (F1). Remplace tuple (bool, Optional[str])."""

    is_success: bool = False
    error_message: Optional[str] = None

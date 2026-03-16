"""
Contrats explicites pour auth_service (Lot E1).

Remplace les tuples faibles (user, error) par des types typés.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Optional

if TYPE_CHECKING:
    from app.models.user import User


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

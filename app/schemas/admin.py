"""
Schémas et exceptions pour les use cases admin (LOT B2).

Remplace les tuples faibles (result, err, code) par des contrats explicites.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.core.user_roles import CanonicalUserRole


class AdminError(Exception):
    """Erreur métier admin : message utilisateur et code HTTP."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# ── Résultats succès ───────────────────────────────────────────────────────


class AdminActionSuccess(BaseModel):
    """Résultat succès simple (config, delete, send-reset, etc.)."""

    status: str = "ok"
    message: str | None = None


class AdminUserMutationResult(BaseModel):
    """Résultat PATCH /api/admin/users/{user_id}."""

    id: int
    username: str
    role: CanonicalUserRole | None = None
    is_active: bool | None = None


class AdminResendVerificationResult(BaseModel):
    """Résultat POST /api/admin/users/{user_id}/resend-verification."""

    already_verified: bool
    message: str


class AdminExportDataResult(BaseModel):
    """Données pour export CSV (headers + rows)."""

    headers: List[str]
    rows: List[List[Any]]


# ── Résultats internes service (D4) ───────────────────────────────────────────
# Remplace les tuples (success, err, code) et (success, already_verified, err, code).


class AdminActionResult(BaseModel):
    """Résultat interne admin (success/error). Remplace tuple (bool, str?, int)."""

    success: bool
    error: str | None = None
    status_code: int = 200


class AdminResendVerificationServiceResult(AdminActionResult):
    """Résultat interne resend_verification. Remplace tuple (bool, bool, str?, int)."""

    already_verified: bool = False


class AdminContentMutationResult(BaseModel):
    """
    Résultat mutation admin content (badge, exercise, challenge) — I3.
    Remplace tuple (Optional[Dict], Optional[str], int).
    """

    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    status_code: int = 200

    @property
    def is_success(self) -> bool:
        return self.error_message is None

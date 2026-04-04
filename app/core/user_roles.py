"""
Source unique de vérité pour les rôles utilisateur.

Ce module introduit une nomenclature canonique compréhensible côté application/API
tout en conservant les valeurs legacy persistées en base de données.

Périmètre strict :
- rôles utilisateur uniquement
- ne pas utiliser pour les niveaux de difficulté, badges ou rangs gamifiés
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Final

from app.models.user import UserRole


class CanonicalUserRole(str, Enum):
    """Rôles utilisateur canoniques exposés par l'application."""

    APPRENANT = "apprenant"
    ENSEIGNANT = "enseignant"
    MODERATEUR = "moderateur"
    ADMIN = "admin"


LEGACY_TO_CANONICAL_USER_ROLE: Final[dict[str, CanonicalUserRole]] = {
    UserRole.PADAWAN.value: CanonicalUserRole.APPRENANT,
    UserRole.MAITRE.value: CanonicalUserRole.ENSEIGNANT,
    UserRole.GARDIEN.value: CanonicalUserRole.MODERATEUR,
    UserRole.ARCHIVISTE.value: CanonicalUserRole.ADMIN,
}

CANONICAL_TO_LEGACY_USER_ROLE: Final[dict[CanonicalUserRole, str]] = {
    canonical: legacy for legacy, canonical in LEGACY_TO_CANONICAL_USER_ROLE.items()
}

ADULT_DASHBOARD_USER_ROLES: Final[tuple[CanonicalUserRole, ...]] = (
    CanonicalUserRole.ENSEIGNANT,
    CanonicalUserRole.MODERATEUR,
    CanonicalUserRole.ADMIN,
)


def _coerce_user_role_value(role: Any) -> str | None:
    """Extrait une valeur de rôle depuis un enum, une string ou un objet compatible."""

    if role is None:
        return None

    raw_value = role.value if hasattr(role, "value") else role
    if raw_value is None:
        return None

    return str(raw_value).strip().lower()


def normalize_user_role(role: Any) -> CanonicalUserRole:
    """
    Normalise un rôle utilisateur vers sa valeur canonique.

    Accepte temporairement les formes canoniques et legacy.
    """

    raw_value = _coerce_user_role_value(role)
    if not raw_value:
        raise ValueError("Rôle utilisateur manquant.")

    if raw_value in LEGACY_TO_CANONICAL_USER_ROLE:
        return LEGACY_TO_CANONICAL_USER_ROLE[raw_value]

    try:
        return CanonicalUserRole(raw_value)
    except ValueError as exc:
        valid_roles = ", ".join(role.value for role in CanonicalUserRole)
        legacy_roles = ", ".join(sorted(LEGACY_TO_CANONICAL_USER_ROLE))
        raise ValueError(
            "Rôle utilisateur invalide. "
            f"Valeurs canoniques: {valid_roles}. "
            f"Alias legacy acceptés: {legacy_roles}."
        ) from exc


def serialize_user_role(role: Any) -> str | None:
    """Sérialise un rôle utilisateur vers la sortie API canonique."""

    if role is None:
        return None
    return normalize_user_role(role).value


def to_legacy_user_role_value(role: Any) -> str:
    """Convertit un rôle canonique ou legacy vers la valeur legacy persistée en DB."""

    canonical_role = normalize_user_role(role)
    return CANONICAL_TO_LEGACY_USER_ROLE[canonical_role]


def to_legacy_user_role_enum(role: Any) -> UserRole:
    """Convertit un rôle canonique ou legacy vers l'enum ORM legacy."""

    return UserRole(to_legacy_user_role_value(role))


def is_apprenant_role(role: Any) -> bool:
    """Indique si un rôle correspond à un apprenant."""

    return serialize_user_role(role) == CanonicalUserRole.APPRENANT.value


def is_admin_role(role: Any) -> bool:
    """Indique si un rôle correspond à l'admin plateforme."""

    return serialize_user_role(role) == CanonicalUserRole.ADMIN.value


def can_access_adult_dashboard(role: Any) -> bool:
    """Autorise uniquement les audiences adultes sur le dashboard analytique."""

    serialized_role = serialize_user_role(role)
    return serialized_role in {role.value for role in ADULT_DASHBOARD_USER_ROLES}

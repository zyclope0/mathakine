from unittest.mock import MagicMock

import pytest

from app.core.user_roles import (
    CanonicalUserRole,
    can_access_adult_dashboard,
    normalize_user_role,
    serialize_user_role,
    to_legacy_user_role_enum,
    to_legacy_user_role_value,
)
from app.models.user import UserRole
from app.schemas.user import UserCreate
from app.utils.db_helpers import adapt_enum_for_db, get_python_enum_value


@pytest.mark.parametrize(
    ("raw_role", "expected_role"),
    [
        ("padawan", CanonicalUserRole.APPRENANT),
        ("apprenant", CanonicalUserRole.APPRENANT),
        ("maitre", CanonicalUserRole.ENSEIGNANT),
        ("enseignant", CanonicalUserRole.ENSEIGNANT),
        ("gardien", CanonicalUserRole.MODERATEUR),
        ("moderateur", CanonicalUserRole.MODERATEUR),
        ("archiviste", CanonicalUserRole.ADMIN),
        ("admin", CanonicalUserRole.ADMIN),
    ],
)
def test_normalize_user_role_accepts_legacy_and_canonical_values(raw_role, expected_role):
    assert normalize_user_role(raw_role) == expected_role


def test_normalize_user_role_rejects_invalid_value():
    with pytest.raises(ValueError, match="Rôle utilisateur invalide"):
        normalize_user_role("chevalier")


def test_serialize_user_role_exposes_canonical_api_value():
    assert serialize_user_role(UserRole.GARDIEN) == CanonicalUserRole.MODERATEUR.value


def test_to_legacy_user_role_value_maps_canonical_role_to_db_value():
    assert to_legacy_user_role_value("admin") == UserRole.ARCHIVISTE.value


def test_to_legacy_user_role_enum_maps_canonical_role_to_orm_enum():
    assert to_legacy_user_role_enum("enseignant") == UserRole.MAITRE


def test_adapt_enum_for_db_accepts_canonical_user_roles():
    mock_db = MagicMock()
    assert adapt_enum_for_db("UserRole", "enseignant", mock_db) == "MAITRE"


def test_get_python_enum_value_returns_canonical_role_for_userrole():
    assert get_python_enum_value(UserRole, "ARCHIVISTE") == CanonicalUserRole.ADMIN.value


def test_usercreate_schema_accepts_legacy_role_and_exposes_canonical_enum():
    user = UserCreate(
        username="schema_legacy_user",
        email="schema-legacy@example.com",
        password="TestPassword123!",
        role="gardien",
    )

    assert user.role == CanonicalUserRole.MODERATEUR


def test_usercreate_schema_accepts_canonical_role():
    user = UserCreate(
        username="schema_canonical_user",
        email="schema-canonical@example.com",
        password="TestPassword123!",
        role="enseignant",
    )

    assert user.role == CanonicalUserRole.ENSEIGNANT


def test_can_access_adult_dashboard_is_false_for_apprenant():
    assert can_access_adult_dashboard("apprenant") is False


@pytest.mark.parametrize("adult_role", ["enseignant", "moderateur", "admin"])
def test_can_access_adult_dashboard_is_true_for_adult_roles(adult_role):
    assert can_access_adult_dashboard(adult_role) is True

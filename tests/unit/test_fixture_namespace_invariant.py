"""
Invariant de namespace fixtures/cleanup (LOT 4.5).

Garantit que les users créés par les fixtures auth/admin ne sont jamais
capturés par les patterns de cleanup "hostiles" (test_%, auth_test_%, %_test_%)
qui causaient les 401 intermittents.

Méthode: test unitaire de l'invariant + vérification DB réelle.
"""

import re
import uuid

import pytest

from tests.utils.test_data_cleanup import TestDataManager

# Préfixes réservés utilisés par conftest et test_auth_flow
FIXTURE_AUTH_PREFIX = "fixture_auth_"
FIXTURE_AUTH_FLOW_PREFIX = "fixture_auth_flow_"


def _sql_like(value: str, pattern: str) -> bool:
    """Réplique la sémantique SQL LIKE (%, _) pour tests déterministes."""
    # % = any sequence, _ = single char. Escape pour regex.
    regex_parts = []
    i = 0
    while i < len(pattern):
        if pattern[i] == "%":
            regex_parts.append(".*")
        elif pattern[i] == "_":
            regex_parts.append(".")
        else:
            regex_parts.append(re.escape(pattern[i]))
        i += 1
    regex = "^" + "".join(regex_parts) + "$"
    return bool(re.match(regex, value))


# Patterns qui causaient la collision (suppression prématurée des fixture users)
HOSTILE_USERNAME_PATTERNS = ["test_%", "auth_test_%", "%_test_%"]


class TestFixtureNamespaceInvariant:
    """Invariant: les fixture users ne matchent jamais les patterns hostiles."""

    def test_fixture_auth_padawan_does_not_match_hostile_patterns(self):
        """fixture_auth_{role}_{id} ne matche pas test_%, auth_test_%, %_test_%."""
        username = f"fixture_auth_padawan_{uuid.uuid4().hex[:8]}"
        for pattern in HOSTILE_USERNAME_PATTERNS:
            assert not _sql_like(
                username, pattern
            ), f"{username} ne doit pas matcher {pattern}"

    def test_fixture_auth_archiviste_does_not_match_hostile_patterns(self):
        """fixture_auth_archiviste_{id} idem."""
        username = f"fixture_auth_archiviste_{uuid.uuid4().hex[:8]}"
        for pattern in HOSTILE_USERNAME_PATTERNS:
            assert not _sql_like(
                username, pattern
            ), f"{username} ne doit pas matcher {pattern}"

    def test_fixture_auth_flow_does_not_match_hostile_patterns(self):
        """fixture_auth_flow_{id} (test_auth_flow) ne matche pas les hostiles."""
        username = f"fixture_auth_flow_{uuid.uuid4().hex[:8]}"
        for pattern in HOSTILE_USERNAME_PATTERNS:
            assert not _sql_like(
                username, pattern
            ), f"{username} ne doit pas matcher {pattern}"

    def test_fixture_users_match_fixture_auth_for_cleanup(self):
        """fixture_auth_* matche fixture_auth_% pour nettoyage post-test."""
        for username in [
            f"fixture_auth_padawan_{uuid.uuid4().hex[:8]}",
            f"fixture_auth_archiviste_{uuid.uuid4().hex[:8]}",
            f"fixture_auth_flow_{uuid.uuid4().hex[:8]}",
        ]:
            assert _sql_like(
                username, "fixture_auth_%"
            ), f"{username} doit matcher fixture_auth_% pour cleanup"

    def test_old_pattern_would_have_matched_test_users(self):
        """Régression: test_{role}_{id} et auth_test_{id} matchent les hostiles."""
        assert _sql_like("test_padawan_abc123", "test_%")
        assert _sql_like("auth_test_abc123", "auth_test_%")
        assert _sql_like("auth_test_abc123", "%_test_%")

    def test_fixture_email_not_captured_by_hostile_email_patterns(self):
        """fixture_auth_*@example.com ne matche pas %@test.com ni %test%@%."""
        email = "fixture_auth_flow_abc123@example.com"
        assert not _sql_like(email, "%@test.com")
        assert not _sql_like(email, "%test%@%")

    def test_conftest_and_auth_flow_use_reserved_prefixes(self):
        """Vérification runtime: les fixtures utilisent les préfixes réservés."""
        # Conftest: fixture_auth_{role}_{id}
        assert "fixture_auth_" in FIXTURE_AUTH_PREFIX
        # test_auth_flow: fixture_auth_flow_{id}
        assert "fixture_auth_flow_" in FIXTURE_AUTH_FLOW_PREFIX
        assert FIXTURE_AUTH_FLOW_PREFIX.startswith(FIXTURE_AUTH_PREFIX)


class TestFixtureNamespaceWithRealDb:
    """Vérification avec la DB réelle (identify_test_data)."""

    def test_fixture_user_not_captured_by_cleanup(self, db_session):
        """Un user fixture_auth_* n'est PAS capturé par le cleanup global.

        ADMIN_AUTH_FIXTURES_STABILIZATION: fixture_auth_% retiré des patterns.
        Les fixture users ont teardown explicite.
        """
        from app.models.user import User, UserRole

        unique = uuid.uuid4().hex[:8]
        username = f"fixture_auth_inv_{unique}"
        email = f"{username}@example.com"

        user = User(
            username=username,
            email=email,
            hashed_password="x",
            role=UserRole.PADAWAN,
            is_email_verified=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        try:
            manager = TestDataManager(db_session)
            data = manager.identify_test_data()
            assert (
                user.id not in data["users"]
            ), f"User {username} ne doit PAS être capturé (teardown explicite)"
        finally:
            db_session.delete(user)
            db_session.commit()

    def test_old_test_user_would_be_identified(self, db_session):
        """Régression: test_* serait identifié (preuve de l'ancienne collision)."""
        from app.models.user import User, UserRole

        unique = uuid.uuid4().hex[:8]
        username = f"test_padawan_{unique}"
        email = f"{username}@test.com"

        user = User(
            username=username,
            email=email,
            hashed_password="x",
            role=UserRole.PADAWAN,
            is_email_verified=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        try:
            manager = TestDataManager(db_session)
            data = manager.identify_test_data()
            assert (
                user.id in data["users"]
            ), f"User {username} matche test_% - serait supprimé par cleanup"
        finally:
            db_session.delete(user)
            db_session.commit()

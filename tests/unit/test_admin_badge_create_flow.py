"""
Tests unitaires pour le flux de création badge admin (Lot F3).
"""

from app.models.achievement import Achievement
from app.services.admin_badge_create_flow import (
    persist_badge_create,
    prepare_badge_create_data,
    validate_badge_create_pre_persist,
)
from tests.utils.test_helpers import unique_username


class TestPrepareBadgeCreateData:
    """Étape 1 : préparation / normalisation."""

    def test_normalizes_code(self):
        prepared = prepare_badge_create_data(
            {
                "code": "  My Badge  ",
                "name": "Test",
                "requirements": {"attempts_count": 5},
            }
        )
        assert prepared["code"] == "my_badge"

    def test_normalizes_name(self):
        prepared = prepare_badge_create_data(
            {"code": "x", "name": "  Trimmed  ", "requirements": {"attempts_count": 1}}
        )
        assert prepared["name"] == "Trimmed"

    def test_defaults_difficulty(self):
        prepared = prepare_badge_create_data(
            {"code": "x", "name": "Y", "requirements": {"attempts_count": 1}}
        )
        assert prepared["difficulty"] == "bronze"

    def test_extracts_requirements(self):
        req = {"attempts_count": 10}
        prepared = prepare_badge_create_data(
            {"code": "x", "name": "Y", "requirements": req}
        )
        assert prepared["requirements"] == req


class TestValidateBadgeCreatePrePersist:
    """Étape 2 : validation métier."""

    def test_rejects_empty_code(self, db_session):
        prepared = {"code": "", "name": "X", "requirements": {"attempts_count": 1}}
        err, status = validate_badge_create_pre_persist(prepared, db_session)
        assert err == "Le code est obligatoire."
        assert status == 400

    def test_rejects_empty_name(self, db_session):
        prepared = {"code": "x", "name": "", "requirements": {"attempts_count": 1}}
        err, status = validate_badge_create_pre_persist(prepared, db_session)
        assert err == "Le nom est obligatoire."
        assert status == 400

    def test_rejects_invalid_requirements(self, db_session):
        prepared = {"code": "x", "name": "Y", "requirements": {"attempts_count": 0}}
        err, status = validate_badge_create_pre_persist(prepared, db_session)
        assert err is not None
        assert status == 400

    def test_rejects_duplicate_code(self, db_session):
        code = f"dup_{unique_username()}"
        a = Achievement(code=code, name="Existing", requirements={"attempts_count": 1})
        db_session.add(a)
        db_session.commit()

        prepared = {
            "code": code,
            "name": "New",
            "requirements": {"attempts_count": 1},
        }
        err, status = validate_badge_create_pre_persist(prepared, db_session)
        assert "existe déjà" in (err or "")
        assert status == 409

    def test_accepts_valid_prepared(self, db_session):
        prepared = {
            "code": f"valid_{unique_username()}",
            "name": "Valid",
            "requirements": {"attempts_count": 5},
        }
        err, status = validate_badge_create_pre_persist(prepared, db_session)
        assert err is None
        assert status == 0


class TestPersistBadgeCreate:
    """Étape 3 : mutation / persistance."""

    def test_creates_achievement(self, db_session):
        code = f"persist_{unique_username()}"
        prepared = {
            "code": code,
            "name": "Persist Test",
            "description": "Desc",
            "requirements": {"attempts_count": 3},
            "difficulty": "silver",
            "points_reward": 10,
        }
        a = persist_badge_create(db_session, prepared, admin_user_id=None)
        assert a.id is not None
        assert a.code == code
        assert a.name == "Persist Test"
        assert a.requirements == {"attempts_count": 3}
        assert a.is_active is True

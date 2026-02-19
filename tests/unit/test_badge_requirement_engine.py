"""
Tests unitaires pour badge_requirement_engine (Lot C-2).
Détection type, get_requirement_progress.
"""
from app.models.attempt import Attempt
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.user import User, UserRole
from app.services.badge_requirement_engine import (
    detect_requirement_type,
    get_requirement_progress,
)
from app.utils.db_helpers import get_enum_value
from tests.utils.test_helpers import unique_username, unique_email


class TestDetectRequirementType:
    """Tests detect_requirement_type."""

    def test_attempts_count(self):
        assert detect_requirement_type({"attempts_count": 50}) == "attempts_count"

    def test_logic_attempts_count(self):
        assert detect_requirement_type({"logic_attempts_count": 10}) == "logic_attempts_count"

    def test_mixte(self):
        assert detect_requirement_type({"attempts_count": 20, "logic_attempts_count": 5}) == "mixte"

    def test_success_rate(self):
        assert detect_requirement_type({"min_attempts": 50, "success_rate": 80}) == "success_rate"

    def test_consecutive(self):
        assert detect_requirement_type({"exercise_type": "addition", "consecutive_correct": 20}) == "consecutive"
        assert detect_requirement_type({"consecutive_correct": 15}) == "consecutive"

    def test_max_time(self):
        assert detect_requirement_type({"max_time": 5}) == "max_time"

    def test_consecutive_days(self):
        assert detect_requirement_type({"consecutive_days": 7}) == "consecutive_days"

    def test_min_per_type(self):
        assert detect_requirement_type({"min_per_type": 5}) == "min_per_type"

    def test_comeback_days(self):
        assert detect_requirement_type({"comeback_days": 7}) == "comeback"

    def test_empty_or_invalid(self):
        assert detect_requirement_type({}) is None
        assert detect_requirement_type(None) is None


class TestGetRequirementProgress:
    """Tests get_requirement_progress avec DB."""

    def test_attempts_count_progress(self, db_session):
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        req = {"attempts_count": 10}
        p = get_requirement_progress(db_session, user.id, req)
        assert p is not None
        progress, cur, tgt = p
        assert tgt == 10
        assert cur == 0
        assert progress == 0.0

    def test_attempts_count_with_data(self, db_session):
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        ex = Exercise(
            title="Ex",
            exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db_session),
            difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db_session),
            age_group="6-8",
            question="1+1=?",
            correct_answer="2",
            is_active=True,
        )
        db_session.add(ex)
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(ex)

        for _ in range(5):
            db_session.add(Attempt(user_id=user.id, exercise_id=ex.id, user_answer="2", is_correct=True))
        db_session.commit()

        p = get_requirement_progress(db_session, user.id, {"attempts_count": 10})
        assert p is not None
        progress, cur, tgt = p
        assert cur == 5
        assert tgt == 10
        assert progress == 0.5

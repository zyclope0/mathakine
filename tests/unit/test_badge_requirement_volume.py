"""
Tests unitaires pour le cluster attempts/volume (Lot F2).

Vérifie les checkers et progress getters du module badge_requirement_volume.
"""

from app.models.attempt import Attempt
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.user import User, UserRole
from app.services.badges.badge_requirement_engine import (
    check_requirements,
    get_requirement_progress,
)
from app.services.badges.badge_requirement_fallbacks import (
    check_badge_requirements_by_code,
)
from app.services.badges.badge_requirement_volume import (
    check_attempts_count,
    check_logic_attempts_count,
    check_mixte,
    check_success_rate,
    progress_attempts_count,
    progress_mixte,
    progress_success_rate,
)
from app.utils.db_helpers import get_enum_value
from tests.utils.test_helpers import unique_email, unique_username


class TestVolumeCheckers:
    """Tests des checkers du cluster volume."""

    def test_attempts_count_satisfied_with_cache(self, db_session):
        """attempts_count: count >= target avec cache."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        req = {"attempts_count": 5}
        cache = {"attempts_count": 10}
        assert check_attempts_count(db_session, user.id, req, None, cache) is True

    def test_attempts_count_not_satisfied_with_cache(self, db_session):
        """attempts_count: count < target avec cache."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        req = {"attempts_count": 10}
        cache = {"attempts_count": 3}
        assert check_attempts_count(db_session, user.id, req, None, cache) is False

    def test_attempts_count_no_target(self, db_session):
        """attempts_count: pas de target_key → False."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        assert check_attempts_count(db_session, user.id, {}, None, None) is False

    def test_logic_attempts_count_with_cache(self, db_session):
        """logic_attempts_count: utilise logic_correct_count du cache."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        req = {"logic_attempts_count": 3}
        cache = {"logic_correct_count": 5}
        assert check_logic_attempts_count(db_session, user.id, req, None, cache) is True

    def test_mixte_requires_both(self, db_session):
        """mixte: exige attempts_count ET logic_attempts_count."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        req = {"attempts_count": 5, "logic_attempts_count": 3}
        cache = {"attempts_count": 10, "logic_correct_count": 1}
        assert check_mixte(db_session, user.id, req, None, cache) is False

        cache["logic_correct_count"] = 5
        assert check_mixte(db_session, user.id, req, None, cache) is True

    def test_success_rate_satisfied_with_cache(self, db_session):
        """success_rate: min_attempts atteint ET taux >= rate avec cache. G2."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        req = {"min_attempts": 10, "success_rate": 80}
        cache = {"attempts_total": 20, "attempts_correct": 18}  # 90% >= 80%
        assert check_success_rate(db_session, user.id, req, None, cache) is True

    def test_success_rate_not_satisfied_min_attempts(self, db_session):
        """success_rate: total < min_attempts → False."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        req = {"min_attempts": 10, "success_rate": 80}
        cache = {"attempts_total": 5, "attempts_correct": 5}  # 100% mais seulement 5
        assert check_success_rate(db_session, user.id, req, None, cache) is False

    def test_success_rate_no_target_key(self, db_session):
        """success_rate: pas de min_attempts ou success_rate → False."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        assert check_success_rate(db_session, user.id, {}, None, None) is False


class TestVolumeProgress:
    """Tests des progress getters du cluster volume."""

    def test_progress_attempts_count_ratio(self, db_session):
        """progression = min(1, cur/tgt)."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        req = {"attempts_count": 10}
        cache = {"attempts_count": 5}
        result = progress_attempts_count(db_session, user.id, req, cache)
        assert result is not None
        p, c, t = result
        assert p == 0.5
        assert c == 5
        assert t == 10

    def test_progress_mixte_takes_min(self, db_session):
        """mixte: progress = min des deux."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        req = {"attempts_count": 10, "logic_attempts_count": 5}
        cache = {"attempts_count": 8, "logic_correct_count": 2}
        result = progress_mixte(db_session, user.id, req, cache)
        assert result is not None
        p, c, t = result
        assert p == 0.4  # logic: 2/5 = 0.4 < 8/10 = 0.8
        assert c == 2
        assert t == 5

    def test_progress_success_rate_with_cache(self, db_session):
        """progress_success_rate: affiche correct/required (pas total/min_attempts). G2."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        req = {"min_attempts": 10, "success_rate": 80}
        cache = {"attempts_total": 5, "attempts_correct": 4}
        result = progress_success_rate(db_session, user.id, req, cache)
        assert result is not None
        p, correct, required = result
        # required = ceil(max(5,10)*0.8) = 8 ; correct=4 → p_correct=0.5, p_attempts=0.5
        assert required == 8
        assert correct == 4
        assert p == 0.5

    def test_progress_success_rate_complete(self, db_session):
        """progress_success_rate: atteint → p=1.0, affiche correct/required."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        req = {"min_attempts": 10, "success_rate": 80}
        cache = {"attempts_total": 20, "attempts_correct": 18}  # 90% >= 80%
        result = progress_success_rate(db_session, user.id, req, cache)
        assert result is not None
        p, correct, required = result
        assert p == 1.0
        assert correct == 18  # correct affiché
        assert required == 16  # ceil(20*0.8)


class TestVolumeIntegration:
    """Intégration via badge_requirement_engine (comportement observable stable)."""

    def test_check_requirements_attempts_count_via_engine(self, db_session):
        """check_requirements → attempts_count via engine."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        ex = Exercise(
            title="Ex",
            exercise_type=get_enum_value(
                ExerciseType, ExerciseType.ADDITION.value, db_session
            ),
            difficulty=get_enum_value(
                DifficultyLevel, DifficultyLevel.INITIE.value, db_session
            ),
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
            db_session.add(
                Attempt(
                    user_id=user.id, exercise_id=ex.id, user_answer="2", is_correct=True
                )
            )
        db_session.commit()

        req = {"attempts_count": 5}
        assert check_requirements(db_session, user.id, req) is True
        assert check_requirements(db_session, user.id, {"attempts_count": 10}) is False

    def test_get_requirement_progress_attempts_count_via_engine(self, db_session):
        """get_requirement_progress → attempts_count via engine."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        db_session.commit()

        p = get_requirement_progress(db_session, user.id, {"attempts_count": 10})
        assert p is not None
        prog, cur, tgt = p
        assert tgt == 10
        assert cur == 0
        assert prog == 0.0

    def test_fallback_expert_delegates_to_volume_success_rate(self, db_session):
        """H3: Fallback expert délègue à check_success_rate (source unique)."""
        user = User(
            username=unique_username(),
            email=unique_email(),
            hashed_password="hash",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        )
        db_session.add(user)
        ex = Exercise(
            title="Ex",
            exercise_type=get_enum_value(
                ExerciseType, ExerciseType.ADDITION.value, db_session
            ),
            difficulty=get_enum_value(
                DifficultyLevel, DifficultyLevel.INITIE.value, db_session
            ),
            age_group="6-8",
            question="1+1=?",
            correct_answer="2",
            is_active=True,
        )
        db_session.add(ex)
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(ex)

        # Objet minimal: check_badge_requirements_by_code utilise uniquement badge.code
        badge = type("Badge", (), {"code": "expert"})()

        # 50 tentatives, 42 correctes = 84% >= 80% (expert default)
        for i in range(50):
            db_session.add(
                Attempt(
                    user_id=user.id,
                    exercise_id=ex.id,
                    user_answer="2",
                    is_correct=(i < 42),
                )
            )
        db_session.commit()

        assert (
            check_badge_requirements_by_code(db_session, user.id, badge, {}, None)
            is True
        )

        # 30 tentatives, 29 correctes = 96% mais < 50 min_attempts
        db_session.query(Attempt).filter(Attempt.user_id == user.id).delete()
        db_session.commit()
        for i in range(30):
            db_session.add(
                Attempt(
                    user_id=user.id,
                    exercise_id=ex.id,
                    user_answer="2",
                    is_correct=(i < 29),
                )
            )
        db_session.commit()

        assert (
            check_badge_requirements_by_code(db_session, user.id, badge, {}, None)
            is False
        )

"""Tests causaux — points ledger pour défis logiques réussis (lot C1)."""

from app.core.security import get_password_hash
from app.models.logic_challenge import AgeGroup, LogicChallenge, LogicChallengeType
from app.models.point_event import PointEvent
from app.models.user import User, UserRole
from app.services.badges.badge_service import BadgeService
from app.services.challenges.challenge_attempt_service import (
    submit_challenge_attempt_sync,
)
from app.services.exercises.exercise_attempt_service import POINTS_PER_CORRECT_EXERCISE
from app.services.gamification.point_source import PointEventSourceType
from app.utils.db_helpers import get_enum_value
from tests.utils.test_helpers import unique_email, unique_username


def _create_padawan(db_session) -> User:
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password=get_password_hash("Test123!Ab"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_sequence_challenge(db_session, creator_id: int) -> LogicChallenge:
    ch = LogicChallenge(
        title=f"Gamif test chall {unique_username()}",
        description="Description test gamification défi",
        challenge_type=get_enum_value(
            LogicChallengeType, LogicChallengeType.SEQUENCE, db_session
        ),
        age_group=get_enum_value(AgeGroup, AgeGroup.GROUP_10_12, db_session),
        correct_answer="42",
        solution_explanation="42",
        hints=["h1"],
        creator_id=creator_id,
        difficulty_rating=2.0,
        estimated_time_minutes=5,
    )
    db_session.add(ch)
    db_session.commit()
    db_session.refresh(ch)
    return ch


def test_logic_challenge_correct_creates_point_event_and_increments_total(
    db_session,
):
    user = _create_padawan(db_session)
    challenge = _create_sequence_challenge(db_session, user.id)

    submit_challenge_attempt_sync(
        db_session,
        challenge.id,
        user.id,
        "42",
        time_spent=5.0,
        hints_used_count=0,
    )

    db_session.refresh(user)
    assert user.total_points == POINTS_PER_CORRECT_EXERCISE

    events = (
        db_session.query(PointEvent)
        .filter(PointEvent.user_id == user.id)
        .order_by(PointEvent.id)
        .all()
    )
    assert len(events) == 1
    assert events[0].source_type == PointEventSourceType.LOGIC_CHALLENGE_COMPLETED
    assert events[0].source_id == challenge.id
    assert events[0].points_delta == POINTS_PER_CORRECT_EXERCISE


def test_logic_challenge_incorrect_does_not_award_points(db_session):
    user = _create_padawan(db_session)
    challenge = _create_sequence_challenge(db_session, user.id)

    submit_challenge_attempt_sync(
        db_session,
        challenge.id,
        user.id,
        "wrong",
        time_spent=1.0,
        hints_used_count=0,
    )

    db_session.refresh(user)
    assert user.total_points == 0
    assert (
        db_session.query(PointEvent).filter(PointEvent.user_id == user.id).count() == 0
    )


def test_logic_challenge_correct_still_invokes_badges_streak_daily(
    db_session,
    monkeypatch,
):
    """Non-régression : chemins badges / streak / daily toujours appelés après apply_points."""
    user = _create_padawan(db_session)
    challenge = _create_sequence_challenge(db_session, user.id)

    badge_calls: list[int] = []
    streak_calls: list[int] = []
    daily_calls: list[tuple[int, bool]] = []

    def fake_check_badges(self, user_id, attempt_data=None):
        badge_calls.append(user_id)
        return []

    def fake_streak(session, uid, auto_commit=False):
        streak_calls.append(uid)

    def fake_daily(session, uid, ok):
        daily_calls.append((uid, ok))

    monkeypatch.setattr(BadgeService, "check_and_award_badges", fake_check_badges)
    monkeypatch.setattr(
        "app.services.challenges.challenge_attempt_service.update_user_streak",
        fake_streak,
    )
    monkeypatch.setattr(
        "app.services.progress.daily_challenge_service.record_logic_challenge_completed",
        fake_daily,
    )

    submit_challenge_attempt_sync(
        db_session,
        challenge.id,
        user.id,
        "42",
        time_spent=3.0,
        hints_used_count=0,
    )

    assert user.id in badge_calls
    assert streak_calls == [user.id]
    assert daily_calls == [(user.id, True)]

    db_session.refresh(user)
    assert user.total_points == POINTS_PER_CORRECT_EXERCISE

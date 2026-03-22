"""Tests causaux — moteur gamification persistant + ledger."""

import pytest

from app.core.security import get_password_hash
from app.models.point_event import PointEvent
from app.models.user import User, UserRole
from app.services.gamification.exceptions import (
    GamificationUserNotFoundError,
    InvalidGamificationPointsDeltaError,
)
from app.services.gamification.gamification_service import GamificationService
from app.services.gamification.point_source import PointEventSourceType
from app.utils.db_helpers import get_enum_value
from tests.utils.test_helpers import unique_email, unique_username


def _create_user(db_session) -> User:
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


def test_apply_points_updates_user_columns_and_ledger(db_session):
    user = _create_user(db_session)
    out = GamificationService.apply_points(
        db_session,
        user.id,
        150,
        PointEventSourceType.DAILY_CHALLENGE_COMPLETED,
        source_id=99,
        details={"challenge_type": "volume_exercises"},
    )
    db_session.commit()
    db_session.refresh(user)

    assert user.total_points == 150
    assert user.current_level == 2
    assert user.experience_points == 50
    assert out["total_points"] == 150
    assert out["gamification_level"]["current"] == user.current_level

    events = (
        db_session.query(PointEvent)
        .filter(PointEvent.user_id == user.id)
        .order_by(PointEvent.id)
        .all()
    )
    assert len(events) == 1
    assert events[0].points_delta == 150
    assert events[0].balance_after == 150
    assert events[0].source_type == PointEventSourceType.DAILY_CHALLENGE_COMPLETED
    assert events[0].source_id == 99


def test_apply_points_rejects_non_positive_delta(db_session):
    user = _create_user(db_session)
    with pytest.raises(InvalidGamificationPointsDeltaError):
        GamificationService.apply_points(
            db_session,
            user.id,
            0,
            PointEventSourceType.BADGE_AWARDED,
        )


def test_apply_points_user_not_found(db_session):
    with pytest.raises(GamificationUserNotFoundError):
        GamificationService.apply_points(
            db_session,
            999_999,
            10,
            PointEventSourceType.BADGE_AWARDED,
        )


def test_apply_points_sequential_badges_accumulate(db_session):
    user = _create_user(db_session)
    GamificationService.apply_points(
        db_session,
        user.id,
        40,
        PointEventSourceType.BADGE_AWARDED,
        source_id=1,
        details={"code": "a"},
    )
    GamificationService.apply_points(
        db_session,
        user.id,
        60,
        PointEventSourceType.BADGE_AWARDED,
        source_id=2,
        details={"code": "b"},
    )
    db_session.commit()
    db_session.refresh(user)
    assert user.total_points == 100
    assert user.current_level == 2
    assert user.experience_points == 0
    assert (
        db_session.query(PointEvent).filter(PointEvent.user_id == user.id).count() == 2
    )

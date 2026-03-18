from datetime import date
from unittest.mock import patch

from app.core.security import get_password_hash
from app.models.daily_challenge import DailyChallenge
from app.models.user import User, UserRole
from app.services.progress.daily_challenge_service import (
    CHALLENGE_TYPE_LOGIC,
    CHALLENGE_TYPE_SPECIFIC,
    CHALLENGE_TYPE_VOLUME,
    get_or_create_today_for_user,
    record_exercise_completed,
    record_logic_challenge_completed,
)
from app.utils.db_helpers import get_enum_value


def _create_user(db_session, *, username: str, email: str) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash("Force123Jedi"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_get_or_create_today_for_user_is_idempotent(db_session):
    user = _create_user(
        db_session,
        username="test_daily_owner",
        email="test_daily_owner@example.com",
    )

    with patch.object(db_session, "commit", wraps=db_session.commit) as commit_spy:
        first_batch = get_or_create_today_for_user(db_session, user.id)
        first_ids = [challenge.id for challenge in first_batch]

        second_batch = get_or_create_today_for_user(db_session, user.id)
        second_ids = [challenge.id for challenge in second_batch]

    persisted = (
        db_session.query(DailyChallenge)
        .filter(DailyChallenge.user_id == user.id, DailyChallenge.date == date.today())
        .order_by(DailyChallenge.id)
        .all()
    )

    assert len(first_batch) == 3
    assert len(second_batch) == 3
    assert len(persisted) == 3
    assert first_ids == second_ids
    assert commit_spy.call_count == 2


def test_record_exercise_completed_updates_volume_and_specific_challenges(db_session):
    user = _create_user(
        db_session,
        username="test_daily_exercise",
        email="test_daily_exercise@example.com",
    )

    volume = DailyChallenge(
        user_id=user.id,
        date=date.today(),
        challenge_type=CHALLENGE_TYPE_VOLUME,
        metadata_={},
        target_count=1,
        completed_count=0,
        status="pending",
        bonus_points=10,
    )
    specific = DailyChallenge(
        user_id=user.id,
        date=date.today(),
        challenge_type=CHALLENGE_TYPE_SPECIFIC,
        metadata_={"exercise_type": "addition"},
        target_count=1,
        completed_count=0,
        status="pending",
        bonus_points=15,
    )
    logic = DailyChallenge(
        user_id=user.id,
        date=date.today(),
        challenge_type=CHALLENGE_TYPE_LOGIC,
        metadata_={},
        target_count=1,
        completed_count=0,
        status="pending",
        bonus_points=20,
    )
    db_session.add_all([volume, specific, logic])
    db_session.commit()

    completed_now = record_exercise_completed(db_session, user.id, "addition", True)
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(volume)
    db_session.refresh(specific)
    db_session.refresh(logic)

    assert {entry["challenge_type"] for entry in completed_now} == {
        CHALLENGE_TYPE_VOLUME,
        CHALLENGE_TYPE_SPECIFIC,
    }
    assert volume.status == "completed"
    assert specific.status == "completed"
    assert logic.status == "pending"
    assert user.total_points == 25


def test_record_logic_challenge_completed_updates_only_logic_challenges(db_session):
    user = _create_user(
        db_session,
        username="test_daily_logic",
        email="test_daily_logic@example.com",
    )

    logic = DailyChallenge(
        user_id=user.id,
        date=date.today(),
        challenge_type=CHALLENGE_TYPE_LOGIC,
        metadata_={},
        target_count=1,
        completed_count=0,
        status="pending",
        bonus_points=20,
    )
    volume = DailyChallenge(
        user_id=user.id,
        date=date.today(),
        challenge_type=CHALLENGE_TYPE_VOLUME,
        metadata_={},
        target_count=1,
        completed_count=0,
        status="pending",
        bonus_points=10,
    )
    db_session.add_all([logic, volume])
    db_session.commit()

    completed_now = record_logic_challenge_completed(db_session, user.id, True)
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(logic)
    db_session.refresh(volume)

    assert completed_now == [
        {
            "id": logic.id,
            "challenge_type": CHALLENGE_TYPE_LOGIC,
            "bonus_points": 20,
        }
    ]
    assert logic.status == "completed"
    assert volume.status == "pending"
    assert user.total_points == 20

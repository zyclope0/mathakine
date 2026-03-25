"""Tests causaux — table challenge_progress + upsert (lot C3a)."""

from app.core.security import get_password_hash
from app.models.challenge_progress import ChallengeProgress
from app.models.logic_challenge import AgeGroup, LogicChallenge, LogicChallengeType
from app.models.user import User, UserRole
from app.services.challenges.challenge_attempt_service import (
    submit_challenge_attempt_sync,
)
from app.services.challenges.challenge_progress_service import (
    list_challenge_progress_for_user,
    upsert_challenge_progress,
)
from app.utils.db_helpers import get_enum_value
from tests.utils.test_helpers import unique_email, unique_username


def test_upsert_challenge_progress_increments_and_recomputes_rate(db_session):
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password=get_password_hash("Test123!Ab"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    upsert_challenge_progress(db_session, user.id, "sequence", True)
    db_session.commit()

    row = (
        db_session.query(ChallengeProgress)
        .filter(
            ChallengeProgress.user_id == user.id,
            ChallengeProgress.challenge_type == "sequence",
        )
        .one()
    )
    assert row.total_attempts == 1
    assert row.correct_attempts == 1
    assert row.completion_rate == 100.0
    assert row.mastery_level == "expert"

    upsert_challenge_progress(db_session, user.id, "sequence", False)
    db_session.commit()
    db_session.refresh(row)

    assert row.total_attempts == 2
    assert row.correct_attempts == 1
    assert row.completion_rate == 50.0
    assert row.mastery_level == "apprentice"


def test_submit_challenge_attempt_updates_challenge_progress(db_session):
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password=get_password_hash("Test123!Ab"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    ch = LogicChallenge(
        title=f"Prog test {unique_username()}",
        description="d",
        challenge_type=get_enum_value(
            LogicChallengeType, LogicChallengeType.SEQUENCE, db_session
        ),
        age_group=get_enum_value(AgeGroup, AgeGroup.GROUP_10_12, db_session),
        correct_answer="42",
        solution_explanation="e",
        creator_id=user.id,
        difficulty_rating=2.0,
        estimated_time_minutes=5,
    )
    db_session.add(ch)
    db_session.commit()
    db_session.refresh(ch)

    submit_challenge_attempt_sync(
        db_session,
        ch.id,
        user.id,
        "42",
        time_spent=1.0,
        hints_used_count=0,
    )

    rows = (
        db_session.query(ChallengeProgress)
        .filter(ChallengeProgress.user_id == user.id)
        .all()
    )
    assert len(rows) == 1
    assert rows[0].correct_attempts >= 1
    assert rows[0].total_attempts >= 1


def test_list_challenge_progress_for_user_empty_and_populated(db_session):
    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password=get_password_hash("Test123!Ab"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert list_challenge_progress_for_user(db_session, user.id) == []

    upsert_challenge_progress(db_session, user.id, "visual", True)
    db_session.commit()

    out = list_challenge_progress_for_user(db_session, user.id)
    assert len(out) == 1
    assert out[0]["challenge_type"] == "visual"
    assert out[0]["completion_rate"] == 100.0
    assert out[0]["last_attempted_at"] is not None

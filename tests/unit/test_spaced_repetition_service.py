"""DB-backed spaced repetition service (F04-P1)."""

import uuid
from datetime import date

from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.spaced_repetition_item import SpacedRepetitionItem
from app.models.user import User, UserRole
from app.repositories.spaced_repetition_repository import get_item_for_user_exercise
from app.services.exercises.exercise_attempt_service import submit_answer
from app.services.spaced_repetition.sm2_constants import INITIAL_EASE_FACTOR
from app.services.spaced_repetition.spaced_repetition_service import (
    record_exercise_attempt_for_spaced_repetition,
)
from app.utils.db_helpers import get_enum_value


def _make_user_exercise(db_session):
    uid = str(uuid.uuid4())[:8]
    user = User(
        username=f"sr_u_{uid}",
        email=f"sr_{uid}@test.com",
        hashed_password="hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(user)
    db_session.flush()
    exercise = Exercise(
        title=f"SR ex {uid}",
        exercise_type=get_enum_value(
            ExerciseType, ExerciseType.ADDITION.value, db_session
        ),
        difficulty=get_enum_value(
            DifficultyLevel, DifficultyLevel.INITIE.value, db_session
        ),
        age_group="6-8",
        question="1+1=?",
        correct_answer="2",
        choices=["1", "2", "3"],
        explanation="",
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(exercise)
    return user, exercise


def test_record_idempotent_same_attempt_id(db_session):
    user, exercise = _make_user_exercise(db_session)
    fixed = date(2026, 3, 15)
    record_exercise_attempt_for_spaced_repetition(
        db_session,
        user_id=user.id,
        exercise_id=exercise.id,
        is_correct=True,
        time_spent_seconds=10.0,
        attempt_id=1001,
        review_date=fixed,
    )
    db_session.commit()
    row1 = get_item_for_user_exercise(db_session, user.id, exercise.id)
    assert row1 is not None
    rep_after_first = row1.repetition_count

    record_exercise_attempt_for_spaced_repetition(
        db_session,
        user_id=user.id,
        exercise_id=exercise.id,
        is_correct=True,
        time_spent_seconds=10.0,
        attempt_id=1001,
        review_date=fixed,
    )
    db_session.commit()
    row2 = get_item_for_user_exercise(db_session, user.id, exercise.id)
    assert row2.repetition_count == rep_after_first
    assert row2.last_attempt_id == 1001


def test_record_sequential_attempts_advance_state(db_session):
    user, exercise = _make_user_exercise(db_session)
    d0 = date(2026, 1, 1)
    record_exercise_attempt_for_spaced_repetition(
        db_session,
        user_id=user.id,
        exercise_id=exercise.id,
        is_correct=True,
        time_spent_seconds=30.0,
        attempt_id=1,
        review_date=d0,
    )
    db_session.commit()
    row = get_item_for_user_exercise(db_session, user.id, exercise.id)
    assert row.repetition_count == 1
    assert row.next_review_date == date(2026, 1, 2)

    record_exercise_attempt_for_spaced_repetition(
        db_session,
        user_id=user.id,
        exercise_id=exercise.id,
        is_correct=True,
        time_spent_seconds=30.0,
        attempt_id=2,
        review_date=date(2026, 1, 2),
    )
    db_session.commit()
    row = get_item_for_user_exercise(db_session, user.id, exercise.id)
    assert row.repetition_count == 2
    assert row.next_review_date == date(2026, 1, 5)


def test_submit_answer_persists_spaced_repetition_item(db_session):
    user, exercise = _make_user_exercise(db_session)
    submit_answer(
        db_session,
        exercise.id,
        user.id,
        selected_answer="2",
        time_spent=20.0,
    )
    row = get_item_for_user_exercise(db_session, user.id, exercise.id)
    assert row is not None
    assert row.exercise_id == exercise.id
    assert row.ease_factor == round(INITIAL_EASE_FACTOR + 0.1, 2)
    assert row.repetition_count == 1


def test_submit_answer_incorrect_still_creates_sr_row(db_session):
    user, exercise = _make_user_exercise(db_session)
    submit_answer(
        db_session,
        exercise.id,
        user.id,
        selected_answer="99",
        time_spent=1.0,
    )
    row = get_item_for_user_exercise(db_session, user.id, exercise.id)
    assert row is not None
    assert row.repetition_count == 0
    assert row.last_quality == 0

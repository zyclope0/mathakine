"""
Tests unitaires pour le service F32 — Session entrelacée.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.exceptions import InterleavedNotEnoughVariety
from app.models.attempt import Attempt
from app.models.exercise import Exercise, ExerciseType
from app.models.user import User, UserRole
from app.services.interleaved_practice_service import get_interleaved_plan


def _create_user(db):
    uid = uuid.uuid4().hex[:8]
    user = User(
        username=f"interleaved_test_{uid}",
        email=f"interleaved_{uid}@test.com",
        hashed_password="hash",
        role=UserRole.PADAWAN,
        is_email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_exercise(db, exercise_type: str = "addition"):
    ex = Exercise(
        title="Test",
        exercise_type=exercise_type.upper(),
        difficulty="INITIE",
        age_group="6-8",
        question="1+1?",
        correct_answer="2",
        is_active=True,
        creator_id=None,
        is_archived=False,
    )
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return ex


def test_interleaved_plan_not_enough_variety_zero_attempts(db_session):
    """Moins de 2 types éligibles : lève InterleavedNotEnoughVariety."""
    user = _create_user(db_session)
    with pytest.raises(InterleavedNotEnoughVariety):
        get_interleaved_plan(db_session, user.id, length=10)


def test_interleaved_plan_not_enough_variety_one_type(db_session):
    """Un seul type avec >= 2 tentatives et >= 60% : lève InterleavedNotEnoughVariety."""
    user = _create_user(db_session)
    ex = _create_exercise(db_session, "addition")
    for _ in range(3):
        a = Attempt(
            user_id=user.id,
            exercise_id=ex.id,
            user_answer="2",
            is_correct=True,
        )
        db_session.add(a)
    db_session.commit()

    with pytest.raises(InterleavedNotEnoughVariety):
        get_interleaved_plan(db_session, user.id, length=10)


def test_interleaved_plan_success_two_types(db_session):
    """Deux types éligibles : plan valide, pas de doublons consécutifs."""
    user = _create_user(db_session)
    ex_add = _create_exercise(db_session, "addition")
    ex_mul = _create_exercise(db_session, "multiplication")

    for _ in range(3):
        a = Attempt(
            user_id=user.id,
            exercise_id=ex_add.id,
            user_answer="2",
            is_correct=True,
        )
        db_session.add(a)
    for _ in range(3):
        a = Attempt(
            user_id=user.id,
            exercise_id=ex_mul.id,
            user_answer="6",
            is_correct=True,
        )
        db_session.add(a)
    db_session.commit()

    plan = get_interleaved_plan(db_session, user.id, length=10)

    assert plan["session_kind"] == "interleaved"
    assert plan["length"] == 10
    assert len(plan["eligible_types"]) >= 2
    assert len(plan["plan"]) == 10
    assert plan["message_key"] == "dashboard.quickStart.interleavedPedagogy"

    for i in range(1, len(plan["plan"])):
        assert plan["plan"][i] != plan["plan"][i - 1], "Pas de doublons consécutifs"


def test_interleaved_plan_success_three_types(db_session):
    """Trois types éligibles : plan round-robin sur 3 types."""
    user = _create_user(db_session)
    ex_add = _create_exercise(db_session, "addition")
    ex_mul = _create_exercise(db_session, "multiplication")
    ex_div = _create_exercise(db_session, "division")

    for ex in [ex_add, ex_mul, ex_div]:
        for _ in range(3):
            a = Attempt(
                user_id=user.id,
                exercise_id=ex.id,
                user_answer="ok",
                is_correct=True,
            )
            db_session.add(a)
    db_session.commit()

    plan = get_interleaved_plan(db_session, user.id, length=6)

    assert len(plan["plan"]) == 6
    assert set(plan["plan"]) == {"addition", "multiplication", "division"}
    for i in range(1, len(plan["plan"])):
        assert plan["plan"][i] != plan["plan"][i - 1]


def test_interleaved_plan_filters_low_success_rate(db_session):
    """Type avec < 60% réussite : exclu des éligibles."""
    user = _create_user(db_session)
    ex_add = _create_exercise(db_session, "addition")
    ex_mul = _create_exercise(db_session, "multiplication")

    for _ in range(5):
        a = Attempt(
            user_id=user.id,
            exercise_id=ex_add.id,
            user_answer="2",
            is_correct=True,
        )
        db_session.add(a)
    for _ in range(5):
        a = Attempt(
            user_id=user.id,
            exercise_id=ex_mul.id,
            user_answer="wrong",
            is_correct=False,
        )
        db_session.add(a)
    db_session.commit()

    with pytest.raises(InterleavedNotEnoughVariety):
        get_interleaved_plan(db_session, user.id, length=10)


def test_interleaved_plan_length_default(db_session):
    """length=0 ou négatif : fallback sur 10."""
    user = _create_user(db_session)
    ex_add = _create_exercise(db_session, "addition")
    ex_mul = _create_exercise(db_session, "multiplication")
    for ex in [ex_add, ex_mul]:
        for _ in range(3):
            a = Attempt(
                user_id=user.id,
                exercise_id=ex.id,
                user_answer="ok",
                is_correct=True,
            )
            db_session.add(a)
    db_session.commit()

    plan = get_interleaved_plan(db_session, user.id, length=0)
    assert plan["length"] == 10
    assert len(plan["plan"]) == 10

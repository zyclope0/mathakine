"""F04-P2 — lecture agrégée SR (read-model dashboard)."""

import uuid
from datetime import date

from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.spaced_repetition_item import SpacedRepetitionItem
from app.models.user import User, UserRole
from app.repositories.spaced_repetition_repository import (
    aggregate_spaced_repetition_for_user,
)
from app.services.spaced_repetition.spaced_repetition_read_service import (
    get_spaced_repetition_user_summary,
)
from app.services.users.user_service import UserService
from app.utils.db_helpers import get_enum_value


def _user(db_session):
    uid = str(uuid.uuid4())[:8]
    u = User(
        username=f"sr_read_{uid}",
        email=f"sr_read_{uid}@test.com",
        hashed_password="hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(u)
    db_session.flush()
    return u


def _exercise(db_session, suffix: str, **kwargs):
    ex = Exercise(
        title=f"SR read {suffix}",
        exercise_type=get_enum_value(
            ExerciseType, ExerciseType.ADDITION.value, db_session
        ),
        difficulty=get_enum_value(
            DifficultyLevel, DifficultyLevel.INITIE.value, db_session
        ),
        age_group="6-8",
        question="1+1=?",
        correct_answer="2",
        choices=["1", "2"],
        explanation="",
        **kwargs,
    )
    db_session.add(ex)
    db_session.flush()
    return ex


def _sr_row(user_id: int, exercise_id: int, next_d: date) -> SpacedRepetitionItem:
    return SpacedRepetitionItem(
        user_id=user_id,
        exercise_id=exercise_id,
        ease_factor=2.5,
        interval_days=1,
        next_review_date=next_d,
        repetition_count=1,
        last_quality=5,
        last_attempt_id=None,
    )


def test_aggregate_counts_overdue_due_today_and_next_future(db_session):
    u = _user(db_session)
    e1, e2, e3 = (
        _exercise(db_session, "a"),
        _exercise(db_session, "b"),
        _exercise(db_session, "c"),
    )
    today = date(2026, 6, 15)
    db_session.add(_sr_row(u.id, e1.id, date(2026, 6, 14)))
    db_session.add(_sr_row(u.id, e2.id, today))
    db_session.add(_sr_row(u.id, e3.id, date(2026, 6, 20)))
    db_session.commit()

    n, overdue, due_today, next_f = aggregate_spaced_repetition_for_user(
        db_session, u.id, today
    )
    assert n == 3
    assert overdue == 1
    assert due_today == 1
    assert next_f == date(2026, 6, 20)


def test_read_service_payload_shape(db_session):
    u = _user(db_session)
    ex = _exercise(db_session, "one")
    db_session.add(_sr_row(u.id, ex.id, date(2026, 3, 1)))
    db_session.commit()

    payload = get_spaced_repetition_user_summary(
        db_session, u.id, today=date(2026, 2, 1)
    )
    assert payload["f04_initialized"] is True
    assert payload["active_cards_count"] == 1
    assert payload["due_today_count"] == 0
    assert payload["overdue_count"] == 0
    assert payload["next_review_date"] == "2026-03-01"


def test_get_user_stats_for_dashboard_includes_spaced_repetition(db_session):
    u = _user(db_session)
    db_session.commit()

    out = UserService.get_user_stats_for_dashboard(db_session, u.id, "30")
    assert "spaced_repetition" in out
    sr = out["spaced_repetition"]
    assert sr["f04_initialized"] is False
    assert sr["active_cards_count"] == 0
    assert sr["due_today_count"] == 0
    assert sr["overdue_count"] == 0
    assert sr["next_review_date"] is None


def test_read_model_excludes_archived_exercise_cards(db_session):
    u = _user(db_session)
    ex = _exercise(db_session, "archived", is_archived=True)
    today = date(2026, 6, 15)
    db_session.add(_sr_row(u.id, ex.id, today))
    db_session.commit()

    n, overdue, due_today, next_f = aggregate_spaced_repetition_for_user(
        db_session, u.id, today
    )
    assert n == 0
    assert overdue == 0
    assert due_today == 0
    assert next_f is None

    payload = get_spaced_repetition_user_summary(db_session, u.id, today=today)
    assert payload["f04_initialized"] is False
    assert payload["active_cards_count"] == 0
    assert payload["due_today_count"] == 0
    assert payload["overdue_count"] == 0
    assert payload["next_review_date"] is None

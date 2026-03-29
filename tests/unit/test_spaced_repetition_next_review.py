"""F04-P4 — prochaine révision due (lecture seule, ordre, payload review-safe)."""

import uuid
from datetime import date

from sqlalchemy import func

from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.spaced_repetition_item import SpacedRepetitionItem
from app.models.user import User, UserRole
from app.services.spaced_repetition.spaced_repetition_next_review_service import (
    build_next_review_api_payload,
)
from app.utils.db_helpers import get_enum_value


def _user(db_session):
    uid = str(uuid.uuid4())[:8]
    u = User(
        username=f"sr_next_{uid}",
        email=f"sr_next_{uid}@test.com",
        hashed_password="hash",
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(u)
    db_session.flush()
    return u


def _exercise(db_session, suffix: str, **kwargs):
    ex = Exercise(
        title=f"SR next {suffix}",
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
        explanation="spoiler",
        hint="also spoiler",
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


def test_next_review_null_when_nothing_due(db_session):
    u = _user(db_session)
    ex = _exercise(db_session, "future")
    db_session.add(_sr_row(u.id, ex.id, date(2099, 1, 1)))
    db_session.commit()

    out = build_next_review_api_payload(db_session, u.id, today=date(2026, 6, 15))
    assert out["has_due_review"] is False
    assert out["next_review"] is None
    assert out["summary"]["active_cards_count"] == 1


def test_overdue_before_due_today(db_session):
    u = _user(db_session)
    e_over = _exercise(db_session, "over")
    e_today = _exercise(db_session, "today")
    today = date(2026, 6, 15)
    db_session.add(_sr_row(u.id, e_over.id, date(2026, 6, 10)))
    db_session.add(_sr_row(u.id, e_today.id, today))
    db_session.commit()

    out = build_next_review_api_payload(db_session, u.id, today=today)
    assert out["has_due_review"] is True
    nr = out["next_review"]
    assert nr["exercise_id"] == e_over.id
    assert nr["due_status"] == "overdue"


def test_oldest_overdue_date_first(db_session):
    u = _user(db_session)
    e_old = _exercise(db_session, "old")
    e_new = _exercise(db_session, "newer")
    today = date(2026, 6, 15)
    db_session.add(_sr_row(u.id, e_new.id, date(2026, 6, 12)))
    db_session.add(_sr_row(u.id, e_old.id, date(2026, 6, 1)))
    db_session.commit()

    out = build_next_review_api_payload(db_session, u.id, today=today)
    assert out["next_review"]["exercise_id"] == e_old.id


def test_due_today_tie_breaker_by_review_item_id(db_session):
    u = _user(db_session)
    e1 = _exercise(db_session, "a")
    e2 = _exercise(db_session, "b")
    today = date(2026, 6, 15)
    db_session.add(_sr_row(u.id, e2.id, today))
    db_session.add(_sr_row(u.id, e1.id, today))
    db_session.commit()

    out = build_next_review_api_payload(db_session, u.id, today=today)
    rows = (
        db_session.query(SpacedRepetitionItem)
        .filter(SpacedRepetitionItem.user_id == u.id)
        .order_by(SpacedRepetitionItem.id.asc())
        .all()
    )
    assert out["next_review"]["review_item_id"] == rows[0].id


def test_exercise_payload_review_safe(db_session):
    u = _user(db_session)
    ex = _exercise(db_session, "mcq")
    db_session.add(_sr_row(u.id, ex.id, date(2026, 1, 1)))
    db_session.commit()

    out = build_next_review_api_payload(db_session, u.id, today=date(2026, 6, 1))
    ex_out = out["next_review"]["exercise"]
    for forbidden in ("correct_answer", "explanation", "hint"):
        assert forbidden not in ex_out
    assert ex_out["question"] == "1+1=?"
    assert ex_out["choices"] == ["1", "2"]


def test_archived_exercise_excluded_no_actionable_card(db_session):
    u = _user(db_session)
    ex = _exercise(db_session, "arch", is_archived=True)
    db_session.add(_sr_row(u.id, ex.id, date(2020, 1, 1)))
    db_session.commit()

    out = build_next_review_api_payload(db_session, u.id, today=date(2026, 6, 1))
    assert out["has_due_review"] is False
    assert out["next_review"] is None
    assert out["summary"]["f04_initialized"] is False
    assert out["summary"]["active_cards_count"] == 0
    assert out["summary"]["due_today_count"] == 0
    assert out["summary"]["overdue_count"] == 0


def test_read_only_no_row_mutation(db_session):
    u = _user(db_session)
    ex = _exercise(db_session, "ro")
    db_session.add(_sr_row(u.id, ex.id, date(2026, 1, 1)))
    db_session.commit()

    today = date(2026, 6, 1)
    updated_before = db_session.query(
        func.max(SpacedRepetitionItem.updated_at)
    ).scalar()
    build_next_review_api_payload(db_session, u.id, today=today)
    build_next_review_api_payload(db_session, u.id, today=today)
    updated_after = db_session.query(func.max(SpacedRepetitionItem.updated_at)).scalar()
    assert updated_before == updated_after

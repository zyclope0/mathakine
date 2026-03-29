"""F04-P4 — GET /api/users/me/reviews/next (auth, forme JSON)."""

import uuid
from datetime import date

import pytest

from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.spaced_repetition_item import SpacedRepetitionItem
from app.utils.db_helpers import get_enum_value


@pytest.mark.asyncio
async def test_reviews_next_unauthorized(client):
    r = await client.get("/api/users/me/reviews/next")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_reviews_next_authenticated_shape(padawan_client, db_session):
    pc = padawan_client
    client = pc["client"]
    user_id = pc["user_id"]

    uid = str(uuid.uuid4())[:8]
    ex = Exercise(
        title=f"API SR next {uid}",
        exercise_type=get_enum_value(
            ExerciseType, ExerciseType.ADDITION.value, db_session
        ),
        difficulty=get_enum_value(
            DifficultyLevel, DifficultyLevel.INITIE.value, db_session
        ),
        age_group="6-8",
        question="2+2=?",
        correct_answer="4",
        choices=["3", "4"],
        explanation="no",
    )
    db_session.add(ex)
    db_session.flush()
    db_session.add(
        SpacedRepetitionItem(
            user_id=user_id,
            exercise_id=ex.id,
            ease_factor=2.5,
            interval_days=1,
            next_review_date=date(2020, 1, 1),
            repetition_count=1,
            last_quality=5,
            last_attempt_id=None,
        )
    )
    db_session.commit()

    r = await client.get("/api/users/me/reviews/next")
    assert r.status_code == 200
    body = r.json()
    assert body["has_due_review"] is True
    assert "summary" in body
    for k in (
        "f04_initialized",
        "active_cards_count",
        "due_today_count",
        "overdue_count",
        "next_review_date",
    ):
        assert k in body["summary"]
    nr = body["next_review"]
    assert nr["review_item_id"] >= 1
    assert nr["exercise_id"] == ex.id
    assert nr["due_status"] == "overdue"
    assert nr["next_review_date"] == "2020-01-01"
    exj = nr["exercise"]
    assert exj["id"] == ex.id
    for forbidden in ("correct_answer", "explanation", "hint"):
        assert forbidden not in exj

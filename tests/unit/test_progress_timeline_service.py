"""
Tests unitaires pour le service F07 — Courbe d'évolution temporelle.
"""

import uuid
from datetime import datetime, timezone

import pytest

from app.models.attempt import Attempt
from app.models.exercise import DifficultyLevel, Exercise, ExerciseType
from app.models.user import User, UserRole
from app.services.progress.progress_timeline_service import (
    DEFAULT_PERIOD,
    VALID_PERIODS,
    get_progress_timeline,
)


def _create_exercise(db, exercise_type: str = "addition"):
    ex = Exercise(
        title="Test",
        exercise_type=ExerciseType(exercise_type.upper()),
        difficulty=DifficultyLevel.INITIE,
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


def _create_user(db):
    uid = uuid.uuid4().hex[:8]
    user = User(
        username=f"timeline_test_{uid}",
        email=f"timeline_{uid}@test.com",
        hashed_password="hash",
        role=UserRole.PADAWAN,
        is_email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_valid_periods():
    """Vérifie que les périodes valides sont 7d et 30d."""
    assert VALID_PERIODS == frozenset({"7d", "30d"})
    assert DEFAULT_PERIOD == "7d"


def test_get_progress_timeline_empty(db_session):
    """Aucune tentative : points avec attempts=0, success_rate_pct=0, avg_time null."""
    user = _create_user(db_session)
    # Fixer la date pour des bornes prévisibles
    fake_now = datetime(2026, 3, 7, 12, 0, 0, tzinfo=timezone.utc)

    result = get_progress_timeline(
        db_session, user.id, period="7d", now_fn=lambda: fake_now
    )

    assert result["period"] == "7d"
    assert result["from"] == "2026-03-01"
    assert result["to"] == "2026-03-07"
    assert len(result["points"]) == 7
    for p in result["points"]:
        assert p["attempts"] == 0
        assert p["correct"] == 0
        assert p["success_rate_pct"] == 0.0
        assert p["avg_time_spent_s"] is None
        assert p["by_type"] == {}

    assert result["summary"]["total_attempts"] == 0
    assert result["summary"]["total_correct"] == 0
    assert result["summary"]["overall_success_rate_pct"] == 0.0


def test_get_progress_timeline_with_attempts(db_session):
    """Avec tentatives : agrégation correcte, success_rate, avg_time."""
    user = _create_user(db_session)
    ex = _create_exercise(db_session, "addition")

    # Créer des tentatives à une date fixe (2026-03-05)
    target_date = datetime(2026, 3, 5, 14, 30, 0, tzinfo=timezone.utc)
    for _ in range(3):
        a = Attempt(
            user_id=user.id,
            exercise_id=ex.id,
            user_answer="2",
            is_correct=True,
            time_spent=30.0,
        )
        db_session.add(a)
    a2 = Attempt(
        user_id=user.id,
        exercise_id=ex.id,
        user_answer="wrong",
        is_correct=False,
        time_spent=45.0,
    )
    db_session.add(a2)
    db_session.commit()

    # Patcher created_at via raw SQL ou en mettant à jour après commit
    # SQLAlchemy : on peut utiliser session.execute pour UPDATE
    from sqlalchemy import text

    db_session.execute(
        text("UPDATE attempts SET created_at = :ts WHERE user_id = :uid"),
        {"ts": target_date, "uid": user.id},
    )
    db_session.commit()

    fake_now = datetime(2026, 3, 7, 12, 0, 0, tzinfo=timezone.utc)
    result = get_progress_timeline(
        db_session, user.id, period="7d", now_fn=lambda: fake_now
    )

    assert result["period"] == "7d"
    assert len(result["points"]) == 7

    # Trouver le point du 2026-03-05
    pt_0505 = next(p for p in result["points"] if p["date"] == "2026-03-05")
    assert pt_0505["attempts"] == 4
    assert pt_0505["correct"] == 3
    assert pt_0505["success_rate_pct"] == 75.0  # 3/4 * 100
    assert pt_0505["avg_time_spent_s"] is not None  # (30*3 + 45) / 4 = 33.75
    assert "addition" in pt_0505["by_type"]
    assert pt_0505["by_type"]["addition"]["attempts"] == 4
    assert pt_0505["by_type"]["addition"]["correct"] == 3

    assert result["summary"]["total_attempts"] == 4
    assert result["summary"]["total_correct"] == 3
    assert result["summary"]["overall_success_rate_pct"] == 75.0


def test_get_progress_timeline_period_fallback(db_session):
    """Période invalide : fallback sur 7d."""
    user = _create_user(db_session)
    fake_now = datetime(2026, 3, 7, 12, 0, 0, tzinfo=timezone.utc)

    result = get_progress_timeline(
        db_session, user.id, period="invalid", now_fn=lambda: fake_now
    )
    assert result["period"] == "7d"

    result_30 = get_progress_timeline(
        db_session, user.id, period="30d", now_fn=lambda: fake_now
    )
    assert result_30["period"] == "30d"
    assert len(result_30["points"]) == 30


def test_get_progress_timeline_avg_time_null_when_no_valid_time(db_session):
    """avg_time_spent_s null si time_spent NULL ou négatif."""
    user = _create_user(db_session)
    user_id = user.id
    ex = _create_exercise(db_session)

    a = Attempt(
        user_id=user_id,
        exercise_id=ex.id,
        user_answer="2",
        is_correct=True,
        time_spent=None,  # Pas de temps
    )
    db_session.add(a)
    db_session.commit()

    from sqlalchemy import text

    fake_date = datetime(2026, 3, 5, 12, 0, 0, tzinfo=timezone.utc)
    db_session.execute(
        text("UPDATE attempts SET created_at = :ts WHERE user_id = :uid"),
        {"ts": fake_date, "uid": user_id},
    )
    db_session.commit()

    fake_now = datetime(2026, 3, 7, 12, 0, 0, tzinfo=timezone.utc)
    result = get_progress_timeline(
        db_session, user_id, period="7d", now_fn=lambda: fake_now
    )

    pt = next(p for p in result["points"] if p["date"] == "2026-03-05")
    assert pt["attempts"] == 1
    assert pt["avg_time_spent_s"] is None

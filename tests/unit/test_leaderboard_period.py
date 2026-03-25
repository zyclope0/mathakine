"""Tests causaux — classement par fenêtre temporelle (point_events)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, text

from app.core.leaderboard_period import (
    LeaderboardPeriod,
    leaderboard_period_cutoff_utc,
    parse_leaderboard_period,
)
from app.core.security import get_password_hash
from app.models.point_event import PointEvent
from app.models.user import User, UserRole
from app.services.gamification.gamification_service import GamificationService
from app.services.gamification.point_source import PointEventSourceType
from app.services.users.user_service import UserService
from app.utils.db_helpers import get_enum_value


def test_parse_leaderboard_period_defaults_and_errors():
    assert parse_leaderboard_period(None) is LeaderboardPeriod.ALL
    assert parse_leaderboard_period("") is LeaderboardPeriod.ALL
    assert parse_leaderboard_period("WEEK") is LeaderboardPeriod.WEEK
    with pytest.raises(ValueError):
        parse_leaderboard_period("invalid")


def test_get_leaderboard_week_prefers_recent_point_events(db_session):
    """Utilisateur avec gros cumul mais sans points sur la fenêtre : derrière un actif récent."""
    suffix = uuid.uuid4().hex[:8]
    u_stale = User(
        username=f"stale_{suffix}",
        email=f"stale_{suffix}@t.com",
        hashed_password=get_password_hash("Test123!"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        total_points=0,
    )
    u_hot = User(
        username=f"hot_{suffix}",
        email=f"hot_{suffix}@t.com",
        hashed_password=get_password_hash("Test123!"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        total_points=50,
    )
    db_session.add_all([u_stale, u_hot])
    db_session.commit()
    db_session.refresh(u_stale)
    db_session.refresh(u_hot)

    GamificationService.apply_points(
        db_session,
        u_stale.id,
        99_999,
        PointEventSourceType.EXERCISE_COMPLETED,
        source_id=1,
    )
    db_session.commit()
    old_ts = datetime.now(timezone.utc) - timedelta(days=14)
    db_session.execute(
        text("UPDATE point_events SET created_at = :ts WHERE user_id = :uid"),
        {"ts": old_ts, "uid": u_stale.id},
    )
    db_session.commit()

    GamificationService.apply_points(
        db_session,
        u_hot.id,
        80,
        PointEventSourceType.EXERCISE_COMPLETED,
        source_id=2,
    )
    db_session.commit()

    cutoff = leaderboard_period_cutoff_utc(LeaderboardPeriod.WEEK)
    stale_sum = (
        db_session.query(func.coalesce(func.sum(PointEvent.points_delta), 0))
        .filter(
            PointEvent.user_id == u_stale.id,
            PointEvent.created_at >= cutoff,
        )
        .scalar()
    )
    assert int(stale_sum or 0) == 0

    board = UserService.get_leaderboard_for_api(
        db_session,
        current_user_id=u_hot.id,
        limit=10,
        period=LeaderboardPeriod.WEEK,
    )
    hot_entry = next(e for e in board if e["username"] == u_hot.username)
    assert hot_entry["total_points"] == 80


def test_get_user_rank_week_matches_window(db_session):
    suf = uuid.uuid4().hex[:8]
    u_a = User(
        username=f"rank_a_lb_{suf}",
        email=f"rank_a_lb_{suf}@t.com",
        hashed_password=get_password_hash("Test123!"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    u_b = User(
        username=f"rank_b_lb_{suf}",
        email=f"rank_b_lb_{suf}@t.com",
        hashed_password=get_password_hash("Test123!"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add_all([u_a, u_b])
    db_session.commit()
    db_session.refresh(u_a)
    db_session.refresh(u_b)

    GamificationService.apply_points(
        db_session, u_b.id, 200, PointEventSourceType.EXERCISE_COMPLETED, source_id=1
    )
    GamificationService.apply_points(
        db_session, u_a.id, 50, PointEventSourceType.EXERCISE_COMPLETED, source_id=2
    )
    db_session.commit()

    out_a = UserService.get_user_rank_by_points_for_api(
        db_session, u_a.id, period=LeaderboardPeriod.WEEK
    )
    assert out_a["total_points"] == 50

    out_b = UserService.get_user_rank_by_points_for_api(
        db_session, u_b.id, period=LeaderboardPeriod.WEEK
    )
    assert out_b["total_points"] == 200
    assert out_b["rank"] < out_a["rank"]

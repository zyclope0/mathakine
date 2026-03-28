"""F42-C2 — bridge maîtrise / diagnostic / défis → tier."""

from unittest.mock import patch

import pytest

from app.core.constants import AgeGroups, DifficultyLevels
from app.core.mastery_tier_bridge import (
    canonical_age_group_from_user,
    canonical_age_group_with_fallback,
    challenge_mastery_string_to_pedagogical_band,
    enrich_diagnostic_scores_f42,
    mastery_level_int_to_pedagogical_band,
    mastery_to_tier,
    project_challenge_progress_row_f42,
    project_exercise_progress_f42,
    tier_from_diagnostic_difficulty,
)


def _user_stub(**kwargs):
    u = type("U", (), {})()
    for k, v in kwargs.items():
        setattr(u, k, v)
    return u


def test_mastery_level_int_to_pedagogical_band_matches_c1a_table():
    assert mastery_level_int_to_pedagogical_band(1) == "discovery"
    assert mastery_level_int_to_pedagogical_band(2) == "discovery"
    assert mastery_level_int_to_pedagogical_band(3) == "learning"
    assert mastery_level_int_to_pedagogical_band(4) == "consolidation"
    assert mastery_level_int_to_pedagogical_band(5) == "consolidation"
    assert mastery_level_int_to_pedagogical_band(None) == "learning"
    assert mastery_level_int_to_pedagogical_band(99) == "learning"


def test_mastery_to_tier_monotonic_same_age():
    age = AgeGroups.GROUP_9_11
    t1 = mastery_to_tier(1, age)
    t3 = mastery_to_tier(3, age)
    t5 = mastery_to_tier(5, age)
    assert t1 is not None and t3 is not None and t5 is not None
    assert t1 < t3 < t5


def test_mastery_to_tier_age_group_absent():
    assert mastery_to_tier(3, None) is None
    assert mastery_to_tier(3, "") is None


@patch("app.core.mastery_tier_bridge.logger")
@patch(
    "app.core.mastery_tier_bridge.compute_tier_from_age_group_and_band",
    return_value=99,
)
def test_mastery_to_tier_clamps_high_and_warns(mock_compute, mock_log):
    """F42-P2c — valeur aberrante simulée → clamp 12 + warning."""
    t = mastery_to_tier(3, AgeGroups.GROUP_9_11)
    assert t == 12
    mock_log.warning.assert_called_once()


@patch("app.core.mastery_tier_bridge.logger")
@patch(
    "app.core.mastery_tier_bridge.compute_tier_from_age_group_and_band",
    return_value=-5,
)
def test_mastery_to_tier_clamps_low_and_warns(mock_compute, mock_log):
    t = mastery_to_tier(3, AgeGroups.GROUP_9_11)
    assert t == 1
    mock_log.warning.assert_called_once()


@patch("app.core.mastery_tier_bridge.logger")
def test_mastery_to_tier_no_warning_when_in_range(mock_log):
    t = mastery_to_tier(3, AgeGroups.GROUP_9_11)
    assert 1 <= t <= 12
    mock_log.warning.assert_not_called()


def test_canonical_age_group_prefers_persisted_age_group():
    u = _user_stub(age_group="9-11", preferred_difficulty=DifficultyLevels.INITIE)
    assert canonical_age_group_from_user(u) == AgeGroups.GROUP_9_11


def test_canonical_age_group_fallback_preferred_then_grade():
    u = _user_stub(age_group=None, preferred_difficulty=DifficultyLevels.CHEVALIER)
    assert canonical_age_group_from_user(u) == AgeGroups.GROUP_12_14
    u2 = _user_stub(age_group=None, preferred_difficulty=None, grade_level=12)
    assert canonical_age_group_from_user(u2) == AgeGroups.ADULT


def test_canonical_age_group_with_fallback_when_empty():
    u = _user_stub(age_group=None, preferred_difficulty=None, grade_level=None)
    assert canonical_age_group_with_fallback(u) == AgeGroups.GROUP_9_11


def test_tier_from_diagnostic_difficulty_padawan_band():
    canon = AgeGroups.GROUP_6_8
    t = tier_from_diagnostic_difficulty(DifficultyLevels.PADAWAN, canon)
    assert t == 2  # age_band 0, band learning (1) → 0*3+1+1=2


def test_enrich_diagnostic_scores_f42_adds_fields():
    scores = {
        "addition": {
            "level": 1,
            "difficulty": DifficultyLevels.CHEVALIER,
            "correct": 2,
            "total": 3,
        }
    }
    out = enrich_diagnostic_scores_f42(scores, canonical_age_group=AgeGroups.GROUP_9_11)
    cell = out["addition"]
    assert cell["difficulty"] == DifficultyLevels.CHEVALIER
    assert cell["pedagogical_band"] == "consolidation"
    assert cell["difficulty_tier"] == 6  # age band 1 × 3 + band 2 + 1 = 6


def test_challenge_mastery_string_ordering_maps_to_non_decreasing_tiers():
    canon = AgeGroups.GROUP_12_14
    from app.core.difficulty_tier import compute_tier_from_age_group_and_band

    tiers = []
    for label in ("novice", "apprentice", "adept", "expert"):
        band = challenge_mastery_string_to_pedagogical_band(label)
        tiers.append(compute_tier_from_age_group_and_band(canon, band))
    assert tiers == sorted(tiers)
    assert len(set(tiers)) >= 2


def test_project_exercise_progress_f42():
    prog = type(
        "P",
        (),
        {"mastery_level": 4, "difficulty": "PADAWAN", "user_id": 1},
    )()
    u = _user_stub(age_group="12-14")
    snap = project_exercise_progress_f42(prog, u)
    assert snap["pedagogical_band"] == "consolidation"
    assert snap["difficulty_tier"] is not None
    assert snap["canonical_age_group"] == AgeGroups.GROUP_12_14


def test_project_challenge_progress_row_f42():
    row = type("R", (), {"mastery_level": "expert"})()
    u = _user_stub(age_group="6-8")
    snap = project_challenge_progress_row_f42(row, u)
    assert snap["pedagogical_band"] == "consolidation"
    assert snap["difficulty_tier"] == 3  # 0*3+2+1


def test_update_progress_after_attempt_returns_f42_with_user(db_session):
    from app.core.security import get_password_hash
    from app.models.user import User, UserRole
    from app.repositories.exercise_attempt_repository import (
        update_progress_after_attempt,
    )
    from app.utils.db_helpers import get_enum_value
    from tests.utils.test_helpers import unique_email, unique_username

    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password=get_password_hash("Test123!Ab"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        age_group="9-11",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    snap = update_progress_after_attempt(
        db_session,
        user.id,
        "addition",
        "PADAWAN",
        True,
        1.0,
        user=user,
    )
    assert snap is not None
    assert snap["canonical_age_group"] == AgeGroups.GROUP_9_11
    assert snap["difficulty_tier"] is not None
    # Un seul essai correct → taux 100 % → mastery_level 5 → bande consolidation (C1A).
    assert snap["pedagogical_band"] == "consolidation"
    assert snap["mastery_level"] == 5


def test_update_progress_after_attempt_invalidates_adaptive_context_cache(db_session):
    from datetime import datetime, timedelta, timezone

    from app.core.security import get_password_hash
    from app.models.progress import Progress
    from app.models.user import User, UserRole
    from app.repositories.exercise_attempt_repository import (
        update_progress_after_attempt,
    )
    from app.services.exercises.adaptive_difficulty_service import (
        resolve_adaptive_context,
    )
    from app.utils.db_helpers import get_enum_value
    from tests.utils.test_helpers import unique_email, unique_username

    user = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password=get_password_hash("Test123!Ab"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
        age_group="9-11",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    progress = Progress(
        user_id=user.id,
        exercise_type="addition",
        difficulty="PADAWAN",
        total_attempts=6,
        correct_attempts=5,
        average_time=1.0,
        streak=1,
        highest_streak=1,
        completion_rate=(5 / 6) * 100,
        mastery_level=3,
        last_active_date=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db_session.add(progress)
    db_session.commit()

    ctx_before = resolve_adaptive_context(db_session, user, "ADDITION")
    assert ctx_before.pedagogical_band == "learning"

    snap = update_progress_after_attempt(
        db_session,
        user.id,
        "addition",
        "PADAWAN",
        True,
        1.0,
        user=user,
    )
    assert snap is not None
    assert snap["pedagogical_band"] == "consolidation"

    ctx_after = resolve_adaptive_context(db_session, user, "ADDITION")
    assert ctx_after.pedagogical_band == "consolidation"


@pytest.mark.parametrize(
    "grade_system",
    ["suisse", "unifie", None],
)
def test_swiss_user_without_age_uses_grade_only(grade_system):
    """Pas de mapping spécial : grade_level reste la seule voie si age_group absent."""
    u = _user_stub(
        age_group=None,
        preferred_difficulty=None,
        grade_level=5,
        grade_system=grade_system,
    )
    assert canonical_age_group_from_user(u) == AgeGroups.GROUP_9_11

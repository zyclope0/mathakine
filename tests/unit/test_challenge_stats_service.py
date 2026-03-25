"""Tests causaux — agrégats défis pour GET /api/challenges/stats (lot C2)."""

from app.core.security import get_password_hash
from app.models.logic_challenge import AgeGroup, LogicChallenge, LogicChallengeType
from app.models.user import User, UserRole
from app.services.challenges.challenge_stats_service import ChallengeStatsService
from app.utils.db_helpers import get_enum_value
from tests.utils.test_helpers import unique_email, unique_username


def test_get_challenges_stats_for_api_structure(db_session):
    """Structure { total, by_type, by_difficulty, by_age_group } + compteurs cohérents."""
    u = User(
        username=unique_username(),
        email=unique_email(),
        hashed_password=get_password_hash("Test123!Ab"),
        role=get_enum_value(UserRole, UserRole.PADAWAN.value, db_session),
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    ch = LogicChallenge(
        title="Stats test challenge",
        description="d",
        challenge_type=get_enum_value(
            LogicChallengeType, LogicChallengeType.SEQUENCE, db_session
        ),
        age_group=get_enum_value(AgeGroup, AgeGroup.GROUP_10_12, db_session),
        correct_answer="1",
        solution_explanation="e",
        creator_id=u.id,
        difficulty="PADAWAN",
        difficulty_rating=3.0,
        is_active=True,
        is_archived=False,
    )
    db_session.add(ch)
    db_session.commit()

    out = ChallengeStatsService.get_challenges_stats_for_api(db_session)

    assert out["total"] >= 1
    assert "by_type" in out
    assert "by_difficulty" in out
    assert "by_age_group" in out
    assert "total_archived" in out
    assert isinstance(out["by_type"], dict)
    assert any(v.get("count", 0) >= 1 for v in out["by_type"].values())
    assert "PADAWAN" in out["by_difficulty"] or out["by_difficulty"]

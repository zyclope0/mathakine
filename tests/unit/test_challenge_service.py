"""
Tests unitaires pour app.services.challenge_service.
E3 : validation du flux list_challenges et _execute_list_with_ordering.
E3b : validation du flux create_challenge (préparation, validation, persistance).
"""

import uuid

import pytest

from app.models.logic_challenge import AgeGroup, LogicChallenge, LogicChallengeType
from app.models.user import User


@pytest.fixture
def sample_challenges(db_session):
    """Crée des challenges de test pour les tests de liste."""
    unique_id = uuid.uuid4().hex[:8]
    user = User(
        username=f"list_test_{unique_id}",
        email=f"list_{unique_id}@test.com",
        hashed_password="pw",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    challenges = []
    for i in range(3):
        c = LogicChallenge(
            title=f"Challenge E3 test {i}",
            description="Desc",
            challenge_type=LogicChallengeType.SEQUENCE,
            age_group=AgeGroup.GROUP_10_12,
            correct_answer="42",
            solution_explanation="Expl",
            creator_id=user.id,
            is_active=True,
        )
        db_session.add(c)
        challenges.append(c)
    db_session.commit()
    for c in challenges:
        db_session.refresh(c)
    return challenges


def test_list_challenges_order_recent(db_session, sample_challenges):
    """list_challenges avec order=recent retourne les plus récents en premier."""
    from app.services.challenges.challenge_service import list_challenges

    result = list_challenges(
        db_session,
        challenge_type=LogicChallengeType.SEQUENCE.value,
        limit=10,
        offset=0,
        order="recent",
    )
    assert len(result) >= 3
    ids = [c.id for c in result]
    assert ids == sorted(ids, reverse=True)


def test_list_challenges_order_random_with_total(db_session, sample_challenges):
    """list_challenges avec order=random et total utilise random_offset."""
    from app.services.challenges.challenge_service import list_challenges

    total = len(sample_challenges) + 5
    result = list_challenges(
        db_session,
        challenge_type=LogicChallengeType.SEQUENCE.value,
        limit=2,
        offset=0,
        order="random",
        total=total,
    )
    assert len(result) <= 2


def test_list_challenges_order_random_without_total(db_session, sample_challenges):
    """list_challenges avec order=random sans total utilise func.random fallback."""
    from app.services.challenges.challenge_service import list_challenges

    result = list_challenges(
        db_session,
        challenge_type=LogicChallengeType.SEQUENCE.value,
        limit=2,
        offset=0,
        order="random",
        total=None,
    )
    assert len(result) <= 2


# --- E3b : create_challenge decomposition ---


def test_prepare_challenge_data_normalizes_age_group():
    """_prepare_challenge_data normalise age_group et applique les défauts."""
    from app.services.challenges.challenge_service import _prepare_challenge_data

    data = _prepare_challenge_data(
        title="T",
        description="D",
        challenge_type="SEQUENCE",
        age_group="9-11",
        correct_answer="42",
        solution_explanation="E",
    )
    assert data["age_group"] == AgeGroup.GROUP_10_12
    assert data["hints"] == []
    assert data["visual_data"] == {}
    assert data["is_active"] is True
    assert "created_at" in data


def test_validate_challenge_data_raises_on_empty_title():
    """_validate_challenge_data lève ValueError si titre vide."""
    from app.services.challenges.challenge_service import _validate_challenge_data

    with pytest.raises(ValueError, match="titre"):
        _validate_challenge_data(
            {"title": "", "description": "D", "correct_answer": "42"}
        )


def test_validate_challenge_data_raises_on_empty_description():
    """_validate_challenge_data lève ValueError si description vide."""
    from app.services.challenges.challenge_service import _validate_challenge_data

    with pytest.raises(ValueError, match="description"):
        _validate_challenge_data(
            {"title": "T", "description": "", "correct_answer": "42"}
        )


def test_create_challenge_raises_on_invalid_data(db_session):
    """create_challenge lève ValueError si données invalides."""
    import uuid

    from app.models.user import User
    from app.services.challenges.challenge_service import create_challenge

    user = User(
        username=f"val_{uuid.uuid4().hex[:8]}",
        email=f"val_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="pw",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    with pytest.raises(ValueError, match="titre"):
        create_challenge(
            db_session,
            title="",
            description="D",
            challenge_type="SEQUENCE",
            age_group="9-11",
            correct_answer="42",
            solution_explanation="E",
            creator_id=user.id,
        )


def test_create_challenge_persists_choices_column(db_session):
    """Les choices passés à create_challenge sont stockés sur LogicChallenge.choices."""
    import uuid

    from app.models.user import User
    from app.services.challenges.challenge_service import create_challenge

    user = User(
        username=f"ch_{uuid.uuid4().hex[:8]}",
        email=f"ch_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="pw",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    choice_list = ["8", "9", "10", "11"]
    ch = create_challenge(
        db_session,
        title="QCM",
        description="D",
        challenge_type="SEQUENCE",
        age_group="9-11",
        correct_answer="10",
        solution_explanation="E",
        creator_id=user.id,
        choices=choice_list,
    )
    db_session.refresh(ch)
    assert ch.choices == choice_list

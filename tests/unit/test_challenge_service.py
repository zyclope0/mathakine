"""
Tests unitaires pour app.services.challenge_service.
E3 : validation du flux list_challenges et _execute_list_with_ordering.
E3b : validation du flux create_challenge (préparation, validation, persistance).
"""

import uuid
from datetime import datetime, timezone

import pytest

from app.models.logic_challenge import (
    AgeGroup,
    LogicChallenge,
    LogicChallengeAttempt,
    LogicChallengeType,
)
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
    """list_challenges avec order=random sans total : count + random_offset (pas ORDER BY RANDOM)."""
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


def test_list_challenges_active_only_excludes_archived_active_challenge(db_session):
    """B2: actif + archivé = exclu de la liste publique (active_only=True)."""
    import uuid

    from app.models.user import User
    from app.services.challenges.challenge_service import (
        count_challenges,
        list_challenges,
    )

    unique_id = uuid.uuid4().hex[:8]
    user = User(
        username=f"arch_{unique_id}",
        email=f"arch_{unique_id}@test.com",
        hashed_password="pw",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    arch_tag = f"at1_archived_{unique_id}"
    # Horodatage récent explicite : évite created_at NULL / nullslast hors fenêtre limit.
    recent_ts = datetime(2099, 1, 1, tzinfo=timezone.utc)
    ch = LogicChallenge(
        title=f"Archivé E3b {unique_id}",
        description="D",
        challenge_type=LogicChallengeType.SEQUENCE,
        age_group=AgeGroup.GROUP_10_12,
        correct_answer="1",
        solution_explanation="E",
        creator_id=user.id,
        is_active=True,
        is_archived=True,
        tags=arch_tag,
        created_at=recent_ts,
    )
    db_session.add(ch)
    db_session.commit()
    db_session.refresh(ch)

    public_list = list_challenges(
        db_session,
        tags=arch_tag,
        limit=20,
        offset=0,
        order="recent",
        active_only=True,
    )
    public_ids = {c.id for c in public_list}
    assert ch.id not in public_ids

    public_total = count_challenges(
        db_session,
        tags=arch_tag,
        active_only=True,
    )
    full_count = count_challenges(
        db_session,
        tags=arch_tag,
        active_only=False,
    )
    assert full_count >= public_total
    assert public_total == 0
    admin_list = list_challenges(
        db_session,
        tags=arch_tag,
        limit=20,
        offset=0,
        order="recent",
        active_only=False,
    )
    admin_ids = {c.id for c in admin_list}
    assert ch.id in admin_ids


def test_list_challenges_active_only_false_includes_inactive(db_session):
    """active_only=False inclut les défis is_active=False (contrat admin / listing complet)."""
    import uuid

    from app.models.user import User
    from app.services.challenges.challenge_service import list_challenges

    unique_id = uuid.uuid4().hex[:8]
    user = User(
        username=f"ina_{unique_id}",
        email=f"ina_{unique_id}@test.com",
        hashed_password="pw",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    tag_marker = f"at1_inactive_{unique_id}"
    recent_ts = datetime(2099, 1, 2, tzinfo=timezone.utc)
    inactive = LogicChallenge(
        title=f"Inactif E3b {unique_id}",
        description="D",
        challenge_type=LogicChallengeType.SEQUENCE,
        age_group=AgeGroup.GROUP_10_12,
        correct_answer="1",
        solution_explanation="E",
        creator_id=user.id,
        is_active=False,
        is_archived=False,
        tags=tag_marker,
        created_at=recent_ts,
    )
    db_session.add(inactive)
    db_session.commit()
    db_session.refresh(inactive)

    public = list_challenges(
        db_session,
        tags=tag_marker,
        limit=20,
        order="recent",
        active_only=True,
    )
    assert inactive.id not in {c.id for c in public}

    full = list_challenges(
        db_session,
        tags=tag_marker,
        limit=20,
        order="recent",
        active_only=False,
    )
    assert len(full) >= 1
    assert inactive.id in {c.id for c in full}


def test_execute_list_ordering_random_without_total_uses_id_order_not_func_random():
    """total=None : random_offset sur order_by(id), jamais func.random() (évite scan O(n))."""
    from unittest.mock import MagicMock

    from app.models.logic_challenge import LogicChallenge
    from app.services.challenges.challenge_service import _execute_list_with_ordering

    mock_query = MagicMock()
    tail = MagicMock()
    tail.all.return_value = ["c1", "c2"]
    mock_query.order_by.return_value.offset.return_value.limit.return_value = tail
    mock_query.count.return_value = 10

    out = _execute_list_with_ordering(
        mock_query, order="random", limit=2, offset=0, total=None
    )
    assert out == ["c1", "c2"]
    mock_query.count.assert_called_once()
    mock_query.order_by.assert_called_once_with(LogicChallenge.id)


def test_execute_list_ordering_random_without_total_empty_count():
    """total=None et count 0 : liste vide sans order_by."""
    from unittest.mock import MagicMock

    from app.services.challenges.challenge_service import _execute_list_with_ordering

    mock_query = MagicMock()
    mock_query.count.return_value = 0

    out = _execute_list_with_ordering(
        mock_query, order="random", limit=5, offset=0, total=None
    )
    assert out == []
    mock_query.count.assert_called_once()
    mock_query.order_by.assert_not_called()


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


# --- B3 : get_challenge_stats agrégat atomique ---


def test_get_challenge_stats_no_attempts_zeros_and_rate(db_session):
    """Sans tentative : totaux à 0 et success_rate 0.0 (contrat stable)."""
    import uuid

    from app.models.user import User
    from app.services.challenges.challenge_service import get_challenge_stats

    uid = uuid.uuid4().hex[:8]
    user = User(
        username=f"st_{uid}",
        email=f"st_{uid}@test.com",
        hashed_password="pw",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    ch = LogicChallenge(
        title=f"Stats vides {uid}",
        description="D",
        challenge_type=LogicChallengeType.SEQUENCE,
        age_group=AgeGroup.GROUP_10_12,
        correct_answer="1",
        solution_explanation="E",
        creator_id=user.id,
        is_active=True,
        difficulty_rating=4.0,
    )
    db_session.add(ch)
    db_session.commit()
    db_session.refresh(ch)

    stats = get_challenge_stats(db_session, ch.id)
    assert stats is not None
    assert stats["challenge_id"] == ch.id
    assert stats["title"] == ch.title
    assert stats["total_attempts"] == 0
    assert stats["correct_attempts"] == 0
    assert stats["unique_users"] == 0
    assert stats["success_rate"] == 0.0
    assert stats["difficulty_rating"] == 4.0


def test_get_challenge_stats_single_aggregate_matches_attempts(db_session):
    """Tentatives correctes / incorrectes, utilisateurs distincts, success_rate cohérent."""
    import uuid

    from app.models.user import User
    from app.services.challenges.challenge_service import get_challenge_stats

    uid = uuid.uuid4().hex[:8]
    u1 = User(
        username=f"s1_{uid}",
        email=f"s1_{uid}@test.com",
        hashed_password="pw",
    )
    u2 = User(
        username=f"s2_{uid}",
        email=f"s2_{uid}@test.com",
        hashed_password="pw",
    )
    db_session.add_all([u1, u2])
    db_session.commit()
    db_session.refresh(u1)
    db_session.refresh(u2)

    ch = LogicChallenge(
        title=f"Stats mix {uid}",
        description="D",
        challenge_type=LogicChallengeType.PATTERN,
        age_group=AgeGroup.GROUP_10_12,
        correct_answer="x",
        solution_explanation="E",
        creator_id=u1.id,
        is_active=True,
        difficulty_rating=3.5,
    )
    db_session.add(ch)
    db_session.commit()
    db_session.refresh(ch)

    db_session.add_all(
        [
            LogicChallengeAttempt(
                user_id=u1.id,
                challenge_id=ch.id,
                user_solution="bad",
                is_correct=False,
            ),
            LogicChallengeAttempt(
                user_id=u1.id,
                challenge_id=ch.id,
                user_solution="bad2",
                is_correct=False,
            ),
            LogicChallengeAttempt(
                user_id=u2.id,
                challenge_id=ch.id,
                user_solution="bad3",
                is_correct=False,
            ),
            LogicChallengeAttempt(
                user_id=u2.id,
                challenge_id=ch.id,
                user_solution="x",
                is_correct=True,
            ),
        ]
    )
    db_session.commit()

    stats = get_challenge_stats(db_session, ch.id)
    assert stats is not None
    assert stats["total_attempts"] == 4
    assert stats["correct_attempts"] == 1
    assert stats["unique_users"] == 2
    assert stats["success_rate"] == 25.0


def test_get_challenge_stats_inactive_challenge_returns_none(db_session):
    """get_challenge_stats délègue la résolution du défi à get_challenge (actif seulement)."""
    import uuid

    from app.models.user import User
    from app.services.challenges.challenge_service import get_challenge_stats

    uid = uuid.uuid4().hex[:8]
    user = User(
        username=f"ina_st_{uid}",
        email=f"ina_st_{uid}@test.com",
        hashed_password="pw",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    ch = LogicChallenge(
        title=f"Inactif stats {uid}",
        description="D",
        challenge_type=LogicChallengeType.SEQUENCE,
        age_group=AgeGroup.GROUP_10_12,
        correct_answer="1",
        solution_explanation="E",
        creator_id=user.id,
        is_active=False,
    )
    db_session.add(ch)
    db_session.commit()
    db_session.refresh(ch)

    assert get_challenge_stats(db_session, ch.id) is None

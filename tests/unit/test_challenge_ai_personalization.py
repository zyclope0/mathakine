"""F42-C3A — contexte de génération défis (profil vs âge explicite, calibration distincte)."""

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

from app.core.constants import AgeGroups, DifficultyLevels
from app.core.difficulty_tier import compute_user_target_difficulty_tier
from app.schemas.logic_challenge import ChallengeStreamPersonalizationMeta
from app.services.challenges.challenge_ai_service import _persist_challenge_sync
from app.services.challenges.challenge_generation_context import (
    build_challenge_generation_user_context,
    build_personalization_prompt_section_from_meta,
    personalization_meta_from_context,
)
from app.services.recommendation.recommendation_user_context import (
    RecommendationUserContext,
)


def _user_stub() -> MagicMock:
    u = MagicMock()
    u.id = 99
    u.learning_goal = None
    u.practice_rhythm = None
    u.preferred_difficulty = None
    u.grade_level = None
    return u


def _reco(
    *,
    age: str,
    difficulty: str,
) -> RecommendationUserContext:
    tier = compute_user_target_difficulty_tier(age, difficulty)
    return RecommendationUserContext(
        age_group=age,
        global_default_difficulty=difficulty,
        learning_goal="",
        practice_rhythm="",
        diagnostic_difficulty_by_type={},
        target_difficulty_tier=tier,
    )


def test_profile_path_resolves_age_without_explicit() -> None:
    db = MagicMock()
    user = _user_stub()
    reco = _reco(age=AgeGroups.GROUP_6_8, difficulty=DifficultyLevels.PADAWAN)
    with patch(
        "app.services.challenges.challenge_generation_context.build_recommendation_user_context",
        return_value=reco,
    ):
        ctx = build_challenge_generation_user_context(
            db=db, user=user, explicit_age_group_raw=None
        )
    assert ctx.age_group_source == "profile"
    assert ctx.resolved_age_group == AgeGroups.GROUP_6_8
    assert ctx.explicit_age_group is None


def test_explicit_age_overrides_profile_envelope_keeps_profile_band() -> None:
    db = MagicMock()
    user = _user_stub()
    reco = _reco(age=AgeGroups.GROUP_6_8, difficulty=DifficultyLevels.PADAWAN)
    with patch(
        "app.services.challenges.challenge_generation_context.build_recommendation_user_context",
        return_value=reco,
    ):
        ctx = build_challenge_generation_user_context(
            db=db, user=user, explicit_age_group_raw="12-14"
        )
    assert ctx.age_group_source == "explicit"
    assert ctx.resolved_age_group == AgeGroups.GROUP_12_14
    assert ctx.explicit_age_group == AgeGroups.GROUP_12_14
    assert ctx.user_context_age_group == AgeGroups.GROUP_6_8
    assert ctx.target_pedagogical_band == "learning"


def test_same_explicit_age_different_user_calibration_differs() -> None:
    db = MagicMock()
    user = _user_stub()
    reco_initie = _reco(age=AgeGroups.GROUP_9_11, difficulty=DifficultyLevels.INITIE)
    reco_hard = _reco(age=AgeGroups.GROUP_9_11, difficulty=DifficultyLevels.CHEVALIER)
    with patch(
        "app.services.challenges.challenge_generation_context.build_recommendation_user_context",
        return_value=reco_initie,
    ):
        soft = build_challenge_generation_user_context(
            db=db, user=user, explicit_age_group_raw="9-11"
        )
    with patch(
        "app.services.challenges.challenge_generation_context.build_recommendation_user_context",
        return_value=reco_hard,
    ):
        hard = build_challenge_generation_user_context(
            db=db, user=user, explicit_age_group_raw="9-11"
        )
    assert soft.resolved_target_tier != hard.resolved_target_tier
    assert soft.calibration_text != hard.calibration_text


def test_prompt_section_contains_tier_and_calibration() -> None:
    meta = ChallengeStreamPersonalizationMeta(
        user_context_age_group=AgeGroups.GROUP_9_11,
        age_group_source="profile",
        target_pedagogical_band="learning",
        resolved_target_tier=5,
        calibration_text="9-11 ans – apprentissage : test marker",
    )
    block = build_personalization_prompt_section_from_meta(meta)
    assert "5" in block
    assert "test marker" in block
    assert "learning" in block


def test_personalization_meta_roundtrip_from_context() -> None:
    db = MagicMock()
    user = _user_stub()
    reco = _reco(age=AgeGroups.GROUP_12_14, difficulty=DifficultyLevels.CHEVALIER)
    with patch(
        "app.services.challenges.challenge_generation_context.build_recommendation_user_context",
        return_value=reco,
    ):
        ctx = build_challenge_generation_user_context(
            db=db, user=user, explicit_age_group_raw=None
        )
    meta = personalization_meta_from_context(ctx)
    assert meta.age_group_source == "profile"
    assert meta.calibration_text == ctx.calibration_text


def test_persist_challenge_sync_returns_difficulty_tier() -> None:
    @contextmanager
    def fake_sync_db_session():
        yield MagicMock()

    created = MagicMock()
    created.id = 321
    created.title = "Défi séquence"
    created.description = "desc"
    created.challenge_type = "sequence"
    created.age_group = "9-11"
    created.question = "?"
    created.correct_answer = "42"
    created.solution_explanation = "exp"
    created.hints = ["h1"]
    created.visual_data = {"items": [1, 2, 3]}
    created.difficulty_rating = 3.4
    created.difficulty_tier = 5
    created.estimated_time_minutes = 7
    created.tags = "logic,sequence"
    created.is_active = True
    created.created_at = None
    created.choices = ["40", "41", "42"]

    normalized = {
        "title": "Défi séquence",
        "description": "desc",
        "challenge_type": "sequence",
        "age_group": "9-11",
        "question": "?",
        "correct_answer": "42",
        "solution_explanation": "exp",
        "hints": ["h1"],
        "visual_data": {"items": [1, 2, 3]},
        "difficulty_rating": 3.4,
        "estimated_time_minutes": 7,
        "tags": "logic,sequence",
        "choices": ["40", "41", "42"],
        "response_mode": "single_choice",
    }

    with (
        patch(
            "app.services.challenges.challenge_ai_service.sync_db_session",
            fake_sync_db_session,
        ),
        patch(
            "app.services.challenges.challenge_ai_service.challenge_service.create_challenge",
            return_value=created,
        ),
    ):
        out = _persist_challenge_sync(
            normalized,
            user_id=99,
            challenge_type="sequence",
            model="gpt-test",
            f42_personalization={"resolved_target_tier": 5},
        )

    assert out is not None
    assert out["difficulty_tier"] == 5
    assert out["difficulty_rating"] == 3.4


@pytest.mark.parametrize("raw", ["__profile__", "__PROFILE__ "])
def test_prepare_stream_context_treats_profile_marker_as_omission(raw: str) -> None:
    from app.services.challenges.challenge_stream_service import (
        _is_profile_age_omission_marker,
    )

    assert _is_profile_age_omission_marker(raw) is True

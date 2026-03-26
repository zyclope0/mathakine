"""Tests unitaires — F42 matrice difficulty_tier (1–12)."""

from app.core.constants import AgeGroups
from app.core.difficulty_tier import (
    compute_difficulty_tier_for_exercise_strings,
    compute_user_target_difficulty_tier,
    exercise_tier_filter_expression,
    pedagogical_band_index_from_difficulty,
)
from app.models.logic_challenge import AgeGroup as ChAge


def test_compute_tier_exercise_6_8_initie():
    assert compute_difficulty_tier_for_exercise_strings("6-8", "INITIE") == 1


def test_compute_tier_exercise_9_11_padawan():
    assert compute_difficulty_tier_for_exercise_strings("9-11", "PADAWAN") == 5


def test_compute_tier_exercise_tous_ages_none():
    assert compute_difficulty_tier_for_exercise_strings("tous-ages", "PADAWAN") is None


def test_user_target_tier_all_ages_none():
    assert compute_user_target_difficulty_tier(AgeGroups.ALL_AGES, "PADAWAN") is None


def test_user_target_tier_15_plus_grand_maitre():
    assert compute_user_target_difficulty_tier("15+", "GRAND_MAITRE") == 12


def test_pedagogical_band_easy_medium_hard():
    assert pedagogical_band_index_from_difficulty("easy") == 0
    assert pedagogical_band_index_from_difficulty("medium") == 1
    assert pedagogical_band_index_from_difficulty("hard") == 2


def test_exercise_tier_filter_expression_none_tier_legacy_only():
    expr = exercise_tier_filter_expression(None, "PADAWAN")
    # SQLAlchemy BinaryExpression — compare key column
    assert "difficulty" in str(expr).lower()


def test_logic_challenge_age_group_mapping_import():
    from app.core.difficulty_tier import compute_difficulty_tier_for_logic_challenge

    t = compute_difficulty_tier_for_logic_challenge(ChAge.GROUP_10_12, "PADAWAN", 3.0)
    assert t == 5

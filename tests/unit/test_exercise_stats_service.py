"""Tests pour app.services.exercise_stats_service."""

import pytest

from app.services.exercise_stats_service import ExerciseStatsService


def test_get_exercises_stats_for_api_structure(db_session):
    """Vérifie que get_exercises_stats_for_api retourne la structure attendue."""
    result = ExerciseStatsService.get_exercises_stats_for_api(db_session)

    assert "archive_status" in result
    assert "academy_statistics" in result
    assert "by_discipline" in result
    assert "by_rank" in result
    assert "by_apprentice_group" in result
    assert "global_performance" in result
    assert "legendary_challenges" in result
    assert "sage_wisdom" in result

    ac = result["academy_statistics"]
    assert "total_exercises" in ac
    assert "total_challenges" in ac
    assert "total_content" in ac

    gp = result["global_performance"]
    assert "total_attempts" in gp
    assert "mastery_rate" in gp
    assert "message" in gp

"""
Tests unitaires pour badge_requirement_validation (cluster E4).
"""

import pytest

from app.services.badges.badge_requirement_validation import validate_badge_requirements


class TestValidateBadgeRequirements:
    """Tests validate_badge_requirements."""

    def test_none_returns_error(self):
        ok, err = validate_badge_requirements(None)
        assert not ok
        assert "requis" in (err or "")

    def test_not_dict_returns_error(self):
        ok, err = validate_badge_requirements([])
        assert not ok
        assert "JSON" in (err or "")

    def test_empty_dict_returns_error(self):
        ok, err = validate_badge_requirements({})
        assert not ok
        assert "clé" in (err or "")

    def test_attempts_count_valid(self):
        ok, err = validate_badge_requirements({"attempts_count": 50})
        assert ok
        assert err is None

    def test_attempts_count_invalid(self):
        ok, err = validate_badge_requirements({"attempts_count": 0})
        assert not ok
        assert "attempts_count" in (err or "")

    def test_success_rate_valid(self):
        ok, err = validate_badge_requirements({"min_attempts": 50, "success_rate": 80})
        assert ok
        assert err is None

    def test_success_rate_invalid_min_attempts(self):
        ok, err = validate_badge_requirements({"min_attempts": 0, "success_rate": 80})
        assert not ok
        assert "min_attempts" in (err or "")

    def test_success_rate_invalid_rate(self):
        ok, err = validate_badge_requirements({"min_attempts": 50, "success_rate": 150})
        assert not ok
        assert "success_rate" in (err or "")

    def test_logic_attempts_count_valid(self):
        ok, err = validate_badge_requirements({"logic_attempts_count": 10})
        assert ok
        assert err is None

    def test_mixte_valid(self):
        ok, err = validate_badge_requirements(
            {"attempts_count": 20, "logic_attempts_count": 5}
        )
        assert ok
        assert err is None

    def test_consecutive_correct_valid(self):
        """E6: consecutive_correct >= 1 accepté."""
        ok, err = validate_badge_requirements({"consecutive_correct": 5})
        assert ok
        assert err is None

    def test_consecutive_correct_invalid(self):
        """E6: consecutive_correct < 1 rejeté."""
        ok, err = validate_badge_requirements({"consecutive_correct": 0})
        assert not ok
        assert "consecutive_correct" in (err or "")

    def test_max_time_valid(self):
        """E6: max_time >= 0 accepté."""
        ok, err = validate_badge_requirements({"max_time": 120})
        assert ok
        assert err is None

    def test_max_time_invalid(self):
        """E6: max_time < 0 rejeté."""
        ok, err = validate_badge_requirements({"max_time": -1})
        assert not ok
        assert "max_time" in (err or "")

    def test_consecutive_days_valid(self):
        """E6: consecutive_days >= 1 accepté."""
        ok, err = validate_badge_requirements({"consecutive_days": 7})
        assert ok
        assert err is None

    def test_consecutive_days_invalid(self):
        """E6: consecutive_days < 1 rejeté."""
        ok, err = validate_badge_requirements({"consecutive_days": 0})
        assert not ok
        assert "consecutive_days" in (err or "")

    def test_comeback_days_valid(self):
        """E6: comeback_days >= 1 accepté."""
        ok, err = validate_badge_requirements({"comeback_days": 3})
        assert ok
        assert err is None

    def test_comeback_days_invalid(self):
        """E6: comeback_days < 1 rejeté."""
        ok, err = validate_badge_requirements({"comeback_days": 0})
        assert not ok
        assert "comeback_days" in (err or "")

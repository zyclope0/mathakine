"""
Tests de régression pour TokenTracker.

Couvre le bug M5 (audit 01/03/2026) : key.split("_")[0] tronquait les
challenge_types contenant "_" (ex. LOGIC_SEQUENCE → "LOGIC").
"""

import pytest
from datetime import datetime
from app.utils.token_tracker import TokenTracker


class TestGetDailySummary:
    """Tests pour get_daily_summary (bug M5)."""

    def test_simple_type_without_underscore(self):
        """Type sans underscore — comportement de base inchangé."""
        tracker = TokenTracker()
        tracker.track_usage("SEQUENCE", 100, 50)

        summary = tracker.get_daily_summary()

        assert "SEQUENCE" in summary
        assert summary["SEQUENCE"]["tokens"] == 150

    def test_type_with_single_underscore(self):
        """Régression M5 : type avec un underscore n'est plus tronqué."""
        tracker = TokenTracker()
        tracker.track_usage("LOGIC_SEQUENCE", 100, 50)

        summary = tracker.get_daily_summary()

        assert "LOGIC_SEQUENCE" in summary, (
            "Bug M5 : 'LOGIC_SEQUENCE' tronqué en 'LOGIC' avec key.split('_')[0]"
        )
        assert "LOGIC" not in summary

    def test_type_with_multiple_underscores(self):
        """Type avec plusieurs underscores — pas de troncature."""
        tracker = TokenTracker()
        tracker.track_usage("PATTERN_MATCHING_HARD", 200, 100)

        summary = tracker.get_daily_summary()

        assert "PATTERN_MATCHING_HARD" in summary
        assert "PATTERN" not in summary
        assert "PATTERN_MATCHING" not in summary

    def test_multiple_types_no_collision(self):
        """Plusieurs types distincts n'écrasent pas leurs totaux mutuels."""
        tracker = TokenTracker()
        tracker.track_usage("LOGIC_SEQUENCE", 100, 50)
        tracker.track_usage("LOGIC_VISUAL", 200, 100)
        tracker.track_usage("SEQUENCE", 50, 25)

        summary = tracker.get_daily_summary()

        assert "LOGIC_SEQUENCE" in summary
        assert "LOGIC_VISUAL" in summary
        assert "SEQUENCE" in summary
        assert summary["LOGIC_SEQUENCE"]["tokens"] == 150
        assert summary["LOGIC_VISUAL"]["tokens"] == 300
        assert summary["SEQUENCE"]["tokens"] == 75

    def test_empty_tracker_returns_empty_dict(self):
        """Tracker vide → dict vide."""
        tracker = TokenTracker()
        assert tracker.get_daily_summary() == {}

    def test_different_date_not_included(self):
        """Données d'un autre jour ne sont pas incluses."""
        tracker = TokenTracker()
        tracker.track_usage("SEQUENCE", 100, 50)

        # Demander le résumé pour une date très éloignée
        past_date = datetime(2020, 1, 1)
        summary = tracker.get_daily_summary(past_date)

        assert summary == {}

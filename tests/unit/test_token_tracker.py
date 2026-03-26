"""
Tests de régression pour TokenTracker.

Couvre le bug M5 (audit 01/03/2026) : key.split("_")[0] tronquait les
challenge_types contenant "_" (ex. LOGIC_SEQUENCE → "LOGIC").
"""

from datetime import datetime

import pytest

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

        assert (
            "LOGIC_SEQUENCE" in summary
        ), "Bug M5 : 'LOGIC_SEQUENCE' tronqué en 'LOGIC' avec key.split('_')[0]"
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


class TestWorkloadBreakdown:
    def test_get_stats_groups_by_workload(self):
        tracker = TokenTracker()
        tracker.track_usage("assistant_chat:simple", 100, 50, model="gpt-5-mini")
        tracker.track_usage("exercise_ai:addition", 120, 60, model="o3")
        tracker.track_usage("sequence", 200, 100, model="o3")

        stats = tracker.get_stats(days=1)

        assert stats["by_workload"]["assistant_chat"]["count"] == 1
        assert stats["by_workload"]["exercises_ai"]["count"] == 1
        assert stats["by_workload"]["challenges_ai"]["count"] == 1
        assert "retention" in stats
        assert "cost_disclaimer_fr" in stats

    def test_unknown_metric_key_buckets_unknown_not_challenges(self):
        tracker = TokenTracker()
        tracker.track_usage("weird_legacy_key", 50, 50, model="gpt-4o-mini")
        stats = tracker.get_stats(days=1)
        assert stats["by_workload"]["unknown"]["count"] == 1
        assert (
            "challenges_ai" not in stats["by_workload"]
            or stats["by_workload"].get("challenges_ai", {}).get("count", 0) == 0
        )

    def test_prune_caps_events_per_key(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "app.utils.ai_workload_keys.RUNTIME_AI_METRICS_MAX_EVENTS_PER_KEY",
            4,
        )
        tracker = TokenTracker()
        for _ in range(6):
            tracker.track_usage("pattern", 10, 10, model="o3")
        assert len(tracker._usage_history["pattern"]) == 4

    def test_gpt54_pricing_uses_premium_rate(self):
        tracker = TokenTracker()

        usage = tracker.track_usage(
            "assistant_chat:premium",
            1000,
            1000,
            model="gpt-5.4",
        )

        assert usage["cost"] == pytest.approx(0.0175)

    def test_gpt5_mini_pricing_uses_public_chat_default_rate(self):
        tracker = TokenTracker()

        usage = tracker.track_usage(
            "assistant_chat:simple",
            1000,
            1000,
            model="gpt-5-mini",
        )

        assert usage["cost"] == pytest.approx(0.00225)


class TestGetStatsReadPathNoMutation:
    """Lecture filtrée ne doit pas créer de buckets vides (admin ai-stats)."""

    def test_unknown_challenge_type_does_not_create_usage_bucket(self):
        tracker = TokenTracker()
        stats = tracker.get_stats(challenge_type="totally_unknown_metric_key", days=1)
        assert stats["total_tokens"] == 0
        assert stats["count"] == 0
        assert "totally_unknown_metric_key" not in tracker._usage_history

    def test_many_unknown_challenge_types_do_not_grow_store(self):
        tracker = TokenTracker()
        for i in range(50):
            tracker.get_stats(challenge_type=f"unknown_probe_{i}", days=1)
        assert len(tracker._usage_history) == 0

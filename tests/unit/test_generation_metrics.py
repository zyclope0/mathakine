import pytest

from app.utils.generation_metrics import GenerationMetrics


class TestGenerationMetricsSummary:
    def test_summary_exposes_workload_and_error_breakdown(self):
        metrics = GenerationMetrics()
        metrics.record_generation(
            "assistant_chat:simple",
            success=False,
            validation_passed=False,
            duration_seconds=1.1,
            error_type="RateLimitError",
        )
        metrics.record_generation(
            "exercise_ai:addition",
            success=True,
            validation_passed=True,
            duration_seconds=2.0,
        )
        metrics.record_generation(
            "sequence",
            success=True,
            validation_passed=True,
            auto_corrected=True,
            duration_seconds=3.0,
        )

        summary = metrics.get_summary(days=1)

        assert "assistant_chat" in summary["by_workload"]
        assert "exercises_ai" in summary["by_workload"]
        assert "challenges_ai" in summary["by_workload"]
        assert summary["error_types"]["RateLimitError"] == 1
        assert "retention" in summary
        assert "metrics_disclaimer_fr" in summary

    def test_unknown_key_in_unknown_workload(self):
        metrics = GenerationMetrics()
        metrics.record_generation(
            "not_a_known_anything",
            success=True,
            validation_passed=True,
            duration_seconds=1.0,
        )
        summary = metrics.get_summary(days=1)
        assert "unknown" in summary["by_workload"]
        assert summary["by_workload"]["unknown"]["total_generations"] == 1

    def test_prune_caps_per_key(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "app.utils.ai_workload_keys.RUNTIME_AI_METRICS_MAX_EVENTS_PER_KEY",
            3,
        )
        metrics = GenerationMetrics()
        for _ in range(5):
            metrics.record_generation("riddle", success=True, validation_passed=True)
        assert len(metrics._generation_history["riddle"]) == 3

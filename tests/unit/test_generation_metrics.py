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
        assert summary.get("generation_status_counts") == {}

    def test_summary_generation_status_counts_global_and_by_type(self):
        metrics = GenerationMetrics()
        metrics.record_generation(
            "puzzle",
            success=True,
            validation_passed=True,
            auto_corrected=False,
            duration_seconds=1.0,
            generation_status="accepted",
        )
        metrics.record_generation(
            "puzzle",
            success=False,
            validation_passed=False,
            duration_seconds=0.5,
            error_type="x",
            generation_status="rejected",
        )
        metrics.record_generation(
            "exercise_ai:addition",
            success=True,
            validation_passed=True,
            duration_seconds=1.0,
        )

        summary = metrics.get_summary(days=1)
        assert summary["generation_status_counts"] == {"accepted": 1, "rejected": 1}
        by_type = summary["by_type"]
        assert "puzzle" in by_type
        assert by_type["puzzle"]["generation_status_counts"] == {
            "accepted": 1,
            "rejected": 1,
        }
        assert "total_generations" in by_type["puzzle"]
        assert "success_rate" in by_type["puzzle"]

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

    def test_error_code_counts_global_and_by_type(self):
        metrics = GenerationMetrics()
        metrics.record_generation(
            "puzzle",
            success=False,
            validation_passed=False,
            error_type="validation_failed",
            error_codes=["a", "b"],
        )
        metrics.record_generation(
            "riddle",
            success=True,
            validation_passed=True,
            duration_seconds=0.1,
        )
        s = metrics.get_summary(days=1)
        assert s["error_code_counts"] == {"a": 1, "b": 1}
        assert s["by_type"]["puzzle"]["error_code_counts"] == {"a": 1, "b": 1}
        assert s["by_type"]["riddle"]["error_code_counts"] == {}

    def test_latency_percentiles_in_summary(self):
        metrics = GenerationMetrics()
        # 10 records avec des durées connues pour valider P50/P95
        durations = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for d in durations:
            metrics.record_generation(
                "deduction",
                success=True,
                validation_passed=True,
                duration_seconds=d,
            )

        summary = metrics.get_summary(days=1)
        assert "latency" in summary
        latency = summary["latency"]
        assert "p50_ms" in latency
        assert "p95_ms" in latency
        # P50 sur 10 valeurs triées : interpolation entre index 4 et 5 (500ms et 600ms)
        assert 540.0 <= latency["p50_ms"] <= 560.0
        # P95 sur 10 valeurs : proche de 950ms
        assert 940.0 <= latency["p95_ms"] <= 960.0

    def test_latency_percentiles_empty(self):
        metrics = GenerationMetrics()
        summary = metrics.get_summary(days=1)
        assert summary["latency"] == {"p50_ms": 0.0, "p95_ms": 0.0}


class TestChessRepairMetrics:
    def test_chess_repair_counters_in_summary(self):
        metrics = GenerationMetrics()
        metrics.record_chess_repair(succeeded=True)
        metrics.record_chess_repair(succeeded=False)
        metrics.record_chess_repair(succeeded=True)

        summary = metrics.get_summary(days=1)
        assert "chess_repair" in summary
        cr = summary["chess_repair"]
        assert cr["chess_repair_attempted"] == 3
        assert cr["chess_repair_succeeded"] == 2
        assert cr["chess_repair_failed"] == 1

    def test_chess_repair_empty(self):
        metrics = GenerationMetrics()
        summary = metrics.get_summary(days=1)
        assert summary["chess_repair"] == {
            "chess_repair_attempted": 0,
            "chess_repair_succeeded": 0,
            "chess_repair_failed": 0,
        }

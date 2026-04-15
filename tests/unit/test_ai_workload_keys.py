"""Classification workloads IA (IA12) — fail-closed, pas d'attribution silencieuse aux défis."""

import app.utils.ai_workload_keys as ai_workload_keys
from app.utils.ai_workload_keys import (
    WORKLOAD_CHALLENGES_AI,
    WORKLOAD_EXERCISES_AI,
    WORKLOAD_UNKNOWN,
    classify_ai_workload_key,
    is_challenge_ai_metric_key,
    normalize_ai_metric_key,
    runtime_ai_metrics_retention_meta,
)


def test_normalize_strips_and_lowercases() -> None:
    assert normalize_ai_metric_key("  SEQUENCE ") == "sequence"


def test_classify_exercise_prefix() -> None:
    assert classify_ai_workload_key("exercise_ai:addition") == WORKLOAD_EXERCISES_AI


def test_classify_assistant_variants() -> None:
    assert classify_ai_workload_key("assistant_chat") == "assistant_chat"
    assert classify_ai_workload_key("assistant_chat:simple") == "assistant_chat"


def test_classify_known_challenge_type() -> None:
    assert classify_ai_workload_key("pattern") == WORKLOAD_CHALLENGES_AI
    assert classify_ai_workload_key("SEQUENCE") == WORKLOAD_CHALLENGES_AI


def test_classify_unknown_not_challenges_ai() -> None:
    assert classify_ai_workload_key("totally_unknown_metric") == WORKLOAD_UNKNOWN
    assert classify_ai_workload_key("logic_sequence") == WORKLOAD_UNKNOWN


def test_classify_unknown_logs_the_actual_metric_key(monkeypatch) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(
        ai_workload_keys.logger, "warning", lambda msg, *args: warnings.append(msg % args if args else msg)
    )

    assert classify_ai_workload_key("future_metric:key") == WORKLOAD_UNKNOWN
    assert warnings
    assert "future_metric:key" in warnings[0]


def test_empty_key_unknown() -> None:
    assert classify_ai_workload_key("") == WORKLOAD_UNKNOWN
    assert classify_ai_workload_key(None) == WORKLOAD_UNKNOWN


def test_is_challenge_ai_metric_key() -> None:
    assert is_challenge_ai_metric_key("chess") is True
    assert is_challenge_ai_metric_key("logic_sequence") is False


def test_retention_meta_shape() -> None:
    meta = runtime_ai_metrics_retention_meta()
    assert meta["max_age_days"] >= 1
    assert meta["max_events_per_key"] >= 1
    assert "disclaimer_fr" in meta

"""IA11a : campagne comparative offline (aucun live)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.evaluation import campaign_matrix as cm
from app.evaluation import comparative_campaign as comparative_mod
from app.evaluation.ai_generation_harness import run_offline_harness_report
from app.evaluation.comparative_campaign import (
    aggregate_decision_metrics,
    main,
    run_comparative_offline_campaign,
)
from app.evaluation.corpus_loader import default_corpus_path


def test_load_ia11a_campaign_matrix():
    p = cm.default_campaign_path("ia11a_offline_default")
    data = cm.load_campaign_matrix(p)
    assert data["offline_only"] is True
    assert data["campaign_id"] == "ia11a_offline_default"
    keys = {s["workload_key"] for s in data["segments"]}
    assert keys == {"simple_generator", "exercises_ai", "challenges_ai"}


def test_validate_rejects_non_offline_campaign():
    p = cm.default_campaign_path("ia11a_offline_default")
    raw = json.loads(p.read_text(encoding="utf-8"))
    raw["offline_only"] = False
    with pytest.raises(ValueError, match="offline_only"):
        cm._validate_campaign_matrix(raw)


def test_validate_rejects_executed_variant_status():
    p = cm.default_campaign_path("ia11a_offline_default")
    raw = json.loads(p.read_text(encoding="utf-8"))
    raw["segments"][1]["live_planned_variants"] = [
        {"variant_id": "bad", "status": "executed", "pipeline": "x"}
    ]
    with pytest.raises(ValueError, match="interdit"):
        cm._validate_campaign_matrix(raw)


def test_aggregate_decision_metrics_counts():
    results = [
        {
            "success": True,
            "structural_ok": True,
            "business_ok": True,
            "latency_ms": 10.0,
            "difficulty_flags": {},
            "choices_flags": {"a": 1},
        },
        {
            "success": False,
            "structural_ok": True,
            "business_ok": False,
            "latency_ms": 20.0,
        },
    ]
    m = aggregate_decision_metrics(results)
    assert m["cases_total"] == 2
    assert m["scenario_compliance_n"] == 1
    assert m["structural_ok_n"] == 2
    assert m["business_ok_n"] == 1
    assert m["median_latency_ms"] == 15.0
    assert m["cost_tokens_live"] == "non_disponible_offline"


def test_median_latency_empty_returns_none():
    assert comparative_mod._median([]) is None


def test_median_latency_odd_returns_central_value():
    assert comparative_mod._median([30.0, 10.0, 20.0]) == 20.0


def test_median_latency_even_returns_mean_of_two_central():
    assert comparative_mod._median([10.0, 20.0]) == 15.0
    assert comparative_mod._median([1.0, 2.0, 3.0, 4.0]) == 2.5


def test_aggregate_median_matches_manual_median_on_simple_harness():
    """Segment simple = 4 cas (pair) : médiane = moyenne des 2e et 3e latences triées."""
    r = run_offline_harness_report("simple", default_corpus_path())
    lats = sorted(
        float(x["latency_ms"]) for x in r.results if x.get("latency_ms") is not None
    )
    m = aggregate_decision_metrics(r.results)
    assert m["median_latency_ms"] == comparative_mod._median(lats)


def test_run_offline_harness_report_is_sync_subset():
    r = run_offline_harness_report("simple", default_corpus_path())
    assert r.mode == "offline"
    assert all(x["pipeline"] == "simple_generator" for x in r.results)


def test_comparative_campaign_never_calls_dispatch_live(tmp_path: Path):
    def _boom(*_a, **_k):
        raise AssertionError("dispatch_live ne doit pas etre appele en IA11a")

    with patch("app.evaluation.runners.dispatch_live", side_effect=_boom):
        payload, jpath, mpath, md = run_comparative_offline_campaign(
            campaign_id="ia11a_offline_default",
            corpus_path=None,
            output_dir=tmp_path,
        )
    assert payload["live_executed"] is False
    assert payload["offline_only"] is True
    assert len(payload["segments"]) == 3
    assert jpath.is_file() and mpath.is_file()
    assert "simple_generator" in md
    assert "planned_not_executed" in md


def test_main_writes_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("MATHAKINE_AI_EVAL_LIVE", raising=False)
    out = tmp_path / "cmp_out"
    code = main(
        [
            "--campaign",
            "ia11a_offline_default",
            "--output-dir",
            str(out),
        ]
    )
    assert list(out.glob("comparative_campaign_*.json"))
    assert list(out.glob("comparative_campaign_*.md"))
    assert code in (0, 1)


def test_run_offline_harness_matches_async_offline_branch():
    """Refactor IA11a : _run_async(offline) delegue a run_offline_harness_report."""
    import asyncio

    from app.evaluation import ai_generation_harness as mod

    corpus = default_corpus_path()
    sync_rep = run_offline_harness_report("simple", corpus)
    async_rep = asyncio.run(mod._run_async("offline", "simple", corpus))
    assert sync_rep.cases_total == async_rep.cases_total
    assert sync_rep.cases_passed == async_rep.cases_passed
    assert len(sync_rep.results) == len(async_rep.results)

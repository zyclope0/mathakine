"""IA11b : matrice live bornée + hybride (mock live, pas d’OpenAI en CI)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.evaluation import campaign_matrix as cm
from app.evaluation.comparative_campaign import (
    aggregate_decision_metrics,
    build_ia11b_recommendation_markdown,
    run_ia11b_bounded_live_campaign,
)
from app.evaluation.corpus_loader import default_corpus_path
from app.evaluation.schemas import CaseResult, HarnessReport


def test_load_ia11b_bounded_matrix():
    p = cm.default_ia11b_campaign_path("ia11b_live_bounded")
    data = cm.load_ia11b_bounded_campaign(p)
    assert data["offline_only"] is False
    assert data["base_offline_campaign_id"] == "ia11a_offline_default"
    assert len(data["live_executions"]) == 4


def test_ia11b_validate_rejects_more_than_two_per_workload():
    p = cm.default_ia11b_campaign_path("ia11b_live_bounded")
    raw = json.loads(p.read_text(encoding="utf-8"))
    raw["live_executions"].append(
        {
            "workload_key": "exercises_ai",
            "variant_id": "extra",
            "source_case_id": "live_openai_exercise_addition",
            "eval_model": "o3",
        }
    )
    with pytest.raises(ValueError, match="au plus 2"):
        cm._validate_ia11b_bounded_campaign(raw)


def test_aggregate_decision_metrics_live_shape():
    results = [
        {
            "success": True,
            "structural_ok": True,
            "business_ok": True,
            "latency_ms": 5.0,
            "tokens_prompt": 10,
            "tokens_completion": 20,
            "cost_usd_estimate": 0.001,
        }
    ]
    m = aggregate_decision_metrics(results, execution_mode="live")
    assert m["execution_mode"] == "live"
    assert isinstance(m["cost_tokens_live"], dict)
    assert m["cost_tokens_live"]["tokens_prompt_sum"] == 10


def _fake_live_harness(
    cases: list, *, corpus_path=None, report_target: str = ""
) -> HarnessReport:
    c = cases[0]
    res = CaseResult(
        case_id=c["id"],
        pipeline=str(c.get("pipeline", "")),
        success=True,
        latency_ms=7.0,
        structural_ok=True,
        business_ok=True,
        eval_model=c.get("eval_model"),
        expected_success=True,
    )
    return HarnessReport(
        mode="live",
        target=report_target,
        corpus_path=str(corpus_path or default_corpus_path()),
        corpus_version=1,
        cases_total=1,
        cases_run=1,
        cases_passed=1,
        cases_failed=0,
        cases_skipped=0,
        results=[res.to_dict()],
        summary_markdown="",
        token_tracker_snapshot={"mock": True},
        limitations_note="test",
    )


def test_run_ia11b_bounded_with_mocked_live(tmp_path: Path):
    with patch(
        "app.evaluation.comparative_campaign.run_live_harness_for_explicit_cases",
        side_effect=_fake_live_harness,
    ):
        payload, jpath, mpath, md = run_ia11b_bounded_live_campaign(
            ia11b_campaign_id="ia11b_live_bounded",
            corpus_path=None,
            output_dir=tmp_path,
        )
    assert payload["live_executed"] is True
    assert payload["ia11a_base_campaign_id"] == "ia11a_offline_default"
    assert jpath.is_file() and mpath.is_file()
    ex_seg = next(s for s in payload["segments"] if s["workload_key"] == "exercises_ai")
    assert len(ex_seg["live_executed_variants"]) == 2
    assert "Recommandation IA11b" in md
    rec = build_ia11b_recommendation_markdown(payload["segments"])
    assert "faible" in rec.lower()


@pytest.mark.asyncio
async def test_run_openai_exercise_stream_rejects_disallowed_eval_model():
    from app.evaluation import runners

    case = {
        "id": "t1",
        "pipeline": "openai_exercise_stream",
        "exercise_type": "addition",
        "age_group": "9-11",
        "prompt": "x",
        "expected_success": True,
    }
    r = await runners.run_openai_exercise_stream(
        case, model_override="modele_inconnu_allowlist_xyz"
    )
    assert r.success is False
    assert r.failure_reason and "eval_model_invalid" in r.failure_reason

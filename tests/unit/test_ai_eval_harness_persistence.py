"""Tests causaux — persistance DB du harness IA8 (opt-in, mapping structuré)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app.evaluation.reporting import build_markdown_summary
from app.evaluation.schemas import HarnessReport
from app.models.ai_eval_harness_run import AiEvalHarnessRun
from app.repositories.ai_eval_harness_repository import AiEvalHarnessRepository
from app.services.evaluation.ai_eval_harness_persistence_service import (
    AiEvalHarnessPersistenceService,
)


def test_persistence_service_maps_cases_and_snapshot(db_session):
    run_uuid = str(uuid.uuid4())
    report = HarnessReport(
        mode="offline",
        target="simple",
        corpus_path="/tmp/corpus.json",
        corpus_version=42,
        cases_total=1,
        cases_run=1,
        cases_passed=1,
        cases_failed=0,
        cases_skipped=0,
        results=[
            {
                "case_id": "c1",
                "pipeline": "simple_generator",
                "success": True,
                "expected_success": True,
                "failure_reason": None,
                "structural_ok": True,
                "business_ok": True,
                "latency_ms": 1.5,
                "structural_errors": [],
                "business_errors": [],
                "difficulty_flags": {},
                "choices_flags": {},
                "tokens_prompt": None,
                "tokens_completion": None,
                "cost_usd_estimate": None,
                "live_skipped": False,
                "skip_reason": None,
                "rationale": None,
                "pedagogical_note": None,
            }
        ],
        limitations_note="lim",
        run_uuid=run_uuid,
    )
    report.summary_markdown = build_markdown_summary(report)

    started = datetime(2026, 3, 22, 12, 0, tzinfo=timezone.utc)
    completed = datetime(2026, 3, 22, 12, 1, tzinfo=timezone.utc)

    svc = AiEvalHarnessPersistenceService(db_session)
    run = svc.persist_harness_run(
        report=report,
        run_uuid=run_uuid,
        json_artifact_path="/reports/a.json",
        markdown_artifact_path="/reports/a.md",
        started_at=started,
        completed_at=completed,
        git_revision="abc123",
        live_opt_in=False,
    )
    assert run.id is not None

    payload = svc.get_run_payload_by_uuid(run_uuid)
    assert payload is not None
    assert payload["run"]["run_uuid"] == run_uuid
    assert payload["run"]["json_artifact_path"] == "/reports/a.json"
    assert payload["run"]["cases_passed"] == 1
    assert len(payload["cases"]) == 1
    assert payload["cases"][0]["case_id"] == "c1"
    assert payload["cases"][0]["pipeline"] == "simple_generator"
    assert payload["cases"][0]["latency_ms"] == 1.5

    row = (
        db_session.query(AiEvalHarnessRun)
        .filter(AiEvalHarnessRun.run_uuid == run_uuid)
        .first()
    )
    assert row is not None
    snap = row.report_snapshot_json
    assert snap is not None
    assert snap["cases_run"] == report.cases_run
    assert snap["results"] == report.results

    db_session.delete(row)
    db_session.commit()


def test_repository_list_recent_includes_persisted_run(db_session):
    run_uuid = str(uuid.uuid4())
    report = HarnessReport(
        mode="offline",
        target="fixtures",
        corpus_path="/x",
        corpus_version=1,
        cases_total=0,
        cases_run=0,
        cases_passed=0,
        cases_failed=0,
        cases_skipped=0,
        results=[],
        limitations_note="",
        run_uuid=run_uuid,
    )
    now = datetime.now(timezone.utc)
    svc = AiEvalHarnessPersistenceService(db_session)
    svc.persist_harness_run(
        report=report,
        run_uuid=run_uuid,
        json_artifact_path=None,
        markdown_artifact_path=None,
        started_at=now,
        completed_at=now,
        git_revision=None,
        live_opt_in=False,
    )

    recent = AiEvalHarnessRepository.list_recent_runs(db_session, limit=5)
    uuids = {r.run_uuid for r in recent}
    assert run_uuid in uuids

    db_session.query(AiEvalHarnessRun).filter_by(run_uuid=run_uuid).delete()
    db_session.commit()


def test_main_without_persist_does_not_open_db_session(tmp_path):
    from app.evaluation import ai_generation_harness as mod

    out = tmp_path / "harness_out"
    with patch("app.db.base.SessionLocal") as m_sess:
        code = mod.main(
            [
                "--mode",
                "offline",
                "--target",
                "simple",
                "--output-dir",
                str(out),
            ]
        )
    m_sess.assert_not_called()
    assert code in (0, 1)


def test_main_with_persist_invokes_persist_seam(tmp_path, monkeypatch):
    """Le flag --persist doit appeler le seam de persistance (pas de SQL dans la CLI)."""
    from app.evaluation import ai_generation_harness as mod

    captured: list[dict] = []

    def _rec(**kwargs):
        captured.append(kwargs)

    monkeypatch.setattr(mod, "_persist_harness_report", _rec)
    out = tmp_path / "harness_out_p"
    code = mod.main(
        [
            "--mode",
            "offline",
            "--target",
            "simple",
            "--output-dir",
            str(out),
            "--persist",
        ]
    )
    assert len(captured) == 1
    assert captured[0]["report"].run_uuid
    assert captured[0]["json_artifact_path"]
    assert captured[0]["markdown_artifact_path"]
    assert code in (0, 1)

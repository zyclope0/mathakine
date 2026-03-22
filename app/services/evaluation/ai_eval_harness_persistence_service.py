"""
Persistance DB des rapports du harness IA — à partir du ``HarnessReport`` structuré.

Ne pas reparser Markdown/JSON fichiers : la vérité d'écriture est ``report.to_dict()``.

Lecture admin read-only des runs : ``GET /api/admin/ai-eval-harness-runs``
(``list_ai_eval_harness_runs_for_admin`` + :class:`AiEvalHarnessRepository`).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.evaluation.schemas import HarnessReport
from app.models.ai_eval_harness_run import AiEvalHarnessCaseResult, AiEvalHarnessRun
from app.repositories.ai_eval_harness_repository import AiEvalHarnessRepository


class AiEvalHarnessPersistenceService:
    """Orchestration persistance run + cas (délègue l'accès données au repository)."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = AiEvalHarnessRepository()

    def persist_harness_run(
        self,
        *,
        report: HarnessReport,
        run_uuid: str,
        json_artifact_path: Optional[str],
        markdown_artifact_path: Optional[str],
        started_at: datetime,
        completed_at: datetime,
        git_revision: Optional[str],
        live_opt_in: bool,
    ) -> AiEvalHarnessRun:
        snapshot = report.to_dict()
        run = AiEvalHarnessRun(
            run_uuid=run_uuid,
            mode=report.mode,
            target=report.target,
            corpus_path=report.corpus_path,
            corpus_version=report.corpus_version,
            started_at=started_at,
            completed_at=completed_at,
            cases_total=report.cases_total,
            cases_run=report.cases_run,
            cases_passed=report.cases_passed,
            cases_failed=report.cases_failed,
            cases_skipped=report.cases_skipped,
            limitations_note=report.limitations_note or "",
            json_artifact_path=json_artifact_path,
            markdown_artifact_path=markdown_artifact_path,
            token_tracker_snapshot=report.token_tracker_snapshot,
            report_snapshot_json=snapshot,
            git_revision=git_revision,
            app_version=settings.PROJECT_VERSION,
            live_opt_in=live_opt_in,
        )
        cases = self._build_case_rows(report.results)
        self._repo.insert_run_with_cases(self._db, run=run, cases=cases)
        self._db.commit()
        self._db.refresh(run)
        return run

    def _build_case_rows(
        self, results: List[Dict[str, Any]]
    ) -> List[AiEvalHarnessCaseResult]:
        rows: List[AiEvalHarnessCaseResult] = []
        for r in results:
            cost = r.get("cost_usd_estimate")
            dec_cost: Optional[Decimal] = None
            if cost is not None:
                try:
                    dec_cost = Decimal(str(cost))
                except Exception:
                    dec_cost = None
            rows.append(
                AiEvalHarnessCaseResult(
                    case_id=str(r.get("case_id", "")),
                    pipeline=str(r.get("pipeline", "")),
                    success=bool(r.get("success")),
                    expected_success=bool(r.get("expected_success", True)),
                    failure_reason=r.get("failure_reason"),
                    structural_ok=r.get("structural_ok"),
                    business_ok=r.get("business_ok"),
                    latency_ms=r.get("latency_ms"),
                    live_skipped=bool(r.get("live_skipped")),
                    skip_reason=r.get("skip_reason"),
                    tokens_prompt=r.get("tokens_prompt"),
                    tokens_completion=r.get("tokens_completion"),
                    cost_usd_estimate=dec_cost,
                    structural_errors=r.get("structural_errors") or [],
                    business_errors=r.get("business_errors") or [],
                    difficulty_flags=r.get("difficulty_flags") or {},
                    choices_flags=r.get("choices_flags") or {},
                    rationale=r.get("rationale"),
                    pedagogical_note=r.get("pedagogical_note"),
                )
            )
        return rows

    def get_run_payload_by_uuid(self, run_uuid: str) -> Optional[Dict[str, Any]]:
        run = self._repo.get_run_by_uuid(self._db, run_uuid)
        if run is None:
            return None
        cases = self._repo.list_case_results_for_run(self._db, run.id)
        return {
            "run": self._repo.run_to_summary_dict(run),
            "cases": [self._repo.case_to_dict(c) for c in cases],
        }

    def list_recent_run_summaries(self, *, limit: int = 20) -> List[Dict[str, Any]]:
        runs = self._repo.list_recent_runs(self._db, limit=limit)
        return [self._repo.run_to_summary_dict(r) for r in runs]

"""Accès données — runs et résultats par cas du harness d'évaluation IA."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy.orm import Session

from app.models.ai_eval_harness_run import AiEvalHarnessCaseResult, AiEvalHarnessRun


class AiEvalHarnessRepository:
    """Lecture / écriture des enregistrements de harness (pas de logique métier)."""

    @staticmethod
    def insert_run_with_cases(
        db: Session,
        *,
        run: AiEvalHarnessRun,
        cases: Sequence[AiEvalHarnessCaseResult],
    ) -> AiEvalHarnessRun:
        db.add(run)
        db.flush()
        for row in cases:
            row.run_id = run.id
            db.add(row)
        db.flush()
        return run

    @staticmethod
    def get_run_by_uuid(db: Session, run_uuid: str) -> Optional[AiEvalHarnessRun]:
        return (
            db.query(AiEvalHarnessRun)
            .filter(AiEvalHarnessRun.run_uuid == run_uuid)
            .first()
        )

    @staticmethod
    def list_case_results_for_run(
        db: Session, run_id: int
    ) -> List[AiEvalHarnessCaseResult]:
        return (
            db.query(AiEvalHarnessCaseResult)
            .filter(AiEvalHarnessCaseResult.run_id == run_id)
            .order_by(AiEvalHarnessCaseResult.id)
            .all()
        )

    @staticmethod
    def list_recent_runs(db: Session, *, limit: int = 20) -> List[AiEvalHarnessRun]:
        return (
            db.query(AiEvalHarnessRun)
            .order_by(AiEvalHarnessRun.completed_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def run_to_summary_dict(run: AiEvalHarnessRun) -> Dict[str, Any]:
        return {
            "id": run.id,
            "run_uuid": run.run_uuid,
            "mode": run.mode,
            "target": run.target,
            "corpus_path": run.corpus_path,
            "corpus_version": run.corpus_version,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "cases_total": run.cases_total,
            "cases_run": run.cases_run,
            "cases_passed": run.cases_passed,
            "cases_failed": run.cases_failed,
            "cases_skipped": run.cases_skipped,
            "limitations_note": run.limitations_note,
            "json_artifact_path": run.json_artifact_path,
            "markdown_artifact_path": run.markdown_artifact_path,
            "git_revision": run.git_revision,
            "app_version": run.app_version,
            "live_opt_in": run.live_opt_in,
            "created_at": run.created_at.isoformat() if run.created_at else None,
        }

    @staticmethod
    def case_to_dict(row: AiEvalHarnessCaseResult) -> Dict[str, Any]:
        cost = row.cost_usd_estimate
        return {
            "case_id": row.case_id,
            "pipeline": row.pipeline,
            "success": row.success,
            "expected_success": row.expected_success,
            "failure_reason": row.failure_reason,
            "structural_ok": row.structural_ok,
            "business_ok": row.business_ok,
            "latency_ms": row.latency_ms,
            "live_skipped": row.live_skipped,
            "skip_reason": row.skip_reason,
            "tokens_prompt": row.tokens_prompt,
            "tokens_completion": row.tokens_completion,
            "cost_usd_estimate": float(cost) if cost is not None else None,
            "structural_errors": row.structural_errors,
            "business_errors": row.business_errors,
            "difficulty_flags": row.difficulty_flags,
            "choices_flags": row.choices_flags,
            "rationale": row.rationale,
            "pedagogical_note": row.pedagogical_note,
        }

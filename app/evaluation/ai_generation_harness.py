"""
CLI / module d'orchestration du harness d'évaluation IA7.

Usage:
    python -m app.evaluation.ai_generation_harness --mode offline
    python -m app.evaluation.ai_generation_harness --mode live --target openai_exercises

Live : opt-in explicite ``MATHAKINE_AI_EVAL_LIVE=1`` **ou** ``--live`` (voir doc).

Persistance DB (IA8) : opt-in ``--persist`` après écriture des artefacts JSON/MD.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.evaluation.corpus_loader import default_corpus_path, iter_cases, load_corpus
from app.evaluation.reporting import (
    aggregate_from_results,
    build_markdown_summary,
    write_report,
)
from app.evaluation.runners import dispatch_live, dispatch_offline
from app.evaluation.schemas import CaseResult, HarnessReport


def _configure_stdout_utf8() -> None:
    """Évite UnicodeEncodeError sur consoles Windows (cp1252) pour les JSON harness."""
    reconf = getattr(sys.stdout, "reconfigure", None)
    if callable(reconf):
        try:
            reconf(encoding="utf-8")
        except Exception:
            pass


def _print_json(obj: Any) -> None:
    _configure_stdout_utf8()
    try:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    except UnicodeEncodeError:
        print(json.dumps(obj, ensure_ascii=True, indent=2))


LIMITATIONS = (
    "Ce harness mesure la conformité aux validateurs et heuristiques déjà codés en backend, "
    "plus latence (et agrégats token_tracker en live). "
    "Il ne mesure pas la qualité pédagogique réelle, ni l'alignement curriculum, "
    "ni l'absence de biais. "
    "Un score « OK » peut masquer un énoncé ambigu ou inadapté à l'âge."
)


def run_offline_harness_report(
    target: str,
    corpus_path: Optional[Path] = None,
) -> HarnessReport:
    """
    Exécute le harness **uniquement** en offline (aucun ``dispatch_live``).

    Réutilisé par la campagne comparative IA11a et par ``_run_async`` (mode offline).
    """
    corpus = corpus_path or default_corpus_path()
    data = load_corpus(corpus)
    version = int(data.get("version", 0))
    cases = iter_cases(data, target=target, mode="offline")
    results: List[CaseResult] = [dispatch_offline(c) for c in cases]
    n, passed, failed, skipped = aggregate_from_results(results)
    report = HarnessReport(
        mode="offline",
        target=target,
        corpus_path=str(corpus),
        corpus_version=version,
        cases_total=len(cases),
        cases_run=n,
        cases_passed=passed,
        cases_failed=failed,
        cases_skipped=skipped,
        results=[r.to_dict() for r in results],
        summary_markdown="",
        token_tracker_snapshot=None,
        limitations_note=LIMITATIONS,
    )
    report.summary_markdown = build_markdown_summary(report)
    return report


def harness_live_opt_in_allowed(*, live_cli_flag: bool = False) -> bool:
    """Opt-in explicite pour appels OpenAI réels (env ou flag CLI)."""
    env = os.environ.get("MATHAKINE_AI_EVAL_LIVE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    return env or bool(live_cli_flag)


def _live_allowed(args: argparse.Namespace) -> bool:
    return harness_live_opt_in_allowed(live_cli_flag=bool(getattr(args, "live", False)))


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _try_git_revision() -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=_repo_root(),
            stderr=subprocess.DEVNULL,
            timeout=3,
        )
        return out.decode().strip()[:64] or None
    except Exception:
        return None


def _persist_harness_report(
    *,
    report: HarnessReport,
    json_artifact_path: str,
    markdown_artifact_path: str,
    started_at: datetime,
    completed_at: datetime,
    live_opt_in: bool,
) -> None:
    from app.db.base import SessionLocal
    from app.services.evaluation.ai_eval_harness_persistence_service import (
        AiEvalHarnessPersistenceService,
    )

    run_uuid = report.run_uuid
    if not run_uuid:
        raise ValueError("run_uuid manquant : doit être défini avant persistance")

    git_revision = _try_git_revision()
    db = SessionLocal()
    try:
        svc = AiEvalHarnessPersistenceService(db)
        svc.persist_harness_run(
            report=report,
            run_uuid=run_uuid,
            json_artifact_path=json_artifact_path,
            markdown_artifact_path=markdown_artifact_path,
            started_at=started_at,
            completed_at=completed_at,
            git_revision=git_revision,
            live_opt_in=live_opt_in,
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _show_persisted_run(run_uuid: str) -> int:
    from app.db.base import SessionLocal
    from app.services.evaluation.ai_eval_harness_persistence_service import (
        AiEvalHarnessPersistenceService,
    )

    db = SessionLocal()
    try:
        svc = AiEvalHarnessPersistenceService(db)
        payload = svc.get_run_payload_by_uuid(run_uuid)
        if payload is None:
            print(f"Aucun run trouvé pour run_uuid={run_uuid}", file=sys.stderr)
            return 4
        _print_json(payload)
        return 0
    finally:
        db.close()


def _list_persisted_runs(limit: int) -> int:
    from app.db.base import SessionLocal
    from app.services.evaluation.ai_eval_harness_persistence_service import (
        AiEvalHarnessPersistenceService,
    )

    db = SessionLocal()
    try:
        svc = AiEvalHarnessPersistenceService(db)
        rows = svc.list_recent_run_summaries(limit=limit)
        _print_json(rows)
        return 0
    finally:
        db.close()


def run_live_harness_for_explicit_cases(
    cases: List[Dict[str, Any]],
    *,
    corpus_path: Optional[Path] = None,
    report_target: str = "bounded_live",
) -> HarnessReport:
    """
    Exécute ``dispatch_live`` sur une liste de cas **déjà enrichis** (ex. ``eval_model``).

    Utilisé par IA11b pour un passage unique par variante sans élargir le corpus.
    """
    corpus = corpus_path or default_corpus_path()
    data = load_corpus(corpus)
    version = int(data.get("version", 0))

    async def _run() -> List[CaseResult]:
        out: List[CaseResult] = []
        for c in cases:
            out.append(await dispatch_live(c))
        return out

    results = asyncio.run(_run())
    n, passed, failed, skipped = aggregate_from_results(results)
    token_snap: Dict[str, Any] | None = None
    try:
        from app.utils.token_tracker import token_tracker

        token_snap = token_tracker.get_stats(days=1)
    except Exception as e:
        token_snap = {"error": str(e)}

    report = HarnessReport(
        mode="live",
        target=report_target,
        corpus_path=str(corpus),
        corpus_version=version,
        cases_total=len(cases),
        cases_run=n,
        cases_passed=passed,
        cases_failed=failed,
        cases_skipped=skipped,
        results=[r.to_dict() for r in results],
        summary_markdown="",
        token_tracker_snapshot=token_snap,
        limitations_note=LIMITATIONS,
    )
    report.summary_markdown = build_markdown_summary(report)
    return report


async def _run_async(
    mode: str,
    target: str,
    corpus_path: Path,
) -> HarnessReport:
    if mode == "offline":
        return run_offline_harness_report(target, corpus_path)

    data = load_corpus(corpus_path)
    version = int(data.get("version", 0))
    cases = iter_cases(data, target=target, mode=mode)
    results: List[CaseResult] = []
    for case in cases:
        results.append(await dispatch_live(case))

    n, passed, failed, skipped = aggregate_from_results(results)
    token_snap: Dict[str, Any] | None = None
    try:
        from app.utils.token_tracker import token_tracker

        token_snap = token_tracker.get_stats(days=1)
    except Exception as e:
        token_snap = {"error": str(e)}

    report = HarnessReport(
        mode=mode,
        target=target,
        corpus_path=str(corpus_path),
        corpus_version=version,
        cases_total=len(cases),
        cases_run=n,
        cases_passed=passed,
        cases_failed=failed,
        cases_skipped=skipped,
        results=[r.to_dict() for r in results],
        summary_markdown="",
        token_tracker_snapshot=token_snap,
        limitations_note=LIMITATIONS,
    )
    report.summary_markdown = build_markdown_summary(report)
    return report


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Harness d'évaluation génération IA")
    parser.add_argument(
        "--mode",
        choices=("offline", "live"),
        default="offline",
        help="offline = CI sans réseau ; live = appels modèles réels (opt-in)",
    )
    parser.add_argument(
        "--target",
        default="all",
        choices=(
            "all",
            "simple",
            "template_exercises",
            "fixtures",
            "openai_exercises",
            "openai_challenges",
            "exercises_ai",
            "challenges_ai",
        ),
        help="Sous-ensemble du corpus",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=None,
        help="Chemin vers corpus.json (défaut: tests/fixtures/ai_eval/corpus.json)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/ai_eval"),
        help="Dossier pour JSON + Markdown",
    )
    parser.add_argument(
        "--stdout-json",
        action="store_true",
        help="Imprime le rapport JSON sur stdout",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Autorise le mode live (avec clé OpenAI). Peut être combiné à MATHAKINE_AI_EVAL_LIVE=1.",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Après les rapports fichiers, enregistre le run et les cas en base (opt-in).",
    )
    parser.add_argument(
        "--show-run",
        metavar="UUID",
        default=None,
        help="Affiche un run persisté (JSON) et quitte sans exécuter le harness.",
    )
    parser.add_argument(
        "--list-persisted",
        action="store_true",
        help="Liste les derniers runs persistés (JSON) et quitte.",
    )
    parser.add_argument(
        "--list-limit",
        type=int,
        default=20,
        help="Avec --list-persisted : nombre max de runs (défaut 20).",
    )
    args = parser.parse_args(argv)

    if args.show_run:
        return _show_persisted_run(args.show_run)
    if args.list_persisted:
        return _list_persisted_runs(args.list_limit)

    if args.mode == "live":
        if not _live_allowed(args):
            print(
                "ERREUR: mode live refusé. Définir MATHAKINE_AI_EVAL_LIVE=1 "
                "ou passer --live explicitement.",
                file=sys.stderr,
            )
            return 2

    corpus = args.corpus or default_corpus_path()
    started_at = datetime.now(timezone.utc)
    report = asyncio.run(_run_async(args.mode, args.target, corpus))
    completed_at = datetime.now(timezone.utc)

    if args.persist:
        report.run_uuid = str(uuid.uuid4())

    if args.stdout_json:
        _print_json(report.to_dict())

    jpath, mpath = write_report(report, args.output_dir)
    print(f"Rapport JSON : {jpath}")
    print(f"Rapport MD   : {mpath}")
    print()
    print(report.summary_markdown)

    if args.persist:
        try:
            _persist_harness_report(
                report=report,
                json_artifact_path=str(jpath),
                markdown_artifact_path=str(mpath),
                started_at=started_at,
                completed_at=completed_at,
                live_opt_in=args.mode == "live",
            )
            print()
            print(f"Persistance DB OK — run_uuid={report.run_uuid}")
        except Exception as e:
            print(f"ERREUR persistance DB: {e}", file=sys.stderr)
            return 3

    def _case_considered_ok(res: Dict[str, Any]) -> bool:
        # ``success`` encode déjà l'adéquation au scénario (positif = validateurs OK ;
        # négatif ``expected_success: false`` = succès si rejet observé).
        if res.get("success"):
            return True
        # Hors ligne : pipelines live-only marqués skipped, pas une défaillance.
        if res.get("live_skipped"):
            return True
        return False

    return 0 if all(_case_considered_ok(r) for r in report.results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

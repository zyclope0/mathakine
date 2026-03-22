"""Rapport JSON + résumé Markdown."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.evaluation.schemas import CaseResult, HarnessReport


def build_markdown_summary(report: HarnessReport) -> str:
    lines: List[str] = []
    lines.append(f"# AI generation harness — {report.mode}")
    lines.append("")
    lines.append(f"- **Corpus** : `{report.corpus_path}` (v{report.corpus_version})")
    lines.append(f"- **Cible** : `{report.target}`")
    lines.append(
        f"- **Cas** : {report.cases_run} exécutés, "
        f"{report.cases_passed} OK, {report.cases_failed} échecs, "
        f"{report.cases_skipped} ignorés"
    )
    lines.append("")
    by_pipe: Dict[str, List[bool]] = defaultdict(list)
    lat_by_pipe: Dict[str, List[float]] = defaultdict(list)
    for r in report.results:
        p = str(r.get("pipeline", "?"))
        by_pipe[p].append(bool(r.get("success")))
        if r.get("latency_ms") is not None:
            lat_by_pipe[p].append(float(r["latency_ms"]))
    lines.append("## Synthèse par pipeline")
    lines.append("")
    lines.append("| pipeline | pass | fail | latence médiane (ms) |")
    lines.append("|----------|------|------|----------------------|")
    for pipe, oks in sorted(by_pipe.items()):
        n = len(oks)
        passed = sum(1 for x in oks if x)
        fails = n - passed
        med = ""
        if lat_by_pipe.get(pipe):
            xs = sorted(lat_by_pipe[pipe])
            med = f"{xs[len(xs) // 2]:.1f}"
        lines.append(f"| {pipe} | {passed} | {fails} | {med} |")
    lines.append("")
    lines.append("## Détail des échecs")
    lines.append("")
    for r in report.results:
        if r.get("success"):
            continue
        if r.get("live_skipped"):
            lines.append(f"- `{r.get('case_id')}` — ignoré ({r.get('skip_reason')})")
            continue
        lines.append(
            f"- `{r.get('case_id')}` ({r.get('pipeline')}) — {r.get('failure_reason')}"
        )
    lines.append("")
    lines.append("## Limites")
    lines.append("")
    lines.append(report.limitations_note)
    return "\n".join(lines)


def write_report(
    report: HarnessReport,
    output_dir: Path,
) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jpath = output_dir / f"harness_report_{report.mode}_{ts}.json"
    mpath = output_dir / f"harness_report_{report.mode}_{ts}.md"
    with jpath.open("w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
    with mpath.open("w", encoding="utf-8") as f:
        f.write(report.summary_markdown)
    return jpath, mpath


def aggregate_from_results(results: List[CaseResult]) -> tuple[int, int, int, int]:
    passed = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success and not r.live_skipped)
    skipped = sum(1 for r in results if r.live_skipped)
    return len(results), passed, failed, skipped

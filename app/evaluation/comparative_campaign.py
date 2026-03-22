"""
Campagne comparative IA11a (offline) et IA11b (hybride offline IA11a + live borné).

IA11a :
    python -m app.evaluation.comparative_campaign --campaign ia11a_offline_default

IA11b (opt-in live explicite, réutilise la matrice offline IA11a comme base) :
    python -m app.evaluation.comparative_campaign --ia11b-bounded-live --live \\
        --ia11b-campaign ia11b_live_bounded

Garanties IA11a :
    - aucun ``dispatch_live`` ni appel OpenAI ;
    - ``MATHAKINE_AI_EVAL_LIVE`` est ignoré (rappel stderr).

Les sorties sont des agrégats **par workload / variante** sans score global opaque.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.evaluation.ai_generation_harness import (
    harness_live_opt_in_allowed,
    run_live_harness_for_explicit_cases,
    run_offline_harness_report,
)
from app.evaluation.campaign_matrix import (
    CampaignSegmentSpec,
    default_campaign_path,
    default_ia11b_campaign_path,
    load_campaign_matrix,
    load_ia11b_bounded_campaign,
)
from app.evaluation.corpus_loader import default_corpus_path, load_corpus


def _median(xs: List[float]) -> float | None:
    """Médiane : élément central (impair) ou moyenne des deux centraux (pair)."""
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2.0


def aggregate_decision_metrics(
    results: List[Dict[str, Any]],
    *,
    execution_mode: str = "offline",
    token_tracker_isolation_note: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Métriques de décision explicites (pas de score composite).

    - scenario_compliance : aligné sur ``success`` (conformité au scénario attend_success du corpus).
    - structural_ok / business_ok : taux sur les cas où le champ est renseigné (non null).
    """
    n = len(results)
    scenario_ok = sum(1 for r in results if r.get("success"))
    skipped = sum(1 for r in results if r.get("live_skipped"))
    st_elig = [r for r in results if r.get("structural_ok") is not None]
    st_ok = sum(1 for r in st_elig if r.get("structural_ok"))
    biz_elig = [r for r in results if r.get("business_ok") is not None]
    biz_ok = sum(1 for r in biz_elig if r.get("business_ok"))
    lats = [float(r["latency_ms"]) for r in results if r.get("latency_ms") is not None]
    flags_n = sum(
        1
        for r in results
        if (r.get("difficulty_flags") or {}) or (r.get("choices_flags") or {})
    )
    row: Dict[str, Any] = {
        "execution_mode": execution_mode,
        "cases_total": n,
        "scenario_compliance_n": scenario_ok,
        "scenario_compliance_rate": (scenario_ok / n) if n else 0.0,
        "live_skipped_n": skipped,
        "structural_ok_n": st_ok,
        "structural_eligible_n": len(st_elig),
        "structural_pass_rate": (st_ok / len(st_elig)) if st_elig else None,
        "business_ok_n": biz_ok,
        "business_eligible_n": len(biz_elig),
        "business_pass_rate": (biz_ok / len(biz_elig)) if biz_elig else None,
        "median_latency_ms": _median(lats),
        "cases_with_heuristic_flags_n": flags_n,
    }
    if execution_mode == "offline":
        row["cost_tokens_live"] = "non_disponible_offline"
        row["notes"] = (
            "Les taux ne sont pas comparables entre workloads (pipelines différents). "
            "Pas de coût/tokens API sans exécution live (IA11b)."
        )
    else:
        tp_vals = [
            int(r["tokens_prompt"])
            for r in results
            if r.get("tokens_prompt") is not None
        ]
        tc_vals = [
            int(r["tokens_completion"])
            for r in results
            if r.get("tokens_completion") is not None
        ]
        cost_vals = [
            float(r["cost_usd_estimate"])
            for r in results
            if r.get("cost_usd_estimate") is not None
        ]
        tok_n = 0
        if tp_vals or tc_vals or cost_vals:
            tok_n = max(len(tp_vals), len(tc_vals), len(cost_vals))
        row["cost_tokens_live"] = {
            "tokens_prompt_sum": sum(tp_vals) if tp_vals else None,
            "tokens_completion_sum": sum(tc_vals) if tc_vals else None,
            "cost_usd_estimate_sum": sum(cost_vals) if cost_vals else None,
            "cases_with_token_fields_n": tok_n,
        }
        row["notes"] = token_tracker_isolation_note or (
            "Les champs tokens par cas peuvent être absents selon le pipeline ; "
            "le token_tracker reste un agrégat processus, non isolé par variante."
        )
    return row


def _pipeline_breakdown(results: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    by_pipe: Dict[str, Dict[str, int]] = {}
    for r in results:
        p = str(r.get("pipeline", "?"))
        bucket = by_pipe.setdefault(p, {"pass": 0, "fail": 0, "skipped": 0})
        if r.get("live_skipped"):
            bucket["skipped"] += 1
        elif r.get("success"):
            bucket["pass"] += 1
        else:
            bucket["fail"] += 1
    return by_pipe


def build_comparative_markdown(
    campaign: Dict[str, Any],
    segments_payload: List[Dict[str, Any]],
) -> str:
    lines: List[str] = []
    lines.append(f"# {campaign.get('title', 'Campagne comparative')}")
    lines.append("")
    lines.append(
        f"- **Campagne** : `{campaign.get('campaign_id')}` (v{campaign.get('version')})"
    )
    lines.append("- **Exécution** : offline uniquement — **aucun live OpenAI**")
    lines.append(f"- **Avertissement** : {campaign.get('honesty_disclaimer', '')}")
    lines.append("")
    lines.append("## Non mesurable en offline")
    for x in campaign.get("non_measurable_offline") or []:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Tableau comparatif par workload (agrégats)")
    lines.append("")
    lines.append(
        "| workload | cible harness | cas | scénario OK | struct. OK | métier OK | latence méd. (ms) |"
    )
    lines.append(
        "|----------|---------------|-----|-------------|------------|-----------|-------------------|"
    )
    for sp in segments_payload:
        m = sp["decision_metrics"]
        lat = (
            f"{m['median_latency_ms']:.4f}"
            if m["median_latency_ms"] is not None
            else "—"
        )
        lines.append(
            f"| {sp['workload_key']} | `{sp['harness_target']}` | {m['cases_total']} | "
            f"{m['scenario_compliance_n']}/{m['cases_total']} | "
            f"{m['structural_ok_n']}/{m['structural_eligible_n'] or '—'} | "
            f"{m['business_ok_n']}/{m['business_eligible_n'] or '—'} | {lat} |"
        )
    lines.append("")
    lines.append("## Variantes live planifiées (non exécutées)")
    for sp in segments_payload:
        vars_ = sp.get("live_planned_variants") or []
        if not vars_:
            continue
        lines.append(f"### {sp['workload_key']}")
        for v in vars_:
            lines.append(
                f"- **{v.get('variant_id')}** — `{v.get('status')}` — "
                f"{v.get('execution_gate', '')}"
            )
        lines.append("")
    lines.append("## Prérequis IA11b")
    for p in campaign.get("ia11b_prerequisites") or []:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("## Limites harness (rappel)")
    lines.append("")
    lines.append(
        segments_payload[0]["harness_report"].get("limitations_note", "")
        if segments_payload
        else ""
    )
    return "\n".join(lines).strip() + "\n"


_WORKLOAD_EXPECTED_LIVE_PIPE: Dict[str, str] = {
    "exercises_ai": "openai_exercise_stream",
    "challenges_ai": "openai_challenge_stream",
}


def build_offline_comparative_segments(
    campaign: Dict[str, Any],
    corpus_path: Path | None,
) -> Tuple[List[Dict[str, Any]], str]:
    """Construit les segments offline (réutilisé par IA11a et la base offline d’IA11b)."""
    segments_out: List[Dict[str, Any]] = []
    for seg in campaign["segments"]:
        spec = CampaignSegmentSpec.from_dict(seg)
        report = run_offline_harness_report(spec.harness_target, corpus_path)
        rd = report.to_dict()
        metrics = aggregate_decision_metrics(rd["results"])
        segments_out.append(
            {
                "workload_key": spec.workload_key,
                "harness_target": spec.harness_target,
                "description": spec.description,
                "offline_comparison_axes": spec.offline_comparison_axes,
                "live_planned_variants": spec.live_planned_variants,
                "decision_metrics": metrics,
                "pipeline_breakdown": _pipeline_breakdown(rd["results"]),
                "harness_report": rd,
            }
        )
    resolved_corpus = (
        str(corpus_path)
        if corpus_path
        else (
            segments_out[0]["harness_report"]["corpus_path"]
            if segments_out
            else "default"
        )
    )
    return segments_out, resolved_corpus


def build_ia11b_recommendation_markdown(segments_payload: List[Dict[str, Any]]) -> str:
    """
    Recommandation **documentaire** (pas de switch runtime).

    Confiance explicite : n=1 par variante live → faible.
    """
    lines: List[str] = [
        "## Recommandation IA11b (documentaire)",
        "",
        "**Niveau de confiance** : *faible* — un seul cas live par variante sur le corpus borné ; "
        "ne pas extrapoler à la qualité pédagogique globale.",
        "",
    ]
    for seg in segments_payload:
        lv = seg.get("live_executed_variants") or []
        if not lv:
            continue
        wl = seg["workload_key"]
        lines.append(f"### Workload `{wl}`")
        baseline = next(
            (x for x in lv if "o3_baseline" in str(x.get("variant_id", ""))), None
        )
        cand = next(
            (
                x
                for x in lv
                if "candidate" in str(x.get("variant_id", ""))
                or "gpt4o_mini" in str(x.get("variant_id", ""))
            ),
            None,
        )
        for v in lv:
            results = v.get("harness_report", {}).get("results") or []
            r0: Dict[str, Any] = results[0] if results else {}
            scen = "OK" if r0.get("success") else "FAIL"
            lines.append(
                f"- **`{v.get('variant_id')}`** (`{v.get('eval_model')}`) : "
                f"scénario={scen} ; struct={r0.get('structural_ok')} ; "
                f"métier={r0.get('business_ok')} ; lat_ms={r0.get('latency_ms')}"
            )
        if baseline and cand:
            br = (baseline.get("harness_report", {}).get("results") or [{}])[0]
            cr = (cand.get("harness_report", {}).get("results") or [{}])[0]
            b_ok, c_ok = bool(br.get("success")), bool(cr.get("success"))
            if b_ok and not c_ok:
                lines.append(
                    "- **Recommandation** : conserver **o3** sur ce workload pour l’instant "
                    "(candidat en échec sur le cas borné)."
                )
            elif b_ok and c_ok:
                lines.append(
                    "- **Recommandation** : les deux passent le cas unique ; **signal insuffisant** "
                    "pour changer de modèle (comparer latence/tokens si présents, sans sur-interpréter)."
                )
            else:
                lines.append(
                    "- **Recommandation** : baseline en échec — corriger infra / prompt / cas "
                    "avant toute lecture « candidat vs baseline »."
                )
        elif baseline:
            lines.append(
                "- **Recommandation** : seule une variante baseline live est documentée ; "
                "pas de comparaison candidat sur ce workload."
            )
        lines.append("")
    lines.append("### Hors scope (rappel)")
    lines.extend(
        [
            "- `assistant_chat` hors cadre ; défauts produit inchangés ; pas de décision runtime implicite.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def build_ia11b_hybrid_markdown(
    ia11b: Dict[str, Any],
    ia11a: Dict[str, Any],
    segments_payload: List[Dict[str, Any]],
    recommendation_md: str,
) -> str:
    """Markdown humain : offline (IA11a) + exécutions live distinguées + recommandation."""
    lines: List[str] = []
    lines.append(f"# {ia11b.get('title', 'IA11b — campagne hybride')}")
    lines.append("")
    lines.append(
        f"- **Campagne IA11b** : `{ia11b.get('campaign_id')}` (v{ia11b.get('version')})"
    )
    lines.append(
        f"- **Base offline** : `{ia11a.get('campaign_id')}` (segments identiques à IA11a)"
    )
    lines.append(
        "- **Live** : exécuté sous opt-in explicite (`--live` ou `MATHAKINE_AI_EVAL_LIVE=1`)"
    )
    lines.append(f"- **Avertissement** : {ia11b.get('honesty_disclaimer', '')}")
    lines.append("")
    lines.append("## Tableau comparatif offline (référence IA11a)")
    lines.append("")
    lines.append(
        "| workload | cible harness | cas | scénario OK | struct. OK | métier OK | latence méd. (ms) |"
    )
    lines.append(
        "|----------|---------------|-----|-------------|------------|-----------|-------------------|"
    )
    for sp in segments_payload:
        m = sp["decision_metrics"]
        if m.get("execution_mode", "offline") != "offline":
            continue
        lat = (
            f"{m['median_latency_ms']:.4f}"
            if m["median_latency_ms"] is not None
            else "—"
        )
        lines.append(
            f"| {sp['workload_key']} | `{sp['harness_target']}` | {m['cases_total']} | "
            f"{m['scenario_compliance_n']}/{m['cases_total']} | "
            f"{m['structural_ok_n']}/{m['structural_eligible_n'] or '—'} | "
            f"{m['business_ok_n']}/{m['business_eligible_n'] or '—'} | {lat} |"
        )
    lines.append("")
    lines.append("## Exécutions live bornées (par variante)")
    lines.append("")
    lines.append(
        "| workload | variante | eval_model | scénario OK | struct. | métier | lat_ms | tokens (p/c) |"
    )
    lines.append(
        "|----------|----------|------------|-------------|---------|--------|--------|--------------|"
    )
    for sp in segments_payload:
        for v in sp.get("live_executed_variants") or []:
            r0 = (v.get("harness_report", {}).get("results") or [{}])[0]
            tp, tc = r0.get("tokens_prompt"), r0.get("tokens_completion")
            tok = "—" if tp is None and tc is None else f"{tp or 0}/{tc or 0}"
            scen = "oui" if r0.get("success") else "non"
            lines.append(
                f"| {sp['workload_key']} | `{v.get('variant_id')}` | `{v.get('eval_model')}` | "
                f"{scen} | {r0.get('structural_ok')} | {r0.get('business_ok')} | "
                f"{r0.get('latency_ms')} | {tok} |"
            )
    lines.append("")
    lines.append("## Non mesurable en offline (rappel IA11a)")
    for x in ia11a.get("non_measurable_offline") or []:
        lines.append(f"- {x}")
    lines.append("")
    lines.append(recommendation_md.strip())
    lines.append("")
    lines.append("## Limites harness (rappel)")
    lines.append("")
    lines.append(
        segments_payload[0]["harness_report"].get("limitations_note", "")
        if segments_payload
        else ""
    )
    return "\n".join(lines).strip() + "\n"


def run_ia11b_bounded_live_campaign(
    *,
    ia11b_campaign_id: str,
    corpus_path: Path | None,
    output_dir: Path,
) -> Tuple[Dict[str, Any], Path, Path, str]:
    """
    IA11b : segments offline = matrice IA11a ; live = lignes explicites de la matrice IA11b.
    """
    ib_path = default_ia11b_campaign_path(ia11b_campaign_id)
    ia11b = load_ia11b_bounded_campaign(ib_path)
    base_id = str(ia11b["base_offline_campaign_id"])
    base_path = default_campaign_path(base_id)
    ia11a = load_campaign_matrix(base_path)

    cpath_resolved = corpus_path or default_corpus_path()
    segments_out, _ = build_offline_comparative_segments(ia11a, corpus_path)

    data = load_corpus(cpath_resolved)
    case_by_id = {str(c["id"]): c for c in (data.get("cases") or [])}

    execs_by_wl: Dict[str, List[Dict[str, Any]]] = {}
    for row in ia11b["live_executions"]:
        execs_by_wl.setdefault(str(row["workload_key"]), []).append(row)

    iso_note = "token_tracker agrège les appels du processus Python ; non attribuable proprement à une variante."
    for seg in segments_out:
        wl = str(seg["workload_key"])
        lives = execs_by_wl.get(wl) or []
        live_variants_out: List[Dict[str, Any]] = []
        for row in lives:
            sid = str(row["source_case_id"])
            variant_id = str(row["variant_id"])
            em = str(row["eval_model"])
            src = case_by_id.get(sid)
            if not src:
                raise ValueError(f"Cas corpus introuvable pour IA11b: {sid}")
            pipe = str(src.get("pipeline", ""))
            exp_pipe = _WORKLOAD_EXPECTED_LIVE_PIPE.get(wl)
            if exp_pipe and pipe != exp_pipe:
                raise ValueError(
                    f"Incohérence IA11b : workload {wl!r} attend pipeline {exp_pipe!r} "
                    f"pour le cas {sid!r}, trouvé {pipe!r}"
                )
            case_run = copy.deepcopy(src)
            case_run["id"] = f"{sid}__{variant_id}"
            case_run["eval_model"] = em
            prev_r = str(case_run.get("rationale") or "")
            case_run["rationale"] = (
                f"{prev_r} [IA11b variant={variant_id} eval_model={em}]".strip()
            )
            rep = run_live_harness_for_explicit_cases(
                [case_run],
                corpus_path=cpath_resolved,
                report_target=f"{wl}__{variant_id}",
            )
            rd = rep.to_dict()
            metrics = aggregate_decision_metrics(
                rd["results"],
                execution_mode="live",
                token_tracker_isolation_note=iso_note,
            )
            live_variants_out.append(
                {
                    "variant_id": variant_id,
                    "source_case_id": sid,
                    "eval_model": em,
                    "execution_mode": "live",
                    "decision_metrics": metrics,
                    "pipeline_breakdown": _pipeline_breakdown(rd["results"]),
                    "harness_report": rd,
                }
            )
        seg["live_executed_variants"] = live_variants_out

    token_snap_global: Dict[str, Any]
    try:
        from app.utils.token_tracker import token_tracker

        token_snap_global = token_tracker.get_stats(days=1)
    except Exception as e:
        token_snap_global = {"error": str(e)}

    rec_md = build_ia11b_recommendation_markdown(segments_out)
    md = build_ia11b_hybrid_markdown(ia11b, ia11a, segments_out, rec_md)

    payload: Dict[str, Any] = {
        "schema": "mathakine.ai_eval.comparative_campaign.v1",
        "campaign_id": ia11b["campaign_id"],
        "campaign_version": ia11b["version"],
        "offline_only": False,
        "live_executed": True,
        "ia11a_base_campaign_id": base_id,
        "ia11a_base_matrix_path": str(base_path),
        "ia11b_matrix_path": str(ib_path),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "corpus_path": str(cpath_resolved),
        "honesty_disclaimer": ia11b.get("honesty_disclaimer"),
        "token_tracker_snapshot_post_live": token_snap_global,
        "non_measurable_offline": ia11a.get("non_measurable_offline"),
        "ia11b_recommendation_markdown": rec_md,
        "segments": segments_out,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jpath = output_dir / f"comparative_campaign_{ia11b_campaign_id}_{ts}.json"
    mpath = output_dir / f"comparative_campaign_{ia11b_campaign_id}_{ts}.md"
    with jpath.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    with mpath.open("w", encoding="utf-8") as f:
        f.write(md)
    return payload, jpath, mpath, md


def run_comparative_offline_campaign(
    *,
    campaign_id: str,
    corpus_path: Path | None,
    output_dir: Path,
) -> Tuple[Dict[str, Any], Path, Path, str]:
    """
    Enchaîne les segments définis dans la matrice JSON (harness offline uniquement).

    Returns:
        payload complet, chemin JSON, chemin Markdown, markdown (texte)
    """
    cpath = default_campaign_path(campaign_id)
    campaign = load_campaign_matrix(cpath)
    segments_out, resolved_corpus = build_offline_comparative_segments(
        campaign, corpus_path
    )
    payload: Dict[str, Any] = {
        "schema": "mathakine.ai_eval.comparative_campaign.v1",
        "campaign_id": campaign["campaign_id"],
        "campaign_version": campaign["version"],
        "offline_only": True,
        "live_executed": False,
        "mathakine_ai_eval_live_env_ignored": True,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign_matrix_path": str(cpath),
        "corpus_path": resolved_corpus,
        "honesty_disclaimer": campaign.get("honesty_disclaimer"),
        "non_measurable_offline": campaign.get("non_measurable_offline"),
        "ia11b_prerequisites": campaign.get("ia11b_prerequisites"),
        "segments": segments_out,
    }
    md = build_comparative_markdown(campaign, segments_out)

    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jpath = output_dir / f"comparative_campaign_{campaign_id}_{ts}.json"
    mpath = output_dir / f"comparative_campaign_{campaign_id}_{ts}.md"
    with jpath.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    with mpath.open("w", encoding="utf-8") as f:
        f.write(md)
    return payload, jpath, mpath, md


def _case_ok_for_exit(res: Dict[str, Any]) -> bool:
    if res.get("success"):
        return True
    if res.get("live_skipped"):
        return True
    return False


def _exit_code_from_payload(payload: Dict[str, Any]) -> int:
    for seg in payload.get("segments") or []:
        for r in seg.get("harness_report", {}).get("results") or []:
            if not _case_ok_for_exit(r):
                return 1
        for lv in seg.get("live_executed_variants") or []:
            for r in lv.get("harness_report", {}).get("results") or []:
                if not _case_ok_for_exit(r):
                    return 1
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="IA11a / IA11b — Campagne comparative harness (offline ou hybride borné)"
    )
    parser.add_argument(
        "--ia11b-bounded-live",
        action="store_true",
        help="Exécute IA11b : base offline IA11a + live borné (exige --live ou MATHAKINE_AI_EVAL_LIVE=1)",
    )
    parser.add_argument(
        "--ia11b-campaign",
        default="ia11b_live_bounded",
        help="Identifiant fichier matrice IA11b (tests/fixtures/ai_eval/campaigns/<id>.json)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Avec --ia11b-bounded-live : opt-in explicite aux appels OpenAI réels",
    )
    parser.add_argument(
        "--campaign",
        default="ia11a_offline_default",
        help="Identifiant = nom du fichier tests/fixtures/ai_eval/campaigns/<id>.json (IA11a)",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=None,
        help="Corpus JSON (défaut : même que le harness)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/ai_eval/campaigns"),
        help="Dossier pour JSON + Markdown comparatif",
    )
    parser.add_argument(
        "--stdout-json",
        action="store_true",
        help="Imprime le payload JSON sur stdout",
    )
    args = parser.parse_args(argv)

    if args.ia11b_bounded_live:
        if not harness_live_opt_in_allowed(live_cli_flag=bool(args.live)):
            print(
                "ERREUR IA11b : mode live refusé. Passer --live ou définir MATHAKINE_AI_EVAL_LIVE=1.",
                file=sys.stderr,
            )
            return 2
        payload, jpath, mpath, md = run_ia11b_bounded_live_campaign(
            ia11b_campaign_id=args.ia11b_campaign,
            corpus_path=args.corpus,
            output_dir=args.output_dir,
        )
    else:
        if os.environ.get("MATHAKINE_AI_EVAL_LIVE", "").strip():
            print(
                "[IA11a] MATHAKINE_AI_EVAL_LIVE est défini : ignoré pour cette commande "
                "(campagne strictement offline, aucun appel live).",
                file=sys.stderr,
            )

        payload, jpath, mpath, md = run_comparative_offline_campaign(
            campaign_id=args.campaign,
            corpus_path=args.corpus,
            output_dir=args.output_dir,
        )

    if args.stdout_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    print(f"Comparatif JSON : {jpath}")
    print(f"Comparatif MD   : {mpath}")
    print()
    print(md)

    return _exit_code_from_payload(payload)


if __name__ == "__main__":
    raise SystemExit(main())

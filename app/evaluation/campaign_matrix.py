"""
Matrice de campagne comparative offline (IA11a).

Charge la configuration versionnée sous ``tests/fixtures/ai_eval/campaigns/``.
Aucune exécution live : la matrice décrit protocole, segments harness et variantes planifiées.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


def default_campaigns_dir() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "fixtures"
        / "ai_eval"
        / "campaigns"
    )


def default_campaign_path(campaign_id: str) -> Path:
    """Fichier attendu : ``{campaign_id}.json``."""
    p = default_campaigns_dir() / f"{campaign_id}.json"
    if not p.is_file():
        raise FileNotFoundError(f"Campagne introuvable: {p}")
    return p


def load_campaign_matrix(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    _validate_campaign_matrix(data)
    return data


def default_ia11b_campaign_path(campaign_id: str) -> Path:
    """Fichier attendu : ``{campaign_id}.json`` (même répertoire que IA11a)."""
    p = default_campaigns_dir() / f"{campaign_id}.json"
    if not p.is_file():
        raise FileNotFoundError(f"Campagne IA11b introuvable: {p}")
    return p


def load_ia11b_bounded_campaign(path: Path) -> Dict[str, Any]:
    """Charge la matrice IA11b (hybride) — validation distincte de :func:`load_campaign_matrix`."""
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    _validate_ia11b_bounded_campaign(data)
    return data


def _validate_ia11b_bounded_campaign(data: Dict[str, Any]) -> None:
    if data.get("offline_only") is True:
        raise ValueError("IA11b : offline_only doit être false (campagne hybride).")
    cid = data.get("campaign_id")
    if not cid or not isinstance(cid, str):
        raise ValueError("campaign_id manquant ou invalide (IA11b)")
    base = data.get("base_offline_campaign_id")
    if not base or not isinstance(base, str):
        raise ValueError("base_offline_campaign_id requis (référence IA11a)")
    base_path = default_campaign_path(base)
    if not base_path.is_file():
        raise ValueError(f"Campagne IA11a de base introuvable: {base_path}")
    ex = data.get("live_executions")
    if not isinstance(ex, list) or not ex:
        raise ValueError("live_executions doit être une liste non vide")
    from app.core.ai_generation_policy import (
        assert_exercise_ai_model_allowed,
        normalize_exercise_ai_model_id,
    )

    by_wl: Dict[str, int] = {}
    for i, row in enumerate(ex):
        if not isinstance(row, dict):
            raise ValueError(f"live_executions[{i}] invalide")
        for k in ("workload_key", "variant_id", "source_case_id", "eval_model"):
            if not row.get(k):
                raise ValueError(f"live_executions[{i}] : {k} requis")
        wl = str(row["workload_key"])
        by_wl[wl] = by_wl.get(wl, 0) + 1
        if by_wl[wl] > 2:
            raise ValueError(
                f"IA11b borné : au plus 2 exécutions live par workload ({wl!r} > 2)."
            )
        try:
            em = normalize_exercise_ai_model_id(str(row["eval_model"]))
            assert_exercise_ai_model_allowed(em)
        except Exception as e:
            raise ValueError(f"live_executions[{i}].eval_model invalide: {e}") from e


def _validate_campaign_matrix(data: Dict[str, Any]) -> None:
    if not data.get("offline_only") is True:
        raise ValueError("IA11a : la campagne doit avoir offline_only=true")
    cid = data.get("campaign_id")
    if not cid or not isinstance(cid, str):
        raise ValueError("campaign_id manquant ou invalide")
    segs = data.get("segments")
    if not isinstance(segs, list) or not segs:
        raise ValueError("segments doit être une liste non vide")
    for i, s in enumerate(segs):
        if not isinstance(s, dict):
            raise ValueError(f"segment[{i}] invalide")
        for k in ("workload_key", "harness_target"):
            if not s.get(k):
                raise ValueError(f"segment[{i}] : {k} requis")
        variants = s.get("live_planned_variants") or []
        for j, v in enumerate(variants):
            if not isinstance(v, dict):
                raise ValueError(f"segment[{i}].live_planned_variants[{j}] invalide")
            st = v.get("status")
            if st and "executed" in st.lower() and "not" not in st.lower():
                raise ValueError(
                    f"variante {v.get('variant_id')} : statut interdit en IA11a (exécution live)"
                )


@dataclass(frozen=True)
class CampaignSegmentSpec:
    workload_key: str
    harness_target: str
    description: str
    offline_comparison_axes: List[str]
    live_planned_variants: List[Dict[str, Any]]

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> CampaignSegmentSpec:
        return CampaignSegmentSpec(
            workload_key=str(d["workload_key"]),
            harness_target=str(d["harness_target"]),
            description=str(d.get("description", "")),
            offline_comparison_axes=list(d.get("offline_comparison_axes") or []),
            live_planned_variants=list(d.get("live_planned_variants") or []),
        )

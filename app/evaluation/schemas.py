"""Structures de rapport (sérialisables JSON)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CaseResult:
    """Résultat d'un cas du corpus."""

    case_id: str
    pipeline: str
    success: bool
    failure_reason: Optional[str] = None
    latency_ms: Optional[float] = None
    structural_ok: Optional[bool] = None
    structural_errors: List[str] = field(default_factory=list)
    business_ok: Optional[bool] = None
    business_errors: List[str] = field(default_factory=list)
    difficulty_flags: Dict[str, Any] = field(default_factory=dict)
    choices_flags: Dict[str, Any] = field(default_factory=dict)
    tokens_prompt: Optional[int] = None
    tokens_completion: Optional[int] = None
    cost_usd_estimate: Optional[float] = None
    live_skipped: bool = False
    skip_reason: Optional[str] = None
    rationale: Optional[str] = None
    pedagogical_note: Optional[str] = None
    expected_success: bool = True
    # Harness / campagne : modèle explicitement fixé pour l’évaluation (hors défaut produit).
    eval_model: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HarnessReport:
    mode: str
    target: str
    corpus_path: str
    corpus_version: int
    cases_total: int
    cases_run: int
    cases_passed: int
    cases_failed: int
    cases_skipped: int
    results: List[Dict[str, Any]] = field(default_factory=list)
    summary_markdown: str = ""
    token_tracker_snapshot: Optional[Dict[str, Any]] = None
    limitations_note: str = ""
    # Renseigné avant écriture des artefacts si persistance DB (--persist).
    run_uuid: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

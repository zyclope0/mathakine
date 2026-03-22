"""
Politique de calibration de la difficulté des défis (backend, post-génération IA).

Objectifs (lot IA5) :
- éviter une ``difficulty_rating`` décorative ou contradictoire avec la structure ;
- exposer des signaux explicites (axes) pour audit dans ``generation_parameters`` ;
- rester compatible avec l'échelle publique 1.0–5.0 (``difficulty_rating``).

La contrainte d'unicité logique complète (grilles zebra) n'est pas prouvée ici — seulement
des garde-fous objectivables.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from app.core.constants import calculate_difficulty_for_age_group, normalize_age_group

# Marqueurs de fuite de règle dans le titre (trop explicite pour une difficulté élevée)
_TITLE_RULE_LEAK_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"×\s*\d", re.I),
    re.compile(r"\bx\s*\d+\b", re.I),
    re.compile(r"\*\s*\d+"),
    re.compile(r"\+\d+|\+\s*\d+"),
    re.compile(
        r"\b(symétrie|symetrie|alternance|double|triple|fois\s*2|fois\s*3|×2|×3)\b",
        re.I,
    ),
    re.compile(r"\bcycle\s+(×|x|\*)", re.I),
    re.compile(r"\b(n\^2|n²|carrés?\s+suivant)", re.I),
)


@dataclass(frozen=True)
class ChallengeDifficultySignals:
    """Signaux heuristiques structurés (sérialisables en JSON)."""

    reasoning_steps_hint: int  # ordre de grandeur, pas une preuve
    rule_visibility: str  # "hidden" | "partial" | "explicit_in_title" | "unknown"
    constraint_count: int
    elements_to_deduce: int
    notes: Tuple[str, ...] = ()


def title_suggests_rule_leak(title: str) -> bool:
    """True si le titre révèle probablement la règle (incohérent avec une difficulté haute)."""
    if not title or not str(title).strip():
        return False
    t = str(title).strip()
    return any(p.search(t) for p in _TITLE_RULE_LEAK_PATTERNS)


def _count_question_cells(grid: Any) -> int:
    if not isinstance(grid, list):
        return 0
    n = 0
    for row in grid:
        if not isinstance(row, (list, tuple)):
            continue
        for c in row:
            if c == "?" or (isinstance(c, str) and "?" in c):
                n += 1
    return n


def estimate_structure_signals(
    challenge_type: str,
    visual_data: Dict[str, Any],
    title: str,
) -> ChallengeDifficultySignals:
    """Dérive des signaux à partir du contenu (sans appeler le LLM)."""
    ct = (challenge_type or "").strip().lower()
    vd = visual_data or {}
    notes: List[str] = []

    rule_visibility = "unknown"
    if title_suggests_rule_leak(title):
        rule_visibility = "explicit_in_title"
    elif (
        ct == "sequence"
        and isinstance(vd.get("pattern"), str)
        and vd["pattern"].strip()
    ):
        rule_visibility = "partial"

    reasoning_steps_hint = 2
    constraint_count = 0
    elements_to_deduce = 1

    if ct == "pattern":
        grid = vd.get("grid", [])
        q = _count_question_cells(grid)
        elements_to_deduce = max(1, q)
        constraint_count = q * 2  # lignes / colonnes implicites
        reasoning_steps_hint = min(5, 2 + q)
    elif ct == "sequence":
        seq = vd.get("sequence", [])
        n = len(seq) if isinstance(seq, list) else 0
        constraint_count = max(0, n - 1)
        reasoning_steps_hint = min(5, 2 + max(0, n // 3))
    elif ct == "puzzle":
        pieces = vd.get("pieces", vd.get("items", []))
        hints = vd.get("hints", vd.get("rules", vd.get("clues", [])))
        np_ = len(pieces) if isinstance(pieces, list) else 0
        nh = len(hints) if isinstance(hints, list) else 0
        constraint_count = nh + max(0, np_ - 1)
        elements_to_deduce = max(1, np_)
        reasoning_steps_hint = min(5, 2 + nh // 2)
    elif ct == "deduction":
        entities = vd.get("entities", {})
        clues = vd.get("clues", [])
        if isinstance(entities, dict):
            constraint_count = sum(
                len(v) for v in entities.values() if isinstance(v, list)
            )
        if isinstance(clues, list):
            constraint_count += len(clues)
        ncat = len(entities) if isinstance(entities, dict) else 0
        first_len = 0
        if isinstance(entities, dict) and entities:
            first = next(iter(entities.values()))
            if isinstance(first, list):
                first_len = len(first)
        elements_to_deduce = max(1, first_len)
        reasoning_steps_hint = min(
            6, 2 + ncat + (len(clues) if isinstance(clues, list) else 0) // 2
        )
    elif ct == "graph":
        nodes = vd.get("nodes", [])
        edges = vd.get("edges", [])
        if isinstance(nodes, list):
            constraint_count += len(nodes)
        if isinstance(edges, list):
            constraint_count += len(edges)
        reasoning_steps_hint = min(5, 3 + constraint_count // 4)
    else:
        notes.append("type_without_fine_signals")

    return ChallengeDifficultySignals(
        reasoning_steps_hint=reasoning_steps_hint,
        rule_visibility=rule_visibility,
        constraint_count=constraint_count,
        elements_to_deduce=elements_to_deduce,
        notes=tuple(notes),
    )


def validate_title_difficulty_coherence(
    title: str, difficulty_rating: float
) -> List[str]:
    """Erreurs si le titre révèle la règle tout en annonçant une difficulté élevée."""
    errors: List[str] = []
    if difficulty_rating >= 4.0 and title_suggests_rule_leak(title):
        errors.append(
            "Difficulté incohérente : le titre semble révéler la règle (mots-chiffres, "
            "symétrie, ×, +n…) alors que difficulty_rating >= 4.0. Adoucir le titre ou "
            "abaisser la difficulté."
        )
    return errors


def validate_difficulty_structural_coherence(
    challenge_type: str,
    visual_data: Dict[str, Any],
    difficulty_rating: float,
) -> List[str]:
    """Erreurs objectivables : structure trop simple vs difficulté annoncée."""
    errors: List[str] = []
    ct = (challenge_type or "").strip().upper()
    vd = visual_data or {}

    if ct == "PATTERN":
        grid = vd.get("grid", [])
        q = _count_question_cells(grid)
        if q <= 1 and difficulty_rating > 3.0:
            errors.append(
                "PATTERN : une seule case '?' ne justifie pas difficulty_rating > 3.0 "
                "(déduction locale sans pattern global)."
            )
    if ct == "SEQUENCE":
        if (
            isinstance(vd.get("pattern"), str)
            and vd["pattern"].strip()
            and difficulty_rating >= 4.0
        ):
            errors.append(
                "SEQUENCE : visual_data.pattern présent avec difficulty_rating >= 4.0 "
                "(la règle est trop exposée pour une difficulté élevée)."
            )
    if ct == "PUZZLE":
        pieces = vd.get("pieces", vd.get("items", []))
        np_ = len(pieces) if isinstance(pieces, list) else 0
        if np_ > 0 and np_ <= 4 and difficulty_rating >= 4.0:
            errors.append(
                "PUZZLE : au plus 4 pièces avec difficulty_rating >= 4.0 — "
                "ajoutez de pièces et des indices indirects, ou baissez la difficulté."
            )
    if ct == "DEDUCTION":
        clues = vd.get("clues", [])
        nclues = len(clues) if isinstance(clues, list) else 0
        entities = vd.get("entities", {})
        ncat = len(entities) if isinstance(entities, dict) else 0
        if ncat >= 2 and nclues < 2 and difficulty_rating >= 3.0:
            errors.append(
                "DEDUCTION : moins de 2 indices (clues) pour une grille multi-catégories "
                "avec difficulty_rating >= 3.0 — insuffisant pour guider sans deviner."
            )
    return errors


def calibrate_challenge_difficulty(
    *,
    challenge_type: str,
    age_group: str,
    visual_data: Union[Dict[str, Any], str, None],
    title: str,
    ai_difficulty: Optional[float],
) -> Tuple[float, Dict[str, Any]]:
    """
    Calcule ``difficulty_rating`` final + métadonnées ``difficulty_calibration`` pour la persistance.

    Reprend la logique historique (écart à la baseline âge, plafond pattern, plancher adulte)
    puis applique des plafonds basés sur les signaux structurels.
    """
    vd: Dict[str, Any]
    if visual_data is None:
        vd = {}
    elif isinstance(visual_data, str):
        try:
            vd = json.loads(visual_data)
        except (json.JSONDecodeError, TypeError):
            vd = {}
    else:
        vd = dict(visual_data) if isinstance(visual_data, dict) else {}

    canonical_age = normalize_age_group(age_group)
    baseline = calculate_difficulty_for_age_group(canonical_age)

    if (
        ai_difficulty is not None
        and isinstance(ai_difficulty, (int, float))
        and 1.0 <= float(ai_difficulty) <= 5.0
    ):
        ad = float(ai_difficulty)
        if abs(ad - baseline) > 1.5:
            final = baseline
            pre_adjust = "snapped_to_age_baseline"
        else:
            final = ad
            pre_adjust = "kept_ai_within_band"
    else:
        final = baseline
        pre_adjust = "default_baseline"

    # Plancher adulte (comportement existant)
    age_key = (age_group or "").strip().lower()
    if age_key == "adulte" and final < 4.0:
        final = max(final, 4.0)
        pre_adjust = f"{pre_adjust}+adult_floor"

    # Plafond pattern 1 case (comportement existant)
    if challenge_type.lower() == "pattern":
        grid = vd.get("grid", [])
        q = _count_question_cells(grid if isinstance(grid, list) else [])
        if q <= 1 and final > 3.0:
            final = min(final, 3.0)
            pre_adjust = f"{pre_adjust}+pattern_single_cell_cap"

    signals = estimate_structure_signals(challenge_type, vd, title)
    caps_applied: List[str] = []

    if signals.rule_visibility == "explicit_in_title" and final > 3.0:
        final = min(final, 3.0)
        caps_applied.append("title_rule_leak_cap_3_0")

    if challenge_type.lower() == "puzzle":
        pieces = vd.get("pieces", vd.get("items", []))
        np_ = len(pieces) if isinstance(pieces, list) else 0
        if np_ > 0 and np_ <= 4 and final > 3.0:
            final = min(final, 3.0)
            caps_applied.append("puzzle_small_piece_count_cap_3_0")

    if challenge_type.lower() == "deduction":
        clues = vd.get("clues", [])
        nclues = len(clues) if isinstance(clues, list) else 0
        entities = vd.get("entities", {})
        ncat = len(entities) if isinstance(entities, dict) else 0
        if ncat >= 2 and nclues < 2 and final > 2.5:
            final = min(final, 2.5)
            caps_applied.append("deduction_insufficient_clues_cap_2_5")

    sig_dict = asdict(signals)
    sig_dict["notes"] = list(sig_dict["notes"])

    calibration_meta: Dict[str, Any] = {
        "pre_adjustment": pre_adjust,
        "age_baseline": baseline,
        "signals": sig_dict,
        "caps_applied": caps_applied,
        "final_rating": round(final, 2),
    }
    return round(final, 2), calibration_meta

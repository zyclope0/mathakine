"""
Stable, deterministic error codes for challenge validation messages (observability only).
"""

from __future__ import annotations

import re
import unicodedata
from collections import OrderedDict
from typing import Callable, Optional

_CODE_VALIDATION_UNKNOWN = "validation_unknown"


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


def _fix_common_mojibake(text: str) -> str:
    """Mojibake typique: UTF-8 re-lu en Latin-1 (ex. dÃ©jÃ , Ã©chec). Après .lower() : dã©jã, ã©chec."""
    t = text
    t = re.sub(r"dã©jã\s*", "deja ", t, flags=re.IGNORECASE)
    t = t.replace("ã©chec", "echec")
    return t


def _normalize_error_text(error: str) -> str:
    t = str(error).lower()
    t = _fix_common_mojibake(t)
    t = _strip_accents(t)
    t = re.sub(r"[^\w\s:.'+\-/,%]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _build_rules() -> list[tuple[str, Callable[[str, Optional[str]], bool]]]:
    rules: list[tuple[str, Callable[[str, Optional[str]], bool]]] = []
    a = rules.append

    a(
        (
            "graph_nodes_missing",
            lambda t, ct: "visual_data" in t
            and "nodes" in t
            and ("manquant" in t or "invalide" in t),
        )
    )
    a(
        (
            "graph_edge_out_of_bounds",
            lambda t, ct: "arete" in t and ("inexistant" in t or "reference" in t),
        )
    )
    a(
        (
            "graph_answer_inconsistent",
            lambda t, ct: "graph" in t and "incoh" in t,
        )
    )
    a(
        (
            "chess_king_in_check",
            lambda t, ct: "chess" in t
            and "echec" in t
            and ("deja" in t or "jou" in t or "roi" in t),
        )
    )
    a(
        (
            "chess_invalid_piece",
            lambda t, ct: "chess" in t and "piece" in t and "invalide" in t,
        )
    )
    a(
        (
            "chess_board_malformed",
            lambda t, ct: "chess" in t
            and (
                "8 rangees" in t
                or "8 elements" in t
                or ("board" in t and "manquant" in t)
                or "board[" in t
            ),
        )
    )
    a(
        (
            "chess_missing_kings",
            lambda t, ct: "chess" in t and "roi" in t and "exactement" in t,
        )
    )
    a(
        (
            "malformed_choices",
            lambda t, ct: "choice" in t
            and ("doit" in t or "liste" in t)
            and "equivalent" not in t,
        )
    )
    a(
        (
            "duplicate_choices",
            lambda t, ct: "qcm" in t and "doublon" in t,
        )
    )
    a(
        (
            "missing_correct_answer",
            lambda t, ct: "correct_answer" in t and "vide" in t,
        )
    )
    a(
        (
            "missing_solution_explanation",
            lambda t, ct: "solution_explanation" in t and "vide" in t,
        )
    )
    a(
        (
            "visual_data_malformed",
            lambda t, ct: "visual_data" in t and "json" in t,
        )
    )
    a(
        (
            "missing_visual_data",
            lambda t, ct: "visual_data" in t and "manquant" in t,
        )
    )
    a(
        (
            "pattern_unverifiable",
            lambda t, ct: "pattern" in t and "non verif" in t,
        )
    )
    a(
        (
            "pattern_answer_inconsistent",
            lambda t, ct: "pattern" in t and "inco" in t and "non verif" not in t,
        )
    )
    a(
        (
            "sequence_answer_inconsistent",
            lambda t, ct: "sequence" in t and "incoh" in t,
        )
    )
    a(
        (
            "probability_sum_not_one",
            lambda t, ct: "probab" in t
            and "1" in t
            and any(
                x in t
                for x in (
                    "somm",
                    "poids",
                    "weight",
                    "total",
                    "urne",
                    "urns",
                )
            ),
        )
    )
    a(
        (
            "probability_equivalent_choices",
            lambda t, ct: (ct or "").strip().lower() == "probability"
            and "equivalent" in t,
        )
    )
    a(
        (
            "probability_equivalent_choices",
            lambda t, ct: "qcm" in t and "probab" in t and "equivalent" in t,
        )
    )
    a(
        (
            "probability_answer_inconsistent",
            lambda t, ct: "probab" in t and "incoh" in t,
        )
    )
    a(
        (
            "deduction_duplicate_first_segment",
            lambda t, ct: "deduction" in t
            and "meme entit" in t
            and "plusieurs fois" in t,
        )
    )
    a(
        (
            "deduction_bijection_violated",
            lambda t, ct: "deduction" in t and "one-to-one" in t,
        )
    )
    a(
        (
            "deduction_no_unique_solution",
            lambda t, ct: "deduction" in t
            and ("solution unique" in t or "plusieurs" in t or "menent" in t),
        )
    )
    a(
        (
            "deduction_no_solution",
            lambda t, ct: "deduction" in t
            and ("aucune solution" in t or "contradict" in t),
        )
    )
    a(
        (
            "deduction_constraint_parse_failed",
            lambda t, ct: "deduction" in t
            and ("association" in t or "segments" in t or "sans association" in t),
        )
    )
    a(
        (
            "deduction_answer_entities_missing",
            lambda t, ct: "deduction" in t
            and "entit" in t
            and "manquant" in t
            and "correct_answer" in t,
        )
    )
    a(
        (
            "deduction_answer_mismatch",
            lambda t, ct: "deduction" in t
            and ("ne correspond" in t or "correspond pas" in t),
        )
    )
    a(
        (
            "puzzle_missing_clues",
            lambda t, ct: "puzzle" in t
            and ("incomplet" in t or "aucun indice" in t or "seulement" in t),
        )
    )
    a(
        (
            "puzzle_answer_inconsistent",
            lambda t, ct: "puzzle" in t and "incoh" in t,
        )
    )
    a(
        (
            "coding_answer_inconsistent",
            lambda t, ct: "maze" in t and "chemin" in t,
        )
    )
    return rules


_CLASSIFICATION_RULES = _build_rules()


def classify_challenge_validation_error(
    error: str, challenge_type: str | None = None
) -> str:
    t = _normalize_error_text(error)
    ct = (challenge_type or "").strip() or None
    for code, check in _CLASSIFICATION_RULES:
        try:
            if check(t, ct):
                return code
        except Exception:  # noqa: BLE001 — must never break callers
            continue
    return _CODE_VALIDATION_UNKNOWN


def classify_challenge_validation_errors(
    errors: list[str], challenge_type: str | None = None
) -> list[str]:
    """Return deduplicated error codes, preserving first-seen order."""
    ordered: OrderedDict[str, None] = OrderedDict()
    for err in errors:
        c = classify_challenge_validation_error(err, challenge_type)
        if c not in ordered:
            ordered[c] = None
    return list(ordered.keys())

"""
Service de vérification des réponses aux défis logiques.

Extrait du handler challenge_handlers.py — 7 stratégies de comparaison
selon le type de défi + 4 helpers de normalisation.

Phase 3, item 3.1 — audit architecture 03/2026.
"""

import ast
import json
import re
import unicodedata
from typing import Dict, List, Optional, Tuple

from app.core.logging_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Mapping ordinaux FR → chiffres
# ---------------------------------------------------------------------------
_ORDINAL_NORM: Dict[str, str] = {
    "1er": "1",
    "1ère": "1",
    "1e": "1",
    "1ere": "1",
    "2ème": "2",
    "2eme": "2",
    "2e": "2",
    "3ème": "3",
    "3eme": "3",
    "3e": "3",
    "4ème": "4",
    "4eme": "4",
    "4e": "4",
    "5ème": "5",
    "5eme": "5",
    "5e": "5",
    "6ème": "6",
    "6eme": "6",
    "6e": "6",
    "7ème": "7",
    "7eme": "7",
    "7e": "7",
    "8ème": "8",
    "8eme": "8",
    "8e": "8",
    "9ème": "9",
    "9eme": "9",
    "9e": "9",
    "10ème": "10",
    "10eme": "10",
    "10e": "10",
}

# Notation échecs EN → FR
_EN_TO_FR_CHESS: Dict[str, str] = {
    "Q": "D",
    "R": "T",
    "B": "F",
    "N": "C",
    "K": "R",
    "P": "P",
}

# Ensembles pour normalisation visuelle
_SHAPES = frozenset(
    {
        "carre",
        "cercle",
        "triangle",
        "rectangle",
        "losange",
        "etoile",
        "hexagone",
        "pentagone",
        "heptagone",
        "octogone",
        "nonagone",
    }
)

_COLORS = frozenset(
    {
        "rouge",
        "bleu",
        "vert",
        "jaune",
        "orange",
        "violet",
        "rose",
        "gris",
        "noir",
        "blanc",
        "red",
        "blue",
        "green",
        "yellow",
        "purple",
        "gray",
        "grey",
        "pink",
        "black",
        "white",
    }
)

_SHAPE_SYNONYMS: List[Tuple[str, str]] = [
    ("rectangle", "carre"),
    ("square", "carre"),
    ("circle", "cercle"),
    ("carré", "carre"),
    ("étoile", "etoile"),
    ("heptagon", "heptagone"),
    ("octagon", "octogone"),
    ("nonagon", "nonagone"),
]

_ANSWER_LIST_SEPARATOR_RE = re.compile(r"\s*(?:,|;|\n)\s*")


# ---------------------------------------------------------------------------
# Helpers publics
# ---------------------------------------------------------------------------


def normalize_accents(text: str) -> str:
    """Retire les accents pour tolérance (carré→carre, élève→eleve)."""
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def normalize_shape_answer(text: str) -> str:
    """Normalise pour VISUAL : synonymes, accents, ordre forme+couleur."""
    if not text:
        return ""
    t = text.lower().strip()
    for old, new in _SHAPE_SYNONYMS:
        t = re.sub(rf"\b{re.escape(old)}\b", new, t)
    t = normalize_accents(t)
    mots = t.split()
    f, c = None, None
    for m in mots:
        if m in _SHAPES:
            f = m
        elif m in _COLORS:
            c = m
    if f and c:
        t = f"{f} {c}"
    return t


def parse_multi_visual_answer(text: str) -> List[Tuple[int, str]]:
    """Parse multi-cellules VISUAL.

    Formats acceptés :
    - 'Position 6: carré bleu, Position 9: triangle vert'
    - '6:cercle rouge,9:étoile jaune' (format IA)
    """
    if not text or not text.strip():
        return []
    parts: List[Tuple[int, str]] = []
    for segment in _ANSWER_LIST_SEPARATOR_RE.split(text.strip()):
        segment = segment.strip()
        if not segment:
            continue
        if ":" in segment:
            pos_part, ans_part = segment.split(":", 1)
            ans_part = ans_part.strip()
            pos_digits = "".join(c for c in pos_part if c.isdigit())
            if pos_digits and ans_part and not ans_part.isdigit():
                parts.append((int(pos_digits), normalize_shape_answer(ans_part)))
                continue
        parts.append((0, normalize_shape_answer(segment)))
    if parts:
        return parts
    return [(0, normalize_shape_answer(text))] if text.strip() else []


def parse_answer_to_list(answer: str) -> List[str]:
    """Parse une réponse en liste, gérant plusieurs formats.

    Formats : liste Python, CSV, espaces, valeur simple.
    """
    answer = str(answer).strip()

    if answer.startswith("[") and answer.endswith("]"):
        try:
            parsed = ast.literal_eval(answer)
            if isinstance(parsed, list):
                return [str(item).strip().lower() for item in parsed]
        except (ValueError, SyntaxError):
            pass
        inner = answer[1:-1]
        items = []
        for item in inner.split(","):
            item = item.strip().strip("'").strip('"').strip().lower()
            if item:
                items.append(item)
        return items

    if _ANSWER_LIST_SEPARATOR_RE.search(answer):
        return [
            item.strip().lower()
            for item in _ANSWER_LIST_SEPARATOR_RE.split(answer)
            if item.strip()
        ]

    parts = [p.strip().lower() for p in answer.split() if p.strip()]
    if len(parts) > 1:
        return parts

    return [answer.lower()] if answer else []


# ---------------------------------------------------------------------------
# Stratégies de comparaison
# ---------------------------------------------------------------------------


def compare_deduction(user_answer: str, correct_answer: str) -> bool:
    """Compare les réponses pour les défis de déduction.

    L'ordre des associations n'a pas d'importance, seul le contenu compte.
    Normalise les ordinaux français (1er, 2ème...) en chiffres.
    """

    def _norm_ordinal(s: str) -> str:
        t = s.strip().lower()
        return _ORDINAL_NORM.get(t, t)

    def _parse_associations(answer: str) -> set:
        answer = str(answer).strip().lower()
        associations: set = set()
        if ":" in answer:
            for part in answer.split(","):
                part = part.strip()
                if part:
                    raw = [e.strip() for e in part.split(":") if e.strip()]
                    elements = tuple(sorted([_norm_ordinal(e) for e in raw]))
                    if elements:
                        associations.add(elements)
        elif "{" in answer:
            try:
                data = json.loads(answer.replace("'", '"'))
                if isinstance(data, dict):
                    for key, values in data.items():
                        if isinstance(values, dict):
                            elements = tuple(
                                sorted(
                                    [str(key).lower()]
                                    + [str(v).lower() for v in values.values()]
                                )
                            )
                        else:
                            elements = tuple(
                                sorted([str(key).lower(), str(values).lower()])
                            )
                        associations.add(elements)
            except (json.JSONDecodeError, ValueError, TypeError, AttributeError):
                pass
        return associations

    user_assoc = _parse_associations(user_answer)
    correct_assoc = _parse_associations(correct_answer)
    logger.debug("Deduction - User: {}, Correct: {}", user_assoc, correct_assoc)
    return user_assoc == correct_assoc


def compare_probability(user_answer: str, correct_answer: str) -> bool:
    """Compare les réponses probabilité (fractions, %, décimaux) avec tolérance."""

    def _parse_value(text: str) -> Optional[float]:
        if not text or not isinstance(text, str):
            return None
        t = text.strip()
        if "/" in t:
            try:
                a, b = t.split("/", 1)
                num, den = float(a.strip()), float(b.strip())
                return num / den if den else None
            except (ValueError, ZeroDivisionError):
                return None
        if "%" in t:
            try:
                return float(t.replace("%", "").strip()) / 100
            except ValueError:
                return None
        try:
            return float(t.replace(",", "."))
        except ValueError:
            return None

    u_val = _parse_value(user_answer)
    c_val = _parse_value(correct_answer or "")
    is_correct = u_val is not None and c_val is not None and abs(u_val - c_val) < 0.001
    if not is_correct and user_answer.strip() == (correct_answer or "").strip():
        is_correct = True
    logger.debug(
        "PROBABILITY - User: {}, Correct: {}, Parsed: {}/{}, Result: {}",
        user_answer,
        correct_answer,
        u_val,
        c_val,
        is_correct,
    )
    return is_correct


def compare_chess(user_answer: str, correct_answer: str) -> bool:
    """Compare les réponses échecs avec normalisation notation FR/EN."""

    def _normalize(text: str) -> str:
        if not text or not isinstance(text, str):
            return ""
        t = text.strip()
        t = re.sub(r"\d+[.)]\s*", "", t)
        t = re.sub(r"\s+", " ", t).strip()
        parts = t.split()
        out = []
        for p in parts:
            if len(p) >= 1 and p[0].upper() in _EN_TO_FR_CHESS:
                out.append(_EN_TO_FR_CHESS[p[0].upper()] + p[1:])
            else:
                out.append(p)
        t = " ".join(out).upper()
        return t.replace(" ", "")

    u_norm = _normalize(user_answer)
    correct_raw = correct_answer or ""
    correct_variants = [s.strip() for s in correct_raw.split("|") if s.strip()]
    correct_norms = [_normalize(v) for v in correct_variants]
    is_correct = (
        u_norm in correct_norms if correct_norms else u_norm == _normalize(correct_raw)
    )
    logger.debug(
        "CHESS - User: {}, Correct: {}, Result: {}", u_norm, correct_norms, is_correct
    )
    return is_correct


def compare_graph(user_answer: str, correct_answer: str) -> bool:
    """Compare les réponses graphe (ensemble de noeuds ou chemin ordonné)."""
    user_list = parse_answer_to_list(user_answer)
    correct_list = parse_answer_to_list(correct_answer or "")
    user_set = {u.strip().upper() for u in user_list if u.strip()}
    correct_set = {c.strip().upper() for c in correct_list if c.strip()}
    is_node_list = len(correct_set) > 1 and not any("-" in str(c) for c in correct_list)
    if is_node_list:
        is_correct = user_set == correct_set
    else:
        is_correct = user_list == correct_list
    logger.debug(
        "GRAPH - User: {}, Correct: {}, Result: {}",
        user_set if is_node_list else user_list,
        correct_set if is_node_list else correct_list,
        is_correct,
    )
    return is_correct


def compare_visual_pattern(
    user_answer: str,
    correct_answer: str,
    challenge_type: str,
    visual_data: Optional[dict] = None,
) -> bool:
    """Compare les réponses VISUAL/PATTERN avec tolérance formes et couleurs."""
    computed_pattern_answer = None
    if (
        "pattern" in challenge_type
        and visual_data
        and not str(correct_answer or "").strip()
    ):
        grid = visual_data.get("grid") if isinstance(visual_data, dict) else None
        if grid:
            from app.services.challenges.challenge_validation_analysis import (
                analyze_pattern,
                compute_pattern_answers_multi,
            )

            computed_multi = compute_pattern_answers_multi(grid)
            if computed_multi:
                computed_pattern_answer = computed_multi
            else:
                for i, row in enumerate(grid):
                    if not isinstance(row, (list, tuple)):
                        continue
                    for j, cell in enumerate(row):
                        if cell == "?" or (isinstance(cell, str) and "?" in str(cell)):
                            computed_pattern_answer = analyze_pattern(grid, i, j)
                            break
                    if computed_pattern_answer is not None:
                        break

    effective_correct = (correct_answer or computed_pattern_answer or "").strip()

    is_ordered_multi_answer = (
        ("pattern" in challenge_type or "visual" in challenge_type)
        and effective_correct
        and _ANSWER_LIST_SEPARATOR_RE.search(effective_correct)
        and "position" not in effective_correct.lower()
    )

    if is_ordered_multi_answer:
        user_list = parse_answer_to_list(user_answer)
        correct_list = parse_answer_to_list(effective_correct)
        user_norm = [normalize_shape_answer(u) for u in user_list]
        correct_norm = [normalize_shape_answer(c) for c in correct_list]
        is_correct = len(user_norm) == len(correct_norm) and all(
            u == c for u, c in zip(user_norm, correct_norm)
        )
    else:
        user_parts = parse_multi_visual_answer(user_answer)
        correct_parts = parse_multi_visual_answer(effective_correct or "")
        is_multi_position = (
            len(correct_parts) > 1 and any(p[0] > 0 for p in correct_parts)
        ) or (len(user_parts) > 1 and any(p[0] > 0 for p in user_parts))

        if is_multi_position:
            if len(correct_parts) == 1 and len(user_parts) == 1:
                is_correct = user_parts[0][1] == correct_parts[0][1]
            elif len(user_parts) == len(correct_parts):
                correct_sorted = sorted(correct_parts, key=lambda x: x[0])
                user_sorted = sorted(user_parts, key=lambda x: x[0])
                by_position = all(
                    u[1] == c[1] for u, c in zip(user_sorted, correct_sorted)
                )
                if not by_position and all(u[0] == 0 for u in user_parts):
                    user_answers = {p[1] for p in user_parts if p[1]}
                    correct_answers = {p[1] for p in correct_parts if p[1]}
                    is_correct = user_answers == correct_answers
                else:
                    is_correct = by_position
            else:
                user_answers = {p[1] for p in user_parts if p[1]}
                correct_answers = {p[1] for p in correct_parts if p[1]}
                is_correct = user_answers == correct_answers and len(
                    user_answers
                ) == len(correct_answers)
        else:
            user_list = parse_answer_to_list(user_answer)
            correct_list = parse_answer_to_list(effective_correct)
            u = user_list[0] if user_list else ""
            c = correct_list[0] if correct_list else ""
            is_correct = normalize_shape_answer(u) == normalize_shape_answer(c)

    logger.debug("VISUAL/PATTERN - Result: {}", is_correct)
    return is_correct


def compare_sequence_default(user_answer: str, correct_answer: str) -> bool:
    """Comparaison par défaut (SEQUENCE et autres types simples)."""
    user_list = parse_answer_to_list(user_answer)
    correct_list = parse_answer_to_list(correct_answer)
    logger.debug("Default comparison - User: {}, Correct: {}", user_list, correct_list)
    if len(user_list) > 1 or len(correct_list) > 1:
        return user_list == correct_list
    u = user_list[0] if user_list else ""
    c = correct_list[0] if correct_list else ""
    return u == c


# ---------------------------------------------------------------------------
# Point d'entrée unique
# ---------------------------------------------------------------------------


def check_answer(
    challenge_type: str,
    user_answer: str,
    correct_answer: str,
    visual_data: Optional[dict] = None,
) -> bool:
    """Vérifie une réponse selon le type de défi.

    Args:
        challenge_type: Type du défi (ex: 'DEDUCTION', 'PROBABILITY', etc.)
        user_answer: Réponse soumise par l'utilisateur
        correct_answer: Réponse attendue
        visual_data: Données visuelles optionnelles (grille pattern)

    Returns:
        True si la réponse est correcte.
    """
    ct = challenge_type.lower() if challenge_type else ""

    if "deduction" in ct and ":" in user_answer:
        return compare_deduction(user_answer, correct_answer)
    elif "probability" in ct:
        return compare_probability(user_answer, correct_answer)
    elif "chess" in ct:
        return compare_chess(user_answer, correct_answer)
    elif "graph" in ct:
        return compare_graph(user_answer, correct_answer)
    elif "visual" in ct or "pattern" in ct:
        return compare_visual_pattern(user_answer, correct_answer, ct, visual_data)
    else:
        return compare_sequence_default(user_answer, correct_answer)

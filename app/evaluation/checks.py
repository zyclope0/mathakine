"""
Checks réutilisant les validateurs métier existants (pas de duplication des règles).

Sépare explicitement :
- validité structurelle (champs présents, types)
- validité métier (heuristiques pédagogiques / cohérence)
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Tuple

from app.services.challenges.challenge_difficulty_policy import (
    validate_difficulty_structural_coherence,
    validate_title_difficulty_coherence,
)
from app.services.challenges.challenge_validator import validate_challenge_logic
from app.services.exercises.exercise_ai_validation import validate_exercise_ai_output

_NUMERIC_TYPES_OPERAND_CHECK = frozenset(
    {"addition", "soustraction", "multiplication", "division"}
)


def _parse_int_operand(v: Any) -> Optional[int]:
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str):
        s = v.strip()
        if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
            return int(s)
    return None


def _parse_correct_as_number(s: str) -> Optional[float]:
    t = str(s).replace(",", ".").strip()
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _extract_two_operands_for_local_numeric(
    payload: Dict[str, Any], question: str
) -> Tuple[Optional[int], Optional[int]]:
    """Opérandes depuis num1/num2 (générateurs locaux) ou motif « Calcule a op b »."""
    n1 = _parse_int_operand(payload.get("num1"))
    n2 = _parse_int_operand(payload.get("num2"))
    if n1 is not None and n2 is not None:
        return n1, n2
    q = (question or "").strip()
    patterns = (
        ("addition", r"Calcule\s+(\d+)\s*\+\s*(\d+)"),
        ("soustraction", r"Calcule\s+(\d+)\s*-\s*(\d+)"),
        ("multiplication", r"Calcule\s+(\d+)\s*[×*xX]\s*(\d+)"),
        ("division", r"Calcule\s+(\d+)\s*[÷/]\s*(\d+)"),
    )
    for _op_name, pat in patterns:
        m = re.search(pat, q)
        if m:
            return int(m.group(1)), int(m.group(2))
    return None, None


def local_numeric_answer_coherence_errors(
    payload: Dict[str, Any], exercise_type: str
) -> List[str]:
    """
    Vérifie que ``correct_answer`` coïncide avec le calcul déterministe sur les opérandes,
    lorsqu'ils sont connus (champs num1/num2 ou question « Calcule … » du générateur).

    Ne couvre pas les énoncés narratifs sans opérandes extractibles (pas de faux négatif).
    """
    et = str(exercise_type or payload.get("exercise_type", "")).strip().lower()
    if et not in _NUMERIC_TYPES_OPERAND_CHECK:
        return []
    q = str(payload.get("question", ""))
    n1, n2 = _extract_two_operands_for_local_numeric(payload, q)
    if n1 is None or n2 is None:
        return []
    if et == "addition":
        expected = float(n1 + n2)
    elif et == "soustraction":
        expected = float(n1 - n2)
    elif et == "multiplication":
        expected = float(n1 * n2)
    else:
        if n2 == 0:
            return ["division_operande_diviseur_zero"]
        expected = float(n1 // n2)

    ca = _parse_correct_as_number(str(payload.get("correct_answer", "")))
    if ca is None:
        return []
    if not math.isclose(ca, expected, rel_tol=0.0, abs_tol=1e-9):
        return [
            "reponse_numerique_incoherente_avec_operandes_connus:"
            f"attendu≈{expected},correct_answer={payload.get('correct_answer')}"
        ]
    return []


def check_local_exercise_business_truth(
    payload: Dict[str, Any], exercise_type: str
) -> Tuple[bool, List[str]]:
    """
    Vérité métier minimale pour générateurs locaux (simple / template).

    Réutilise ``validate_exercise_ai_output`` (mêmes règles que le flux IA).
    Les générateurs locaux n'exposent en général pas ``hint`` : si la clé est absente,
    l'exigence de longueur sur l'indice ne s'applique pas (évite un vert structure-only).

    Ajoute une cohérence **déterministe** pour les types + − × ÷ lorsque deux opérandes
    entières sont déductibles (champs ``num1``/``num2`` ou texte « Calcule a op b »).
    """
    et = str(exercise_type or payload.get("exercise_type", "")).strip().lower()
    hint_key_present = "hint" in payload
    ok, reasons = validate_exercise_ai_output(
        exercise_type=et,
        title=str(payload.get("title", "")),
        question=str(payload.get("question", "")),
        correct_answer=str(payload.get("correct_answer", "")),
        choices=payload.get("choices"),
        explanation=str(payload.get("explanation", "")),
        hint=str(payload.get("hint", "")),
    )
    if not hint_key_present:
        reasons = [r for r in reasons if r != "hint_trop_court_ou_vide"]
    reasons.extend(local_numeric_answer_coherence_errors(payload, et))
    ok = len(reasons) == 0
    return ok, reasons


def check_exercise_structural_minimal(
    payload: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    """Champs minimaux pour tout exercice généré (simple ou template)."""
    errs: List[str] = []
    for key in ("title", "question", "correct_answer", "choices"):
        if key not in payload or payload[key] in (None, ""):
            errs.append(f"missing_or_empty:{key}")
    ch = payload.get("choices")
    if not isinstance(ch, list):
        errs.append("choices_not_list")
    elif len(ch) < 3:
        errs.append("choices_too_few")
    return len(errs) == 0, errs


def check_exercise_openai_shape(
    *,
    exercise_type: str,
    title: str,
    question: str,
    correct_answer: str,
    choices: Any,
    explanation: str,
    hint: str,
) -> Tuple[bool, List[str]]:
    """Même contrat que le flux OpenAI post-parse."""
    return validate_exercise_ai_output(
        exercise_type=exercise_type,
        title=title,
        question=question,
        correct_answer=correct_answer,
        choices=choices,
        explanation=explanation,
        hint=hint,
    )


def check_challenge_fixture(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    return validate_challenge_logic(data)


def challenge_difficulty_signals(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Signaux de cohérence titre/difficulté vs structure — ce ne sont pas des « scores ».
    Une liste vide = pas d'alerte heuristique ; ce n'est pas une garantie pédagogique.
    """
    title = str(data.get("title", "") or "")
    rating = float(data.get("difficulty_rating") or 3.0)
    ct = str(data.get("challenge_type", "") or "").upper()
    vd = data.get("visual_data") or {}
    if isinstance(vd, str):
        vd = {}
    if not isinstance(vd, dict):
        vd = {}

    return {
        "title_difficulty_messages": validate_title_difficulty_coherence(title, rating),
        "structure_difficulty_messages": validate_difficulty_structural_coherence(
            ct, vd, rating
        ),
    }


def exercise_choices_signals(
    exercise_type: str,
    correct_answer: str,
    choices: Any,
) -> Dict[str, Any]:
    """Résumé léger pour le rapport (les détails sont dans validate_exercise_ai_output)."""
    if not isinstance(choices, list):
        return {"choices_count": None, "note": "choices_not_list"}
    return {
        "choices_count": len(choices),
        "exercise_type_normalized": (exercise_type or "").strip().lower(),
        "correct_answer_repr": str(correct_answer)[:80],
    }

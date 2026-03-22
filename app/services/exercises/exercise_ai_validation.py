"""
Validation métier post-génération pour le flux exercices IA (SSE OpenAI).

Objectif : refuser de persister un contenu structurellement valide mais pédagogiquement
inutilisable (choix incohérents, bonne réponse absente, champs vides).

Limites assumées : pas de preuve mathématique formelle ; heuristiques explicites uniquement.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional, Sequence, Tuple

# Types pour lesquels on exige des choix / réponse correcte interprétables comme nombres.
_NUMERIC_EXERCISE_TYPES = frozenset(
    {"addition", "soustraction", "multiplication", "division"}
)

_MIN_TITLE_LEN = 3
_MIN_QUESTION_LEN = 12
_MIN_EXPLANATION_LEN = 40
_MIN_HINT_LEN = 8


def _strip_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_float(token: str) -> Optional[float]:
    t = str(token).replace(",", ".").strip()
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _try_parse_number(token: str) -> bool:
    return _parse_float(token) is not None


def _floats_close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=1e-9)


def _numeric_answer_in_choices(correct: str, choices: List[str]) -> bool:
    ca = _parse_float(correct)
    if ca is None:
        return False
    for c in choices:
        cv = _parse_float(c)
        if cv is not None and _floats_close(ca, cv):
            return True
    return False


def _numeric_choices_all_distinct(choices: List[str]) -> bool:
    vals: List[float] = []
    for s in choices:
        v = _parse_float(s)
        if v is None:
            return True
        vals.append(v)
    seen: List[float] = []
    for v in vals:
        if any(_floats_close(v, u) for u in seen):
            return False
        seen.append(v)
    return True


def validate_exercise_ai_output(
    *,
    exercise_type: str,
    title: str,
    question: str,
    correct_answer: str,
    choices: Any,
    explanation: str,
    hint: str,
) -> Tuple[bool, List[str]]:
    """
    Valide le paquet exercice après parsing JSON et sanitization des champs texte.

    Returns:
        (True, []) si OK
        (False, [codes ou messages courts]) sinon — ne pas persister si False.
    """
    reasons: List[str] = []
    et = (exercise_type or "").strip().lower()

    t = _strip_str(title)
    q = _strip_str(question)
    ca = _strip_str(correct_answer)
    expl = _strip_str(explanation)
    h = _strip_str(hint)

    if len(t) < _MIN_TITLE_LEN:
        reasons.append("title_trop_court")
    if len(q) < _MIN_QUESTION_LEN:
        reasons.append("question_trop_courte_ou_vide")
    if not ca:
        reasons.append("correct_answer_vide")
    if len(expl) < _MIN_EXPLANATION_LEN:
        reasons.append("explication_trop_courte_ou_vide")
    if len(h) < _MIN_HINT_LEN:
        reasons.append("hint_trop_court_ou_vide")

    if not isinstance(choices, Sequence) or isinstance(choices, (str, bytes)):
        reasons.append("choices_doit_etre_une_liste")
        return False, reasons

    choice_list = list(choices)
    if len(choice_list) != 4:
        reasons.append("choices_doit_contenir_4_elements")
        return False, reasons

    choices_str: List[str] = []
    for i, c in enumerate(choice_list):
        s = _strip_str(c)
        if not s:
            reasons.append(f"choice_{i}_vide")
        choices_str.append(s)

    if et in _NUMERIC_EXERCISE_TYPES:
        if ca and not _try_parse_number(ca):
            reasons.append("correct_answer_non_numerique_attendu")
        for i, s in enumerate(choices_str):
            if s and not _try_parse_number(s):
                reasons.append(f"choice_{i}_non_numerique_attendu")
        if choices_str and all(_try_parse_number(s) for s in choices_str):
            if not _numeric_choices_all_distinct(choices_str):
                reasons.append("choices_non_distincts")
        elif len(set(choices_str)) != len(choices_str):
            reasons.append("choices_non_distincts")
    else:
        if len(set(choices_str)) != len(choices_str):
            reasons.append("choices_non_distincts")

    if ca and choices_str:
        if et in _NUMERIC_EXERCISE_TYPES:
            if not _numeric_answer_in_choices(ca, choices_str):
                reasons.append("correct_answer_absente_des_choix")
        elif ca not in choices_str:
            reasons.append("correct_answer_absente_des_choix")

    return (len(reasons) == 0, reasons)


def format_validation_error_message(reasons: List[str]) -> str:
    """Message utilisateur court ; détail technique reste en logs."""
    if not reasons:
        return "Validation échouée."
    # Première cause la plus parlante pour l’apprenant
    friendly = {
        "correct_answer_absente_des_choix": (
            "La réponse correcte ne figure pas parmi les choix proposés. "
            "Génération refusée pour éviter une question piège."
        ),
        "choices_non_distincts": "Les choix ne sont pas tous distincts.",
        "choices_doit_contenir_4_elements": "Il faut exactement quatre choix de réponse.",
    }
    first = reasons[0]
    return friendly.get(
        first,
        "Le contenu généré ne respecte pas les contrôles de qualité. Réessayez plus tard.",
    )

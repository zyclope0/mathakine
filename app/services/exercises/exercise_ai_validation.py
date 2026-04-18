"""
Validation métier post-génération pour le flux exercices IA (SSE OpenAI).

Objectif : refuser de persister un contenu structurellement valide mais pédagogiquement
inutilisable (choix incohérents, bonne réponse absente, champs vides).

Limites assumées : pas de preuve mathématique formelle ; heuristiques explicites uniquement.

GAP-4 — vérification arithmétique conservative (stdlib uniquement) :
  Principe fail-open : on ne rejette que les cas prouvables mécaniquement.
  Si la question est un problème texte, si l'expression est ambiguë ou si le parsing
  échoue, on laisse passer (None). On rejette seulement quand :
    1. le type est l'un des 4 types numériques purs (ADDITION, SOUSTRACTION,
       MULTIPLICATION, DIVISION) ;
    2. la regex extrait exactement UNE expression binaire dans la question
       (0 match = pas d'expression, 2+ = ambiguïté → skip dans les deux cas) ;
    3. les deux opérandes ET la réponse se parsent en flottant strict ;
    4. le résultat calculé diffère de correct_answer au-delà de la tolérance numérique.
"""

from __future__ import annotations

import logging
import math
import operator as _op
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

_logger = logging.getLogger(__name__)

# Types pour lesquels on exige des choix / réponse correcte interprétables comme nombres.
_NUMERIC_EXERCISE_TYPES = frozenset(
    {"addition", "soustraction", "multiplication", "division"}
)

# ---------------------------------------------------------------------------
# GAP-4 — vérification arithmétique
# ---------------------------------------------------------------------------

# Opérateurs reconnus → fonction Python. Tiret typographique (−) inclus.
_ARITH_OP_MAP: Dict[str, Any] = {
    "+": _op.add,
    "−": _op.sub,  # U+2212 tiret typographique
    "-": _op.sub,
    "×": _op.mul,
    "*": _op.mul,
    "÷": _op.truediv,
    "/": _op.truediv,
}

# Capture : <nombre gauche> <opérateur> <nombre droit>
# Borné : chaque opérande ≤ 6 chiffres/espaces (évite de capturer des phrases longues).
# Symboles opérateurs exacts uniquement (pas de lettres comme "x" pour éviter confusion).
_ARITH_RE = re.compile(
    r"(\d[\d\s]{0,6}(?:[,\.]\d+)?)"  # opérande gauche
    r"\s*([+\-−×÷/\*])\s*"            # opérateur
    r"(\d[\d\s]{0,6}(?:[,\.]\d+)?)",  # opérande droit
)

# Format strict d'un nombre après nettoyage des séparateurs milliers et virgule décimale.
_STRICT_NUMBER_RE = re.compile(r"^\d+(?:\.\d+)?$")


def _parse_float_strict(token: str) -> Optional[float]:
    """
    Parse un nombre depuis une chaîne, en acceptant :
      - entiers : "123"
      - virgule décimale : "3,5" → 3.5
      - espace de milliers : "1 234" → 1234
      - combiné : "1 234,5" → 1234.5

    Rejette tout token contenant des lettres ou des formats ambigus.
    Retourne None si le parsing échoue.
    """
    t = token.strip()
    # Supprimer les espaces entre chiffres (séparateur milliers)
    t = re.sub(r"(\d)\s(\d)", r"\1\2", t)
    # Virgule décimale → point
    t = t.replace(",", ".")
    # Format strict : uniquement chiffres + point décimal optionnel
    if not _STRICT_NUMBER_RE.match(t):
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _normalize_latex_operators(text: str) -> str:
    """
    Normalise les opérateurs LaTeX vers leurs équivalents Unicode reconnus par _ARITH_RE.

    Transformations :
      \\times → ×  (U+00D7)
      \\div   → ÷  (U+00F7)
      $...$   → contenu interne (supprime les délimiteurs math LaTeX)

    Appelée au début de _try_verify_arithmetic pour couvrir le chemin nominal
    du générateur IA, qui formate les questions avec du LaTeX (ex : "Calcule $3 \\times 4$").
    """
    t = text.replace("\\times", "×").replace("\\div", "÷")
    # Supprime les délimiteurs $...$ en conservant le contenu
    t = re.sub(r"\$([^$]+)\$", r"\1", t)
    return t


def _try_verify_arithmetic(question: str, correct_answer: str) -> Optional[str]:
    """
    Vérifie arithmétiquement la réponse si la question contient une expression
    binaire non ambiguë.

    Normalise d'abord les opérateurs LaTeX (\\times, \\div, délimiteurs $)
    pour couvrir le chemin nominal du générateur IA.

    Retourne None (pas d'erreur) si :
      - aucune expression trouvée dans la question ;
      - plusieurs expressions trouvées (ambiguïté) ;
      - parsing d'un opérande ou de la réponse impossible ;
      - division par zéro.

    Retourne un message d'erreur compact si l'expression est trouvée, parsée
    correctement, et que le résultat calculé ≠ correct_answer (tolérance 1e-6 rel,
    1e-9 abs).

    Ce message est destiné aux logs internes uniquement (non affiché à l'utilisateur).
    """
    normalized = _normalize_latex_operators(question)
    matches = _ARITH_RE.findall(normalized)
    if len(matches) != 1:
        # 0 = pas d'expression simple ; 2+ = ambiguïté → fail-open
        return None

    a_str, op_sym, b_str = matches[0]

    a = _parse_float_strict(a_str)
    b = _parse_float_strict(b_str)
    ca = _parse_float_strict(correct_answer)

    if a is None or b is None or ca is None:
        return None

    op_fn = _ARITH_OP_MAP.get(op_sym.strip())
    if op_fn is None:
        return None

    try:
        expected = op_fn(a, b)
    except ZeroDivisionError:
        return None

    if not math.isclose(expected, ca, rel_tol=1e-6, abs_tol=1e-9):
        return (
            f"arithmetic_mismatch: {a_str.strip()} {op_sym} {b_str.strip()}"
            f" = {expected:.10g} != correct_answer={ca}"
        )

    return None

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

    # GAP-4 — vérification arithmétique conservative (types numériques purs uniquement)
    if et in _NUMERIC_EXERCISE_TYPES and ca:
        arith_error = _try_verify_arithmetic(q, ca)
        if arith_error is not None:
            reasons.append("correct_answer_arithmetiquement_fausse")
            # Détail technique en log (non exposé à l'utilisateur final)
            _logger.warning(
                "[ExerciseAIValidation] GAP-4 arithmetic check failed: %s", arith_error
            )

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
        "correct_answer_arithmetiquement_fausse": (
            "La réponse annoncée ne correspond pas au résultat du calcul. "
            "Génération refusée pour garantir l'exactitude pédagogique."
        ),
    }
    first = reasons[0]
    return friendly.get(
        first,
        "Le contenu généré ne respecte pas les contrôles de qualité. Réessayez plus tard.",
    )

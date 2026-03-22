"""
Équivalence de réponses pour la correction d'exercices (hors TEXTE/MIXTE).

Objectif pédagogique : accepter des formes équivalentes courantes (pourcentage, virgule
décimale FR, fraction vs décimal) sans élargir abusivement (ex. 0100 ≠ 100, 0.50 ≠ 0.5).

La comparaison stricte (strip) est tentée en premier par l'appelant ; ce module ne gère
que les écarts « tolérés » explicitement.
"""

from __future__ import annotations

import math
import re
from typing import Optional

# Réponse entièrement fractionnaire « simple » (évite d'interpréter des dates ou du texte).
_FRACTION_ONLY = re.compile(r"^\s*(-?\d+(?:[.,]\d+)?)\s*/\s*(-?\d+(?:[.,]\d+)?)\s*$")


def _strip_outer_percent(symbol: str) -> str:
    """Retire un suffixe % éventuel (ex. « 45 % », « 45% » -> « 45 »)."""
    s = symbol.strip()
    return re.sub(r"\s*%\s*$", "", s).strip()


def _comma_to_dot(s: str) -> str:
    return s.strip().replace(",", ".")


def _parse_fraction_or_float(token: str) -> Optional[float]:
    """
    Interprète une fraction simple « a/b » ou un flottant (virgule ou point).
    Retourne None si non parsable ou division par zéro.
    """
    t = token.strip()
    if not t:
        return None
    m = _FRACTION_ONLY.match(t)
    if m:
        try:
            a = float(_comma_to_dot(m.group(1)))
            b = float(_comma_to_dot(m.group(2)))
        except ValueError:
            return None
        if b == 0.0:
            return None
        return a / b
    try:
        return float(_comma_to_dot(t))
    except ValueError:
        return None


def _percent_tolerance_equivalent(selected: str, correct: str) -> bool:
    """
    True si l'une des réponses comporte % et la valeur numérique coincide apres retrait du %.

    Ex. « 45% » / « 45 » / « 45 % » ; « 12,5% » vs « 12.5 » via combinaison avec virgules.
    """
    s_raw = selected.strip()
    c_raw = correct.strip()
    if "%" not in s_raw and "%" not in c_raw:
        return False
    s = _strip_outer_percent(s_raw)
    c = _strip_outer_percent(c_raw)
    if s == c:
        return True
    return _comma_decimal_string_equivalent(s, c)


def _comma_decimal_string_equivalent(selected: str, correct: str) -> bool:
    """« 3,5 » et « 3.5 » apres normalisation unique des virgules."""
    if not selected.strip() or not correct.strip():
        return False
    return _comma_to_dot(selected) == _comma_to_dot(correct)


def _fraction_float_equivalent(selected: str, correct: str) -> bool:
    """
    Équivalence fraction / décimal / autre fraction (meme valeur réelle).

    Déclenché seulement si au moins une réponse contient « / » (forme fractionnaire).
    """
    s_raw = selected.strip()
    c_raw = correct.strip()
    if "/" not in s_raw and "/" not in c_raw:
        return False
    fs = _parse_fraction_or_float(s_raw)
    fc = _parse_fraction_or_float(c_raw)
    if fs is None or fc is None:
        return False
    return math.isclose(fs, fc, rel_tol=0.0, abs_tol=1e-9)


def answers_equivalent_numeric_tolerant(selected: str, correct: str) -> bool:
    """
    Règles de tolerance supplementaires (apres echec de l'egalite stricte strip).

    Ordre : pourcentage, separateur decimal, fraction/decimale equivalente.
    """
    if not correct.strip():
        return False
    if _percent_tolerance_equivalent(selected, correct):
        return True
    if _comma_decimal_string_equivalent(selected, correct):
        return True
    if _fraction_float_equivalent(selected, correct):
        return True
    return False

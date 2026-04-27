"""Utilities for ordered challenge payloads.

Shared by challenge validators **and** renderers to avoid divergent
interpretations of ``visual_data.pieces`` / ``items`` / ``shapes`` /
``correct_answer``.

``item_label(raw, fields=...)`` est la fonction centrale : elle extrait un
libellé **affichable** depuis un élément quelconque produit par le LLM, et
**refuse de produire une repr Python** (``"{'id': ...}"``) — cause
historique des leaks dans l'UI.

Contrat :
- string → trim.
- numeric → repr canonique.
- dict → premier champ textuel dans l'ordre officiel
  ``label → value → name → text → description → id → piece_id → tag``
  (override via ``fields``). Fail-open ``""`` si rien de reconnu.
- string ressemblant à ``"{'name': '...'}"`` ou ``'{"name": "..."}"`` → on
  tente de réextraire la valeur via ``_parse_python_dict_like_label_str``.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Iterable, List, Optional

_ANSWER_PART_SEPARATOR_RE = re.compile(r"\s*(?:,|;|\n)\s*")
_NUMERIC_TOKEN_RE = re.compile(r"^[+-]?\d+(?:[.,]\d+)?$")

# --- Canonical math-token normalization ---------------------------------
#
# LLMs frequently mix LaTeX (``\ln(x)``, ``\sqrt{x}``, ``x^2``) in
# ``visual_data.pieces`` and Unicode (``ln(x)``, ``√x``, ``x²``) in
# ``correct_answer`` for the same item. A naive ``set(pieces) - set(answer)``
# raised false positives like ``"Puzzle: éléments manquants dans
# correct_answer: {'\\ln(x)', 'e^x', '\\sqrt{x}', ...}"`` (Sentry 115344051)
# even though every piece was actually present.
#
# ``canonical_token`` produces a representation-agnostic key for set/equality
# matching only — it MUST NOT be used as a display label.

_UNICODE_SUPERSCRIPTS: Dict[str, str] = {
    "⁰": "^0",
    "¹": "^1",
    "²": "^2",
    "³": "^3",
    "⁴": "^4",
    "⁵": "^5",
    "⁶": "^6",
    "⁷": "^7",
    "⁸": "^8",
    "⁹": "^9",
    "⁺": "^+",
    "⁻": "^-",
    "⁼": "^=",
    "⁽": "^(",
    "⁾": "^)",
    "ⁿ": "^n",
    "ⁱ": "^i",
    "ˣ": "^x",
    "ʸ": "^y",
    "ᵃ": "^a",
    "ᵇ": "^b",
    "ᶜ": "^c",
    "ᵈ": "^d",
    "ᵉ": "^e",
    "ᵏ": "^k",
}

_UNICODE_SUBSCRIPTS: Dict[str, str] = {
    "₀": "_0",
    "₁": "_1",
    "₂": "_2",
    "₃": "_3",
    "₄": "_4",
    "₅": "_5",
    "₆": "_6",
    "₇": "_7",
    "₈": "_8",
    "₉": "_9",
    "ₙ": "_n",
    "ᵢ": "_i",
    "ₓ": "_x",
}

_UNICODE_MATH_OPS: Dict[str, str] = {
    "√": "sqrt",
    "×": "*",
    "·": "*",
    "÷": "/",
    "−": "-",  # Unicode minus
    "≤": "<=",
    "≥": ">=",
    "≠": "!=",
    "≈": "~",
    "∞": "inf",
    "π": "pi",
    "θ": "theta",
    "α": "alpha",
    "β": "beta",
    "γ": "gamma",
}

_LATEX_KEEP_CHARS = re.compile(r"[\\{}()\[\]\s]+")


def canonical_token(text: Any) -> str:
    """Representation-agnostic canonical key for set/equality matching.

    Idempotent. Designed to make LaTeX (``\\ln(x)``, ``\\sqrt{x}``, ``x^2``)
    and Unicode (``ln(x)``, ``√x``, ``x²``, ``eˣ``) variants of the same item
    collapse to the same key. Also folds NFKC-equivalent accents.

    Strips backslashes, braces, parentheses, brackets and whitespace so that
    ``\\sqrt{x}``, ``sqrt(x)``, ``√x`` all collapse to ``sqrtx``.

    NEVER use as a display label — it is lossy by design.
    """
    if text is None:
        return ""
    s = str(text)
    if not s:
        return ""
    # IMPORTANT : mapper super/subscripts AVANT NFKC. NFKC applique la
    # décomposition de compatibilité et fait disparaître l'information
    # « exposant » (ex. ``ˣ`` U+02E3 → ``x``, ``²`` U+00B2 → ``2``), ce
    # qui rendrait ``eˣ`` indistinct de ``ex`` après normalisation.
    for src, dst in _UNICODE_SUPERSCRIPTS.items():
        if src in s:
            s = s.replace(src, dst)
    for src, dst in _UNICODE_SUBSCRIPTS.items():
        if src in s:
            s = s.replace(src, dst)
    s = unicodedata.normalize("NFKC", s)
    s = s.lower()
    for src, dst in _UNICODE_MATH_OPS.items():
        if src in s:
            s = s.replace(src, dst)
    s = _LATEX_KEEP_CHARS.sub("", s)
    return s


def canonical_piece_key(piece: Any) -> str:
    """``piece_order_key`` + ``canonical_token`` for matching against answers."""
    return canonical_token(piece_order_key(piece))


DEFAULT_ITEM_LABEL_FIELDS: tuple = (
    "label",
    "value",
    "name",
    "text",
    "description",
    "id",
    "piece_id",
    "tag",
)

_PY_DICT_LABEL_FIELD_RE = re.compile(
    r"""['"](?P<field>name|label|value|text|description|id|piece_id|tag)['"]\s*:\s*['"](?P<val>[^'"]*)['"]""",
    re.IGNORECASE,
)


def _parse_python_dict_like_label_str(text: str) -> Optional[str]:
    """Extrait un libellé depuis une chaîne style ``"{'name': 'cercle rouge'}"``.

    Retourne ``None`` si la chaîne n'a pas la forme d'une repr dict
    (fail-open sur les vraies chaînes de forme comme ``"cercle rouge"``).
    """
    s = text.strip()
    if not (s.startswith("{") and s.endswith("}")):
        return None
    fields: Dict[str, str] = {}
    for m in _PY_DICT_LABEL_FIELD_RE.finditer(s):
        fields.setdefault(m.group("field").lower(), m.group("val").strip())
    if not fields:
        return None
    for k in DEFAULT_ITEM_LABEL_FIELDS:
        v = fields.get(k)
        if v:
            return v
    return None


def item_label(
    raw: Any,
    fields: Optional[Iterable[str]] = None,
    *,
    fallback: str = "",
) -> str:
    """Libellé affichable pour un élément arbitraire de ``visual_data``.

    Ne produit **jamais** la repr Python d'un dict — fail-open ``fallback``
    (vide par défaut).
    """
    if raw is None:
        return fallback
    if isinstance(raw, bool):
        return fallback
    if isinstance(raw, (int, float)):
        return str(raw)
    keys = tuple(fields) if fields is not None else DEFAULT_ITEM_LABEL_FIELDS
    if isinstance(raw, dict):
        for key in keys:
            v = raw.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return str(v)
        return fallback
    if isinstance(raw, str):
        parsed = _parse_python_dict_like_label_str(raw)
        if parsed is not None:
            return parsed
        return raw.strip()
    # Autres types (list/tuple/set) : pas d'étiquette affichable stable ;
    # jamais de ``str(x)`` silencieux qui leak.
    return fallback


_PIECE_LABEL_FIELDS: tuple = ("label", "value", "name", "id", "piece_id", "tag")
_PIECE_ORDER_KEY_FIELDS: tuple = ("id", "piece_id", "label", "value", "name", "tag")


def piece_label(piece: Any) -> str:
    """Label d'une pièce de puzzle — alias orienté puzzle d'``item_label``.

    Conservé pour stabilité des imports publics. Préfère ``item_label`` pour
    tout nouveau code générique.
    """
    return item_label(piece, fields=_PIECE_LABEL_FIELDS)


def piece_order_key(piece: Any) -> str:
    """Stable ordering key for puzzle answers."""
    return item_label(piece, fields=_PIECE_ORDER_KEY_FIELDS)


def split_ordered_answer_parts(answer: Any) -> List[str]:
    """Split an ordered answer while preserving each item as a trimmed string."""
    if isinstance(answer, list):
        return [str(part).strip() for part in answer if str(part).strip()]
    text = str(answer or "").strip()
    if not text:
        return []
    return [
        part.strip() for part in _ANSWER_PART_SEPARATOR_RE.split(text) if part.strip()
    ]


def parse_numeric_token(token: str) -> Optional[float]:
    """Parse a standalone numeric token, fail-closed for mixed labels."""
    compact = str(token).strip().replace(" ", "")
    if not _NUMERIC_TOKEN_RE.fullmatch(compact):
        return None
    try:
        return float(compact.replace(",", "."))
    except ValueError:
        return None


def parse_numeric_order(tokens: List[str]) -> Optional[List[float]]:
    """Return numeric values only when every token is a standalone number."""
    values = [parse_numeric_token(token) for token in tokens]
    if any(value is None for value in values):
        return None
    return [float(value) for value in values if value is not None]


def is_numeric_sort_solution(pieces: Any, correct_answer: Any) -> bool:
    """True when a numeric puzzle solution is exactly ascending or descending sort."""
    if not isinstance(pieces, list) or len(pieces) < 3:
        return False

    piece_numbers = parse_numeric_order([piece_label(piece) for piece in pieces])
    answer_numbers = parse_numeric_order(split_ordered_answer_parts(correct_answer))
    if piece_numbers is None or answer_numbers is None:
        return False
    if len(piece_numbers) != len(answer_numbers):
        return False

    ascending = sorted(piece_numbers)
    descending = list(reversed(ascending))
    return answer_numbers == ascending or answer_numbers == descending

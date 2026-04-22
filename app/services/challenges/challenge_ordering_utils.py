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
from typing import Any, Dict, Iterable, List, Optional

_ANSWER_PART_SEPARATOR_RE = re.compile(r"\s*(?:,|;|\n)\s*")
_NUMERIC_TOKEN_RE = re.compile(r"^[+-]?\d+(?:[.,]\d+)?$")

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


def piece_label(piece: Any) -> str:
    """Label d'une pièce de puzzle — alias orienté puzzle d'``item_label``.

    Conservé pour stabilité des imports publics. Préfère ``item_label`` pour
    tout nouveau code générique.
    """
    return item_label(piece, fields=_PIECE_LABEL_FIELDS)


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

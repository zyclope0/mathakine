"""Utilities for ordered challenge payloads.

Shared by challenge validators to avoid divergent interpretations of
``visual_data.pieces`` / ``correct_answer``.
"""

from __future__ import annotations

import re
from typing import Any, List, Optional

_ANSWER_PART_SEPARATOR_RE = re.compile(r"\s*(?:,|;|\n)\s*")
_NUMERIC_TOKEN_RE = re.compile(r"^[+-]?\d+(?:[.,]\d+)?$")


def piece_label(piece: Any) -> str:
    """Return the learner-visible label for one puzzle piece."""
    if isinstance(piece, dict):
        value = piece.get("label") or piece.get("value") or piece.get("name") or piece
    else:
        value = piece
    return str(value).strip()


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

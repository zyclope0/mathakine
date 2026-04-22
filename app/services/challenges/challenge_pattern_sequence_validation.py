"""
Validateurs PATTERN et SEQUENCE pour la validation des challenges.
Extrait de challenge_validator.py (B3.7) - famille pattern/sequence.

Reutilise les analyzers de challenge_validation_analysis (B3.6).
"""

import math
import re
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

from app.services.challenges.challenge_validation_analysis import (
    analyze_pattern,
    analyze_sequence,
    compute_pattern_answers_multi,
    find_question_position_in_grid,
)

_STRICT_NUMERIC_PATTERN_RE = re.compile(r"^[+-]?\d+(?:[,.]\d+)?$")
_NUMERIC_TOLERANCE = 1e-9


def _count_question_cells(grid: List[List[Any]]) -> int:
    count = 0
    for row in grid:
        if not isinstance(row, (list, tuple)):
            continue
        for cell in row:
            if cell == "?" or (isinstance(cell, str) and "?" in str(cell)):
                count += 1
    return count


def _looks_numeric_pattern_grid(grid: List[List[Any]]) -> bool:
    numeric_count = 0
    non_empty_count = 0
    for row in grid:
        if not isinstance(row, (list, tuple)):
            continue
        for cell in row:
            text = str(cell).strip()
            if not text or "?" in text:
                continue
            non_empty_count += 1
            if not _STRICT_NUMERIC_PATTERN_RE.fullmatch(text):
                continue
            numeric_count += 1
    return non_empty_count > 0 and numeric_count == non_empty_count


def _parse_numeric_pattern_cell(cell: Any) -> Optional[float]:
    if cell == "?" or (isinstance(cell, str) and "?" in str(cell)):
        return None
    text = str(cell).strip()
    if not text or not _STRICT_NUMERIC_PATTERN_RE.fullmatch(text):
        return None
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def _format_numeric_pattern_value(value: float) -> str:
    rounded = round(value)
    if math.isclose(value, rounded, rel_tol=0.0, abs_tol=_NUMERIC_TOLERANCE):
        return str(int(rounded))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _split_multi_answer_parts(correct_answer: str) -> List[str]:
    return [p.strip() for p in str(correct_answer).split(",") if p.strip()]


def _validate_unverified_multi_answer_shape(
    correct_answer: str, question_count: int, numeric_grid: bool
) -> List[str]:
    parts = _split_multi_answer_parts(correct_answer)
    if len(parts) != question_count:
        return [
            "Pattern multi-cellules non verifiable: "
            f"correct_answer doit contenir {question_count} valeurs separees par des virgules"
        ]

    if numeric_grid and any(
        not _STRICT_NUMERIC_PATTERN_RE.fullmatch(part) for part in parts
    ):
        return [
            "Pattern numerique multi-cellules non verifiable: "
            "correct_answer doit contenir uniquement des valeurs numeriques"
        ]

    return []


def _candidate_from_arithmetic_line(
    known_points: List[Tuple[int, float]],
    missing_indices: List[int],
) -> Optional[Dict[int, float]]:
    if len(known_points) < 3:
        return None
    (idx_a, value_a), (idx_b, value_b) = known_points[0], known_points[1]
    distance = idx_b - idx_a
    if distance == 0:
        return None
    step = (value_b - value_a) / distance
    for idx, value in known_points[2:]:
        expected = value_a + step * (idx - idx_a)
        if not math.isclose(value, expected, rel_tol=0.0, abs_tol=_NUMERIC_TOLERANCE):
            return None
    return {idx: value_a + step * (idx - idx_a) for idx in missing_indices}


def _candidate_from_geometric_line(
    known_points: List[Tuple[int, float]],
    missing_indices: List[int],
) -> Optional[Dict[int, float]]:
    if len(known_points) < 3:
        return None
    if any(value == 0 for _, value in known_points):
        return None
    if any(
        right_idx - left_idx != 1
        for (left_idx, _), (right_idx, _) in zip(known_points, known_points[1:])
    ):
        # Fractional exponents across gaps would make this too permissive.
        return None
    (_, first_value), (_, second_value) = known_points[0], known_points[1]
    ratio = second_value / first_value
    for (_, left_value), (_, right_value) in zip(known_points, known_points[1:]):
        expected = left_value * ratio
        if not math.isclose(
            right_value, expected, rel_tol=0.0, abs_tol=_NUMERIC_TOLERANCE
        ):
            return None
    first_idx, first_value = known_points[0]
    return {idx: first_value * (ratio ** (idx - first_idx)) for idx in missing_indices}


def _has_known_second_difference_evidence(
    numeric_values: List[Optional[float]],
) -> bool:
    adjacent_known_intervals = 0
    for idx in range(len(numeric_values) - 1):
        if numeric_values[idx] is not None and numeric_values[idx + 1] is not None:
            adjacent_known_intervals += 1
    for idx in range(len(numeric_values) - 2):
        if (
            numeric_values[idx] is not None
            and numeric_values[idx + 1] is not None
            and numeric_values[idx + 2] is not None
        ):
            return True
    return adjacent_known_intervals >= 2


def _candidate_from_quadratic_line(
    numeric_values: List[Optional[float]],
    known_points: List[Tuple[int, float]],
    missing_indices: List[int],
) -> Optional[Dict[int, float]]:
    # Constant second difference is useful for staircase numeric patterns, but
    # only if the line already exposes two adjacent known intervals.
    if len(known_points) < 3 or not _has_known_second_difference_evidence(
        numeric_values
    ):
        return None

    def evaluate(points: Tuple[Tuple[int, float], ...], x: int) -> float:
        total = 0.0
        for point_idx, (x_i, y_i) in enumerate(points):
            basis = 1.0
            for other_idx, (x_j, _) in enumerate(points):
                if point_idx == other_idx:
                    continue
                basis *= (x - x_j) / (x_i - x_j)
            total += y_i * basis
        return total

    candidates: List[Dict[int, float]] = []
    for points in combinations(known_points, 3):
        if len({idx for idx, _ in points}) != 3:
            continue
        if all(
            math.isclose(
                value,
                evaluate(points, idx),
                rel_tol=0.0,
                abs_tol=_NUMERIC_TOLERANCE,
            )
            for idx, value in known_points
        ):
            candidates.append({idx: evaluate(points, idx) for idx in missing_indices})

    return _merge_numeric_candidates(candidates)


def _merge_numeric_candidates(
    candidates: List[Dict[int, float]],
) -> Optional[Dict[int, float]]:
    if not candidates:
        return None
    merged = dict(candidates[0])
    for candidate in candidates[1:]:
        if set(candidate) != set(merged):
            return None
        for idx, value in candidate.items():
            if not math.isclose(
                merged[idx], value, rel_tol=0.0, abs_tol=_NUMERIC_TOLERANCE
            ):
                return None
    return merged


def _infer_numeric_line_missing_values(line: List[Any]) -> Optional[Dict[int, float]]:
    numeric_values = [_parse_numeric_pattern_cell(cell) for cell in line]
    missing_indices = [
        idx
        for idx, cell in enumerate(line)
        if cell == "?" or (isinstance(cell, str) and "?" in str(cell))
    ]
    if not missing_indices:
        return {}
    if any(
        value is None and idx not in missing_indices
        for idx, value in enumerate(numeric_values)
    ):
        return None
    known_points = [
        (idx, value) for idx, value in enumerate(numeric_values) if value is not None
    ]
    candidates = [
        candidate
        for candidate in (
            _candidate_from_arithmetic_line(known_points, missing_indices),
            _candidate_from_geometric_line(known_points, missing_indices),
            _candidate_from_quadratic_line(
                numeric_values, known_points, missing_indices
            ),
        )
        if candidate is not None
    ]
    return _merge_numeric_candidates(candidates)


def _compute_numeric_pattern_answers_multi(grid: List[List[Any]]) -> Optional[str]:
    positions: List[Tuple[int, int]] = []
    for row_idx, row in enumerate(grid):
        if not isinstance(row, list):
            return None
        for col_idx, cell in enumerate(row):
            if cell == "?" or (isinstance(cell, str) and "?" in str(cell)):
                positions.append((row_idx, col_idx))
    if not positions:
        return None

    answers: Dict[Tuple[int, int], float] = {}
    for row_idx, row in enumerate(grid):
        if not any((row_idx, col_idx) in positions for col_idx in range(len(row))):
            continue
        row_answers = _infer_numeric_line_missing_values(row)
        if row_answers is None:
            continue
        for col_idx, value in row_answers.items():
            answers[(row_idx, col_idx)] = value

    if len(answers) != len(positions):
        return None
    return ", ".join(
        _format_numeric_pattern_value(answers[position])
        for position in sorted(positions)
    )


def validate_pattern_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide un challenge de type PATTERN.
    Verifie que la reponse correspond au pattern dans la grille.
    """
    del explanation  # interface partagee avec les autres validateurs
    errors: List[str] = []

    if not visual_data or "grid" not in visual_data:
        errors.append("visual_data.grid manquant pour un challenge PATTERN")
        return errors

    grid = visual_data.get("grid", [])
    if not grid or not isinstance(grid, list):
        errors.append("visual_data.grid doit etre un tableau")
        return errors

    question_count = _count_question_cells(grid)

    # Plusieurs "?" -> format "O, O, X, O"
    if question_count > 1:
        numeric_grid = _looks_numeric_pattern_grid(grid)
        if numeric_grid:
            expected_multi = _compute_numeric_pattern_answers_multi(grid)
            if not expected_multi:
                errors.extend(
                    _validate_unverified_multi_answer_shape(
                        correct_answer, question_count, numeric_grid
                    )
                )
                return errors
        else:
            expected_multi = compute_pattern_answers_multi(grid)
            if not expected_multi:
                errors.extend(
                    _validate_unverified_multi_answer_shape(
                        correct_answer, question_count, numeric_grid
                    )
                )
                return errors
        if expected_multi:
            correct_parts = [
                p.strip().upper() for p in str(correct_answer).split(",") if p.strip()
            ]
            expected_parts = [
                p.strip().upper() for p in expected_multi.split(",") if p.strip()
            ]
            if (
                len(correct_parts) != len(expected_parts)
                or correct_parts != expected_parts
            ):
                errors.append(
                    f"Pattern multi-cellules incoherent: attendu '{expected_multi}', "
                    f"correct_answer='{correct_answer}'"
                )
        return errors

    # Une seule "?"
    question_pos = find_question_position_in_grid(grid)
    if not question_pos:
        return errors
    row_idx, col_idx = question_pos
    expected_answer = analyze_pattern(grid, row_idx, col_idx)
    if expected_answer:
        correct_normalized = str(correct_answer).strip().upper()
        expected_normalized = str(expected_answer).strip().upper()
        if correct_normalized != expected_normalized:
            errors.append(
                f"Pattern incoherent: le pattern suggere '{expected_answer}', "
                f"mais correct_answer est '{correct_answer}'"
            )

    return errors


def validate_sequence_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide un challenge de type SEQUENCE.
    Verifie que la reponse correspond a la sequence logique.
    """
    del explanation  # interface partagee avec les autres validateurs
    errors: List[str] = []

    if not visual_data or "sequence" not in visual_data:
        # Sequence peut etre dans visual_data ou directement dans la question
        return errors

    sequence = visual_data.get("sequence", [])
    if not sequence or not isinstance(sequence, list):
        return errors

    # Analyser la sequence pour determiner le prochain element
    expected = analyze_sequence(sequence)

    if expected is not None:
        correct_normalized = str(correct_answer).strip()
        expected_normalized = str(expected).strip()

        if correct_normalized != expected_normalized:
            errors.append(
                f"Sequence incoherente: la sequence {sequence} suggere '{expected}', "
                f"mais correct_answer est '{correct_answer}'"
            )

    return errors

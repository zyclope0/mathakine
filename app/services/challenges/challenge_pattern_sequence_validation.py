"""
Validateurs PATTERN et SEQUENCE pour la validation des challenges.
Extrait de challenge_validator.py (B3.7) - famille pattern/sequence.

Reutilise les analyzers de challenge_validation_analysis (B3.6).
"""

from typing import Any, Dict, List

from app.services.challenges.challenge_validation_analysis import (
    analyze_pattern,
    analyze_sequence,
    compute_pattern_answers_multi,
    find_question_position_in_grid,
)


def _count_question_cells(grid: List[List[Any]]) -> int:
    count = 0
    for row in grid:
        if not isinstance(row, (list, tuple)):
            continue
        for cell in row:
            if cell == "?" or (isinstance(cell, str) and "?" in str(cell)):
                count += 1
    return count


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
        expected_multi = compute_pattern_answers_multi(grid)
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

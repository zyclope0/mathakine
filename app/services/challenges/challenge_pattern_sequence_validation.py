"""
Validateurs PATTERN et SEQUENCE pour la validation des challenges.
Extrait de challenge_validator.py (B3.7) — famille pattern/sequence.

Réutilise les analyzers de challenge_validation_analysis (B3.6).
"""

from typing import Any, Dict, List

from app.services.challenges.challenge_validation_analysis import (
    analyze_pattern,
    analyze_sequence,
    compute_pattern_answers_multi,
    find_question_position_in_grid,
)


def validate_pattern_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide un challenge de type PATTERN.
    Vérifie que la réponse correspond au pattern dans la grille.
    """
    errors = []

    if not visual_data or "grid" not in visual_data:
        errors.append("visual_data.grid manquant pour un challenge PATTERN")
        return errors

    grid = visual_data.get("grid", [])
    if not grid or not isinstance(grid, list):
        errors.append("visual_data.grid doit être un tableau")
        return errors

    # Plusieurs "?" → format "O, O, X, O"
    expected_multi = compute_pattern_answers_multi(grid)
    if expected_multi:
        correct_parts = [
            p.strip().upper() for p in str(correct_answer).split(",") if p.strip()
        ]
        expected_parts = [
            p.strip().upper() for p in expected_multi.split(",") if p.strip()
        ]
        if len(correct_parts) != len(expected_parts) or correct_parts != expected_parts:
            errors.append(
                f"Pattern multi-cellules incohérent: attendu '{expected_multi}', "
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
                f"Pattern incohérent: le pattern suggère '{expected_answer}', "
                f"mais correct_answer est '{correct_answer}'"
            )

    return errors


def validate_sequence_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide un challenge de type SEQUENCE.
    Vérifie que la réponse correspond à la séquence logique.
    """
    errors = []

    if not visual_data or "sequence" not in visual_data:
        # Sequence peut être dans visual_data ou directement dans la question
        return errors

    sequence = visual_data.get("sequence", [])
    if not sequence or not isinstance(sequence, list):
        return errors

    # Analyser la séquence pour déterminer le prochain élément
    expected = analyze_sequence(sequence)

    if expected is not None:
        correct_normalized = str(correct_answer).strip()
        expected_normalized = str(expected).strip()

        if correct_normalized != expected_normalized:
            errors.append(
                f"Séquence incohérente: la séquence {sequence} suggère '{expected}', "
                f"mais correct_answer est '{correct_answer}'"
            )

    return errors

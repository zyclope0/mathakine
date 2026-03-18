"""
Tests pour app.services.challenge_validation_analysis.
Valident les analyzers de patterns et sequences utilises par la validation des challenges.
"""

import pytest

from app.services.challenges.challenge_validation_analysis import (
    analyze_latin_square_pattern,
    analyze_pattern,
    analyze_sequence,
    compute_pattern_answers_multi,
    find_question_position_in_grid,
)

# ── find_question_position_in_grid (E2) ─────────────────────────────────────


def test_find_question_position_in_grid_found():
    """Trouve la premiere position '?' dans la grille."""
    grid = [["X", "O", "X"], ["O", "?", "O"], ["X", "O", "X"]]
    assert find_question_position_in_grid(grid) == (1, 1)


def test_find_question_position_in_grid_not_found():
    """Retourne None si aucune '?'."""
    grid = [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "X"]]
    assert find_question_position_in_grid(grid) is None


def test_find_question_position_in_grid_cell_contains_question():
    """Detecte cellule contenant '?' (ex: '?')."""
    grid = [["a", "b"], ["c", "?"]]
    assert find_question_position_in_grid(grid) == (1, 1)


def test_find_question_position_in_grid_skips_non_list_rows():
    """Lignes non-list sont ignorees."""
    grid = [["X", "O"], "invalid", ["?", "X"]]
    assert find_question_position_in_grid(grid) == (2, 0)


# ── compute_pattern_answers_multi ──────────────────────────────────────────


def test_compute_pattern_answers_multi_no_question_marks():
    """Sans '?', retourne None."""
    grid = [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "X"]]
    assert compute_pattern_answers_multi(grid) is None


def test_compute_pattern_answers_multi_single_question():
    """Une seule '?' deduit le symbole manquant (latin square)."""
    grid = [
        ["triangle", "cercle", "carre"],
        ["cercle", "carre", "triangle"],
        ["carre", "cercle", "?"],
    ]
    result = compute_pattern_answers_multi(grid)
    assert result == "triangle"


def test_compute_pattern_answers_multi_multiple_questions():
    """Plusieurs '?' retournent la liste ordonnee si deducible."""
    grid = [
        ["X", "O", "?"],
        ["O", "X", "O"],
        ["?", "O", "X"],
    ]
    # Positions (0,2) et (2,0) : pattern X-O-X en ligne et colonne -> X pour les deux
    result = compute_pattern_answers_multi(grid)
    assert result == "X, X"


def test_compute_pattern_answers_multi_non_list_row_skipped():
    """Lignes non-list sont ignorees ; seule (0,2) resolue via pattern X-O-X -> X."""
    grid = [["X", "O", "?"], "invalid", ["O", "X", "O"]]
    result = compute_pattern_answers_multi(grid)
    assert result == "X"


# ── analyze_pattern ──────────────────────────────────────────────────────────


def test_analyze_pattern_empty_grid():
    """Grille vide ou invalide retourne None."""
    assert analyze_pattern([], 0, 0) is None
    assert analyze_pattern([[1]], 1, 0) is None
    assert analyze_pattern([[1]], 0, 1) is None


def test_analyze_pattern_latin_square():
    """Latin square : element manquant dans la ligne."""
    grid = [
        ["1", "2", "3"],
        ["2", "3", "1"],
        ["3", "?", "2"],
    ]
    assert analyze_pattern(grid, 2, 1) == "1"


def test_analyze_pattern_checkerboard_rows_0_2():
    """Damier : lignes 0 et 2 identiques, ? en (2,1)."""
    grid = [
        ["A", "B", "A"],
        ["B", "A", "B"],
        ["A", "?", "A"],
    ]
    assert analyze_pattern(grid, 2, 1) == "B"


def test_analyze_pattern_symmetry_horizontal():
    """Symetrie horizontale : ? = cellule miroir."""
    grid = [
        ["X", "O", "X"],
        ["O", "X", "O"],
        ["X", "O", "?"],
    ]
    # mirror de (2,2) = (0,0) = X
    assert analyze_pattern(grid, 2, 2) == "X"


def test_analyze_pattern_symmetry_vertical():
    """Symetrie verticale : ? = cellule miroir en colonne."""
    grid = [
        ["X", "O", "?"],
        ["O", "X", "O"],
        ["X", "O", "X"],
    ]
    # mirror col 2 = col 0, row 0 = X
    assert analyze_pattern(grid, 0, 2) == "X"


def test_analyze_pattern_row_x_o_x():
    """Pattern X-O-X en ligne, col 2 = X."""
    grid = [["X", "O", "?"]]
    assert analyze_pattern(grid, 0, 2) == "X"


def test_analyze_pattern_row_o_x_o():
    """Pattern O-X-O en ligne, col 2 = O."""
    grid = [["O", "X", "?"]]
    assert analyze_pattern(grid, 0, 2) == "O"


def test_analyze_pattern_row_same_value():
    """Ligne avec meme valeur repetee."""
    grid = [["X", "X", "?"]]
    assert analyze_pattern(grid, 0, 2) == "X"


def test_analyze_pattern_col_x_o_x():
    """Pattern X-O-X en colonne."""
    grid = [["X"], ["O"], ["?"]]
    assert analyze_pattern(grid, 2, 0) == "X"


def test_analyze_pattern_diagonal_main_symmetry_wins():
    """Sur cette grille, la symetrie (mirror vertical) l'emporte sur l'heuristique diagonale."""
    grid = [
        ["X", "O", "O"],
        ["O", "O", "X"],
        ["O", "X", "?"],
    ]
    # (2,2) : mirror = (0,0) en colonne -> grid[0][2] = O (priorite symetrie avant diagonales)
    result = analyze_pattern(grid, 2, 2)
    assert result == "O"


def test_analyze_pattern_position_2_0_latin_square_col_wins():
    """
    Causalite reelle : latin square (colonne 0 manque X) gagne.
    Sur cette grille, ? en (2,0) : colonne 0 a [O,O,?], all_elements={O,X}, manque X.
    La diagonale secondaire n'est jamais atteinte (priorite 1 latin square).
    """
    grid = [
        ["O", "O", "X"],
        ["O", "X", "O"],
        ["?", "X", "O"],
    ]
    result = analyze_pattern(grid, 2, 0)
    assert result == "X"


# ── analyze_latin_square_pattern ─────────────────────────────────────────────


def test_analyze_latin_square_empty():
    """Grille vide retourne None."""
    assert analyze_latin_square_pattern([], 0, 0) is None
    assert analyze_latin_square_pattern("not a list", 0, 0) is None


def test_analyze_latin_square_few_elements():
    """Moins de 2 elements uniques retourne None."""
    assert analyze_latin_square_pattern([["?", "?"]], 0, 0) is None


def test_analyze_latin_square_missing_in_row():
    """Element manquant dans la ligne."""
    grid = [
        ["triangle", "cercle", "carre"],
        ["cercle", "carre", "triangle"],
        ["carre", "cercle", "?"],
    ]
    assert analyze_latin_square_pattern(grid, 2, 2) == "triangle"


def test_analyze_latin_square_missing_in_col():
    """Element manquant dans la colonne."""
    grid = [
        ["1", "2", "3"],
        ["2", "3", "?"],
        ["3", "1", "2"],
    ]
    assert analyze_latin_square_pattern(grid, 1, 2) == "1"


def test_analyze_latin_square_preserves_case():
    """Conserve la casse originale de l'element trouve."""
    grid = [
        ["Triangle", "Cercle", "Carre"],
        ["Cercle", "Carre", "Triangle"],
        ["Carre", "Cercle", "?"],
    ]
    result = analyze_latin_square_pattern(grid, 2, 2)
    assert result == "Triangle"


def test_analyze_latin_square_target_row_not_list():
    """Ligne cible non-list retourne None."""
    grid = [["a", "b"], "invalid", ["b", "?"]]
    assert analyze_latin_square_pattern(grid, 1, 1) is None


# ── analyze_sequence ─────────────────────────────────────────────────────────


def test_analyze_sequence_empty():
    """Sequence vide ou trop courte retourne None."""
    assert analyze_sequence([]) is None
    assert analyze_sequence([1]) is None


def test_analyze_sequence_arithmetic():
    """Sequence arithmetique simple."""
    assert analyze_sequence([1, 2, 3, 4]) == "5"
    assert analyze_sequence([10, 20, 30]) == "40"
    assert analyze_sequence([-1, 0, 1, 2]) == "3"


def test_analyze_sequence_arithmetic_second_order():
    """Sequence arithmetique second ordre (diffs +1)."""
    # 1, 2, 4, 7, 11 -> diffs 1,2,3,4 -> next diff 5, next num 16
    assert analyze_sequence([1, 2, 4, 7, 11]) == "16"


def test_analyze_sequence_geometric():
    """Sequence geometrique."""
    assert analyze_sequence([2, 4, 8, 16]) == "32"
    assert analyze_sequence([3, 9, 27]) == "81"


def test_analyze_sequence_non_numeric():
    """Sequence avec elements non numeriques retourne None."""
    assert analyze_sequence(["a", "b", "c"]) is None


def test_analyze_sequence_mixed_string_numbers():
    """Sequence mixte avec nombres en string."""
    assert analyze_sequence(["1", "2", "3", "4"]) == "5"


def test_analyze_sequence_second_order_before_geometric():
    """Sequence 1,2,4 : second ordre (diffs +1) prioritaire sur geometrique -> 7."""
    assert analyze_sequence([1, 2, 4]) == "7"

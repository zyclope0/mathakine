"""
Analyzers partagés pour la validation des challenges.
Extrait de challenge_validator.py (B3.6) — helpers utilisés par plusieurs validateurs
et par auto_correct_challenge.

Ne contient pas la logique de validation métier, uniquement l'analyse de patterns
et de séquences pour déduire les réponses attendues.
"""

from typing import Any, List, Optional, Tuple


def find_question_position_in_grid(grid: List[List[Any]]) -> Optional[Tuple[int, int]]:
    """
    Trouve la position (row, col) de la première cellule '?' dans une grille.
    Utilisé par validate_grid_in_visual, validate_pattern_challenge, auto_correct_challenge.

    Returns:
        (row_idx, col_idx) ou None si aucune cellule '?' trouvée.
    """
    for i, row in enumerate(grid):
        if not isinstance(row, list):
            continue
        for j, cell in enumerate(row):
            if cell == "?" or (isinstance(cell, str) and "?" in str(cell)):
                return (i, j)
    return None


def compute_pattern_answers_multi(grid: List[List[Any]]) -> Optional[str]:
    """
    Pour une grille PATTERN avec plusieurs "?", retourne la liste des symboles dans l'ordre
    (ligne par ligne, colonne par colonne). Format: "O, O, X, O"
    Retourne None si aucune "?" ou si on ne peut pas déduire tous les symboles.
    """
    positions = []
    for i, row in enumerate(grid):
        if not isinstance(row, (list, tuple)):
            continue
        for j, cell in enumerate(row):
            if cell == "?" or (isinstance(cell, str) and "?" in str(cell)):
                positions.append((i, j))
    if not positions:
        return None
    symbols = []
    for i, j in sorted(positions):
        s = analyze_pattern(grid, i, j)
        if not s:
            return None
        symbols.append(str(s).strip())
    return ", ".join(symbols)


def analyze_pattern(grid: List[List[Any]], row_idx: int, col_idx: int) -> Optional[str]:
    """
    Analyse un pattern dans une grille pour déterminer la réponse attendue.
    Supporte plusieurs types de patterns :
    - Symétrie (horizontale, verticale, centrale)
    - Latin square (chaque ligne/colonne contient chaque élément une seule fois)
    - Patterns alternés simples (X-O-X, etc.)
    - Patterns de répétition

    Args:
        grid: Grille 2D
        row_idx: Index de la ligne contenant '?'
        col_idx: Index de la colonne contenant '?'

    Returns:
        Réponse attendue ou None si le pattern ne peut pas être déterminé
    """
    if not grid or row_idx >= len(grid) or col_idx >= len(grid[0]):
        return None

    rows, cols = len(grid), len(grid[0])

    # 1. Latin Square d'abord : prioritaire car déterministe (chaque ligne/col contient chaque symbole une fois)
    latin_answer = analyze_latin_square_pattern(grid, row_idx, col_idx)
    if latin_answer:
        return latin_answer

    # 2. Damier (checkerboard) : lignes paires identiques (0=2), impaires (1=3)
    def _rows_match(r1: int, r2: int) -> bool:
        if r1 >= len(grid) or r2 >= len(grid):
            return False
        for j in range(len(grid[0])):
            a, b = str(grid[r1][j]).strip(), str(grid[r2][j]).strip()
            if a not in ("?", "") and b not in ("?", "") and a != b:
                return False
        return True

    if rows >= 3:
        if row_idx in (0, 2) and _rows_match(0, 2):
            ref_row = 0 if row_idx == 2 else 2
            ref_val = grid[ref_row][col_idx]
            if ref_val and str(ref_val).strip() not in ("?", ""):
                return str(ref_val).strip()
        if row_idx in (1, 3) and rows >= 4 and _rows_match(1, 3):
            ref_row = 1 if row_idx == 3 else 3
            ref_val = grid[ref_row][col_idx]
            if ref_val and str(ref_val).strip() not in ("?", ""):
                return str(ref_val).strip()

    # 3. Symétrie : grille symétrique horizontale/verticale → ? = cellule miroir
    mirror_row = rows - 1 - row_idx
    mirror_col = cols - 1 - col_idx
    if mirror_row != row_idx and 0 <= mirror_row < rows and col_idx < cols:
        mirror_cell = grid[mirror_row][col_idx]
        if (
            mirror_cell
            and str(mirror_cell).strip() != "?"
            and "?" not in str(mirror_cell)
        ):
            return str(mirror_cell).strip()
    if mirror_col != col_idx and 0 <= mirror_col < cols:
        mirror_cell = grid[row_idx][mirror_col]
        if (
            mirror_cell
            and str(mirror_cell).strip() != "?"
            and "?" not in str(mirror_cell)
        ):
            return str(mirror_cell).strip()
    if 0 <= mirror_row < rows and 0 <= mirror_col < cols:
        mirror_cell = grid[mirror_row][mirror_col]
        if (
            mirror_cell
            and str(mirror_cell).strip() != "?"
            and "?" not in str(mirror_cell)
        ):
            return str(mirror_cell).strip()

    # 3. Analyser le pattern horizontal (ligne) pour patterns simples
    row = grid[row_idx]
    if len(row) >= 2:
        # Pattern X-O-X suggère X
        if col_idx == 2 and row[0] == "X" and row[1] == "O":
            return "X"
        # Pattern O-X-O suggère O
        if col_idx == 2 and row[0] == "O" and row[1] == "X":
            return "O"
        # Pattern alterné simple
        if col_idx == 2:
            if row[0] == row[1]:  # Même valeur répétée
                return row[0]
            else:  # Pattern alterné
                # Si X-O, alors ? = X (pour compléter X-O-X)
                if row[0] == "X" and row[1] == "O":
                    return "X"
                elif row[0] == "O" and row[1] == "X":
                    return "O"

    # 3. Analyser le pattern vertical (colonne)
    if len(grid) >= 2:
        col = [
            grid[i][col_idx]
            for i in range(len(grid))
            if i < len(grid) and col_idx < len(grid[i])
        ]
        if len(col) >= 2:
            # Pattern X-O-X suggère X
            if row_idx == 2 and col[0] == "X" and col[1] == "O":
                return "X"
            # Pattern O-X-O suggère O
            if row_idx == 2 and col[0] == "O" and col[1] == "X":
                return "O"
            # Pattern alterné simple
            if row_idx == 2:
                if col[0] == col[1]:  # Même valeur répétée
                    return col[0]
                else:  # Pattern alterné
                    if col[0] == "X" and col[1] == "O":
                        return "X"
                    elif col[0] == "O" and col[1] == "X":
                        return "O"

    # 4. Analyser les diagonales si applicable
    if row_idx == col_idx:  # Diagonale principale
        diag = [
            grid[i][i]
            for i in range(min(len(grid), len(grid[0])))
            if i < len(grid) and i < len(grid[0])
        ]
        if len(diag) >= 2:
            if diag[0] == diag[1]:
                return diag[0]
            elif diag[0] == "X" and diag[1] == "O":
                return "X"
            elif diag[0] == "O" and diag[1] == "X":
                return "O"

    # Diagonale secondaire
    if row_idx + col_idx == len(grid) - 1:
        diag2 = [
            grid[i][len(grid[0]) - 1 - i] for i in range(min(len(grid), len(grid[0])))
        ]
        if len(diag2) >= 2:
            if diag2[0] == diag2[1]:
                return diag2[0]
            elif diag2[0] == "X" and diag2[1] == "O":
                return "X"
            elif diag2[0] == "O" and diag2[1] == "X":
                return "O"

    return None


def analyze_latin_square_pattern(
    grid: List[List[Any]], row_idx: int, col_idx: int
) -> Optional[str]:
    """
    Analyse un pattern de type "Latin Square" où chaque ligne et/ou colonne
    doit contenir chaque élément unique exactement une fois.

    Exemples de grilles supportées:
    - [triangle, cercle, carré] / [cercle, carré, triangle] / [carré, ?, triangle] → cercle
    - [1, 2, 3] / [2, 3, 1] / [3, ?, 2] → 1

    Args:
        grid: Grille 2D
        row_idx: Index de la ligne contenant '?'
        col_idx: Index de la colonne contenant '?'

    Returns:
        Élément manquant ou None si le pattern n'est pas un latin square
    """
    if not grid or not isinstance(grid, list):
        return None

    # Collecter tous les éléments uniques de la grille (sauf '?')
    all_elements = set()
    for row in grid:
        if isinstance(row, list):
            for cell in row:
                cell_str = str(cell).strip().lower()
                if cell_str != "?" and "?" not in cell_str:
                    all_elements.add(cell_str)

    if len(all_elements) < 2:
        return None

    # Vérifier si c'est un latin square :
    # Le nombre d'éléments uniques devrait être égal à la taille de la grille
    grid_size = len(grid)
    if len(all_elements) != grid_size:
        # Ce n'est peut-être pas un latin square parfait, mais on peut quand même essayer
        pass

    # Analyser la ligne contenant '?' pour trouver l'élément manquant
    target_row = grid[row_idx]
    if not isinstance(target_row, list):
        return None

    elements_in_row = set()
    for cell in target_row:
        cell_str = str(cell).strip().lower()
        if cell_str != "?" and "?" not in cell_str:
            elements_in_row.add(cell_str)

    # L'élément manquant est celui qui est dans all_elements mais pas dans elements_in_row
    missing_in_row = all_elements - elements_in_row

    if len(missing_in_row) == 1:
        missing = list(missing_in_row)[0]
        # Retrouver la casse originale
        for row in grid:
            if isinstance(row, list):
                for cell in row:
                    if str(cell).strip().lower() == missing:
                        return str(cell)
        return missing

    # Si plusieurs éléments manquent dans la ligne, essayer avec la colonne
    if col_idx < len(grid[0]) if len(grid) > 0 and isinstance(grid[0], list) else False:
        elements_in_col = set()
        for row in grid:
            if isinstance(row, list) and col_idx < len(row):
                cell_str = str(row[col_idx]).strip().lower()
                if cell_str != "?" and "?" not in cell_str:
                    elements_in_col.add(cell_str)

        missing_in_col = all_elements - elements_in_col

        if len(missing_in_col) == 1:
            missing = list(missing_in_col)[0]
            # Retrouver la casse originale
            for row in grid:
                if isinstance(row, list):
                    for cell in row:
                        if str(cell).strip().lower() == missing:
                            return str(cell)
            return missing

    # Si on a trouvé des candidats dans la ligne ET la colonne, prendre l'intersection
    if len(missing_in_row) > 0:
        missing_in_col_set = set()
        if col_idx < (len(grid[0]) if grid and isinstance(grid[0], list) else 0):
            for row in grid:
                if isinstance(row, list) and col_idx < len(row):
                    cell_str = str(row[col_idx]).strip().lower()
                    if cell_str != "?" and "?" not in cell_str:
                        missing_in_col_set.add(cell_str)
            missing_in_col = all_elements - missing_in_col_set

            intersection = missing_in_row & missing_in_col
            if len(intersection) == 1:
                missing = list(intersection)[0]
                # Retrouver la casse originale
                for row in grid:
                    if isinstance(row, list):
                        for cell in row:
                            if str(cell).strip().lower() == missing:
                                return str(cell)
                return missing

    return None


def analyze_sequence(sequence: List[Any]) -> Optional[str]:
    """
    Analyse une séquence pour déterminer le prochain élément.
    Gère : arithmétique, arithmétique second ordre (diffs croissantes), géométrique.
    """
    if not sequence or len(sequence) < 2:
        return None

    try:
        nums = [
            float(s)
            for s in sequence
            if isinstance(s, (int, float, str))
            and str(s).replace(".", "").replace("-", "").isdigit()
        ]
    except (ValueError, TypeError):
        return None

    if len(nums) < 2:
        return None

    # 1. Séquence arithmétique simple (différence constante)
    diff = nums[1] - nums[0]
    if all(nums[i + 1] - nums[i] == diff for i in range(len(nums) - 1)):
        next_num = nums[-1] + diff
        return str(int(next_num)) if next_num.is_integer() else str(next_num)

    # 2. Séquence arithmétique second ordre (différences croissantes +1)
    if len(nums) >= 3:
        diffs = [nums[i + 1] - nums[i] for i in range(len(nums) - 1)]
        if all(diffs[i + 1] - diffs[i] == 1 for i in range(len(diffs) - 1)):
            next_diff = diffs[-1] + 1
            next_num = nums[-1] + next_diff
            return str(int(next_num)) if next_num.is_integer() else str(next_num)

    # 3. Séquence géométrique (ratio constant, nombres > 0)
    if len(nums) >= 2 and all(n != 0 for n in nums):
        ratio = nums[1] / nums[0]
        if ratio != 0 and all(
            abs((nums[i + 1] / nums[i]) - ratio) < 1e-9 for i in range(len(nums) - 1)
        ):
            next_num = nums[-1] * ratio
            return str(int(next_num)) if next_num.is_integer() else str(next_num)

    return None

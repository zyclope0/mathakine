"""
Module de validation logique pour les challenges générés par IA.
Vérifie la cohérence entre visual_data, correct_answer et solution_explanation.
"""
import json
from typing import Any, Dict, List, Optional, Tuple

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ChallengeValidationError(Exception):
    """Exception levée lors de la validation d'un challenge."""
    pass


def validate_challenge_logic(challenge_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valide la cohérence logique d'un challenge généré par IA.
    
    Args:
        challenge_data: Dictionnaire contenant les données du challenge
        
    Returns:
        Tuple (is_valid, errors) où :
        - is_valid: True si le challenge est valide, False sinon
        - errors: Liste des erreurs détectées
    """
    errors = []
    
    challenge_type = challenge_data.get('challenge_type', '').upper()
    visual_data = challenge_data.get('visual_data', {})
    correct_answer = challenge_data.get('correct_answer', '')
    solution_explanation = challenge_data.get('solution_explanation', '')
    
    # Parser visual_data si nécessaire
    if isinstance(visual_data, str):
        try:
            visual_data = json.loads(visual_data)
        except json.JSONDecodeError:
            errors.append("visual_data n'est pas un JSON valide")
            return False, errors
    
    # Validation spécifique selon le type de challenge
    if challenge_type == 'PATTERN':
        pattern_errors = validate_pattern_challenge(visual_data, correct_answer, solution_explanation)
        errors.extend(pattern_errors)
    
    elif challenge_type == 'SEQUENCE':
        sequence_errors = validate_sequence_challenge(visual_data, correct_answer, solution_explanation)
        errors.extend(sequence_errors)
    
    elif challenge_type == 'PUZZLE':
        puzzle_errors = validate_puzzle_challenge(visual_data, correct_answer, solution_explanation)
        errors.extend(puzzle_errors)
    
    elif challenge_type == 'GRAPH':
        graph_errors = validate_graph_challenge(visual_data, correct_answer, solution_explanation)
        errors.extend(graph_errors)
    
    elif challenge_type == 'VISUAL':
        # VISUAL inclut les défis spatiaux (rotation, symétrie, etc.)
        visual_errors = validate_spatial_challenge(visual_data, correct_answer, solution_explanation)
        errors.extend(visual_errors)
    
    elif challenge_type == 'CODING':
        # Valider les défis de type labyrinthe/maze
        coding_errors = validate_coding_challenge(visual_data, correct_answer, solution_explanation)
        errors.extend(coding_errors)
    
    # Validation générale
    # Convertir en string si c'est une liste
    correct_answer_str = ','.join(correct_answer) if isinstance(correct_answer, list) else str(correct_answer) if correct_answer else ''
    explanation_str = str(solution_explanation) if solution_explanation else ''
    
    if not correct_answer_str or not correct_answer_str.strip():
        errors.append("correct_answer est vide")
    
    if not explanation_str or not explanation_str.strip():
        errors.append("solution_explanation est vide")
    
    return len(errors) == 0, errors


def validate_pattern_challenge(visual_data: Dict[str, Any], correct_answer: str, explanation: str) -> List[str]:
    """
    Valide un challenge de type PATTERN.
    Vérifie que la réponse correspond au pattern dans la grille.
    """
    errors = []
    
    if not visual_data or 'grid' not in visual_data:
        errors.append("visual_data.grid manquant pour un challenge PATTERN")
        return errors
    
    grid = visual_data.get('grid', [])
    if not grid or not isinstance(grid, list):
        errors.append("visual_data.grid doit être un tableau")
        return errors
    
    # Trouver la position du '?'
    question_pos = None
    for i, row in enumerate(grid):
        if not isinstance(row, list):
            continue
        for j, cell in enumerate(row):
            if cell == '?' or (isinstance(cell, str) and '?' in cell):
                question_pos = (i, j)
                break
        if question_pos:
            break
    
    if not question_pos:
        # Pas de '?' à compléter, considérer comme valide
        return errors
    
    row_idx, col_idx = question_pos
    
    # Analyser le pattern pour déterminer la réponse attendue
    expected_answer = analyze_pattern(grid, row_idx, col_idx)
    
    if expected_answer:
        # Normaliser les réponses pour comparaison
        correct_normalized = str(correct_answer).strip().upper()
        expected_normalized = str(expected_answer).strip().upper()
        
        if correct_normalized != expected_normalized:
            errors.append(
                f"Pattern incohérent: le pattern suggère '{expected_answer}', "
                f"mais correct_answer est '{correct_answer}'. "
                f"Vérifiez la grille: {grid}"
            )
    
    return errors


def analyze_pattern(grid: List[List[Any]], row_idx: int, col_idx: int) -> Optional[str]:
    """
    Analyse un pattern dans une grille pour déterminer la réponse attendue.
    Supporte plusieurs types de patterns :
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
    
    # 1. Essayer d'abord le pattern "Latin Square" (chaque ligne contient tous les éléments)
    # C'est le pattern le plus courant pour les grilles de formes
    latin_answer = analyze_latin_square_pattern(grid, row_idx, col_idx)
    if latin_answer:
        return latin_answer
    
    # 2. Analyser le pattern horizontal (ligne) pour patterns simples
    row = grid[row_idx]
    if len(row) >= 2:
        # Pattern X-O-X suggère X
        if col_idx == 2 and row[0] == 'X' and row[1] == 'O':
            return 'X'
        # Pattern O-X-O suggère O
        if col_idx == 2 and row[0] == 'O' and row[1] == 'X':
            return 'O'
        # Pattern alterné simple
        if col_idx == 2:
            if row[0] == row[1]:  # Même valeur répétée
                return row[0]
            else:  # Pattern alterné
                # Si X-O, alors ? = X (pour compléter X-O-X)
                if row[0] == 'X' and row[1] == 'O':
                    return 'X'
                elif row[0] == 'O' and row[1] == 'X':
                    return 'O'
    
    # 3. Analyser le pattern vertical (colonne)
    if len(grid) >= 2:
        col = [grid[i][col_idx] for i in range(len(grid)) if i < len(grid) and col_idx < len(grid[i])]
        if len(col) >= 2:
            # Pattern X-O-X suggère X
            if row_idx == 2 and col[0] == 'X' and col[1] == 'O':
                return 'X'
            # Pattern O-X-O suggère O
            if row_idx == 2 and col[0] == 'O' and col[1] == 'X':
                return 'O'
            # Pattern alterné simple
            if row_idx == 2:
                if col[0] == col[1]:  # Même valeur répétée
                    return col[0]
                else:  # Pattern alterné
                    if col[0] == 'X' and col[1] == 'O':
                        return 'X'
                    elif col[0] == 'O' and col[1] == 'X':
                        return 'O'
    
    # 4. Analyser les diagonales si applicable
    if row_idx == col_idx:  # Diagonale principale
        diag = [grid[i][i] for i in range(min(len(grid), len(grid[0]))) if i < len(grid) and i < len(grid[0])]
        if len(diag) >= 2:
            if diag[0] == diag[1]:
                return diag[0]
            elif diag[0] == 'X' and diag[1] == 'O':
                return 'X'
            elif diag[0] == 'O' and diag[1] == 'X':
                return 'O'
    
    # Diagonale secondaire
    if row_idx + col_idx == len(grid) - 1:
        diag2 = [grid[i][len(grid[0]) - 1 - i] for i in range(min(len(grid), len(grid[0])))]
        if len(diag2) >= 2:
            if diag2[0] == diag2[1]:
                return diag2[0]
            elif diag2[0] == 'X' and diag2[1] == 'O':
                return 'X'
            elif diag2[0] == 'O' and diag2[1] == 'X':
                return 'O'
    
    return None


def analyze_latin_square_pattern(grid: List[List[Any]], row_idx: int, col_idx: int) -> Optional[str]:
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
                if cell_str != '?' and '?' not in cell_str:
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
        if cell_str != '?' and '?' not in cell_str:
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
                if cell_str != '?' and '?' not in cell_str:
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
                    if cell_str != '?' and '?' not in cell_str:
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


def validate_sequence_challenge(visual_data: Dict[str, Any], correct_answer: str, explanation: str) -> List[str]:
    """
    Valide un challenge de type SEQUENCE.
    Vérifie que la réponse correspond à la séquence logique.
    """
    errors = []
    
    if not visual_data or 'sequence' not in visual_data:
        # Sequence peut être dans visual_data ou directement dans la question
        return errors
    
    sequence = visual_data.get('sequence', [])
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


def analyze_sequence(sequence: List[Any]) -> Optional[str]:
    """
    Analyse une séquence pour déterminer le prochain élément.
    """
    if not sequence or len(sequence) < 2:
        return None
    
    # Séquence arithmétique simple
    if len(sequence) >= 2:
        try:
            # Convertir en nombres si possible
            nums = [float(s) for s in sequence if isinstance(s, (int, float, str)) and str(s).replace('.', '').isdigit()]
            if len(nums) >= 2:
                diff = nums[1] - nums[0]
                next_num = nums[-1] + diff
                return str(int(next_num)) if next_num.is_integer() else str(next_num)
        except (ValueError, TypeError):
            pass
    
    return None


def validate_puzzle_challenge(visual_data: Dict[str, Any], correct_answer: str, explanation: str) -> List[str]:
    """
    Valide un challenge de type PUZZLE.
    Vérifie que:
    - La réponse correspond à l'ordre logique des pièces
    - Des indices/règles sont fournis pour déterminer l'ordre
    - L'explication justifie l'ordre correct
    """
    errors = []
    
    if not visual_data:
        errors.append("visual_data manquant pour un challenge PUZZLE")
        return errors
    
    pieces = visual_data.get('pieces', visual_data.get('items', []))
    if not pieces or not isinstance(pieces, list):
        errors.append("visual_data.pieces manquant pour un challenge PUZZLE")
        return errors
    
    # Vérifier qu'il y a des indices/règles pour résoudre le puzzle
    hints = visual_data.get('hints', visual_data.get('rules', visual_data.get('clues', visual_data.get('indices', []))))
    description = visual_data.get('description', '')
    
    if not hints and not description:
        errors.append(
            "PUZZLE incomplet: aucun indice (hints/rules/clues) ni description fourni. "
            "L'utilisateur n'a aucun moyen de déterminer l'ordre correct."
        )
    
    # Vérifier que les indices sont substantiels (pas vides ou trop courts)
    if hints and isinstance(hints, list):
        valid_hints = [h for h in hints if isinstance(h, str) and len(h.strip()) > 5]
        if len(valid_hints) < 2 and len(pieces) > 2:
            errors.append(
                f"PUZZLE avec {len(pieces)} éléments mais seulement {len(valid_hints)} indice(s) valide(s). "
                f"Ajoutez plus d'indices pour permettre la résolution."
            )
    
    # Parser les pièces en liste de strings normalisées
    piece_values = []
    for p in pieces:
        if isinstance(p, dict):
            val = p.get('label') or p.get('value') or p.get('name') or str(p)
        else:
            val = p
        piece_values.append(str(val).strip().lower())
    
    # Pour un puzzle, la réponse devrait être une liste ordonnée
    if correct_answer:
        # Gérer correct_answer comme liste ou string
        if isinstance(correct_answer, list):
            answer_parts = [str(p).strip().lower() for p in correct_answer]
        else:
            answer_parts = [p.strip().lower() for p in str(correct_answer).split(',')]
        
        if len(answer_parts) != len(piece_values):
            errors.append(
                f"Puzzle incohérent: correct_answer contient {len(answer_parts)} éléments, "
                f"mais pieces contient {len(piece_values)} éléments"
            )
        
        # Vérifier que tous les éléments de pieces sont dans la réponse
        missing = set(piece_values) - set(answer_parts)
        if missing:
            errors.append(f"Puzzle: éléments manquants dans correct_answer: {missing}")
    
    # Vérifier que l'explication justifie l'ordre
    if explanation and piece_values:
        # L'explication devrait mentionner au moins quelques éléments
        explanation_lower = str(explanation).lower()
        mentioned_count = sum(1 for p in piece_values if p in explanation_lower)
        if mentioned_count < len(piece_values) // 2:
            errors.append(
                "L'explication ne mentionne pas assez d'éléments du puzzle pour justifier l'ordre."
            )
    
    return errors


def validate_graph_challenge(visual_data: Dict[str, Any], correct_answer: str, explanation: str) -> List[str]:
    """
    Valide un challenge de type GRAPH.
    Vérifie que les nœuds et arêtes sont cohérents.
    """
    errors = []
    
    if not visual_data:
        return errors
    
    nodes = visual_data.get('nodes', visual_data.get('vertices', []))
    edges = visual_data.get('edges', visual_data.get('links', []))
    
    if not nodes or not isinstance(nodes, list):
        errors.append("visual_data.nodes manquant ou invalide pour un challenge GRAPH")
        return errors
    
    # Créer un set des noms de nœuds pour vérification
    node_names = set()
    for node in nodes:
        if isinstance(node, dict):
            node_names.add(str(node.get('label', node.get('value', node.get('id', '')))).upper())
        else:
            node_names.add(str(node).upper())
    
    # Vérifier que toutes les arêtes référencent des nœuds existants
    if edges and isinstance(edges, list):
        for edge in edges:
            if isinstance(edge, dict):
                from_node = str(edge.get('from', '')).upper()
                to_node = str(edge.get('to', '')).upper()
            elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
                from_node = str(edge[0]).upper()
                to_node = str(edge[1]).upper()
            else:
                continue
            
            if from_node and from_node not in node_names and not from_node.isdigit():
                errors.append(f"Arête référence un nœud inexistant: '{edge[0] if isinstance(edge, list) else edge.get('from')}'")
            if to_node and to_node not in node_names and not to_node.isdigit():
                errors.append(f"Arête référence un nœud inexistant: '{edge[1] if isinstance(edge, list) else edge.get('to')}'")
    
    return errors


def validate_spatial_challenge(visual_data: Dict[str, Any], correct_answer: str, explanation: str) -> List[str]:
    """
    Valide un challenge de type VISUAL (inclut les défis spatiaux).
    Vérifie la cohérence des données de symétrie, de formes, ou de grilles.
    """
    errors = []
    
    if not visual_data:
        return errors
    
    # Vérifier si c'est un défi avec grille (souvent catégorisé comme VISUAL mais contient une grille)
    grid = visual_data.get('grid', visual_data.get('matrix', visual_data.get('pattern')))
    if grid and isinstance(grid, list) and len(grid) > 0:
        # C'est en fait un pattern caché dans un challenge VISUAL
        # Appliquer la même validation que pour PATTERN
        pattern_errors = validate_grid_in_visual(grid, correct_answer, explanation)
        errors.extend(pattern_errors)
        return errors
    
    # Vérifier les données de symétrie
    if visual_data.get('type') == 'symmetry':
        layout = visual_data.get('layout', [])
        symmetry_line = visual_data.get('symmetry_line')
        
        if not layout or not isinstance(layout, list):
            errors.append("visual_data.layout manquant pour un défi de symétrie")
            return errors
        
        # Vérifier qu'il y a une question (cellule avec '?' ou question: true)
        has_question = False
        for item in layout:
            if isinstance(item, dict):
                if item.get('question') or item.get('shape') == '?':
                    has_question = True
                    break
        
        if not has_question:
            errors.append("Défi de symétrie: aucune cellule marquée comme question")
        
        # Vérifier la cohérence gauche/droite
        left_items = [i for i in layout if isinstance(i, dict) and i.get('side') == 'left']
        right_items = [i for i in layout if isinstance(i, dict) and i.get('side') == 'right']
        
        if not left_items or not right_items:
            errors.append("Défi de symétrie: les côtés gauche et droite doivent être définis")
    
    # Vérifier les formes basiques
    shapes = visual_data.get('shapes', [])
    if shapes and isinstance(shapes, list):
        # Détecter si c'est un défi avec associations forme-couleur
        colors = {'rouge', 'red', 'bleu', 'blue', 'vert', 'green', 'jaune', 'yellow', 
                  'orange', 'violet', 'purple', 'rose', 'pink', 'noir', 'black', 'blanc', 'white'}
        shape_names = {'triangle', 'cercle', 'circle', 'carré', 'carre', 'square', 
                       'rectangle', 'losange', 'diamond', 'étoile', 'etoile', 'star'}
        
        # Collecter les associations forme-couleur visibles (hors ?)
        visible_associations = {}  # {forme: set(couleurs)}
        question_shape = None
        
        for shape in shapes:
            shape_lower = str(shape).lower()
            if '?' in shape_lower:
                # C'est la question - extraire la forme
                for sn in shape_names:
                    if sn in shape_lower:
                        question_shape = sn
                        break
                continue
            
            # Trouver la forme et la couleur
            found_shape = None
            found_color = None
            for sn in shape_names:
                if sn in shape_lower:
                    found_shape = sn
                    break
            for c in colors:
                if c in shape_lower:
                    found_color = c
                    break
            
            if found_shape and found_color:
                if found_shape not in visible_associations:
                    visible_associations[found_shape] = set()
                visible_associations[found_shape].add(found_color)
        
        # Si c'est un défi couleur et que la réponse est une couleur
        correct_lower = str(correct_answer).lower() if correct_answer else ''
        answer_is_color = any(c in correct_lower for c in colors)
        
        if question_shape and answer_is_color:
            # Vérifier que cette association forme-couleur est visible
            if question_shape not in visible_associations:
                errors.append(
                    f"VISUAL incomplet: la forme '{question_shape}' avec '?' n'a aucun exemple visible "
                    f"montrant sa couleur associée. L'utilisateur ne peut pas deviner '{correct_answer}'."
                )
            elif correct_lower not in str(visible_associations.get(question_shape, set())).lower():
                errors.append(
                    f"VISUAL incohérent: la réponse '{correct_answer}' n'est pas visible dans les exemples "
                    f"de '{question_shape}'. Visible: {visible_associations.get(question_shape, set())}"
                )
    
    # Vérifier que correct_answer n'est pas vide
    if not correct_answer or not str(correct_answer).strip():
        errors.append("correct_answer est vide pour un défi VISUAL")
    
    return errors


def validate_grid_in_visual(grid: List[List[Any]], correct_answer: str, explanation: str) -> List[str]:
    """
    Valide une grille contenue dans un challenge VISUAL.
    Vérifie la cohérence entre la grille et la réponse fournie.
    """
    errors = []
    
    # Trouver la position du '?'
    question_pos = None
    for i, row in enumerate(grid):
        if not isinstance(row, list):
            continue
        for j, cell in enumerate(row):
            if cell == '?' or (isinstance(cell, str) and '?' in str(cell)):
                question_pos = (i, j)
                break
        if question_pos:
            break
    
    if not question_pos:
        # Pas de '?' à compléter
        return errors
    
    row_idx, col_idx = question_pos
    
    # Analyser le pattern pour déterminer la réponse attendue
    expected_answer = analyze_latin_square_pattern(grid, row_idx, col_idx)
    if not expected_answer:
        expected_answer = analyze_pattern(grid, row_idx, col_idx)
    
    if expected_answer:
        # Normaliser les réponses pour comparaison
        correct_normalized = str(correct_answer).strip().lower()
        expected_normalized = str(expected_answer).strip().lower()
        
        if correct_normalized != expected_normalized:
            errors.append(
                f"Grille VISUAL incohérente: le pattern suggère '{expected_answer}', "
                f"mais correct_answer est '{correct_answer}'. "
                f"Grille: {grid}"
            )
    
    return errors


def auto_correct_challenge(challenge_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tente de corriger automatiquement un challenge invalide.
    
    Args:
        challenge_data: Dictionnaire contenant les données du challenge
        
    Returns:
        Dictionnaire corrigé (peut être identique si aucune correction possible)
    """
    corrected = challenge_data.copy()
    
    challenge_type = challenge_data.get('challenge_type', '').upper()
    visual_data = challenge_data.get('visual_data', {})
    
    # Parser visual_data si nécessaire
    if isinstance(visual_data, str):
        try:
            visual_data = json.loads(visual_data)
        except json.JSONDecodeError:
            return corrected
    
    # Correction pour PATTERN
    if challenge_type == 'PATTERN' and visual_data and 'grid' in visual_data:
        grid = visual_data.get('grid', [])
        if grid:
            # Trouver la position du '?'
            question_pos = None
            for i, row in enumerate(grid):
                if not isinstance(row, list):
                    continue
                for j, cell in enumerate(row):
                    if cell == '?' or (isinstance(cell, str) and '?' in cell):
                        question_pos = (i, j)
                        break
                if question_pos:
                    break
            
            if question_pos:
                row_idx, col_idx = question_pos
                expected_answer = analyze_pattern(grid, row_idx, col_idx)
                
                if expected_answer:
                    logger.info(f"Correction automatique PATTERN: correct_answer changé de '{corrected.get('correct_answer')}' à '{expected_answer}'")
                    corrected['correct_answer'] = expected_answer
                    
                    # Mettre à jour l'explication si elle est contradictoire
                    explanation = corrected.get('solution_explanation', '')
                    if expected_answer.upper() not in explanation.upper():
                        corrected['solution_explanation'] = (
                            f"En analysant le pattern dans la grille, on observe que le motif se répète. "
                            f"Le pattern suggère que la réponse est '{expected_answer}'. "
                            f"{explanation}"
                        )
    
    # Correction pour VISUAL avec grille
    if challenge_type == 'VISUAL' and visual_data:
        grid = visual_data.get('grid', visual_data.get('matrix', visual_data.get('pattern')))
        if grid and isinstance(grid, list) and len(grid) > 0:
            # Trouver la position du '?'
            question_pos = None
            for i, row in enumerate(grid):
                if not isinstance(row, list):
                    continue
                for j, cell in enumerate(row):
                    if cell == '?' or (isinstance(cell, str) and '?' in str(cell)):
                        question_pos = (i, j)
                        break
                if question_pos:
                    break
            
            if question_pos:
                row_idx, col_idx = question_pos
                expected_answer = analyze_latin_square_pattern(grid, row_idx, col_idx)
                if not expected_answer:
                    expected_answer = analyze_pattern(grid, row_idx, col_idx)
                
                if expected_answer:
                    current_answer = str(corrected.get('correct_answer', '')).strip().lower()
                    expected_lower = expected_answer.lower()
                    
                    if current_answer != expected_lower:
                        logger.info(f"Correction automatique VISUAL: correct_answer changé de '{corrected.get('correct_answer')}' à '{expected_answer}'")
                        corrected['correct_answer'] = expected_answer
                        
                        # Mettre à jour l'explication et le titre si contradictoires
                        explanation = corrected.get('solution_explanation', '')
                        title = corrected.get('title', '')
                        question = corrected.get('question', '')
                        
                        # Corriger l'explication
                        if expected_lower not in explanation.lower():
                            corrected['solution_explanation'] = (
                                f"En analysant la grille, chaque ligne doit contenir chaque forme une seule fois. "
                                f"La ligne avec '?' contient déjà les autres formes, donc l'élément manquant est '{expected_answer}'. "
                            )
                        
                        # Corriger le titre si incohérent
                        # Ex: "Où est le carré manquant ?" devrait devenir "Où est le cercle manquant ?"
                        if title:
                            title_lower = title.lower()
                            # Détecter si le titre mentionne une mauvaise forme
                            shapes = ['triangle', 'cercle', 'carré', 'losange', 'étoile', 'rectangle']
                            for shape in shapes:
                                if shape in title_lower and shape != expected_lower:
                                    # Le titre mentionne une autre forme que la bonne réponse
                                    new_title = title.replace(shape, expected_answer).replace(shape.capitalize(), expected_answer.capitalize())
                                    logger.info(f"Correction automatique titre: '{title}' → '{new_title}'")
                                    corrected['title'] = new_title
                                    break
    
    # Correction pour SEQUENCE
    if challenge_type == 'SEQUENCE' and visual_data and 'sequence' in visual_data:
        sequence = visual_data.get('sequence', [])
        if sequence and isinstance(sequence, list) and len(sequence) >= 2:
            expected_answer = analyze_sequence(sequence)
            
            if expected_answer:
                current_answer = corrected.get('correct_answer', '')
                if str(current_answer).strip() != str(expected_answer).strip():
                    logger.info(f"Correction automatique SEQUENCE: correct_answer changé de '{current_answer}' à '{expected_answer}'")
                    corrected['correct_answer'] = expected_answer
                    
                    # Mettre à jour l'explication si elle est contradictoire
                    explanation = corrected.get('solution_explanation', '')
                    if expected_answer not in explanation:
                        corrected['solution_explanation'] = (
                            f"En analysant la séquence {sequence}, on observe une progression arithmétique. "
                            f"Le prochain élément de la séquence est '{expected_answer}'. "
                            f"{explanation}"
                        )
    
    # Correction pour CODING (labyrinthes)
    if challenge_type == 'CODING' and visual_data:
        maze = visual_data.get('maze') or visual_data.get('grid') or visual_data.get('labyrinth')
        start = visual_data.get('start') or visual_data.get('start_position')
        end = visual_data.get('end') or visual_data.get('end_position') or visual_data.get('goal')
        
        if maze and start and end:
            # C'est un labyrinthe - valider et corriger le chemin
            current_answer = corrected.get('correct_answer', '')
            correct_path = solve_maze_bfs(maze, start, end)
            
            if correct_path:
                # Vérifier si la réponse actuelle est valide
                is_valid = validate_maze_path(maze, start, end, current_answer)
                
                if not is_valid:
                    logger.info(f"Correction automatique MAZE: chemin invalide '{current_answer}' → '{correct_path}'")
                    corrected['correct_answer'] = correct_path
                    corrected['solution_explanation'] = (
                        f"Pour aller du départ {start} à l'arrivée {end}, "
                        f"le chemin optimal est : {correct_path}. "
                        f"Ce chemin évite tous les murs (#) et utilise uniquement les cases libres."
                    )
            else:
                logger.warning(f"Impossible de trouver un chemin valide dans le labyrinthe de {start} à {end}")
    
    return corrected


def validate_coding_challenge(visual_data: Dict[str, Any], correct_answer: str, explanation: str) -> List[str]:
    """
    Valide un challenge de type CODING.
    REJETTE les défis qui ne sont pas de vraie cryptographie.
    """
    errors = []
    
    if not visual_data:
        errors.append("CODING: visual_data est vide - un défi de cryptographie doit avoir des données")
        return errors
    
    # Types valides pour CODING (cryptographie)
    valid_coding_types = ['caesar', 'substitution', 'binary', 'symbols', 'algorithm', 'maze']
    coding_type = visual_data.get('type', '').lower()
    
    # Détecter si c'est un labyrinthe (même sans "type" explicite)
    maze = visual_data.get('maze') or visual_data.get('grid') or visual_data.get('labyrinth')
    start = visual_data.get('start') or visual_data.get('start_position')
    end = visual_data.get('end') or visual_data.get('end_position') or visual_data.get('goal')
    is_maze = maze and start and end
    
    # Détecter si c'est une SÉQUENCE ou un FAUX LABYRINTHE (INVALIDE pour CODING)
    has_sequence = visual_data.get('sequence') is not None
    has_pattern = visual_data.get('pattern') and not visual_data.get('encoded_message')
    has_shapes = visual_data.get('shapes') is not None
    
    # Détecter les "labyrinthes de nombres" - CE N'EST PAS DE LA CRYPTOGRAPHIE !
    has_numbers = visual_data.get('numbers') is not None
    has_target = visual_data.get('target') is not None
    has_movement_options = visual_data.get('movement_options') is not None or visual_data.get('movement') is not None
    is_fake_number_maze = has_numbers and (has_target or has_movement_options)
    
    # Rejeter les séquences, patterns, et faux labyrinthes
    if has_sequence:
        errors.append("CODING INVALIDE: 'sequence' détectée - utiliser le type SEQUENCE, pas CODING")
        return errors
    
    if has_pattern and not is_maze:
        errors.append("CODING INVALIDE: 'pattern' sans cryptographie - utiliser le type PATTERN, pas CODING")
        return errors
    
    if has_shapes:
        errors.append("CODING INVALIDE: 'shapes' détectées - utiliser le type VISUAL, pas CODING")
        return errors
    
    if is_fake_number_maze:
        errors.append(
            "CODING INVALIDE: 'numbers' + 'target' détectés - c'est un labyrinthe de nombres, "
            "pas de la cryptographie ! Utiliser le type SEQUENCE ou PUZZLE, pas CODING."
        )
        return errors
    
    # Rejeter aussi les défis avec uniquement des nombres et pas de message encodé
    if has_numbers and not visual_data.get('encoded_message') and not visual_data.get('message'):
        errors.append(
            "CODING INVALIDE: 'numbers' sans 'encoded_message' - CODING doit avoir un message secret à décoder, "
            "pas une liste de nombres."
        )
        return errors
    
    # Vérifier le type ou la présence d'éléments de cryptographie
    has_encoded_message = visual_data.get('encoded_message') or visual_data.get('message')
    has_crypto_key = visual_data.get('key') or visual_data.get('partial_key') or visual_data.get('shift')
    has_steps = visual_data.get('steps') and isinstance(visual_data.get('steps'), list)
    
    is_valid_crypto = (
        coding_type in valid_coding_types or
        is_maze or
        has_encoded_message or
        (has_crypto_key and has_encoded_message) or
        has_steps
    )
    
    if not is_valid_crypto:
        errors.append(
            f"CODING INVALIDE: Le visual_data ne contient pas de cryptographie valide. "
            f"Attendu: type={valid_coding_types}, encoded_message, key/shift, ou maze. "
            f"Reçu: {list(visual_data.keys())}"
        )
    
    # Si c'est un labyrinthe, valider le chemin
    if is_maze:
        if not validate_maze_path(maze, start, end, correct_answer):
            errors.append(f"MAZE: Le chemin '{correct_answer}' ne mène pas du départ {start} à l'arrivée {end}")
    
    return errors


def solve_maze_bfs(maze: List[List[str]], start: List[int], end: List[int]) -> Optional[str]:
    """
    Résout un labyrinthe avec BFS et retourne le chemin en directions.
    
    Args:
        maze: Grille du labyrinthe (# = mur, espace = chemin)
        start: Position de départ [row, col]
        end: Position d'arrivée [row, col]
    
    Returns:
        Chemin en directions (ex: "BAS, BAS, DROITE, DROITE") ou None si pas de solution
    """
    from collections import deque
    
    if not maze or not start or not end:
        return None
    
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0
    
    start_row, start_col = start[0], start[1]
    end_row, end_col = end[0], end[1]
    
    # Vérifier que start et end sont valides
    if not (0 <= start_row < rows and 0 <= start_col < cols):
        return None
    if not (0 <= end_row < rows and 0 <= end_col < cols):
        return None
    
    # Directions : (delta_row, delta_col, nom)
    directions = [
        (-1, 0, "HAUT"),
        (1, 0, "BAS"),
        (0, -1, "GAUCHE"),
        (0, 1, "DROITE")
    ]
    
    # BFS
    queue = deque([(start_row, start_col, [])])
    visited = {(start_row, start_col)}
    
    while queue:
        row, col, path = queue.popleft()
        
        # Arrivée atteinte
        if row == end_row and col == end_col:
            return ", ".join(path) if path else "DÉJÀ À L'ARRIVÉE"
        
        for dr, dc, direction in directions:
            new_row, new_col = row + dr, col + dc
            
            # Vérifier les limites
            if not (0 <= new_row < rows and 0 <= new_col < cols):
                continue
            
            # Vérifier si déjà visité
            if (new_row, new_col) in visited:
                continue
            
            # Vérifier si c'est un mur
            cell = maze[new_row][new_col] if isinstance(maze[new_row], list) else maze[new_row]
            if isinstance(cell, list):
                cell = cell[new_col] if new_col < len(cell) else '#'
            
            if cell in ['#', '█', '1']:
                continue
            
            # Ajouter à la file
            visited.add((new_row, new_col))
            queue.append((new_row, new_col, path + [direction]))
    
    return None  # Pas de chemin trouvé


def validate_maze_path(maze: List[List[str]], start: List[int], end: List[int], path_str: str) -> bool:
    """
    Vérifie si un chemin est valide dans un labyrinthe.
    
    Args:
        maze: Grille du labyrinthe
        start: Position de départ [row, col]
        end: Position d'arrivée [row, col]
        path_str: Chemin en texte (ex: "BAS, DROITE, DROITE")
    
    Returns:
        True si le chemin est valide et mène à l'arrivée
    """
    if not maze or not start or not end or not path_str:
        return False
    
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0
    
    # Parser le chemin
    directions_map = {
        'haut': (-1, 0), 'up': (-1, 0), 'h': (-1, 0),
        'bas': (1, 0), 'down': (1, 0), 'b': (1, 0),
        'gauche': (0, -1), 'left': (0, -1), 'g': (0, -1),
        'droite': (0, 1), 'right': (0, 1), 'd': (0, 1)
    }
    
    # Extraire les directions du chemin
    path_parts = [p.strip().lower() for p in path_str.replace(',', ' ').split() if p.strip()]
    
    row, col = start[0], start[1]
    
    for direction in path_parts:
        if direction not in directions_map:
            continue
        
        dr, dc = directions_map[direction]
        new_row, new_col = row + dr, col + dc
        
        # Vérifier les limites
        if not (0 <= new_row < rows and 0 <= new_col < cols):
            return False
        
        # Vérifier si c'est un mur
        cell = maze[new_row]
        if isinstance(cell, list):
            cell = cell[new_col] if new_col < len(cell) else '#'
        elif isinstance(cell, str) and new_col < len(cell):
            cell = cell[new_col]
        else:
            cell = '#'
        
        if cell in ['#', '█', '1']:
            return False
        
        row, col = new_row, new_col
    
    # Vérifier si on est arrivé à destination
    return row == end[0] and col == end[1]


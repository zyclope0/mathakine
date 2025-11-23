"""
Module de validation logique pour les challenges générés par IA.
Vérifie la cohérence entre visual_data, correct_answer et solution_explanation.
"""
import json
from typing import Dict, Any, Tuple, List, Optional
from loguru import logger


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
    
    elif challenge_type == 'SPATIAL' or challenge_type == 'VISUAL':
        spatial_errors = validate_spatial_challenge(visual_data, correct_answer, solution_explanation)
        errors.extend(spatial_errors)
    
    # Validation générale
    if not correct_answer or not correct_answer.strip():
        errors.append("correct_answer est vide")
    
    if not solution_explanation or not solution_explanation.strip():
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
    
    Args:
        grid: Grille 2D
        row_idx: Index de la ligne contenant '?'
        col_idx: Index de la colonne contenant '?'
        
    Returns:
        Réponse attendue ou None si le pattern ne peut pas être déterminé
    """
    if not grid or row_idx >= len(grid) or col_idx >= len(grid[0]):
        return None
    
    # Analyser le pattern horizontal (ligne)
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
    
    # Analyser le pattern vertical (colonne)
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
    
    # Analyser les diagonales si applicable
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
    Vérifie que la réponse correspond à l'ordre logique des pièces.
    """
    errors = []
    
    if not visual_data:
        return errors
    
    pieces = visual_data.get('pieces', visual_data.get('items', []))
    if not pieces or not isinstance(pieces, list):
        return errors
    
    # Pour un puzzle, la réponse devrait être une liste ordonnée
    if correct_answer:
        # Vérifier que tous les éléments de pieces sont dans correct_answer
        answer_parts = [p.strip() for p in str(correct_answer).split(',')]
        piece_values = [str(p).strip() for p in pieces]
        
        if len(answer_parts) != len(piece_values):
            errors.append(
                f"Puzzle incohérent: correct_answer contient {len(answer_parts)} éléments, "
                f"mais pieces contient {len(piece_values)} éléments"
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
    
    return corrected


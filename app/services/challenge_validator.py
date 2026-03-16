"""
Module de validation logique pour les challenges générés par IA.
Vérifie la cohérence entre visual_data, correct_answer et solution_explanation.
"""

import json
from typing import Any, Dict, List, Tuple

from app.core.logging_config import get_logger
from app.services.challenge_pattern_sequence_validation import (
    validate_pattern_challenge,
    validate_sequence_challenge,
)
from app.services.challenge_validation_analysis import (
    analyze_latin_square_pattern,
    analyze_pattern,
    analyze_sequence,
    compute_pattern_answers_multi,
    find_question_position_in_grid,
)
from app.services.maze_validator import solve_maze_bfs, validate_maze_path

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

    challenge_type = challenge_data.get("challenge_type", "").upper()
    visual_data = challenge_data.get("visual_data", {})
    correct_answer = challenge_data.get("correct_answer", "")
    solution_explanation = challenge_data.get("solution_explanation", "")

    # Parser visual_data si nécessaire
    if isinstance(visual_data, str):
        try:
            visual_data = json.loads(visual_data)
        except json.JSONDecodeError:
            errors.append("visual_data n'est pas un JSON valide")
            return False, errors

    # Dispatch par type de challenge (B3.5)
    validator = _VALIDATORS_BY_TYPE.get(challenge_type)
    if validator:
        type_errors = validator(visual_data, correct_answer, solution_explanation)
        errors.extend(type_errors)

    # Validation générale
    # Convertir en string si c'est une liste
    correct_answer_str = (
        ",".join(correct_answer)
        if isinstance(correct_answer, list)
        else str(correct_answer) if correct_answer else ""
    )
    explanation_str = str(solution_explanation) if solution_explanation else ""

    if not correct_answer_str or not correct_answer_str.strip():
        errors.append("correct_answer est vide")

    if not explanation_str or not explanation_str.strip():
        errors.append("solution_explanation est vide")

    return len(errors) == 0, errors


def validate_puzzle_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
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

    pieces = visual_data.get("pieces", visual_data.get("items", []))
    if not pieces or not isinstance(pieces, list):
        errors.append("visual_data.pieces manquant pour un challenge PUZZLE")
        return errors

    # Vérifier qu'il y a des indices/règles pour résoudre le puzzle
    hints = visual_data.get(
        "hints",
        visual_data.get(
            "rules", visual_data.get("clues", visual_data.get("indices", []))
        ),
    )
    description = visual_data.get("description", "")

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
            val = p.get("label") or p.get("value") or p.get("name") or str(p)
        else:
            val = p
        piece_values.append(str(val).strip().lower())

    # Pour un puzzle, la réponse devrait être une liste ordonnée
    if correct_answer:
        # Gérer correct_answer comme liste ou string
        if isinstance(correct_answer, list):
            answer_parts = [str(p).strip().lower() for p in correct_answer]
        else:
            answer_parts = [p.strip().lower() for p in str(correct_answer).split(",")]

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


def validate_graph_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide un challenge de type GRAPH.
    Vérifie que les nœuds et arêtes sont cohérents.
    """
    errors = []

    if not visual_data:
        return errors

    nodes = visual_data.get("nodes", visual_data.get("vertices", []))
    edges = visual_data.get("edges", visual_data.get("links", []))

    if not nodes or not isinstance(nodes, list):
        errors.append("visual_data.nodes manquant ou invalide pour un challenge GRAPH")
        return errors

    # Créer un set des noms de nœuds pour vérification
    node_names = set()
    for node in nodes:
        if isinstance(node, dict):
            node_names.add(
                str(node.get("label", node.get("value", node.get("id", "")))).upper()
            )
        else:
            node_names.add(str(node).upper())

    # Vérifier que toutes les arêtes référencent des nœuds existants
    if edges and isinstance(edges, list):
        for edge in edges:
            if isinstance(edge, dict):
                from_node = str(edge.get("from", "")).upper()
                to_node = str(edge.get("to", "")).upper()
            elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
                from_node = str(edge[0]).upper()
                to_node = str(edge[1]).upper()
            else:
                continue

            if from_node and from_node not in node_names and not from_node.isdigit():
                errors.append(
                    f"Arête référence un nœud inexistant: '{edge[0] if isinstance(edge, list) else edge.get('from')}'"
                )
            if to_node and to_node not in node_names and not to_node.isdigit():
                errors.append(
                    f"Arête référence un nœud inexistant: '{edge[1] if isinstance(edge, list) else edge.get('to')}'"
                )

    return errors


def validate_spatial_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide un challenge de type VISUAL (inclut les défis spatiaux).
    Vérifie la cohérence des données de symétrie, de formes, ou de grilles.
    """
    errors = []

    if not visual_data:
        return errors

    # Vérifier si c'est un défi avec grille (souvent catégorisé comme VISUAL mais contient une grille)
    grid = visual_data.get(
        "grid", visual_data.get("matrix", visual_data.get("pattern"))
    )
    if grid and isinstance(grid, list) and len(grid) > 0:
        # C'est en fait un pattern caché dans un challenge VISUAL
        # Appliquer la même validation que pour PATTERN
        pattern_errors = validate_grid_in_visual(grid, correct_answer, explanation)
        errors.extend(pattern_errors)
        return errors

    # Vérifier les données de symétrie
    if visual_data.get("type") == "symmetry":
        layout = visual_data.get("layout", [])
        symmetry_line = visual_data.get("symmetry_line")

        if not layout or not isinstance(layout, list):
            errors.append("visual_data.layout manquant pour un défi de symétrie")
            return errors

        # Vérifier qu'il y a une question (cellule avec '?' ou question: true)
        has_question = False
        for item in layout:
            if isinstance(item, dict):
                if item.get("question") or item.get("shape") == "?":
                    has_question = True
                    break

        if not has_question:
            errors.append("Défi de symétrie: aucune cellule marquée comme question")

        # Vérifier la cohérence gauche/droite
        left_items = [
            i for i in layout if isinstance(i, dict) and i.get("side") == "left"
        ]
        right_items = [
            i for i in layout if isinstance(i, dict) and i.get("side") == "right"
        ]

        if not left_items or not right_items:
            errors.append(
                "Défi de symétrie: les côtés gauche et droite doivent être définis"
            )

    # Vérifier les formes basiques
    shapes = visual_data.get("shapes", [])
    if shapes and isinstance(shapes, list):
        # Détecter si c'est un défi avec associations forme-couleur
        colors = {
            "rouge",
            "red",
            "bleu",
            "blue",
            "vert",
            "green",
            "jaune",
            "yellow",
            "orange",
            "violet",
            "purple",
            "rose",
            "pink",
            "noir",
            "black",
            "blanc",
            "white",
        }
        shape_names = {
            "triangle",
            "cercle",
            "circle",
            "carré",
            "carre",
            "square",
            "rectangle",
            "losange",
            "diamond",
            "étoile",
            "etoile",
            "star",
        }

        # Collecter les associations forme-couleur visibles (hors ?)
        visible_associations = {}  # {forme: set(couleurs)}
        question_shape = None

        for shape in shapes:
            shape_lower = str(shape).lower()
            if "?" in shape_lower:
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

        # Format multi-cellules (ex: "Position 2: carré bleu, Position 6: triangle vert")
        correct_lower = str(correct_answer).lower() if correct_answer else ""
        is_multi_cell = "position" in correct_lower and (
            "," in correct_lower or correct_lower.count(":") >= 2
        )
        if is_multi_cell:
            # Ne pas appliquer la validation forme-couleur unique (trop complexe à valider auto)
            pass
        else:
            answer_is_color = any(c in correct_lower for c in colors)
            if question_shape and answer_is_color:
                if question_shape not in visible_associations:
                    errors.append(
                        f"VISUAL incomplet: la forme '{question_shape}' avec '?' n'a aucun exemple visible "
                        f"montrant sa couleur associée. L'utilisateur ne peut pas deviner '{correct_answer}'."
                    )
                else:
                    # Vérifier que la couleur/form de la réponse est visible (ex: "carré bleu" -> bleu dans visible)
                    visible_colors = visible_associations.get(question_shape, set())
                    answer_color_found = any(c in correct_lower for c in visible_colors)
                    if not answer_color_found and visible_colors:
                        errors.append(
                            f"VISUAL incohérent: la réponse '{correct_answer}' n'est pas visible dans les exemples "
                            f"de '{question_shape}'. Visible: {visible_colors}"
                        )

    # Vérifier que correct_answer n'est pas vide
    if not correct_answer or not str(correct_answer).strip():
        errors.append("correct_answer est vide pour un défi VISUAL")

    return errors


def validate_grid_in_visual(
    grid: List[List[Any]], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide une grille contenue dans un challenge VISUAL.
    Vérifie la cohérence entre la grille et la réponse fournie.
    """
    errors = []

    question_pos = find_question_position_in_grid(grid)
    if not question_pos:
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

    challenge_type = challenge_data.get("challenge_type", "").upper()
    visual_data = challenge_data.get("visual_data", {})

    # Parser visual_data si nécessaire
    if isinstance(visual_data, str):
        try:
            visual_data = json.loads(visual_data)
        except json.JSONDecodeError:
            return corrected

    # Correction pour PATTERN
    if challenge_type == "PATTERN" and visual_data and "grid" in visual_data:
        grid = visual_data.get("grid", [])
        if grid:
            # Plusieurs "?" → format "O, O, X, O"
            expected_multi = compute_pattern_answers_multi(grid)
            if expected_multi:
                logger.info(
                    f"Correction automatique PATTERN (multi): correct_answer = '{expected_multi}'"
                )
                corrected["correct_answer"] = expected_multi
                explanation = corrected.get("solution_explanation", "")
                if (
                    expected_multi[:20] not in explanation
                    and expected_multi.split(",")[0].strip().upper()
                    not in explanation.upper()
                ):
                    corrected["solution_explanation"] = (
                        f"Les symboles manquants, dans l'ordre des cases (ligne par ligne), sont : {expected_multi}. "
                        f"{explanation}"
                    )
            else:
                question_pos = find_question_position_in_grid(grid)
                if question_pos:
                    row_idx, col_idx = question_pos
                    expected_answer = analyze_pattern(grid, row_idx, col_idx)
                    if expected_answer:
                        logger.info(
                            f"Correction automatique PATTERN: correct_answer = '{expected_answer}'"
                        )
                        corrected["correct_answer"] = expected_answer

                    # Mettre à jour l'explication si elle est contradictoire
                    explanation = corrected.get("solution_explanation", "")
                    if expected_answer.upper() not in explanation.upper():
                        corrected["solution_explanation"] = (
                            f"En analysant le pattern dans la grille, on observe que le motif se répète. "
                            f"Le pattern suggère que la réponse est '{expected_answer}'. "
                            f"{explanation}"
                        )

    # Correction pour VISUAL avec grille
    if challenge_type == "VISUAL" and visual_data:
        grid = visual_data.get(
            "grid", visual_data.get("matrix", visual_data.get("pattern"))
        )
        if grid and isinstance(grid, list) and len(grid) > 0:
            question_pos = find_question_position_in_grid(grid)
            if question_pos:
                row_idx, col_idx = question_pos
                expected_answer = analyze_latin_square_pattern(grid, row_idx, col_idx)
                if not expected_answer:
                    expected_answer = analyze_pattern(grid, row_idx, col_idx)

                if expected_answer:
                    current_answer = (
                        str(corrected.get("correct_answer", "")).strip().lower()
                    )
                    expected_lower = expected_answer.lower()

                    if current_answer != expected_lower:
                        logger.info(
                            f"Correction automatique VISUAL: correct_answer changé de '{corrected.get('correct_answer')}' à '{expected_answer}'"
                        )
                        corrected["correct_answer"] = expected_answer

                        # Mettre à jour l'explication et le titre si contradictoires
                        explanation = corrected.get("solution_explanation", "")
                        title = corrected.get("title", "")
                        question = corrected.get("question", "")

                        # Corriger l'explication
                        if expected_lower not in explanation.lower():
                            corrected["solution_explanation"] = (
                                f"En analysant la grille, chaque ligne doit contenir chaque forme une seule fois. "
                                f"La ligne avec '?' contient déjà les autres formes, donc l'élément manquant est '{expected_answer}'. "
                            )

                        # Corriger le titre si incohérent
                        # Ex: "Où est le carré manquant ?" devrait devenir "Où est le cercle manquant ?"
                        if title:
                            title_lower = title.lower()
                            # Détecter si le titre mentionne une mauvaise forme
                            shapes = [
                                "triangle",
                                "cercle",
                                "carré",
                                "losange",
                                "étoile",
                                "rectangle",
                            ]
                            for shape in shapes:
                                if shape in title_lower and shape != expected_lower:
                                    # Le titre mentionne une autre forme que la bonne réponse
                                    new_title = title.replace(
                                        shape, expected_answer
                                    ).replace(
                                        shape.capitalize(), expected_answer.capitalize()
                                    )
                                    logger.info(
                                        f"Correction automatique titre: '{title}' → '{new_title}'"
                                    )
                                    corrected["title"] = new_title
                                    break

    # Correction pour SEQUENCE
    if challenge_type == "SEQUENCE" and visual_data and "sequence" in visual_data:
        sequence = visual_data.get("sequence", [])
        if sequence and isinstance(sequence, list) and len(sequence) >= 2:
            expected_answer = analyze_sequence(sequence)

            if expected_answer:
                current_answer = corrected.get("correct_answer", "")
                if str(current_answer).strip() != str(expected_answer).strip():
                    logger.info(
                        f"Correction automatique SEQUENCE: correct_answer changé de '{current_answer}' à '{expected_answer}'"
                    )
                    corrected["correct_answer"] = expected_answer

                    # Mettre à jour l'explication si elle est contradictoire
                    explanation = corrected.get("solution_explanation", "")
                    if expected_answer not in explanation:
                        corrected["solution_explanation"] = (
                            f"En analysant la séquence {sequence}, on observe une progression arithmétique. "
                            f"Le prochain élément de la séquence est '{expected_answer}'. "
                            f"{explanation}"
                        )

    # Correction pour CODING (labyrinthes)
    if challenge_type == "CODING" and visual_data:
        maze = (
            visual_data.get("maze")
            or visual_data.get("grid")
            or visual_data.get("labyrinth")
        )
        start = visual_data.get("start") or visual_data.get("start_position")
        end = (
            visual_data.get("end")
            or visual_data.get("end_position")
            or visual_data.get("goal")
        )

        if maze and start and end:
            # C'est un labyrinthe - valider et corriger le chemin
            current_answer = corrected.get("correct_answer", "")
            correct_path = solve_maze_bfs(maze, start, end)

            if correct_path:
                # Vérifier si la réponse actuelle est valide
                is_valid = validate_maze_path(maze, start, end, current_answer)

                if not is_valid:
                    logger.info(
                        f"Correction automatique MAZE: chemin invalide '{current_answer}' → '{correct_path}'"
                    )
                    corrected["correct_answer"] = correct_path
                    corrected["solution_explanation"] = (
                        f"Pour aller du départ {start} à l'arrivée {end}, "
                        f"le chemin optimal est : {correct_path}. "
                        f"Ce chemin évite tous les murs (#) et utilise uniquement les cases libres."
                    )
            else:
                logger.warning(
                    f"Impossible de trouver un chemin valide dans le labyrinthe de {start} à {end}"
                )

    return corrected


def validate_riddle_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide un challenge de type RIDDLE.
    Vérifie la présence de données permettant de résoudre l'énigme.
    """
    errors = []
    if not visual_data:
        errors.append("RIDDLE: visual_data manquant")
        return errors
    has_clues = bool(visual_data.get("clues") or visual_data.get("indices"))
    has_context = bool(
        visual_data.get("context")
        or visual_data.get("scenario")
        or visual_data.get("scene")
    )
    has_riddle = bool(visual_data.get("riddle") or visual_data.get("question"))
    has_grid = bool(visual_data.get("grid") or visual_data.get("pattern"))
    if not (has_clues or has_context or has_riddle or has_grid):
        errors.append(
            "RIDDLE: visual_data doit contenir au moins clues, context, riddle ou grid "
            "pour permettre de résoudre l'énigme"
        )
    return errors


def validate_probability_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide un challenge de type PROBABILITY.
    Vérifie la présence de données numériques (quantités, totaux).
    """
    errors = []
    if not visual_data:
        errors.append("PROBABILITY: visual_data manquant")
        return errors
    has_counts = False
    for key, val in visual_data.items():
        if key.lower() in ("total", "description", "question"):
            continue
        if isinstance(val, (int, float)) and val > 0:
            has_counts = True
            break
        if isinstance(val, dict):
            for v in val.values():
                if isinstance(v, (int, float)) and v > 0:
                    has_counts = True
                    break
    if not has_counts:
        errors.append(
            "PROBABILITY: visual_data doit contenir des quantités numériques "
            "(ex: rouge_bonbons: 10, bleu_bonbons: 5)"
        )
    return errors


def validate_chess_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """Valide un challenge de type CHESS (échecs)."""
    errors = []
    if not visual_data:
        errors.append("CHESS: visual_data est vide")
        return errors

    board = visual_data.get("board", [])
    if not board or not isinstance(board, list):
        errors.append("CHESS: visual_data.board manquant ou invalide")
        return errors

    if len(board) != 8:
        errors.append(f"CHESS: board doit avoir 8 rangées, reçu {len(board)}")
    valid_pieces = {"K", "k", "Q", "q", "R", "r", "B", "b", "N", "n", "P", "p", ""}
    for i, row in enumerate(board):
        if not isinstance(row, (list, tuple)) or len(row) != 8:
            errors.append(f"CHESS: board[{i}] doit être une liste de 8 éléments")
            break
        for j, cell in enumerate(row):
            val = str(cell).strip() if cell else ""
            if val and val not in valid_pieces:
                errors.append(f"CHESS: pièce invalide '{cell}' en [{i},{j}]")
                break

    turn = visual_data.get("turn", "").lower()
    if turn not in ("white", "black"):
        errors.append(f"CHESS: turn doit être 'white' ou 'black', reçu '{turn}'")

    objective = visual_data.get("objective", "")
    valid_obj = ("mat_en_1", "mat_en_2", "mat_en_3", "meilleur_coup")
    if objective not in valid_obj:
        errors.append(f"CHESS: objective doit être parmi {valid_obj}")

    if not correct_answer or not str(correct_answer).strip():
        errors.append("CHESS: correct_answer est vide (notation algébrique attendue)")

    return errors


def validate_coding_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide un challenge de type CODING.
    REJETTE les défis qui ne sont pas de vraie cryptographie.
    """
    errors = []

    if not visual_data:
        errors.append(
            "CODING: visual_data est vide - un défi de cryptographie doit avoir des données"
        )
        return errors

    # Types valides pour CODING (cryptographie)
    valid_coding_types = [
        "caesar",
        "substitution",
        "binary",
        "symbols",
        "algorithm",
        "maze",
    ]
    coding_type = visual_data.get("type", "").lower()

    # Détecter si c'est un labyrinthe (même sans "type" explicite)
    maze = (
        visual_data.get("maze")
        or visual_data.get("grid")
        or visual_data.get("labyrinth")
    )
    start = visual_data.get("start") or visual_data.get("start_position")
    end = (
        visual_data.get("end")
        or visual_data.get("end_position")
        or visual_data.get("goal")
    )
    is_maze = maze and start and end

    # Détecter si c'est une SÉQUENCE ou un FAUX LABYRINTHE (INVALIDE pour CODING)
    has_sequence = visual_data.get("sequence") is not None
    has_pattern = visual_data.get("pattern") and not visual_data.get("encoded_message")
    has_shapes = visual_data.get("shapes") is not None

    # Détecter les "labyrinthes de nombres" - CE N'EST PAS DE LA CRYPTOGRAPHIE !
    has_numbers = visual_data.get("numbers") is not None
    has_target = visual_data.get("target") is not None
    has_movement_options = (
        visual_data.get("movement_options") is not None
        or visual_data.get("movement") is not None
    )
    is_fake_number_maze = has_numbers and (has_target or has_movement_options)

    # Rejeter les séquences, patterns, et faux labyrinthes
    if has_sequence:
        errors.append(
            "CODING INVALIDE: 'sequence' détectée - utiliser le type SEQUENCE, pas CODING"
        )
        return errors

    if has_pattern and not is_maze:
        errors.append(
            "CODING INVALIDE: 'pattern' sans cryptographie - utiliser le type PATTERN, pas CODING"
        )
        return errors

    if has_shapes:
        errors.append(
            "CODING INVALIDE: 'shapes' détectées - utiliser le type VISUAL, pas CODING"
        )
        return errors

    if is_fake_number_maze:
        errors.append(
            "CODING INVALIDE: 'numbers' + 'target' détectés - c'est un labyrinthe de nombres, "
            "pas de la cryptographie ! Utiliser le type SEQUENCE ou PUZZLE, pas CODING."
        )
        return errors

    # Rejeter aussi les défis avec uniquement des nombres et pas de message encodé
    if (
        has_numbers
        and not visual_data.get("encoded_message")
        and not visual_data.get("message")
    ):
        errors.append(
            "CODING INVALIDE: 'numbers' sans 'encoded_message' - CODING doit avoir un message secret à décoder, "
            "pas une liste de nombres."
        )
        return errors

    # Vérifier le type ou la présence d'éléments de cryptographie
    has_encoded_message = visual_data.get("encoded_message") or visual_data.get(
        "message"
    )
    has_crypto_key = (
        visual_data.get("key")
        or visual_data.get("partial_key")
        or visual_data.get("shift")
    )
    has_steps = visual_data.get("steps") and isinstance(visual_data.get("steps"), list)

    is_valid_crypto = (
        coding_type in valid_coding_types
        or is_maze
        or has_encoded_message
        or (has_crypto_key and has_encoded_message)
        or has_steps
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
            errors.append(
                f"MAZE: Le chemin '{correct_answer}' ne mène pas du départ {start} à l'arrivée {end}"
            )

    # Substitution : clé complète OU partial_key avec règle déductible (caesar, atbash, keyword)
    if coding_type == "substitution" and has_encoded_message:
        msg = (
            visual_data.get("encoded_message") or visual_data.get("message") or ""
        ).upper()
        decode_key = visual_data.get("key") or visual_data.get("partial_key") or {}
        rule_type = (
            visual_data.get("rule_type") or visual_data.get("deducible_rule") or ""
        ).lower()
        letters_in_msg = set(c for c in msg if c.isalpha())
        keys_upper = set(k.upper() for k in decode_key.keys())
        missing = letters_in_msg - keys_upper
        # Si règle déductible (César, Atbash, clé-mot), partial_key avec 3+ exemples suffit
        is_deducible = rule_type in (
            "caesar",
            "cesar",
            "atbash",
            "reverse",
            "keyword",
            "cle-mot",
        )
        if is_deducible:
            if len(decode_key) < 2:
                errors.append(
                    "SUBSTITUTION: Avec rule_type déductible, fournir au moins 2-3 exemples dans partial_key."
                )
        elif missing:
            errors.append(
                f"SUBSTITUTION INVALIDE: La clé ne couvre pas toutes les lettres du message ({sorted(missing)}). "
                "Fournir une clé complète OU rule_type (caesar/atbash/keyword) avec partial_key déductible."
            )
    return errors


# ---------------------------------------------------------------------------
# Dispatch : challenge_type -> validator (B3.5)
# ---------------------------------------------------------------------------

_VALIDATORS_BY_TYPE = {
    "PATTERN": validate_pattern_challenge,
    "SEQUENCE": validate_sequence_challenge,
    "PUZZLE": validate_puzzle_challenge,
    "GRAPH": validate_graph_challenge,
    "VISUAL": validate_spatial_challenge,
    "CODING": validate_coding_challenge,
    "RIDDLE": validate_riddle_challenge,
    "PROBABILITY": validate_probability_challenge,
    "CHESS": validate_chess_challenge,
}

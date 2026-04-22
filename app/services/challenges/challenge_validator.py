"""
Module de validation logique pour les challenges générés par IA.
Vérifie la cohérence entre visual_data, correct_answer et solution_explanation.
"""

import json
import math
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from app.core.logging_config import get_logger
from app.services.challenges.challenge_answer_quality import validate_challenge_choices
from app.services.challenges.challenge_coding_validation import (
    validate_coding_challenge,
)
from app.services.challenges.challenge_contract_policy import (
    apply_visual_contract_normalization,
    validate_choices_policy,
    validate_symmetry_canonical,
)
from app.services.challenges.challenge_deduction_solver import (
    analyze_deduction_uniqueness,
)
from app.services.challenges.challenge_difficulty_policy import (
    sanitize_leaky_title,
    validate_difficulty_structural_coherence,
    validate_title_difficulty_coherence,
)
from app.services.challenges.challenge_ordering_utils import (
    is_numeric_sort_solution,
    piece_label,
    split_ordered_answer_parts,
)
from app.services.challenges.challenge_pattern_sequence_validation import (
    _looks_numeric_pattern_grid,
    validate_pattern_challenge,
    validate_sequence_challenge,
)
from app.services.challenges.challenge_validation_analysis import (
    analyze_latin_square_pattern,
    analyze_pattern,
    analyze_sequence,
    compute_pattern_answers_multi,
    find_question_position_in_grid,
)
from app.services.challenges.maze_validator import solve_maze_bfs, validate_maze_path

logger = get_logger(__name__)

_GRAPH_WEIGHT_KEYS = (
    "weight",
    "cost",
    "time",
    "distance",
    "label",
    "value",
    "poids",
    "prix",
)
_GRAPH_ENDPOINT_FROM_KEYS = ("from", "source", "u", "start")
_GRAPH_ENDPOINT_TO_KEYS = ("to", "target", "v", "end")
_GRAPH_OBJECTIVE_KEYS = ("objective", "task", "question", "description")
_GRAPH_NUMBER_RE = re.compile(r"[-+]?\d+(?:[.,]\d+)?")
_GRAPH_ROUTE_SPLIT_RE = re.compile(r"\s*(?:<->|->|→|↔|–|—|-|à|to)\s*", re.I)


_CHESS_VALID_PIECES = frozenset(
    {"K", "k", "Q", "q", "R", "r", "B", "b", "N", "n", "P", "p"}
)
_CHESS_EMPTY = ""
_CHESS_KNIGHT_OFFSETS = (
    (-2, -1),
    (-2, 1),
    (-1, -2),
    (-1, 2),
    (1, -2),
    (1, 2),
    (2, -1),
    (2, 1),
)
_CHESS_KING_OFFSETS = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)
_CHESS_BISHOP_DIRECTIONS = ((-1, -1), (-1, 1), (1, -1), (1, 1))
_CHESS_ROOK_DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))


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
    title = str(challenge_data.get("title", "") or "")

    # Parser visual_data si nécessaire
    if isinstance(visual_data, str):
        try:
            visual_data = json.loads(visual_data)
        except json.JSONDecodeError:
            errors.append("visual_data n'est pas un JSON valide")
            return False, errors

    if not isinstance(visual_data, dict):
        visual_data = {}

    # IA9 — contrat visual (symétrie canonique) avant validateurs typés
    nv = apply_visual_contract_normalization(
        challenge_data.get("challenge_type", "") or challenge_type,
        visual_data,
    )
    challenge_data["visual_data"] = nv
    visual_data = nv

    dr_for_choices = None
    dr_raw = challenge_data.get("difficulty_rating")
    if isinstance(dr_raw, (int, float)) and 1.0 <= float(dr_raw) <= 5.0:
        dr_for_choices = float(dr_raw)
    errors.extend(
        validate_choices_policy(
            challenge_data.get("challenge_type", "") or challenge_type,
            dr_for_choices,
            challenge_data.get("choices"),
        )
    )

    # Dispatch par type de challenge (B3.5)
    validator = _VALIDATORS_BY_TYPE.get(challenge_type)
    if validator:
        type_errors = validator(visual_data, correct_answer, solution_explanation)
        errors.extend(type_errors)

    # Convertir en string si c'est une liste
    correct_answer_str = (
        ",".join(str(x) for x in correct_answer)
        if isinstance(correct_answer, list)
        else str(correct_answer) if correct_answer else ""
    )

    errors.extend(
        validate_challenge_choices(
            challenge_type,
            correct_answer_str,
            challenge_data.get("choices"),
        )
    )

    dr = challenge_data.get("difficulty_rating")
    if isinstance(dr, (int, float)) and 1.0 <= float(dr) <= 5.0:
        drf = float(dr)
        errors.extend(validate_title_difficulty_coherence(title, drf))
        errors.extend(
            validate_difficulty_structural_coherence(challenge_type, visual_data, drf)
        )

    # Validation générale
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
    piece_values = [piece_label(p).lower() for p in pieces]

    # Pour un puzzle, la réponse devrait être une liste ordonnée
    if correct_answer:
        # Gérer correct_answer comme liste ou string
        answer_parts = [p.lower() for p in split_ordered_answer_parts(correct_answer)]

        if len(answer_parts) != len(piece_values):
            errors.append(
                f"Puzzle incohérent: correct_answer contient {len(answer_parts)} éléments, "
                f"mais pieces contient {len(piece_values)} éléments"
            )

        # Vérifier que tous les éléments de pieces sont dans la réponse
        missing = set(piece_values) - set(answer_parts)
        trivial_numeric_sort = is_numeric_sort_solution(pieces, correct_answer)
        if trivial_numeric_sort:
            errors.append(
                "PUZZLE trivial: correct_answer correspond au tri numerique croissant/decroissant des pieces. "
                "Le puzzle doit exiger une regle d'ordre non reductible a un simple tri."
            )

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


def _graph_node_key(node: Any, index: int) -> str:
    if isinstance(node, dict):
        value = node.get("label", node.get("value", node.get("id", index)))
    else:
        value = node
    return str(value).strip().upper()


def _first_present(data: Dict[str, Any], keys: Tuple[str, ...]) -> Any:
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return None


def _parse_graph_number(value: Any, *, allow_embedded: bool = False) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None

    text = str(value).strip().replace(" ", "").replace("\u202f", "")
    if not text:
        return None

    match = (
        _GRAPH_NUMBER_RE.search(text)
        if allow_embedded
        else _GRAPH_NUMBER_RE.fullmatch(text)
    )
    if not match:
        return None

    try:
        return float(match.group(0).replace(",", "."))
    except ValueError:
        return None


def _graph_text_mentions_mst(visual_data: Dict[str, Any], explanation: str) -> bool:
    texts = [str(explanation or "")]
    texts.extend(str(visual_data.get(key) or "") for key in _GRAPH_OBJECTIVE_KEYS)
    joined = " ".join(texts).lower()

    return (
        "mst" in joined
        or "minimum_spanning_tree" in joined
        or "minimum spanning" in joined
        or (
            "arbre" in joined
            and "couvrant" in joined
            and ("minimal" in joined or "minimum" in joined)
        )
    )


def _graph_endpoint_index(
    raw_value: Any,
    node_index_by_key: Dict[str, int],
    node_count: int,
) -> Optional[int]:
    if isinstance(raw_value, bool) or raw_value is None:
        return None

    if isinstance(raw_value, int) and 0 <= raw_value < node_count:
        return raw_value

    key = str(raw_value).strip().upper()
    return node_index_by_key.get(key)


def _split_graph_route(raw_value: Any) -> Optional[Tuple[str, str]]:
    if not isinstance(raw_value, str):
        return None
    parts = [
        part.strip() for part in _GRAPH_ROUTE_SPLIT_RE.split(raw_value) if part.strip()
    ]
    if len(parts) < 2:
        return None
    return parts[0], parts[1]


def _weighted_graph_edges(
    edges: List[Any],
    node_index_by_key: Dict[str, int],
    node_count: int,
) -> Optional[List[Tuple[int, int, float]]]:
    weighted_edges: List[Tuple[int, int, float]] = []

    for edge in edges:
        from_raw: Any
        to_raw: Any
        weight_raw: Any

        if isinstance(edge, dict):
            from_raw = _first_present(edge, _GRAPH_ENDPOINT_FROM_KEYS)
            to_raw = _first_present(edge, _GRAPH_ENDPOINT_TO_KEYS)
            route = _split_graph_route(
                edge.get("route") or edge.get("edge") or edge.get("name")
            )
            if route is not None:
                from_raw = from_raw if from_raw is not None else route[0]
                to_raw = to_raw if to_raw is not None else route[1]
            weight_raw = _first_present(edge, _GRAPH_WEIGHT_KEYS)
        elif isinstance(edge, (list, tuple)) and len(edge) >= 3:
            from_raw, to_raw, weight_raw = edge[0], edge[1], edge[2]
        else:
            return None

        from_index = _graph_endpoint_index(from_raw, node_index_by_key, node_count)
        to_index = _graph_endpoint_index(to_raw, node_index_by_key, node_count)
        weight = _parse_graph_number(weight_raw)
        if from_index is None or to_index is None or weight is None:
            return None

        weighted_edges.append((from_index, to_index, weight))

    return weighted_edges


def _minimum_spanning_tree_total(
    node_count: int, weighted_edges: List[Tuple[int, int, float]]
) -> Optional[float]:
    parent = list(range(node_count))
    rank = [0] * node_count

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(left: int, right: int) -> bool:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return False
        if rank[left_root] < rank[right_root]:
            parent[left_root] = right_root
        elif rank[left_root] > rank[right_root]:
            parent[right_root] = left_root
        else:
            parent[right_root] = left_root
            rank[left_root] += 1
        return True

    total = 0.0
    selected_edges = 0
    for from_index, to_index, weight in sorted(
        weighted_edges, key=lambda item: item[2]
    ):
        if union(from_index, to_index):
            total += weight
            selected_edges += 1
            if selected_edges == node_count - 1:
                break

    if selected_edges != node_count - 1:
        return None
    return total


def _graph_text_mentions_shortest_path(
    visual_data: Dict[str, Any], explanation: str
) -> bool:
    texts = [str(explanation or "")]
    texts.extend(str(visual_data.get(key) or "") for key in _GRAPH_OBJECTIVE_KEYS)
    joined = " ".join(texts).lower()

    return (
        "shortest_path" in joined
        or "shortest path" in joined
        or "plus court" in joined
        or "chemin minimal" in joined
        or "coût minimal" in joined
        or "cout minimal" in joined
        or "route la plus" in joined
        or "trajet le plus rapide" in joined
    )


def _extract_shortest_path_endpoints(
    visual_data: Dict[str, Any],
    explanation: str,
    node_index_by_key: Dict[str, int],
) -> Optional[Tuple[int, int]]:
    source = (
        visual_data.get("source")
        or visual_data.get("start")
        or visual_data.get("origin")
        or visual_data.get("from")
    )
    target = (
        visual_data.get("target")
        or visual_data.get("end")
        or visual_data.get("destination")
        or visual_data.get("to")
    )

    source_index = _graph_endpoint_index(
        source, node_index_by_key, len(node_index_by_key)
    )
    target_index = _graph_endpoint_index(
        target, node_index_by_key, len(node_index_by_key)
    )
    if source_index is not None and target_index is not None:
        return source_index, target_index

    texts = [str(explanation or "")]
    texts.extend(str(visual_data.get(key) or "") for key in _GRAPH_OBJECTIVE_KEYS)
    joined = " ".join(texts)
    node_pattern = "|".join(re.escape(key) for key in node_index_by_key)
    if not node_pattern:
        return None

    endpoint_patterns = (
        rf"\b(?:de|from)\s+({node_pattern})\s+(?:à|a|to|jusqu['’]?\s*a?|vers)\s+({node_pattern})\b",
        rf"\b({node_pattern})\s*(?:→|->|à|to)\s*({node_pattern})\b",
    )
    for pattern in endpoint_patterns:
        match = re.search(pattern, joined, re.I)
        if match:
            left = node_index_by_key.get(match.group(1).upper())
            right = node_index_by_key.get(match.group(2).upper())
            if left is not None and right is not None:
                return left, right
    return None


def _shortest_path_total(
    node_count: int,
    weighted_edges: List[Tuple[int, int, float]],
    source_index: int,
    target_index: int,
    *,
    directed: bool = False,
) -> Optional[float]:
    distances = [math.inf] * node_count
    visited = [False] * node_count
    adjacency: List[List[Tuple[int, float]]] = [[] for _ in range(node_count)]
    for from_index, to_index, weight in weighted_edges:
        if weight < 0:
            return None
        adjacency[from_index].append((to_index, weight))
        if not directed:
            adjacency[to_index].append((from_index, weight))

    distances[source_index] = 0.0
    for _ in range(node_count):
        current = min(
            (idx for idx in range(node_count) if not visited[idx]),
            key=lambda idx: distances[idx],
            default=None,
        )
        if current is None or math.isinf(distances[current]):
            break
        if current == target_index:
            return distances[current]
        visited[current] = True
        for neighbor, weight in adjacency[current]:
            candidate = distances[current] + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate

    return None if math.isinf(distances[target_index]) else distances[target_index]


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
    node_keys = [_graph_node_key(node, index) for index, node in enumerate(nodes)]
    node_names = set(node_keys)
    node_index_by_key = {key: index for index, key in enumerate(node_keys)}

    # Vérifier que toutes les arêtes référencent des nœuds existants
    if edges and isinstance(edges, list):
        for edge in edges:
            if isinstance(edge, dict):
                route = _split_graph_route(
                    edge.get("route") or edge.get("edge") or edge.get("name")
                )
                from_raw = _first_present(edge, _GRAPH_ENDPOINT_FROM_KEYS)
                to_raw = _first_present(edge, _GRAPH_ENDPOINT_TO_KEYS)
                from_node = str(
                    from_raw if from_raw is not None else route[0] if route else ""
                ).upper()
                to_node = str(
                    to_raw if to_raw is not None else route[1] if route else ""
                ).upper()
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

    if (
        edges
        and isinstance(edges, list)
        and _graph_text_mentions_mst(visual_data, explanation)
    ):
        weighted_edges = _weighted_graph_edges(edges, node_index_by_key, len(nodes))
        answer_total = _parse_graph_number(correct_answer, allow_embedded=True)
        if weighted_edges is None:
            errors.append(
                "GRAPH arbre couvrant minimal: chaque arête doit avoir deux nœuds valides et un poids numérique."
            )
        elif answer_total is None:
            errors.append(
                "GRAPH arbre couvrant minimal: correct_answer doit contenir le coût total numérique."
            )
        else:
            expected_total = _minimum_spanning_tree_total(len(nodes), weighted_edges)
            if expected_total is None:
                errors.append(
                    "GRAPH arbre couvrant minimal: le graphe pondéré doit être connecté."
                )
            elif not math.isclose(
                expected_total, answer_total, rel_tol=1e-9, abs_tol=1e-9
            ):
                expected_display = (
                    int(expected_total)
                    if expected_total.is_integer()
                    else round(expected_total, 6)
                )
                errors.append(
                    "GRAPH arbre couvrant minimal: correct_answer incohérent. "
                    f"Attendu {expected_display}, reçu {correct_answer}."
                )

    if (
        edges
        and isinstance(edges, list)
        and _graph_text_mentions_shortest_path(visual_data, explanation)
    ):
        weighted_edges = _weighted_graph_edges(edges, node_index_by_key, len(nodes))
        answer_total = _parse_graph_number(correct_answer, allow_embedded=True)
        endpoints = _extract_shortest_path_endpoints(
            visual_data, explanation, node_index_by_key
        )
        if (
            weighted_edges is not None
            and answer_total is not None
            and endpoints is not None
        ):
            expected_total = _shortest_path_total(
                len(nodes),
                weighted_edges,
                endpoints[0],
                endpoints[1],
                directed=bool(visual_data.get("directed")),
            )
            if expected_total is not None and not math.isclose(
                expected_total, answer_total, rel_tol=1e-9, abs_tol=1e-9
            ):
                expected_display = (
                    int(expected_total)
                    if expected_total.is_integer()
                    else round(expected_total, 6)
                )
                errors.append(
                    "GRAPH chemin minimal: correct_answer incohérent. "
                    f"Attendu {expected_display}, reçu {correct_answer}."
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

        errors.extend(validate_symmetry_canonical(visual_data))

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
    difficulty_raw = challenge_data.get("difficulty_rating")
    difficulty_rating = (
        float(difficulty_raw)
        if isinstance(difficulty_raw, (int, float))
        and 1.0 <= float(difficulty_raw) <= 5.0
        else None
    )

    # Parser visual_data si nécessaire
    if isinstance(visual_data, str):
        try:
            visual_data = json.loads(visual_data)
        except json.JSONDecodeError:
            return corrected

    title = str(corrected.get("title", "") or "")
    sanitized_title = sanitize_leaky_title(
        challenge_type,
        title,
        difficulty_rating,
        visual_data if isinstance(visual_data, dict) else {},
    )
    if sanitized_title and sanitized_title != title:
        logger.info(
            "Correction automatique titre (fuite de règle): '{}' → '{}'",
            title,
            sanitized_title,
        )
        corrected["title"] = sanitized_title

    # Correction pour PATTERN
    if challenge_type == "PATTERN" and visual_data and "grid" in visual_data:
        grid = visual_data.get("grid", [])
        if grid:
            # Plusieurs "?" → format "O, O, X, O"
            question_count = 0
            for row in grid:
                if not isinstance(row, (list, tuple)):
                    continue
                for cell in row:
                    if cell == "?" or (isinstance(cell, str) and "?" in str(cell)):
                        question_count += 1
            if question_count > 1:
                if not _looks_numeric_pattern_grid(grid):
                    expected_multi = compute_pattern_answers_multi(grid)
                    if expected_multi:
                        logger.info(
                            "Correction automatique PATTERN (multi): correct_answer = '{}'",
                            expected_multi,
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
                            "Correction automatique PATTERN: correct_answer = '{}'",
                            expected_answer,
                        )
                        corrected["correct_answer"] = expected_answer

                        # Mettre à jour l'explication si elle est contradictoire (expected_answer non None)
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
                            "Correction automatique VISUAL: correct_answer changé de '{}' à '{}'",
                            corrected.get("correct_answer"),
                            expected_answer,
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
                                        "Correction automatique titre: '{}' → '{}'",
                                        title,
                                        new_title,
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
                        "Correction automatique SEQUENCE: correct_answer changé de '{}' à '{}'",
                        current_answer,
                        expected_answer,
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
                        "Correction automatique MAZE: chemin invalide '{}' → '{}'",
                        current_answer,
                        correct_path,
                    )
                    corrected["correct_answer"] = correct_path
                    corrected["solution_explanation"] = (
                        f"Pour aller du départ {start} à l'arrivée {end}, "
                        f"le chemin optimal est : {correct_path}. "
                        f"Ce chemin évite tous les murs (#) et utilise uniquement les cases libres."
                    )
            else:
                logger.warning(
                    "Impossible de trouver un chemin valide dans le labyrinthe de {} à {}",
                    start,
                    end,
                )

    # Correction pour SYMMETRY (visual_data.type == "symmetry")
    # Cas Sentry #110986970 : LLM génère un layout sans cellule marquée question
    if (
        challenge_type == "VISUAL"
        and isinstance(visual_data, dict)
        and visual_data.get("type") == "symmetry"
    ):
        layout = visual_data.get("layout", [])
        has_question = any(
            isinstance(item, dict)
            and (item.get("question") or item.get("shape") == "?")
            for item in layout
        )
        if not has_question and layout:
            # Marquer le premier item côté droit comme cellule-question
            for item in layout:
                if isinstance(item, dict) and item.get("side") == "right":
                    item["question"] = True
                    logger.info(
                        "Correction automatique SYMMETRY: cellule-question marquée sur le côté droit"
                    )
                    corrected["visual_data"] = visual_data
                    break

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
    expected = _compute_weighted_two_draw_different_color_probability(visual_data)
    provided = _parse_probability_answer_fraction(correct_answer)
    if expected is not None and provided is not None:
        tolerance = (
            Fraction(5, 100000) if "%" in str(correct_answer) else Fraction(1, 1000000)
        )
        if abs(expected - provided) > tolerance:
            errors.append(
                "PROBABILITY: correct_answer incohérent avec visual_data. "
                f"Attendu environ {_format_probability_percent(expected)}, reçu {correct_answer}."
            )
    return errors


_PROBABILITY_CONTAINER_META_KEYS = {
    "total",
    "selection_probability",
    "selectionprobability",
    "probability",
    "weight",
}


def _parse_probability_answer_fraction(raw: Any) -> Optional[Fraction]:
    if raw is None:
        return None
    text = str(raw).strip().strip("$").replace(" ", "").replace(",", ".")
    if not text:
        return None
    text = text.replace("\\left", "").replace("\\right", "")
    latex_match = re.fullmatch(
        r"\\(?:dfrac|frac|tfrac)\{([+-]?\d+(?:\.\d+)?)\}\{([+-]?\d+(?:\.\d+)?)\}",
        text,
    )
    if latex_match:
        try:
            denominator = Fraction(latex_match.group(2))
            return (
                Fraction(latex_match.group(1)) / denominator
                if denominator != 0
                else None
            )
        except (ValueError, ZeroDivisionError):
            return None

    is_percent = text.endswith("%")
    if is_percent:
        text = text[:-1]
    try:
        if "/" in text:
            numerator, denominator = text.split("/", 1)
            den = Fraction(denominator)
            value = Fraction(numerator) / den if den != 0 else None
        else:
            value = Fraction(text)
    except (ValueError, ZeroDivisionError):
        return None
    if value is None:
        return None
    return value / 100 if is_percent else value


def _parse_draw_count(raw: Any) -> int:
    if isinstance(raw, bool) or raw is None:
        return 0
    if isinstance(raw, (int, float)):
        return int(raw)
    match = re.search(r"\d+", str(raw))
    return int(match.group(0)) if match else 0


def _parse_draws_without_replacement_count(visual_data: Dict[str, Any]) -> int:
    explicit = visual_data.get("draws_without_replacement")
    if explicit is not None:
        return _parse_draw_count(explicit)

    raw_draws = visual_data.get("draws")
    if raw_draws is None:
        return 0

    draw_text = str(raw_draws).lower()
    if (
        "without replacement" not in draw_text
        and "sans remise" not in draw_text
        and "non remise" not in draw_text
    ):
        return 0
    return _parse_draw_count(raw_draws)


def _format_probability_percent(value: Fraction) -> str:
    return f"{float(value * 100):.2f}%"


def _numeric_fraction(raw: Any) -> Optional[Fraction]:
    if isinstance(raw, bool) or raw is None:
        return None
    try:
        return Fraction(str(raw))
    except (ValueError, ZeroDivisionError):
        return None


def _probability_population_counts(composition: Dict[str, Any]) -> List[int]:
    counts: List[int] = []
    for key, value in composition.items():
        normalized_key = str(key).lower().replace("_", "")
        if normalized_key in _PROBABILITY_CONTAINER_META_KEYS:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if value > 0:
            counts.append(int(value))
    return counts


def _iter_probability_containers(
    visual_data: Dict[str, Any],
) -> List[Tuple[str, List[int], Optional[Fraction]]]:
    containers: List[Tuple[str, List[int], Optional[Fraction]]] = []
    urns = visual_data.get("urns")
    if isinstance(urns, dict):
        source = urns
    else:
        source = {
            key: value
            for key, value in visual_data.items()
            if isinstance(value, dict)
            and str(key).lower().replace("-", "_").startswith(("box_", "urn_", "urne_"))
        }

    for label, composition in source.items():
        if not isinstance(composition, dict):
            continue
        counts = _probability_population_counts(composition)
        if len(counts) < 2:
            continue
        declared_total = _numeric_fraction(composition.get("total"))
        if declared_total is not None and declared_total != sum(counts):
            return []
        weight = _numeric_fraction(
            composition.get("selection_probability")
            or composition.get("selectionProbability")
            or composition.get("probability")
            or composition.get("weight")
        )
        containers.append((str(label), counts, weight))
    return containers


def _event_targets_different_colors(visual_data: Dict[str, Any]) -> bool:
    text = " ".join(
        str(visual_data.get(key, ""))
        for key in ("event", "question", "description", "draws")
    ).lower()
    return (
        "different colors" in text
        or "couleurs differentes" in text
        or "couleurs différentes" in text
    )


def _compute_weighted_two_draw_different_color_probability(
    visual_data: Dict[str, Any],
) -> Optional[Fraction]:
    draws = _parse_draws_without_replacement_count(visual_data)
    if draws != 2 or not _event_targets_different_colors(visual_data):
        return None

    containers = _iter_probability_containers(visual_data)
    if len(containers) < 1:
        return None

    raw_weights = [weight for _label, _counts, weight in containers]
    if all(weight is None for weight in raw_weights):
        weights = [Fraction(1, len(containers)) for _ in containers]
    elif all(weight is not None for weight in raw_weights):
        weights = [weight for weight in raw_weights if weight is not None]
        total_weight = sum(weights, Fraction(0, 1))
        if total_weight <= 0:
            return None
        if total_weight != 1:
            weights = [weight / total_weight for weight in weights]
    else:
        return None

    expected = Fraction(0, 1)
    for (_label, counts, _weight), weight in zip(containers, weights):
        total = sum(counts)
        if total < 2:
            return None
        same_color = sum(
            Fraction(count * (count - 1), total * (total - 1)) for count in counts
        )
        expected += weight * (1 - same_color)
    return expected


def validate_deduction_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide un défi DEDUCTION (grille logique type Einstein / Zebra).

    Contrat structurel + **bijection par catégorie** : sur chaque colonne, une valeur du
    domaine ne peut être assignée qu'à une seule entité de la première catégorie ; si la
    taille du domaine égale le nombre de lignes, chaque valeur du domaine doit apparaître
    exactement une fois (permutation). Ne prouve pas la cohérence avec les ``clues`` ni
    l'unicité logique globale du puzzle.
    """
    errors: List[str] = []
    _ = explanation

    if not visual_data:
        errors.append("DEDUCTION: visual_data manquant")
        return errors

    if str(visual_data.get("type", "")).lower() != "logic_grid":
        errors.append("DEDUCTION: visual_data.type doit être 'logic_grid'")

    entities = visual_data.get("entities")
    if not isinstance(entities, dict) or len(entities) < 2:
        errors.append(
            "DEDUCTION: entities doit contenir au moins 2 catégories (listes non vides)"
        )
        return errors

    category_order = list(entities.keys())
    categories: List[Tuple[str, List[str]]] = []
    for cat in category_order:
        vals = entities[cat]
        if not isinstance(vals, list) or len(vals) == 0:
            errors.append(f"DEDUCTION: entities['{cat}'] doit être une liste non vide")
            return errors
        categories.append((cat, [str(v).strip() for v in vals if v is not None]))

    clues = visual_data.get("clues", [])
    if not isinstance(clues, list) or len(clues) < 2:
        errors.append(
            "DEDUCTION: fournir au moins 2 indices (clues) pour guider la déduction"
        )

    if not correct_answer or not str(correct_answer).strip():
        errors.append("DEDUCTION: correct_answer vide")
        return errors

    parts = [p.strip() for p in str(correct_answer).split(",") if p.strip()]
    if not parts:
        errors.append("DEDUCTION: correct_answer sans association valide")
        return errors

    n_cat = len(categories)
    first_cat_allowed = {x.lower() for x in categories[0][1]}
    expected_n = len(first_cat_allowed)

    if len(parts) != expected_n:
        errors.append(
            f"DEDUCTION: attendu {expected_n} associations (une par entité de "
            f"« {category_order[0]} »), reçu {len(parts)}"
        )

    first_segments: List[str] = []
    valid_rows: List[List[str]] = []

    for part in parts:
        segs = [s.strip() for s in part.split(":")]
        if len(segs) != n_cat:
            errors.append(
                f"DEDUCTION: chaque association doit avoir {n_cat} segments ':' "
                f"(ordre des catégories: {category_order}), reçu: {part!r}"
            )
            continue
        valid_rows.append(segs)
        first_segments.append(segs[0].lower())
        for i, (_cat, allowed) in enumerate(categories):
            val = segs[i]
            allowed_l = {a.lower() for a in allowed}
            if val.lower() not in allowed_l:
                errors.append(
                    f"DEDUCTION: la valeur {val!r} n'appartient pas à la catégorie "
                    f"'{category_order[i]}' pour l'association {part!r}"
                )

    if len(first_segments) == expected_n and len(set(first_segments)) != len(
        first_segments
    ):
        errors.append(
            "DEDUCTION: une même entité (première catégorie) apparaît plusieurs fois"
        )

    seen_first = set(first_segments)
    missing_entities = first_cat_allowed - seen_first
    if missing_entities:
        errors.append(
            "DEDUCTION: entités manquantes dans correct_answer (première catégorie): "
            f"{sorted(missing_entities)}"
        )

    # Bijection structurelle : pas de valeur réutilisée dans une même catégorie (colonnes).
    if valid_rows:
        for j in range(n_cat):
            col_vals = [row[j].lower() for row in valid_rows]
            if len(col_vals) != len(set(col_vals)):
                errors.append(
                    f"DEDUCTION: la catégorie « {category_order[j]} » impose une assignation "
                    f"one-to-one : une même valeur apparaît pour plusieurs lignes "
                    f"(ex. deux personnes avec la même valeur)."
                )

    # Si |domaine catégorie j| == nombre de lignes complètes, exiger une permutation exacte.
    if len(valid_rows) == expected_n:
        for j, (_cat, allowed) in enumerate(categories):
            allowed_l = [str(a).strip() for a in allowed if a is not None]
            allowed_set = {a.lower() for a in allowed_l}
            col_set = {row[j].lower() for row in valid_rows}
            if len(allowed_set) == expected_n and len(col_set) == expected_n:
                if col_set != allowed_set:
                    errors.append(
                        f"DEDUCTION: pour « {category_order[j]} », chaque valeur du domaine "
                        f"doit apparaître exactement une fois sur les {expected_n} lignes "
                        f"(bijection) ; obtenu {sorted(col_set)}, attendu {sorted(allowed_set)}"
                    )

    uniqueness = analyze_deduction_uniqueness(visual_data, correct_answer)
    if uniqueness.checked:
        if uniqueness.solution_count == 0:
            errors.append(
                "DEDUCTION: les indices reconnus ne permettent aucune solution cohérente "
                "(contraintes contradictoires)."
            )
        elif uniqueness.solution_count > 1:
            errors.append(
                "DEDUCTION: les indices reconnus ne mènent pas à une solution unique "
                "(plusieurs plannings restent possibles). Ajouter un indice discriminant."
            )
        elif uniqueness.expected_answer_matches is False:
            errors.append(
                "DEDUCTION: correct_answer ne correspond pas à l'unique solution "
                "déduite des indices reconnus."
            )

    return errors


def _chess_piece_at(board: List[List[str]], row: int, col: int) -> str:
    if 0 <= row < 8 and 0 <= col < 8:
        return board[row][col]
    return _CHESS_EMPTY


def _chess_piece_color(piece: str) -> Optional[str]:
    if not piece:
        return None
    return "white" if piece.isupper() else "black"


def _chess_find_piece_positions(
    board: List[List[str]], target_piece: str
) -> List[Tuple[int, int]]:
    positions: List[Tuple[int, int]] = []
    for row_index, row in enumerate(board):
        for col_index, piece in enumerate(row):
            if piece == target_piece:
                positions.append((row_index, col_index))
    return positions


def _chess_is_attacked_by(
    board: List[List[str]], target_row: int, target_col: int, attacker_color: str
) -> bool:
    attacker_is_white = attacker_color == "white"
    pawn_piece = "P" if attacker_is_white else "p"
    knight_piece = "N" if attacker_is_white else "n"
    king_piece = "K" if attacker_is_white else "k"
    bishop_piece = "B" if attacker_is_white else "b"
    rook_piece = "R" if attacker_is_white else "r"
    queen_piece = "Q" if attacker_is_white else "q"

    pawn_source_row = target_row + (1 if attacker_is_white else -1)
    for pawn_source_col in (target_col - 1, target_col + 1):
        if _chess_piece_at(board, pawn_source_row, pawn_source_col) == pawn_piece:
            return True

    for row_delta, col_delta in _CHESS_KNIGHT_OFFSETS:
        if (
            _chess_piece_at(board, target_row + row_delta, target_col + col_delta)
            == knight_piece
        ):
            return True

    for row_delta, col_delta in _CHESS_KING_OFFSETS:
        if (
            _chess_piece_at(board, target_row + row_delta, target_col + col_delta)
            == king_piece
        ):
            return True

    for row_delta, col_delta in _CHESS_BISHOP_DIRECTIONS:
        row = target_row + row_delta
        col = target_col + col_delta
        while 0 <= row < 8 and 0 <= col < 8:
            piece = _chess_piece_at(board, row, col)
            if piece:
                if piece in (bishop_piece, queen_piece):
                    return True
                break
            row += row_delta
            col += col_delta

    for row_delta, col_delta in _CHESS_ROOK_DIRECTIONS:
        row = target_row + row_delta
        col = target_col + col_delta
        while 0 <= row < 8 and 0 <= col < 8:
            piece = _chess_piece_at(board, row, col)
            if piece:
                if piece in (rook_piece, queen_piece):
                    return True
                break
            row += row_delta
            col += col_delta

    return False


def _validate_chess_position_legality(board: List[List[str]], turn: str) -> List[str]:
    errors: List[str] = []
    piece_count = sum(1 for row in board for piece in row if piece)
    if not (4 <= piece_count <= 8):
        errors.append(
            f"CHESS: position tactique attendue avec 4 à 8 pièces, reçu {piece_count}"
        )

    white_kings = _chess_find_piece_positions(board, "K")
    black_kings = _chess_find_piece_positions(board, "k")
    if len(white_kings) != 1:
        errors.append(
            f"CHESS: il doit y avoir exactement un roi blanc, reçu {len(white_kings)}"
        )
    if len(black_kings) != 1:
        errors.append(
            f"CHESS: il doit y avoir exactement un roi noir, reçu {len(black_kings)}"
        )
    if errors:
        return errors

    if turn == "white":
        black_king_row, black_king_col = black_kings[0]
        if _chess_is_attacked_by(board, black_king_row, black_king_col, "white"):
            errors.append(
                "CHESS: roi noir déjà en échec alors que c'est aux Blancs de jouer"
            )
    elif turn == "black":
        white_king_row, white_king_col = white_kings[0]
        if _chess_is_attacked_by(board, white_king_row, white_king_col, "black"):
            errors.append(
                "CHESS: roi blanc déjà en échec alors que c'est aux Noirs de jouer"
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

    board_is_rectangular = True
    normalized_board: List[List[str]] = []
    if len(board) != 8:
        errors.append(f"CHESS: board doit avoir 8 rangées, reçu {len(board)}")
        board_is_rectangular = False
    for i, row in enumerate(board):
        if not isinstance(row, (list, tuple)) or len(row) != 8:
            errors.append(f"CHESS: board[{i}] doit être une liste de 8 éléments")
            board_is_rectangular = False
            break
        normalized_row: List[str] = []
        for j, cell in enumerate(row):
            val = str(cell).strip() if cell else ""
            normalized_row.append(val)
            if val and val not in _CHESS_VALID_PIECES:
                errors.append(f"CHESS: pièce invalide '{cell}' en [{i},{j}]")
                board_is_rectangular = False
                break
        normalized_board.append(normalized_row)

    turn = visual_data.get("turn", "").lower()
    if turn not in ("white", "black"):
        errors.append(f"CHESS: turn doit être 'white' ou 'black', reçu '{turn}'")

    objective = visual_data.get("objective", "")
    valid_obj = ("mat_en_1", "mat_en_2", "mat_en_3", "meilleur_coup")
    if objective not in valid_obj:
        errors.append(f"CHESS: objective doit être parmi {valid_obj}")

    if not correct_answer or not str(correct_answer).strip():
        errors.append("CHESS: correct_answer est vide (notation algébrique attendue)")

    if (
        board_is_rectangular
        and len(normalized_board) == 8
        and turn in ("white", "black")
    ):
        errors.extend(_validate_chess_position_legality(normalized_board, turn))

    return errors


# validate_coding_challenge : voir challenge_coding_validation (I5)


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
    "DEDUCTION": validate_deduction_challenge,
}

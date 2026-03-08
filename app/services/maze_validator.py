"""
Helpers de validation pour les labyrinthes (challenges CODING type maze).
Logique pure : résolution BFS et validation de chemin.
"""

from collections import deque
from typing import List, Optional


def solve_maze_bfs(
    maze: List[List[str]], start: List[int], end: List[int]
) -> Optional[str]:
    """
    Résout un labyrinthe avec BFS et retourne le chemin en directions.

    Args:
        maze: Grille du labyrinthe (# = mur, espace = chemin)
        start: Position de départ [row, col]
        end: Position d'arrivée [row, col]

    Returns:
        Chemin en directions (ex: "BAS, BAS, DROITE, DROITE") ou None si pas de solution
    """
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
    directions = [(-1, 0, "HAUT"), (1, 0, "BAS"), (0, -1, "GAUCHE"), (0, 1, "DROITE")]

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
            cell = (
                maze[new_row][new_col]
                if isinstance(maze[new_row], list)
                else maze[new_row]
            )
            if isinstance(cell, list):
                cell = cell[new_col] if new_col < len(cell) else "#"

            if cell in ["#", "█", "1"]:
                continue

            # Ajouter à la file
            visited.add((new_row, new_col))
            queue.append((new_row, new_col, path + [direction]))

    return None  # Pas de chemin trouvé


def validate_maze_path(
    maze: List[List[str]], start: List[int], end: List[int], path_str: str
) -> bool:
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
        "haut": (-1, 0),
        "up": (-1, 0),
        "h": (-1, 0),
        "bas": (1, 0),
        "down": (1, 0),
        "b": (1, 0),
        "gauche": (0, -1),
        "left": (0, -1),
        "g": (0, -1),
        "droite": (0, 1),
        "right": (0, 1),
        "d": (0, 1),
    }

    # Extraire les directions du chemin
    path_parts = [
        p.strip().lower() for p in path_str.replace(",", " ").split() if p.strip()
    ]

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
            cell = cell[new_col] if new_col < len(cell) else "#"
        elif isinstance(cell, str) and new_col < len(cell):
            cell = cell[new_col]
        else:
            cell = "#"

        if cell in ["#", "█", "1"]:
            return False

        row, col = new_row, new_col

    # Vérifier si on est arrivé à destination
    return row == end[0] and col == end[1]

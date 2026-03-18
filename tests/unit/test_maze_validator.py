"""
Tests de caractérisation pour les helpers maze (solve_maze_bfs, validate_maze_path).
Figent le comportement avant extraction depuis challenge_validator.
"""

import pytest

from app.services.challenges.maze_validator import solve_maze_bfs, validate_maze_path


class TestSolveMazeBfs:
    """Tests pour solve_maze_bfs."""

    def test_simple_path_found(self):
        """Chemin simple de départ à arrivée."""
        maze = [
            [" ", " ", "#"],
            ["#", " ", " "],
            [" ", " ", " "],
        ]
        path = solve_maze_bfs(maze, [0, 0], [2, 2])
        assert path is not None
        assert validate_maze_path(maze, [0, 0], [2, 2], path)

    def test_already_at_end(self):
        """Départ = arrivée."""
        maze = [[" ", " "], [" ", " "]]
        assert solve_maze_bfs(maze, [0, 0], [0, 0]) == "DÉJÀ À L'ARRIVÉE"

    def test_no_solution(self):
        """Pas de chemin possible."""
        maze = [
            [" ", "#", " "],
            ["#", "#", "#"],
            [" ", "#", " "],
        ]
        assert solve_maze_bfs(maze, [0, 0], [2, 2]) is None

    def test_empty_maze_returns_none(self):
        """Grille vide."""
        assert solve_maze_bfs([], [0, 0], [1, 1]) is None

    def test_invalid_start_returns_none(self):
        """Start hors limites."""
        maze = [[" ", " "], [" ", " "]]
        assert solve_maze_bfs(maze, [-1, 0], [1, 1]) is None
        assert solve_maze_bfs(maze, [0, 5], [1, 1]) is None

    def test_invalid_end_returns_none(self):
        """End hors limites."""
        maze = [[" ", " "], [" ", " "]]
        assert solve_maze_bfs(maze, [0, 0], [5, 5]) is None

    def test_wall_characters(self):
        """Murs reconnus : #, █, 1."""
        maze = [[" ", "#", " "], [" ", "█", " "], [" ", "1", " "]]
        assert solve_maze_bfs(maze, [0, 0], [0, 2]) is None
        maze2 = [[" ", " ", " "], [" ", " ", " "]]
        assert solve_maze_bfs(maze2, [0, 0], [1, 2]) is not None


class TestValidateMazePath:
    """Tests pour validate_maze_path."""

    def test_valid_path(self):
        """Chemin valide mène à l'arrivée."""
        maze = [
            [" ", " ", "#"],
            ["#", " ", " "],
            [" ", " ", " "],
        ]
        # Path from solve_maze_bfs for this maze (DROITE avoids wall at [1,0])
        assert validate_maze_path(maze, [0, 0], [2, 2], "DROITE, BAS, BAS, DROITE")

    def test_valid_path_french_directions(self):
        """Directions en français."""
        maze = [[" ", " "], [" ", " "]]
        assert validate_maze_path(maze, [0, 0], [1, 1], "bas, droite")
        assert validate_maze_path(maze, [0, 0], [1, 0], "BAS")

    def test_invalid_path_hits_wall(self):
        """Chemin traverse un mur."""
        maze = [[" ", "#", " "], [" ", " ", " "]]
        assert not validate_maze_path(maze, [0, 0], [1, 2], "DROITE, DROITE, BAS")

    def test_invalid_path_wrong_destination(self):
        """Chemin valide mais n'arrive pas à la cible."""
        maze = [[" ", " "], [" ", " "]]
        assert not validate_maze_path(maze, [0, 0], [1, 1], "BAS")  # arrive [1,0]

    def test_empty_input_returns_false(self):
        """Entrées vides."""
        maze = [[" ", " "], [" ", " "]]
        assert not validate_maze_path(maze, [0, 0], [1, 1], "")
        assert not validate_maze_path([], [0, 0], [1, 1], "BAS")

    def test_direction_aliases(self):
        """Alias up/down/left/right, h/b/g/d."""
        maze = [[" ", " "], [" ", " "]]
        assert validate_maze_path(maze, [0, 0], [1, 0], "down")
        assert validate_maze_path(maze, [0, 0], [0, 1], "right")
        assert validate_maze_path(maze, [1, 1], [0, 0], "up, left")
        assert validate_maze_path(maze, [0, 0], [1, 0], "b")
        assert validate_maze_path(maze, [0, 0], [0, 1], "d")

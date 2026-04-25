"""
Renderer visual_data contract tests (Phase 3B).

Chaque classe teste la forme minimale de visual_data qu'un renderer frontend expect
pour un type de défi donné. Ces tests appellent les validateurs spécialisés directement
(pas validate_challenge_logic) pour isoler les contrats de structure de rendu.

Ils ne testent pas la logique métier (déjà couverte par IA9 et les golden tests 3A).
"""

from __future__ import annotations

import pytest

from app.services.challenges.challenge_coding_validation import validate_coding_challenge
from app.services.challenges.challenge_pattern_sequence_validation import (
    validate_pattern_challenge,
)
from app.services.challenges.challenge_validator import (
    validate_chess_challenge,
    validate_graph_challenge,
    validate_probability_challenge,
    validate_spatial_challenge,
)


def _legal_board() -> list[list[str]]:
    """Plateau 8x8 avec roi blanc en a1, roi noir en h8, et pions pour légalité (4-8 pièces)."""
    board = [[" "] * 8 for _ in range(8)]
    board[0][0] = "K"  # roi blanc en a1
    board[7][7] = "k"  # roi noir en h8
    board[1][1] = "P"  # pion blanc
    board[6][6] = "p"  # pion noir
    return board


class TestChessRendererContract:
    """chess renderer attend : visual_data.board (8x8), turn, objective."""

    def test_minimal_valid_shape_accepted(self) -> None:
        vd = {"board": _legal_board(), "turn": "white", "objective": "meilleur_coup"}
        errors = validate_chess_challenge(vd, "Ka2", "Le roi avance.")
        assert errors == [], f"Forme minimale rejetée à tort : {errors}"

    def test_missing_board_rejected(self) -> None:
        vd = {"turn": "white", "objective": "meilleur_coup"}
        errors = validate_chess_challenge(vd, "Ka2", "explication")
        assert any("board" in e.lower() for e in errors), (
            f"Absence de board non détectée. Erreurs: {errors}"
        )

    def test_invalid_turn_rejected(self) -> None:
        vd = {"board": _legal_board(), "turn": "rouge", "objective": "mat_en_1"}
        errors = validate_chess_challenge(vd, "Ka2", "explication")
        assert any("turn" in e.lower() for e in errors), (
            f"turn invalide non détecté. Erreurs: {errors}"
        )

    def test_invalid_objective_rejected(self) -> None:
        vd = {"board": _legal_board(), "turn": "white", "objective": "inconnu"}
        errors = validate_chess_challenge(vd, "Ka2", "explication")
        assert any("objective" in e.lower() for e in errors), (
            f"objective invalide non détecté. Erreurs: {errors}"
        )


class TestGraphRendererContract:
    """graph renderer attend : visual_data.nodes (list) + edges (list)."""

    def test_valid_nodes_edges_accepted(self) -> None:
        vd = {
            "nodes": ["A", "B", "C"],
            "edges": [
                {"from": "A", "to": "B", "weight": 4},
                {"from": "B", "to": "C", "weight": 3},
            ],
            "objective": "shortest_path",
            "question": "Chemin le plus court de A à C ?",
        }
        errors = validate_graph_challenge(vd, "A-B-C", "Le chemin passe par B.")
        assert errors == [], f"Forme valide rejetée : {errors}"

    def test_missing_nodes_rejected(self) -> None:
        vd = {"edges": []}
        errors = validate_graph_challenge(vd, "A", "explication")
        assert any(
            "nodes" in e.lower() for e in errors
        ), f"Absence de nodes non détectée. Erreurs: {errors}"


class TestProbabilityRendererContract:
    """probability renderer attend : quantités numériques directes dans visual_data (pas de clé 'events')."""

    def test_numeric_quantities_accepted(self) -> None:
        vd = {"rouge_bonbons": 10, "bleu_bonbons": 5}
        errors = validate_probability_challenge(vd, "2/3", "Deux bonbons rouges sur trois.")
        # L'answer peut ne pas correspondre, mais la structure visuelle est valide
        structure_errors = [
            e for e in errors
            if "quantit" in e.lower() or "visual_data manquant" in e.lower()
        ]
        assert structure_errors == [], f"Structure numérique rejetée : {structure_errors}"

    def test_only_meta_keys_rejected(self) -> None:
        """visual_data avec uniquement des clés méta (total, description, question) est invalide."""
        vd = {"total": 15, "description": "sac de bonbons", "question": "quelle proba ?"}
        errors = validate_probability_challenge(vd, "1/2", "explication")
        assert any("quantit" in e.lower() for e in errors), (
            f"Absence de quantités numériques non détectée. Erreurs: {errors}"
        )

    def test_nested_numeric_dict_accepted(self) -> None:
        """visual_data imbriqué avec valeurs numériques est accepté."""
        vd = {
            "sac_rouge": {"bonbons": 8},
            "sac_bleu": {"bonbons": 4},
        }
        errors = validate_probability_challenge(vd, "2/3", "explication")
        structure_errors = [
            e for e in errors
            if "quantit" in e.lower() or "visual_data manquant" in e.lower()
        ]
        assert structure_errors == [], f"Dict imbriqué rejeté : {structure_errors}"


class TestCodingRendererContract:
    """coding renderer attend : encoded_message + optionnellement type."""

    def test_caesar_with_encoded_message_accepted(self) -> None:
        vd = {"type": "caesar", "encoded_message": "Ifmmp", "shift": 1}
        errors = validate_coding_challenge(vd, "Hello", "Décalage de 1.")
        assert errors == [], f"Type caesar rejeté : {errors}"

    def test_missing_encoded_message_with_no_type_rejected(self) -> None:
        vd = {}  # Aucune donnée cryptographie
        errors = validate_coding_challenge(vd, "Hello", "explication")
        assert any(
            "vide" in e.lower() or "cryptographie" in e.lower()
            for e in errors
        ), f"visual_data vide non rejeté. Erreurs: {errors}"

    def test_substitution_with_key_accepted(self) -> None:
        vd = {
            "type": "substitution",
            "encoded_message": "KHOOR",
            "key": {"K": "H", "H": "E", "O": "L", "R": "O"},
        }
        errors = validate_coding_challenge(vd, "HELLO", "Substitution simple.")
        assert errors == [], f"Type substitution avec clé rejeté : {errors}"


class TestVisualRendererContract:
    """visual renderer attend : type='symmetry' → layout + symmetry_line ; ou shapes."""

    def test_symmetry_requires_layout(self) -> None:
        vd = {"type": "symmetry"}
        errors = validate_spatial_challenge(vd, "triangle", "explication")
        assert any("layout" in e.lower() for e in errors), (
            f"Absence layout non détectée. Erreurs: {errors}"
        )

    def test_symmetry_valid_layout_accepted(self) -> None:
        vd = {
            "type": "symmetry",
            "symmetry_line": "vertical",
            "layout": [
                {"shape": "cercle", "side": "left", "color": "rouge"},
                {"shape": "?", "side": "right", "question": True},
            ],
        }
        errors = validate_spatial_challenge(vd, "cercle", "Symétrie par rapport à l'axe vertical.")
        layout_errors = [e for e in errors if "layout" in e.lower() and "manquant" in e.lower()]
        assert layout_errors == [], f"Layout valide rejeté : {layout_errors}"


class TestPatternRendererContract:
    """pattern renderer attend : visual_data.grid (liste 2D avec au moins un '?')."""

    def test_missing_grid_rejected(self) -> None:
        vd = {}
        errors = validate_pattern_challenge(vd, "5", "explication")
        assert any("grid" in e.lower() for e in errors), (
            f"Absence grid non détectée. Erreurs: {errors}"
        )

    def test_grid_with_question_marker_accepted(self) -> None:
        vd = {"grid": [[1, 2, 3], [2, 3, 4], [3, 4, "?"]]}
        # The pattern analyzer will deduce the answer from the grid
        errors = validate_pattern_challenge(vd, "5", "La suite augmente de 1.")
        # Just check that the grid itself is not flagged as missing
        grid_missing_errors = [e for e in errors if "grid manquant" in e.lower()]
        assert grid_missing_errors == [], f"Grid valide rejeté comme manquant : {grid_missing_errors}"

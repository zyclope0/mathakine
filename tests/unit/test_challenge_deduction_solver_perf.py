"""
Performance and edge-case tests for the deduction solver (Phase 3D).

Couvre :
- search_space_too_large : grille 9×9 sans contraintes suffisantes → retour immédiat
- grille ambiguë : solution_count != 1 (plusieurs solutions possibles)
- valeurs dupliquées : _build_model retourne None → reason='unsupported_model'
- benchmark 4×4 : grille bien formée résolue en < 500ms (marquée @slow)

MAX_DEDUCTION_SOLVER_COMBINATIONS = 50_000
_total_search_space = factorial(n_entities) ** n_secondary_categories
"""

from __future__ import annotations

import time

import pytest

from app.services.challenges.challenge_deduction_solver import (
    MAX_DEDUCTION_SOLVER_COMBINATIONS,
    analyze_deduction_uniqueness,
)


def test_constant_value() -> None:
    """Documenter que MAX_DEDUCTION_SOLVER_COMBINATIONS = 50_000 (contrat stable)."""
    assert MAX_DEDUCTION_SOLVER_COMBINATIONS == 50_000


class TestSearchSpaceTooLarge:
    """Grille dont search_space > 50_000 : retour immédiat sans exploration."""

    # 9 entités × 1 catégorie secondaire → 9! = 362_880 > 50_000
    # 1 contrainte structurée présente pour que le parsing réussisse et atteigne la vérification du search_space
    _VISUAL_LARGE = {
        "type": "logic_grid",
        "entities": {
            "Personnes": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"],
            "Couleurs": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"],
        },
        "clues": [],
        "constraints": [
            {
                "type": "entity_value",
                "left": {"category": "Personnes", "value": "P1"},
                "right": {"category": "Couleurs", "value": "C1"},
            },
        ],
    }

    def test_returns_without_computation(self) -> None:
        result = analyze_deduction_uniqueness(self._VISUAL_LARGE, "P1:C1")
        assert result.checked is False
        assert result.reason == "search_space_too_large"

    def test_returns_immediately(self) -> None:
        """Le retour doit être quasi-instantané (< 200ms CI-safe) pour une grille trop grande."""
        start = time.perf_counter()
        analyze_deduction_uniqueness(self._VISUAL_LARGE, "P1:C1")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 200, f"Retour trop lent pour search_space_too_large : {elapsed_ms:.1f}ms"


class TestAmbiguousGrid:
    """Grille avec contraintes insuffisantes → plusieurs solutions possibles."""

    # 3 entités × 1 catégorie secondaire → search_space = 3! = 6 (< 50_000, exploré)
    # 1 seule contrainte pour 3 entités → Alice=Rouge déterminé, Bob et Clara peuvent échanger
    _VISUAL_AMBIGUOUS = {
        "type": "logic_grid",
        "entities": {
            "Personnes": ["Alice", "Bob", "Clara"],
            "Couleurs": ["Rouge", "Bleu", "Vert"],
        },
        "clues": [],
        "constraints": [
            {
                "type": "entity_value",
                "left": {"category": "Personnes", "value": "Alice"},
                "right": {"category": "Couleurs", "value": "Rouge"},
            },
        ],
    }

    def test_ambiguous_grid_has_multiple_solutions(self) -> None:
        result = analyze_deduction_uniqueness(
            self._VISUAL_AMBIGUOUS, "Alice:Rouge,Bob:Bleu,Clara:Vert"
        )
        assert result.checked is True, (
            f"Le solveur n'a pas pu parser la grille ambiguë : {result.reason}"
        )
        assert result.solution_count > 1, (
            f"Grille ambiguë identifiée à tort comme unique : {result.solution_count} solution(s)"
        )


class TestDuplicateValuesInCategory:
    """Catégorie avec valeurs dupliquées → _build_model retourne None → unsupported_model."""

    _VISUAL_DUPLICATES = {
        "type": "logic_grid",
        "entities": {
            "Personnes": ["Alice", "Alice"],  # doublon intentionnel
            "Couleurs": ["Rouge", "Bleu"],
        },
        "clues": [],
        "constraints": [
            {
                "type": "entity_value",
                "left": {"category": "Personnes", "value": "Alice"},
                "right": {"category": "Couleurs", "value": "Rouge"},
            },
        ],
    }

    def test_duplicate_entities_returns_unsupported_model(self) -> None:
        result = analyze_deduction_uniqueness(self._VISUAL_DUPLICATES, "Alice:Rouge")
        assert result.checked is False
        assert result.reason == "unsupported_model"


@pytest.mark.slow
class TestSolverBenchmark:
    """Benchmark : grille 4×4 bien formée résolue en < 500ms.

    Marquée @slow pour pouvoir être exclue des runs rapides :
      pytest -m "not slow"
    """

    # 4 entités × 2 catégories secondaires → search_space = 4!^2 = 576 (exploré)
    # 6 contraintes déterministes → solution unique
    _VISUAL_4X4 = {
        "type": "logic_grid",
        "entities": {
            "Personnes": ["Alice", "Bob", "Clara", "David"],
            "Métiers": ["Médecin", "Avocat", "Architecte", "Ingénieur"],
            "Villes": ["Paris", "Lyon", "Marseille", "Toulouse"],
        },
        "clues": [],
        "constraints": [
            {
                "type": "entity_value",
                "left": {"category": "Personnes", "value": "Alice"},
                "right": {"category": "Métiers", "value": "Médecin"},
            },
            {
                "type": "entity_value",
                "left": {"category": "Personnes", "value": "Bob"},
                "right": {"category": "Métiers", "value": "Avocat"},
            },
            {
                "type": "entity_value",
                "left": {"category": "Personnes", "value": "Clara"},
                "right": {"category": "Métiers", "value": "Architecte"},
            },
            {
                "type": "entity_value",
                "left": {"category": "Personnes", "value": "Alice"},
                "right": {"category": "Villes", "value": "Paris"},
            },
            {
                "type": "entity_value",
                "left": {"category": "Personnes", "value": "Bob"},
                "right": {"category": "Villes", "value": "Lyon"},
            },
            {
                "type": "entity_value",
                "left": {"category": "Personnes", "value": "Clara"},
                "right": {"category": "Villes", "value": "Marseille"},
            },
        ],
    }
    _ANSWER_4X4 = "Alice:Médecin:Paris,Bob:Avocat:Lyon,Clara:Architecte:Marseille,David:Ingénieur:Toulouse"

    def test_4x4_unique_solution(self) -> None:
        result = analyze_deduction_uniqueness(self._VISUAL_4X4, self._ANSWER_4X4)
        assert result.checked is True, f"Solveur n'a pas pu vérifier : {result.reason}"
        assert result.solution_count == 1, f"Solution non unique : {result.solution_count} solutions"

    def test_4x4_under_500ms(self) -> None:
        start = time.perf_counter()
        result = analyze_deduction_uniqueness(self._VISUAL_4X4, self._ANSWER_4X4)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert result.checked is True  # sanity check
        assert elapsed_ms < 500, (
            f"Solveur 4×4 trop lent : {elapsed_ms:.1f}ms (seuil 500ms CI-safe)"
        )

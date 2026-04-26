"""
Performance and edge-case tests for the deduction solver (Phase 3D).

Couvre :
- seuil MAX_DEDUCTION_SOLVER_COMBINATIONS : 8! exploré, 9! court-circuité (test comportemental)
- search_space_too_large : retour immédiat sans exploration (sans dépendance temporelle)
- grille ambiguë : solution_count > 1 (plusieurs solutions possibles)
- valeurs dupliquées : _build_model retourne None → reason='unsupported_model'
- benchmark 4×4 : grille bien formée résolue en < 500ms et réponse calibrée (marquée @slow)

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


def test_max_combinations_seuil_is_strict() -> None:
    """Le seuil 50 000 est un contrat de performance : strictement supérieur ⇒ pas exploré.

    Vérifie le comportement (pas seulement la valeur de la constante) sur deux côtés
    du seuil :
    - search_space == 50_000 ⇒ exploré (pas de short-circuit)
    - search_space > 50_000  ⇒ short-circuit avec ``search_space_too_large``
    """
    # 8! = 40 320 (≤ 50 000) avec 1 catégorie secondaire ⇒ exploré
    visual_under = {
        "type": "logic_grid",
        "entities": {
            "Personnes": [f"P{i}" for i in range(1, 9)],
            "Couleurs": [f"C{i}" for i in range(1, 9)],
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
    res_under = analyze_deduction_uniqueness(visual_under, "P1:C1")
    assert (
        res_under.reason != "search_space_too_large"
    ), f"8! = 40 320 doit être exploré, reçu reason={res_under.reason!r}"

    # 9! = 362 880 (> 50 000) ⇒ short-circuit
    visual_over = {
        "type": "logic_grid",
        "entities": {
            "Personnes": [f"P{i}" for i in range(1, 10)],
            "Couleurs": [f"C{i}" for i in range(1, 10)],
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
    res_over = analyze_deduction_uniqueness(visual_over, "P1:C1")
    assert res_over.checked is False
    assert res_over.reason == "search_space_too_large"

    # Ancrage explicite : si la constante bouge, ce test doit être ré-évalué.
    assert MAX_DEDUCTION_SOLVER_COMBINATIONS == 50_000


class TestSearchSpaceTooLarge:
    """Grille dont search_space > 50_000 : retour immédiat sans exploration."""

    # 9 entités × 1 catégorie secondaire → 9! = 362 880 > 50 000.
    # 1 contrainte structurée pour que le parsing atteigne la vérification du search_space.
    # NB : ne pas ajouter de catégorie supplémentaire — le coût construit avant le
    # short-circuit n'est garanti que pour ce gabarit (1 catégorie secondaire).
    _N_ENTITIES = 9
    _N_SECONDARY_CATEGORIES = 1
    _VISUAL_LARGE = {
        "type": "logic_grid",
        "entities": {
            "Personnes": [f"P{i}" for i in range(1, _N_ENTITIES + 1)],
            "Couleurs": [f"C{i}" for i in range(1, _N_ENTITIES + 1)],
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

    def test_visual_large_invariant(self) -> None:
        """Garde-fou : 1 catégorie principale + 1 secondaire (cf. _total_search_space)."""
        secondary = len(self._VISUAL_LARGE["entities"]) - 1
        assert (
            secondary == self._N_SECONDARY_CATEGORIES
        ), f"_VISUAL_LARGE doit garder 1 catégorie secondaire, reçu {secondary}"

    def test_returns_without_computation(self) -> None:
        result = analyze_deduction_uniqueness(self._VISUAL_LARGE, "P1:C1")
        assert result.checked is False
        assert result.reason == "search_space_too_large"


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
        assert (
            result.checked is True
        ), f"Le solveur n'a pas pu parser la grille ambiguë : {result.reason}"
        assert (
            result.solution_count > 1
        ), f"Grille ambiguë identifiée à tort comme unique : {result.solution_count} solution(s)"


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
        assert (
            result.solution_count == 1
        ), f"Solution non unique : {result.solution_count} solutions"
        # P2-4 : _ANSWER_4X4 est calibrée pour être l'unique solution déduite des 6 contraintes.
        assert result.expected_answer_matches is True, (
            f"La réponse calibrée doit correspondre à la solution unique "
            f"(reçu expected_answer_matches={result.expected_answer_matches})"
        )

    def test_4x4_under_500ms(self) -> None:
        start = time.perf_counter()
        result = analyze_deduction_uniqueness(self._VISUAL_4X4, self._ANSWER_4X4)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert result.checked is True  # sanity check
        assert (
            elapsed_ms < 500
        ), f"Solveur 4×4 trop lent : {elapsed_ms:.1f}ms (seuil 500ms CI-safe)"

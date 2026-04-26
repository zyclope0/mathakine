# Phase 3 Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verrouiller les contrats de validation et de rendu des défis IA par des tests déterministes sans DB ni OpenAI (Phase 3A golden tests, 3B renderer contracts, 3D deduction solver perf).

**Architecture:** Trois tâches indépendantes, chacune crée un ou plusieurs fichiers de test sans toucher au code de production. La Task 1 crée `tests/challenges/` + fixtures JSON. La Task 2 crée `tests/unit/test_challenge_renderer_contracts.py`. La Task 3 crée `tests/unit/test_challenge_deduction_solver_perf.py`.

**Tech Stack:** Python 3.12, pytest, `validate_challenge_logic` + `classify_challenge_validation_errors` + `analyze_deduction_uniqueness` (APIs publiques existantes). Pas de mock, pas de DB, pas d'OpenAI.

---

## Fichiers créés

| Fichier | Tâche |
|---------|-------|
| `tests/challenges/__init__.py` | Task 1 |
| `tests/fixtures/challenges/chess_valid.json` | Task 1 |
| `tests/fixtures/challenges/chess_invalid_king_check.json` | Task 1 |
| `tests/fixtures/challenges/deduction_valid.json` | Task 1 |
| `tests/fixtures/challenges/deduction_invalid_format.json` | Task 1 |
| `tests/fixtures/challenges/coding_valid.json` | Task 1 |
| `tests/challenges/test_regression_by_type.py` | Task 1 |
| `tests/unit/test_challenge_renderer_contracts.py` | Task 2 |
| `tests/unit/test_challenge_deduction_solver_perf.py` | Task 3 |

**Aucun fichier de production modifié.**

---

## Contexte technique

**Imports clés à utiliser :**
```python
from app.services.challenges.challenge_validator import (
    validate_challenge_logic,
    validate_chess_challenge,
    validate_probability_challenge,
    validate_graph_challenge,
    validate_spatial_challenge,
)
from app.services.challenges.challenge_coding_validation import validate_coding_challenge
from app.services.challenges.challenge_pattern_sequence_validation import validate_pattern_challenge
from app.services.challenges.challenge_validation_error_codes import (
    classify_challenge_validation_errors,
)
from app.services.challenges.challenge_deduction_solver import (
    analyze_deduction_uniqueness,
    MAX_DEDUCTION_SOLVER_COMBINATIONS,
)
```

**Signatures :**
- `validate_challenge_logic(challenge_data: Dict) -> Tuple[bool, List[str]]`
- `classify_challenge_validation_errors(errors: List[str], challenge_type: str) -> List[str]` — retourne les codes stables (ex: `"chess_king_in_check"`)
- `analyze_deduction_uniqueness(visual_data: Dict, correct_answer: str) -> DeductionUniquenessResult`
- `DeductionUniquenessResult` : dataclass avec `checked: bool`, `solution_count: int`, `reason: str`, `expected_answer_matches: Optional[bool]`
- `MAX_DEDUCTION_SOLVER_COMBINATIONS = 50_000`

**Format correct_answer déduction :** `"Entité1:ValCat2:ValCat3,Entité2:ValCat2:ValCat3"` (une entrée par entité, autant de segments que de catégories, séparés par `:`)

---

## Task 1 — Golden tests 3A : fixtures JSON + test paramétrié

**Files:**
- Create: `tests/challenges/__init__.py`
- Create: `tests/fixtures/challenges/chess_valid.json`
- Create: `tests/fixtures/challenges/chess_invalid_king_check.json`
- Create: `tests/fixtures/challenges/deduction_valid.json`
- Create: `tests/fixtures/challenges/deduction_invalid_format.json`
- Create: `tests/fixtures/challenges/coding_valid.json`
- Create: `tests/challenges/test_regression_by_type.py`

- [ ] **Step 1 : Créer les dossiers**

```bash
mkdir -p tests/challenges tests/fixtures/challenges
touch tests/challenges/__init__.py
touch tests/fixtures/__init__.py
```

- [ ] **Step 2 : Créer `chess_valid.json`**

Position légale : roi blanc en a1, roi noir en h8, aucune pièce en entre-deux. Tour blanc à jouer, roi noir non en échec → position valide.

```json
{
  "challenge": {
    "challenge_type": "CHESS",
    "title": "Mat en un coup",
    "description": "Trouvez le meilleur coup pour les blancs.",
    "correct_answer": "Ka2",
    "solution_explanation": "Le roi avance en a2.",
    "difficulty_rating": 1,
    "visual_data": {
      "board": [
        [" "," "," "," "," "," "," ","k"],
        [" "," "," "," "," "," "," "," "],
        [" "," "," "," "," "," "," "," "],
        [" "," "," "," "," "," "," "," "],
        [" "," "," "," "," "," "," "," "],
        [" "," "," "," "," "," "," "," "],
        [" "," "," "," "," "," "," "," "],
        ["K"," "," "," "," "," "," "," "]
      ],
      "turn": "white",
      "objective": "meilleur_coup"
    },
    "choices": null,
    "response_mode": "text"
  },
  "expected_valid": true,
  "expected_error_codes": []
}
```

- [ ] **Step 3 : Créer `chess_invalid_king_check.json`**

Position illégale : tour blanche en h1, roi noir en h8 — la tour attaque le roi noir sur la colonne h. C'est le tour des blancs, donc le roi noir (côté qui vient de jouer) est en échec : position invalide.

```json
{
  "challenge": {
    "challenge_type": "CHESS",
    "title": "Position illégale",
    "description": "Le roi noir est en échec au départ.",
    "correct_answer": "Rxh8",
    "solution_explanation": "La tour capture le roi.",
    "difficulty_rating": 1,
    "visual_data": {
      "board": [
        [" "," "," "," "," "," "," ","k"],
        [" "," "," "," "," "," "," "," "],
        [" "," "," "," "," "," "," "," "],
        [" "," "," "," "," "," "," "," "],
        [" "," "," "," "," "," "," "," "],
        [" "," "," "," "," "," "," "," "],
        [" "," "," "," "," "," "," "," "],
        ["K"," "," "," "," "," "," ","R"]
      ],
      "turn": "white",
      "objective": "mat_en_1"
    },
    "choices": null,
    "response_mode": "text"
  },
  "expected_valid": false,
  "expected_error_codes": ["chess_king_in_check"]
}
```

- [ ] **Step 4 : Créer `deduction_valid.json`**

Grille 2×2 avec 2 clues suffisants → solution unique `"Alice:Rouge,Bob:Bleu"`.

```json
{
  "challenge": {
    "challenge_type": "DEDUCTION",
    "title": "Qui a quelle couleur ?",
    "description": "Associe chaque personne à sa couleur.",
    "correct_answer": "Alice:Rouge,Bob:Bleu",
    "solution_explanation": "Alice a Rouge d'après le premier indice, Bob a donc Bleu.",
    "difficulty_rating": 2,
    "visual_data": {
      "type": "logic_grid",
      "entities": {
        "Personnes": ["Alice", "Bob"],
        "Couleurs": ["Rouge", "Bleu"]
      },
      "clues": [
        "Alice a la même couleur que Rouge.",
        "Bob a la même couleur que Bleu."
      ]
    },
    "choices": null,
    "response_mode": "text"
  },
  "expected_valid": true,
  "expected_error_codes": []
}
```

- [ ] **Step 5 : Créer `deduction_invalid_format.json`**

`correct_answer` avec format incorrect : 2 catégories dans `entities`, mais la réponse n'a qu'un seul segment par entité (manque le séparateur `:Couleur`). → erreur `deduction_constraint_parse_failed`.

```json
{
  "challenge": {
    "challenge_type": "DEDUCTION",
    "title": "Déduction malformée",
    "description": "Associe chaque personne à sa couleur.",
    "correct_answer": "Alice,Bob",
    "solution_explanation": "Alice correspond à Rouge.",
    "difficulty_rating": 2,
    "visual_data": {
      "type": "logic_grid",
      "entities": {
        "Personnes": ["Alice", "Bob"],
        "Couleurs": ["Rouge", "Bleu"]
      },
      "clues": [
        "Indice numéro un.",
        "Indice numéro deux."
      ]
    },
    "choices": null,
    "response_mode": "text"
  },
  "expected_valid": false,
  "expected_error_codes": ["deduction_constraint_parse_failed"]
}
```

- [ ] **Step 6 : Créer `coding_valid.json`**

Type `caesar` avec `encoded_message` et `shift` → structure valide, pas de vérification answer par le validateur pour ce type.

```json
{
  "challenge": {
    "challenge_type": "CODING",
    "title": "Message chiffré",
    "description": "Décrypte ce message utilisant un chiffrement de César.",
    "correct_answer": "Hello",
    "solution_explanation": "Chaque lettre est décalée d'un cran (I→H, f→e, m→l, m→l, p→o).",
    "difficulty_rating": 2,
    "visual_data": {
      "type": "caesar",
      "encoded_message": "Ifmmp",
      "shift": 1
    },
    "choices": null,
    "response_mode": "text"
  },
  "expected_valid": true,
  "expected_error_codes": []
}
```

- [ ] **Step 7 : Créer `tests/challenges/test_regression_by_type.py`**

```python
"""
Golden regression tests for challenge validation (Phase 3A).

Each JSON fixture in tests/fixtures/challenges/ describes one challenge payload
and its expected validation outcome. The test is parametrized: adding a new fixture
file automatically adds a new test case.

Fixture format:
  {
    "challenge": { ...full challenge dict... },
    "expected_valid": true | false,
    "expected_error_codes": ["code1", "code2"]   # stable codes from challenge_validation_error_codes
  }
"""

from __future__ import annotations

import json
from glob import glob
from pathlib import Path

import pytest

from app.services.challenges.challenge_validation_error_codes import (
    classify_challenge_validation_errors,
)
from app.services.challenges.challenge_validator import validate_challenge_logic

_FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "challenges"


def _load_fixture_ids() -> list[str]:
    return [Path(p).stem for p in sorted(glob(str(_FIXTURES_DIR / "*.json")))]


@pytest.mark.parametrize("fixture_name", _load_fixture_ids())
def test_challenge_regression(fixture_name: str) -> None:
    """Each fixture must produce exactly the expected validity and error codes."""
    fixture_path = _FIXTURES_DIR / f"{fixture_name}.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    challenge = data["challenge"]
    is_valid, errors = validate_challenge_logic(challenge)

    assert is_valid == data["expected_valid"], (
        f"[{fixture_name}] is_valid attendu={data['expected_valid']}, "
        f"obtenu={is_valid}. Erreurs brutes: {errors}"
    )

    actual_codes = classify_challenge_validation_errors(
        errors, challenge.get("challenge_type", "")
    )
    assert set(actual_codes) == set(data["expected_error_codes"]), (
        f"[{fixture_name}] error_codes attendus={data['expected_error_codes']}, "
        f"obtenus={actual_codes}. Erreurs brutes: {errors}"
    )
```

- [ ] **Step 8 : Vérifier que le test se découvre et passe**

```bash
pytest tests/challenges/test_regression_by_type.py -v --override-ini="addopts="
```

Attendu :
```
PASSED tests/challenges/test_regression_by_type.py::test_challenge_regression[chess_valid]
PASSED tests/challenges/test_regression_by_type.py::test_challenge_regression[chess_invalid_king_check]
PASSED tests/challenges/test_regression_by_type.py::test_challenge_regression[deduction_valid]
PASSED tests/challenges/test_regression_by_type.py::test_challenge_regression[deduction_invalid_format]
PASSED tests/challenges/test_regression_by_type.py::test_challenge_regression[coding_valid]
5 passed
```

Si un test échoue avec `is_valid` ou `error_codes` inattendu, affiche les erreurs brutes dans le message d'assertion — utilise-les pour corriger la fixture, pas le test.

- [ ] **Step 9 : Commit**

```bash
git add tests/challenges/ tests/fixtures/
git commit -m "test(challenges): add golden test fixtures and parametrized regression suite (Phase 3A)"
```

---

## Task 2 — Contrats renderer 3B

**Files:**
- Create: `tests/unit/test_challenge_renderer_contracts.py`

Ces tests appellent les **validateurs spécialisés** (pas `validate_challenge_logic`) pour vérifier que les formes minimales de `visual_data` sont acceptées ou rejetées. Ils documentent le contrat que le frontend consomme.

- [ ] **Step 1 : Créer `tests/unit/test_challenge_renderer_contracts.py`**

```python
"""
Renderer visual_data contract tests (Phase 3B).

Chaque classe teste la forme minimale de visual_data qu'un renderer frontend attend
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


def _empty_board() -> list[list[str]]:
    """Plateau 8x8 avec roi blanc en a1 et roi noir en h8 (position légale)."""
    board = [[""] * 8 for _ in range(8)]
    board[0][7] = "k"  # roi noir en h8 (rang 8, colonne h)
    board[7][0] = "K"  # roi blanc en a1 (rang 1, colonne a)
    return board


class TestChessRendererContract:
    """chess renderer attend : visual_data.board (8x8), turn, objective."""

    def test_minimal_valid_shape_accepted(self) -> None:
        vd = {"board": _empty_board(), "turn": "white", "objective": "meilleur_coup"}
        errors = validate_chess_challenge(vd, "Ka2", "Le roi avance.")
        assert errors == [], f"Forme minimale rejetée à tort : {errors}"

    def test_missing_board_rejected(self) -> None:
        vd = {"turn": "white", "objective": "meilleur_coup"}
        errors = validate_chess_challenge(vd, "Ka2", "explication")
        assert any("board" in e.lower() for e in errors), (
            f"Absence de board non détectée. Erreurs: {errors}"
        )

    def test_invalid_turn_rejected(self) -> None:
        vd = {"board": _empty_board(), "turn": "rouge", "objective": "mat_en_1"}
        errors = validate_chess_challenge(vd, "Ka2", "explication")
        assert any("turn" in e.lower() for e in errors), (
            f"turn invalide non détecté. Erreurs: {errors}"
        )

    def test_invalid_objective_rejected(self) -> None:
        vd = {"board": _empty_board(), "turn": "white", "objective": "inconnu"}
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
            "nodes" in e.lower() or "visual_data" in e.lower() or "nœud" in e.lower()
            for e in errors
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
        assert any("quantit" in e.lower() or "numerique" in e.lower() for e in errors), (
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

    def test_missing_encoded_message_rejected(self) -> None:
        vd = {"type": "substitution"}
        errors = validate_coding_challenge(vd, "Hello", "explication")
        assert any(
            "encoded" in e.lower() or "message" in e.lower() or "cryptographie" in e.lower()
            for e in errors
        ), f"Absence encoded_message non détectée. Erreurs: {errors}"

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
                {"shape": "cercle", "side": "right", "color": "rouge"},
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
        errors = validate_pattern_challenge(vd, "5", "La suite augmente de 1.")
        grid_errors = [e for e in errors if "grid manquant" in e.lower()]
        assert grid_errors == [], f"Grid valide rejeté : {grid_errors}"
```

- [ ] **Step 2 : Vérifier que les tests passent**

```bash
pytest tests/unit/test_challenge_renderer_contracts.py -v --override-ini="addopts="
```

Attendu : tous les tests passent. Si un test échoue, lis le message d'erreur pour comprendre le contrat réel du validateur et ajuste le test (pas le validateur).

- [ ] **Step 3 : Commit**

```bash
git add tests/unit/test_challenge_renderer_contracts.py
git commit -m "test(challenges): add renderer visual_data contract tests (Phase 3B)"
```

---

## Task 3 — Perf solveur déduction 3D

**Files:**
- Create: `tests/unit/test_challenge_deduction_solver_perf.py`

- [ ] **Step 1 : Créer `tests/unit/test_challenge_deduction_solver_perf.py`**

```python
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


class TestSearchSpaceTooLarge:
    """Grille dont search_space > 50_000 : retour immédiat sans exploration."""

    # 9 entités × 1 catégorie secondaire → 9! = 362_880 > 50_000
    _VISUAL_LARGE = {
        "type": "logic_grid",
        "entities": {
            "Personnes": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"],
            "Couleurs": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"],
        },
        "clues": [],
        "constraints": [
            {"type": "entity_value", "entity": "P1", "category": "Couleurs", "value": "C1"},
        ],
    }

    def test_returns_without_computation(self) -> None:
        result = analyze_deduction_uniqueness(self._VISUAL_LARGE, "P1:C1")
        assert result.checked is False
        assert result.reason == "search_space_too_large"

    def test_constant_value(self) -> None:
        """Documenter que MAX_DEDUCTION_SOLVER_COMBINATIONS = 50_000 (contrat stable)."""
        assert MAX_DEDUCTION_SOLVER_COMBINATIONS == 50_000

    def test_returns_immediately(self) -> None:
        """Le retour doit être quasi-instantané (< 50ms) pour une grille trop grande."""
        start = time.perf_counter()
        analyze_deduction_uniqueness(self._VISUAL_LARGE, "P1:C1")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 50, f"Retour trop lent pour search_space_too_large : {elapsed_ms:.1f}ms"


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
            {"type": "entity_value", "entity": "Alice", "category": "Couleurs", "value": "Rouge"},
        ],
    }

    def test_ambiguous_grid_has_multiple_solutions(self) -> None:
        result = analyze_deduction_uniqueness(
            self._VISUAL_AMBIGUOUS, "Alice:Rouge,Bob:Bleu,Clara:Vert"
        )
        # Soit checked=True avec solution_count > 1, soit checked=False (parse failed)
        # Dans les deux cas : pas de solution unique
        is_unique = result.checked and result.solution_count == 1
        assert not is_unique, (
            f"Grille ambiguë identifiée à tort comme unique : {result}"
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
            {"type": "entity_value", "entity": "Alice", "category": "Couleurs", "value": "Rouge"},
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
            {"type": "entity_value", "entity": "Alice", "category": "Métiers", "value": "Médecin"},
            {"type": "entity_value", "entity": "Bob", "category": "Métiers", "value": "Avocat"},
            {"type": "entity_value", "entity": "Clara", "category": "Métiers", "value": "Architecte"},
            {"type": "entity_value", "entity": "Alice", "category": "Villes", "value": "Paris"},
            {"type": "entity_value", "entity": "Bob", "category": "Villes", "value": "Lyon"},
            {"type": "entity_value", "entity": "Clara", "category": "Villes", "value": "Marseille"},
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
```

- [ ] **Step 2 : Vérifier que les tests passent**

```bash
pytest tests/unit/test_challenge_deduction_solver_perf.py -v --override-ini="addopts="
```

Attendu : tous passent. Si `test_4x4_unique_solution` échoue avec `checked=False`, vérifie que la structure des `constraints` structurées est bien parsée par `_parse_constraints` — utilise alors des clues en langage naturel à la place (voir `test_challenge_ia9_contract_policy.py` lignes 461-478 pour le format).

Pour exclure le benchmark des runs rapides :
```bash
pytest tests/unit/test_challenge_deduction_solver_perf.py -v -m "not slow" --override-ini="addopts="
```
Attendu : 4 passed (les deux tests slow exclus).

- [ ] **Step 3 : Commit**

```bash
git add tests/unit/test_challenge_deduction_solver_perf.py
git commit -m "test(deduction): add solver perf, uniqueness and edge case tests (Phase 3D)"
```

---

## Vérification finale

```bash
pytest tests/challenges/ tests/unit/test_challenge_renderer_contracts.py tests/unit/test_challenge_deduction_solver_perf.py -v --override-ini="addopts="
```

Attendu : 5 (3A) + ~14 (3B) + 6 (3D) = ~25 passed, 0 failed.

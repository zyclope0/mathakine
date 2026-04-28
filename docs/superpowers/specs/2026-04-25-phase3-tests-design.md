# Phase 3 — Tests qui protègent les règles (3A + 3B + 3D)

> **[CLOS — livré 2026-04-25]** Phases 3A (golden tests), 3B (contrats renderer), 3D (perf solveur déduction) implémentées et vérifiées.

## Objectif

Verrouiller les contrats de validation et de rendu des défis IA par des tests déterministes, sans DB, sans OpenAI. Trois livrables indépendants :

- **3A** — Golden tests paramétrés sur fixtures JSON manuelles (`test_regression_by_type.py`)
- **3B** — Contrats renderer : forme minimale de `visual_data` par type (`test_challenge_renderer_contracts.py`)
- **3D** — Perf + edge cases solveur déduction (`test_challenge_deduction_solver_perf.py`)

Shadow mode (3C) différé : touche le pipeline de génération, risque de bord, traité séparément.

---

## Architecture

### Fichiers créés

| Fichier | Rôle |
|---------|------|
| `tests/challenges/__init__.py` | Package |
| `tests/challenges/test_regression_by_type.py` | 3A — golden tests paramétrés |
| `tests/fixtures/challenges/chess_valid.json` | Fixture chess nominale |
| `tests/fixtures/challenges/chess_invalid_king_check.json` | Fixture chess roi en échec |
| `tests/fixtures/challenges/deduction_valid.json` | Fixture déduction 3x3, solution unique |
| `tests/fixtures/challenges/deduction_ambiguous.json` | Fixture déduction sans contraintes suffisantes |
| `tests/fixtures/challenges/coding_valid.json` | Fixture coding substitution nominale |
| `tests/unit/test_challenge_renderer_contracts.py` | 3B — formes visual_data renderer |
| `tests/unit/test_challenge_deduction_solver_perf.py` | 3D — perf + edge cases solveur |

### Fichiers non modifiés

Aucun fichier de production modifié. API publique utilisée :

- `validate_challenge_logic(challenge_data: Dict) -> Tuple[bool, List[str]]` — `challenge_validator.py:104`
- `classify_challenge_validation_errors(errors: List[str], challenge_type: str) -> List[str]` — `challenge_validation_error_codes.py`
- `analyze_deduction_uniqueness(visual_data: Dict, correct_answer: str) -> DeductionUniquenessResult` — `challenge_deduction_solver.py:574`
- `MAX_DEDUCTION_SOLVER_COMBINATIONS = 50_000` — `challenge_deduction_solver.py:25`

---

## Task 1 — Golden tests 3A

### Format fixture JSON (champs réels du backend)

```json
{
  "challenge": {
    "challenge_type": "CHESS",
    "title": "...",
    "description": "...",
    "correct_answer": "Qxf7#",
    "solution_explanation": "La dame capture en f7, mat en 1 coup.",
    "difficulty_rating": 3,
    "visual_data": {
      "board": [
        ["r","n","b","q","k","b","n","r"],
        ["p","p","p","p"," ","p","p","p"],
        [" "," "," "," "," "," "," "," "],
        [" "," "," "," ","p"," "," "," "],
        [" "," "," "," ","P","P"," "," "],
        [" "," "," "," "," ","N"," "," "],
        ["P","P","P","P"," "," ","P","P"],
        ["R","N","B","Q","K","B"," ","R"]
      ],
      "turn": "white",
      "objective": "mat_en_1"
    },
    "choices": null,
    "response_mode": "text"
  },
  "expected_valid": true,
  "expected_error_codes": []
}
```

**Champs obligatoires du contrat backend :**
- `correct_answer` (pas `solution`)
- `solution_explanation` (pas `explanation`)
- `difficulty_rating` (pas `difficulty`)
- `challenge_type` en majuscules (`"CHESS"`, `"DEDUCTION"`, `"CODING"`, etc.)

### Test paramétrié

```python
from glob import glob
import json
import pytest
from app.services.challenges.challenge_validator import validate_challenge_logic
from app.services.challenges.challenge_validation_error_codes import (
    classify_challenge_validation_errors,
)

@pytest.mark.parametrize("fixture_path", sorted(glob("tests/fixtures/challenges/*.json")))
def test_challenge_regression(fixture_path):
    data = json.loads(open(fixture_path, encoding="utf-8").read())
    challenge = data["challenge"]
    is_valid, errors = validate_challenge_logic(challenge)

    assert is_valid == data["expected_valid"], (
        f"Fixture {fixture_path}: is_valid attendu={data['expected_valid']}, "
        f"obtenu={is_valid}. Erreurs: {errors}"
    )

    actual_codes = classify_challenge_validation_errors(
        errors, challenge.get("challenge_type", "")
    )
    assert set(actual_codes) == set(data["expected_error_codes"]), (
        f"Fixture {fixture_path}: error_codes attendus={data['expected_error_codes']}, "
        f"obtenus={actual_codes}. Messages bruts: {errors}"
    )
```

**Pourquoi `expected_error_codes` et non les messages bruts :** les messages d'erreur (`"CHESS: turn doit être 'white' ou 'black'"`) peuvent changer facilement. Les error codes (`"chess_board_malformed"`) sont des constantes stables définies dans `challenge_validation_error_codes.py`.

### Fixtures livrées (priorité risque)

| Fixture | Type | expected_valid | expected_error_codes | Cas testé |
|---------|------|---------------|---------------------|-----------|
| `chess_valid.json` | CHESS | true | [] | Position légale, roi non en échec |
| `chess_invalid_king_check.json` | CHESS | false | ["chess_king_in_check"] | Roi en échec détecté |
| `deduction_valid.json` | DEDUCTION | true | [] | Grille 3x3, indices suffisants, 1 solution |
| `deduction_ambiguous.json` | DEDUCTION | false | ["deduction_no_unique_solution"] | Grille sans contraintes suffisantes |
| `coding_valid.json` | CODING | true | [] | Substitution caesar avec encoded_message |

Fixtures additionnelles (`sequence_valid.json`, `probability_valid.json`, etc.) en nominal-only si le temps le permet.

### Vérification

```bash
pytest tests/challenges/test_regression_by_type.py -v
```

Attendu : 5 passed (une assertion par fixture).

---

## Task 2 — Contrats renderer 3B

### Principe

Tests unitaires purs, fixtures inline. Chaque test vérifie la **forme minimale de `visual_data`** qu'un renderer frontend attend. Ces tests ne valident pas la logique métier — ils verrouillent la structure de données que le frontend consomme, distinctement de `test_challenge_ia9_contract_policy.py` (règles métier IA9).

### Formes minimales par type (terrain réel du validateur)

| Type | Clés requises | Contraintes |
|------|--------------|-------------|
| `CHESS` | `board`, `turn`, `objective` | `board` = liste 8×8 ; `turn` ∈ `{"white","black"}` ; `objective` ∈ `{"mat_en_1","mat_en_2","mat_en_3","meilleur_coup"}` |
| `GRAPH` | `nodes`, `edges` | listes (peuvent être vides pour graphe minimal) |
| `PROBABILITY` | au moins une clé numérique `> 0` (ex: `rouge_bonbons: 10`) | pas de clé `events` — quantités numériques directes |
| `CODING` | `encoded_message` (ou `message`) ET optionnellement `type` | `type` ∈ `{"substitution","caesar","atbash","keyword","maze"}` |
| `VISUAL` (symétrie) | `type: "symmetry"`, `layout`, `symmetry_line` | `layout` = liste de dicts avec `side` |
| `VISUAL` (shapes) | `shapes` | liste de dicts formes |
| `PATTERN` | `grid` | liste de listes 2D avec au moins une cellule `"?"` |

### Structure du fichier

```python
class TestChessRendererContract:
    def test_requires_board_8x8(self): ...
    def test_requires_turn_white_or_black(self): ...
    def test_requires_objective_known_value(self): ...

class TestGraphRendererContract:
    def test_requires_nodes_and_edges_lists(self): ...

class TestProbabilityRendererContract:
    def test_requires_at_least_one_numeric_quantity(self): ...
    def test_meta_keys_only_is_invalid(self): ...

class TestCodingRendererContract:
    def test_requires_encoded_message(self): ...
    def test_type_substitution_with_encoded_message_is_valid(self): ...

class TestVisualRendererContract:
    def test_symmetry_requires_layout_and_symmetry_line(self): ...
    def test_shapes_variant_requires_shapes_list(self): ...

class TestPatternRendererContract:
    def test_requires_grid_with_question_marker(self): ...
```

Ces tests font des assertions directes sur des dicts inline — **pas d'appel à `validate_challenge_logic()`**.

### Vérification

```bash
pytest tests/unit/test_challenge_renderer_contracts.py -v
```

Attendu : ~12-15 passed.

---

## Task 3 — Perf solveur déduction 3D

### 4 tests

**Test 1 — Search space trop grand (timeout implicite)**

Construire un `visual_data` deduction sans contraintes dont le search space dépasse `MAX_DEDUCTION_SOLVER_COMBINATIONS`. Vérifier que `analyze_deduction_uniqueness()` retourne immédiatement avec `reason="search_space_too_large"` sans boucle combinatoire.

```python
def test_large_search_space_returns_without_computation():
    result = analyze_deduction_uniqueness(visual_data_large, correct_answer="Alice")
    assert result.checked is False
    assert result.reason == "search_space_too_large"
```

**Test 2 — Grille ambiguë (>1 solution)**

Grille 3×3 avec clues insuffisants → plusieurs assignements valides.

```python
def test_ambiguous_grid_returns_multiple_solutions():
    result = analyze_deduction_uniqueness(visual_data_ambiguous, correct_answer="Alice")
    assert result.solution_count != 1 or result.checked is False
```

**Test 3 — Valeurs dupliquées dans une catégorie**

`visual_data` avec une catégorie ayant des doublons → `_build_model` retourne `None` → résultat `unsupported_model`.

```python
def test_duplicate_values_returns_unsupported_model():
    result = analyze_deduction_uniqueness(visual_data_with_duplicates, correct_answer="Alice")
    assert result.checked is False
    assert result.reason == "unsupported_model"
```

**Test 4 — Benchmark grille 4×4**

```python
import time
import pytest

@pytest.mark.performance
def test_deduction_solver_4x4_under_500ms():
    start = time.perf_counter()
    result = analyze_deduction_uniqueness(visual_data_4x4, correct_answer="Alice")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert result.checked is True
    assert result.solution_count == 1
    assert elapsed_ms < 500, f"Solveur trop lent : {elapsed_ms:.1f}ms (seuil 500ms)"
```

**Seuil 500ms** (et non 100ms) : plus tolérant pour Windows, GitHub Actions (ubuntu-latest), et Render — évite les faux rouges CI liés à la charge machine. Le marqueur `@pytest.mark.performance` permet d'exclure ce test des runs rapides si nécessaire via `pytest -m "not performance"`.

### Vérification

```bash
pytest tests/unit/test_challenge_deduction_solver_perf.py -v
```

Attendu : 4 passed. Pour exclure le benchmark : `pytest tests/unit/test_challenge_deduction_solver_perf.py -v -m "not performance"`.

---

## Séquençage et commits

1. Task 1 : `tests/fixtures/challenges/` + `tests/challenges/test_regression_by_type.py`
   → `git commit -m "test(challenges): add golden test fixtures and parametrized regression suite (Phase 3A)"`

2. Task 2 : `tests/unit/test_challenge_renderer_contracts.py`
   → `git commit -m "test(challenges): add renderer visual_data contract tests (Phase 3B)"`

3. Task 3 : `tests/unit/test_challenge_deduction_solver_perf.py`
   → `git commit -m "test(deduction): add solver perf, uniqueness and edge case tests (Phase 3D)"`

---

## Contraintes absolues

- Zéro appel DB, zéro appel OpenAI, zéro mock réseau
- Zéro modification de fichiers de production
- Fixtures JSON : champs réels du backend (`correct_answer`, `solution_explanation`, `difficulty_rating`, `challenge_type` en majuscules)
- Fixtures invalides : `expected_error_codes` (codes stables de `challenge_validation_error_codes.py`), pas les messages d'erreur bruts
- Benchmark 3D : seuil 500ms, marqueur `@pytest.mark.performance`

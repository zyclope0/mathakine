# Phase 3 — Tests qui protègent les règles (3A + 3B + 3D)

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
| `tests/fixtures/challenges/chess_invalid_king_check.json` | Fixture chess erreur king in check |
| `tests/fixtures/challenges/deduction_valid.json` | Fixture déduction nominale (1 solution unique) |
| `tests/fixtures/challenges/deduction_ambiguous.json` | Fixture déduction ambiguë (>1 solution) |
| `tests/fixtures/challenges/coding_valid.json` | Fixture coding nominale |
| `tests/unit/test_challenge_renderer_contracts.py` | 3B — formes visual_data renderer |
| `tests/unit/test_challenge_deduction_solver_perf.py` | 3D — perf + edge cases solveur |

### Fichiers non modifiés

Aucun fichier de production n'est modifié. Les tests s'appuient sur l'API publique existante :

- `validate_challenge_logic(challenge_data: Dict) -> Tuple[bool, List[str]]` — `challenge_validator.py:104`
- `auto_correct_challenge(challenge_data: Dict) -> Dict` — `challenge_validator.py:874`
- `analyze_deduction_uniqueness(visual_data: Dict, correct_answer: str) -> DeductionUniquenessResult` — `challenge_deduction_solver.py:574`
- `MAX_DEDUCTION_SOLVER_COMBINATIONS = 50_000` — `challenge_deduction_solver.py:25`
- `_build_model(visual_data: Dict) -> Optional[_DeductionModel]` — `challenge_deduction_solver.py:124` (privé, mais testé via `analyze_deduction_uniqueness`)

---

## Task 1 — Golden tests 3A

### Format fixture JSON

```json
{
  "challenge": {
    "challenge_type": "chess",
    "title": "...",
    "description": "...",
    "solution": "...",
    "difficulty": 2,
    "visual_data": { "fen": "..." },
    "choices": null,
    "response_mode": "text"
  },
  "expected_valid": true,
  "expected_errors": []
}
```

Champ `expected_errors` : liste des messages d'erreur exacts retournés par `validate_challenge_logic()`. Peut être non-vide si `expected_valid` est `false`.

### Test paramétrié

```python
from glob import glob
import json
import pytest
from app.services.challenges.challenge_validator import validate_challenge_logic

@pytest.mark.parametrize("fixture_path", sorted(glob("tests/fixtures/challenges/*.json")))
def test_challenge_regression(fixture_path):
    data = json.loads(open(fixture_path, encoding="utf-8").read())
    is_valid, errors = validate_challenge_logic(data["challenge"])
    assert is_valid == data["expected_valid"]
    assert set(errors) == set(data["expected_errors"])
```

### Fixtures livrées (priorité risque)

| Fixture | Type | expected_valid | Cas testé |
|---------|------|---------------|-----------|
| `chess_valid.json` | chess | true | Position légale, roi non en échec |
| `chess_invalid_king_check.json` | chess | false | Roi en échec détecté par le validateur |
| `deduction_valid.json` | deduction | true | Grille 3x3 avec solution unique |
| `deduction_ambiguous.json` | deduction | false | Grille sans contraintes suffisantes (erreur validation) |
| `coding_valid.json` | coding | true | Structure cipher complète |

Fixtures additionnelles (`sequence_valid.json`, `probability_valid.json`, etc.) en nominal-only si temps le permet — à ajouter dans le même dossier sans modifier le test.

### Vérification

```bash
pytest tests/challenges/test_regression_by_type.py -v
```

Attendu : N passed (N = nombre de fixtures × 1 test chacun).

---

## Task 2 — Contrats renderer 3B

### Principe

Tests unitaires purs, fixtures inline (pas de JSON). Chaque test vérifie la forme minimale de `visual_data` qu'un renderer frontend attend. Ces tests ne valident pas la logique métier (déjà couverte par 3A et IA9) — ils vérifient la **structure de données** que le frontend consomme.

Les renderers frontend concernés : `ChallengeChessRenderer`, `ChallengeGraphRenderer`, `ChallengeProbabilityRenderer`, `ChallengeCodingRenderer`, `ChallengeVisualRenderer`.

### Forme minimale par type

| Type | Clés requises dans `visual_data` | Contraintes |
|------|----------------------------------|-------------|
| `chess` | `fen` | string non vide |
| `graph` | `nodes`, `edges` | listes (peuvent être vides pour graphe vide valide) |
| `probability` | `events` | liste d'au moins 1 élément |
| `coding` | `language` OU (`cipher_type` + `encrypted_text`) | string non vide |
| `visual` / `pattern` | `elements` OU `grid` | liste ou dict non vide |

### Structure du fichier

```python
# test_challenge_renderer_contracts.py

class TestChessRendererContract:
    def test_requires_fen_string(self): ...
    def test_fen_must_be_non_empty(self): ...

class TestGraphRendererContract:
    def test_requires_nodes_and_edges(self): ...
    def test_nodes_and_edges_must_be_lists(self): ...

class TestProbabilityRendererContract:
    def test_requires_events_list(self): ...
    def test_events_must_have_at_least_one_item(self): ...

class TestCodingRendererContract:
    def test_requires_language_or_cipher(self): ...
    def test_language_must_be_non_empty_string(self): ...

class TestVisualPatternRendererContract:
    def test_requires_elements_or_grid(self): ...
```

Ces tests sont des assertions directes sur des dicts inline — pas d'appel à `validate_challenge_logic()`.

### Vérification

```bash
pytest tests/unit/test_challenge_renderer_contracts.py -v
```

Attendu : ~10-15 passed.

---

## Task 3 — Perf solveur déduction 3D

### 4 tests

**Test 1 — Timeout (search space trop grand)**

Construire une grille sans contraintes dont le search space dépasse `MAX_DEDUCTION_SOLVER_COMBINATIONS = 50_000`. Vérifier que `analyze_deduction_uniqueness()` retourne `DeductionUniquenessResult(checked=False, reason="search_space_too_large")`.

**Test 2 — Unicité ambiguë**

Grille 3x3 avec contraintes insuffisantes → plusieurs solutions valides → `solution_count > 1` ou `checked=False`.

**Test 3 — Cas limite : valeurs dupliquées**

Passer `visual_data` avec une catégorie ayant des valeurs dupliquées → `_build_model` retourne `None` via `analyze_deduction_uniqueness` → `DeductionUniquenessResult(checked=False, reason="unsupported_model")`.

**Test 4 — Benchmark < 100ms**

Grille 4x4 bien formée avec solution unique. Mesure avec `time.perf_counter()` :

```python
import time
def test_deduction_solver_4x4_under_100ms():
    start = time.perf_counter()
    result = analyze_deduction_uniqueness(visual_data_4x4, correct_answer)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert result.checked is True
    assert result.solution_count == 1
    assert elapsed_ms < 100, f"Solveur trop lent : {elapsed_ms:.1f}ms"
```

### Vérification

```bash
pytest tests/unit/test_challenge_deduction_solver_perf.py -v
```

Attendu : 4 passed.

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
- Les fixtures JSON doivent être lisibles par un humain sans contexte projet
- Le benchmark 100ms est mesuré sans warm-up (premier appel)

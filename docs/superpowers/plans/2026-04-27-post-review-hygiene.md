# Post-Review Hygiene Implementation Plan

> **DONE** — implemented by commits `c58b5bc`, `cfd3a96`, `9cf2504`, `4bb3af6`, and the final beta.5 release-alignment commit.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corriger 3 lots d'hygiène identifiés par la revue multi-modèles des 32 commits : doc cosmétique + loguru, PII résiduel dans user_handlers, et fixtures golden tests manquantes / response_mode invalide.

**Architecture:** 3 commits indépendants, scope étroit, zéro migration DB, zéro nouvelle feature. Task 1 et Task 3 sont sans risque (mécanique). Task 2 est isolée volontairement (PII = lecture + correction chirurgicale, non mécanique).

**Tech Stack:** Python 3.12, loguru, pytest, validate_challenge_logic()

---

## Fichiers touchés

| Fichier | Task | Opération |
|---------|------|-----------|
| `docs/superpowers/plans/2026-04-25-cosmetic-findings.md` | 1 | Corriger direction migration loguru dans le texte |
| `app/utils/generation_metrics.py:82-91` | 1 | `%s` / `%.2fs` → `{}` / `{:.2f}s` dans logger.debug |
| `server/handlers/user_handlers.py:164-167` | 2 | `current_user.get("username")` → `current_user.get("id")` |
| `server/handlers/user_handlers.py:214-216` | 2 | `current_user.get("username")` → `current_user.get("id")` |
| `tests/fixtures/challenges/chess_valid.json` | 3 | `response_mode: "text"` → `"open_text"` |
| `tests/fixtures/challenges/chess_invalid_king_check.json` | 3 | `response_mode: "text"` → `"open_text"` |
| `tests/fixtures/challenges/coding_valid.json` | 3 | `response_mode: "text"` → `"open_text"` |
| `tests/fixtures/challenges/deduction_valid.json` | 3 | `response_mode: "text"` → `"interactive_grid"` |
| `tests/fixtures/challenges/deduction_invalid_format.json` | 3 | `response_mode: "text"` → `"interactive_grid"` |
| `tests/fixtures/challenges/sequence_valid.json` | 3 | Créer — fixture nominale SEQUENCE |
| `tests/fixtures/challenges/probability_valid.json` | 3 | Créer — fixture nominale PROBABILITY |
| `tests/fixtures/challenges/graph_valid.json` | 3 | Créer — fixture nominale GRAPH |

---

## Task 1 — Doc cosmétique + generation_metrics loguru

**Contexte :** `docs/superpowers/plans/2026-04-25-cosmetic-findings.md` décrit la migration loguru comme `{}` → `%s` (sens inversé). La convention du projet est `%s` → `{}` (loguru n'interpole pas `%s`). Par ailleurs, `app/utils/generation_metrics.py` utilise encore `%s` dans son seul appel `logger.debug`, alors que le fix auth (commit `c5b6e53`) a harmonisé `auth_service.py`. Ces deux corrections sont mécaniques et sans risque.

**Files:**
- Modify: `docs/superpowers/plans/2026-04-25-cosmetic-findings.md` (section Task 2, lignes ~36-205)
- Modify: `app/utils/generation_metrics.py:82-91`

---

- [ ] **Step 1 : Corriger la direction dans le plan cosmétique**

Dans `docs/superpowers/plans/2026-04-25-cosmetic-findings.md`, la Task 2 (Sec-C2) décrit la migration à l'envers. Remplacer le texte erroné :

Ligne ~36 :
```
| `app/services/auth/auth_service.py` | Harmoniser `{}` → `%s` dans les appels logger (23 occurrences) |
```
→
```
| `app/services/auth/auth_service.py` | Harmoniser `%s` → `{}` dans les appels logger — TERMINÉ (commit c5b6e53) |
```

Ligne ~137 :
```
**Contexte :** `auth_service.py` utilise le format loguru `{}` (ex: `"user_alias={}"`) au lieu de la convention projet `%s` (CLAUDE.md : `logger.error("msg %s", var)`). Les deux fonctionnent avec loguru, mais la convention `%s` est celle du reste du codebase. Il y a 23 occurrences de `{}` dans des chaînes de log. Cette tâche les remplace toutes par `%s`.
```
→
```
**Contexte :** `auth_service.py` utilisait le format stdlib `%s` au lieu du format loguru `{}`. La convention du projet est `{}` (loguru n'interpole pas `%s` — les variables restent littérales). TERMINÉ dans le commit c5b6e53 : 23 occurrences corrigées.
```

Ligne ~139 :
```
**Règle simple :** dans une string argument d'un logger call, remplacer chaque `{}` par `%s`.
```
→
```
**Règle simple :** dans une string argument d'un logger call loguru, utiliser `{}` et non `%s`.
```

- [ ] **Step 2 : Corriger generation_metrics.py**

Dans `app/utils/generation_metrics.py`, lignes 82-91, remplacer :

```python
        logger.debug(
            "Metrics recorded - "
            "Type: %s, Success: %s, Validation: %s, "
            "Auto-corrected: %s, Duration: %.2fs",
            challenge_type,
            success,
            validation_passed,
            auto_corrected,
            duration_seconds,
        )
```

par :

```python
        logger.debug(
            "Metrics recorded - "
            "Type: {}, Success: {}, Validation: {}, "
            "Auto-corrected: {}, Duration: {:.2f}s",
            challenge_type,
            success,
            validation_passed,
            auto_corrected,
            duration_seconds,
        )
```

- [ ] **Step 3 : Vérifier qu'il ne reste aucun `%s` dans generation_metrics.py**

```bash
python -c "
import pathlib
content = pathlib.Path('app/utils/generation_metrics.py').read_text(encoding='utf-8')
lines = [(i+1, l) for i, l in enumerate(content.splitlines()) if '%s' in l]
assert not lines, f'%s restants : {lines}'
print('OK — aucun %s dans generation_metrics.py')
"
```

Attendu : `OK — aucun %s dans generation_metrics.py`

- [ ] **Step 4 : Vérifier que les tests existants passent**

```bash
pytest tests/unit/test_generation_metrics.py -v
```

Attendu : tous verts (le logger.debug ne fait que logguer, aucun test ne vérifie le format de la string).

- [ ] **Step 5 : Commit**

```bash
git add docs/superpowers/plans/2026-04-25-cosmetic-findings.md app/utils/generation_metrics.py
git commit -m "fix(docs+metrics): correct loguru migration direction in cosmetic plan, harmonize %s→{} in generation_metrics logger"
```

---

## Task 2 — PII résiduel dans user_handlers (isolé)

**Contexte :** Deux appels `logger.info` dans `server/handlers/user_handlers.py` passent encore `current_user.get("username")` comme argument, exposant un PII en clair dans les logs. La correction **n'est pas mécanique** : il ne faut pas simplement passer `{}` en remplacement de `%s` — loguru interpolerait alors le username visible. Le bon correctif est de remplacer la valeur par `current_user.get("id")` (user_id entier, non-PII).

Les deux lignes concernées :

**Ligne 164-167** — route GET /api/users/ :
```python
        logger.info(
            "Accès à la liste de tous les utilisateurs par %s. Fonctionnalité en développement.",
            current_user.get("username"),
        )
```

**Ligne 214-216** — route GET /api/users/leaderboard :
```python
        logger.info(
            "Classement récupéré par %s: %s utilisateurs",
            current_user.get("username"),
            len(leaderboard),
        )
```

**Files:**
- Modify: `server/handlers/user_handlers.py:164-167` et `214-216`

---

- [ ] **Step 1 : Confirmer les lignes de fuite PII (logger + username)**

```bash
python -c "
import pathlib, re
content = pathlib.Path('server/handlers/user_handlers.py').read_text(encoding='utf-8')
lines = content.splitlines()
for i, line in enumerate(lines, 1):
    if 'username' in line and ('logger.' in lines[i-2] or 'logger.' in lines[i-3] or 'logger.' in lines[i-1]):
        print(f'  ligne {i}: {line.strip()}')
"
```

Attendu : exactement les lignes ~166 et ~216. Cette commande cherche `username` dans le contexte immédiat d'un appel logger — elle ne remonte pas les occurrences métier (création de compte, validation de form). Si d'autres lignes apparaissent dans ce contexte, les traiter avec la même logique (user_id, pas username).

- [ ] **Step 2 : Corriger la ligne 164-167**

Remplacer :
```python
        logger.info(
            "Accès à la liste de tous les utilisateurs par %s. Fonctionnalité en développement.",
            current_user.get("username"),
        )
```

par :
```python
        logger.info(
            "Accès à la liste de tous les utilisateurs par user_id={}. Fonctionnalité en développement.",
            current_user.get("id"),
        )
```

- [ ] **Step 3 : Corriger la ligne 214-216**

Remplacer :
```python
        logger.info(
            "Classement récupéré par %s: %s utilisateurs",
            current_user.get("username"),
            len(leaderboard),
        )
```

par :
```python
        logger.info(
            "Classement récupéré par user_id={}: {} utilisateurs",
            current_user.get("id"),
            len(leaderboard),
        )
```

- [ ] **Step 4 : Vérifier qu'il ne reste aucun username dans les appels logger**

```bash
python -c "
import pathlib, re
content = pathlib.Path('server/handlers/user_handlers.py').read_text(encoding='utf-8')
lines = content.splitlines()
leaks = []
for i, line in enumerate(lines, 1):
    if 'username' in line and ('logger.' in lines[i-2] or 'logger.' in lines[i-3] or 'logger.' in lines[i-1]):
        leaks.append(f'ligne {i}: {line.strip()}')
assert not leaks, f'PII encore exposé dans les logs : {leaks}'
print('OK — aucun username dans les appels logger')
"
```

Attendu : `OK — aucun username dans les appels logger`

Les occurrences de `username` dans la logique métier (ex: `username=(data.get("username") or "").strip()` pour la création de compte) sont normales et hors scope.

- [ ] **Step 5 : Lancer les tests**

```bash
pytest tests/ -k "user" -v --tb=short 2>&1 | tail -20
```

Attendu : pas de régression (les handlers sont testés par intégration, les changements de log n'affectent pas les réponses HTTP).

- [ ] **Step 6 : Commit**

```bash
git add server/handlers/user_handlers.py
git commit -m "fix(security): replace residual username PII with user_id in user_handlers logs"
```

---

## Task 3 — Fixtures 3A : response_mode + 3 nouvelles fixtures

**Contexte :** Les 5 fixtures existantes ont toutes `"response_mode": "text"` qui n'est pas dans `RESPONSE_MODES` (`open_text`, `single_choice`, `interactive_visual`, `interactive_order`, `interactive_grid`). Valeurs correctes par type d'après `compute_response_mode()` :

| Type | response_mode correct |
|------|-----------------------|
| CHESS | `open_text` |
| CODING | `open_text` |
| DEDUCTION | `interactive_grid` |
| SEQUENCE | `interactive_grid` |
| PROBABILITY | `open_text` |
| GRAPH | `open_text` |

Les 3 nouvelles fixtures (SEQUENCE, PROBABILITY, GRAPH) doivent être validées par `validate_challenge_logic()` avant d'être commitées, avec `expected_error_codes: []` et sans `validation_unknown`.

**Files:**
- Modify: `tests/fixtures/challenges/chess_valid.json`
- Modify: `tests/fixtures/challenges/chess_invalid_king_check.json`
- Modify: `tests/fixtures/challenges/coding_valid.json`
- Modify: `tests/fixtures/challenges/deduction_valid.json`
- Modify: `tests/fixtures/challenges/deduction_invalid_format.json`
- Create: `tests/fixtures/challenges/sequence_valid.json`
- Create: `tests/fixtures/challenges/probability_valid.json`
- Create: `tests/fixtures/challenges/graph_valid.json`

---

- [ ] **Step 1 : Corriger response_mode dans les 5 fixtures existantes**

`tests/fixtures/challenges/chess_valid.json` — remplacer `"response_mode": "text"` par `"response_mode": "open_text"`.

`tests/fixtures/challenges/chess_invalid_king_check.json` — remplacer `"response_mode": "text"` par `"response_mode": "open_text"`.

`tests/fixtures/challenges/coding_valid.json` — remplacer `"response_mode": "text"` par `"response_mode": "open_text"`.

`tests/fixtures/challenges/deduction_valid.json` — remplacer `"response_mode": "text"` par `"response_mode": "interactive_grid"`.

`tests/fixtures/challenges/deduction_invalid_format.json` — remplacer `"response_mode": "text"` par `"response_mode": "interactive_grid"`.

- [ ] **Step 2 : Ajouter la vérification response_mode dans test_regression_by_type.py**

Dans `tests/challenges/test_regression_by_type.py`, ajouter l'import et l'assertion dans `test_challenge_regression` juste après la lecture de la fixture (avant le bloc `validate_challenge_logic`) :

```python
from app.services.challenges.challenge_contract_policy import RESPONSE_MODES
```

Et dans le corps du test, après `expected_codes: list[str] = list(data["expected_error_codes"])` :

```python
    # P1-0 : response_mode doit être absent ou appartenir au contrat RESPONSE_MODES.
    rm = challenge.get("response_mode")
    if rm is not None:
        assert rm in RESPONSE_MODES, (
            f"[{fixture_name}] response_mode={rm!r} invalide — "
            f"valeurs acceptées : {RESPONSE_MODES}"
        )
```

- [ ] **Step 2b : Lancer les golden tests après ajout de la vérification**

```bash
pytest tests/challenges/test_regression_by_type.py -v
```

Attendu : 5 passed. Si des fixtures ont encore `"text"`, elles échoueront ici — corriger d'abord les Step 1 avant de relancer.

- [ ] **Step 3 : Créer sequence_valid.json**

Créer `tests/fixtures/challenges/sequence_valid.json` :

```json
{
  "challenge": {
    "challenge_type": "SEQUENCE",
    "title": "Suite arithmétique",
    "description": "Trouvez le prochain terme de la suite.",
    "correct_answer": "13",
    "solution_explanation": "La suite augmente de 3 à chaque étape : 1, 4, 7, 10, 13.",
    "difficulty_rating": 1,
    "visual_data": {
      "sequence": [1, 4, 7, 10],
      "answer_position": 4
    },
    "choices": null,
    "response_mode": "interactive_grid"
  },
  "expected_valid": true,
  "expected_error_codes": []
}
```

- [ ] **Step 4 : Créer probability_valid.json**

Créer `tests/fixtures/challenges/probability_valid.json` :

```json
{
  "challenge": {
    "challenge_type": "PROBABILITY",
    "title": "Tirage dans une urne",
    "description": "Une urne contient 2 boules rouges et 3 boules bleues. Quelle est la probabilité de tirer une boule rouge ?",
    "correct_answer": "2/5",
    "solution_explanation": "2 boules rouges sur un total de 5 boules : P(rouge) = 2/5.",
    "difficulty_rating": 1,
    "visual_data": {
      "rouge": 2,
      "bleu": 3
    },
    "choices": null,
    "response_mode": "open_text"
  },
  "expected_valid": true,
  "expected_error_codes": []
}
```

- [ ] **Step 5 : Créer graph_valid.json**

Créer `tests/fixtures/challenges/graph_valid.json` :

```json
{
  "challenge": {
    "challenge_type": "GRAPH",
    "title": "Chemin le plus court",
    "description": "Trouvez le chemin le plus court de A à C dans ce graphe.",
    "correct_answer": "A,B,C",
    "solution_explanation": "Le chemin A → B → C a un poids total de 2, c'est le plus court.",
    "difficulty_rating": 1,
    "visual_data": {
      "nodes": ["A", "B", "C"],
      "edges": [
        {"from": "A", "to": "B", "weight": 1},
        {"from": "B", "to": "C", "weight": 1}
      ]
    },
    "choices": null,
    "response_mode": "open_text"
  },
  "expected_valid": true,
  "expected_error_codes": []
}
```

- [ ] **Step 6 : Valider les 3 nouvelles fixtures par le runtime**

```bash
python -c "
from app.services.challenges.challenge_validator import validate_challenge_logic
from app.services.challenges.challenge_validation_error_codes import classify_challenge_validation_errors
import json, pathlib

for name in ['sequence_valid', 'probability_valid', 'graph_valid']:
    data = json.loads(pathlib.Path(f'tests/fixtures/challenges/{name}.json').read_text())
    c = data['challenge']
    ok, errors = validate_challenge_logic(c)
    codes = classify_challenge_validation_errors(errors, c.get('challenge_type', ''))
    assert ok is True, f'{name}: expected valid=True, got {ok}. Errors: {errors}'
    assert codes == [], f'{name}: expected no error codes, got {codes}'
    assert 'validation_unknown' not in codes, f'{name}: validation_unknown present'
    print(f'{name}: OK')
print('Toutes les fixtures valides.')
"
```

Attendu :
```
sequence_valid: OK
probability_valid: OK
graph_valid: OK
Toutes les fixtures valides.
```

- [ ] **Step 7 : Lancer la suite complète de golden tests (8 fixtures maintenant)**

```bash
pytest tests/challenges/test_regression_by_type.py -v
```

Attendu : 8 passed (5 existants + 3 nouveaux).

- [ ] **Step 8 : Commit**

```bash
git add tests/fixtures/challenges/ tests/challenges/test_regression_by_type.py
git commit -m "test(fixtures): fix response_mode contract in 5 existing fixtures, add sequence/probability/graph valid golden tests, guard response_mode in regression test"
```

---

## Vérification finale

```bash
pytest tests/challenges/ tests/unit/test_generation_metrics.py -v --tb=short
```

Attendu : tous verts, aucun `validation_unknown` dans les outputs.

```bash
git log --oneline -5
```

Attendu : 3 commits propres (cosmetic+metrics, PII, fixtures).

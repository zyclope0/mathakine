# PILOTAGE B5.4 - Resserrement mypy scope exercise

> Date: 13/03/2026
> Statut: terminé
> Lot: B5 - CI and typing hardening, sous-lot B5.4

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `pyproject.toml` | M - override mypy pour scope exercise |
| `docs/03-PROJECT/PILOTAGE_CURSOR_BACKEND_CONTRACTS_HARDENING_B54_MYPY_EXERCISE_2026-03-13.md` | A - ce document |

---

## 2. Runtime touché ou non

**Non.** Aucun fichier Python modifié. Seule la configuration mypy dans `pyproject.toml` a été étendue.

---

## 3. Config mypy avant / après

### Avant

- Global : `no_implicit_optional = false`, `disable_error_code` large (assignment, arg-type, return-value, etc.)
- Override B5.2 badge : 9 modules avec durcissement
- Override B5.3 auth : 2 modules avec durcissement
- Pas d'override pour le domaine exercise (generation, query)

### Après

- Global : inchangé
- Override B5.2 badge : inchangé
- Override B5.3 auth : inchangé
- **Nouvel override B5.4 exercise** (2 modules) :
  - `no_implicit_optional = true`
  - `check_untyped_defs = true`
  - `disable_error_code` réduit : `assignment` retiré (Optional explicite requis)
  - Modules : `exercise_generation_service`, `exercise_query_service`

---

## 4. Scope strict retenu

| Module | Statut |
|--------|--------|
| `app.services.exercise_generation_service` | strict |
| `app.services.exercise_query_service` | strict |

**Hors scope (volontairement)** :
- `app.services.exercise_service` — interdit par la mission
- `app.services.exercise_attempt_service` — hors périmètre
- `app/schemas.exercise` — non nécessaire (les services importent les schémas mais passent déjà mypy)
- `app/repositories/exercise_repository.py` — aucun ajustement requis
- `server/handlers/exercise_handlers.py` — hors périmètre B5.4

---

## 5. Corrections de typage appliquées

Aucune. Le scope exercise passait déjà mypy avec les exigences strictes sans modification de code.

---

## 6. Commande mypy utilisée

```bash
mypy app/services/exercise_generation_service.py app/services/exercise_query_service.py
```

---

## 7. Résultat mypy run 1

```
Success: no issues found in 2 source files
```

---

## 8. Résultat mypy run 2

```
Success: no issues found in 2 source files
```

---

## 9. Résultat tests éventuels

```
pytest -q tests/unit/test_exercise_service.py tests/unit/test_exercise_generation.py tests/unit/test_exercise_handlers.py tests/api/test_exercise_endpoints.py --maxfail=20
57 passed in 18.42s
```

---

## 10. Résultat black

```
All done! 257 files would be left unchanged.
```

---

## 11. Résultat isort

```
(no output - vert)
```

---

## 12. Ce qui a été prouvé

- Scope exercise passe mypy avec config plus stricte (no_implicit_optional, check_untyped_defs, assignment réactivé)
- Run 1 et run 2 verts
- Tests exercise verts (57 passed)
- black et isort verts
- Aucune modification runtime — lot config/doc uniquement

---

## 13. Ce qui n'a pas été prouvé

- Passage du mypy global `app/ server/`
- Extension du scope strict à `exercise_service.py`, `exercise_attempt_service.py` ou `exercise_handlers.py`
- Inclusion de `app/schemas/exercise.py` ou `app/repositories/exercise_repository.py` dans le scope

---

## 14. Risques résiduels

- Le mypy global CI peut échouer sur des fichiers hors scope exercise
- `exercise_service.py` reste hors scope — un lot dédié sera nécessaire pour le durcir

---

## 15. Ce qui reste relâché (scope exercise)

Même avec le durcissement, le scope exercise conserve :
- `arg-type`, `return-value`, `union-attr`, `attr-defined`, `var-annotated`, `call-overload`, `operator`, `index` dans `disable_error_code`
- `ignore_missing_imports = true` (hérité du global)
- `Dict[str, Any]` et `List[int]` comme contrats de retour (à remplacer par des DTO dans un lot ultérieur)

---

## 16. GO / NO-GO

**GO** - Le lot B5.4 est clos : resserrement mypy sur le scope exercise (exercise_generation_service, exercise_query_service), documenté et validé. Aucun débordement sur `exercise_service.py`.

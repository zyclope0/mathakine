# PILOTAGE B5.5 - Resserrement mypy scope challenge

> Date: 13/03/2026
> Statut: terminé
> Lot: B5 - CI and typing hardening, sous-lot B5.5

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `pyproject.toml` | M - override mypy pour scope challenge (query, stream) |
| `docs/03-PROJECT/PILOTAGE_CURSOR_BACKEND_CONTRACTS_HARDENING_B55_MYPY_CHALLENGE_2026-03-13.md` | A - ce document |

---

## 2. Runtime touché ou non

**Non.** Aucun fichier Python modifié. Seule la configuration mypy dans `pyproject.toml` a été étendue.

---

## 3. Config mypy avant / après

### Avant

- Global : `no_implicit_optional = false`, `disable_error_code` large (assignment, arg-type, return-value, etc.)
- Override B5.2 badge : 9 modules avec durcissement
- Override B5.3 auth : 2 modules avec durcissement
- Override B5.4 exercise : 2 modules avec durcissement
- Pas d'override pour le domaine challenge (query, stream)

### Après

- Global : inchangé
- Override B5.2 badge : inchangé
- Override B5.3 auth : inchangé
- Override B5.4 exercise : inchangé
- **Nouvel override B5.5 challenge** (2 modules) :
  - `no_implicit_optional = true`
  - `check_untyped_defs = true`
  - `disable_error_code` réduit : `assignment` retiré (Optional explicite requis)
  - Modules : `challenge_query_service`, `challenge_stream_service`

---

## 4. Scope strict retenu

| Module | Statut |
|--------|--------|
| `app.services.challenge_query_service` | strict |
| `app.services.challenge_stream_service` | strict |

**Hors scope (volontairement)** :
- `app.services.challenge_service` — interdit par la mission
- `app.services.challenge_ai_service` — interdit
- `app.services.challenge_validator` — interdit
- `app.services.challenge_answer_service` — hors périmètre
- `app.services.logic_challenge_service` — hors périmètre
- `app/schemas/logic_challenge` — non nécessaire (les services importent les schémas mais passent déjà mypy)
- `server/handlers/challenge_handlers.py` — hors périmètre B5.5

---

## 5. Corrections de typage appliquées

Aucune. Le scope challenge passait déjà mypy avec les exigences strictes sans modification de code.

---

## 6. Commande mypy utilisée

```bash
mypy app/services/challenge_query_service.py app/services/challenge_stream_service.py
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
pytest -q tests/api/test_challenge_endpoints.py tests/api/test_challenges_flow.py tests/unit/test_logic_challenge_service.py tests/unit/test_challenge_answer_service.py --maxfail=20
102 passed in 43.83s
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

- Scope challenge (query, stream) passe mypy avec config plus stricte (no_implicit_optional, check_untyped_defs, assignment réactivé)
- Run 1 et run 2 verts
- Tests challenge verts (102 passed)
- black et isort verts
- Aucune modification runtime — lot config/doc uniquement

---

## 13. Ce qui n'a pas été prouvé

- Passage du mypy global `app/ server/`
- Extension du scope strict à `challenge_service.py`, `challenge_validator.py`, `challenge_ai_service.py` ou `challenge_answer_service.py`
- Inclusion de `app/schemas/logic_challenge.py` dans le scope

---

## 14. Risques résiduels

- Le mypy global CI peut échouer sur des fichiers hors scope challenge
- Les gros hotspots (`challenge_service`, `challenge_validator`, `challenge_ai_service`) restent hors scope — des lots dédiés seront nécessaires pour les durcir

---

## 15. Ce qui reste relâché (scope challenge)

Même avec le durcissement, le scope challenge conserve :
- `arg-type`, `return-value`, `union-attr`, `attr-defined`, `var-annotated`, `call-overload`, `operator`, `index` dans `disable_error_code`
- `ignore_missing_imports = true` (hérité du global)
- `dict[str, Any]` et `List[int]` comme contrats de retour (à remplacer par des DTO dans un lot ultérieur)

---

## 16. GO / NO-GO

**GO** - Le lot B5.5 est clos : resserrement mypy sur le scope challenge (challenge_query_service, challenge_stream_service), documenté et validé. Aucun débordement sur les gros hotspots challenge.

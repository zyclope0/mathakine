# PILOTAGE B5.3 - Resserrement mypy scope auth

> Date: 13/03/2026
> Statut: terminé
> Lot: B5 - CI and typing hardening, sous-lot B5.3

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `pyproject.toml` | M - override mypy pour scope auth |
| `docs/03-PROJECT/PILOTAGE_CURSOR_BACKEND_CONTRACTS_HARDENING_B53_MYPY_AUTH_2026-03-13.md` | A - ce document |

---

## 2. Runtime touché ou non

**Non.** Aucun fichier Python modifié. Seule la configuration mypy dans `pyproject.toml` a été étendue.

---

## 3. Config mypy avant / après

### Avant

- Global : `no_implicit_optional = false`, `disable_error_code` large (assignment, arg-type, return-value, etc.)
- Override critique : `app.db.adapter`, `app.utils.error_handler`, `app.exceptions` - mêmes relaxations
- Override B5.2 badge : 9 modules avec durcissement
- Pas d'override pour le domaine auth

### Après

- Global : inchangé
- Override B5.2 badge : inchangé
- **Nouvel override B5.3 auth** (2 modules) :
  - `no_implicit_optional = true`
  - `check_untyped_defs = true`
  - `disable_error_code` réduit : `assignment` retiré (Optional explicite requis)
  - Modules : `auth_session_service`, `auth_recovery_service`

---

## 4. Scope strict retenu

| Module | Statut |
|--------|--------|
| `app.services.auth_session_service` | strict |
| `app.services.auth_recovery_service` | strict |

**Hors scope (volontairement)** :
- `app.services.auth_service` — refactor large interdit par la mission
- `app/schemas/user.py` — non nécessaire (auth_session/auth_recovery n'importent pas ces schémas)
- `app/exceptions.py` — aucun ajustement requis
- `server/handlers/auth_handlers.py` — hors périmètre B5.3

---

## 5. Corrections de typage appliquées

Aucune. Le scope auth passait déjà mypy avec les exigences strictes sans modification de code.

---

## 6. Commande mypy utilisée

```bash
mypy app/services/auth_session_service.py app/services/auth_recovery_service.py
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
pytest -q tests/api/test_auth_flow.py tests/integration/test_auth_cookies_only.py tests/integration/test_auth_no_fallback.py tests/unit/test_auth_service.py --maxfail=20
68 passed in 29.29s
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

- Scope auth passe mypy avec config plus stricte (no_implicit_optional, check_untyped_defs, assignment réactivé)
- Run 1 et run 2 verts
- Tests auth verts (68 passed)
- black et isort verts
- Aucune modification runtime — lot config/doc uniquement

---

## 13. Ce qui n'a pas été prouvé

- Passage du mypy global `app/ server/`
- Extension du scope strict à `auth_service.py` ou `auth_handlers.py`
- Inclusion de `app/schemas/user.py` dans le scope auth

---

## 14. Risques résiduels

- Le mypy global CI peut échouer sur des fichiers hors scope auth
- `auth_service.py` reste hors scope — un lot dédié sera nécessaire pour le durcir

---

## 15. Ce qui reste relâché (scope auth)

Même avec le durcissement, le scope auth conserve :
- `arg-type`, `return-value`, `union-attr`, `attr-defined`, `var-annotated`, `call-overload`, `operator`, `index` dans `disable_error_code`
- `ignore_missing_imports = true` (hérité du global)
- `Dict[str, Any]` comme contrats de retour (à remplacer par des DTO dans un lot ultérieur)

---

## 16. GO / NO-GO

**GO** - Le lot B5.3 est clos : resserrement mypy sur le scope auth (auth_session_service, auth_recovery_service), documenté et validé. Aucun débordement sur `auth_service.py`.

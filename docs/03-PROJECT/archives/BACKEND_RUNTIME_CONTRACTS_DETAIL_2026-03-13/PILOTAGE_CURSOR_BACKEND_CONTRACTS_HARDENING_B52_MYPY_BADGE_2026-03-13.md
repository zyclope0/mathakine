# PILOTAGE B5.2 - Premier resserrement mypy (scope badge)

> Date: 13/03/2026
> Statut: terminé
> Lot: B5 - CI and typing hardening, sous-lot B5.2

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `pyproject.toml` | M - override mypy pour scope badge |
| `app/services/badge_service.py` | M - `attempt_data: Optional[Dict[str, Any]] = None` |
| `docs/03-PROJECT/PILOTAGE_CURSOR_BACKEND_CONTRACTS_HARDENING_B52_MYPY_BADGE_2026-03-13.md` | A - ce document |

---

## 2. Runtime touché ou non

**Oui, mineur.** Un seul changement : annotation de type dans `badge_service.py` (`attempt_data: Optional[Dict[str, Any]] = None`). Aucune logique métier modifiée.

---

## 3. Config mypy avant / après

### Avant

- Global : `no_implicit_optional = false`, `disable_error_code` large (assignment, arg-type, return-value, etc.)
- Override critique : `app.db.adapter`, `app.utils.error_handler`, `app.exceptions` - mêmes relaxations
- Pas d'override pour le domaine badge

### Après

- Global : inchangé
- **Nouvel override badge** (9 modules) :
  - `no_implicit_optional = true`
  - `check_untyped_defs = true`
  - `disable_error_code` réduit : `assignment` retiré (Optional explicite requis)
  - Modules : `badge_service`, `badge_application_service`, `badge_user_view_service`, `badge_progress_service`, `badge_rarity_service`, `badge_stats_cache`, `badge_award_persistence`, `badge_gamification_updates`, `app.schemas.badge`

---

## 4. Scope strict retenu

| Module | Statut |
|--------|--------|
| `app.services.badge_service` | strict |
| `app.services.badge_application_service` | strict |
| `app.services.badge_user_view_service` | strict |
| `app.services.badge_progress_service` | strict |
| `app.services.badge_rarity_service` | strict |
| `app.services.badge_stats_cache` | strict |
| `app.services.badge_award_persistence` | strict |
| `app.services.badge_gamification_updates` | strict |
| `app.schemas.badge` | strict |

---

## 5. Corrections de typage appliquées

- `badge_service.py` : `attempt_data: Dict[str, Any] = None` -> `attempt_data: Optional[Dict[str, Any]] = None`

---

## 6. Commande mypy utilisée

```bash
mypy app/services/badge_service.py app/services/badge_application_service.py app/services/badge_user_view_service.py app/services/badge_progress_service.py app/services/badge_rarity_service.py app/services/badge_stats_cache.py app/services/badge_award_persistence.py app/services/badge_gamification_updates.py app/schemas/badge.py
```

---

## 7. Résultat mypy run 1

```
Success: no issues found in 9 source files
```

---

## 8. Résultat mypy run 2

```
Success: no issues found in 9 source files
```

---

## 9. Résultat tests éventuels

```
pytest -q tests/api/test_badge_endpoints.py tests/api/test_admin_badges.py tests/unit/test_badge_requirement_engine.py --maxfail=20
27 passed in 13.41s
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

- Scope badge passe mypy avec config plus stricte (no_implicit_optional, check_untyped_defs, assignment réactivé)
- Run 1 et run 2 verts
- Tests badge verts
- black et isort verts
- Aucune régression runtime

---

## 13. Ce qui n'a pas été prouvé

- Passage du mypy global `app/ server/` (erreurs préexistantes dans `admin_audit_service`, `user_handlers`)
- Extension du scope strict à d'autres domaines

---

## 14. Risques résiduels

- Le mypy global CI peut échouer sur des fichiers hors scope badge
- L'extension du plan à d'autres modules nécessitera des lots dédiés

---

## 15. Ce qui reste relâché (scope badge)

Même avec le durcissement, le scope badge conserve :
- `arg-type`, `return-value`, `union-attr`, `attr-defined`, `var-annotated`, `call-overload`, `operator`, `index` dans `disable_error_code`
- `ignore_missing_imports = true` (hérité du global)
- `Dict[str, Any]` et `List[Dict[str, Any]]` comme contrats de retour (à remplacer par des DTO dans un lot ultérieur)

---

## 16. Plan d'extension module par module

| Phase | Modules cibles | Priorité |
|-------|----------------|----------|
| B5.2 (fait) | badge_service, badge_application_service, badge_user_view_service, badge_progress_service, badge_rarity_service, badge_stats_cache, badge_award_persistence, badge_gamification_updates, app.schemas.badge | - |
| Suivant | auth_session_service, auth_recovery_service | haute |
| Suivant | exercise_generation_service, exercise_query_service | haute |
| À exclure pour l'instant | challenge_validator, admin_content_service, user_service | lot dédié |

---

## 17. GO / NO-GO

**GO** - Le lot B5.2 est clos : premier resserrement mypy sur le scope badge, documenté et validé.

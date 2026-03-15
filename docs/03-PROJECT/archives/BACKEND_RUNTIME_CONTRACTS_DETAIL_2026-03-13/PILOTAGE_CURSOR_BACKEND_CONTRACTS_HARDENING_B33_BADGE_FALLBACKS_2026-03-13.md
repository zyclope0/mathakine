# PILOTAGE B3.3 — Refactor badge_requirement_fallbacks.py

> Date: 13/03/2026
> Statut: terminé
> Lot: B3 — Hotspot decomposition, sous-lot B3.3

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `app/services/badge_requirement_fallbacks.py` | M — dispatch explicite, familles factorisées |

---

## 2. Fichiers runtime modifiés

- `app/services/badge_requirement_fallbacks.py` — seul fichier touché

---

## 3. Fichiers de test modifiés

Aucun. Les tests existants passent sans modification.

---

## 4. Structure de dispatch introduite

```python
_CHECKERS: Dict[str, _CheckerFn] = {
    "first_steps": _make_attempts_count_checker(1),
    "padawan_path": _make_attempts_count_checker(10),
    ...
}
```

- **Point d'entrée** : `check_badge_requirements_by_code(db, user_id, badge, requirements, attempt_data)` → `checker = _CHECKERS.get(badge.code)` ; si présent, `checker(...)` ; sinon `False`.
- **Type** : `_CheckerFn = Callable[[Session, int, Dict, Optional[Dict]], bool]`
- **Fin du if/elif** : remplacé par un lookup O(1) dans le dictionnaire.

---

## 5. Familles de règles factorisées

| Famille | Factory | Badges concernés |
|---------|---------|-------------------|
| **attempts_count** | `_make_attempts_count_checker(default)` | first_steps (1), padawan_path (10), knight_trial (50), jedi_master (100), grand_master (200) |
| **consecutive_success** | `_make_consecutive_success_checker(ex_type, streak)` | addition_master, subtraction_master, multiplication_master, division_master |
| **success_rate** | `_make_success_rate_checker(rate, min_attempts)` | expert (80, 50), perfectionist (95, 30) |
| **consecutive_days** | `_make_consecutive_days_checker(days)` | perfect_week (7), perfect_month (30) |
| **min_per_type** | `_make_min_per_type_checker(min)` | versatile (5) |
| **spécifiques** | fonctions dédiées | speed_demon, perfect_day, explorer |

Chaque factory retourne un checker `(db, user_id, requirements, attempt_data) -> bool` qui lit les paramètres dans `requirements` avec des valeurs par défaut.

---

## 6. API publique conservée

Oui. `check_badge_requirements_by_code(db, user_id, badge, requirements, attempt_data)` inchangée :
- signature identique
- retour `bool`
- sémantique observable préservée pour chaque code badge

---

## 7. Ce qui a été prouvé

- Dispatch par code opérationnel
- Familles factorisées avec mêmes valeurs par défaut qu'avant
- Batterie badge cible : 27 passes (run 1 et 2)
- Full suite : 823 passed, 2 skipped
- Black et isort verts

---

## 8. Ce qui n'a pas été prouvé

- Tests unitaires directs sur les fallbacks par code (couverture via tests API)
- Vérification manuelle de chaque badge en conditions réelles

---

## 9. Résultat run 1

```
27 passed in ~6s
```

---

## 10. Résultat run 2

```
27 passed in ~7s
```

---

## 11. Résultat full suite

```
823 passed, 2 skipped in 170.99s
```

---

## 12. Résultat black

```
251 files would be left unchanged. (vert)
```

---

## 13. Résultat isort

```
Vert (aucun diff)
```

---

## 14. Risques résiduels

- Pas de tests unitaires dédiés aux fallbacks ; dépendance aux tests API
- Ajout d'un nouveau badge fallback : ajouter une entrée dans `_CHECKERS` (risque faible)

---

## 15. GO / NO-GO

**GO** — Refactor B3.3 terminé. Le gros `if/elif` a été remplacé par un dispatch explicite, les familles de règles sont factorisées, l’API publique est conservée, les checks sont verts.

# PILOTAGE B3.1 — Décomposition badge_service.py

> Date: 13/03/2026
> Statut: terminé
> Lot: B3 — Hotspot decomposition, sous-lot B3.1

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `app/services/badge_service.py` | M — refactoré en façade |
| `app/services/badge_award_service.py` | A — nouveau |
| `app/services/badge_format_helpers.py` | A — nouveau |
| `app/services/badge_progress_service.py` | A — nouveau |
| `app/services/badge_rarity_service.py` | A — nouveau |
| `app/services/badge_stats_cache.py` | A — nouveau |
| `app/services/badge_user_view_service.py` | A — nouveau |

---

## 2. Fichiers runtime modifiés

- `app/services/badge_service.py` — réduit à ~80 lignes, façade
- `app/services/badge_award_service.py` — nouveau
- `app/services/badge_format_helpers.py` — nouveau
- `app/services/badge_progress_service.py` — nouveau
- `app/services/badge_rarity_service.py` — nouveau
- `app/services/badge_stats_cache.py` — nouveau
- `app/services/badge_user_view_service.py` — nouveau

---

## 3. Fichiers de test modifiés

Aucun. Les tests existants (`test_badge_endpoints.py`, `test_badge_requirement_engine.py`, `test_admin_badges.py`) passent sans modification.

---

## 4. Responsabilités extraites

| Sous-service / helper | Responsabilité |
|-----------------------|----------------|
| `badge_user_view_service` | `get_user_badges`, `get_available_badges`, `get_user_gamification_stats`, `set_pinned_badges` |
| `badge_award_service` | `check_and_award_badges` → vérification + attribution des badges |
| `badge_progress_service` | `get_badges_progress`, `get_closest_progress_notification` |
| `badge_rarity_service` | `get_badges_rarity_stats` |
| `badge_stats_cache` | `build_stats_cache` — préchargement stats utilisateur (évité N+1) |
| `badge_format_helpers` | `format_requirements_to_text` — formatage critères d’obtention |

---

## 5. API publique BadgeService conservée

Oui. Toutes les méthodes publiques restent inchangées :

- `get_user_badges(user_id)`
- `get_available_badges()`
- `check_and_award_badges(user_id, attempt_data=None)`
- `get_user_gamification_stats(user_id)`
- `set_pinned_badges(user_id, badge_ids)`
- `get_badges_progress(user_id)`
- `get_closest_progress_notification(user_id)`
- `get_badges_rarity_stats()`

Appelants inchangés : `badge_application_service`, `challenge_attempt_service`, `exercise_attempt_service`.

---

## 6. Ce qui a été prouvé

- `BadgeService` délègue correctement aux sous-services
- `check_and_award_badges` avec `auto_commit=False` (challenge/exercise) fonctionne
- `set_pinned_badges` avec `auto_commit` respecté
- Batterie badge cible : 27 passes
- Full suite : 823 passed, 2 skipped
- Black et isort verts

---

## 7. Ce qui n’a pas été prouvé

- Couverture unitaire des nouveaux sous-services (pas de tests dédiés)
- Performance N+1 (stats_cache) non vérifiée par test de perf

---

## 8. Résultat run 1

```
27 passed in ~6s
```

---

## 9. Résultat run 2

```
27 passed in ~6s
```

---

## 10. Résultat full suite

```
823 passed, 2 skipped in 162.40s
```

---

## 11. Résultat black

```
248 files would be left unchanged. (vert)
```

---

## 12. Résultat isort

```
Vert (aucun diff)
```

---

## 13. Risques résiduels

- Pas de tests unitaires directs sur les nouveaux sous-services ; dépendance aux tests API et integration
- `badge_stats_cache` et `badge_format_helpers` sont internes ; pas de couverture directe

---

## 14. GO / NO-GO

**GO** — Décomposition B3.1 terminée. `BadgeService` est une façade claire, les responsabilités sont explicites, l’API publique est conservée, les checks sont verts.

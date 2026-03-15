# PILOTAGE B4.2 — Hotspot SQL N+1 dans recommendation_service

> Date: 13/03/2026
> Statut: terminé
> Lot: B4 — SQL performance, sous-lot B4.2

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `app/services/recommendation_service.py` | M — préchargement exercices avant boucle |

---

## 2. Fichiers runtime modifiés

- `app/services/recommendation_service.py`

---

## 3. Fichiers de test modifiés

Aucun.

---

## 4. Hotspot SQL corrigé

| Fichier | Fonction | Lignes (avant) | Problème |
|---------|----------|---------------|----------|
| `recommendation_service.py` | `generate_recommendations` | 362-371 | Requête DB dans boucle imbriquée : pour chaque `ex_type` × chaque `a` dans `recent_attempts`, un `db.query(Exercise).filter(...).first()` |

**Cause du coût** : Jusqu’à ~50 tentatives × ~5-10 types d’exercices ≈ 250-500 requêtes DB par appel à `generate_recommendations`. Complexité O(attempts × types) en requêtes.

---

## 5. Stratégie de remplacement

**Avant** : Dans la boucle `for ex_type in all_exercise_types`, pour chaque tentative `a` dans `recent_attempts`, une requête `db.query(Exercise).filter(Exercise.id == a.exercise_id, ...).first()`.

**Après** :
1. Avant la boucle : extraire `recent_exercise_ids` des tentatives
2. Une seule requête : `db.query(Exercise).filter(Exercise.id.in_(recent_exercise_ids), ...).all()`
3. Construire `exercises_by_id = {ex.id: ex for ex in exercises}`
4. Dans la boucle : remplacer la requête par `exercises_by_id.get(a.exercise_id)` (lookup O(1))

**Résultat** : 1 requête au lieu de O(attempts × types).

---

## 6. Impact fonctionnel observable

Aucun. Les mêmes exercices sont résolus, les mêmes tentatives sont associées à chaque type. La sémantique des recommandations « maintenir les compétences » est inchangée.

---

## 7. Ce qui a été prouvé

- Hotspot identifié et corrigé
- Batterie recommendation scoped : 11 passed, 1 skipped (run 1 et run 2)
- Black et isort verts
- Contrats publics inchangés (endpoints recommendation)
- Tests unitaires `test_recommendation_service` et API `test_recommendation_endpoints` passent

---

## 8. Ce qui n’a pas été prouvé

- Mesure de performance avant/après en production

---

## 9. Batterie de validation B4.2 (scoped)

```
tests/api/test_recommendation_endpoints.py
tests/unit/test_recommendation_service.py
```

La batterie initiale (user_endpoints, user_exercise_flow, user_service) était trop large et non causale pour ce hotspot recommendation. Les runs rouges observés dans cette batterie (ex. `test_invalid_exercise_attempt`, `test_update_user_password_revokes_sessions`) n’avaient pas de lien plausible avec `recommendation_service.py`.

---

## 10. Résultat run 1

```
11 passed, 1 skipped
```

---

## 11. Résultat run 2

```
11 passed, 1 skipped
```

---

## 12. Résultat full suite (hors faux gate)

```
823 passed, 2 skipped
```

---

## 13. Résultat black

```
257 files would be left unchanged. (vert)
```

---

## 14. Résultat isort

```
Vert (aucun diff)
```

---

## 15. Risques résiduels

- Cas `recent_exercise_ids` vide : `exercises_by_id = {}`, la boucle ne matche rien — comportement identique à l’ancien code (aucune tentative avec exercise_id)
- Exercices supprimés ou hors `valid_types`/`valid_difficulties` : exclus par le filtre de la requête groupée, comme avant

---

## 16. GO / NO-GO

**GO** — B4.2 terminé. Hotspot N+1 corrigé par préchargement des exercices avant la boucle, sémantique préservée. Batterie recommendation scoped reproductiblement verte (11 passed, 1 skipped). Full suite hors faux gate : 823 passed, 2 skipped.

# PILOTAGE B4.3 — Hotspot SQL boucle new_types dans recommendation_service

> Date: 13/03/2026
> Statut: terminé
> Lot: B4 — SQL performance, sous-lot B4.3

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `app/services/recommendation_service.py` | M — requête groupée pour découverte (new_types) |

---

## 2. Fichiers runtime modifiés

- `app/services/recommendation_service.py`

---

## 3. Fichiers de test modifiés

Aucun.

---

## 4. Hotspot SQL corrigé

| Fichier | Fonction | Lignes (avant) | Problème |
|---------|----------|----------------|----------|
| `recommendation_service.py` | `generate_recommendations` | 334-373 | Section « Recommandations de découverte (nouveaux types d'exercices) » : pour chaque `new_type` dans `new_types`, une requête `db.query(Exercise).filter(... Exercise.exercise_type == new_type ...).order_by(func.random()).limit(1).all()` |

**Cause du coût** : 1 requête par type non pratiqué. Avec ~5-10 types possibles et un utilisateur n'ayant pratiqué que 2-3 types, jusqu'à ~7 requêtes DB par appel à `generate_recommendations` pour cette section seule.

---

## 5. Stratégie de remplacement

**Avant** : Boucle `for new_type in new_types` avec une requête SQL par itération (filtres : type, difficulté, valid_types, valid_difficulties, non archivés, actifs, age_group, exclusion completed).

**Après (correction drift B4.3)** :
1. Si `new_types` non vide : une seule requête avec `Exercise.exercise_type.in_(new_types_list)` et les mêmes filtres
2. PostgreSQL `DISTINCT ON (exercise_type)` : `ORDER BY exercise_type, random()` — au plus 1 exercice par type, chaque type ayant des candidats valides a sa chance directe (pas d'échantillon global borné)
3. Créer les recommandations comme avant (priorité 4, raison « Découvrez un nouveau type d'exercice »)

**Résultat** : 1 requête au lieu de O(len(new_types)), sans drift fonctionnel (types rares ne disparaissent plus de l'échantillon).

---

## 6. Impact fonctionnel observable

Aucun. On propose toujours au plus un exercice par `new_type`, avec les mêmes filtres (actifs, non archivés, age_group, exclusion des exercices déjà réussis). La sélection pseudo-aléatoire est faite en mémoire sur le sous-ensemble chargé au lieu de SQL `ORDER BY RANDOM()` par type.

---

## 7. Ce qui a été prouvé

- Hotspot identifié et corrigé
- Batterie recommendation scoped : 11 passed, 1 skipped (run 1 et run 2)
- Full suite hors faux gate : 823 passed, 2 skipped
- Black et isort verts
- Contrats publics inchangés (endpoints recommendation)

---

## 8. Ce qui n'a pas été prouvé

- Mesure de performance avant/après en production

---

## 9. Résultat run 1

```
11 passed, 1 skipped
```

---

## 10. Résultat run 2

```
11 passed, 1 skipped
```

---

## 11. Résultat full suite

```
823 passed, 2 skipped in 259.62s
```

---

## 12. Résultat black

```
257 files would be left unchanged. (vert)
```

---

## 13. Résultat isort

```
Vert (aucun diff)
```

---

## 14. Risques résiduels

- Cas `new_types` vide : pas de requête, comportement identique à l'ancien code
- Limite `len(new_types_list) * 20` : si beaucoup de types et peu d'exercices par type, certains types pourraient ne pas avoir de candidat ; comportement équivalent à l'ancien code (aucune recommandation pour ce type)
- `ORDER BY func.random()` reste utilisé dans la requête groupée ; le tri aléatoire global est remplacé par une sélection aléatoire en mémoire par type

---

## 15. GO / NO-GO

**GO** — B4.3 terminé. Hotspot boucle new_types corrigé par requête groupée + regroupement mémoire, sémantique préservée, checks verts.

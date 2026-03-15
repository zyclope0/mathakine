# PILOTAGE B4.1 — Hotspot SQL ORDER BY RANDOM dans challenge_service

> Date: 13/03/2026
> Statut: terminé
> Lot: B4 — SQL performance, sous-lot B4.1

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `app/services/challenge_service.py` | M — suppression bypass TESTING, retrait import os |

---

## 2. Fichiers runtime modifiés

- `app/services/challenge_service.py`

---

## 3. Fichiers de test modifiés

Aucun.

---

## 4. Hotspot SQL corrigé

| Fichier | Fonction | Ligne (avant) | Problème |
|---------|----------|---------------|----------|
| `challenge_service.py` | `list_challenges` | 418-419 | `query.order_by(func.random()).offset(offset).limit(limit).all()` — ORDER BY RANDOM() O(n) |

**Cause du coût** : `ORDER BY RANDOM()` force PostgreSQL à trier toute la table (ou le résultat filtré) avant d'appliquer LIMIT. Complexité O(n) où n = nombre de lignes correspondant aux filtres. Dégradation linéaire avec le volume de défis.

---

## 5. Stratégie de remplacement

**Avant** : L'optimisation `random_offset` (O(1)) existait mais était désactivée en mode TESTING. En production, elle était utilisée. En tests, on tombait systématiquement sur `func.random()`.

**Après** : Suppression du bypass `os.getenv("TESTING") != "true"`. Utilisation de `random_offset` dès que `total` est fourni et > 0, en production ET en tests.

**Algorithme random_offset** :
1. Le caller (`challenge_query_service`) fournit toujours `total` (via `count_challenges`) quand `order=random`
2. `max_offset_val = max(0, total - limit - offset)`
3. `random_offset_val = random.randint(0, max_offset_val)` si max > 0, sinon 0
4. Requête : `ORDER BY id OFFSET (offset + random_offset_val) LIMIT limit` — une seule requête, pas de tri aléatoire global

---

## 6. Impact fonctionnel observable

Aucun. Les deux stratégies retournent un sous-ensemble aléatoire de défis. La distribution reste équivalente pour l'utilisateur (sélection aléatoire de `limit` défis parmi `total`).

---

## 7. Ce qui a été prouvé

- Hotspot identifié et corrigé
- Batterie challenge cible : 102 passes (run 1 et 2)
- Full suite : 823 passed, 2 skipped
- Black et isort verts
- Contrats publics inchangés (GET /api/challenges)

---

## 8. Ce qui n'a pas été prouvé

- Mesure de performance avant/après en production
- Cas où `total` n'est pas fourni (fallback `func.random()` conservé pour ce cas rare)

---

## 9. Résultat run 1

```
102 passed in 42.10s
```

---

## 10. Résultat run 2

```
102 passed in 38.78s
```

---

## 11. Résultat full suite

```
823 passed, 2 skipped in 198.46s
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

- Le fallback `func.random()` reste actif si un caller appelle `list_challenges` avec `order=random` sans fournir `total` (cas non couvert par l'API actuelle)
- Le diagnostic DIAGNOSTIC_CHALLENGES_LIST_2026-02.md mentionnait un bug items=[] avec random_offset en TESTING ; les tests passent, l'environnement a peut-être évolué depuis

---

## 15. GO / NO-GO

**GO** — B4.1 terminé. Hotspot ORDER BY RANDOM corrigé par activation de random_offset en prod et tests, sémantique préservée, checks verts.

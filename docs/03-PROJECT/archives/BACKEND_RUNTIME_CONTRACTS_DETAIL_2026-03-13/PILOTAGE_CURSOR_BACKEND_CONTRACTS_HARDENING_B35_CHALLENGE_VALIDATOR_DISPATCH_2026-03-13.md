# PILOTAGE B3.5 — Dispatch challenge_validator.py

> Date: 13/03/2026
> Statut: terminé
> Lot: B3 — Hotspot decomposition, sous-lot B3.5

---

## 1. Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `app/services/challenge_validator.py` | M — dispatch explicite dans validate_challenge_logic |

---

## 2. Fichiers runtime modifiés

- `app/services/challenge_validator.py` — seul fichier touché

---

## 3. Fichiers de test modifiés

Aucun. Les tests challenge existants passent sans modification.

---

## 4. Structure de dispatch/orchestration introduite

```python
# En fin de module (après tous les validate_*)
_VALIDATORS_BY_TYPE = {
    "PATTERN": validate_pattern_challenge,
    "SEQUENCE": validate_sequence_challenge,
    "PUZZLE": validate_puzzle_challenge,
    "GRAPH": validate_graph_challenge,
    "VISUAL": validate_spatial_challenge,
    "CODING": validate_coding_challenge,
    "RIDDLE": validate_riddle_challenge,
    "PROBABILITY": validate_probability_challenge,
    "CHESS": validate_chess_challenge,
}
```

Dans `validate_challenge_logic` :
```python
validator = _VALIDATORS_BY_TYPE.get(challenge_type)
if validator:
    type_errors = validator(visual_data, correct_answer, solution_explanation)
    errors.extend(type_errors)
```

- **Avant** : if/elif monolithique (~55 lignes) sur 9 types
- **Après** : lookup O(1) + appel du validator (~6 lignes)
- **Validateurs concrets** : laissés en place (validate_pattern_challenge, validate_sequence_challenge, etc.)
- **auto_correct_challenge** : non modifié (hors périmètre B3.5)

---

## 5. API publique conservée

Oui. `validate_challenge_logic(challenge_data) -> Tuple[bool, List[str]]` inchangée :
- signature identique
- sémantique préservée pour chaque type
- `auto_correct_challenge` inchangé
- `ChallengeValidationError` inchangé

Appelants inchangés : `challenge_ai_service`, `challenge_answer_service`.

---

## 6. Ce qui a été prouvé

- Dispatch par type opérationnel
- Batterie challenge cible : 102 passes (run 1 et 2)
- Full suite : 823 passed, 2 skipped
- Black et isort verts

---

## 7. Ce qui n'a pas été prouvé

- `auto_correct_challenge` conserve un if/elif (hors périmètre)
- Tests unitaires directs sur le dispatch

---

## 8. Résultat run 1

```
102 passed in 26.70s
```

---

## 9. Résultat run 2

```
102 passed in 27.01s
```

---

## 10. Résultat full suite

```
823 passed, 2 skipped in 164.32s
```

---

## 11. Résultat black

```
255 files would be left unchanged. (vert)
```

---

## 12. Résultat isort

```
Vert (aucun diff)
```

---

## 13. Risques résiduels

- `auto_correct_challenge` reste avec if/elif (lot futur)
- Validateurs concrets toujours dans le même fichier (~1200 lignes)

---

## 14. GO / NO-GO

**GO** — B3.5 terminé. Dispatch explicite `challenge_type -> validator` en place, orchestration de `validate_challenge_logic` clarifiée, API publique conservée, checks verts.

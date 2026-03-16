# Micro-lot E3b - Challenge Service Create Flow Decomposition

> Iteration `E`
> Status: closed (2026-03-16)

## Contexte

E3 a extrait `_execute_list_with_ordering` pour `list_challenges` — gain local utile mais insuffisant pour clore E3. E3b traite un flux dense et critique avec une vraie décomposition en 4 étapes métier.

## Flux choisi

`create_challenge` — flux critique utilisé par `challenge_ai_service._persist_challenge_sync` pour persister les défis générés par IA.

## Densité initiale constatée

~70 lignes inline mélangeant :
- normalisation age_group
- construction de l'objet LogicChallenge (14+ champs)
- persistance (add, commit, refresh)
- logging

## Étapes séparées après décomposition

1. **Préparation** : `_prepare_challenge_data(...)` — normalise age_group, applique défauts (hints, visual_data), produit un dict prêt pour persistance
2. **Validation** : `_validate_challenge_data(data)` — vérifie titre, description, correct_answer non vides ; lève ValueError si invalide
3. **Mutation** : `_persist_challenge(db, data)` — construit LogicChallenge, add, commit, refresh
4. **Résultat** : `create_challenge` orchestre et retourne le challenge créé

## Structure retenue

- `_prepare_challenge_data` : étape 1, pur (pas de DB)
- `_validate_challenge_data` : étape 2, pur
- `_persist_challenge` : étape 3, mutation DB
- `create_challenge` : point d'entrée public, orchestration lisible

## Hors scope (inchangé)

- list_challenges, record_attempt, get_challenge_for_api
- challenge_ai_service
- handlers HTTP

---

## Compte-rendu final E3b (format obligatoire)

### 1. Fichiers modifiés
- `app/services/challenge_service.py` — décomposition create_challenge en 4 étapes
- `tests/unit/test_challenge_service.py` — 4 tests E3b (prepare, validate, create_raises)
- `docs/03-PROJECT/PILOTAGE_CURSOR_TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_E3B_CHALLENGE_SERVICE_CREATE_FLOW_2026-03-16.md` — ce document

### 2. Fichiers runtime modifiés
- `app/services/challenge_service.py`

### 3. Fichiers de test modifiés
- `tests/unit/test_challenge_service.py`

### 4. Flux choisi
`create_challenge`

### 5. Densité initiale constatée
~70 lignes mélangeant préparation, validation implicite, mutation et résultat.

### 6. Étapes séparées après décomposition
1. _prepare_challenge_data
2. _validate_challenge_data
3. _persist_challenge
4. create_challenge (orchestration)

### 7. Structure retenue
Trois helpers internes + point d'entrée public.

### 8. Ce qui a été prouvé
- Comportement stable : test_challenge_service_integration, tests API
- Testabilité : tests unitaires pour prepare, validate, create_raises

### 9. Ce qui n'a pas été prouvé
- record_attempt, get_challenge_for_api
- challenge_ai_service (hors scope)

### 10. Résultat run 1
81 passed

### 11. Résultat run 2
81 passed

### 12. Résultat full suite éventuelle
`892 passed, 2 skipped`

### 13. Résultat black
OK

### 14. Résultat isort
OK

### 15. Risques résiduels
- Validation ajoutée : create_challenge lève maintenant ValueError si titre/description/correct_answer vides. Les appelants (challenge_ai_service) valident déjà en amont — pas de régression attendue.
- Cette évolution est un durcissement du contrat interne du service, pas une garantie de comportement strictement identique sur des entrées invalides.

### 16. GO / NO-GO
**GO**

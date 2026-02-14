# Analyse de duplication (DRY) — Mathakine

**Date :** Février 2026  
**Dernière analyse complète :** Février 2026  
**Objectif :** Identifier le code dupliqué frontend/backend pour préparer la consolidation (DRY)

---

## Périmètre de l'analyse (scan complet)

| Zone | Fichiers analysés | % du projet |
|------|-------------------|-------------|
| **Frontend** (ts/tsx) | 167 fichiers | 55 % |
| **Backend** (py: server, app, tests) | 136 fichiers | 45 % |
| **Total** | ~303 fichiers source | 100 % |

*Exclusions : node_modules, __pycache__, .next, venv, configs.*

---

## Résumé exécutif

| Périmètre | Zones de duplication | Effort estimé | Statut |
|-----------|----------------------|---------------|--------|
| **Backend** | 4–5 patterns majeurs | 4–6 h | ~70 % traité |
| **Frontend** | 3–4 zones (cards, modals, hooks) | 6–8 h | ~80 % traité |
| **Tests** | Fixtures, patterns | 2 h | En attente |

---

## 1. Backend — Duplications identifiées

### 1.1 Pattern `await request.json()` + validation (répété ~15×)

**Fichiers :** Tous les handlers (auth, user, chat, exercise, challenge, recommendation)

**Pattern actuel (copié ~15 fois) :**
```python
try:
    data = await request.json()
    field = data.get('field', '').strip()
    if not field:
        return JSONResponse({"error": "Champ requis"}, status_code=400)
    # ...
except Exception as e:
    return ErrorHandler.create_error_response(e, 400)
```

**Proposition :** Créer `app/utils/request_utils.py` avec :
- `parse_json_body(request, required_fields: list, optional_fields: dict) -> dict | JSONResponse`
- Gère le try/except, les `.strip()`, les messages 400 standardisés

---

### 1.2 Pattern `get_db_session()` + try/finally (répété ~50×)

**Fichiers :** `auth_handlers`, `user_handlers`, `exercise_handlers`, `challenge_handlers`, `badge_handlers`, `recommendation_handlers`, `auth.py`

**Pattern actuel :**
```python
db = EnhancedServerAdapter.get_db_session()
try:
    # ... logique ...
    db.commit()
except Exception as e:
    db.rollback()
    return ErrorHandler.create_error_response(e)
finally:
    db.close()
```

**Proposition :** Décorateur `@with_db_session` ou context manager `with get_db_session() as db:` qui gère commit/rollback/close automatiquement.

---

### 1.3 `safe_parse_json` dupliqué (évaluation 2026-02)

**Mentionné dans :** `EVALUATION_PROJET_2026-02-07.md` — « `safe_parse_json()` dupliqué dans 3 fichiers »

**Proposition :** Centraliser dans `app/utils/json_utils.py` (qui existe déjà avec `parse_choices_json`, `make_json_serializable`) — ajouter `safe_parse_json(request)` si ce n'est pas déjà présent.

---

### 1.4 Error handling mixte

**Constat :** Mix de `ErrorHandler.create_error_response()` et `JSONResponse({"error": ...}, status_code=400)` direct.

**Proposition :** Uniformiser via `ErrorHandler.create_error_response()` ou `ErrorHandler.create_validation_error()` pour toutes les erreurs 4xx/5xx.

---

## 2. Frontend — Duplications identifiées

### 2.1 ExerciseCard vs ChallengeCard (quasi-identique)

**Fichiers :**
- `frontend/components/exercises/ExerciseCard.tsx`
- `frontend/components/challenges/ChallengeCard.tsx`

**Structure commune :**
- `motion.div` avec mêmes variants (opacity, scale, whileHover)
- `Card` avec `card-spatial-depth`, `role="article"`
- Badge "Résolu" vert identique
- `CardHeader`, `CardTitle`, badges type/âge
- Bouton "Voir" / "Découvrir" en bas
- `useAccessibleAnimation`, `createVariants`, `createTransition`

**Différences :** Types (Exercise vs Challenge), hooks (useCompletedExercises vs useCompletedChallenges), constantes (exercises vs challenges).

**Proposition :** Créer `ContentCard<T>` générique avec `renderHeader`, `renderFooter`, `onClick` en props. Ou `useContentCard()` hook partagé pour la logique (variants, completed badge, etc.).

---

### 2.2 ExerciseModal vs ChallengeModal (structure similaire)

**Fichiers :**
- `frontend/components/exercises/ExerciseModal.tsx`
- `frontend/components/challenges/ChallengeModal.tsx`

**Structure commune :**
- `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle`
- Pattern `useExercise(id)` / `useChallenge(id)` → `{ data, isLoading, error }`
- Badge type + âge
- Boutons / actions différentes (exercice = choix, challenge = formulaire)

**Proposition :** Base `ContentModal` avec slots pour header, body, footer. Ou extraire `useContentModal(id, fetchHook)` pour isLoading/error/handleClose.

---

### 2.3 useExercises vs useChallenges (pattern quasi-identique)

**Fichiers :**
- `frontend/hooks/useExercises.ts`
- `frontend/hooks/useChallenges.ts`

**Structure commune :**
- `useQuery` avec `queryKey` [entity, skip, limit, type, age_group, search, locale]
- `URLSearchParams` pour construire la query string
- `api.get<PaginatedResponse<T>>(endpoint)`
- `useEffect` pour invalider sur changement de locale
- `debugLog`, `staleTime`, `gcTime`, `retry`

**Proposition :** Hook générique `usePaginatedContent<T>(config: { endpoint, queryKey, paramKeys })` qui factorise la logique.

---

### 2.4 Constantes âge (exercises vs challenges)

**Fichiers :**
- `frontend/lib/constants/exercises.ts` — `AGE_GROUP_DISPLAY`, `AGE_GROUP_COLORS`, `getAgeGroupColor`
- `frontend/lib/constants/challenges.ts` — Ré-exporte `getAgeGroupColor` depuis exercises ✅, mais définit `getAgeGroupDisplay` avec un `displayMap` en dur qui duplique `AGE_GROUP_DISPLAY`

**Proposition :** `challenges.ts` doit utiliser `AGE_GROUP_DISPLAY` de `exercises.ts` au lieu de son propre `displayMap`.

---

### 2.5 useCompletedExercises vs useCompletedChallenges (quasi-identique)

**Fichier :** `frontend/hooks/useCompletedItems.ts` — 2 hooks dans le même fichier

**Structure commune :**
- `useQuery<number[], ApiClientError>` avec `queryKey` différent
- `api.get<{ completed_ids: number[] }>(endpoint)` — `/api/exercises/completed-ids` vs `/api/challenges/completed-ids`
- Gestion 401 → retourner `[]`
- Même `staleTime`, `refetchOnMount`, `refetchOnWindowFocus`, `retry`
- Retour : `{ completedIds, isLoading, error, isCompleted(id) }`

**Différences :** Endpoint, queryKey, log de debug.

**Proposition :** Hook générique `useCompletedIds(config: { endpoint, queryKey })` — 2 occurrences, règle des 3 non atteinte. Optionnel.

---

## 3. Tests — Duplications

**Mentionné dans :** `tests/PLAN_TESTS_AMELIORATION.md`

- `test_challenge_endpoints.py` et `test_logic_challenge_isolated.py` couvrent les mêmes endpoints
- Helpers d'auth (cookie, headers) dupliqués — proposer `tests/fixtures/auth_fixtures.py`

---

## 4. Priorités suggérées pour refactoring

| Priorité | Action | Effort | Impact |
|----------|--------|--------|--------|
| P1 | Backend : `parse_json_body()` utilitaire | 1h | Réduit ~15 blocs |
| P2 | Backend : décorateur/CM `@with_db_session` | 2h | Réduit ~50 blocs try/finally |
| P3 | Frontend : `ContentCard` ou `useContentCard` | 2h | Réduit duplication cards |
| P4 | Frontend : `usePaginatedContent` hook | 1h | Réduit duplication hooks |
| P5 | Frontend : `getAgeGroupDisplay` unifié | 30 min | Supprime doublon |
| P6 | Tests : fixtures auth centralisées | 1h | Maintenabilité |

---

## 5. Réalisations (15/02/2026)

| Priorité | Statut | Détails |
|----------|--------|---------|
| **P5** | ✅ Fait | `getAgeGroupDisplay` dans `exercises.ts`, ré-exporté par `challenges.ts` |
| **P1** | ✅ Fait | `app/utils/request_utils.py` — `parse_json_body()`. Utilisé dans : `auth_handlers` (3×), `chat_handlers` (1×). Reste 7× `request.json()` dans exercise, challenge, user, recommendation — extension optionnelle |
| **P2** | ✅ Fait | `app/utils/db_utils.py` — `db_session()` context manager async. Migration complète vers `async with db_session() as db` dans : `auth.py`, `auth_handlers`, `user_handlers`, `exercise_handlers`, `challenge_handlers`, `badge_handlers`, `recommendation_handlers` |
| **P3** | ✅ Fait | `ContentCardBase.tsx` déjà existant, utilisé par `ExerciseCard` et `ChallengeCard` |
| **P4** | ✅ Fait | `frontend/hooks/usePaginatedContent.ts` — hook générique pour pagination. Refactor de `useExercises` et `useChallenges` qui l'utilisent. |
| **P6** | ⏳ En attente | Fixtures auth centralisées — à faire si besoin |

---

## 6. Métriques du scan (Février 2026)

### 6.1 Backend — Occurrences mesurées

| Pattern | Occurrences | Traité | Restant | Fichiers concernés |
|---------|-------------|--------|---------|-------------------|
| `await request.json()` | 11 | 4 (parse_json_body) | 7 | auth, chat, exercise, challenge, user, recommendation |
| `JSONResponse({"error": ...})` | ~45 | — | ~45 | Tous les handlers |
| `ErrorHandler.create_error_response()` | ~10 | ~10 | 0 | exercise, challenge |
| `db_session()` (CM) | — | 100 % | 0 | Tous les handlers migrés |

**Constat :** `parse_json_body` utilisé dans 4 endpoints (auth x3, chat x1). Les 7 autres `request.json()` dans exercise, challenge, user, recommendation pourraient en bénéficier. Error handling : mix ErrorHandler (~10) et JSONResponse direct (~45) — uniformisation optionnelle.

### 6.2 Frontend — Occurrences mesurées

| Pattern | Fichiers | Statut | Détail |
|---------|----------|--------|--------|
| usePaginatedContent | useExercises, useChallenges | ✅ Factorisé | Hook générique en place |
| ContentCardBase | ExerciseCard, ChallengeCard | ✅ Factorisé | Composant partagé |
| useExercise / useChallenge | 2 hooks | ⚠️ Similaire | Structure quasi-identique (~35 lignes chacun) — 2 occurrences, règle des 3 non atteinte |
| useCompletedExercises / useCompletedChallenges | 2 hooks (même fichier) | ⚠️ Similaire | Quasi-identique — 2 occurrences, règle des 3 non atteinte |
| ExerciseModal / ChallengeModal | 2 composants | ⚠️ Similaire | Dialog, useExercise/useChallenge, badges — 2 occurrences |
| Constantes âge | exercises.ts, challenges.ts | ✅ Unifié | challenges ré-exporte exercises |
| Chatbot / ChatbotFloating | 2 composants | ℹ️ Volontaire | Variantes (inliné vs flottant) — duplication acceptable |

### 6.3 Tests — Périmètre

| Élément | Fichiers avec auth/cookies | Fixtures centralisées |
|---------|---------------------------|------------------------|
| conftest.py | — | Fixtures de base |
| test_auth_flow, test_sse_auth, test_challenges_flow… | 8+ fichiers | Non — helpers dupliqués (test_user_data, padawan_client, authenticated_user) |

### 6.4 Utilitaires non dupliqués

- `app/utils/json_utils.py` : pas de `safe_parse_json` — mention dans EVALUATION était peut-être obsolète ou ailleurs. Contient `parse_choices_json`, `make_json_serializable`.

---

## 7. Synthèse et recommandations

### Réalisé (priorités P1–P5)
- Backend : db_session (100 %), parse_json_body (4 endpoints)
- Frontend : usePaginatedContent, ContentCardBase, getAgeGroupDisplay unifié

### Optionnel (règle des 3 non atteinte)
| Zone | Occ. | Action | Priorité |
|------|------|--------|----------|
| useExercise / useChallenge | 2 | Attendre 3ᵉ hook similaire | Basse |
| useCompletedExercises / useCompletedChallenges | 2 | Idem | Basse |
| ExerciseModal / ChallengeModal | 2 | Idem | Basse |
| Étendre parse_json_body | 7 handlers | Réduit duplication mineure | Moyenne |
| Error handling uniforme | ~45 JSONResponse | Effort élevé, gain modéré | Basse |
| Fixtures auth tests | 8+ fichiers | Si maintenance tests douloureuse | Conditionnelle |

### Conclusion
**~80 % des duplications significatives traitées.** Les gains majeurs (db_session, usePaginatedContent, ContentCard) sont en place. Le reste répond à la règle des 3 : attendre une 3ᵉ occurrence ou une douleur concrète avant de factoriser.

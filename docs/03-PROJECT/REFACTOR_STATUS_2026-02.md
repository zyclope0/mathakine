# État du refactoring — Mathakine

**Date :** 28/02/2026  
**Référence :** [PLAN_CLEAN_CODE_ET_DTO_2026-02.md](./PLAN_CLEAN_CODE_ET_DTO_2026-02.md), [PLAN_REFACTO_ARCHITECTURE_2026-02.md](./PLAN_REFACTO_ARCHITECTURE_2026-02.md)

---

## Vue d'ensemble

| Plan | P1–P3 / Ph1–Ph3 | Restant |
|------|-----------------|---------|
| **Clean Code & DTO** | ✅ Terminé | P4 (admin DTO, OpenAPI, mypy) |
| **Architecture** | ✅ Terminé | Ph4 (dépendances inversées, reporté) |

---

## Clean Code & DTO — Terminé (P1–P3)

### Priorité 1
- **1.1** Facteur commun count/select — Helper pour requêtes listes
- **1.2** SubmitAnswerRequest (Pydantic) — validation entrée POST attempt
- **1.3** ExerciseListResponse, ExerciseListItem — contrat sortie GET exercises

### Priorité 2
- **2.1** ListExercisesQuery — contrat entrée GET /api/exercises
- **2.2** ListChallengesQuery, ChallengeListResponse — pattern aligné
- **2.3** `app/utils/enum_mapping.py` — `*_from_api`, `*_to_api` centralisés

### Priorité 3
- **3.1** `app/exceptions.py` — ExerciseNotFoundError, ExerciseSubmitError
- **3.2** Handlers submit_answer, get_exercise — catch ciblé (ExerciseNotFoundError, ExerciseSubmitError)
- **3.3** SubmitAnswerResponse (Pydantic) — `submit_answer_result` retourne type dédié

### Alignement auditeur (28/02/2026)
- **parse_json_body_any** : `app/utils/request_utils.py` — centralise parsing JSON sans validation de champs
- Handlers migrés : admin (10×), user (3×), challenge (1×), recommendation, badge, feedback, analytics
- **ChallengeNotFoundError** : `app/exceptions.py` — `get_challenge_or_raise`, `get_challenge_for_api` lève
- Catch ciblé : `get_challenge`, `submit_challenge_answer`, `get_challenge_hint`

### Priorité 4 (à faire)
- 4.1 DTO endpoints admin (AdminUsersQuery, etc.)
- 4.2 Documenter contrats OpenAPI
- 4.3 Audit mypy modules critiques

---

## Architecture — Terminé (Ph1–Ph3)

### Phase 1 — Routes découpées ✅
- **Avant :** `server/routes.py` monolithique (~383 lignes, 65+ imports)
- **Après :** `server/routes/` par domaine
  - `core.py`, `auth.py`, `users.py`, `exercises.py`, `challenges.py`, `badges.py`, `admin.py`, `misc.py`
  - Agrégation via `get_routes()` dans `__init__.py`

### Phase 2 — Parsing / mapping handlers ✅
- `parse_challenge_list_params` → ChallengeListParams
- `parse_admin_*_params` — admin_list_params.py
- `format_paginated_response`, `challenge_to_api_dict`

### Phase 3 — ExerciseService découpé ✅
- **Extraction :** `app/services/exercise_stats_service.py` (~270 lignes)
- Handler `get_exercises_stats` utilise ExerciseStatsService
- ExerciseService allégé

### Phase 4 (reporté)
- Dépendances inversées (ORM direct assumé pour l’instant)

---

## Fichiers clés

| Élément | Fichier |
|---------|---------|
| Exceptions métier | `app/exceptions.py` (ExerciseNotFoundError, ExerciseSubmitError, ChallengeNotFoundError) |
| Schémas API exercices | `app/schemas/exercise.py` (SubmitAnswerRequest, SubmitAnswerResponse) |
| Mapping enum | `app/utils/enum_mapping.py` |
| Routes par domaine | `server/routes/*.py` |
| Stats exercices | `app/services/exercise_stats_service.py` |

---

## Références

- [PLAN_CLEAN_CODE_ET_DTO_2026-02.md](./PLAN_CLEAN_CODE_ET_DTO_2026-02.md) — Détail étapes et historique
- [PLAN_REFACTO_ARCHITECTURE_2026-02.md](./PLAN_REFACTO_ARCHITECTURE_2026-02.md) — Phases architecture
- [ANALYSE_DUPLICATION_DRY_2026-02.md](./ANALYSE_DUPLICATION_DRY_2026-02.md) — DRY backend/frontend

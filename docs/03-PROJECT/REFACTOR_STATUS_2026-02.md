# État du refactoring — Mathakine

**Date :** 07/03/2026  
**Référence :** [PLAN_CLEAN_CODE_ET_DTO_2026-02.md](./PLAN_CLEAN_CODE_ET_DTO_2026-02.md), [PLAN_REFACTO_ARCHITECTURE_2026-02.md](./AUDITS_ET_RAPPORTS_ARCHIVES/PLAN_REFACTO_ARCHITECTURE_2026-02.md)

---

## Vue d'ensemble

| Plan | P1–P3 / Ph1–Ph3 | Restant |
|------|-----------------|---------|
| **Clean Code & DTO** | ✅ Terminé | P4 (admin DTO, OpenAPI) — mypy ✅ fait |
| **Architecture** | ✅ Terminé | Ph4 (dépendances inversées, reporté) |
| **Stabilisation pré-backlog** | ✅ B1 flux critiques clarifiés, ✅ B2 handlers critiques allégés, ✅ F2 anti-patterns React nettoyés, ✅ F1.1/F1.2 dashboard alignés | `F1.3` / `F1.4` design-system restant avant backlog |

---

## Stabilisation pré-backlog — Mars 2026

### B1 — Transactions backend

- `daily_challenge` : commit unique clarifié dans `app/services/daily_challenge_service.py`
- `auth/register` : création user + token regroupée via `create_registered_user_with_verification()`
- `auth/login` : login + session regroupés via `authenticate_user_with_session()`
- `exercise attempt` : `ExerciseService.submit_answer_result()` reste le propriétaire du commit final
- `challenge attempt` : `LogicChallengeService.submit_answer_result()` reste le propriétaire du commit final
- `profile/session` : mutations profil et sessions laissées aux services sans logique transactionnelle métier complexe côté handler

### Vérification B1

- suites unitaires et API ciblées vertes sur `daily`, `auth`, `user`, `exercise`, `challenge`
- passe finale B1 : `163` tests ciblés OK
- réserve conservée hors flux critiques : zones `admin_*`, `feedback`, `analytics`, `enhanced_server_adapter`, `challenge_service` legacy

### B2 — Handler -> service boundary

- `auth_handlers.py` : login/refresh recentrés sur appel service + helpers de réponse/cookies
- `user_handlers.py` : normalisation profil et sérialisation utilisateur sorties du handler principal
- `exercise_handlers.py` : validation de payload de soumission isolée
- `challenge_handlers.py` : normalisation de payload de soumission isolée
- lot B2 validé par suites ciblées `auth/user` puis `exercise/challenge`

### F2 — Anti-patterns React

- `F2.1` : `DarkModeToggle`, `InstallPrompt`, `AlphaBanner`, `reset-password/page.tsx`
- `F2.2` : `ProtectedRoute`, `AccessibilityToolbar`, `ExerciseModal`
- `F2.3` : `CodingRenderer`, `DeductionRenderer`, `ProbabilityRenderer`, `RiddleRenderer`, `GraphRenderer`, `ChessRenderer`
- `0` occurrence restante de `eslint-disable-next-line react-hooks/set-state-in-effect` sur le périmètre identifié

### F1 — Design system frontend

- `F1.1` : `LeaderboardWidget`, `AverageTimeWidget`, `RecentActivity`, `CategoryAccuracyChart`, `LevelIndicator`
- `F1.2` : `QuickStartActions`, `StatsCard`, `DashboardSkeletons`
- surfaces dashboard unifiées autour de classes partagées dans `frontend/app/globals.css`
- restent avant backlog : `F1.3` (générateurs) et `F1.4` (renderers visuels, surtout `CodingRenderer`)

### Validation locale complète

- backend : `flake8` critique, `black --check`, `isort --check`, `mypy`, `pytest tests/ -m "not slow"`, smoke `/health`
- frontend : `tsc --noEmit`, `eslint`, `prettier --check`, `i18n:check`, `i18n:validate`, `vitest --run`, `next build`
- résultat : validation locale verte au 07/03/2026 ; lot `F1.1` / `F1.2` revalidé avec `eslint`, `tsc --noEmit`, `next build`

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
- 4.3 Audit mypy modules critiques — ✅ Fait (22/02) : config pyproject, CI, types critiques (adapter, error_handler), overrides no-any-return

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
- [PLAN_REFACTO_ARCHITECTURE_2026-02.md](./AUDITS_ET_RAPPORTS_ARCHIVES/PLAN_REFACTO_ARCHITECTURE_2026-02.md) — Phases architecture
- [ANALYSE_DUPLICATION_DRY_2026-02.md](./ANALYSE_DUPLICATION_DRY_2026-02.md) — DRY backend/frontend

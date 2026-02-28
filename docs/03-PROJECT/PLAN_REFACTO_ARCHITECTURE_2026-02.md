# Plan de refactoring architecture & modularité

**Date :** 28/02/2026  
**Référence :** Recommandations Audit Backend Alpha 2, Évaluation projet  
**Objectif :** Réduire le couplage handlers/routes/services et améliorer la maintenabilité.

---

## État des lieux (28/02/2026)

| Recommandation | Avancement | Priorité |
|----------------|------------|----------|
| 1. Couplage transport HTTP ↔ logique ↔ persistance | ~60 % | P2 |
| 2. Module routes trop massif | ~10 % | **P2 (en cours)** |
| 3. ExerciseService monolithique | ~20 % | P3 |
| 4. Dépendances inversées | ~40 % | P4 |

---

## Phase 1 — Découper routes.py ✅ terminé

**Objectif :** Réduire le fichier routes unique (~383 lignes, 65+ imports) en modules par domaine.

**Structure cible (implémentée) :**
```
server/
  routes/
    __init__.py         # get_routes() — agrège les sous-modules
    core.py             # health, robots, metrics
    auth.py             # api/auth/*
    users.py            # api/users/*
    exercises.py        # api/exercises/*
    challenges.py       # api/challenges/*
    badges.py           # api/badges/*
    admin.py            # Mount /api/admin/*
    misc.py             # analytics, feedback, recommendations, chat
```

**Convention :** Chaque module exporte `get_xxx_routes() -> List` ou une liste `ROUTES`.

---

## Phase 2 — Découplage handlers (parsing / mapping) ✅ terminé

**Objectif :** Extraire le parsing des paramètres et le mapping de réponse hors des handlers.

**Réalisé (28/02/2026) :**
- `app/utils/response_formatters.py` : `format_paginated_response(items, total, skip, limit)`
- `server/handlers/challenge_list_params.py` : `parse_challenge_list_params(request)` → `ChallengeListParams`
- `app/services/challenge_service.py` : `challenge_to_api_dict(challenge)` pour le mapping
- `server/handlers/admin_list_params.py` : `parse_admin_users_params`, `parse_admin_exercises_params`, `parse_admin_challenges_params`
- Handlers `get_challenges_list`, `admin_users`, `admin_exercises`, `admin_challenges` refactorés

---

## Phase 3 — Découper ExerciseService ✅ terminé

**Objectif :** Réduire le monolithe (~1118 lignes) en services focalisés.

**Réalisé (28/02/2026) :**
- `app/services/exercise_stats_service.py` : `ExerciseStatsService.get_exercises_stats_for_api` (~270 lignes)
- Handler `get_exercises_stats` utilise `ExerciseStatsService`
- `ExerciseService` allégé (~290 lignes en moins)

---

## Phase 4 — Dépendances inversées (optionnel)

**Statut :** Reporté. Le pattern ORM direct dans les services est assumé pour l’instant.

---

## Suite — Clean Code & DTO

→ **[PLAN_CLEAN_CODE_ET_DTO_2026-02.md](./PLAN_CLEAN_CODE_ET_DTO_2026-02.md)** : plan par priorité (DTO, duplication, exceptions, typage).

---

## Historique des modifications

| Date | Phase | Détail |
|------|-------|--------|
| 28/02/2026 | 1 | Création du plan, découpage routes.py : `server/routes/` (core, auth, users, exercises, challenges, badges, admin, misc) |
| 28/02/2026 | 2 | Parsing : challenge_list_params, admin_list_params. Mapping : format_paginated_response, challenge_to_api_dict |
| 28/02/2026 | 3 | ExerciseStatsService : extraction get_exercises_stats_for_api (~270 lignes) |

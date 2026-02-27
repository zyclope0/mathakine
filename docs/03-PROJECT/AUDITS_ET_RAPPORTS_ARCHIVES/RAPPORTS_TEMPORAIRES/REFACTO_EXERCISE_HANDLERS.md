# Refactoring exercise_handlers — Plan méthodique

> Date : 22/02/2026  
> Référence : INVENTAIRE_HANDLERS_DB_DIRECTE.md § 2

---

## Vue d'ensemble

| Handler | Requêtes DB actuelles | Service cible |
|---------|----------------------|---------------|
| `get_exercises_list` | `Exercise`, `Attempt.exercise_id`, filtres, pagination | `ExerciseService.get_exercises_list_for_api` |
| `get_exercises_stats` | `Exercise`, `Attempt`, `LogicChallenge`, `LogicChallengeAttempt` | `ExerciseService.get_exercises_stats_for_api` |
| `submit_answer` | `Exercise` (cast enums) + `ExerciseService.record_attempt` | `ExerciseService.get_exercise_for_submit_validation` + `record_attempt` (déjà) |

**Déjà utilisés :**
- `ExerciseService.get_exercise_for_api` (get_exercise)
- `ExerciseService.record_attempt` (submit_answer)

---

## Ordre d'implémentation

1. **submit_answer** — 1 méthode : `get_exercise_for_submit_validation` (le + petit)
2. **get_exercises_list** — 1 méthode : `get_exercises_list_for_api`
3. **get_exercises_stats** — 1 méthode : `get_exercises_stats_for_api`

---

## Détail par handler

### 1. submit_answer ✅
- **Extraire :** requête `db.query(Exercise, cast...)` → `ExerciseService.get_exercise_for_submit_validation(db, exercise_id)`
- **Retour :** `Optional[Dict]` avec `id`, `exercise_type`, `difficulty`, `correct_answer`, `choices`, `question`, `explanation` (normalisés en majuscules)
- **Garder en handler :** validation réponse, record_attempt, badges, streak, construction JSONResponse

### 2. get_exercises_list ✅
- **Extraire :** toute la logique DB (completed_ids, query, filtres, pagination, construction items)
- **Méthode :** `get_exercises_list_for_api(db, limit, skip, exercise_type, age_group, search, order, hide_completed, user_id)`
- **Retour :** `Dict` avec `items`, `total`, `page`, `limit`, `hasMore`

### 3. get_exercises_stats ✅
- **Extraire :** toutes les requêtes (Exercise counts, by_type, by_difficulty, by_age, Attempt, LogicChallenge, LogicChallengeAttempt)
- **Méthode :** `get_exercises_stats_for_api(db)`
- **Retour :** `Dict` (response_data complet)
- **Helpers :** `_get_mastery_message`, `_get_sage_wisdom` restent dans le handler (ou dans le service)

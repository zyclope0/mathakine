# Inventaire — Handlers qui interrogent la DB directement

> Audit du contournement de la couche service.  
> Date : 22/02/2026

---

## Synthèse

| Handler | Requêtes directes | Priorité |
|---------|-------------------|----------|
| admin_handlers | ~80+ | Moyenne (admin, peu modifié) |
| user_handlers | 1 (export) | ✅ Refactoré |
| exercise_handlers | 0 | ✅ Refactoré |
| auth_handlers | 0 | ✅ Refactoré (26/02) |
| recommendation_handlers | 0 | ✅ Refactoré |
| feedback_handlers | ~2 | Basse |
| analytics_handlers | 1 import | Basse |
| challenge_handlers | 2 imports (minimal) | Basse |

---

## 1. user_handlers.py — Priorité HAUTE ✅ Refactoré (22/02/2026)

Fréquenté par les utilisateurs connectés. Logique métier déplacée vers `UserService`.

| Méthode / zone | Statut |
|----------------|--------|
| `get_users_leaderboard` | ✅ `UserService.get_leaderboard_for_api` |
| `get_all_user_progress` | ✅ `UserService.get_user_progress_for_api` |
| `get_challenges_progress` | ✅ `UserService.get_challenges_progress_for_api` |
| `update_user_me` | ✅ `UserService.update_user_profile` |
| `update_user_password_me` | ✅ `UserService.update_user_password` |
| `delete_user_me` | ✅ `UserService.delete_user` |
| `get_user_sessions` | ✅ `UserService.get_user_sessions_for_api` |
| `revoke_user_session` | ✅ `UserService.revoke_user_session` |
| `export_user_data` | ⏳ Reste en DB directe (non prioritaire) |

---

## 2. exercise_handlers.py — Priorité HAUTE ✅ Refactoré (22/02/2026)

| Méthode / zone | Statut |
|----------------|--------|
| `submit_answer` | ✅ `ExerciseService.get_exercise_for_submit_validation` + `record_attempt` |
| `get_exercises_list` | ✅ `ExerciseService.get_exercises_list_for_api` |
| `get_exercises_stats` | ✅ `ExerciseService.get_exercises_stats_for_api` |

---

## 3. recommendation_handlers.py — Priorité HAUTE

| Méthode / zone | Opérations DB directes |
|----------------|------------------------|
| `get_recommendations` | `db.query(Attempt)`, `LogicChallengeAttempt`, `Exercise`, `LogicChallenge`, `Recommendation`, `db.commit` |
| `handle_recommendation_complete` | `db.query(Recommendation)`, `db.commit` |

**Service existant :** `RecommendationService` — mais les handlers contournent partiellement le service.

---

## 4. auth_handlers.py — Priorité MOYENNE ✅ Refactoré (26/02/2026)

| Méthode / zone | Statut |
|----------------|--------|
| `verify_email` | ✅ `AuthService.verify_email_token` |
| `api_reset_password` | ✅ `AuthService.reset_password_with_token` |

Les handlers login/logout/refresh passent déjà par `AuthService`. Les flows verify/reset passent désormais par le service.

---

## 5. admin_handlers.py — Priorité MOYENNE

Admin uniquement, beaucoup de requêtes :

- Config : `Setting`
- Overview : `User`, `Exercise`, `LogicChallenge`, `Attempt`
- Users : CRUD `User`
- Exercises : CRUD `Exercise`, duplication
- Badges : `Achievement`, `UserAchievement`
- Challenges : CRUD `LogicChallenge`, duplication
- Audit : `AdminAuditLog`
- Analytics / moderation : agrégations diverses

Créer un `AdminService` serait cohérent mais représente un gros chantier.

---

## 6. feedback_handlers.py — Priorité BASSE

- `submit_feedback` : `db.add(FeedbackReport)`, `db.commit`
- `admin_list_feedback` : `db.query(FeedbackReport)`

2 opérations, volumétrie faible.

---

## Recommandation d’ordre de migration

1. ~~**recommendation_handlers**~~ ✅ Fait
2. ~~**user_handlers**~~ ✅ Fait
3. ~~**exercise_handlers**~~ ✅ Fait
4. ~~**auth_handlers**~~ ✅ Fait (26/02/2026)
5. **feedback_handlers** : rapide, 2 méthodes.
6. **admin_handlers** : à traiter en dernier (volume important).

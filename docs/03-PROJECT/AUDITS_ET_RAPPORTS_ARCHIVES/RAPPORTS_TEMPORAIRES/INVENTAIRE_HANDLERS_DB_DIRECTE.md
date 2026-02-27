# Inventaire — Handlers qui interrogent la DB directement

> Audit du contournement de la couche service.  
> Date : 22/02/2026 — Dernière MAJ : 27/02/2026

---

## Synthèse

| Handler | Requêtes directes | Priorité |
|---------|-------------------|----------|
| admin_handlers | 0 | ✅ Refactoré (27/02) |
| user_handlers | 0 | ✅ Refactoré |
| exercise_handlers | 0 | ✅ Refactoré |
| auth_handlers | 0 | ✅ Refactoré (26/02) |
| recommendation_handlers | 0 | ✅ Refactoré |
| feedback_handlers | 0 | ✅ Refactoré (26/02) |
| analytics_handlers | 0 | ✅ Refactoré (26/02) |
| challenge_handlers | 0 | ✅ Refactoré (26/02) |

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
| `export_user_data` | ✅ `UserService.get_user_export_data_for_api` (26/02) |

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

## 5. admin_handlers.py — Priorité MOYENNE ✅ Refactoré (27/02)

**AdminService créé** — lectures/agrégats déplacés :
- Config GET/PUT : `AdminService.get_config_for_api`, `update_config`
- Overview : `AdminService.get_overview_for_api`
- Audit log : `AdminService.get_audit_log_for_api`
- Modération : `AdminService.get_moderation_for_api`
- Reports : `AdminService.get_reports_for_api`

**Users CRUD** : ✅ `AdminService.list_users_for_admin`, `patch_user_for_admin`, `send_reset_password_for_admin`, `resend_verification_for_admin` (26/02)

**Badges CRUD** : ✅ `AdminService.list_badges_for_admin`, `create_badge_for_admin`, `get_badge_for_admin`, `put_badge_for_admin`, `delete_badge_for_admin` (26/02)

**Exercises CRUD** : ✅ `AdminService.list_exercises_for_admin`, `create_exercise_for_admin`, `get_exercise_for_admin`, `put_exercise_for_admin`, `duplicate_exercise_for_admin`, `patch_exercise_for_admin` (27/02)

**Challenges CRUD** : ✅ `AdminService.list_challenges_for_admin`, `create_challenge_for_admin`, `get_challenge_for_admin`, `put_challenge_for_admin`, `duplicate_challenge_for_admin`, `patch_challenge_for_admin` (27/02)

**Export CSV** : ✅ `AdminService.export_csv_data_for_admin` (27/02)

**Reste en DB directe** : Aucun — admin_handlers refactoré.

---

## 6. feedback_handlers.py — Priorité BASSE ✅ Refactoré (26/02)

- `submit_feedback` : ✅ `FeedbackService.create_feedback_report`
- `admin_list_feedback` : ✅ `FeedbackService.list_feedback_for_admin`

---

## Recommandation d’ordre de migration

1. ~~**recommendation_handlers**~~ ✅ Fait
2. ~~**user_handlers**~~ ✅ Fait
3. ~~**exercise_handlers**~~ ✅ Fait
4. ~~**auth_handlers**~~ ✅ Fait (26/02/2026)
5. ~~**feedback_handlers**~~ ✅ Fait (26/02)
6. ~~**admin_handlers**~~ ✅ Refactoré (27/02) — tout via AdminService (config, users, badges, exercises, challenges, export CSV).

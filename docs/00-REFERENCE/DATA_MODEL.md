# Modèle de données — Mathakine

> Scope : `app/models/`
> Updated : 2026-03-27
> Source : code ORM SQLAlchemy — 22 entités actives

---

## Entités actives

| Entité | Table | Module |
|--------|-------|--------|
| `User` | `users` | `app/models/user.py` |
| `Exercise` | `exercises` | `app/models/exercise.py` |
| `Attempt` | `attempts` | `app/models/attempt.py` |
| `Progress` | `progress` | `app/models/progress.py` |
| `SpacedRepetitionItem` | `spaced_repetition_items` | `app/models/spaced_repetition_item.py` |
| `LogicChallenge` | `logic_challenges` | `app/models/logic_challenge.py` |
| `LogicChallengeAttempt` | `logic_challenge_attempts` | `app/models/logic_challenge.py` |
| `ChallengeProgress` | `challenge_progress` | `app/models/challenge_progress.py` |
| `DailyChallenge` | `daily_challenges` | `app/models/daily_challenge.py` |
| `PointEvent` | `point_events` | `app/models/point_event.py` |
| `Achievement` | `achievements` | `app/models/achievement.py` |
| `UserAchievement` | `user_achievements` | `app/models/achievement.py` |
| `Notification` | `notifications` | `app/models/notification.py` |
| `Recommendation` | `recommendations` | `app/models/recommendation.py` |
| `EdTechEvent` | `edtech_events` | `app/models/edtech_event.py` |
| `FeedbackReport` | `feedback_reports` | `app/models/feedback_report.py` |
| `AdminAuditLog` | `admin_audit_logs` | `app/models/admin_audit_log.py` |
| `Setting` | `settings` | `app/models/setting.py` |
| `DiagnosticResult` | `diagnostic_results` | `app/models/diagnostic_result.py` |
| `AiEvalHarnessRun` | `ai_eval_harness_runs` | `app/models/ai_eval_harness_run.py` |
| `AiEvalHarnessCaseResult` | `ai_eval_harness_case_results` | `app/models/ai_eval_harness_run.py` |
| `UserSession` | `user_sessions` | `app/models/user_session.py` |

---

## Schémas clés

### `users`

| Colonne | Type | Notes |
|---------|------|-------|
| `id` | Integer PK | |
| `username` | String(50) unique | Index |
| `email` | String(100) unique | Index |
| `hashed_password` | String(255) | |
| `role` | Enum(UserRole) | padawan / maitre / gardien / archiviste |
| `is_active` | Boolean | |
| `age_group` | String(10) nullable | F42 : `6-8` / `9-11` / `12-14` / `15+` |
| `grade_level` | Integer nullable | |
| `grade_system` | String(20) nullable | `suisse` / `unifie` |
| `current_level` | Integer default=1 | Niveau compte (1–N) |
| `total_points` | Integer default=0 | Cumul points |
| `experience_points` | Integer default=0 | XP pour progression niveau |
| `jedi_rank` | String(50) default=`youngling` | Legacy — neutralisation affichage en cours |
| `current_streak` | Integer default=0 | Jours consécutifs |
| `best_streak` | Integer default=0 | Record de série |
| `last_activity_date` | Date nullable | |
| `pinned_badge_ids` | JSONB nullable | Max 3 IDs épinglés |
| `preferred_difficulty` | String(50) nullable | |
| `preferred_theme` | String(50) nullable | |
| `accessibility_settings` | JSON (TEXT) nullable | |
| `avatar_url` | String nullable | |
| `is_email_verified` | Boolean | |
| `created_at` / `updated_at` | DateTime TZ | |

---

### `exercises`

| Colonne | Type | Notes |
|---------|------|-------|
| `id` | Integer PK | |
| `title` | String | |
| `creator_id` | Integer FK `users.id` nullable | |
| `exercise_type` | String | Enum `ExerciseType` (ADDITION…DIVERS) |
| `difficulty` | String | Enum `DifficultyLevel` (INITIE…GRAND_MAITRE) |
| `difficulty_tier` | Integer nullable | F42 matrice 1–12, indexé |
| `age_group` | String | Groupe d'âge cible |
| `question` | Text | |
| `correct_answer` | String | |
| `choices` | JSON nullable | QCM |
| `explanation` | Text nullable | |
| `hint` | Text nullable | |
| `ai_generated` | Boolean default=False | |
| `is_active` | Boolean default=True | |
| `is_archived` | Boolean default=False | |
| `tags` | String nullable | Séparés par virgules |
| `context_theme` | String nullable | Thème contextuel (legacy SW) |
| `complexity` | Integer nullable | 1–5 |
| `created_at` | DateTime TZ | |

---

### `logic_challenges`

| Colonne | Type | Notes |
|---------|------|-------|
| `id` | Integer PK | |
| `title` | String | |
| `challenge_type` | Enum(LogicChallengeType) | sequence / pattern / visual / puzzle / riddle / deduction / probability / graph / coding / chess / custom |
| `age_group` | Enum(AgeGroup) | GROUP_6_8 / GROUP_10_12 / GROUP_13_15 / GROUP_15_17 / ADULT / ALL_AGES |
| `difficulty_rating` | Float | 1.0–5.0 (score continu) |
| `difficulty_tier` | Integer nullable | F42 matrice 1–12 |
| `response_mode` | String | `qcm` / `text` / `interaction` (contrat IA9) |
| `choices` | JSON nullable | Options QCM |
| `correct_answer` | String | |
| `question` | Text | |
| `is_active` | Boolean default=True | |
| `is_archived` | Boolean default=False | |
| `ai_generated` | Boolean default=False | |
| `star_wars_title` | String nullable | Champ legacy nullable — dette documentée |
| `created_at` | DateTime TZ | |

---

### `point_events` (ledger gamification)

| Colonne | Type | Notes |
|---------|------|-------|
| `id` | Integer PK | |
| `user_id` | Integer FK `users.id` CASCADE | Index + index composite `(user_id, created_at)` |
| `source_type` | String(50) | `PointEventSourceType` (exercise_correct / challenge_correct / streak_bonus / …) |
| `source_id` | Integer nullable | ID de la ressource source |
| `points_delta` | Integer | Positif ou négatif |
| `balance_after` | Integer | Solde après l'événement |
| `details` | JSONB nullable | Données complémentaires libres |
| `created_at` | DateTime TZ | |

---

### `attempts`

| Colonne | Type | Notes |
|---------|------|-------|
| `id` | Integer PK | |
| `user_id` | Integer FK `users.id` | Index composite `(user_id, exercise_id)` |
| `exercise_id` | Integer FK `exercises.id` | |
| `user_answer` | String | |
| `is_correct` | Boolean | Index |
| `time_spent_seconds` | Float nullable | |
| `created_at` | DateTime TZ | |

---

### `progress`

Agrégats de maîtrise par `(user_id, exercise_type, difficulty)`.

| Colonne | Type | Notes |
|---------|------|-------|
| `id` | Integer PK | |
| `user_id` | Integer FK `users.id` | Index composite `(user_id, exercise_type)` |
| `exercise_type` | String | |
| `difficulty` | String | |
| `total_attempts` | Integer default=0 | |
| `correct_attempts` | Integer default=0 | |
| `success_rate` | Float nullable | |
| `last_attempt_at` | DateTime TZ nullable | |
| `updated_at` | DateTime TZ | |

---

### `spaced_repetition_items`

One SM-2 card per `(user_id, exercise_id)`.

| Colonne | Type | Notes |
|---------|------|-------|
| `id` | Integer PK | |
| `user_id` | Integer FK `users.id` CASCADE | Index |
| `exercise_id` | Integer FK `exercises.id` CASCADE | NOT NULL, index |
| `ease_factor` | Float | Ease factor SM-2 |
| `interval_days` | Integer | Intervalle courant |
| `next_review_date` | Date | Date de prochaine revision |
| `repetition_count` | Integer | Nombre de succes consecutifs |
| `last_quality` | Integer nullable | Qualite SM-2 `0..5` |
| `last_attempt_id` | Integer nullable | Correlation idempotente, sans FK |
| `created_at` / `updated_at` | DateTime TZ | |

Index notable :
- unique `(user_id, exercise_id)`
- composite `(user_id, next_review_date)`

---

## Relations principales

```
users
 ├─── exercises (creator_id)          1:N
 ├─── attempts (user_id)              1:N
 ├─── progress (user_id)              1:N
 ├─── spaced_repetition_items         1:N
 ├─── logic_challenge_attempts        1:N
 ├─── challenge_progress (user_id)    1:N
 ├─── point_events (user_id)          1:N  ← ledger gamification
 ├─── user_achievements (user_id)     N:N via user_achievements
 ├─── notifications (user_id)         1:N
 ├─── recommendations (user_id)       1:N
 ├─── user_sessions (user_id)         1:N
 └─── daily_challenges (user_id)      1:N

exercises ──── attempts               1:N
exercises ──── spaced_repetition_items 1:N

logic_challenges
 ├─── logic_challenge_attempts        1:N
 ├─── challenge_progress              1:N
 └─── daily_challenges                1:N
```

---

## Entités secondaires

| Entité | Rôle | Relations |
|--------|------|-----------|
| `Achievement` | Définition des badges (titre, icône, critère) | via `UserAchievement` |
| `UserAchievement` | Badge obtenu par un utilisateur | `user_id` + `achievement_id` |
| `DailyChallenge` | Défi quotidien assigné à un utilisateur | `user_id` + `logic_challenge_id` |
| `Recommendation` | Recommandation exercice ou défi stockée | `user_id` + `exercise_id` / `challenge_id` |
| `EdTechEvent` | Événement analytics (quick_start_click, first_attempt) | `user_id` nullable |
| `FeedbackReport` | Rapport de feedback utilisateur | `user_id` nullable |
| `AdminAuditLog` | Journal d'audit admin (actions CRUD) | `user_id` |
| `Setting` | Paramètres plateforme (clé/valeur) | Pas de FK |
| `DiagnosticResult` | Résultat du diagnostic initial pédagogique | `user_id` |
| `UserSession` | Sessions JWT actives (refresh tokens) | `user_id` |
| `AiEvalHarnessRun` | Résumé d'un run harness IA (IA8) | Pas de FK |
| `AiEvalHarnessCaseResult` | Résultat par cas d'un run harness | `run_id` |

---

## Tables legacy

`app/models/legacy_tables.py` — tables non mappées à des classes ORM actives, importées uniquement pour que `Base.metadata` soit complet lors des migrations Alembic. Ne pas utiliser directement dans les services.

---

## Migrations

33 versions Alembic dans `migrations/versions/`. Migration la plus récente : `20260327_add_content_difficulty_tier.py`.

Voir `docs/01-GUIDES/DATABASE_MIGRATIONS.md` pour le runbook complet.

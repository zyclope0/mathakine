# API QUICK REFERENCE - MATHAKINE

> Condensed reference of active endpoints
> Updated: 08/04/2026
> Runtime source of truth: `server/routes/`

## Reading Rules

- this document summarizes active Starlette routes only
- final truth remains `server/routes/` + `server/handlers/`
- AI model defaults / allowlists / runtime observability are documented in `docs/00-REFERENCE/AI_MODEL_GOVERNANCE.md`
- `app/api/endpoints/*` has been archived in `_ARCHIVE_2026/app/api/` and is not part of the runtime
- the HTML handler `generate_exercise` still exists but is not an active Starlette route
- auth-sensitive and chat endpoints now rely on distributed Redis rate limiting in production; client IP for keys follows `RATE_LIMIT_TRUST_X_FORWARDED_FOR` (see `app/utils/rate_limit.py`, `.env.example`)

## Auth

| Method | Endpoint | Notes |
|---|---|---|
| POST | `/api/auth/login` | login + auth cookies, rate limited |
| GET | `/api/auth/csrf` | fetches CSRF token |
| POST | `/api/auth/validate-token` | token validation; dedicated rate limit (90/min/IP); Next server uses shared runtime + short success dedup (`validateTokenRuntime.ts`) |
| POST | `/api/auth/refresh` | refresh via cookie/body |
| POST | `/api/auth/logout` | clears auth cookies |
| POST | `/api/auth/forgot-password` | generic message, rate limited |
| POST | `/api/auth/reset-password` | revokes older tokens and sessions |
| GET | `/api/auth/verify-email` | email verification |
| POST | `/api/auth/resend-verification` | generic message, rate limited |

## Users

| Method | Endpoint | Notes |
|---|---|---|
| POST | `/api/users/` | registration, rate limited |
| GET | `/api/users/` | placeholder / in development |
| GET | `/api/users/me` | current user (+ `gamification_level`, `total_points`, `current_level`, **`progression_rank`** (bucket public préféré, F43-A3), **`jedi_rank`** (alias legacy, même valeur), `age_group` nullable : tranche pédagogique `6-8` \| `9-11` \| `12-14` \| `15+` si système unifié ; NULL si Harmos / non renseigné) |
| PUT | `/api/users/me` | profile update (incl. `age_group` ; invalide → 400 ; `grade_system` = `suisse` → `age_group` forcé à NULL) |
| PUT | `/api/users/me/password` | password change + revocation |
| DELETE | `/api/users/me` | delete current account |
| GET | `/api/users/me/export` | GDPR export |
| GET | `/api/users/me/sessions` | active sessions |
| GET | `/api/users/me/rank` | rang par points : `1 +` nombre d’utilisateurs **actifs** avec strictement plus de points ; JSON `{ "rank", "total_points" }`. Query `period` = `all` \| `week` \| `month` : `all` = cumul `users.total_points` ; `week` / `month` = somme des `point_events.points_delta` sur fenêtre glissante 7j / 30j (UTC). Valeur invalide → 400. (auth + accès complet) |
| DELETE | `/api/users/me/sessions/{session_id}` | revoke session |
| GET | `/api/users/me/progress/timeline` | progression timeline (exercices **+** défis logiques ; `by_type` inclut des clés `logic_*`). Prérequis DB : migrations `20260325_challenge_progress` puis `20260325_fix_lca_created_at` (head) — voir `docs/03-PROJECT/IMPLEMENTATION_F07_TIMELINE.md` §3.1 bis |
| GET | `/api/users/me/progress` | global progression |
| GET | `/api/users/me/challenges/progress` | progression défis (agrégat + liste par défi) |
| GET | `/api/users/me/challenges/detailed-progress` | maîtrise **par type** de défi (`challenge_progress`) : `items[]` avec `challenge_type`, `total_attempts`, `correct_attempts`, `completion_rate`, `mastery_level`, etc. — alimente le radar défis et le breakdown du widget dashboard |
| GET | `/api/users/stats` | stats **filtre temporel** (tentatives, réussite, séries, graphiques…) — **sans** XP ni niveau compte ; gamification persistante → `/me` (`gamification_level`, `total_points`, …) ; bloc **`spaced_repetition`** (F04) : `f04_initialized`, `active_cards_count`, `due_today_count`, `overdue_count`, `next_review_date` (ISO ou null) ; compteurs alignes sur des cartes **actionnables** seulement (exercices actifs et non archives) |
| GET | `/api/users/me/reviews/next` | F04-P4 : **une** prochaine carte SR due (lecture seule) ; JSON `has_due_review`, `summary` (même forme que le bloc SR de GET /api/users/stats), `next_review` ou null ; `next_review.exercise` = énoncé review-safe (**sans** `correct_answer` / `explanation` / `hint`) ; ordre : retard → dus ce jour → date la plus ancienne → `review_item_id` ; exercice inactif ou archivé exclu (pas de carte « actionnable ») — auth + accès complet |
| GET | `/api/users/leaderboard` | classement : param `limit` (défaut 50, max 100), `period` = `all` \| `week` \| `month` (défaut `all`). `total_points` dans chaque entrée = cumul historique (`users.total_points`) si `all`, sinon somme des gains sur la fenêtre (`point_events`, 7j / 30j glissant UTC). Champs entrée : `rank`, `username`, `total_points`, `current_level`, **`progression_rank`** (F43-A3) + **`jedi_rank`** (alias legacy, même valeur), `is_current_user`, `avatar_url` (nullable), `current_streak`, `badges_count`. Filtre confidentialité `show_in_leaderboards`. `period` invalide → 400. |
| DELETE | `/api/users/{user_id}` | active route, redirects self-delete to `/api/users/me` semantics |

## Daily Challenge

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/daily-challenges` | 3 daily challenges for the user |

## Diagnostic

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/diagnostic/status` | latest score / state |
| POST | `/api/diagnostic/start` | starts a session, returns `state_token` |
| POST | `/api/diagnostic/question` | body uses `state_token`, returns next signed token |
| POST | `/api/diagnostic/answer` | body uses `state_token` + `user_answer`; no client `correct_answer` trust |
| POST | `/api/diagnostic/complete` | body uses `state_token`, persists final result |

Contract note:
- `/api/diagnostic/question` does not expose `correct_answer`
- `/api/diagnostic/answer` may return `correct_answer` only after submission for feedback

## Exercises

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/exercises` | list / filters / hide_completed |
| GET | `/api/exercises/stats` | home + admin academy stats |
| GET | `/api/exercises/interleaved-plan` | interleaved plan |
| GET | `/api/exercises/{exercise_id}` | exercise detail |
| POST | `/api/exercises/generate` | active generation route |
| POST | `/api/exercises/generate-ai-stream` | AI generation SSE (JSON body: `exercise_type`, `age_group`, `prompt`; optional legacy `difficulty` → `age_group`) ; evenements `status`, `exercise`, `error`, `done` — `done` est emis sur succes nominal et fins gerees (`error` validation / persistance). Cote frontend, le client explicite maintenant les echecs `401`, `403`, CSRF manquant et backend generique avant affichage toast. |
| GET | `/api/exercises/completed-ids` | completed ids |
| POST | `/api/exercises/{exercise_id}/attempt` | submit answer (see note below) |

**Exercise attempt — answer matching (backend):** For types other than TEXTE/MIXTE, after exact trim match, equivalent forms are accepted: trailing `%` vs plain number (e.g. `45%` vs `45`), decimal comma vs dot (`3,5` vs `3.5`), simple fraction vs decimal when at least one side uses `/` (e.g. `1/2` vs `0.5`). Not accepted: e.g. `0100` vs `100`, `0.50` vs `0.5`. Implementation: `app/utils/exercise_answer_compare.py`.

## Challenges

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/challenges` | list / filters / hide_completed |
| GET | `/api/challenges/stats` | agrégats **catalogue** défis actifs (`is_active` + non archivés) : `total`, `total_archived`, `by_type`, `by_difficulty`, `by_age_group` — chaque bucket `{ count, percentage }` (pourcentages relatifs à `total`). Auth + accès complet requis (`require_full_access`). Impl. : `ChallengeStatsService.get_challenges_stats_for_api` |
| GET | `/api/challenges/{challenge_id}` | challenge detail (incl. `response_mode` IA9, `choices` filtrés selon politique type) |
| POST | `/api/challenges/{challenge_id}/attempt` | soumission réponse ; corps JSON selon `ChallengeAttemptRequest`. Réponse typée `SubmitChallengeAttemptResult` : `is_correct`, `explanation` (si correct), `new_badges` (chaque entrée : **`thematic_title`** clé publique préférée F43-A4 + **`star_wars_title`** alias legacy, même valeur), `progress_notification`, `hints_remaining` (si incorrect), **`points_earned`** (entier si tentative correcte **et** crédit ledger `apply_points` réussi ; sinon omis/`null`) |
| GET | `/api/challenges/{challenge_id}/hint` | hint |
| GET | `/api/challenges/completed-ids` | completed ids |
| POST | `/api/challenges/generate-ai-stream` | AI generation SSE (JSON body: `challenge_type`, `age_group`, `prompt`) ; événements `status`, `warning`, `challenge`, `error`, `done` — si la validation finale échoue après auto-correction : `error` puis `done`, **pas** d’événement `challenge` ni persistance. Cote frontend, le client explicite maintenant les echecs `401`, `403`, CSRF manquant et backend generique avant affichage toast. |
| GET | `/api/challenges/badges/progress` | challenge badge progress |

## Badges

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/badges/user` | user badges ; chaque entrée `earned_badges[]` inclut **`thematic_title`** (F43-A4, préféré) et **`star_wars_title`** (legacy, même valeur) |
| GET | `/api/badges/available` | public badges, `?limit=N` (défaut 100, max 200) ; même paire de clés **`thematic_title`** + **`star_wars_title`** (alias) sur chaque badge |
| POST | `/api/badges/check` | badge check ; `new_badges[]` avec **`thematic_title`** + **`star_wars_title`** (même valeur) |
| GET | `/api/badges/stats` | gamification stats |
| GET | `/api/badges/rarity` | rarity stats |
| PATCH | `/api/badges/pin` | pin `badge_ids` |
| GET | `/api/challenges/badges/progress` | challenge badge progress |

## Gamification (points ledger)

**Persistence (serveur uniquement)**

- Table PostgreSQL `point_events` : ledger des attributions de points. Écriture **uniquement** côté backend via `GamificationService.apply_points` (`app/services/gamification/gamification_service.py`). **Aucun** endpoint public ne liste les lignes du ledger ni n’expose un `apply_points` générique pour les clients (choix produit / sécurité).

**Exposé aux clients**

- `GET /api/users/me` — champs compte : `gamification_level`, `total_points`, `current_level`, **`progression_rank`** (bucket de rang public préféré, F43-A3), **`jedi_rank`** (alias legacy, même valeur), etc.
- `GET /api/badges/stats` — stats agrégées gamification pour l’utilisateur courant (`get_user_gamification_stats`).
- `POST /api/challenges/{id}/attempt` — champ **`points_earned`** sur la réponse lorsque les points du défi sont attribués avec succès (voir section Challenges).

**Référence longue** : voir `docs/02-FEATURES/GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md` pour la vérité actuelle du compte gamification/ledger, et `ROADMAP_FONCTIONNALITES.md` (F38) pour les suites produit éventuelles.

## Admin

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/admin/health` | admin health |
| GET | `/api/admin/overview` | overview |
| GET | `/api/admin/observability/f43-account-progression` | F43-A1 read-only : répartition utilisateurs **actifs** par colonnes persistées ``users.current_level`` / ``users.jedi_rank`` (mises à jour lors des gains de points). Distinct du détail affiché sur `/me`, qui peut dériver niveau/rang depuis ``total_points``. |
| GET | `/api/admin/users` | user list |
| PATCH | `/api/admin/users/{user_id}` | mutate user |
| POST | `/api/admin/users/{user_id}/send-reset-password` | send reset |
| POST | `/api/admin/users/{user_id}/resend-verification` | resend verification |
| DELETE | `/api/admin/users/{user_id}` | admin delete |
| GET | `/api/admin/exercises` | exercise list |
| POST | `/api/admin/exercises` | create exercise |
| POST | `/api/admin/exercises/{exercise_id}/duplicate` | duplicate exercise |
| GET | `/api/admin/exercises/{exercise_id}` | exercise detail |
| PUT | `/api/admin/exercises/{exercise_id}` | full update |
| PATCH | `/api/admin/exercises/{exercise_id}` | partial update |
| GET | `/api/admin/challenges` | challenge list |
| POST | `/api/admin/challenges` | create challenge |
| POST | `/api/admin/challenges/{challenge_id}/duplicate` | duplicate challenge |
| GET | `/api/admin/challenges/{challenge_id}` | challenge detail |
| PUT | `/api/admin/challenges/{challenge_id}` | full update |
| PATCH | `/api/admin/challenges/{challenge_id}` | partial update |
| GET | `/api/admin/reports` | reports |
| GET | `/api/admin/feedback` | admin feedback |
| GET | `/api/admin/audit-log` | audit log |
| GET | `/api/admin/moderation` | moderation |
| GET | `/api/admin/config` | config read |
| PUT | `/api/admin/config` | config write |
| GET | `/api/admin/export` | CSV export |
| GET | `/api/admin/badges` | badge list |
| POST | `/api/admin/badges` | create badge |
| GET | `/api/admin/badges/{badge_id}` | badge detail |
| PUT | `/api/admin/badges/{badge_id}` | badge update |
| DELETE | `/api/admin/badges/{badge_id}` | soft delete badge |
| GET | `/api/admin/analytics/edtech` | EdTech analytics |
| GET | `/api/admin/ai-stats` | AI runtime stats : coûts **estimés** (pas compta), tokens, ventilation workload (`assistant_chat` = chat **public** rate-limité). Rétention in-memory bornée (`stats.retention`). |
| GET | `/api/admin/generation-metrics` | Qualité runtime (incl. chat public) ; clés inconnues → bucket `unknown` (plus d’attribution silencieuse aux défis). `summary.retention`. |
| GET | `/api/admin/ai-eval-harness-runs?limit=N` | Derniers runs harness **persistés** (IA8) : mode, cible, compteurs, chemins d’artefacts ; distinct du runtime in-memory. |

## Misc

| Method | Endpoint | Notes |
|---|---|---|
| POST | `/api/analytics/event` | app analytics |
| POST | `/api/feedback` | create feedback |
| GET | `/api/recommendations` | recommendations |
| POST | `/api/recommendations/generate` | generate recommendations |
| POST | `/api/recommendations/complete` | mark recommendation complete |
| POST | `/api/chat` | public chat, rate limited |
| POST | `/api/chat/stream` | public chat SSE, rate limited; runtime model policy and cost observability are described in `docs/00-REFERENCE/AI_MODEL_GOVERNANCE.md`. Le proxy Next est maintenant teste directement, y compris la garde de configuration backend invalide. |
| GET | `/health` | backend health |
| GET | `/robots.txt` | robots |
| GET | `/metrics` | Prometheus metrics |

## References

- [AUTH_FLOW.md](AUTH_FLOW.md)
- [F03_DIAGNOSTIC_INITIAL.md](F03_DIAGNOSTIC_INITIAL.md)
- [../00-REFERENCE/ARCHITECTURE.md](../00-REFERENCE/ARCHITECTURE.md)
- [../03-PROJECT/POINTS_RESTANTS_2026-03-15.md](../03-PROJECT/POINTS_RESTANTS_2026-03-15.md)


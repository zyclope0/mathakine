# API QUICK REFERENCE - MATHAKINE

> Condensed reference of active endpoints
> Updated: 23/03/2026
> Runtime source of truth: `server/routes/`

## Reading Rules

- this document summarizes active Starlette routes only
- final truth remains `server/routes/` + `server/handlers/`
- AI model defaults / allowlists / runtime observability are documented in `docs/00-REFERENCE/AI_MODEL_GOVERNANCE.md`
- `app/api/endpoints/*` has been archived in `_ARCHIVE_2026/app/api/` and is not part of the runtime
- the HTML handler `generate_exercise` still exists but is not an active Starlette route
- auth-sensitive and chat endpoints now rely on distributed Redis rate limiting in production

## Auth

| Method | Endpoint | Notes |
|---|---|---|
| POST | `/api/auth/login` | login + auth cookies, rate limited |
| GET | `/api/auth/csrf` | fetches CSRF token |
| POST | `/api/auth/validate-token` | token validation, rate limited |
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
| GET | `/api/users/me` | current user (+ `gamification_level`, `total_points`, `current_level`, `jedi_rank`) |
| PUT | `/api/users/me` | profile update |
| PUT | `/api/users/me/password` | password change + revocation |
| DELETE | `/api/users/me` | delete current account |
| GET | `/api/users/me/export` | GDPR export |
| GET | `/api/users/me/sessions` | active sessions |
| DELETE | `/api/users/me/sessions/{session_id}` | revoke session |
| GET | `/api/users/me/progress/timeline` | progression timeline |
| GET | `/api/users/me/progress` | global progression |
| GET | `/api/users/me/challenges/progress` | challenge progression |
| GET | `/api/users/stats` | stats **filtre temporel** (tentatives, réussite, séries, graphiques…) — **sans** XP ni niveau compte ; gamification persistante → `/me` (`gamification_level`, `total_points`, …) |
| GET | `/api/users/leaderboard` | leaderboard |
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
| POST | `/api/exercises/generate-ai-stream` | AI generation SSE (JSON body: `exercise_type`, `age_group`, `prompt`; optional legacy `difficulty` → `age_group`) |
| GET | `/api/exercises/completed-ids` | completed ids |
| POST | `/api/exercises/{exercise_id}/attempt` | submit answer (see note below) |

**Exercise attempt — answer matching (backend):** For types other than TEXTE/MIXTE, after exact trim match, equivalent forms are accepted: trailing `%` vs plain number (e.g. `45%` vs `45`), decimal comma vs dot (`3,5` vs `3.5`), simple fraction vs decimal when at least one side uses `/` (e.g. `1/2` vs `0.5`). Not accepted: e.g. `0100` vs `100`, `0.50` vs `0.5`. Implementation: `app/utils/exercise_answer_compare.py`.

## Challenges

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/challenges` | list / filters / hide_completed |
| GET | `/api/challenges/{challenge_id}` | challenge detail (incl. `response_mode` IA9, `choices` filtrés selon politique type) |
| POST | `/api/challenges/{challenge_id}/attempt` | submit answer |
| GET | `/api/challenges/{challenge_id}/hint` | hint |
| GET | `/api/challenges/completed-ids` | completed ids |
| POST | `/api/challenges/generate-ai-stream` | AI generation SSE (JSON body: `challenge_type`, `age_group`, `prompt`) ; événements `status`, `warning`, `challenge`, `error`, `done` — si la validation finale échoue après auto-correction : `error` puis `done`, **pas** d’événement `challenge` ni persistance |
| GET | `/api/challenges/badges/progress` | challenge badge progress |

## Badges

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/badges/user` | user badges |
| GET | `/api/badges/available` | public badges, `?limit=N` (défaut 100, max 200) |
| POST | `/api/badges/check` | badge check |
| GET | `/api/badges/stats` | gamification stats |
| GET | `/api/badges/rarity` | rarity stats |
| PATCH | `/api/badges/pin` | pin `badge_ids` |
| GET | `/api/challenges/badges/progress` | challenge badge progress |

## Gamification (points ledger)

**Persistence (serveur uniquement)**

- Table PostgreSQL `point_events` : ledger des attributions de points. Écriture **uniquement** côté backend via `GamificationService.apply_points` (`app/services/gamification/gamification_service.py`). **Aucun** endpoint public ne liste les lignes du ledger ni n’expose un `apply_points` générique pour les clients (choix produit / sécurité).

**Exposé aux clients**

- `GET /api/users/me` — champs persistants de compte : `gamification_level`, `total_points`, `current_level`, `jedi_rank`, etc.
- `GET /api/badges/stats` — stats agrégées gamification pour l’utilisateur courant (`get_user_gamification_stats`).

**Référence longue** : voir `docs/02-FEATURES/GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md` pour la vérité actuelle du compte gamification/ledger, et `ROADMAP_FONCTIONNALITES.md` (F38) pour les suites produit éventuelles.

## Admin

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/admin/health` | admin health |
| GET | `/api/admin/overview` | overview |
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
| POST | `/api/chat/stream` | public chat SSE, rate limited; runtime model policy and cost observability are described in `docs/00-REFERENCE/AI_MODEL_GOVERNANCE.md` |
| GET | `/health` | backend health |
| GET | `/robots.txt` | robots |
| GET | `/metrics` | Prometheus metrics |

## References

- [AUTH_FLOW.md](AUTH_FLOW.md)
- [F03_DIAGNOSTIC_INITIAL.md](F03_DIAGNOSTIC_INITIAL.md)
- [../00-REFERENCE/ARCHITECTURE.md](../00-REFERENCE/ARCHITECTURE.md)
- [../03-PROJECT/POINTS_RESTANTS_2026-03-15.md](../03-PROJECT/POINTS_RESTANTS_2026-03-15.md)

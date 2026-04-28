# API QUICK REFERENCE - MATHAKINE

> Condensed reference of active endpoints
> Updated: 09/04/2026
> Runtime source of truth: `server/routes/`

## Reading Rules

- this document summarizes active Starlette routes only
- final truth remains `server/routes/` + `server/handlers/`
- AI model defaults / allowlists / runtime observability are documented in `docs/00-REFERENCE/AI_MODEL_GOVERNANCE.md`
- `app/api/endpoints/*` has been archived in `_ARCHIVE_2026/app/api/` and is not part of the runtime
- auth-sensitive and chat endpoints rely on distributed Redis rate limiting in production; client IP for keys follows `RATE_LIMIT_TRUST_X_FORWARDED_FOR`
- frontend Next proxies (`frontend/app/api/*`) are documented separately in `docs/04-FRONTEND/API_ROUTES.md`

## Auth

| Method | Endpoint                        | Notes                                                                                                                                 |
| ------ | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| POST   | `/api/auth/login`               | login + auth cookies, rate limited                                                                                                    |
| GET    | `/api/auth/csrf`                | fetches CSRF token                                                                                                                    |
| POST   | `/api/auth/validate-token`      | token validation; dedicated rate limit (90/min/IP); Next server uses shared runtime + short success dedup (`validateTokenRuntime.ts`) |
| POST   | `/api/auth/refresh`             | refresh via cookie/body                                                                                                               |
| POST   | `/api/auth/logout`              | clears auth cookies                                                                                                                   |
| POST   | `/api/auth/forgot-password`     | generic message, rate limited                                                                                                         |
| POST   | `/api/auth/reset-password`      | revokes older tokens and sessions                                                                                                     |
| GET    | `/api/auth/verify-email`        | email verification                                                                                                                    |
| POST   | `/api/auth/resend-verification` | generic message, rate limited                                                                                                         |

## Users

| Method | Endpoint                                     | Notes                                                                                                                             |
| ------ | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ---- | ----------------------------- |
| POST   | `/api/users/`                                | registration, rate limited                                                                                                        |
| GET    | `/api/users/`                                | placeholder / in development                                                                                                      |
| GET    | `/api/users/me`                              | current user (+ `gamification_level`, `total_points`, `current_level`, `progression_rank`, legacy alias `jedi_rank`, `age_group`) |
| PUT    | `/api/users/me`                              | profile update                                                                                                                    |
| PUT    | `/api/users/me/password`                     | password change + revocation                                                                                                      |
| DELETE | `/api/users/me`                              | delete current account                                                                                                            |
| GET    | `/api/users/me/export`                       | GDPR export                                                                                                                       |
| GET    | `/api/users/me/sessions`                     | active sessions                                                                                                                   |
| DELETE | `/api/users/me/sessions/{session_id}`        | revoke session                                                                                                                    |
| GET    | `/api/users/me/rank`                         | rank by points; `period=all                                                                                                       | week | month`; auth + full access    |
| GET    | `/api/users/me/progress/timeline`            | progression timeline (exercises + challenges)                                                                                     |
| GET    | `/api/users/me/progress`                     | global progression                                                                                                                |
| GET    | `/api/users/me/challenges/progress`          | challenge progress aggregate                                                                                                      |
| GET    | `/api/users/me/challenges/detailed-progress` | mastery by challenge type                                                                                                         |
| GET    | `/api/users/stats`                           | user stats; includes spaced repetition summary block                                                                              |
| GET    | `/api/users/me/reviews/next`                 | next due spaced-repetition review; exercise payload is review-safe (no `correct_answer` / `explanation` / `hint`)                 |
| GET    | `/api/users/leaderboard`                     | leaderboard; `period=all                                                                                                          | week | month`; respects privacy flag |
| DELETE | `/api/users/{user_id}`                       | active route; self-delete redirected to `/api/users/me` semantics                                                                 |

## Daily Challenge

| Method | Endpoint                | Notes                           |
| ------ | ----------------------- | ------------------------------- |
| GET    | `/api/daily-challenges` | 3 daily challenges for the user |

## Diagnostic

| Method | Endpoint                   | Notes                                                                     |
| ------ | -------------------------- | ------------------------------------------------------------------------- |
| GET    | `/api/diagnostic/status`   | latest score / state                                                      |
| POST   | `/api/diagnostic/start`    | starts a session, returns `state_token`                                   |
| POST   | `/api/diagnostic/question` | body uses `state_token`, returns next signed token                        |
| POST   | `/api/diagnostic/answer`   | body uses `state_token` + `user_answer`; no client `correct_answer` trust |
| POST   | `/api/diagnostic/complete` | body uses `state_token`, persists final result                            |

Contract note:

- `/api/diagnostic/question` does not expose `correct_answer`
- `/api/diagnostic/answer` may return `correct_answer` only after submission for feedback

## Exercises

| Method | Endpoint                               | Notes                                                                                                                                                                |
| ------ | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/api/exercises`                       | list / filters / hide_completed                                                                                                                                      |
| GET    | `/api/exercises/stats`                 | home + admin academy stats                                                                                                                                           |
| GET    | `/api/exercises/interleaved-plan`      | interleaved plan                                                                                                                                                     |
| GET    | `/api/exercises/{exercise_id}`         | exercise detail                                                                                                                                                      |
| POST   | `/api/exercises/generate`              | active generation route                                                                                                                                              |
| POST   | `/api/exercises/generate-ai-stream`    | AI generation SSE ; events `status`, `exercise`, `error`, `done` ; frontend distinguishes `401`, `403`, missing CSRF and generic backend errors before toast display |
| GET    | `/api/exercises/completed-ids`         | completed ids                                                                                                                                                        |
| POST   | `/api/exercises/{exercise_id}/attempt` | submit answer                                                                                                                                                        |

Exercise attempt - answer matching:

- exact trim match first
- equivalent forms accepted for `%`, decimal comma/dot, and simple fraction/decimal parity when relevant
- implementation: `app/utils/exercise_answer_compare.py`

## Challenges

| Method | Endpoint                                 | Notes                                                                                                                                                                            |
| ------ | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/api/challenges`                        | list / filters / hide_completed                                                                                                                                                  |
| GET    | `/api/challenges/stats`                  | active-catalog aggregates ; auth + full access                                                                                                                                   |
| GET    | `/api/challenges/{challenge_id}`         | challenge detail (`response_mode`, filtered `choices`)                                                                                                                           |
| POST   | `/api/challenges/{challenge_id}/attempt` | typed response with `is_correct`, `explanation`, `new_badges`, `progress_notification`, `hints_remaining`, `points_earned` when applicable                                       |
| GET    | `/api/challenges/{challenge_id}/hint`    | hint                                                                                                                                                                             |
| GET    | `/api/challenges/completed-ids`          | completed ids                                                                                                                                                                    |
| POST   | `/api/challenges/generate-ai-stream`     | AI generation SSE ; events `status`, `warning`, `challenge`, `error`, `done` ; frontend distinguishes `401`, `403`, missing CSRF and generic backend errors before toast display |
| GET    | `/api/challenges/badges/progress`        | challenge badge progress                                                                                                                                                         |

## Badges

| Method | Endpoint                          | Notes                                                                                     |
| ------ | --------------------------------- | ----------------------------------------------------------------------------------------- |
| GET    | `/api/badges/user`                | user badges ; `earned_badges[]` exposes `thematic_title` + legacy alias `star_wars_title` |
| GET    | `/api/badges/available`           | public badges, `?limit=N` (default 100, max 200)                                          |
| POST   | `/api/badges/check`               | badge check                                                                               |
| GET    | `/api/badges/stats`               | gamification stats                                                                        |
| GET    | `/api/badges/rarity`              | rarity stats                                                                              |
| PATCH  | `/api/badges/pin`                 | pin `badge_ids`                                                                           |
| GET    | `/api/challenges/badges/progress` | challenge badge progress                                                                  |

## Gamification (points ledger)

Persistence is server-only:

- PostgreSQL table `point_events`
- writes only through `GamificationService.apply_points`
- no public endpoint lists ledger rows or exposes a generic `apply_points`

Client-visible surfaces:

- `GET /api/users/me`
- `GET /api/badges/stats`
- `POST /api/challenges/{id}/attempt` via `points_earned`

Long reference: `docs/02-FEATURES/GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md`

## Admin

| Method | Endpoint                                           | Notes                                                                                                                                                        |
| ------ | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GET    | `/api/admin/health`                                | admin health                                                                                                                                                 |
| GET    | `/api/admin/overview`                              | overview                                                                                                                                                     |
| GET    | `/api/admin/observability/f43-account-progression` | read-only account progression distribution                                                                                                                   |
| GET    | `/api/admin/users`                                 | user list                                                                                                                                                    |
| PATCH  | `/api/admin/users/{user_id}`                       | mutate user                                                                                                                                                  |
| POST   | `/api/admin/users/{user_id}/send-reset-password`   | send reset                                                                                                                                                   |
| POST   | `/api/admin/users/{user_id}/resend-verification`   | resend verification                                                                                                                                          |
| DELETE | `/api/admin/users/{user_id}`                       | admin delete                                                                                                                                                 |
| GET    | `/api/admin/exercises`                             | exercise list                                                                                                                                                |
| POST   | `/api/admin/exercises`                             | create exercise                                                                                                                                              |
| POST   | `/api/admin/exercises/{exercise_id}/duplicate`     | duplicate exercise                                                                                                                                           |
| GET    | `/api/admin/exercises/{exercise_id}`               | exercise detail                                                                                                                                              |
| PUT    | `/api/admin/exercises/{exercise_id}`               | full update                                                                                                                                                  |
| PATCH  | `/api/admin/exercises/{exercise_id}`               | partial update                                                                                                                                               |
| GET    | `/api/admin/challenges`                            | challenge list                                                                                                                                               |
| POST   | `/api/admin/challenges`                            | create challenge                                                                                                                                             |
| POST   | `/api/admin/challenges/{challenge_id}/duplicate`   | duplicate challenge                                                                                                                                          |
| GET    | `/api/admin/challenges/{challenge_id}`             | challenge detail                                                                                                                                             |
| PUT    | `/api/admin/challenges/{challenge_id}`             | full update                                                                                                                                                  |
| PATCH  | `/api/admin/challenges/{challenge_id}`             | partial update                                                                                                                                               |
| GET    | `/api/admin/reports`                               | reports                                                                                                                                                      |
| GET    | `/api/admin/feedback`                              | admin feedback                                                                                                                                               |
| GET    | `/api/admin/audit-log`                             | audit log                                                                                                                                                    |
| GET    | `/api/admin/moderation`                            | moderation                                                                                                                                                   |
| GET    | `/api/admin/config`                                | config read                                                                                                                                                  |
| PUT    | `/api/admin/config`                                | config write                                                                                                                                                 |
| GET    | `/api/admin/export`                                | CSV export                                                                                                                                                   |
| GET    | `/api/admin/badges`                                | badge list                                                                                                                                                   |
| POST   | `/api/admin/badges`                                | create badge                                                                                                                                                 |
| GET    | `/api/admin/badges/{badge_id}`                     | badge detail                                                                                                                                                 |
| PUT    | `/api/admin/badges/{badge_id}`                     | badge update                                                                                                                                                 |
| DELETE | `/api/admin/badges/{badge_id}`                     | soft delete badge                                                                                                                                            |
| GET    | `/api/admin/analytics/edtech`                      | EdTech analytics                                                                                                                                             |
| GET    | `/api/admin/ai-stats`                              | AI runtime stats : costs are **estimates**, tokens, workload split (`assistant_chat`, `exercises_ai`, `challenges_ai`) ; in-memory retention remains bounded |
| GET    | `/api/admin/generation-metrics`                    | runtime quality metrics, including `assistant_chat` ; unknown keys go to bucket `unknown`                                                                    |
| GET    | `/api/admin/ai-eval-harness-runs?limit=N`          | latest persisted harness runs ; separate from in-memory runtime stats                                                                                        |

## Misc

| Method | Endpoint                        | Notes                                                                                                                                |
| ------ | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| POST   | `/api/analytics/event`          | app analytics                                                                                                                        |
| POST   | `/api/feedback`                 | create feedback                                                                                                                      |
| GET    | `/api/recommendations`          | recommendations                                                                                                                      |
| POST   | `/api/recommendations/generate` | generate recommendations                                                                                                             |
| POST   | `/api/recommendations/open`     | mark recommendation opened                                                                                                           |
| POST   | `/api/recommendations/clicked`  | mark recommendation clicked (alias stable de /open)                                                                                  |
| POST   | `/api/recommendations/complete` | mark recommendation complete                                                                                                         |
| POST   | `/api/chat`                     | authenticated chat ; requires a valid session ; Next proxy also gates `access_token` before forwarding                               |
| POST   | `/api/chat/stream`              | authenticated chat SSE ; requires a valid session ; Next proxy tests cover auth, invalid backend config, and empty-body SSE fallback |
| GET    | `/live`                         | liveness (process only)                                                                                                              |
| GET    | `/ready`                        | readiness (DB + Redis in prod when `REDIS_URL` set) ; Render `healthCheckPath`                                                       |
| GET    | `/health`                       | alias of `/ready` (readiness)                                                                                                        |
| GET    | `/robots.txt`                   | robots                                                                                                                               |
| GET    | `/metrics`                      | Prometheus metrics                                                                                                                   |

## References

- [AUTH_FLOW.md](AUTH_FLOW.md)
- [F03_DIAGNOSTIC_INITIAL.md](F03_DIAGNOSTIC_INITIAL.md)
- [../00-REFERENCE/ARCHITECTURE.md](../00-REFERENCE/ARCHITECTURE.md)
- [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md)

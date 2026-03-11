# API Quick Reference â€” Mathakine

> RÃ©fÃ©rence condensÃ©e des endpoints â€” Frontend/Backend  
> **Date :** 11/03/2026 (MAJ iterations backend exercise/auth/user et challenge/admin/badge, release 3.1.0-alpha.8)  
> **DÃ©tails :** [ENDPOINTS_NON_INTEGRES](../03-PROJECT/ENDPOINTS_NON_INTEGRES.md), [PLACEHOLDERS_ET_TODO](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/PLACEHOLDERS_ET_TODO.md)

---

## Vue d'ensemble

| Domaine | Routes | Auth requise |
|---------|--------|--------------|
| Auth | 10 | Variable |
| Users | 15 | Sauf register |
| **Daily Challenges** (F02) | **1** | **Oui** |
| **Diagnostic** (F03) | **5** | **Oui** |
| **Admin** | **34** | **Archiviste** |
| Exercises | 10 | Variable |
| Challenges | 10 | Variable |
| Badges | 7 | Variable |
| Recommendations | 3 | Oui |
| Analytics | 1 | Oui |
| Feedback | 1 | Oui |
| Chat | 2 | Non (whitelist) |

---

## Auth

| MÃ©thode | Endpoint | Auth | Body | Statut |
|---------|----------|------|------|--------|
| POST | `/api/auth/login` | Non | `{username, password}` | OK |
| â€” | Inscription | â€” | `POST /api/users/` avec `{username, email, password}` | OK |
| GET | `/api/auth/verify-email` | Non | `?token=` | OK |
| POST | `/api/auth/resend-verification` | Non | `{email}` | OK - message generique sur email inconnu ou mal forme |
| POST | `/api/auth/forgot-password` | Non | `{email}` | OK - message generique (email existant ou non) |
| POST | `/api/auth/reset-password` | Non | `{token, password, password_confirm}` | OK - revoque anciens access/refresh tokens et sessions |
| POST | `/api/auth/logout` | Cookie | â€” | OK |
| POST | `/api/auth/refresh` | Cookie | â€” | OK |
| POST | `/api/auth/validate-token` | Non | `{token}` | OK â€” validation signature/expiration (sync-cookie) |
| GET | `/api/auth/csrf` | Non | â€” | OK |

---

## Users

| MÃ©thode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| POST | `/api/users/` | Non | `{username, email, password}` | OK |
| GET | `/api/users/me` | Oui | â€” | OK |
| PUT | `/api/users/me` | Oui | `{username, full_name, ...}` | OK |
| PUT | `/api/users/me/password` | Oui | `{current_password, new_password}` | OK - aligne sur la revocation auth (`password_changed_at`) |
| DELETE | `/api/users/me` | Oui | â€” | OK |
| GET | `/api/users/me/progress` | Oui | â€” | OK |
| GET | `/api/users/me/progress/timeline` | Oui | `?period=7d\|30d` | OK â€” F07 : `{period, from, to, points[], summary}` |
| GET | `/api/users/me/challenges/progress` | Oui | â€” | OK |
| GET | `/api/users/me/sessions` | Oui | â€” | OK |
| DELETE | `/api/users/me/sessions/{id}` | Oui | â€” | OK |
| GET | `/api/users/me/export` | Oui | â€” | OK |
| GET | `/api/users/stats` | Oui | `?timeRange=7|30|90|all` | OK |
| GET | `/api/users/leaderboard` | Oui | `?limit=50` | OK |
| GET | `/api/users/` | Admin | â€” | Placeholder |
| DELETE | `/api/users/{id}` | Admin | â€” | Placeholder |

---

## Daily Challenges (F02)

| MÃ©thode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/daily-challenges` | Oui (full_access) | â€” | OK â€” Retourne `{challenges: [...]}`, 3 dÃ©fis par jour (volume, specific, logic) |

**ConsommÃ© par :** `useDailyChallenges`, `DailyChallengesWidget`

**RÃ©fÃ©rence :** [F02_DEFIS_QUOTIDIENS.md](F02_DEFIS_QUOTIDIENS.md)

---

## Diagnostic (F03 â€” Test IRT)

| MÃ©thode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/diagnostic/status` | Oui | â€” | OK â€” `{has_completed, latest: {scores, completed_at, ...}}` |
| POST | `/api/diagnostic/start` | Oui | `{triggered_from?: "onboarding"\|"settings"}` | OK |
| POST | `/api/diagnostic/question` | Oui | `{session}` | OK |
| POST | `/api/diagnostic/answer` | Oui | `{session, exercise_type, user_answer, correct_answer}` | OK |
| POST | `/api/diagnostic/complete` | Oui | `{session, duration_seconds?}` | OK |

**ConsommÃ© par :** `useIrtScores`, `LevelEstablishedWidget`, Settings (section Ã‰valuation de niveau)

---

## Exercises

| MÃ©thode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/exercises` | Optionnel | `?skip=&limit=&exercise_type=&age_group=&search=&order=random\|recent&hide_completed=true\|false` | OK â€” Ordre alÃ©atoire par dÃ©faut, `hide_completed` exclut les rÃ©ussis (auth optionnelle) |
| GET | `/api/exercises/stats` | Non | â€” | OK (widget accueil) |
| GET | `/api/exercises/interleaved-plan` | Oui | `?length=10` | OK â€” F32 : plan de session entrelacÃ©e (`409 code=not_enough_variety` si variÃ©tÃ© insuffisante) |
| GET | `/api/exercises/{id}` | Non | â€” | OK |
| POST | `/api/exercises/{id}/attempt` | Oui | `{answer|selected_answer, time_spent?}` | OK |
| GET | `/api/exercises/completed-ids` | Non | â€” | OK â€” whitelist |
| ~~GET~~ | ~~`/api/exercises/generate`~~ | â€” | â€” | SupprimÃ© (audit H2, 01/03/2026) |
| POST | `/api/exercises/generate` | Optionnel | `{exercise_type, age_group?, adaptive?, save?, ai?}` | OK â€” `adaptive=true` + utilisateur auth : rÃ©sout `age_group` automatiquement (F05/F32). Si `save=true`, renvoie un exercice persistÃ© avec `id` ou une erreur `500` |
| GET | `/api/exercises/generate-ai-stream` | Non | â€” | OK (SSE) |
| ~~DELETE~~ | ~~`/api/exercises/{id}`~~ | â€” | â€” | SupprimÃ© â€” archivage prÃ©vu dans lâ€™admin |

---

## Challenges

| MÃ©thode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/challenges` | Oui | `?skip=&limit=&challenge_type=&age_group=&search=&order=random\|recent&hide_completed=true\|false` | OK â€” Ordre alÃ©atoire par dÃ©faut, `hide_completed` exclut les dÃ©fis dÃ©jÃ  rÃ©ussis |
| GET | `/api/challenges/{id}` | Oui | â€” | OK |
| POST | `/api/challenges/{id}/attempt` | Oui | `{answer}` | OK â€” RÃ©ponse inclut `new_badges` si dÃ©blocage (Lot C-1) |
| GET | `/api/challenges/{id}/hint` | Oui | â€” | OK |
| GET | `/api/challenges/completed-ids` | Non | â€” | OK â€” whitelist |
| GET | `/api/challenges/generate-ai-stream` | Non | â€” | OK (SSE) |
| GET | `/api/challenges/badges/progress` | Oui | â€” | OK |
| POST | `/api/challenges/start/{id}` | Oui | â€” | Placeholder (optionnel) |

---

## Badges

| MÃ©thode | Endpoint | Auth | Statut |
|---------|----------|------|--------|
| GET | `/api/badges/user` | Oui | OK |
| GET | `/api/badges/available` | Non | OK â€” whitelist |
| GET | `/api/badges/rarity` | Non | OK â€” stats raretÃ© (cache 90s) |
| POST | `/api/badges/check` | Oui | OK |
| GET | `/api/badges/stats` | Oui | OK |
| PATCH | `/api/badges/pin` | Oui | OK â€” `{badge_ids: [1,2,3]}` |

---

## Admin (rÃ´le archiviste)

| MÃ©thode | Endpoint | Auth | Params / Body | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/admin/health` | Archiviste | â€” | OK |
| GET | `/api/admin/overview` | Archiviste | â€” | OK |
| GET | `/api/admin/users` | Archiviste | `?search=&role=&is_active=&skip=&limit=` | OK |
| PATCH | `/api/admin/users/{id}` | Archiviste | `{is_active?, role?}` | OK |
| POST | `/api/admin/users/{id}/send-reset-password` | Archiviste | â€” | OK |
| POST | `/api/admin/users/{id}/resend-verification` | Archiviste | â€” | OK |
| GET | `/api/admin/exercises` | Archiviste | `?archived=&type=&search=&skip=&limit=` | OK |
| POST | `/api/admin/exercises` | Archiviste | `{title, exercise_type, ...}` | OK |
| GET | `/api/admin/exercises/{id}` | Archiviste | â€” | OK |
| PUT | `/api/admin/exercises/{id}` | Archiviste | body complet | OK |
| PATCH | `/api/admin/exercises/{id}` | Archiviste | `{is_archived: bool}` | OK |
| POST | `/api/admin/exercises/{id}/duplicate` | Archiviste | â€” | OK |
| GET | `/api/admin/challenges` | Archiviste | `?archived=&type=&search=&skip=&limit=` | OK |
| POST | `/api/admin/challenges` | Archiviste | `{title, challenge_type, ...}` | OK |
| GET | `/api/admin/challenges/{id}` | Archiviste | â€” | OK |
| PUT | `/api/admin/challenges/{id}` | Archiviste | body complet | OK |
| PATCH | `/api/admin/challenges/{id}` | Archiviste | `{is_archived: bool}` | OK |
| POST | `/api/admin/challenges/{id}/duplicate` | Archiviste | â€” | OK |
| GET | `/api/admin/badges` | Archiviste | â€” | OK |
| POST | `/api/admin/badges` | Archiviste | `{code, name, description, category, difficulty, points_reward, requirements, ...}` | OK |
| GET | `/api/admin/badges/{id}` | Archiviste | â€” | OK |
| PUT | `/api/admin/badges/{id}` | Archiviste | body complet | OK |
| DELETE | `/api/admin/badges/{id}` | Archiviste | â€” | Soft delete (is_active=false) |
| GET | `/api/admin/reports` | Archiviste | `?period=7d|30d` | OK |
| GET | `/api/admin/moderation` | Archiviste | `?type=exercises|challenges` | OK |
| GET | `/api/admin/feedback` | Archiviste | â€” | OK |
| GET | `/api/admin/audit-log` | Archiviste | `?skip=&limit=` | OK |
| GET | `/api/admin/config` | Archiviste | â€” | OK |
| PUT | `/api/admin/config` | Archiviste | `{settings: {key: value}}` | OK |
| GET | `/api/admin/export` | Archiviste | `?type=&period=` | OK |
| GET | `/api/admin/analytics/edtech` | Archiviste | `?period=7d|30d&event=` | OK â€” CTR Quick Start, first_attempt, by_type (exercise\|challenge\|interleaved) |
| GET | `/api/admin/ai-stats` | Archiviste | â€” | OK |
| GET | `/api/admin/generation-metrics` | Archiviste | â€” | OK |

Pages : `/admin`, `/admin/users`, `/admin/content`, `/admin/moderation`, `/admin/audit-log`, `/admin/config`, `/admin/analytics`.

---

## Analytics EdTech

| MÃ©thode | Endpoint | Auth | Body | Statut |
|---------|----------|------|------|--------|
| POST | `/api/analytics/event` | Oui | `{event, payload}` | OK â€” quick_start_click, first_attempt |

## Feedback

| MÃ©thode | Endpoint | Auth | Body | Statut |
|---------|----------|------|------|--------|
| POST | `/api/feedback` | Oui | `{feedback_type, description, page_url, ...}` | OK |

## Recommendations & Chat

| MÃ©thode | Endpoint | Auth | Statut |
|---------|----------|------|--------|
| GET | `/api/recommendations` | Oui | OK |
| POST | `/api/recommendations/generate` | Oui | OK |
| POST | `/api/recommendations/complete` | Oui | OK |
| POST | `/api/chat` | Non | OK â€” whitelist (page d'accueil publique) |
| POST | `/api/chat/stream` | Non | OK (SSE) â€” whitelist |

---

## Utilitaires

| MÃ©thode | Endpoint | Auth | RÃ´le |
|---------|----------|------|------|
| GET | `/health` | Non | Health check |
| GET | `/metrics` | Non | Prometheus |

---

## Auth : Cookie vs Bearer

- **Cookie** : `access_token` (HttpOnly) â€” utilisÃ© par le frontend Next.js
- **Bearer** : `Authorization: Bearer <token>` â€” pour tests / clients API

â†’ Voir [AUTH_FLOW.md](AUTH_FLOW.md) pour le flux complet.


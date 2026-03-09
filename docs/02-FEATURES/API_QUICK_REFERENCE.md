# API Quick Reference — Mathakine

> Référence condensée des endpoints — Frontend/Backend  
> **Date :** 09/03/2026 (MAJ iteration backend exercise/auth/user, auth recovery/session, export RGPD)  
> **Détails :** [ENDPOINTS_NON_INTEGRES](../03-PROJECT/ENDPOINTS_NON_INTEGRES.md), [PLACEHOLDERS_ET_TODO](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/PLACEHOLDERS_ET_TODO.md)

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

| Méthode | Endpoint | Auth | Body | Statut |
|---------|----------|------|------|--------|
| POST | `/api/auth/login` | Non | `{username, password}` | OK |
| — | Inscription | — | `POST /api/users/` avec `{username, email, password}` | OK |
| GET | `/api/auth/verify-email` | Non | `?token=` | OK |
| POST | `/api/auth/resend-verification` | Non | `{email}` | OK - message generique sur email inconnu ou mal forme |
| POST | `/api/auth/forgot-password` | Non | `{email}` | OK - message generique (email existant ou non) |
| POST | `/api/auth/reset-password` | Non | `{token, password, password_confirm}` | OK - revoque anciens access/refresh tokens et sessions |
| POST | `/api/auth/logout` | Cookie | — | OK |
| POST | `/api/auth/refresh` | Cookie | — | OK |
| POST | `/api/auth/validate-token` | Non | `{token}` | OK — validation signature/expiration (sync-cookie) |
| GET | `/api/auth/csrf` | Non | — | OK |

---

## Users

| Méthode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| POST | `/api/users/` | Non | `{username, email, password}` | OK |
| GET | `/api/users/me` | Oui | — | OK |
| PUT | `/api/users/me` | Oui | `{username, full_name, ...}` | OK |
| PUT | `/api/users/me/password` | Oui | `{current_password, new_password}` | OK - aligne sur la revocation auth (`password_changed_at`) |
| DELETE | `/api/users/me` | Oui | — | OK |
| GET | `/api/users/me/progress` | Oui | — | OK |
| GET | `/api/users/me/progress/timeline` | Oui | `?period=7d\|30d` | OK — F07 : `{period, from, to, points[], summary}` |
| GET | `/api/users/me/challenges/progress` | Oui | — | OK |
| GET | `/api/users/me/sessions` | Oui | — | OK |
| DELETE | `/api/users/me/sessions/{id}` | Oui | — | OK |
| GET | `/api/users/me/export` | Oui | — | OK |
| GET | `/api/users/stats` | Oui | `?timeRange=7|30|90|all` | OK |
| GET | `/api/users/leaderboard` | Oui | `?limit=50` | OK |
| GET | `/api/users/` | Admin | — | Placeholder |
| DELETE | `/api/users/{id}` | Admin | — | Placeholder |

---

## Daily Challenges (F02)

| Méthode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/daily-challenges` | Oui (full_access) | — | OK — Retourne `{challenges: [...]}`, 3 défis par jour (volume, specific, logic) |

**Consommé par :** `useDailyChallenges`, `DailyChallengesWidget`

**Référence :** [F02_DEFIS_QUOTIDIENS.md](F02_DEFIS_QUOTIDIENS.md)

---

## Diagnostic (F03 — Test IRT)

| Méthode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/diagnostic/status` | Oui | — | OK — `{has_completed, latest: {scores, completed_at, ...}}` |
| POST | `/api/diagnostic/start` | Oui | `{triggered_from?: "onboarding"\|"settings"}` | OK |
| POST | `/api/diagnostic/question` | Oui | `{session}` | OK |
| POST | `/api/diagnostic/answer` | Oui | `{session, exercise_type, user_answer, correct_answer}` | OK |
| POST | `/api/diagnostic/complete` | Oui | `{session, duration_seconds?}` | OK |

**Consommé par :** `useIrtScores`, `LevelEstablishedWidget`, Settings (section Évaluation de niveau)

---

## Exercises

| Méthode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/exercises` | Optionnel | `?skip=&limit=&exercise_type=&age_group=&search=&order=random\|recent&hide_completed=true\|false` | OK — Ordre aléatoire par défaut, `hide_completed` exclut les réussis (auth optionnelle) |
| GET | `/api/exercises/stats` | Non | — | OK (widget accueil) |
| GET | `/api/exercises/interleaved-plan` | Oui | `?length=10` | OK — F32 : plan de session entrelacée (`409 code=not_enough_variety` si variété insuffisante) |
| GET | `/api/exercises/{id}` | Non | — | OK |
| POST | `/api/exercises/{id}/attempt` | Oui | `{answer|selected_answer, time_spent?}` | OK |
| GET | `/api/exercises/completed-ids` | Non | — | OK — whitelist |
| ~~GET~~ | ~~`/api/exercises/generate`~~ | — | — | Supprimé (audit H2, 01/03/2026) |
| POST | `/api/exercises/generate` | Optionnel | `{exercise_type, age_group?, adaptive?, save?, ai?}` | OK — `adaptive=true` + utilisateur auth : résout `age_group` automatiquement (F05/F32). Si `save=true`, renvoie un exercice persisté avec `id` ou une erreur `500` |
| GET | `/api/exercises/generate-ai-stream` | Non | — | OK (SSE) |
| ~~DELETE~~ | ~~`/api/exercises/{id}`~~ | — | — | Supprimé — archivage prévu dans l’admin |

---

## Challenges

| Méthode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/challenges` | Oui | `?skip=&limit=&challenge_type=&age_group=&search=&order=random\|recent&hide_completed=true\|false` | OK — Ordre aléatoire par défaut, `hide_completed` exclut les défis déjà réussis |
| GET | `/api/challenges/{id}` | Oui | — | OK |
| POST | `/api/challenges/{id}/attempt` | Oui | `{answer}` | OK — Réponse inclut `new_badges` si déblocage (Lot C-1) |
| GET | `/api/challenges/{id}/hint` | Oui | — | OK |
| GET | `/api/challenges/completed-ids` | Non | — | OK — whitelist |
| GET | `/api/challenges/generate-ai-stream` | Non | — | OK (SSE) |
| GET | `/api/challenges/badges/progress` | Oui | — | OK |
| POST | `/api/challenges/start/{id}` | Oui | — | Placeholder (optionnel) |

---

## Badges

| Méthode | Endpoint | Auth | Statut |
|---------|----------|------|--------|
| GET | `/api/badges/user` | Oui | OK |
| GET | `/api/badges/available` | Non | OK — whitelist |
| GET | `/api/badges/rarity` | Non | OK — stats rareté (cache 90s) |
| POST | `/api/badges/check` | Oui | OK |
| GET | `/api/badges/stats` | Oui | OK |
| PATCH | `/api/badges/pin` | Oui | OK — `{badge_ids: [1,2,3]}` |

---

## Admin (rôle archiviste)

| Méthode | Endpoint | Auth | Params / Body | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/admin/health` | Archiviste | — | OK |
| GET | `/api/admin/overview` | Archiviste | — | OK |
| GET | `/api/admin/users` | Archiviste | `?search=&role=&is_active=&skip=&limit=` | OK |
| PATCH | `/api/admin/users/{id}` | Archiviste | `{is_active?, role?}` | OK |
| POST | `/api/admin/users/{id}/send-reset-password` | Archiviste | — | OK |
| POST | `/api/admin/users/{id}/resend-verification` | Archiviste | — | OK |
| GET | `/api/admin/exercises` | Archiviste | `?archived=&type=&search=&skip=&limit=` | OK |
| POST | `/api/admin/exercises` | Archiviste | `{title, exercise_type, ...}` | OK |
| GET | `/api/admin/exercises/{id}` | Archiviste | — | OK |
| PUT | `/api/admin/exercises/{id}` | Archiviste | body complet | OK |
| PATCH | `/api/admin/exercises/{id}` | Archiviste | `{is_archived: bool}` | OK |
| POST | `/api/admin/exercises/{id}/duplicate` | Archiviste | — | OK |
| GET | `/api/admin/challenges` | Archiviste | `?archived=&type=&search=&skip=&limit=` | OK |
| POST | `/api/admin/challenges` | Archiviste | `{title, challenge_type, ...}` | OK |
| GET | `/api/admin/challenges/{id}` | Archiviste | — | OK |
| PUT | `/api/admin/challenges/{id}` | Archiviste | body complet | OK |
| PATCH | `/api/admin/challenges/{id}` | Archiviste | `{is_archived: bool}` | OK |
| POST | `/api/admin/challenges/{id}/duplicate` | Archiviste | — | OK |
| GET | `/api/admin/badges` | Archiviste | — | OK |
| POST | `/api/admin/badges` | Archiviste | `{code, name, description, category, difficulty, points_reward, requirements, ...}` | OK |
| GET | `/api/admin/badges/{id}` | Archiviste | — | OK |
| PUT | `/api/admin/badges/{id}` | Archiviste | body complet | OK |
| DELETE | `/api/admin/badges/{id}` | Archiviste | — | Soft delete (is_active=false) |
| GET | `/api/admin/reports` | Archiviste | `?period=7d|30d` | OK |
| GET | `/api/admin/moderation` | Archiviste | `?type=exercises|challenges` | OK |
| GET | `/api/admin/feedback` | Archiviste | — | OK |
| GET | `/api/admin/audit-log` | Archiviste | `?skip=&limit=` | OK |
| GET | `/api/admin/config` | Archiviste | — | OK |
| PUT | `/api/admin/config` | Archiviste | `{settings: {key: value}}` | OK |
| GET | `/api/admin/export` | Archiviste | `?type=&period=` | OK |
| GET | `/api/admin/analytics/edtech` | Archiviste | `?period=7d|30d&event=` | OK — CTR Quick Start, first_attempt, by_type (exercise\|challenge\|interleaved) |
| GET | `/api/admin/ai-stats` | Archiviste | — | OK |
| GET | `/api/admin/generation-metrics` | Archiviste | — | OK |

Pages : `/admin`, `/admin/users`, `/admin/content`, `/admin/moderation`, `/admin/audit-log`, `/admin/config`, `/admin/analytics`.

---

## Analytics EdTech

| Méthode | Endpoint | Auth | Body | Statut |
|---------|----------|------|------|--------|
| POST | `/api/analytics/event` | Oui | `{event, payload}` | OK — quick_start_click, first_attempt |

## Feedback

| Méthode | Endpoint | Auth | Body | Statut |
|---------|----------|------|------|--------|
| POST | `/api/feedback` | Oui | `{feedback_type, description, page_url, ...}` | OK |

## Recommendations & Chat

| Méthode | Endpoint | Auth | Statut |
|---------|----------|------|--------|
| GET | `/api/recommendations` | Oui | OK |
| POST | `/api/recommendations/generate` | Oui | OK |
| POST | `/api/recommendations/complete` | Oui | OK |
| POST | `/api/chat` | Non | OK — whitelist (page d'accueil publique) |
| POST | `/api/chat/stream` | Non | OK (SSE) — whitelist |

---

## Utilitaires

| Méthode | Endpoint | Auth | Rôle |
|---------|----------|------|------|
| GET | `/health` | Non | Health check |
| GET | `/metrics` | Non | Prometheus |

---

## Auth : Cookie vs Bearer

- **Cookie** : `access_token` (HttpOnly) — utilisé par le frontend Next.js
- **Bearer** : `Authorization: Bearer <token>` — pour tests / clients API

→ Voir [AUTH_FLOW.md](AUTH_FLOW.md) pour le flux complet.

# API Quick Reference — Mathakine

> Référence condensée des endpoints — Frontend/Backend  
> **Date :** 16/02/2026  
> **Détails :** [ENDPOINTS_NON_INTEGRES](../03-PROJECT/ENDPOINTS_NON_INTEGRES.md), [PLACEHOLDERS_ET_TODO](../03-PROJECT/PLACEHOLDERS_ET_TODO.md)

---

## Vue d'ensemble

| Domaine | Routes | Auth requise |
|---------|--------|--------------|
| Auth | 9 | Variable |
| Users | 14 | Sauf register |
| **Admin** | **25** | **Archiviste** |
| Exercises | 9 | Variable |
| Challenges | 10 | Variable |
| Badges | 5 | Oui |
| Recommendations | 3 | Oui |
| Chat | 2 | Oui |

---

## Auth

| Méthode | Endpoint | Auth | Body | Statut |
|---------|----------|------|------|--------|
| POST | `/api/auth/login` | Non | `{username, password}` | OK |
| — | Inscription | — | `POST /api/users/` avec `{username, email, password}` | OK |
| GET | `/api/auth/verify-email` | Non | `?token=` | OK |
| POST | `/api/auth/resend-verification` | Non | `{email}` | OK |
| POST | `/api/auth/forgot-password` | Non | `{email}` | OK |
| POST | `/api/auth/reset-password` | Non | `{token, new_password}` | OK |
| POST | `/api/auth/logout` | Cookie | — | OK |
| POST | `/api/auth/refresh` | Cookie | — | OK |
| GET | `/api/auth/csrf` | Non | — | OK |

---

## Users

| Méthode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| POST | `/api/users/` | Non | `{username, email, password}` | OK |
| GET | `/api/users/me` | Oui | — | OK |
| PUT | `/api/users/me` | Oui | `{username, full_name, ...}` | OK |
| PUT | `/api/users/me/password` | Oui | `{current_password, new_password}` | OK |
| DELETE | `/api/users/me` | Oui | — | OK |
| GET | `/api/users/me/progress` | Oui | — | OK |
| GET | `/api/users/me/challenges/progress` | Oui | — | OK |
| GET | `/api/users/me/sessions` | Oui | — | OK |
| DELETE | `/api/users/me/sessions/{id}` | Oui | — | OK |
| GET | `/api/users/me/export` | Oui | — | OK |
| GET | `/api/users/stats` | Oui | `?timeRange=7|30|90|all` | OK |
| GET | `/api/users/leaderboard` | Non | `?limit=50` | OK |
| GET | `/api/users/` | Admin | — | Placeholder |
| DELETE | `/api/users/{id}` | Admin | — | Placeholder |

---

## Exercises

| Méthode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/exercises` | Non | — | OK |
| GET | `/api/exercises/stats` | Non | — | OK (widget accueil) |
| GET | `/api/exercises/{id}` | Non | — | OK |
| POST | `/api/exercises/{id}/attempt` | Oui | `{answer}` | OK |
| GET | `/api/exercises/completed-ids` | Oui | — | OK |
| GET | `/api/exercises/generate` | Non | `?type=,rank=` | OK |
| POST | `/api/exercises/generate` | Non | `{type, rank, ...}` | OK |
| GET | `/api/exercises/generate-ai-stream` | Non | — | OK (SSE) |
| DELETE | `/api/exercises/{id}` | — | — | N/A (archivage via admin) |

---

## Challenges

| Méthode | Endpoint | Auth | Body / Params | Statut |
|---------|----------|------|---------------|--------|
| GET | `/api/challenges` | Non | — | OK |
| GET | `/api/challenges/{id}` | Non | — | OK |
| POST | `/api/challenges/{id}/attempt` | Oui | `{answer}` | OK — Réponse inclut `new_badges` si déblocage (Lot C-1) |
| GET | `/api/challenges/{id}/hint` | Oui | — | OK |
| GET | `/api/challenges/completed-ids` | Oui | — | OK |
| GET | `/api/challenges/generate-ai-stream` | Non | — | OK (SSE) |
| GET | `/api/challenges/badges/progress` | Oui | — | OK |
| POST | `/api/challenges/start/{id}` | Oui | — | Placeholder (optionnel) |

---

## Badges

| Méthode | Endpoint | Auth | Statut |
|---------|----------|------|--------|
| GET | `/api/badges/user` | Oui | OK |
| GET | `/api/badges/available` | Oui | OK |
| POST | `/api/badges/check` | Oui | OK |
| GET | `/api/badges/stats` | Oui | OK |

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
| GET | `/api/admin/audit-log` | Archiviste | `?skip=&limit=` | OK |
| GET | `/api/admin/config` | Archiviste | — | OK |
| PUT | `/api/admin/config` | Archiviste | `{settings: {key: value}}` | OK |
| GET | `/api/admin/export` | Archiviste | `?type=&period=` | OK |

Pages : `/admin`, `/admin/users`, `/admin/content`, `/admin/moderation`, `/admin/audit-log`, `/admin/config`.

---

## Recommendations & Chat

| Méthode | Endpoint | Auth | Statut |
|---------|----------|------|--------|
| GET | `/api/recommendations` | Oui | OK |
| POST | `/api/recommendations/generate` | Oui | OK |
| POST | `/api/recommendations/complete` | Oui | OK |
| POST | `/api/chat` | Oui | OK |
| POST | `/api/chat/stream` | Oui | OK (SSE) |

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

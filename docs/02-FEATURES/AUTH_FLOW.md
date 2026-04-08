# Authentication Flow - Mathakine

> User-facing auth journey and backend boundaries
> Updated: 08/04/2026

## Overview

```text
/register -> /verify-email -> /login -> protected application
                ^                |
                |                v
POST /api/auth/resend-verification   session cookies + refresh

/forgot-password -> email reset -> /reset-password?token=... -> /login
```

Production note:

- auth-sensitive endpoints are now protected by distributed Redis rate limiting in production
- memory fallback is dev/test only

## 1. Registration

**Page:** `/register`
**API:** `POST /api/users/`
**Rate limit:** 3 requests/minute per IP

Main fields:

- `username`
- `email`
- `password`
- `full_name` (optional)

Successful flow:

- user creation via `UserCreate`
- verification token generation
- verification email delivery
- frontend redirect to `/verify-email?verify=true`

## 2. Email verification

**Page:** `/verify-email`
**API:** `GET /api/auth/verify-email?token=...`
**Backend boundary:** `auth_recovery_service.py`

Manual resend:

- `POST /api/auth/resend-verification`
- rate limited: 2 requests/minute per IP
- generic response to avoid account enumeration

## 3. Login and session

**Page:** `/login`
**API:** `POST /api/auth/login`
**Backend boundary:** `auth_session_service.py`
**Rate limit:** 5 requests/minute per IP

On success:

- `access_token` returned in the body and stored in an HttpOnly cookie
- `refresh_token` stored in an HttpOnly cookie
- `csrf_token` stored in a readable cookie for double-submit CSRF
- a `UserSession` row is created in the database
- frontend redirects to the protected area

Current default route policy:

- `apprenant` -> `/home-learner`
- `enseignant`, `moderateur`, `admin` -> `/dashboard`

Unverified account behavior:

- login is still allowed
- `access_scope` remains limited until email verification

Refresh / bootstrap:

- `POST /api/auth/refresh` accepts the refresh cookie (or body fallback if needed)
- `POST /api/auth/validate-token` validates the access token before cookie sync; rate limit is **dedicated** (higher per-IP ceiling than login; see `RATE_LIMIT_VALIDATE_TOKEN_MAX` in `app/utils/rate_limit.py`)
- `GET /api/users/me` rebuilds the current user from the validated token
- `POST /api/auth/logout` clears auth cookies

## 4. Forgot password

**Page:** `/forgot-password`
**API:** `POST /api/auth/forgot-password`
**Backend boundary:** `auth_recovery_service.py`
**Rate limit:** 5 requests/minute per IP

The response remains generic whether the email exists or not.

## 5. Password reset

**Page:** `/reset-password`
**API:** `POST /api/auth/reset-password`
**Body:** `{token, password, password_confirm}`
**Backend boundary:** `auth_recovery_service.py` + `auth_service.py`

On success:

- password hash is replaced
- `password_changed_at` is updated
- all active `UserSession` rows are revoked
- older access/refresh tokens are rejected through `iat`

## 6. Password change from settings

**Page:** `/settings`
**API:** `PUT /api/users/me/password`
**Backend boundary:** `user_application_service.py` -> `UserService.update_user_password`

This flow is aligned with reset-password semantics:

- password hash update
- `password_changed_at` update
- session revocation
- older access/refresh tokens rejected after the current response

## 7. Active sessions

**Page:** `/settings`
**API:**

- `GET /api/users/me/sessions`
- `DELETE /api/users/me/sessions/{id}`

Behavior:

- one `UserSession` row per successful login
- current session marked `is_current: true`
- manual revocation available

## Key files

| Role                    | File                                                                                                   |
| ----------------------- | ------------------------------------------------------------------------------------------------------ |
| Frontend auth hook      | `frontend/hooks/useAuth.ts`                                                                            |
| Frontend API client     | `frontend/lib/api/client.ts`                                                                           |
| Frontend route boundary | `frontend/proxy.ts`, `frontend/lib/auth/routeAccess.ts`, `frontend/components/auth/ProtectedRoute.tsx` |
| Frontend pages          | `frontend/app/{login,register,verify-email,forgot-password,reset-password}/page.tsx`                   |
| Backend handlers        | `server/handlers/auth_handlers.py`, `server/handlers/user_handlers.py`                                 |
| Auth session            | `app/services/auth/auth_session_service.py`                                                            |
| Auth recovery           | `app/services/auth/auth_recovery_service.py`                                                           |
| Auth engine             | `app/services/auth/auth_service.py`                                                                    |
| Runtime auth            | `server/auth.py`, `server/middleware.py`                                                               |

Boundary note:

- `frontend/proxy.ts` applies the first server-side route filter before render
- `/admin` now requires an authoritative backend profile on the frontend server boundary, not only a locally decoded JWT role

## Typical HTTP codes

| Endpoint                             | Error case                            | Code  |
| ------------------------------------ | ------------------------------------- | ----- |
| `POST /api/auth/login`               | invalid credentials                   | `401` |
| `POST /api/auth/refresh`             | missing/invalid/revoked refresh token | `401` |
| `GET /api/auth/verify-email`         | invalid or expired token              | `400` |
| `POST /api/auth/resend-verification` | missing email                         | `400` |
| `POST /api/auth/forgot-password`     | email delivery failure                | `500` |
| `POST /api/auth/reset-password`      | invalid or expired token              | `400` |
| `PUT /api/users/me/password`         | incorrect current password            | `401` |
| rate-limited auth endpoints          | too many requests                     | `429` |

See also: [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) and [../01-GUIDES/CONFIGURER_EMAIL.md](../01-GUIDES/CONFIGURER_EMAIL.md)


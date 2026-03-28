# API Routes Next.js — Mathakine Frontend

> Scope : `frontend/app/api/`
> Updated : 2026-03-27
> Voir aussi : [ADR-002](../05-ADR/ADR-002-chat-assistant-public-boundary.md) — décision route chat publique

---

## Vue d'ensemble

Les routes API Next.js (`app/api/`) servent de **proxy** entre le client (même origine) et le backend Starlette.
Elles évitent d'exposer l'URL backend en CORS direct et permettent la gestion des cookies cross-domain en production.

**7 routes actives** :

| Route | Méthode | Auth requis | Type réponse |
|-------|---------|-------------|--------------|
| `POST /api/auth/sync-cookie` | POST | Non | JSON |
| `GET /api/auth/check-cookie` | GET | Non | JSON |
| `POST /api/exercises/generate-ai-stream` | POST | **Oui** (cookie) | SSE |
| `POST /api/challenges/generate-ai-stream` | POST | **Oui** (cookie) | SSE |
| `POST /api/chat` | POST | **Non** ⚠️ | JSON |
| `POST /api/chat/stream` | POST | **Non** ⚠️ | SSE |
| `GET /api/sentry-status` | GET | Non | JSON |

---

## Détail par route

### `POST /api/auth/sync-cookie`

**Fichier** : `frontend/app/api/auth/sync-cookie/route.ts`

**Rôle** : Synchronise le token JWT `access_token` en cookie sur le domaine frontend après login.
En production, le backend pose le cookie sur son propre domaine ; cette route le repose sur l'origine frontend.

**Body** :
```json
{ "access_token": "eyJ..." }
// ou
{ "clear": true }  // pour logout
```

**Flux** :
1. Valide le token auprès de `POST /api/auth/validate-token` backend.
2. Pose `Set-Cookie: access_token=...; HttpOnly; SameSite=Lax; Secure (prod); Max-Age=900`.
3. `clear: true` → Max-Age=0 (efface le cookie).

**Réponses** : `200 { ok: true }` / `400` / `401 Token invalide`

---

### `GET /api/auth/check-cookie`

**Fichier** : `frontend/app/api/auth/check-cookie/route.ts`

**Rôle** : Diagnostic — vérifie si le cookie `access_token` est présent côté frontend.

**Réponses** :
```json
// 200 cookie présent
{ "ok": true, "has_access_token_cookie": true, "hint": "Cookie présent..." }

// 401 cookie absent
{ "ok": false, "has_access_token_cookie": false, "hint": "Cookie manquant..." }
```

---

### `POST /api/exercises/generate-ai-stream`

**Fichier** : `frontend/app/api/exercises/generate-ai-stream/route.ts`

**Rôle** : Proxy SSE vers `POST /api/exercises/generate-ai-stream` backend.
Transmet les cookies d'authentification et le token CSRF.

**Auth** : Vérifie la présence du cookie `access_token` ; erreur SSE `error` si absent.

**Body** : transféré tel quel au backend (objet JSON).

**SSE events** : `status` · `exercise` · `error` · `done`

**Headers propagés** : `Cookie`, `X-CSRF-Token`, `Accept-Language`

---

### `POST /api/challenges/generate-ai-stream`

**Fichier** : `frontend/app/api/challenges/generate-ai-stream/route.ts`

**Rôle** : Proxy SSE vers `POST /api/challenges/generate-ai-stream` backend.
Même pattern que exercices.

**SSE events** : `status` · `warning` · `challenge` · `error` · `done`

---

### `POST /api/chat`

**Fichier** : `frontend/app/api/chat/route.ts`

**Rôle** : Chatbot assistant mathématique — réponse JSON non-streaming.

**⚠️ SANS AUTHENTIFICATION** — voir [ADR-002](../05-ADR/ADR-002-chat-assistant-public-boundary.md).
Seul le rate limiting Redis limite les abus. Risque de coût OpenAI non maîtrisé sans REDIS_URL.

**Body** :
```json
{ "message": "...", "conversation_history": [...] }
```

**Réponse** : `200 { "response": "..." }` (avec fallback si backend indisponible)

---

### `POST /api/chat/stream`

**Fichier** : `frontend/app/api/chat/stream/route.ts`

**Rôle** : Chatbot assistant mathématique — réponse SSE streaming.

**⚠️ SANS AUTHENTIFICATION** — même contrainte que `/api/chat`.

**Body** :
```json
{ "message": "...", "conversation_history": [...], "stream": true }
```

**SSE events** : `status` · `chunk` · `image` · `error` · `done`

---

### `GET /api/sentry-status`

**Fichier** : `frontend/app/api/sentry-status/route.ts`

**Rôle** : Diagnostic Sentry — vérifie la présence des variables d'environnement et envoie une métrique de test en production.

**Réponse** :
```json
{
  "dsnPresent": true,
  "nodeEnv": "production",
  "release": "cae7b43",
  "tracesSampleRate": "0.1",
  "replaysSessionSampleRate": "0.1",
  "replaysOnErrorSampleRate": "1.0",
  "tunnelRoute": "/monitoring",
  "metricsSent": true
}
```

---

## Résolution URL backend

Toutes les routes (sauf `check-cookie`) utilisent `lib/api/backendUrl.ts` :

1. `NEXT_PUBLIC_API_BASE_URL` (priorité)
2. `NEXT_PUBLIC_API_URL` (legacy fallback)
3. `http://localhost:10000` (dev uniquement)
4. Erreur explicite en production si URL absente, mal formée ou locale

---

## Sécurité

| Route | Protection |
|-------|-----------|
| `exercises/generate-ai-stream` | Cookie `access_token` obligatoire + CSRF |
| `challenges/generate-ai-stream` | Cookie `access_token` obligatoire + CSRF |
| `chat` | Rate limiting Redis uniquement (⚠️ sans REDIS_URL = aucune protection) |
| `chat/stream` | Rate limiting Redis uniquement (⚠️ même contrainte) |
| `auth/*` | Validation token backend avant pose cookie |
| `sentry-status` | Public (diagnostic uniquement, pas de données sensibles) |

---

## Tests

Les handlers de routes sont couverts par `frontend/__tests__/unit/app/api/` :
- succès et erreur JSON sur `/api/chat`
- succès SSE et garde config invalide sur `/api/chat/stream`
- succès SSE, refus auth/cookie, et propagation `!ok` sur `/api/exercises/generate-ai-stream`
- idem pour `/api/challenges/generate-ai-stream`

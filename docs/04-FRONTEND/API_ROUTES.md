# API Routes Next.js - Mathakine Frontend

> Scope: `frontend/app/api/`
> Updated: 2026-04-09
> Voir aussi: [frontend/lib/chat/README.md](../../frontend/lib/chat/README.md), [README_TECH.md](../../README_TECH.md), [ADR-002](../05-ADR/ADR-002-chat-assistant-public-boundary.md) pour l'historique superseded du chat public

---

## Vue d'ensemble

Les routes API Next.js (`app/api/`) servent de proxy entre le client (même origine) et le backend Starlette.
Elles évitent d'exposer directement l'URL backend en CORS, portent certaines gardes auth/cookies côté serveur Next, et permettent le streaming SSE sans logique réseau dupliquée dans le navigateur.

**7 routes actives** :

| Route                                     | Méthode | Auth requis                 | Type réponse |
| ----------------------------------------- | ------- | --------------------------- | ------------ |
| `POST /api/auth/sync-cookie`              | POST    | Non                         | JSON         |
| `GET /api/auth/check-cookie`              | GET     | Non                         | JSON         |
| `POST /api/exercises/generate-ai-stream`  | POST    | Oui (cookie `access_token`) | SSE          |
| `POST /api/challenges/generate-ai-stream` | POST    | Oui (cookie `access_token`) | SSE          |
| `POST /api/chat`                          | POST    | Oui (cookie `access_token`) | JSON         |
| `POST /api/chat/stream`                   | POST    | Oui (cookie `access_token`) | SSE          |
| `GET /api/sentry-status`                  | GET     | Non                         | JSON         |

---

## Détail par route

### `POST /api/auth/sync-cookie`

**Fichier** : `frontend/app/api/auth/sync-cookie/route.ts`

**Rôle** : synchronise le token JWT `access_token` en cookie sur le domaine frontend après login.

**Body** :

```json
{ "access_token": "eyJ..." }
```

ou

```json
{ "clear": true }
```

**Flux** :

1. valide le token auprès de `POST /api/auth/validate-token` backend
2. pose `Set-Cookie: access_token=...; HttpOnly; SameSite=Lax; Secure (prod); Max-Age=900`
3. `clear: true` efface le cookie

**Réponses** : `200 { ok: true }`, `400`, `401`

### `GET /api/auth/check-cookie`

**Fichier** : `frontend/app/api/auth/check-cookie/route.ts`

**Rôle** : diagnostic simple de présence du cookie `access_token` côté frontend.

### `POST /api/exercises/generate-ai-stream`

**Fichier** : `frontend/app/api/exercises/generate-ai-stream/route.ts`

**Rôle** : façade SSE fine vers `POST /api/exercises/generate-ai-stream` backend.

**Auth** :

- exige le cookie `access_token`
- sans cookie, retourne un event SSE `error` côté client
- les logs debug "missing auth cookie" sont limités au développement

**Transport partagé** :

- parse JSON / validation objet dans `frontend/lib/api/sseProxyRequest.ts`
- forwarding headers dans `frontend/lib/api/proxyForwardHeaders.ts`
- headers propagés : `Cookie`, `Content-Type`, `X-CSRF-Token`, `Accept-Language`
- garde `body === null` backend : conversion en event SSE d'erreur au lieu d'un flux vide silencieux

**SSE events attendus** : `status`, `exercise`, `error`, `done`

### `POST /api/challenges/generate-ai-stream`

**Fichier** : `frontend/app/api/challenges/generate-ai-stream/route.ts`

**Rôle** : même pattern que la route exercices, avec backend `POST /api/challenges/generate-ai-stream`.

**Transport partagé** : identique à la route exercices via `sseProxyRequest.ts`.

**SSE events attendus** : `status`, `warning`, `challenge`, `error`, `done`

### `POST /api/chat`

**Fichier** : `frontend/app/api/chat/route.ts`

**Rôle** : chatbot assistant mathématique, réponse JSON non-streaming.

**Auth** :

- **authentification requise**
- garde Next proxy sur le cookie `access_token`
- sans session, réponse `401` JSON `UNAUTHORIZED`, alignée sur le backend

**Transport** :

- headers backend via `frontend/lib/api/chatProxyRequest.ts`
- copie utilisateur localisée via `frontend/lib/api/chatProxyLocale.ts`
- `Accept-Language` répercuté vers les messages proxy

### `POST /api/chat/stream`

**Fichier** : `frontend/app/api/chat/stream/route.ts`

**Rôle** : chatbot assistant mathématique, réponse SSE streaming.

**Auth** :

- **authentification requise**
- sans session, réponse `401` JSON côté proxy

**Comportement notable** :

- logs runtime gérés via `frontend/lib/utils/logInDevelopment.ts` (pas de bruit `console.error` en prod pour les branches gérées)
- erreurs `401/403` backend repropagées en JSON
- backend `200` avec `body === null` transformé en event SSE d'erreur explicite
- succès : stream SSE direct avec `X-Accel-Buffering: no`

**SSE events attendus** : `status`, `chunk`, `image`, `error`, `done`

### `GET /api/sentry-status`

**Fichier** : `frontend/app/api/sentry-status/route.ts`

**Rôle** : diagnostic Sentry ; vérifie la présence des variables d'environnement et expose l'état des options frontend Sentry.

---

## Résolution URL backend

Toutes les routes proxy backend utilisent `frontend/lib/api/backendUrl.ts` :

1. `NEXT_PUBLIC_API_BASE_URL`
2. `NEXT_PUBLIC_API_URL` (fallback legacy)
3. `http://localhost:10000` en développement uniquement
4. erreur explicite en production si URL absente, mal formée ou locale

---

## Sécurité

| Route                           | Protection                                               |
| ------------------------------- | -------------------------------------------------------- |
| `exercises/generate-ai-stream`  | cookie `access_token` obligatoire + CSRF forwardé        |
| `challenges/generate-ai-stream` | cookie `access_token` obligatoire + CSRF forwardé        |
| `chat`                          | cookie `access_token` obligatoire + proxy aligné backend |
| `chat/stream`                   | cookie `access_token` obligatoire + proxy aligné backend |
| `auth/*`                        | validation token backend avant pose cookie               |
| `sentry-status`                 | public, diagnostic uniquement                            |

---

## Tests

Les handlers de routes sont couverts par `frontend/__tests__/unit/app/api/` :

- `/api/chat` : succès, erreurs JSON, auth
- `/api/chat/stream` : auth, erreurs backend, branche `body === null`, non-log en production
- `/api/exercises/generate-ai-stream` : succès, refus cookie, propagation backend `!ok`, branche `body === null`
- `/api/challenges/generate-ai-stream` : mêmes garanties que la route exercices

Ces tests sont des tests de handlers Next.js, pas des E2E navigateur.

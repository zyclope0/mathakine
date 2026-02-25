# Audit Sentry — Configuration complète

**Date :** Février 2026  
**Objectif :** Challenger la configuration Sentry frontend + backend

---

## 1. Vue d'ensemble

| Périmètre | Fichiers | DSN | Statut |
|-----------|----------|-----|--------|
| **Frontend (client)** | instrumentation-client.ts | NEXT_PUBLIC_SENTRY_DSN | ✅ |
| **Frontend (server)** | sentry.server.config.ts | SENTRY_DSN \|\| NEXT_PUBLIC_SENTRY_DSN | ✅ |
| **Frontend (edge)** | sentry.edge.config.ts | SENTRY_DSN \|\| NEXT_PUBLIC_SENTRY_DSN | ✅ |
| **Backend (Python)** | app/core/monitoring.py | SENTRY_DSN \|\| NEXT_PUBLIC_SENTRY_DSN | ✅ |

---

## 2. Frontend — Analyse détaillée

### 2.1 Client (instrumentation-client.ts)

| Élément | Valeur | OK ? |
|---------|--------|------|
| DSN | NEXT_PUBLIC_SENTRY_DSN | ✅ |
| Enabled | NODE_ENV === "production" && dsn | ✅ |
| Tunnel | /monitoring (contourne ad blockers) | ✅ |
| tracesSampleRate | 0.1 prod, 1.0 dev | ✅ |
| Session Replay | 10 % sessions, 100 % si erreur | ✅ |
| sendDefaultPii | false | ✅ (sécurité) |

### 2.2 Server & Edge

- Utilisent SENTRY_DSN ou NEXT_PUBLIC_SENTRY_DSN (fallback)
- Pas de tunnel (connexion directe serveur → Sentry)
- Pas de Replay (côté client uniquement)

### 2.3 next.config.ts (withSentryConfig)

| Élément | Valeur | OK ? |
|---------|--------|------|
| org | SENTRY_ORG \|\| "mathakine" | ⚠️ Vérifier slug réel |
| project | SENTRY_PROJECT \|\| "mathakine-frontend" | ⚠️ Ton projet = **mathakin_prod** |
| tunnelRoute | /monitoring | ✅ |
| widenClientFileUpload | true | ✅ (source maps) |

**⚠️ Action :** Si ton projet Sentry est `mathakin_prod`, définir `SENTRY_PROJECT=mathakin_prod` dans Render (frontend). Sinon les source maps iront vers "mathakine-frontend".

### 2.4 Error boundaries

- `app/error.tsx` : capture via Sentry.captureException ✅
- `app/global-error.tsx` : idem ✅
- `instrumentation.ts` : onRequestError = Sentry.captureRequestError ✅

### 2.5 CSP (Content-Security-Policy)

```
connect-src ... https://*.sentry.io https://*.ingest.sentry.io ...
worker-src 'self' blob:
```

✅ Couvre ingest.de.sentry.io (région DE) et ingest.sentry.io  
✅ `worker-src 'self' blob:` — évite le blocage du worker de compression Sentry en prod (erreur console CSP)

### 2.6 Diagnostic

- `GET /api/sentry-status` : retourne dsnPresent, nodeEnv, tunnelRoute ✅

---

## 3. Backend — Analyse détaillée

### 3.1 monitoring.py

| Élément | Valeur | OK ? |
|---------|--------|------|
| DSN | SENTRY_DSN \|\| NEXT_PUBLIC_SENTRY_DSN | ✅ |
| Environment | os.getenv("ENVIRONMENT", "development") | ⚠️ |
| tracesSampleRate | SENTRY_TRACES_SAMPLE_RATE (défaut 0.1) | ✅ |
| send_default_pii | False | ✅ |
| Désactivé si | TESTING=true | ✅ |
| Starlette | Auto-détecté (starlette dans requirements) | ✅ |

**⚠️ Environment :** En prod Render, `ENVIRONMENT=production` est dans render.yaml. Si l’erreur Sentry affichait `environment: development`, vérifier que la variable est bien définie dans le dashboard Render (backend).

### 3.2 render.yaml (backend)

```yaml
- key: NEXT_PUBLIC_SENTRY_DSN
  sync: false
```

✅ Présent. À définir manuellement avec le DSN.

---

## 4. Problèmes identifiés et correctifs

### P1 — Projet Sentry (frontend)

**Problème :** Le fallback `mathakine-frontend` peut ne pas correspondre au projet réel (`mathakin_prod`).

**Correctif :** Définir `SENTRY_PROJECT=mathakin_prod` (ou ton slug exact) dans les env du frontend Render.

### P2 — Environment backend

**Problème :** Les événements peuvent arriver avec `environment: development` si `ENVIRONMENT` n’est pas définie côté backend.

**Correctif :** `render.yaml` définit déjà `ENVIRONMENT: production`. Vérifier dans le dashboard Render (backend) que la variable existe.

### P3 — Doc SENTRY_MONITORING.md

**Problème :** La doc ne mentionne pas le fallback `NEXT_PUBLIC_SENTRY_DSN` pour le backend.

**Correctif :** Mise à jour de la doc.

---

## 5. Checklist configuration Render

### Frontend
- [ ] `NEXT_PUBLIC_SENTRY_DSN` défini (DSN complet)
- [ ] `SENTRY_ORG` = slug org (ex. mathakine)
- [ ] `SENTRY_PROJECT` = slug projet (ex. **mathakin_prod**)
- [ ] `SENTRY_AUTH_TOKEN` = token pour source maps (optionnel)

### Backend
- [ ] `NEXT_PUBLIC_SENTRY_DSN` ou `SENTRY_DSN` défini (même DSN que frontend OK)
- [ ] `ENVIRONMENT` = `production` (déjà dans render.yaml)
- [ ] `SENTRY_TRACES_SAMPLE_RATE` = 0.1 (optionnel, défaut OK)

---

## 6. Synthèse

| Statut | Détail |
|--------|--------|
| ✅ | DSN, tunnel, Replay, error boundaries, CSP |
| ⚠️ | Vérifier SENTRY_PROJECT = slug réel (mathakin_prod) |
| ⚠️ | Vérifier ENVIRONMENT=production sur le backend Render |
| ℹ️ | Backend Starlette : intégration auto via sentry-sdk + starlette |

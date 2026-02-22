# Sentry — Configuration optimale Mathakine

Guide pour configurer Sentry au mieux pour le projet Mathakine (Frontend Next.js + Backend Starlette).

---

## 1. Vue d'ensemble

| Périmètre | Fichier | Fonctionnalités |
|-----------|---------|-----------------|
| **Frontend (client)** | `instrumentation-client.ts` | Erreurs, traces, Replay, tunnel /monitoring |
| **Frontend (serveur)** | `sentry.server.config.ts` | Erreurs SSR, API routes |
| **Frontend (edge)** | `sentry.edge.config.ts` | Middleware Edge |
| **Backend Python** | `app/core/monitoring.py` | Erreurs, traces, métriques HTTP, SQLAlchemy auto |

---

## 2. Variables d'environnement (checklist)

### Obligatoire (prod)

| Variable | Où | Rôle |
|----------|-----|------|
| `NEXT_PUBLIC_SENTRY_DSN` | Frontend Render | DSN Sentry (lu au build) |
| `SENTRY_DSN` | Backend Render | Même DSN (ou fallback `NEXT_PUBLIC_SENTRY_DSN`) |
| `ENVIRONMENT` | Backend | `production` pour taguer correctement |

### Recommandé (release, source maps)

| Variable | Où | Rôle |
|----------|-----|------|
| `SENTRY_RELEASE` | Frontend + Backend | Git commit (ex: `RENDER_GIT_COMMIT`) pour corréler erreurs ↔ déploiement |
| `NEXT_PUBLIC_SENTRY_RELEASE` | Frontend | Idem, pour le bundle client (lu au build) |
| `SENTRY_ORG` | Frontend (build) | Slug org (ex: `mathakine`) |
| `SENTRY_PROJECT` | Frontend (build) | Slug projet (ex: `mathakine-frontend`) |
| `SENTRY_AUTH_TOKEN` | Frontend (build) | Token pour upload source maps |

### Optionnel (tuning)

| Variable | Défaut | Rôle |
|----------|--------|------|
| `SENTRY_TRACES_SAMPLE_RATE` | `0.1` | % des transactions tracées (10 %) |
| `NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE` | `0.1` | Idem côté client |
| `SENTRY_PROFILES_SAMPLE_RATE` | `0` | Profiling (0 = désactivé) |

---

## 3. Configuration Render (étape par étape)

### 3.1 Backend (mathakine-alpha / api)

1. **Render** → Service backend → **Environment**
2. Ajouter :
   ```
   SENTRY_DSN = https://xxx@xxx.ingest.sentry.io/xxx
   ENVIRONMENT = production
   SENTRY_RELEASE = ${RENDER_GIT_COMMIT}
   ```
   *(Render expose automatiquement `RENDER_GIT_COMMIT` — tu peux le mapper ou le laisser auto)*

3. Si `SENTRY_RELEASE` n'est pas défini, le backend utilisera `RENDER_GIT_COMMIT` automatiquement.

### 3.2 Frontend (mathakine-frontend)

1. **Render** → Service frontend → **Environment**
2. Variables **obligatoires** :
   ```
   NEXT_PUBLIC_SENTRY_DSN = https://xxx@xxx.ingest.sentry.io/xxx
   SENTRY_RELEASE = ${RENDER_GIT_COMMIT}
   NEXT_PUBLIC_SENTRY_RELEASE = ${RENDER_GIT_COMMIT}
   ```
   *Note : Les variables `NEXT_PUBLIC_*` sont lues au build. Après ajout, faire un **Manual Deploy**.*

3. Variables **source maps** (optionnel) :
   ```
   SENTRY_ORG = mathakine
   SENTRY_PROJECT = mathakine-frontend
   SENTRY_AUTH_TOKEN = sntrys_xxx
   ```

4. **Render** : vérifier que `${RENDER_GIT_COMMIT}` est bien exposé. Si non, définir manuellement `SENTRY_RELEASE` avec le hash du dernier commit déployé.

---

## 4. Ce qui est déjà configuré

- **request_id** : tag Sentry + header `X-Request-ID` + logs (corrélation)
- **Métriques** : `http.requests`, `http.request.duration` (Sentry + Prometheus)
- **Tunnel** : `/monitoring` pour contourner les ad blockers
- **Replay** : 10 % des sessions, 100 % des sessions avec erreur
- **SQLAlchemy** : spans DB automatiques (détection N+1)
- **before_send** : filtrage health/metrics côté backend

---

## 5. Bonnes pratiques

### Sampling
- **Prod** : 10 % traces (équilibre coût / visibilité)
- **Debug** : augmenter temporairement à 1.0 pour investiguer

### PII
- `sendDefaultPii: false` partout (RGPD, politique logs)
- Ne pas logger email/tokens en clair

### Release
- Toujours définir `SENTRY_RELEASE` = commit Git déployé
- Permet de savoir quelle version a cassé

### Source maps
- Sans elles : stack traces montrent `main-xxx.js:123`
- Avec : `ChallengeModal.tsx:45`

---

## 6. Vérification rapide

1. **Backend** : `curl -I https://mathakine-alpha.onrender.com/health` → doit avoir `X-Request-ID`
2. **Frontend** : `GET https://mathakine.fun/api/sentry-status` → `dsnPresent: true`
3. **Sentry** : Projet → Issues → un event récent doit avoir le tag `request_id`

---

## 7. Dépannage

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| Aucun event en prod | DSN manquant ou `enabled: false` | Vérifier vars, rebuild frontend |
| Pas de source maps | `SENTRY_AUTH_TOKEN` manquant | Token + SENTRY_ORG, SENTRY_PROJECT |
| request_id absent | Middleware non chargé | Vérifier ordre middleware |
| Trop d'events health | — | `before_send` filtre déjà /health et /metrics |

---

## 8. Fichiers de référence

| Fichier | Rôle |
|---------|------|
| `app/core/monitoring.py` | Init backend + métriques |
| `server/middleware.py` | RequestIdMiddleware |
| `frontend/instrumentation-client.ts` | Init client + Replay |
| `frontend/sentry.server.config.ts` | Init serveur Next |
| `frontend/sentry.edge.config.ts` | Init Edge |
| `frontend/next.config.ts` | withSentryConfig, tunnel |
| `docs/03-PROJECT/POLITIQUE_REDACTION_LOGS_PII.md` | Politique PII |

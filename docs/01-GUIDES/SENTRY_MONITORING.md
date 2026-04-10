# Sentry — Configuration opérable Mathakine

Guide runtime réel pour Sentry dans Mathakine (Frontend Next.js + Backend Starlette).

---

## 1. Vue d'ensemble

| Périmètre | Fichier | Fonctionnalités |
|-----------|---------|-----------------|
| **Frontend (client)** | `instrumentation-client.ts` | Erreurs, traces, Replay, tunnel /monitoring |
| **Frontend (serveur)** | `sentry.server.config.ts` | Erreurs SSR, API routes |
| **Frontend (edge)** | `sentry.edge.config.ts` | Middleware Edge |
| **Backend Python** | `app/core/monitoring.py` | Erreurs, traces HTTP (StarletteIntegration), spans DB (SqlalchemyIntegration), métriques |

## 1.1 État réel actuel

- backend : erreurs, traces et métriques Sentry actifs si `SENTRY_DSN` est défini
- frontend : erreurs, traces et Replay actifs si `NEXT_PUBLIC_SENTRY_DSN` est défini au build
- logs Sentry : non activés par défaut
- profiling backend : désactivé par défaut (`SENTRY_PROFILES_SAMPLE_RATE=0`)
- profiling frontend : non activé
- release correlation : recommandée via `SENTRY_RELEASE` et `NEXT_PUBLIC_SENTRY_RELEASE`

---

## 2. Variables d'environnement (checklist)

### Obligatoire (prod)

| Variable | Où | Rôle |
|----------|-----|------|
| `NEXT_PUBLIC_SENTRY_DSN` | Frontend Render | DSN Sentry (lu au build) |
| `SENTRY_DSN` | Backend Render | DSN Sentry backend |
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
| `SENTRY_PROFILES_SAMPLE_RATE` | `0` | Profiling backend (0 = désactivé) |
| `NEXT_PUBLIC_SENTRY_REPLAYS_SESSION_SAMPLE_RATE` | `0.1` | Replay baseline |
| `NEXT_PUBLIC_SENTRY_REPLAYS_ON_ERROR_SAMPLE_RATE` | `1.0` | Replay sur session en erreur |

---

## 3. Configuration Render (étape par étape)

### 3.1 Backend (mathakine-alpha / api)

1. **Render** → Service backend → **Environment**
2. Ajouter :
   ```
   SENTRY_DSN = https://xxx@xxx.ingest.sentry.io/xxx
   ENVIRONMENT = production
   SENTRY_RELEASE = ${RENDER_GIT_COMMIT}
   SENTRY_TRACES_SAMPLE_RATE = 0.1
   ```
   *(Render expose automatiquement `RENDER_GIT_COMMIT` — tu peux le mapper ou le laisser auto côté backend)*

3. `NEXT_PUBLIC_SENTRY_DSN` peut rester présent en rétrocompat, mais le backend doit préférer `SENTRY_DSN`.

### 3.2 Frontend (mathakine-frontend)

1. **Render** → Service frontend → **Environment**
2. Variables **obligatoires** :
   ```
   NEXT_PUBLIC_SENTRY_DSN = https://xxx@xxx.ingest.sentry.io/xxx
   SENTRY_RELEASE = ${RENDER_GIT_COMMIT}
   NEXT_PUBLIC_SENTRY_RELEASE = ${RENDER_GIT_COMMIT}
   NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE = 0.1
   NEXT_PUBLIC_SENTRY_REPLAYS_SESSION_SAMPLE_RATE = 0.1
   NEXT_PUBLIC_SENTRY_REPLAYS_ON_ERROR_SAMPLE_RATE = 1.0
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
- **StarletteIntegration** : transactions HTTP automatiques dans Sentry Performance (backend)
- **SqlalchemyIntegration** : spans DB automatiques + détection requêtes N+1 (backend)
- **User context** : `set_user(username)` côté backend (middleware auth) + `Sentry.setUser()` côté frontend (post-login/logout)
- **before_send** : filtrage health/metrics côté backend
- **handled backend 500s** : les helpers centraux capturent maintenant aussi les exceptions catchées puis transformées en JSON

---

## 5. Bonnes pratiques

### Sampling
- **Prod** : 10 % traces (équilibre coût / visibilité)
- **Debug** : augmenter temporairement à 1.0 pour investiguer
- **Profiling backend** : laisser à `0` tant qu'il n'y a pas un besoin explicite de diagnostic CPU
- **Replay** : conserver `0.1 / 1.0` tant que le volume reste raisonnable

### PII
- `sendDefaultPii: false` partout (RGPD, politique logs)
- Ne pas logger email/tokens en clair

### Logs
- les logs applicatifs restent d'abord dans Render + Loguru
- Sentry Logs n'est pas activé par défaut dans ce projet
- raison : coût, bruit, et stack Loguru déjà en place
- si besoin futur, activer seulement un flux warning/error ciblé, pas la totalité des logs

### Release
- Toujours définir `SENTRY_RELEASE` = commit Git déployé
- Permet de savoir quelle version a cassé

### Source maps
- Sans elles : stack traces montrent `main-xxx.js:123`
- Avec : `ChallengeModal.tsx:45`

---

## 6. Vérification rapide

1. **Backend** : `curl -I https://mathakine-alpha.onrender.com/health` → doit avoir `X-Request-ID`
2. **Frontend** : `GET https://mathakine.fun/api/sentry-status` → `dsnPresent: true`, `release` renseigné, sample rates visibles
3. **Frontend** : depuis un environnement où le DSN est chargé, déclencher une erreur de test (ex. console navigateur après import Sentry : `Sentry.captureException(new Error("smoke"))`) ou s’appuyer sur `/api/sentry-status` + un flux réel ; vérifier l’Issue dans Sentry (la page produit `/test-sentry` a été retirée — QF-01)
4. **Sentry** : un event récent doit avoir `request_id` et, si authentifié, un contexte utilisateur

---

## 7. Dépannage

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| Aucun event en prod | DSN manquant ou `enabled: false` | Vérifier vars, rebuild frontend |
| Pas de release dans Sentry | `SENTRY_RELEASE` / `NEXT_PUBLIC_SENTRY_RELEASE` absents | Définir les variables sur Render puis redéployer |
| Pas de source maps | `SENTRY_AUTH_TOKEN` manquant | Token + SENTRY_ORG, SENTRY_PROJECT |
| request_id absent | Middleware non chargé | Vérifier ordre middleware |
| Trop d'events health | — | `before_send` filtre déjà /health et /metrics |
| Pas de logs Sentry | normal dans l'état actuel | les logs passent par Render + Loguru, pas par Sentry Logs |
| Pas de profils Sentry | normal si `SENTRY_PROFILES_SAMPLE_RATE=0` | laisser à 0 sauf besoin explicite |

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

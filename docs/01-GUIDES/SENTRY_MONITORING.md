# Sentry — Monitoring des erreurs

## Vue d'ensemble

Sentry est configuré sur le frontend Next.js pour capturer les erreurs en production et fournir un monitoring de base (traces, session replay).

## Configuration

### Variables d'environnement

| Variable | Rôle | Où |
|----------|------|-----|
| `NEXT_PUBLIC_SENTRY_DSN` | DSN public Sentry (obligatoire en prod) | `.env.local` / plateforme de déploiement |
| `SENTRY_ORG` | Slug de l'organisation Sentry (optionnel) | CI / déploiement |
| `SENTRY_PROJECT` | Slug du projet (optionnel) | CI / déploiement |
| `SENTRY_AUTH_TOKEN` | Token pour upload des source maps (optionnel) | CI uniquement |

### Comportement

- **Développement** : Sentry est désactivé (`enabled: false` si `NODE_ENV !== "production"`)
- **Production** : Si `NEXT_PUBLIC_SENTRY_DSN` est défini, erreurs et traces sont envoyées
- **Sans DSN** : Aucune donnée n'est envoyée, pas d’erreur côté app

## Fonctionnalités activées

- **Error Monitoring** : Erreurs côté client et serveur
- **Session Replay** : 10 % des sessions, 100 % des sessions avec erreur
- **Performance (traces)** : 10 % des transactions en production

## Fichiers

- `frontend/instrumentation-client.ts` — Init client
- `frontend/sentry.server.config.ts` — Init Node.js (API routes, Server Components)
- `frontend/sentry.edge.config.ts` — Init Edge (middleware)
- `frontend/instrumentation.ts` — Enregistrement des configs + `onRequestError`
- `frontend/app/global-error.tsx` — Erreurs racine (root layout)
- `frontend/app/error.tsx` — Envoi des erreurs à Sentry

## Créer un projet Sentry

1. Créer un compte sur [sentry.io](https://sentry.io)
2. Créer un projet **Next.js**
3. Copier le **DSN** (clé publique)
4. Ajouter dans `.env.local` ou la config de prod :

   ```
   NEXT_PUBLIC_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
   ```

## Source maps — Guide pas à pas

Pour avoir des stack traces lisibles en production (fichiers `.tsx` au lieu de `main-xxx.js`), configure l’upload des source maps.

### Étape 1 : Trouver ton org et ton projet Sentry

1. Va sur [sentry.io](https://sentry.io) et connecte-toi
2. Dans l’URL ou en haut de page, repère le **slug de l’org** (ex. : `mathakine`)
3. Ouvre ton projet Next.js et repère le **slug du projet** (ex. : `mathakine-frontend`)

### Étape 2 : Créer un Personal Token

1. Sentry → **Settings** (roue dentée en bas à gauche)
2. **Developer Settings** → **Personal Tokens**
3. **Create New Token**
4. Nom : `Source Maps Upload` (ou autre)
5. Scopes : coche au minimum **`project:releases`** et **`org:read`**
6. **Create Token**
7. **Copie le token** (format `sntrys_xxx`) — il ne sera plus affiché après

### Étape 3 : Ajouter les variables sur Render (ou ta plateforme)

1. Render → ton **service frontend** (Next.js)
2. **Environment** → **Environment Variables**
3. Ajoute :

   | Key                 | Value      | Secret? |
   |---------------------|------------|---------|
   | `SENTRY_AUTH_TOKEN` | `sntrys_xxx` | ✅ Oui  |
   | `SENTRY_ORG`        | `ton-org-slug` | Non    |
   | `SENTRY_PROJECT`    | `ton-projet-slug` | Non    |

4. Sauvegarde

### Étape 4 : Déclencher un nouveau déploiement

- Push un commit ou **Manual Deploy** sur Render  
- Le build (`npm run build`) uploadera les source maps vers Sentry

### Étape 5 : Vérifier

1. Sentry → ton projet → **Settings** → **Source Maps**
2. Après un build, tu dois voir des **Releases** avec les fichiers uploadés

---

> **Note** : Le DSN (`NEXT_PUBLIC_SENTRY_DSN`) doit déjà être configuré pour recevoir les erreurs.  
> L’Auth Token sert uniquement à l’upload des source maps pendant le build.

## Dépannage : Sentry ne remonte pas en prod

1. **Vérifier le bon service Render**
   - Les variables Sentry doivent être sur le service **frontend** (mathakine-frontend)
   - Pas sur le backend (qui a DATABASE_URL, FRONTEND_URL, etc.)

2. **Vérifier `NEXT_PUBLIC_SENTRY_DSN` sur Render**
   - Render → Service frontend → Environment
   - La variable doit exister et contenir le DSN complet (ex. `https://xxx@xxx.ingest.sentry.io/xxx`)
   - **Important** : les variables `NEXT_PUBLIC_*` sont lues au **build**. Si tu l’as ajoutée après le dernier build, faire un **Manual Deploy** pour rebuilder.

3. **Ad blockers**
   - Un tunnel est configuré (`/monitoring`) pour contourner les bloqueurs
   - Tester sans ad blocker pour confirmer (ex. mode navigation privée ou autre navigateur)

4. **Debug avec logs**
   - Ajouter sur Render : `NEXT_PUBLIC_SENTRY_DEBUG` = `1`
   - Rebuild + déployer, ouvrir la console du navigateur sur le site
   - Tu verras : `[Sentry] init: { enabled, dsnPresent, env, tunnel }`
   - Si `enabled: false` ou `dsnPresent: false` → le DSN n’est pas pris au build

5. **Test client** : dans la console : `throw new Error("Test Sentry")`

6. **Test serveur** : appeler `GET /api/sentry-test`
   - En dev : pas de clé
   - En prod : définir `SENTRY_TEST_KEY` sur Render, puis `GET /api/sentry-test?key=TA_CLE`

7. **Vérifier le DSN au build** : `GET https://mathakine.fun/api/sentry-status`
   - Retourne `{ dsnPresent, nodeEnv, tunnelRoute }`
   - Si `dsnPresent: false` → le DSN n’a pas été pris au build (vars sur le mauvais service ou rebuild nécessaire)

## Tester

En production, déclencher une erreur de test :

```tsx
<button type="button" onClick={() => { throw new Error("Test Sentry"); }}>
  Test
</button>
```

L’erreur doit apparaître dans **Issues** sur le dashboard Sentry.

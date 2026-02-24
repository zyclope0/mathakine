# Variables d'environnement — Déploiement (Render)

**Dernière mise à jour :** Février 2026  
**Pour :** Alpha / Production sur Render

---

## Backend (mathakine-backend)

### Obligatoires

| Variable | Rôle | Valeur exemple |
|----------|------|----------------|
| `DATABASE_URL` | Connexion PostgreSQL | Auto (Render DB) |
| `SECRET_KEY` | Signatures JWT | Généré par Render |
| `FRONTEND_URL` | CORS + redirects | `https://mathakine.fun` |
| `OPENAI_API_KEY` | Chat + génération IA | `sk-xxx` |
| `DEFAULT_ADMIN_PASSWORD` | Validation prod (bloqué si vide/faible). Admin créé via BDD si besoin. | Valeur forte ou placeholder |

### Monitoring (Sentry)

| Variable | Rôle | Valeur exemple |
|----------|------|----------------|
| `NEXT_PUBLIC_SENTRY_DSN` ou `SENTRY_DSN` | Erreurs backend → Sentry | Même DSN que frontend |
| `ENVIRONMENT` | Tag Sentry (prod/staging) | `production` |
| `SENTRY_RELEASE` | Corrélation erreurs ↔ déploiement | `${RENDER_GIT_COMMIT}` ou manuel |
| `SENTRY_TRACES_SAMPLE_RATE` | Taux de traces APM | `0.1` (10 %) |

### Emails (un des deux : SMTP ou SendGrid)

| Variable | Rôle |
|----------|------|
| `SENDGRID_API_KEY` + `SENDGRID_FROM_EMAIL` | SendGrid (prioritaire si défini) |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_USE_TLS` | SMTP classique |

### Optionnels / Auto

| Variable | Rôle |
|----------|------|
| `MATH_TRAINER_PROFILE` | `prod` pour détecter la prod |
| `ENVIRONMENT` | `production` (souvent dans render.yaml) |
| `LOG_LEVEL` | `INFO` minimum en prod |
| `PORT` | Auto par Render |

### ❌ Non nécessaires sur le backend

| Variable | Raison |
|----------|--------|
| `SENTRY_ORG`, `SENTRY_PROJECT`, `SENTRY_AUTH_TOKEN` | Utilisés par le frontend (source maps). Backend Python n'en a pas besoin. |
| `TEST_DATABASE_URL` | Uniquement pour pytest en CI. À retirer de la prod. |

---

## Frontend (mathakine-frontend)

| Variable | Obligatoire | Rôle | Valeur exemple |
|----------|-------------|------|----------------|
| `NEXT_PUBLIC_API_BASE_URL` | ✅ | URL du backend | `https://mathakine-alpha.onrender.com` |
| `NEXT_PUBLIC_SITE_URL` | ✅ | Canonical, OpenGraph | `https://mathakine.fun` |
| `NEXT_PUBLIC_SENTRY_DSN` | — | Erreurs client → Sentry | `https://xxx@xxx.ingest.sentry.io/xxx` |
| `NEXT_PUBLIC_FEEDBACK_EMAIL` | — | Email signalements / feedback | `webmaster@mathakine.fun` |
| `NEXT_PUBLIC_CONTACT_EMAIL` | — | Email contact / formulaire (prioritaire si défini) | `webmaster@mathakine.fun` |
| `SENTRY_RELEASE` | — | Corrélation erreurs ↔ déploiement | `${RENDER_GIT_COMMIT}` |
| `NEXT_PUBLIC_SENTRY_RELEASE` | — | Idem pour le bundle client (build) | `${RENDER_GIT_COMMIT}` |
| `SENTRY_ORG` | — | Organisation Sentry (upload source maps) | Slug de ton org |
| `SENTRY_PROJECT` | — | Projet Sentry (upload source maps) | `mathakine-frontend` |
| `SENTRY_AUTH_TOKEN` | — | Token Sentry pour CI/build (source maps) | `sntrys_xxx` |
| `NODE_ENV` | — | Géré par Render | `production` |

### À définir manuellement (sync: false)

- `NEXT_PUBLIC_SENTRY_DSN`
- `SENTRY_AUTH_TOKEN` (optionnel — pour source maps en prod)

---

## Checklist pré-déploiement alpha

### Backend
- [ ] `SECRET_KEY` générée (Render le fait si `generateValue: true`)
- [ ] `DEFAULT_ADMIN_PASSWORD` définie (obligatoire au démarrage prod, ≠ admin/password/123456)
- [ ] `OPENAI_API_KEY` définie
- [ ] `NEXT_PUBLIC_SENTRY_DSN` ou `SENTRY_DSN` définie
- [ ] `FRONTEND_URL` = `https://mathakine.fun`
- [ ] Emails : SendGrid ou SMTP configuré (mot de passe oublié, vérification)
- [ ] Optionnel : retirer `TEST_DATABASE_URL`, `SENTRY_ORG`, `SENTRY_PROJECT`, `SENTRY_AUTH_TOKEN` de la prod
- [ ] Health check : `GET /health` → 200 OK

### Frontend
- [ ] `NEXT_PUBLIC_API_BASE_URL` = `https://mathakine-alpha.onrender.com`
- [ ] `NEXT_PUBLIC_SITE_URL` = `https://mathakine.fun`
- [ ] `NEXT_PUBLIC_SENTRY_DSN` définie
- [ ] `SENTRY_ORG`, `SENTRY_PROJECT`, `SENTRY_AUTH_TOKEN` (optionnel, pour source maps)

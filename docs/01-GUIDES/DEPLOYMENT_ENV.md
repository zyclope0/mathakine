# Deployment Environment Variables - Render

> Updated: 10/04/2026
> Scope: alpha / production deployment on Render

## Backend (`mathakine-backend`)

### Required In Production

| Variable | Role | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | Render-managed DB URL |
| `SECRET_KEY` | JWT and signed state secrets | generated strong value |
| `FRONTEND_URL` | CORS and redirects | `https://mathakine.fun` |
| `OPENAI_API_KEY` | Chat and AI generation | `sk-xxx` |
| `DEFAULT_ADMIN_PASSWORD` | production startup validation | strong value |
| `REDIS_URL` | distributed rate limiting source of truth | `redis://...` |

Why `REDIS_URL` is required:
- production anti-abuse protection now relies on Redis
- production must not degrade silently to in-memory rate limiting
- startup fails if `REDIS_URL` is missing in production

### Monitoring / environment tags

| Variable | Role | Example |
|---|---|---|
| `ENVIRONMENT` | runtime environment tag | `production` |
| `MATH_TRAINER_PROFILE` | alternative prod detection | `prod` |
| `LOG_LEVEL` | logging level | `INFO` |
| `WEB_CONCURRENCY` | Gunicorn worker count in production | `2` |
| `SENTRY_DSN` | Sentry backend reporting | project DSN |
| `SENTRY_RELEASE` | deployment correlation | `${RENDER_GIT_COMMIT}` |
| `SENTRY_TRACES_SAMPLE_RATE` | APM sampling | `0.1` |
| `SENTRY_PROFILES_SAMPLE_RATE` | backend profiling sampling | `0` |

### Email providers

Use one of the two families below:

| Variable family | Role |
|---|---|
| `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL` | SendGrid |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_USE_TLS` | SMTP |

### Not Needed On The Backend In Production

| Variable | Why |
|---|---|
| `TEST_DATABASE_URL` | test-only |
| `SENTRY_ORG`, `SENTRY_PROJECT`, `SENTRY_AUTH_TOKEN` | frontend source-map upload concerns |

## Frontend (`mathakine-frontend`)

| Variable | Required | Role | Example |
|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | yes | backend base URL | `https://mathakine-alpha.onrender.com` |
| `NEXT_PUBLIC_SITE_URL` | yes | canonical and OpenGraph URL | `https://mathakine.fun` |
| `NEXT_PUBLIC_SENTRY_DSN` | optional | client-side Sentry | DSN |
| `NEXT_PUBLIC_FEEDBACK_EMAIL` | optional | feedback email | `webmaster@mathakine.fun` |
| `NEXT_PUBLIC_CONTACT_EMAIL` | optional | contact email | `webmaster@mathakine.fun` |
| `SENTRY_RELEASE` | optional | release correlation | `${RENDER_GIT_COMMIT}` |
| `NEXT_PUBLIC_SENTRY_RELEASE` | optional | client release tag | `${RENDER_GIT_COMMIT}` |
| `NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE` | optional | client traces sampling | `0.1` |
| `NEXT_PUBLIC_SENTRY_REPLAYS_SESSION_SAMPLE_RATE` | optional | replay baseline sampling | `0.1` |
| `NEXT_PUBLIC_SENTRY_REPLAYS_ON_ERROR_SAMPLE_RATE` | optional | replay on error sampling | `1.0` |
| `SENTRY_ORG` | optional | source-map upload | org slug |
| `SENTRY_PROJECT` | optional | source-map upload | project slug |
| `SENTRY_AUTH_TOKEN` | optional | source-map upload | token |

## Pre-Deploy Checklist

### Backend

- [ ] `SECRET_KEY` is defined and strong
- [ ] `DEFAULT_ADMIN_PASSWORD` is defined and strong
- [ ] `OPENAI_API_KEY` is defined
- [ ] `REDIS_URL` is defined and reachable from Render
- [ ] `FRONTEND_URL` matches the deployed frontend origin
- [ ] one email provider family is configured
- [ ] `SENTRY_DSN` is defined if backend Sentry is enabled
- [ ] `SENTRY_RELEASE` matches the deployed commit if release correlation is desired
- [ ] production start command uses `gunicorn enhanced_server:app --worker-class uvicorn.workers.UvicornWorker`
- [ ] `GET /live` returns 200 (liveness — process only)
- [ ] `GET /ready` returns 200 when PostgreSQL (and Redis in production) are reachable (`render.yaml` health check uses `/ready`; `GET /health` is an alias of readiness)

### Frontend

- [ ] `NEXT_PUBLIC_API_BASE_URL` points to the deployed backend
- [ ] `NEXT_PUBLIC_SITE_URL` matches the visible frontend URL
- [ ] `NEXT_PUBLIC_SENTRY_DSN` is configured if Sentry is used
- [ ] `SENTRY_RELEASE` / `NEXT_PUBLIC_SENTRY_RELEASE` match the deployed commit if release correlation is desired
- [ ] source-map variables are present only if source-map upload is desired

## Notes

- local development may omit `REDIS_URL`; dev/test fall back to memory rate limiting
- production must not omit `REDIS_URL`
- local development keeps `python enhanced_server.py`; Render production uses Gunicorn + `UvicornWorker` against `enhanced_server:app`
- active backend runtime truth is documented in [../00-REFERENCE/ARCHITECTURE.md](../00-REFERENCE/ARCHITECTURE.md)

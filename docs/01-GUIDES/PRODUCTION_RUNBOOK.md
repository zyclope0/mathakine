# PRODUCTION RUNBOOK - MATHAKINE

> Operational runbook for production incidents and risky maintenance
> Updated: 23/03/2026

## Purpose

This runbook covers the operations that should not stay implicit:
- startup failure triage
- health verification
- Alembic migration apply / rollback
- `SECRET_KEY` rotation
- basic AI/runtime abuse checks

This document complements:
- [DEPLOYMENT_ENV.md](DEPLOYMENT_ENV.md)
- [MAINTENANCE.md](MAINTENANCE.md)

---

## 1. Before touching production

1. identify whether the issue is:
   - startup / configuration
   - database / migration
   - auth / token validity
   - AI provider degradation / abuse
2. capture the current deployed revision / config before changing anything
3. avoid combining multiple risky actions in one step

Minimum data to collect first:
- backend health result
- current Alembic revision
- recent deployment timestamp
- recent backend logs

---

## 2. Fast health checks

### Public checks

```bash
curl https://<backend>/live
curl https://<backend>/ready
curl https://<backend>/metrics
```

Expected:
- `/live` -> `200` JSON `{"status":"live"}` (liveness)
- `/ready` -> `200` JSON `{"status":"ready",...}` when DB/Redis (prod) are OK ; `503` if not (`/health` is the same readiness probe)
- `/metrics` -> Prometheus payload

### What startup validates automatically

Production startup rejects invalid settings for:
- `SECRET_KEY`
- `DEFAULT_ADMIN_PASSWORD`
- insecure default DB password if `DATABASE_URL` is not injected directly
- missing `REDIS_URL`

If the app fails at boot, inspect config first before looking for runtime bugs.

---

## 3. Startup failure triage

### Typical sequence

1. check the deploy logs
2. verify required env vars exist
3. verify database reachability
4. verify Redis reachability
5. only then inspect application-specific code paths

### Production env vars to confirm first

- `DATABASE_URL`
- `SECRET_KEY`
- `DEFAULT_ADMIN_PASSWORD`
- `REDIS_URL`
- `FRONTEND_URL`
- `OPENAI_API_KEY` if AI features are expected to work

If the failure mentions config validation, do not redeploy blindly until the env mismatch is fixed.

---

## 4. Alembic migrations

### Inspect current revision

```bash
alembic current
alembic history --verbose
```

### Apply latest migrations

```bash
alembic upgrade head
```

### Roll back the last migration

```bash
alembic downgrade -1
```

### Roll back to a specific revision

```bash
alembic downgrade <revision_id>
```

### Rules

- do not downgrade multiple revisions blindly in production
- first identify the exact migration that introduced the break
- if data compatibility is uncertain, prefer a controlled maintenance window
- if the last deploy changed both code and schema, keep the code/schema pair aligned

### Current migration files

Production schema changes currently include, among others:
- `20260321_add_point_events_ledger.py`
- `20260322_ai_eval_harness_persistence.py`
- `20260324_fix_users_created_at_default.py`
- `20260325_add_challenge_progress.py` (table `challenge_progress`)
- `20260325_fix_lca_created_at.py` (timeline F07 + défis logiques : `logic_challenge_attempts.created_at` fiable ; **head** courant)

Check `migrations/versions/` before assuming the target rollback point.

---

## 5. SECRET_KEY rotation

### Impact

Rotating `SECRET_KEY` invalidates JWT validation for existing access and refresh tokens.

Operational consequence:
- users will need to authenticate again
- any still-open session using old tokens will fail on next protected request / refresh

### Generate a new key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Safe procedure

1. announce a maintenance window if the environment is user-facing
2. generate a new strong key
3. update `SECRET_KEY` in the production environment
4. redeploy the backend
5. verify:
   - `/ready` (readiness)
   - login
   - refresh
   - `/api/users/me`
6. communicate forced re-login if needed

### Do not do

- do not rotate `SECRET_KEY` during an unresolved auth incident without first confirming the current key is the root cause
- do not rotate together with unrelated DB or migration changes unless necessary

---

## 6. AI/runtime abuse or degradation

### What to check

- rate limiting health (`REDIS_URL`, distributed store)
- `/api/admin/ai-stats`
- `/api/admin/generation-metrics`
- OpenAI/API provider errors in backend logs

### Known product boundary

- chat is public by product decision
- protection relies on rate limiting and runtime observability, not on auth gating

### If costs or volume spike

1. confirm Redis-backed rate limiting is active
2. inspect workload split in admin AI monitoring
3. inspect error buckets and model buckets
4. only then change model overrides or rate limits

---

## 7. Post-incident verification checklist

- [ ] `/ready` returns `200` (dependencies OK)
- [ ] critical auth flow works (`login`, `refresh`, `/api/users/me`)
- [ ] AI routes answer as expected for the intended scope
- [ ] no unexpected Alembic drift remains (`alembic current`)
- [ ] logs no longer show the triggering error

---

## References

- [DEPLOYMENT_ENV.md](DEPLOYMENT_ENV.md)
- [MAINTENANCE.md](MAINTENANCE.md)
- [../00-REFERENCE/ARCHITECTURE.md](../00-REFERENCE/ARCHITECTURE.md)
- [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md)
- [../02-FEATURES/API_QUICK_REFERENCE.md](../02-FEATURES/API_QUICK_REFERENCE.md)

# Changelog

All notable changes to the project are documented in this file.

The format follows the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

Visible release source of truth:
- `CHANGELOG.md`
- `frontend/package.json`

Visible product versioning policy:
- `X.Y.Z-alpha.N`: active prerelease train, integration still moving
- `X.Y.Z-beta.N`: feature set frozen, stabilization focused
- `X.Y.Z-rc.N`: release candidate
- `X.Y.Z`: stable visible release
- patch versions (`X.Y.Z+1`) become the primary bugfix signal after a stable release exists; while still in `alpha`, incrementing `alpha.N` is the normal path

## Internal backend milestones (not product releases)

- iteration `exercise/auth/user`: closed
- iteration `challenge/admin/badge`: closed
- iteration `Runtime Truth`: closed
- iteration `Contracts / Hardening`: closed
- iteration `Production Hardening`: closed
- iteration `Security, Boundaries, and API Discipline`: closed
- iteration `Typed Contracts, Service Decomposition, and Legacy Retirement`: closed
- iteration `Academic Backend Rigor, Replicability, and Operability`: closed
- lots G (Residual Contracts and Cleanup): closed (G1-G4)

Active references:
- [`runtime + contracts recap`](docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
- [`production hardening recap`](docs/03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md)
- [`security / boundaries archive`](docs/03-PROJECT/archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/README.md)
- [`iteration E archive`](docs/03-PROJECT/archives/TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_DETAIL_2026-03-16/README.md)
- [`iteration F archive`](docs/03-PROJECT/archives/ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_DETAIL_2026-03-17/README.md)
- [`active remaining follow-ups`](docs/03-PROJECT/POINTS_RESTANTS_2026-03-15.md)

## [Unreleased]

## [3.3.0-alpha.2] - 2026-03-24

### Added
- Gamification: awarding account points on successful **standard exercise** submissions via ledger source `exercise_completed` (aligned with daily challenges and badges).

### Changed
- Challenges listing (`random` order): replace `ORDER BY RANDOM()` fallback with a count + deterministic `id` offset strategy to avoid full-table random sorts under load.
- Frontend: **Exercises** and **Challenges** list sort preference (`random` / `recent`) persisted in the browser across refresh (SSR-safe restore).

### Fixed
- Gamification: PostgreSQL uses a row-level lock when granting points to reduce parallel double-award risk; SQLite test sessions remain compatible (no `FOR UPDATE`).

### Security
- Email service logs redact recipient addresses and SMTP usernames (masked identifiers).
- Test harness: hosted database URLs (e.g. Render, AWS, Supabase, Neon, Railway) are never auto-adopted as `TEST_DATABASE_URL` solely because the database name contains `test`; stricter parity checks between test and production DB configuration.

### Notes
- Documentation: roadmap updates including MVP challenge track note (`docs/02-FEATURES/`).
- Formatting: `black` alignment on touched Python modules in this train.

## [3.3.0-alpha.1] - 2026-03-22

### Changed
- The AI stack is now governed explicitly by workload (`assistant_chat`, `exercises_ai`, `challenges_ai`) with fail-closed model policies and a single runtime governance reference in `docs/00-REFERENCE/AI_MODEL_GOVERNANCE.md`.
- AI exercise/challenge generation flows now use clearer frontend architecture, stricter end-state handling, and direct CTAs to reopen the newly created resource from the generation widget.
- The project now includes bounded runtime AI observability plus offline/live comparative evaluation campaigns and persisted harness run visibility in admin monitoring.

### Fixed
- The public assistant no longer misroutes generic requests such as "create an exercise" to image generation.
- Exercise and challenge AI streams now expose safe user-facing errors and avoid false success when validation or persistence fails.
- Runtime AI cost tracking is now more honest on challenge failures/fallbacks and uses bounded in-memory retention for admin monitoring.

### Notes
- This bump opens a new visible prerelease train because the AI refactor changed user-visible behavior, reliability, and operational governance beyond a simple `alpha.N` bugfix.
- The product remains in alpha: costs shown in admin are still runtime estimates, not accounting truth.

## [3.2.0-alpha.1] - 2026-03-20

### Changed
- Backend maturity iteration `I` and recommendation iteration `R` are now both closed and reflected in the active governance documentation.
- The recommendation engine now exposes materially improved visible product behaviour:
  - canonical exercise-type normalization
  - per-type diagnostic targeting
  - deterministic exercise ranking with anti-repeat behaviour
  - challenge recommendation scoring with structured reasons
  - structured `reason_code` / `reason_params` for exercises and challenges, translated on the dashboard
  - a minimal recommendation feedback lifecycle (`shown`, `open`, qualified manual completion)
- Recommendation discovery now uses the same explicit exercise-selection pipeline as the other ranked exercise branches instead of a standalone SQL-only path.
- Active docs now distinguish clearly between internal backend remediation iterations and visible product release numbering.

### Fixed
- Visible version references were realigned after historical drift in the late `3.1.0-alpha.*` prerelease notes.
- Recommendation serving and recommendation UI reasons now follow the structured post-R baseline documented in the active project docs.

### Notes
- This is intentionally **not** `3.2.0` stable: the current engine is a stronger deterministic heuristic recommender, not a fully learned or feature-complete recommender.
- Current cited post-R baseline:
  - recommendation targeted tests: `40 passed`
  - standard backend gate: `991 passed, 2 skipped`
  - recommendation reason hook vitest: `3 passed`

## [3.1.0-alpha.8] - 2026-03-11

### Changed
- Backend consolidation release centered on `challenge`, `admin` and `badge`, with thinner handlers and explicit application facades across the HTTP boundaries in scope.
- Admin read/mutate/config/content endpoints and badge endpoints now go through dedicated application services without changing public HTTP contracts.
- API proof tests were extended on admin content and badge endpoints to verify the real mutate/public route wiring.

### Fixed
- Fixture namespace collisions between auth/admin fixtures and global cleanup were removed.
- Challenge tests that depended on nondeterministic `challenges[0]` selection now use a stable fixture with a known `correct_answer`.
- Local stability improved by excluding `tests/api/test_admin_auth_stability.py` from standard gates while it still launches `pytest` from inside `pytest`.

## [3.1.0-alpha.7] - 2026-03-09

### Changed
- Backend reliability release centered on `exercise`, `auth` and `user`, with thinner handlers, clearer application services and preserved HTTP boundaries.
- Account management became more robust for profile, sessions, GDPR export and self-delete flows.
- Authentication flows for login, refresh, verification, forgot/reset and post-reset invalidation were reindustrialized without changing public contracts.

### Fixed
- Older access and refresh tokens issued before password reset are now rejected.
- Other active sessions are revoked after password reset.
- Password change from settings now uses the same revocation mechanism.
- `POST /api/auth/resend-verification` keeps a generic secure response on malformed emails.
- `GET /api/users/me/export` is wired to the correct HTTP handler and explicitly covered by API tests.

## [3.1.0-alpha.6] - 2026-03-07

### Historical note
- Earlier `3.1.0-alpha.1` to `3.1.0-alpha.4` prerelease steps existed before the detailed entries below; they are not expanded in this changelog and remain part of the condensed prerelease history.

### Added
- F07: progression timeline via `GET /api/users/me/progress/timeline`
- F32: interleaved session via `GET /api/exercises/interleaved-plan`
- F35: DB URL secret redaction at startup

### Changed
- Dashboard progression and visualizations were harmonized.
- `POST /api/exercises/generate` better supports adaptive `age_group` resolution.

## [3.1.0-alpha.5] - 2026-03-06

### Fixed
- CI database initialization: corrected alembic.ini path resolution and robust fallback for "already exists" errors during create_all.

### Changed
- The root docs, architecture reference, setup guide, testing guide and project index now reflect the closure of `Production Hardening`.
- The detailed `Production Hardening` execution notes were archived; a single active recap now defines the iteration truth.
- The diagnostic feature documentation now reflects the signed `state_token` contract and the removal of `correct_answer` from `/api/diagnostic/question`.
- The deployment guide now documents `REDIS_URL` as mandatory in production.
- The active API reference now reflects:
  - the signed diagnostic flow
  - distributed Redis rate limiting in production
  - the archival of `app/api/endpoints/*`
- The audit-driven `Security, Boundaries, and API Discipline` iteration is now closed and documented in the active project governance docs.
- The `Typed Contracts, Service Decomposition, and Legacy Retirement` iteration is now closed and archived for traceability.
- The `Academic Backend Rigor, Replicability, and Operability` iteration is now closed and archived for traceability.
- Auth service contracts are stronger on the treated bounded scope (`CreateUserResult`, `RefreshTokenResult`, `UpdatePasswordResult`).
- Public badge listing is now explicitly bounded with `default=100` and `max=200`.
- Auth recovery / verification flows now use explicit typed result contracts on the treated bounded scope.
- `challenge_service.create_challenge` now has separated preparation, validation, persistence, and orchestration stages.
- The badge requirement engine volume cluster now lives in `app/services/badge_requirement_volume.py`.
- Admin badge requirement validation is now delegated to a dedicated validation module.
- Admin badge creation now runs through a dedicated create-flow seam with a typed prepared payload.
- Legacy compatibility runtime is clearer:
  - `app/utils/rate_limiter.py` removed
  - `app/utils/db_utils.py` simplified to `sync_db_session`
  - `app/services/enhanced_server_adapter.py` isolated as explicit compatibility legacy
- The runtime/data boundary is now formalized through `app/core/db_boundary.py`.
- Targeted test proof was strengthened on the badge requirement validation and `db_utils` seams.
- Active technical docs now reflect the post-F baseline and keep `POINTS_RESTANTS_2026-03-15.md` as the synthesis tracker.
- Lots G (Residual Contracts and Cleanup) are now closed: G1 `AuthenticateWithSessionResult`, G2 success_rate cluster in volume, G3 admin exercise create flow, G4 sync_db_session via db_boundary (19 services).

### Fixed
- Documentation no longer presents `Production Hardening` as still active.
- Documentation no longer presents `app/api/endpoints/*` as a live runtime perimeter.
- Documentation no longer presents the pre-hardening backend baseline (`823 passed, 2 skipped`, coverage gate `62 %`) as the current truth.
- `MATH_TRAINER_DEBUG` no longer defaults to `true`.
- External JSON error payloads no longer expose traceback details or raw exception internals.
- Request-size guards are now enforced before the previously uncovered JSON/body parsing paths.
- Small silent fallbacks were made explicit and more observable on the treated scope.

### Notes
- Current verified backend gate standard: `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `951 passed, 2 skipped`
- Current measured local coverage on `app` + `server`: `71 %`
- Current backend CI coverage gate: `63 %`
- Detailed historical lot documents remain archived for traceability only.

## [2.1.0] - 2026-02-06

### Added
- random ordering and hide-completed options for exercises and challenges
- badge overhaul
- AI chatbot
- admin area
- Sentry / Prometheus monitoring
- accessibility options

### Security
- CSRF, rate limiting, CORS, secure headers and JWT validation

## [2.0.0] and earlier

Condensed history: adaptive exercises, logic challenges, authentication, email verification, badges and the first dashboard layers.



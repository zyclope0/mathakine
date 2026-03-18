# Changelog

All notable changes to the project are documented in this file.

The format follows the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). The visible product release uses Semantic Versioning with `-alpha.N` suffixes.

Visible release source of truth:
- `CHANGELOG.md`
- `frontend/package.json`

## Internal backend milestones (not product releases)

- iteration `exercise/auth/user`: closed
- iteration `challenge/admin/badge`: closed
- iteration `Runtime Truth`: closed
- iteration `Contracts / Hardening`: closed
- iteration `Production Hardening`: closed
- iteration `Security, Boundaries, and API Discipline`: closed
- iteration `Typed Contracts, Service Decomposition, and Legacy Retirement`: closed
- iteration `Academic Backend Rigor, Replicability, and Operability`: closed
- lots G (Residual Contracts and Cleanup): closed (G1–G4)

Active references:
- [`runtime + contracts recap`](docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
- [`production hardening recap`](docs/03-PROJECT/BILAN_PRODUCTION_HARDENING_2026-03-15.md)
- [`security / boundaries archive`](docs/03-PROJECT/archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/README.md)
- [`iteration E archive`](docs/03-PROJECT/archives/TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_DETAIL_2026-03-16/README.md)
- [`iteration F archive`](docs/03-PROJECT/archives/ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_DETAIL_2026-03-17/README.md)
- [`active remaining follow-ups`](docs/03-PROJECT/POINTS_RESTANTS_2026-03-15.md)

## [Unreleased]

## [3.1.0-alpha.9] - 2026-03-06

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
- Current verified backend gate standard: `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` → `951 passed, 2 skipped`
- Current measured local coverage on `app` + `server`: `71 %`
- Current backend CI coverage gate: `63 %`
- Detailed historical lot documents remain archived for traceability only.

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

### Added
- F07: progression timeline via `GET /api/users/me/progress/timeline`
- F32: interleaved session via `GET /api/exercises/interleaved-plan`
- F35: DB URL secret redaction at startup

### Changed
- Dashboard progression and visualizations were harmonized.
- `POST /api/exercises/generate` better supports adaptive `age_group` resolution.

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

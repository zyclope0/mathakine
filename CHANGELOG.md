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

- [`runtime + contracts recap`](docs/03-PROJECT/archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)
- [`production hardening recap`](docs/03-PROJECT/archives/SUPERSEDED_ITERATION_NOTES_2026-03-15/BILAN_PRODUCTION_HARDENING_2026-03-15.md)
- [`security / boundaries archive`](docs/03-PROJECT/archives/SECURITY_BOUNDARIES_AND_API_DISCIPLINE_DETAIL_2026-03-16/README.md)
- [`iteration E archive`](docs/03-PROJECT/archives/TYPED_CONTRACTS_SERVICE_DECOMPOSITION_AND_LEGACY_RETIREMENT_DETAIL_2026-03-16/README.md)
- [`iteration F archive`](docs/03-PROJECT/archives/ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_DETAIL_2026-03-17/README.md)
- [`remaining follow-ups tracker (archived)`](docs/03-PROJECT/archives/PILOTAGE_AND_TRACKERS_CLOSED_2026-03/POINTS_RESTANTS_2026-03-15.md)

## [Unreleased]

## [3.6.0-beta.2] - 2026-04-17

### Security

- Password policy now enforces at least one special character in all `UserCreate` and password-change flows (`SEC-PASS-01`; `33cb2ad`, `f8f6cb6`).
- `pyasn1` bumped to `>= 0.6.3` to close `CVE-2026-30922` (recursive ASN.1 parsing DoS; Dependabot `#43`).
- `next-pwa` upgraded to `10.2.9` and `serialize-javascript` forced to `>= 7.0.5` to close the prototype-pollution advisory (Dependabot `#38`).
- `pytest` bumped to `9.0.3` for the tmpdir symlink-race fix (Dependabot `#40`).
- Production frontend responses now emit `Strict-Transport-Security`, and production secure-header middleware now also emits `Permissions-Policy: camera=(), microphone=(), geolocation=()`.
- `POST /api/feedback` is now rate-limited, closing the last missing sensitive-write bucket on the public app surface.
- Auth PII (user identifiers, SMTP addresses) is now redacted from structured logs.

### Added

- **ACTIF-03 - frontend test co-location** is now closed: runtime Vitest suites live next to their sources, while `frontend/__tests__/unit/` is intentionally reduced to the architecture guardrail test plus the `_testRequest.ts` helper.
- **ACTIF-04 - frontend coverage hardening** progressed in three steps: thresholds were introduced, raised to `46 / 38 / 42 / 48`, and then backed by eleven additional hook suites (`ACTIF-04-COVERAGE-03`).
- `requirements-dev.txt` now extends the production dependency set with test/doc tooling, while `requirements.txt` stays production-only.
- `frontend/components/challenges/visualizations/_colorMap.ts` now provides the shared visualization color truth (`VISUALIZATION_COLOR_MAP`, `resolveVisualizationColor`, `findVisualizationColorInText`) with dedicated tests.
- `tests/integration/test_enhanced_server_entrypoint.py` now protects the production ASGI entrypoint shape used by Gunicorn/Uvicorn workers.
- `docs/03-PROJECT/ANALYSE_DEPENDANCES_ET_OPPORTUNITES_2026-04-13.md` now tracks dependency-upgrade value and follow-up opportunities as a dedicated active project note.
- Admin feedback triage is now operational end-to-end: detailed modal, `new/read/resolved` workflow, hard delete, and contextual feedback entry points in the header plus exercise/challenge result states.
- `/docs` now acts as the in-app beta onboarding surface, and the dashboard exposes a direct, low-noise entry point to that guide.

### Changed

- All backend logger f-string arguments across `app/` and `server/` were converted to lazy `%`-style interpolation to satisfy Ruff `G004`; supporting codemod stubs were added under `scripts/codemods/`.
- ANSI color codes are now disabled automatically when `stderr` is not a TTY, preventing polluted CI and log-aggregator output.
- Visible version surfaces are now synchronized on `3.6.0-beta.2` across runtime and package metadata.
- Production and development Python installs are now explicitly separated: CI installs `requirements-dev.txt`, while production images stay on `requirements.txt`.
- The production ASGI entrypoint is now the concrete Starlette object exposed at `enhanced_server:app`; this fixed Render startup on `uvicorn 0.44.0`.
- Frontend dependencies were advanced on the active train: `next 16.2.3`, `eslint-config-next 16.2.3`, `next-intl 4.9.1`, `vite 7.3.2`, the Vitest family `4.1.4`, plus targeted library bumps (`dompurify`, `zustand`, `jspdf`, `katex`, `undici`, `pillow`, `sphinx`, `requests`, `uvicorn`).
- Frontend visual polish continued on the active learner-facing surfaces: Nunito became the primary UI sans-serif, JetBrains Mono the monospace companion, and the spatial theme / calm-surface passes were applied across learner home, badges, docs, and dashboard surfaces.
- Documentation governance was tightened: closed implementation notes moved into `docs/03-PROJECT/archives/IMPLEMENTATION_NOTES_CLOSED_2026-04/`, and the legacy `docs/06-WIDGETS/` redirect bucket was archived under `docs/04-FRONTEND/archives/LEGACY_WIDGET_REDIRECTS_2026-04/`.

### Fixed

- `console.error` calls in client-side hooks and auth sync were replaced with the `debugError` guard (development-visible, silent in production).
- Test monkeypatches for `logger.warning` were aligned with the new `(msg, *args)` call shape after the lazy-logging migration.
- Challenge symmetry normalization now converts row-based layouts into the canonical flat format before correction, and visual challenge auto-correction covers the same path.
- Avatar and badge icon delivery were hardened against missing or invalid image sources.
- Middleware entrypoint compatibility was restored for Next.js 16 by moving back to the supported `proxy.ts` convention.
- The challenge solver retry flow now fully resets multi-position visual selections.
- Patch coverage on the beta docs/dashboard delta is now backed by targeted characterization tests for `app/docs/page.tsx` and `DashboardOverviewSection.tsx`.

### Documentation

- Active root, guide, feature, project, and frontend docs were re-aligned on repo truth: current versions, active coverage thresholds, route-test locations, Render service names, requirements split, and the reduced `frontend/__tests__/unit/` footprint.
- `README_TECH.md`, `docs/INDEX.md`, `docs/03-PROJECT/README.md`, `docs/04-FRONTEND/ARCHITECTURE.md`, `docs/04-FRONTEND/API_ROUTES.md`, `docs/04-FRONTEND/HOOKS_CATALOGUE.md`, and `docs/04-FRONTEND/COMPONENTS_CATALOGUE.md` now reflect the current active architecture instead of the pre-co-location snapshot.
- Historical implementation notes and legacy widget redirects were archived out of the active flow, while archive READMEs and cross-links were updated so those notes remain discoverable without pretending to be active source-of-truth documents.
- `.claude/session-plan.md` is now consistently described as a local founder-planning note rather than standalone runtime truth.
- Beta documentation now has clearly separated roles: `/docs` is the short in-app guide, `docs/BETA_GUIDE.md` is the fuller parent/teacher reference, and the dashboard help entry points to the in-app guide.

## [3.6.0-beta.1] - 2026-04-17

### Added

- **C3** — Beta documentation pack: `docs/BETA_GUIDE.md` (closed beta, parents/team); `/docs` FAQ refresh (8 themes, multi-entry feedback, parent Q&A); `DocTip` component with i18n on the accessibility toolbar (Focus, dyslexia) and dashboard streak widget.
- Feedback reports now capture full debug context: `user_role`, `active_theme`, `ni_state`, `component_id` — stored server-side from JWT state, never from client body. Alembic migration `20260416_feedback_context` extends `feedback_reports` table.
- Rate limiting on `POST /api/feedback`: 10 requests/minute/IP via the existing Redis/memory rate-limit infrastructure.
- `Permissions-Policy: camera=(), microphone=(), geolocation=()` added to Next.js response headers (`next.config.ts`).
- Privacy policy (`/privacy`) now covers GDPR Art. 13 explicitly: legal basis section (Art. 6.1.b contract + Art. 6.1.f legitimate interest) and minors/parental consent section (Art. 8), available in both French and English.

### Changed

- Privacy policy date updated to April 2026; `refresh_token` cookie removed from the cookies section (cookie was retired in a previous cycle).
- `frontend/messages/fr.json` and `en.json` extended with `privacy.legalBasis` and `privacy.minors` sections.

### Fixed

- DOMPurify bumped from 3.3.3 to 3.4.0 via `npm audit fix` (Dependabot #41, GHSA-39q2-94rc-95cp, moderate severity transitive via jspdf).
- `SameSite=Lax` on the frontend auth cookie confirmed correct for cross-subdomain architecture (was flagged as L2, resolved as false positive).
- `isort` import order in `server/handlers/feedback_handlers.py` corrected to pass CI gate.

### Notes

- Beta scope: feedback context enrichment (A-tier closed on targeted scope), security hardening (B1+B2 done), user documentation C1/C2/C3 delivered for beta micro-guidage (FAQ + `BETA_GUIDE.md` + `DocTip`).
- OAuth Google evaluation (B3) is deferred to post-beta.

## [3.6.0-alpha.1] - 2026-04-05

### Added

- A dedicated learner home is now shipped as a first-class product surface: `/home-learner` becomes the default entry point for `apprenant`, with a calmer linear layout, quick actions, daily reviews, daily challenges, and progression blocks.
- Active documentation now includes a dedicated frontend UX surface reference covering learner/adult boundaries, neuro-inclusion rules, and theme truth.

### Changed

- User-facing roles are now canonical across the app and API: `apprenant`, `enseignant`, `moderateur`, `admin`. Legacy Star Wars role names remain only as backend/DB compatibility aliases.
- `NI-13` is now enforced by both the Next server boundary and the client guard: `frontend/proxy.ts` protects `/home-learner`, `/dashboard`, and `/admin` before render, while `ProtectedRoute` remains defense in depth after hydration.
- The learner/adult surface split is now explicit:
  - `apprenant` lands on `/home-learner` after login
  - `/dashboard` stays available as a secondary analytics surface for the learner
  - `/admin` now requires authoritative backend truth, not only a locally decoded token
- The theme system now exposes 8 visible themes instead of 7, with `aurora` replacing legacy `peach` and `unicorn` added as a first-class theme. Theme switching also avoids layered transition jank during light/dark changes.
- Learner-facing UX is materially calmer and more explicit: dedicated learner cards/layout, disabled-button guidance on validation, review-safe solver flow, post-answer feedback animation guards, and stable anchored sections on `/home-learner`.
- The exercise and challenge discovery surfaces were tightened substantially without changing their routes or contracts:
  - exercise filters now rely more on progressive disclosure
  - cards are lighter, keyboard-accessible, and less visually noisy
  - the challenge listing is visually realigned with the exercise catalogue
- The leaderboard now uses a stronger gamification treatment while keeping post-polish accessibility fixes in place: safer contrast, corrected ARIA usage, and calmer post-overdrive cleanup.
- Shared navigation and dashboard entry points were polished for better hierarchy and lower clutter: navbar hierarchy, learner home spacing, dashboard header disclosure, and calmer hero/metric balance.

### Fixed

- Logging out now clears the visible authenticated UI state immediately instead of requiring a manual reload.
- Admin role editing now preloads and displays the current canonical role correctly in the modal instead of showing an empty select.
- Server-side auth boundary now rejects inactive users on protected truth-building paths.
- Frontend regression tests were realigned with the shipped UX copy and visible affordances, so CI now validates the actual interface instead of stale wording.

### Notes

- This remains an `alpha` release, not `beta`: the visible product keeps evolving on audience surfaces, role strategy, and UI/UX governance. The feature set is stronger and more coherent, but not yet frozen.

## [3.5.0-alpha.1] - 2026-03-29

### Added

- F04 spaced repetition is now shipped end-to-end for exercises:
  - SM-2 persistence on `submit_answer`
  - derived user summary in `GET /api/users/stats`
  - read-only `GET /api/users/me/reviews/next`
  - dashboard visibility with a dedicated `Revisions du jour` widget
  - frontend `Review now` flow reusing the existing exercise solver
- The dashboard now exposes a calm multi-theme review summary with a direct CTA when due or overdue reviews exist.
- The exercise solver now supports `?session=spaced-review` with a review-safe handoff and post-submit continuation to the next due card.

### Changed

- `GET /api/users/stats` now includes an actionable spaced-repetition summary aligned with active, non-archived exercises only.
- The product now surfaces explanatory feedback after a spaced review submission while still hiding hints and explanations before the learner answers.
- The dashboard overview review surfaces were simplified for lower cognitive load: calmer background treatment, reduced hover noise, denser F04 layout, and clearer Quick Start affordances.

### Fixed

- Multiple-choice exercise options are now keyboard reachable even before any choice is selected.
- Spaced repetition timing edge cases (`0`, `None`, `NaN`, negative values) no longer risk over-rewarding a submission as a "fast correct" answer.
- The frontend spaced-review flow now stays review-safe end-to-end instead of reloading a spoiler-bearing standard exercise payload.

### Notes

- This opens a new visible minor alpha train because F04 is now materially available to end users, not only as backend groundwork.
- Remaining F04 follow-ups are documented as bounded reserves, not blockers: challenge integration, richer review analytics separation, optional remaining-card session meter, and future F23 coupling.

## [3.4.0-alpha.1] - 2026-03-27

### Changed

- Frontend proxy routes now resolve the Python backend through a shared `frontend/lib/api/backendUrl.ts` helper instead of four divergent local implementations.
- Exercise AI SSE now emits an explicit terminal `done` event on controlled success, validation failure and persistence failure paths, aligning the contract more closely with challenges.
- A targeted `react-hooks/exhaustive-deps` review was completed on the treated frontend scope: real latent bugs were fixed (`LocaleInitializer`, `CategoryAccuracyChart`) and intentional disables were documented instead of removed blindly.
- Frontend list completion lookup and pagination semantics are now bounded and deterministic: `useCompletedItems` uses memoized `Set.has()` and `usePaginatedContent` computes `hasMore` client-side from `skip + items.length < total`.
- Dashboard recommendations now render an initial capped slice with local `show more / show less` toggles instead of rendering the whole list unbounded.
- OpenAI workloads now share a process-local circuit breaker for recurrent upstream failures on exercises and challenges, reducing useless timeout pressure during provider incidents.
- AI generation request failures on the frontend are now mapped explicitly between missing CSRF, expired session, forbidden access and generic backend failures before the hooks show user-facing toasts.
- Pedagogical difficulty is now centered on the F42 model: `age_group + pedagogical_band -> difficulty_tier`, with legacy difficulty fields kept as compatibility layers instead of sole truth.
- Local exercise generation, challenge AI personalization, recommendation targeting, progress bridges, diagnostic enrichments, and admin/API boundaries are now aligned on the same F42 calibration seams.
- Public progression ranks are now neutralized and extended to eight buckets across profile, dashboard, leaderboard, badges, and backend level titles.
- Profile and dashboard progression now show a single public rank model: numeric level is displayed separately from the progression rank bucket.
- Account progression no longer uses a flat 100-points-per-level model; the level curve now grows by segments so ranks stay more meaningful over time.
- Legacy per-level titles (`LEVEL_TITLES`) are no longer part of the public progression payload.
- Visible Star Wars references have been removed from the main product surfaces that still exposed them (chat, emails, admin labels, recommendations, targeted schema wording).

### Added

- Frontend tests now cover `LocaleInitializer` (`html[lang]` synchronization) and `CategoryAccuracyChart` (i18n rerender of radar labels).
- Frontend tests now cover the real Next proxy routes for `/api/chat`, `/api/chat/stream`, `/api/exercises/generate-ai-stream` and `/api/challenges/generate-ai-stream`.
- Frontend tests now cover AI generation request preflight and HTTP failure mapping (`csrf_token_missing`, `http_401`, `http_403`, `http_backend`).
- Backend tests now cover:
  - `auto_correct_challenge` when pattern analysis returns `None`
  - the OpenAI circuit breaker state machine and SSE refusal when it is open
- Active documentation now includes a dedicated technical manifest and a simpler product guide for the post-F42 difficulty model and public progression ranks.
- Public/API progress surfaces now expose additive F42 projections where relevant (`canonical_age_group`, `pedagogical_band`, `difficulty_tier`) without breaking legacy contracts.
- Post-F42 observability now includes structured logs for exercise attempts and adaptive-context resolution, plus a read-only admin cohort endpoint for account progression.

### Fixed

- Production proxy configuration now fails fast on malformed or loopback backend URLs instead of silently drifting to unusable values.
- The flaky unit test for `AdminAiMonitoringPage` was stabilized by removing unnecessary heavy runtime imports and mocking non-essential UI/layout wrappers.
- `auto_correct_challenge` no longer risks calling `.upper()` on `None` when pattern auto-correction cannot infer an answer.
- The dead `generation_success` branch in challenge AI generation has been removed.
- Exercise AI request hooks no longer keep a dead `!response.ok` branch after `postAiGenerationSse()` started throwing typed request errors on non-OK HTTP responses.
- Challenge AI SSE payloads now return `difficulty_tier`, including persistence/error paths that already computed the F42 target tier.
- Adaptive exercise fallback behavior is explicitly documented and tested as a neutral legacy-compatible band (`learning`) when no stronger mastery signal exists.
- Admin difficulty boundaries now expose the intended difficulty fields consistently in list/detail flows.
- Account progression cohort observability now derives level/rank from `total_points`, avoiding stale snapshots when persisted gamification columns lag behind the current curve semantics.

### Notes

- This opens a new visible minor prerelease train because F42 changed user-visible pedagogical calibration, challenge personalization behavior, public rank identity, and documentation truth in a material way.
- Legacy backend fields such as `difficulty`, `mastery_level`, `difficulty_rating`, and `jedi_rank` remain intentionally in place as compatibility/storage layers; they are no longer the canonical pedagogical or public-display model by themselves.

## [3.3.0-alpha.3] - 2026-03-25

### Added

- Logic challenges: `SubmitChallengeAttemptResult` exposes `points_earned` when the gamification ledger successfully records the award.
- `GET /api/challenges/stats`: catalog breakdown (totals, by type, difficulty, age group) with semantics aligned to active challenges.
- Dashboard: combined category accuracy view mixing exercises and challenges, challenges progress widget refinements, dedicated radar chart component, `useChallengesStats` hook and widget/chart unit tests.
- User progression timeline can include challenge activity alongside exercises (union/backfill where applicable).
- Backend tests now cover public/admin challenge visibility under unified active/archive filters and aggregate challenge stats semantics.
- Frontend API types: `ChallengesStats` / `ChallengeCatalogStatBucket`; `ChallengeAttemptResponse.message` optional to match runtime payloads.

### Changed

- Challenge filtering and stats: `active_only` uses consistent `is_active` / `is_archived` rules across list, count, and aggregate stats; stats use a single aggregate query where relevant.

### Fixed

- Challenge attempt unit test: mock three nested savepoints (progress, streak, daily) to match `challenge_attempt_service` orchestration.

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
- Active technical docs now reflect the post-F baseline and point to the archived `POINTS_RESTANTS_2026-03-15.md` tracker instead of a removed root file.
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

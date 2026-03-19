# Lot I1 - Architecture Truth and Data-Layer Doctrine

> Iteration `I`
> Status: **done** (2026-03-19, doc-only)

## Mission

Make the active backend architecture claim truthful and explicit again.

This lot is doc-first and doctrine-first:
- clarify what the backend really isolates today
- clarify the role of sync services, `sync_db_session`, and repositories
- stop overstating repository isolation where the code still uses ORM directly in services

## Why This Lot Exists

Current active docs still suggest a stronger repository/data isolation story than the code actually implements.

Reality confirmed by audit:
- many services still import and use `Session`
- repositories exist, but remain selective rather than dominant
- the runtime/data boundary is real at handler/runtime level, but not yet a global repository architecture

## Primary Scope

- `docs/00-REFERENCE/ARCHITECTURE.md`
- `README_TECH.md`
- `docs/03-PROJECT/POINTS_RESTANTS_2026-03-15.md`
- `docs/03-PROJECT/README.md`
- any directly linked project doc that would remain contradictory after the truth alignment

## In Scope

- clarify the real backend execution model
- clarify the real doctrine for `sync_db_session`
- state explicitly that repositories are introduced selectively, not globally
- define the maturity target for future lots without overselling the current state

## Out of Scope

- repository rollout
- service refactor
- HTTP contract changes
- frontend
- new runtime behavior

## Success Criteria

- active docs no longer claim a repository-isolated backend globally
- active docs clearly distinguish:
  - handler/runtime DB boundary truth
  - selective repository usage
  - direct ORM use still present in services
- the next lots can execute against a stable architectural doctrine

## Required Proof

- inventory of service modules importing `Session`
- inventory of repository modules currently present
- explicit wording of what the architecture does and does not claim

## Cursor Execution Notes

- prefer doc-only
- only touch code/config if a directly contradictory claim cannot be fixed otherwise
- if a code change becomes necessary, keep it strictly local and explain why doc-only was insufficient

## Mandatory Validation

If doc-only:
- cite the current verified backend baseline
- no pytest rerun required

If code/config changes:
- rerun the standard gate:
  - `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov`
- rerun:
  - `black app/ server/ tests/ --check`
  - `isort app/ server/ tests/ --check-only --diff`
  - `mypy app/ server/ --ignore-missing-imports`
  - `flake8 app/ server/ --select=E9,F63,F7,F82`

## Stop Conditions

- if making the docs truthful would require a large repository refactor
- in that case:
  - stop code
  - document the active truth honestly
  - defer the refactor to a later bounded lot instead of faking architectural purity

---

## I1 Execution Recap (2026-03-19)

### Proof Collected

- **Service modules** (excl. `__init__.py`): 64
- **Service modules importing Session/sqlalchemy**: 25+ (grep `from sqlalchemy`); maturity audit cited 40 of 64
- **Repository modules**: 2 — `exercise_repository.py`, `exercise_attempt_repository.py`

### Formulations Corrected

| Doc | Before | After |
|-----|--------|-------|
| ARCHITECTURE.md | Main flow: `... -> app/repositories -> PostgreSQL` | `... -> (repositories where used \| ORM/Session direct) -> PostgreSQL` |
| ARCHITECTURE.md | "DB access isolated behind sync services and repositories" | "DB access: sync_db_session() for lifecycle; data access is selective (repositories where introduced) and direct ORM in many services" |
| ARCHITECTURE.md | "repositories/: isolated data access where introduced" | "repositories/: selective (2 modules); most services still use ORM/Session directly" |
| ARCHITECTURE.md | — | New § Data-Layer Doctrine: what is true vs not true |
| README_TECH.md | "all services import via db_boundary (G4)" | Added: "data access is selective (2 repositories) and direct ORM in many services" |
| POINTS_RESTANTS | Section 0 architecture gaps | I1 closed; doctrine established; I2–I8 remaining |

### Doctrine Finale

Voir `docs/00-REFERENCE/ARCHITECTURE.md` § Data-Layer Doctrine (I1).

### Modifications

- `docs/00-REFERENCE/ARCHITECTURE.md`
- `README_TECH.md`
- `docs/03-PROJECT/POINTS_RESTANTS_2026-03-15.md`
- `docs/03-PROJECT/README.md`
- Ce fichier (I1 pilotage)

### Runtime Modifié

Non. Lot doc-only.

### Baseline Citée

`pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` → `950 passed, 3 skipped` (non exécuté, lot doc-only).

### Review Reserve Tracking
Reserve emitted during review:
- initial I1 review found two remaining doc-truth inconsistencies:
  - docs/00-REFERENCE/ARCHITECTURE.md still showed Updated: 18/03/2026 and 951 passed, 2 skipped
  - README_TECH.md still showed Updated: 18/03/2026 and 951 passed, 2 skipped
Disposition:
- fixed by micro-lot I1b
Active reserve after I1b:
- none




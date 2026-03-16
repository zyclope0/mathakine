# Lot E5 - Legacy Compatibility Retirement

> Iteration `E`
> Status: done

## Problem To Solve

Some files still exist mainly as compatibility or historical leftovers.
As long as they remain active or half-active, they make the architecture harder to explain than it should be.

## Scope

Primary targets:
- `app/services/enhanced_server_adapter.py`
- `app/utils/db_utils.py`
- `app/utils/rate_limiter.py`

Allowed support scope:
- direct call sites
- tests proving retirement or isolation
- documentation updates required by the final truth

Out of scope:
- runtime redesign unrelated to these compatibility seams
- broad DB abstraction rewrite

## Required Outcome

- each file in scope is either removed, archived, or clearly isolated as compatibility-only
- active runtime truth becomes easier to state without footnotes

## Recommended Strategy

- prove current real usage first
- remove only what is demonstrably no longer active
- if a seam must remain, document it explicitly as compatibility

## Validation Expectation

- targeted tests around any retired call path, twice
- full backend suite if runtime call sites are affected
- doc updates if runtime truth changes

## GO / NO-GO

GO:
- less active legacy ambiguity
- explicit final runtime truth

NO-GO:
- deleting compatibility without usage proof
- mixing this lot with unrelated cleanup

## E5 Result (2026-03-16)

| Seam | Preuve usage | Décision |
|------|--------------|----------|
| `rate_limiter.py` | Aucun import dans app/ ou server/ | **Retiré** |
| `db_utils.py::db_session` | Aucun usage runtime; tests utilisaient EnhancedServerAdapter | **Retiré** (tests migrés vers sync_db_session) |
| `db_utils.py::sync_db_session` | Source de vérité, utilisé par tous les services | **Conservé** |
| `enhanced_server_adapter.py` | create_generated_exercise utilisé par exercise_ai_service | **Conservé** (get_db_session/close_db_session retirés) |

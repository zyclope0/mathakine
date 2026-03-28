# ADR-001 - Keep Starlette as the backend runtime framework

**Date** : 23/03/2026  
**Status** : Accepted  
**Scope** : HTTP runtime, route composition, handler contracts, documentation truth

---

## Context

Mathakine currently runs on a Starlette application assembled in:
- `enhanced_server.py`
- `server/app.py`
- `server/routes/*.py`

The live runtime creates a `Starlette(...)` application and wires routes via
`starlette.routing.Route` / `Mount`. The historical FastAPI tree has been archived
and is not the current production path.

This decision needed to be written down because multiple documents already say
"Starlette", but the rationale was never formalized in one durable place.

---

## Decision

Mathakine keeps **Starlette** as the single backend web framework for the live
runtime.

Implications:
- active HTTP routing remains centered in `server/routes/`
- handlers remain thin transport adapters in `server/handlers/`
- backend docs must describe Starlette as the runtime framework
- no dual-framework doctrine is maintained

---

## Why this was chosen

1. **It matches the real runtime**
   - `enhanced_server.py` builds and serves the app from `server.app.create_app`
   - `server/app.py` instantiates `Starlette(...)`
   - `server/routes/*.py` expose `Route(...)` from `starlette.routing`

2. **The codebase is already organized around Starlette boundaries**
   - route composition is explicit and centralized
   - middleware and exception handlers are assembled in `server/app.py`
   - the current docs already use `server/routes/` as API truth

3. **Reintroducing FastAPI would create documentation and maintenance drift**
   - two web-framework stories for one runtime
   - duplicated onboarding and debugging paths
   - extra surface for zero immediate product value

---

## Alternatives rejected

### Alternative A - Reintroduce FastAPI as the runtime framework

Rejected because:
- it does not reflect the current running application
- it would require a migration project, not a documentation cleanup
- there is no proven blocker today caused by Starlette

### Alternative B - Keep Starlette in code but keep both Starlette/FastAPI in docs

Rejected because:
- it weakens the source of truth
- it makes onboarding and incident response slower
- it invites incorrect implementation assumptions

---

## Consequences

### Positive

- one clear runtime story
- less ambiguity for handlers, routes, and middleware
- easier incident response and documentation maintenance

### Negative / accepted trade-off

- some historical FastAPI references still need to stay archived for context
- future contributors familiar with FastAPI do not get FastAPI-specific conveniences by default

---

## Proof points in the current tree

- `enhanced_server.py` - lazy ASGI wrapper and app entrypoint
- `server/app.py` - `Starlette(...)` construction and startup wiring
- `server/routes/__init__.py` - route aggregation
- `server/routes/users.py`, `server/routes/badges.py`, etc. - `starlette.routing.Route`

---

## Follow-up ADRs that may still be needed

- chat public without auth but rate-limited
- gamification ledger transaction strategy without `with_for_update`
- AI model policy layering and ops override doctrine

---

## Implementation boundary (A44-S5, 28/03/2026)

- **Transport errors in the auth stack** (`decode_token`, auth middleware) use
  `starlette.exceptions.HTTPException`, not FastAPI’s re-export, so the codebase
  does not imply an in-flight FastAPI migration.
- **`fastapi` is not a declared runtime dependency** in `requirements.txt` as
  long as no module imports it; re-adding it requires an explicit decision
  (amend this ADR or supersede it).

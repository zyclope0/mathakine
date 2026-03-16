# D2 - Payload Size Enforcement

> Date: 15/03/2026
> Status: pending
> Scope: enforce `MAX_CONTENT_LENGTH` before JSON parsing

## 1. Mission

Apply a real request-size guard aligned with `MAX_CONTENT_LENGTH` before JSON parsing happens.

## 2. Proven Current State

- `app/core/config.py` defines `MAX_CONTENT_LENGTH`
- `app/utils/request_utils.py` calls `await request.json()` directly
- no active app-level guard has been proven to reject oversized JSON payloads before parsing

## 3. Risk

- oversized request bodies can consume memory and CPU before being rejected
- the current trust boundary is incomplete because config declares a size limit that runtime does not actually enforce

## 4. Architecture Decision

Imposed decisions:
- one central enforcement path, not duplicated in handlers
- reject oversized payloads with `413`
- use the existing config value as the source of truth

Preferred implementation order:
1. central helper or middleware
2. shared behavior across JSON body parsing helpers
3. no handler-by-handler duplication

## 5. Allowed Scope

- `app/utils/request_utils.py`
- middleware only if that is the cleanest central enforcement
- tests for oversized body rejection
- docs if contract behavior needs to be recorded

## 6. Forbidden Scope

- broad request parsing redesign
- auth or route rewiring
- frontend
- refactor of all input validation in one lot

## 7. Files To Read Before Action

- `app/core/config.py`
- `app/utils/request_utils.py`
- `server/middleware.py`
- tests covering JSON body parsing if present

## 8. Validation

Minimum validation:
- targeted oversized payload tests
- run 1
- run 2
- full backend suite without the false gate if middleware changes
- `black`
- `isort`

## 9. GO / NO-GO

`GO` only if:
- oversized payloads are actually rejected before normal JSON parsing behavior
- the behavior is central, not copy-pasted

`NO-GO` if:
- the limit remains declarative only
- the implementation leaves obvious bypasses

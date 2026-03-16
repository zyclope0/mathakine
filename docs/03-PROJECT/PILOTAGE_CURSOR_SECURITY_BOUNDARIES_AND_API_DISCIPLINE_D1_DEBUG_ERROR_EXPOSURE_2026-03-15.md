# D1 - Debug and Error Exposure

> Date: 15/03/2026
> Status: closed
> Scope: runtime hardening of debug default and API error payload exposure

## 1. Mission

Close the two strongest findings around unsafe runtime defaults and externally visible error details:
- debug mode enabled by default at boot
- detailed error payloads exposed by the API outside production when debug logging is active

## 2. Proven Current State

- `enhanced_server.py` currently defaults `MATH_TRAINER_DEBUG` to `"true"`
- `app/utils/error_handler.py` can include:
  - `error_type`
  - traceback-based `details`
  in the JSON response payload when `LOG_LEVEL=DEBUG` and `ENVIRONMENT != production`

## 3. Risk

- unsafe debug default can leak development behavior into misconfigured environments
- traceback and internal exception metadata in HTTP payloads increase information disclosure risk
- the risk is strongest when environment separation is weak or deployment defaults are wrong

## 4. Architecture Decision

Imposed decisions:
- `MATH_TRAINER_DEBUG` default must become `false`
- external API responses must not include raw traceback or implementation details
- detailed diagnostics may remain in logs only
- if a local-only detail mode is kept, it must be explicit and non-default

## 5. Allowed Scope

- `enhanced_server.py`
- `app/utils/error_handler.py`
- tests strictly needed for this behavior
- docs only if the runtime truth changes enough to require it

## 6. Forbidden Scope

- frontend
- auth redesign
- middleware refactor unrelated to error payloads
- broad logging overhaul
- changing business error semantics outside this scope

## 7. Files To Read Before Action

- `enhanced_server.py`
- `app/utils/error_handler.py`
- any existing tests covering error responses or boot flags

## 8. Validation

Minimum validation:
- targeted tests for error payload behavior
- targeted tests or direct proof for debug default
- run 1
- run 2
- if runtime changes are transverse, full backend suite without the false gate
- `black`
- `isort`

## 9. GO / NO-GO

`GO` only if:
- debug default is no longer true
- API payloads no longer expose traceback/details by default to external callers

`NO-GO` if:
- the response still leaks traceback/details
- the implementation only moves the problem without closing it

## 10. Closure Notes

Closed on 15/03/2026 with:
- `DEBUG=false` by default in `enhanced_server.py`
- no `error_type` / `details` / traceback in external JSON error payloads
- full backend suite green on the validated tree

Non-blocking reserve kept on record:
- no dedicated boot test was added for the `DEBUG` module-level default
- the proof is direct and visible in code, but not covered by a specific test file

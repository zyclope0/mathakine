# Diagnostic Flow - F03

> Feature reference updated on 15/03/2026

## Scope

Adaptive diagnostic for arithmetic fundamentals:
- addition
- subtraction
- multiplication
- division

The diagnostic remains a bounded product flow, not a generic session framework.

## Current Runtime Truth

The current trusted flow is:
- `/api/diagnostic/start` returns an initial `state_token`
- `/api/diagnostic/question` returns the next public question payload and a refreshed token
- `/api/diagnostic/question` does not expose `correct_answer`
- `/api/diagnostic/answer` may return `correct_answer` only after submission for pedagogical feedback
- the trusted correction data is not embedded in the public question payload
- the frontend may still hold returned `session` snapshots for display or continuity, but the trusted state is the signed `state_token`
- the token now carries an opaque `pending_ref`; the trusted pending answer data lives server-side until consumed

## Integrity Model

The current integrity model is:
- session continuity through a signed `state_token`
- no client-supplied `correct_answer` trust
- no `correct_answer` exposure in `/question`
- server-side lookup of the pending correct answer via `pending_ref`
- persistence only at `/complete`

This is stronger than the previous client-trusted flow, while remaining lighter than a full server-side session framework.

## API Summary

| Method | Path | Auth | Request body |
|---|---|---|---|
| GET | `/api/diagnostic/status` | yes | none |
| POST | `/api/diagnostic/start` | yes | `{triggered_from?}` |
| POST | `/api/diagnostic/question` | yes | `{state_token}` |
| POST | `/api/diagnostic/answer` | yes | `{state_token, user_answer}` |
| POST | `/api/diagnostic/complete` | yes | `{state_token, duration_seconds?}` |

## Response Contract Notes

- `/start` returns `{session, state_token, started_at_ts}`
- `/question` returns `{done, question?, state_token}`
- `question` does not contain `correct_answer`
- `/answer` returns `{is_correct, correct_answer?, session, state_token, session_complete}`
- `/complete` returns `{success, result}`

## Out Of Scope

Still out of scope for this feature note:
- Redis-backed generic session storage
- broader recommendation architecture
- global auth/session refactors outside diagnostic

## References

- `server/handlers/diagnostic_handlers.py`
- `app/services/diagnostic/diagnostic_service.py`
- `app/core/security.py`
- `frontend/hooks/useDiagnostic.ts`

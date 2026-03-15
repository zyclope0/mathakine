# F03 - Initial Diagnostic

> Technical reference
> Updated: 15/03/2026
> Status: implemented and hardened
> Source: [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md), [WORKFLOW_EDUCATION_REFACTORING.md](WORKFLOW_EDUCATION_REFACTORING.md)

## 1. Overview

F03 evaluates the learner level across four arithmetic families through a lightweight adaptive IRT-like algorithm. The resulting scores feed recommendation and difficulty adaptation.

Covered families:
- addition
- soustraction
- multiplication
- division

## 2. Adaptive Logic

```text
1. Start from the median level (PADAWAN, ordinal 1)
2. Correct answer -> level +1 (capped at GRAND_MAITRE)
3. Incorrect answer -> level -1 (floored at INITIE)
4. Stop one family after 2 consecutive errors at the same level
5. Complete the session when all families are done or MAX_QUESTIONS is reached
```

Main constants in `app/services/diagnostic_service.py`:
- `DIAGNOSTIC_TYPES`
- `STARTING_LEVEL_ORDINAL`
- `MAX_QUESTIONS`
- `CONSECUTIVE_ERRORS_TO_STOP`

## 3. State And Integrity Model

The backend remains stateless between requests, but the client no longer owns a freeform diagnostic state.

Current contract:
- `/api/diagnostic/start` returns an initial `state_token`
- mutation steps reuse and rotate that token
- the token is signed server-side and expires after a bounded duration
- backend-controlled state embedded in the token is the source of truth for validation
- `/api/diagnostic/question` does not expose `correct_answer`
- `/api/diagnostic/answer` may return `correct_answer` only after submission for pedagogical feedback

The frontend may still hold returned `session` snapshots for display or continuity, but the trusted state is the signed `state_token`.

## 4. Persisted Data

Table: `diagnostic_results`

| Column | Type | Meaning |
|---|---|---|
| `user_id` | int | learner id |
| `triggered_from` | str | `onboarding` or `settings` |
| `scores` | JSONB | score per family |
| `questions_asked` | int | total asked questions |
| `duration_seconds` | int or null | total duration |
| `completed_at` | timestamp | completion time |

Ordinal to difficulty mapping:
- `0=INITIE`
- `1=PADAWAN`
- `2=CHEVALIER`
- `3=MAITRE`
- `4=GRAND_MAITRE`

Validity window for downstream adaptation remains bounded in `adaptive_difficulty_service`.

## 5. Active API Contract

| Method | Endpoint | Auth | Body |
|---|---|---|---|
| GET | `/api/diagnostic/status` | yes | none |
| POST | `/api/diagnostic/start` | yes | `{triggered_from?: "onboarding"|"settings"}` |
| POST | `/api/diagnostic/question` | yes | `{state_token}` |
| POST | `/api/diagnostic/answer` | yes | `{state_token, user_answer}` |
| POST | `/api/diagnostic/complete` | yes | `{state_token, duration_seconds?}` |

Response notes:
- `/question` returns `{done, question?, state_token}`
- `question` no longer contains `correct_answer`
- `/answer` returns `{is_correct, correct_answer?, session, state_token, session_complete}`

See [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md).

## 6. Files Involved

| Role | File |
|---|---|
| Business service | `app/services/diagnostic_service.py` |
| Model | `app/models/diagnostic_result.py` |
| Handlers | `server/handlers/diagnostic_handlers.py` |
| Routes | `server/routes/diagnostic.py` |
| Frontend page | `frontend/app/diagnostic/page.tsx` |
| Frontend hook | `frontend/hooks/useDiagnostic.ts` |
| Settings entry point | settings level evaluation section |

## 7. Integration With Adaptation

`adaptive_difficulty_service` uses `diagnostic_service.get_latest_score()` as the highest-priority signal when a recent diagnostic exists for the requested family.

## 8. Remaining Limits

Known accepted limits after hardening:
- the signed token is replayable during its validity window
- the challenge was integrity, not full server-side persistence or Redis-backed session storage
- the pedagogical feedback step still returns the correct answer after submission by design

## 9. Tests

Main proof files:
- `tests/api/test_diagnostic_endpoints.py`
- `tests/unit/test_adaptive_difficulty_service.py`

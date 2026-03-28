# ADRs - Mathakine

> Architecture Decision Records
> Updated: 28/03/2026

## Purpose

This folder stores durable architecture decisions that should not be buried in
pilotage notes or audit snapshots.

Use ADRs when:
- the decision changes how new code should be written
- the trade-off will likely be questioned again later
- the runtime doctrine must stay stable across multiple lots

## Active ADRs

| ADR | Status | Scope |
|---|---|---|
| [ADR-001](ADR-001-starlette-vs-fastapi.md) | Accepted | Backend web framework and runtime boundary |
| [ADR-002](ADR-002-chat-assistant-public-boundary.md) | Accepted | Chat assistant - public access without authentication |
| [ADR-003](ADR-003-gamification-concurrency-model.md) | Accepted | Gamification - SELECT FOR UPDATE conditional on dialect |
| [ADR-004](ADR-004-ai-model-policy-architecture.md) | Accepted (documented debt) | AI model policy - exercises / challenges duality |
| [ADR-005](ADR-005-spaced-repetition-foundation.md) | Accepted | Spaced repetition foundation - per user/exercise cards, derived user state |

## Reading Rule

- runtime truth still remains the code
- ADRs explain the chosen direction and the rejected alternatives
- project notes in `docs/03-PROJECT/` remain useful for history, not for stable architecture doctrine

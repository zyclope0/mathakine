# ADRs - Mathakine

> Architecture Decision Records
> Updated: 23/03/2026

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
| [ADR-001-starlette-vs-fastapi.md](ADR-001-starlette-vs-fastapi.md) | Accepted | Backend web framework and runtime boundary |

## Candidate Next ADRs

- chat public + rate limiting as product boundary
- gamification ledger concurrency strategy (`with_for_update` not used)
- AI model policy layering and explicit ops overrides

## Reading Rule

- runtime truth still remains the code
- ADRs explain the chosen direction and the rejected alternatives
- project notes in `docs/03-PROJECT/` remain useful for history, not for stable architecture doctrine

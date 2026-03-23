# Gamification account progress and points ledger

> Active reference for account-level gamification persistence
> Updated: 23/03/2026

## Scope

This document describes the persistent gamification layer for the user account:
- points accumulation
- account level progression
- Jedi rank derivation
- points ledger writes

It does **not** describe:
- IRT / pedagogical level estimation
- challenge/exercise difficulty adaptation

---

## Source of truth

### Persistence

- `app/models/user.py`
- `app/models/point_event.py`
- `migrations/versions/20260321_add_point_events_ledger.py`

### Business logic

- `app/services/gamification/gamification_service.py`
- `app/services/gamification/compute.py`
- `app/services/gamification/constants.py`
- `app/services/gamification/point_source.py`

### Exposed routes

- `GET /api/users/me`
- `GET /api/badges/stats`
- `GET /api/badges/user`
- `GET /api/users/leaderboard`

High-level route map remains:
- [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)

---

## Persisted account fields

User-level persistent fields include:
- `total_points`
- `current_level`
- `experience_points`
- `jedi_rank`
- `pinned_badge_ids`
- `current_streak`
- `best_streak`

These fields live on `users` and are not dashboard-only derived values.

---

## Level computation

The current account progression rule is centralized in `compute_state_from_total_points(...)`.

Current constants:
- `POINTS_PER_LEVEL = 100`

Current rule:
- `current_level = max(1, total_points // 100 + 1)`
- `experience_points = total_points % 100`
- `jedi_rank` is derived from the level bracket

Current rank thresholds:
- `< 5` -> `youngling`
- `< 15` -> `padawan`
- `< 30` -> `knight`
- `< 50` -> `master`
- otherwise -> `grand_master`

Any change to this formula should stay centralized in the gamification service / compute layer.

---

## Points ledger (`point_events`)

The ledger table stores one row per points attribution event.

Key columns:
- `user_id`
- `source_type`
- `source_id`
- `points_delta`
- `balance_after`
- `details`
- `created_at`

Important boundary:
- the ledger is written **server-side only**
- there is no public endpoint exposing raw `point_events`
- there is no generic public `apply_points` endpoint for clients

This is intentional for product and security reasons.

---

## Current write paths

### 1. Badge awards

When a newly earned badge has `points_reward > 0`, the badge flow delegates to:
- `app/services/badges/badge_gamification_updates.py`
- then `GamificationService.apply_points(...)`

`source_type` used:
- `badge_awarded`

### 2. Daily challenge completion

When a daily challenge is completed and has `bonus_points > 0`, the flow delegates to:
- `app/services/progress/daily_challenge_service.py`
- then `GamificationService.apply_points(...)`

`source_type` used:
- `daily_challenge_completed`

### Current source enum

Defined in:
- `app/services/gamification/point_source.py`

Current values:
- `badge_awarded`
- `daily_challenge_completed`

---

## Current read surfaces

### `GET /api/users/me`

Used as the main account-facing source for persistent gamification identity:
- `gamification_level`
- `total_points`
- `current_level`
- `jedi_rank`

### `GET /api/badges/stats`

Aggregated stats for the current user:
- `user_stats`
- `badges_summary`
- `performance`

### `GET /api/badges/user`

Returns earned badges and a `user_stats` block including pinned badges and persistent account stats.

### `GET /api/users/leaderboard`

Uses points/ranking information for leaderboard ordering and display.

---

## Transaction / concurrency note

Current behavior:
- `GamificationService.apply_points(...)` updates the user row and appends a ledger row in the same DB flow
- it does **not** use `with_for_update`

Reason documented in code:
- SQLite test compatibility
- low expected contention on this flow

This is an accepted current trade-off, not an undocumented omission.

---

## Relationship with backlog F38

F38 remains the product/backlog follow-up for:
- more coherent account progression UX
- clearer history of gains
- possible richer user-facing exploitation of gamification state

If product eventually needs a public ledger history view, that should be designed explicitly and not inferred from the current backend internals.

---

## Related docs

- [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)
- [BADGES_AMELIORATIONS.md](BADGES_AMELIORATIONS.md)
- [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md)
- [../03-PROJECT/POINTS_RESTANTS_2026-03-15.md](../03-PROJECT/POINTS_RESTANTS_2026-03-15.md)

# Gamification account progress and points ledger

> Active reference for account-level progression
> Updated: 27/03/2026

## Scope

This document describes the persistent gamification layer for the user account:
- points accumulation
- account level progression
- public progression rank derivation
- ledger writes and main read surfaces

It does **not** describe:
- pedagogical difficulty
- diagnostic or mastery estimation
- exercise/challenge content calibration

Those concerns are now documented separately in:
- [DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md](DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md)
- [../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md](../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md)

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

### Public label resolution

- `frontend/lib/gamification/progressionRankLabel.ts`
- `frontend/lib/constants/leaderboard.ts`
- `frontend/messages/fr.json`
- `frontend/messages/en.json`

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

Important:
- the persisted field name is still `jedi_rank` for historical compatibility
- the public UI no longer exposes Jedi wording
- canonical public buckets are now neutral progression buckets

---

## Level computation

The unique account progression rule is centralized in:
- `compute_state_from_total_points(...)`

`total_points` is the source of truth. Level and XP-in-bracket use a **piecewise cost curve** (`LEVEL_UP_COST_SEGMENTS` in `app/services/gamification/constants.py`): each transition `L → L+1` has an integer point cost that steps up by tier (e.g. 200 for low levels, then 300, 420, 580, 750 for higher bands).

- `cumulative_points_at_level_start(L)` = minimum total needed to be at level `L` (level 1 starts at 0).
- `current_level` = largest `L` with `total_points >= cumulative_points_at_level_start(L)`.
- `experience_points` = `total_points - cumulative_points_at_level_start(current_level)` (progress in the current level).
- API `gamification_level.next_level_xp` = `cost_to_advance_from_level(current_level)`.

Legacy (pre F42-P4): `POINTS_PER_LEVEL_LEGACY = 100` — linear `// 100 + 1` model; kept as a named constant only, not used for level math.

The rank bucket is still derived from `current_level` (synthetic level from points).

### Current canonical rank buckets

Technical bucket computation is centralized in:
- `jedi_rank_for_level(...)`

Canonical public buckets:
- `cadet`
- `scout`
- `explorer`
- `navigator`
- `cartographer`
- `commander`
- `stellar_archivist`
- `cosmic_legend`

Current thresholds:
- `< 3` -> `cadet`
- `< 6` -> `scout`
- `< 10` -> `explorer`
- `< 15` -> `navigator`
- `< 22` -> `cartographer`
- `< 30` -> `commander`
- `< 42` -> `stellar_archivist`
- otherwise -> `cosmic_legend`

Numeric level labels (« Niveau n ») are **client-side i18n**; the API exposes `current` and `jedi_rank` only (F42-P5).

---

## Legacy compatibility

Historical persisted values may still contain:
- `youngling`
- `padawan`
- `knight`
- `master`
- `grand_master`

Current handling:
- backend canonicalization is available on treated public payloads
- frontend also canonicalizes defensively before resolving labels/icons

This is acceptable as a compatibility layer.
It should not be treated as the public product vocabulary anymore.

---

## Points ledger (`point_events`)

The ledger stores one row per points attribution event.

Key columns:
- `user_id`
- `source_type`
- `source_id`
- `points_delta`
- `balance_after`
- `details`
- `created_at`

Important boundary:
- ledger writes are server-side only
- there is no generic public `apply_points` endpoint
- there is no raw public ledger dump route

This is intentional.

---

## Current write paths

### Badge awards

When a newly earned badge has `points_reward > 0`, the badge flow delegates to:
- `app/services/badges/badge_gamification_updates.py`
- then `GamificationService.apply_points(...)`

`source_type`:
- `badge_awarded`

### Daily challenge completion

When a daily challenge is completed and has `bonus_points > 0`, the flow delegates to:
- `app/services/progress/daily_challenge_service.py`
- then `GamificationService.apply_points(...)`

`source_type`:
- `daily_challenge_completed`

### Standard exercise completion

Successful standard exercise submissions can also award points through:
- the exercise attempt flow
- then `GamificationService.apply_points(...)`

`source_type`:
- `exercise_completed`

Current source enum:
- `app/services/gamification/point_source.py`

---

## Current read surfaces

### `GET /api/users/me`

Main account-facing source for persistent progression identity:
- `gamification_level`
- `total_points`
- `current_level`
- `jedi_rank` (transport key, neutralized in display)

### `GET /api/badges/stats`

Aggregated stats for the current user:
- `user_stats`
- `badges_summary`
- `performance`

### `GET /api/badges/user`

Returns earned badges and `user_stats`, including persistent account progression state.

### `GET /api/users/leaderboard`

Uses points/rank information for ordering and display.

---

## Transaction / concurrency note

Current behavior:
- `GamificationService.apply_points(...)` updates the user row and appends a ledger row in the same DB flow
- the treated production path is row-lock aware where required
- SQLite test compatibility remains preserved

This is an accepted implementation detail, not an accidental omission.

---

## Relationship with product backlog

The remaining backlog around account progression is now mostly UX/product-facing:
- richer ledger history for the user
- aggregates by source
- clearer account progression storytelling

What is already done:
- persistent points engine
- level/XP/rank computation
- leaderboard, profile/dashboard and badges integration
- public neutral rank labels

What is still optional future work:
- dedicated user-facing history of point gains
- more explicit account progress breakdown by source

---

## Related docs

- [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)
- [DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md](DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md)
- [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md)
- [../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md](../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md)

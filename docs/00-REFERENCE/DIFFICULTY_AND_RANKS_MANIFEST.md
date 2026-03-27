# Difficulty And Ranks Manifest

> Cross-module reference for pedagogical difficulty and public progression ranks
> Updated: 2026-03-27

## Purpose

This document is the living reference for two domains that must stay separate:

1. pedagogical difficulty
2. account progression ranks

It exists to prevent future lots from mixing:
- learning calibration
- diagnostic/mastery signals
- recommendation targeting
- public gamification identity

Live code remains the final truth. This file records the current stable architecture and the intended extension rules.

---

## Non-Negotiable Separation

### Pedagogical difficulty

Used to decide:
- which exercises/challenges should be generated
- how hard they should be
- how progress and diagnostic should be projected
- what content tier should be recommended

Pedagogical difficulty must be driven by:
- age group
- pedagogical band
- difficulty tier
- challenge difficulty rating
- diagnostic/progress/mastery signals

It must **not** be driven by:
- points
- account level
- leaderboard rank
- badges

### Public progression rank

Used to display:
- account progression
- profile/dashboard progression identity
- leaderboard/badges public status

Public progression rank must be driven by:
- total points
- current level
- rank bucket thresholds

It must **not** be used to:
- calibrate content
- infer pedagogical mastery
- replace difficulty tier

---

## Canonical Vocabulary

| Domain | Canonical concept | Notes |
|---|---|---|
| User profile | `age_group` | Persisted user age band used as first-class F42 signal |
| Pedagogy | `pedagogical_band` | `discovery`, `learning`, `consolidation` |
| Pedagogy | `difficulty_tier` | F42 cell `1..12` = age band x pedagogical band |
| Exercise legacy | `difficulty` | Legacy stored string (`INITIE`, `PADAWAN`, `CHEVALIER`, `MAITRE`, `GRAND_MAITRE`) kept for compatibility |
| Challenge public difficulty | `difficulty_rating` | Public scalar `1.0..5.0` for logic challenges |
| Exercise progress | `mastery_level` | Legacy integer `1..5`, projected into F42 through the bridge |
| Challenge progress | `mastery_level` string | Legacy string (`novice`, `apprentice`, `adept`, `expert`) projected into F42 through the bridge |
| Gamification | `current_level` | Account level derived from total points |
| Gamification | `jedi_rank` | Legacy field name kept as transport key for the public rank bucket |
| Gamification UI | progression rank label | Public label resolved from bucket key, never hard-coded from legacy Jedi wording |

---

## Source Of Truth Matrix

### Pedagogical difficulty

| Responsibility | Source of truth |
|---|---|
| Age-group normalization | [user_age_group.py](/D:/Mathakine/app/core/user_age_group.py) and [constants.py](/D:/Mathakine/app/core/constants.py) |
| Tier formula and content-tier helpers | [difficulty_tier.py](/D:/Mathakine/app/core/difficulty_tier.py) |
| Legacy progress/diagnostic -> F42 bridge | [mastery_tier_bridge.py](/D:/Mathakine/app/core/mastery_tier_bridge.py) |
| Exercise runtime adaptive context | [adaptive_difficulty_service.py](/D:/Mathakine/app/services/exercises/adaptive_difficulty_service.py) |
| Recommendation user context | [recommendation_user_context.py](/D:/Mathakine/app/services/recommendation/recommendation_user_context.py) |
| Challenge AI personalization context | [challenge_generation_context.py](/D:/Mathakine/app/services/challenges/challenge_generation_context.py) |
| Challenge public rating calibration | [challenge_difficulty_policy.py](/D:/Mathakine/app/services/challenges/challenge_difficulty_policy.py) |

### Public progression ranks

| Responsibility | Source of truth |
|---|---|
| Points -> level -> rank bucket formula | [compute.py](/D:/Mathakine/app/services/gamification/compute.py) |
| API level title | [level_titles.py](/D:/Mathakine/app/services/gamification/level_titles.py) |
| Account payload builder | [gamification_service.py](/D:/Mathakine/app/services/gamification/gamification_service.py) |
| Frontend bucket canonicalization | [progressionRankLabel.ts](/D:/Mathakine/frontend/lib/gamification/progressionRankLabel.ts) |
| Frontend icons/colors | [leaderboard.ts](/D:/Mathakine/frontend/lib/constants/leaderboard.ts) |
| Public translations | [fr.json](/D:/Mathakine/frontend/messages/fr.json) and [en.json](/D:/Mathakine/frontend/messages/en.json) |

---

## Pedagogical Difficulty Model

### 1. Age groups

Stable user-facing/persisted groups:
- `6-8`
- `9-11`
- `12-14`
- `15+`

Internal canonicalization still maps historical values such as:
- `15-17`
- `adulte`
- `tous-ages`

The normalization seam is:
- [normalize_age_group(...)](/D:/Mathakine/app/core/constants.py)
- [normalized_age_group_from_user_profile(...)](/D:/Mathakine/app/core/user_age_group.py)

### 2. Pedagogical bands

Canonical bands:
- `discovery`
- `learning`
- `consolidation`

These are the only valid second-axis labels for F42 tier computation.

### 3. F42 difficulty tier

The canonical formula is:

`difficulty_tier = age_band_index * 3 + pedagogical_band_index + 1`

Range:
- `1..12`

Centralized in:
- [compute_tier_from_bands(...)](/D:/Mathakine/app/core/difficulty_tier.py)
- [compute_tier_from_age_group_and_band(...)](/D:/Mathakine/app/core/difficulty_tier.py)

### 4. Legacy stored difficulty

Exercises still persist a legacy `difficulty` string for compatibility.

Current legacy buckets are still interpreted through:
- [pedagogical_band_index_from_difficulty(...)](/D:/Mathakine/app/core/difficulty_tier.py)

This legacy field is acceptable as a storage/input compatibility layer, but it is no longer the only pedagogical truth.

### 5. Challenge difficulty rating

Logic challenges expose a public `difficulty_rating` on a `1.0..5.0` scale.

This scale is:
- public-facing
- challenge-specific
- not equivalent to account rank

Current calibration is centralized in:
- [calibrate_challenge_difficulty(...)](/D:/Mathakine/app/services/challenges/challenge_difficulty_policy.py)

---

## Legacy-To-F42 Bridges

### Exercise progress

Legacy storage:
- `Progress.mastery_level` (`1..5`)
- `Progress.difficulty`

Projection source:
- [mastery_level_int_to_pedagogical_band(...)](/D:/Mathakine/app/core/mastery_tier_bridge.py)
- [mastery_to_tier(...)](/D:/Mathakine/app/core/mastery_tier_bridge.py)
- [project_exercise_progress_f42(...)](/D:/Mathakine/app/core/mastery_tier_bridge.py)

Current canonical mapping:
- `1`, `2` -> `discovery`
- `3` -> `learning`
- `4`, `5` -> `consolidation`

### Challenge progress

Legacy storage:
- `ChallengeProgress.mastery_level` string

Projection source:
- [challenge_mastery_string_to_pedagogical_band(...)](/D:/Mathakine/app/core/mastery_tier_bridge.py)
- [project_challenge_progress_row_f42(...)](/D:/Mathakine/app/core/mastery_tier_bridge.py)

Current canonical mapping:
- `novice` -> `discovery`
- `apprentice` -> `learning`
- `adept` -> `learning`
- `expert` -> `consolidation`

### Diagnostic

Legacy storage:
- diagnostic score `difficulty`

Projection source:
- [tier_from_diagnostic_difficulty(...)](/D:/Mathakine/app/core/mastery_tier_bridge.py)
- [enrich_diagnostic_scores_f42(...)](/D:/Mathakine/app/core/mastery_tier_bridge.py)

---

## Age-Group Resolution Order

The preferred resolution order for any F42 projection is:

1. persisted `users.age_group`
2. `preferred_difficulty` only as compatibility fallback
3. `grade_level` fallback
4. explicit safe default only when no better signal exists

Current bridge default:
- `GROUP_9_11`

Current source:
- [canonical_age_group_from_user(...)](/D:/Mathakine/app/core/mastery_tier_bridge.py)
- [canonical_age_group_with_fallback(...)](/D:/Mathakine/app/core/mastery_tier_bridge.py)

Important:
- this fallback is acceptable for compatibility
- it must not silently override a valid explicit age input

---

## Runtime Difficulty Flows

### Exercise generation

Main seams:
- [exercise_generation_service.py](/D:/Mathakine/app/services/exercises/exercise_generation_service.py)
- [adaptive_difficulty_service.py](/D:/Mathakine/app/services/exercises/adaptive_difficulty_service.py)
- [difficulty_tier.py](/D:/Mathakine/app/core/difficulty_tier.py)

Current rule:
- generation may use a stable age-group + a second-axis pedagogical band
- the resulting tier must be computed from the real `(age_group x band)` cell
- if a runtime band override is used, `difficulty_tier` and calibration text must be recomputed accordingly

### Recommendation

Main seam:
- [build_recommendation_user_context(...)](/D:/Mathakine/app/services/recommendation/recommendation_user_context.py)

Current responsibility:
- resolve user age group
- compute global default legacy difficulty
- expose `target_difficulty_tier`

This is the reusable seam for user-context personalization. New personalization lots should prefer reuse/extraction over duplicating age/tier logic.

### Challenge generation

Main seam:
- [challenge_generation_context.py](/D:/Mathakine/app/services/challenges/challenge_generation_context.py)

Current rule:
- explicit age input wins over implicit profile age for the envelope
- user-context pedagogical band remains reusable for personalization
- if explicit age differs from profile age, the effective tier must be recomputed on the explicit age x profile band cell

---

## Account Progression Rank Model

### What it represents

Account progression rank is a public gamification identity derived from points.

It is:
- longitudinal
- motivational
- account-scoped

It is not:
- a pedagogical mastery estimate
- a content difficulty setting

### Current level formula

Centralized in:
- [compute_state_from_total_points(...)](/D:/Mathakine/app/services/gamification/compute.py)

Current formula:
- `current_level = max(1, total_points // POINTS_PER_LEVEL + 1)`
- `experience_points = total_points % POINTS_PER_LEVEL`

Current constant:
- `POINTS_PER_LEVEL = 100`

### Current rank buckets

Current bucket computation is centralized in:
- [jedi_rank_for_level(...)](/D:/Mathakine/app/services/gamification/compute.py)

Current canonical buckets:
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

### Current per-level titles

Displayed account level titles are centralized in:
- [LEVEL_TITLES](/D:/Mathakine/app/services/gamification/level_titles.py)

Important distinction:
- `jedi_rank` is the bucket key
- `level.title` is the human title for the exact numeric level

These are related but not identical concepts.

---

## Public Read Boundaries

### Difficulty / progress

Current additive F42 boundaries include:
- diagnostic projection
- user progress by category
- challenge detailed progress

Reference seams:
- [mastery_tier_bridge.py](/D:/Mathakine/app/core/mastery_tier_bridge.py)
- [user_service.py](/D:/Mathakine/app/services/users/user_service.py)
- [challenge_progress.py](/D:/Mathakine/app/schemas/challenge_progress.py)

### Account progression / ranks

Current public read surfaces include:
- `GET /api/users/me`
- `GET /api/users/leaderboard`
- `GET /api/badges/stats`
- `GET /api/badges/user`

Reference doc:
- [GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md](/D:/Mathakine/docs/02-FEATURES/GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md)

---

## Compatibility Notes

The following legacy names still exist and are acceptable as long as public labels stay clean:
- field name `jedi_rank`
- function `jedi_rank_for_level(...)`
- legacy exercise difficulty strings such as `PADAWAN`
- compatibility mapping from old leaderboard buckets (`youngling`, `padawan`, `knight`, `master`, `grand_master`)

These are technical debt or transport compatibility, not immediate product bugs by themselves.

What is **not** acceptable:
- leaking those names into visible UI labels
- using account rank as a proxy for pedagogical difficulty
- recomputing difficulty tier from incomplete legacy data when a richer runtime/context value already exists

---

## Extension Rules

### If you change pedagogical difficulty

You must review together:
- [difficulty_tier.py](/D:/Mathakine/app/core/difficulty_tier.py)
- [mastery_tier_bridge.py](/D:/Mathakine/app/core/mastery_tier_bridge.py)
- [recommendation_user_context.py](/D:/Mathakine/app/services/recommendation/recommendation_user_context.py)
- exercise/challenge runtime contexts that consume F42

You must not:
- add a second mastery -> band mapping elsewhere
- introduce a new age-group fallback order in a random service
- let explicit age input be silently overwritten by a profile fallback

### If you change challenge difficulty calibration

You must review together:
- [challenge_generation_context.py](/D:/Mathakine/app/services/challenges/challenge_generation_context.py)
- [challenge_difficulty_policy.py](/D:/Mathakine/app/services/challenges/challenge_difficulty_policy.py)
- [challenge_ai_service.py](/D:/Mathakine/app/services/challenges/challenge_ai_service.py)

### If you change public ranks

You must review together:
- [compute.py](/D:/Mathakine/app/services/gamification/compute.py)
- [level_titles.py](/D:/Mathakine/app/services/gamification/level_titles.py)
- [gamification_service.py](/D:/Mathakine/app/services/gamification/gamification_service.py)
- [progressionRankLabel.ts](/D:/Mathakine/frontend/lib/gamification/progressionRankLabel.ts)
- [leaderboard.ts](/D:/Mathakine/frontend/lib/constants/leaderboard.ts)
- [fr.json](/D:/Mathakine/frontend/messages/fr.json)
- [en.json](/D:/Mathakine/frontend/messages/en.json)

You must not:
- change only backend bucket values without updating frontend canonicalization
- change only labels without checking leaderboard/profile/dashboard/badges
- use a per-level title as if it were a bucket label

---

## Testing Checklist

When touching pedagogical difficulty:
- unit tests on tier computation
- unit tests on mastery/diagnostic projection
- boundary/API tests where F42 is exposed
- generation tests proving effective calibration, not only metadata transport

When touching ranks:
- backend tests for point/level/rank computation
- API tests for `/me`, leaderboard, badges
- frontend tests for leaderboard/profile/dashboard visible labels
- no residual public Jedi wording in visible strings

---

## Related References

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [AI_MODEL_GOVERNANCE.md](AI_MODEL_GOVERNANCE.md)
- [GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md](/D:/Mathakine/docs/02-FEATURES/GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md)
- [ROADMAP_FONCTIONNALITES.md](/D:/Mathakine/docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md)

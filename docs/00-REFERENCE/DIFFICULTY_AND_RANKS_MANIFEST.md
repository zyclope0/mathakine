# Difficulty And Ranks Manifest

> Cross-module reference for pedagogical difficulty and public progression ranks
> Updated: 2026-03-28

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

| Domain                      | Canonical concept      | Notes                                                                                                    |
| --------------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------- |
| User profile                | `age_group`            | Persisted user age band used as first-class F42 signal                                                   |
| Pedagogy                    | `pedagogical_band`     | `discovery`, `learning`, `consolidation`                                                                 |
| Pedagogy                    | `difficulty_tier`      | F42 cell `1..12` = age band x pedagogical band                                                           |
| Exercise legacy             | `difficulty`           | Legacy stored string (`INITIE`, `PADAWAN`, `CHEVALIER`, `MAITRE`, `GRAND_MAITRE`) kept for compatibility |
| Challenge public difficulty | `difficulty_rating`    | Public scalar `1.0..5.0` for logic challenges                                                            |
| Exercise progress           | `mastery_level`        | Legacy integer `1..5`, projected into F42 through the bridge                                             |
| Challenge progress          | `mastery_level` string | Legacy string (`novice`, `apprentice`, `adept`, `expert`) projected into F42 through the bridge          |
| Gamification                | `current_level`        | Account level derived from total points                                                                  |
| Gamification                | `jedi_rank`            | Legacy field name kept as transport key for the public rank bucket                                       |
| Gamification UI             | progression rank label | Public label resolved from bucket key, never hard-coded from legacy Jedi wording                         |

### Admin UI — liste exercices (`/admin/content`, FFI-L14)

- **Affichage liste** : ne promeut pas les libellés Star Wars comme vérité produit ; affichage **transitoire** : `Palier n` lorsque `difficulty_tier` est présent sur la ligne liste, sinon niveaux neutres dérivés du legacy `difficulty` (`Niveau 1..5`). Voir `frontend/lib/admin/exercises/adminExerciseCoherence.ts`.
- **Modales édition/création** : conservent les chaînes legacy `ADMIN_DIFFICULTIES` pour compatibilité contrat API actuel.
- **Non-clôture produit** : tant que la **réponse liste admin exercices** n’expose pas de façon **garantie** `difficulty_tier`, l’alignement final sur le canon F42 reste **incomplet** — reliquat **contrat/API + produit**, distinct du découpage frontend.

---

## Source Of Truth Matrix

### Pedagogical difficulty

| Responsibility                           | Source of truth                                                                                       |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Age-group normalization                  | [user_age_group.py](../../app/core/user_age_group.py) and [constants.py](../../app/core/constants.py) |
| Tier formula and content-tier helpers    | [difficulty_tier.py](../../app/core/difficulty_tier.py)                                               |
| Legacy progress/diagnostic -> F42 bridge | [mastery_tier_bridge.py](../../app/core/mastery_tier_bridge.py)                                       |
| Exercise runtime adaptive context        | [adaptive_difficulty_service.py](../../app/services/exercises/adaptive_difficulty_service.py)         |
| Recommendation user context              | [recommendation_user_context.py](../../app/services/recommendation/recommendation_user_context.py)    |
| Challenge AI personalization context     | [challenge_generation_context.py](../../app/services/challenges/challenge_generation_context.py)      |
| Challenge public rating calibration      | [challenge_difficulty_policy.py](../../app/services/challenges/challenge_difficulty_policy.py)        |

### Public progression ranks

| Responsibility                                           | Source of truth                                                                                                                                                        |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Points -> level -> rank bucket formula                   | [compute.py](../../app/services/gamification/compute.py)                                                                                                               |
| Account progression payload (`current`, `jedi_rank`, XP) | [gamification_service.py](../../app/services/gamification/gamification_service.py)                                                                                     |
| Numeric level label (i18n)                               | [LevelIndicator.tsx](../../frontend/components/dashboard/LevelIndicator.tsx) + [fr.json](../../frontend/messages/fr.json) / [en.json](../../frontend/messages/en.json) |
| Frontend bucket canonicalization                         | [progressionRankLabel.ts](../../frontend/lib/gamification/progressionRankLabel.ts)                                                                                     |
| Frontend icons/colors                                    | [leaderboard.ts](../../frontend/lib/constants/leaderboard.ts)                                                                                                          |
| Public translations                                      | [fr.json](../../frontend/messages/fr.json) and [en.json](../../frontend/messages/en.json)                                                                              |

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

- [normalize_age_group(...)](../../app/core/constants.py)
- [normalized_age_group_from_user_profile(...)](../../app/core/user_age_group.py)

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

- [compute_tier_from_bands(...)](../../app/core/difficulty_tier.py)
- [compute_tier_from_age_group_and_band(...)](../../app/core/difficulty_tier.py)

### 4. Legacy stored difficulty

Exercises still persist a legacy `difficulty` string for compatibility.

Current legacy buckets are still interpreted through:

- [pedagogical_band_index_from_difficulty(...)](../../app/core/difficulty_tier.py)

This legacy field is acceptable as a storage/input compatibility layer, but it is no longer the only pedagogical truth.

### 5. Challenge difficulty rating

Logic challenges expose a public `difficulty_rating` on a `1.0..5.0` scale.

This scale is:

- public-facing
- challenge-specific
- not equivalent to account rank

Current calibration is centralized in:

- [calibrate_challenge_difficulty(...)](../../app/services/challenges/challenge_difficulty_policy.py)

---

## Legacy-To-F42 Bridges

### Exercise progress

Legacy storage:

- `Progress.mastery_level` (`1..5`)
- `Progress.difficulty`

Projection source:

- [mastery_level_int_to_pedagogical_band(...)](../../app/core/mastery_tier_bridge.py)
- [mastery_to_tier(...)](../../app/core/mastery_tier_bridge.py)
- [project_exercise_progress_f42(...)](../../app/core/mastery_tier_bridge.py)

Current canonical mapping:

- `1`, `2` -> `discovery`
- `3` -> `learning`
- `4`, `5` -> `consolidation`

### Challenge progress

Legacy storage:

- `ChallengeProgress.mastery_level` string

Projection source:

- [challenge_mastery_string_to_pedagogical_band(...)](../../app/core/mastery_tier_bridge.py)
- [project_challenge_progress_row_f42(...)](../../app/core/mastery_tier_bridge.py)

Current canonical mapping:

- `novice` -> `discovery`
- `apprentice` -> `learning`
- `adept` -> `learning`
- `expert` -> `consolidation`

### Diagnostic

Legacy storage:

- diagnostic score `difficulty`

Projection source:

- [tier_from_diagnostic_difficulty(...)](../../app/core/mastery_tier_bridge.py)
- [enrich_diagnostic_scores_f42(...)](../../app/core/mastery_tier_bridge.py)

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

- [canonical_age_group_from_user(...)](../../app/core/mastery_tier_bridge.py)
- [canonical_age_group_with_fallback(...)](../../app/core/mastery_tier_bridge.py)

Important:

- this fallback is acceptable for compatibility
- it must not silently override a valid explicit age input

---

## Runtime Difficulty Flows

### Exercise generation

Main seams:

- [exercise_generation_service.py](../../app/services/exercises/exercise_generation_service.py)
- [adaptive_difficulty_service.py](../../app/services/exercises/adaptive_difficulty_service.py)
- [difficulty_tier.py](../../app/core/difficulty_tier.py)

Current rule:

- generation may use a stable age-group + a second-axis pedagogical band
- the resulting tier must be computed from the real `(age_group x band)` cell
- if a runtime band override is used, `difficulty_tier` and calibration text must be recomputed accordingly
- if no stronger mastery signal exists, the current neutral fallback band remains `learning`

### Recommendation

Main seam:

- [build_recommendation_user_context(...)](../../app/services/recommendation/recommendation_user_context.py)

Current responsibility:

- resolve user age group
- compute global default legacy difficulty
- expose `target_difficulty_tier`

This is the reusable seam for user-context personalization. New personalization lots should prefer reuse/extraction over duplicating age/tier logic.

### Challenge generation

Main seam:

- [challenge_generation_context.py](../../app/services/challenges/challenge_generation_context.py)

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

- [compute_state_from_total_points(...)](../../app/services/gamification/compute.py)

F42-P4 (piecewise curve): level and XP-in-bracket are derived from `total_points` using tiered per-level costs (`LEVEL_UP_COST_SEGMENTS` in `constants.py`), not a flat 100 points per level. See `cumulative_points_at_level_start`, `level_and_xp_from_total_points`, and `points_to_gain_next_level` in `compute.py`.

Legacy reference: `POINTS_PER_LEVEL_LEGACY = 100` (old linear model); level math no longer uses it.

### Current rank buckets

Current bucket computation is centralized in:

- [jedi_rank_for_level(...)](../../app/services/gamification/compute.py)

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

### Account level display (F42-P5)

- Public **rank** is the progression bucket: `jedi_rank` (canonical key) + UI translations.
- The **numeric level** is `gamification_level.current`; the visible label « Niveau n » / « Level n » is **client i18n** (no per-level narrative table in the API).

---

## Public Read Boundaries

### Difficulty / progress

Current additive F42 boundaries include:

- diagnostic projection
- user progress by category
- challenge detailed progress

Reference seams:

- [mastery_tier_bridge.py](../../app/core/mastery_tier_bridge.py)
- [user_service.py](../../app/services/users/user_service.py)
- [challenge_progress.py](../../app/schemas/challenge_progress.py)

### Account progression / ranks

Current public read surfaces include:

- `GET /api/users/me`
- `GET /api/users/leaderboard`
- `GET /api/badges/stats`
- `GET /api/badges/user`
- `GET /api/admin/observability/f43-account-progression` (read-only admin cohort snapshot recomputed from `total_points`)

Reference doc:

- [GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md](../../docs/02-FEATURES/GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md)

### Observability (post-F42)

Current minimal observability seams include:

- structured log `f43_exercise_attempt` for exercise submit outcomes by `difficulty_tier`
- structured log `f43_adaptive_context` for adaptive context resolution (`mastery_source`, `pedagogical_band`)
- read-only admin cohort snapshot for account progression derived from `total_points`

These seams are for measurement and validation only. They must not become a second source of pedagogical truth.

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

- [difficulty_tier.py](../../app/core/difficulty_tier.py)
- [mastery_tier_bridge.py](../../app/core/mastery_tier_bridge.py)
- [recommendation_user_context.py](../../app/services/recommendation/recommendation_user_context.py)
- exercise/challenge runtime contexts that consume F42

You must not:

- add a second mastery -> band mapping elsewhere
- introduce a new age-group fallback order in a random service
- let explicit age input be silently overwritten by a profile fallback

### If you change challenge difficulty calibration

You must review together:

- [challenge_generation_context.py](../../app/services/challenges/challenge_generation_context.py)
- [challenge_difficulty_policy.py](../../app/services/challenges/challenge_difficulty_policy.py)
- [challenge_ai_service.py](../../app/services/challenges/challenge_ai_service.py)

### If you change public ranks

You must review together:

- [compute.py](../../app/services/gamification/compute.py)
- [gamification_service.py](../../app/services/gamification/gamification_service.py)
- [progressionRankLabel.ts](../../frontend/lib/gamification/progressionRankLabel.ts)
- [leaderboard.ts](../../frontend/lib/constants/leaderboard.ts)
- [fr.json](../../frontend/messages/fr.json)
- [en.json](../../frontend/messages/en.json)

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
- [GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md](../../docs/02-FEATURES/GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md)
- [ROADMAP_FONCTIONNALITES.md](../../docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md)

# R7 — Closure / governance — Recommendation iteration `R` (R1–R6)

> **Date** : 2026-03-21  
> **Type** : **doc-only closure** (no runtime, frontend, API, or migration changes in this lot).  
> **Purpose** : consolidate what iteration **R** actually proved, what it does **not** claim, and honest residual reservations — without rebranding the engine as “ML” or “fully intelligent.”

---

## Validated Recommendation Baseline

Cited as the **last validated closure state** for iteration **R** (recommendations). Re-run commands locally if the tree has diverged.

| Layer | Command / check | Result (closure citation) |
|--------|------------------|----------------------------|
| Reco targeted | `python -m pytest -q tests/unit/test_recommendation_service.py tests/api/test_recommendation_endpoints.py --maxfail=20 --no-cov` | **40 passed** |
| Full gate | `python -m pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` | **991 passed, 2 skipped** |
| Vitest (reasons UI) | `npm exec vitest run __tests__/unit/hooks/useRecommendationsReason.test.ts` (from `frontend/`) | **3 passed** |
| Frontend | `npm run lint`, `npm run format:check`, `npm run build` | **green** |
| Backend quality | `black app/ server/ tests/ --check`, `isort app/ server/ tests/ --check-only`, `mypy app/ server/ --ignore-missing-imports`, `flake8 app/ server/ --select=E9,F63,F7,F82` | **green** |

**Ultimate truth** remains: **`app/services/recommendation/`** + **`server/handlers/recommendation_handlers.py`** + tests above.

---

## What R Proved

| Lot | What is demonstrably true (with tests / code) |
|-----|-----------------------------------------------|
| **R1** | Canonical **`exercise_type`** normalization is used consistently in recommendation paths (`normalize_exercise_type_key`); casing / enum variants do not split user state incorrectly (e.g. discovery vs Progress). |
| **R2** | **`RecommendationUserContext`** + **`get_target_difficulty_for_type`**: per-type diagnostic (when present) and global default feed exercise targeting; not a black-box tuple. |
| **R3** | For **improvement, progression, reactivation, fallback** (at R3 close): bounded pool + **deterministic Python ranking** + **14-day anti-repeat** on exercise recommendations; **`func.random()`** removed from those exercise selection paths. *(Discovery was initially an exception; see R6.)* |
| **R4 / R4b** | **Feedback lifecycle** wired: list impression (`shown_count`), open intent (`clicked_count` / `last_clicked_at` via `recordOpen`), manual complete + **`verified_by_attempt`** correlation; **QuickStartActions** records open only for **guided** CTAs to a specific reco. |
| **R5** | **Challenge** recommendations: explicit scoring (profiles, bounded formula), **`reason_code` / `reason_params`**, EN **`reason`** fallback; no dominant `ORDER BY random()` for challenge pick. |
| **R5b** | **GET** list filters inactive/archived/missing challenges like generation (stale challenge rows hidden). |
| **R5c** | ORM hygiene after bulk delete of incomplete recos: **`synchronize_session=False`** + **`set_committed_value`** on `user.recommendations` to avoid **`ObjectDeletedError`** / session drift in tests and long-lived sessions. |
| **R5d** | Test **cleanup** aligned on **`app.db.base.engine`**, two-phase commit for test data cleanup, catch-all child deletes, **`pytest.fail`** on failed cleanup — **stability** of reco test battery (infra, not product logic). |
| **R6** | **Discovery** integrated into the **same explicit pipeline** as other exercise branches: per–new-type loop, bounded pool, **`select_top_ranked_exercises`** + extended penalized set; **exercise** rows carry **`reason_code` / `reason_params`** with **next-intl** on the dashboard; FR product copy is no longer the primary source of truth for those reasons. |

---

## What R Still Does Not Claim

- **Not** a full **behavioural learning** or **ML** recommender: no online model training, no bandits, no long-horizon reward optimization.
- **`practice_rhythm`** (and similar profile fields) are **not** drivers of ranking in this iteration — storage / onboarding may exist without being consumed by the engine.
- **Auto-completion** of recommendations when the user finishes an exercise **outside** the reco CTA flow is **out of scope** (R4 documented this explicitly).
- **Challenge scoring** is **heuristic and bounded** (`difficulty_rating` often partial); not a psychometric or IRT engine for challenges.
- **No academic-grade cross-content ranking** (exercises vs challenges as a single optimiser): mix rules in API are pragmatic caps, not a unified score.
- **`shown_count`** is “times this row appeared in a GET list response,” not a strict unique user impression metric.
- **Global optimality** within **`MAX_CANDIDATES_TO_RANK`**: candidates outside the last N ids by type are invisible to Python ranking.

---

## Residual Recommendation Reservations

| # | Reservation | Status |
|---|-------------|--------|
| 1 | **Bounded candidate window** (`MAX_CANDIDATES_TO_RANK`) for Python-ranked branches | **Open** — by design trade-off. |
| 2 | **`practice_rhythm` / rhythm-aware scheduling** | **Open** — not consumed by recommendation service in R. |
| 3 | **Post-completion auto reco refresh** (everywhere) | **Open** — R4 scope was minimal lifecycle + honest limits. |
| 4 | **Challenge** side: richer models, content embeddings, A/B, true diversity metrics | **Open** — R5 improved heuristics only. |
| 5 | **Duplicate intent** risk between **maintenance** (no recent attempt) and **discovery** (no Progress on type) for the same type | **Open** — acknowledged as possible edge; not closed in R. |
| 6 | **Discovery = one query per new type** (R6) | **Open** — acceptable N small; watch if catalogue explodes. |
| 7 | R3 **historical** doc (clôture 2026-03-20) described discovery **without** Python ranking | **Resolved in doc** — supersession note points to **R6** + this R7 doc; keep R3 file for R3-era traceability. |

---

## Recommendation Maturity Verdict

**Maturity level (honest):** **“Deterministic heuristic recommender v2”** — improved **stability**, **traceable rules**, **structured reasons (i18n)**, **minimal feedback loop**, and **test-backed** behaviour on the exercised paths.  

It is **not** “intelligent” in the sense of learned personalization from all user actions, nor “complete” relative to every profile field or product dream.  

**Iteration `R` is closed** as an engineering iteration: scope was **bounded remediation + documentation truth**, not a greenfield reco platform.

---

## Recommended Next Candidates

1. **Product decision**: whether to consume **`practice_rhythm`** (and related onboarding fields) in ranking or copy — only with a small, testable lot.
2. **Optional**: narrow lot to reduce **maintenance vs discovery** overlap for “cold” types (if product reproduces pain).
3. **Optional**: **observability** — lightweight metrics on reco branch counts / empty fallbacks (no refactor of the engine).
4. **Continue** non-reco backlog per **`POINTS_RESTANTS_2026-03-15.md`** (handlers, diagnostic hotspots, etc.) — **separate** from iteration R.

---

## Traceability index (iteration R)

| Doc | Role |
|-----|------|
| [CLOTURE_LOT_R3_REMEDIATION_MOTEUR_RECOMMANDATIONS_EXERCICE_2026-03-20.md](./CLOTURE_LOT_R3_REMEDIATION_MOTEUR_RECOMMANDATIONS_EXERCICE_2026-03-20.md) | R3 + R3b truth **at 2026-03-20**; **discovery section superseded** by R6 (banner in file). |
| [RECOMMENDATION_FEEDBACK_LIFECYCLE_R4_2026-03-20.md](./RECOMMENDATION_FEEDBACK_LIFECYCLE_R4_2026-03-20.md) | R4 / R4b lifecycle + UI wiring. |
| [RECOMMENDATION_R5_CHALLENGE_REASON_I18N_2026-03-20.md](./RECOMMENDATION_R5_CHALLENGE_REASON_I18N_2026-03-20.md) | R5–R5d challenge reasons, API, ORM, test infra. |
| [RECOMMENDATION_R6_EXERCISE_DISCOVERY_AND_REASONS_2026-03-21.md](./RECOMMENDATION_R6_EXERCISE_DISCOVERY_AND_REASONS_2026-03-21.md) | R6 discovery pipeline + exercise `reason_code`. |
| **This file** | **R7** closure and governance. |

---

## What R7 Proved

- **Documentary alignment** between historical R3 closure text, post-R6 code, tracker (**`POINTS_RESTANTS`**), and index entries.
- **Explicit** list of **non-claims** and **residual reservations** so future work does not inherit false marketing.

## What R7 Did Not Prove

- No new **runtime** behaviour (this lot is **doc-only**).
- No improvement to **ranking quality** beyond what R1–R6 already shipped.

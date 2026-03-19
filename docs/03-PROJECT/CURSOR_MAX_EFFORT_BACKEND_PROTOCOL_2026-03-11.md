# Cursor Max Effort Backend Protocol

> Date: 11/03/2026
> Status: evergreen reference protocol
> Goal: provide one quality-first validation protocol for backend lots.

## Principle

A backend lot is valid only if four things are true at the same time:

1. touched code has been reviewed factually
2. real wiring has been verified
3. checks are reproducible
4. touched endpoints or runtime paths are explicitly proven

A lot is never `GO` only because one green suite happened once.

## Known False Gate

The following file must not be used as a standard validation gate while it launches `pytest` from `pytest` with coverage:

- `tests/api/test_admin_auth_stability.py`

## Validation Standard

Each lot must explicitly distinguish:
- modified runtime files
- modified test files
- real touched endpoints or runtime paths
- what was proven
- what was not proven
- residual risks

### Standard Gate

1. `git status --short`
2. `git diff --name-only`
3. `run 1` of the target battery
4. `run 2` of the same battery
5. `full suite` if runtime changed
6. `black app/ server/ tests/ --check`
7. `isort app/ server/ tests/ --check-only --diff` if the lot touches backend Python

## Verdict Rules

- `GO` only if green is reproducible
- `NO-GO` if `run 2` fails
- `NO-GO` if touched code was not reviewed factually
- `NO-GO` if touched runtime paths were not listed
- `NO-GO` if the report concludes without distinguishing runtime and tests

## Anti-Loop Rule

When the same symptom comes back across multiple turns, do not continue indefinitely with micro-fixes without new proof.

Mandatory rule:
1. on first failure: diagnose and correct if the cause is proven
2. on second failure for the same symptom: re-check the current tree, verify whether the lot is really in cause, verify false gates and environment
3. on third turn without new causality: STOP, produce a diagnosis/scoping note, then re-qualify the problem

## Pre-Verdict Verification

Before concluding `GO` or `NO-GO`, verify:

1. the truth of the current tree
2. the validity of the proof environment
3. the difference between a scope problem and baseline noise

### Proof Environment

Always verify:
- database availability
- known false gate or not
- `.coverage` contention, Windows locks, accidental parallelism
- concurrent execution of multiple `pytest` commands with coverage

Explicit rule:
- on Windows, do not launch multiple `pytest` commands with `pytest-cov` in parallel
- a `.coverage` lock is a tooling false positive as long as there is no associated business failure
- that tooling false positive must not be confused with a runtime failure

## Mandatory Causal Attribution

Each observed failure must be classified in only one category:
1. runtime regression of the lot
2. pre-existing baseline noise
3. false gate or invalid test harness
4. environment problem
5. unproven hypothesis

Rules:
- never attribute a failure to a lot without explicit causal linkage
- never use an out-of-scope failure as sufficient proof against the lot
- if a failure comes from a false gate, mark it as such and exclude it from the decision
- if a failure comes from an environment problem, conclude `NO-GO environment`, not `NO-GO runtime`

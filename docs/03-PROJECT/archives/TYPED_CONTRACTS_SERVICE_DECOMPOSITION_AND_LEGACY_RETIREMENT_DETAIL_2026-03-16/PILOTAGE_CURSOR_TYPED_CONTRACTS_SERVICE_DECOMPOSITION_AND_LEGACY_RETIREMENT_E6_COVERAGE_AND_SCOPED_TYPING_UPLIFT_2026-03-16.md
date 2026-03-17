# Lot E6 - Coverage and Scoped Typing Uplift

> Iteration `E`
> Status: done

## Problem To Solve

The backend now has a stable quality floor, but the proof margin remains modest:
- coverage gate at `63 %`
- global strict typing still out of scope

The point of `E6` is to consolidate the structural work done by `E1` to `E5`, not to start a blind metrics chase.

## Scope

Primary targets:
- tests around modules changed in `E1` to `E5`
- scoped typing hardening around newly clarified seams

Allowed support scope:
- `mypy` configuration only if the change is clearly bounded and causally justified

Out of scope:
- global strict `mypy`
- arbitrary coverage inflation on untouched modules
- CI gate raise without proof first

## Required Outcome

- stronger test proof on the structural hotspots actually treated by iteration `E`
- cleaner scoped typing where the new seams justify it
- evidence for or against a future CI gate increase

## Recommended Strategy

- prioritize branch-heavy business paths touched by earlier lots
- add proof only where the structural work created cleaner seams
- decide on a future coverage-gate increase only after measurement

## Validation Expectation

- targeted tests twice
- full backend suite
- `black`, `isort`, and scoped `mypy` checks where relevant

## GO / NO-GO

GO:
- better proof on changed hotspots
- scoped typing improvements that stick

NO-GO:
- vanity coverage work
- `mypy` tightening that floods the codebase outside the treated scope

## E6 Result (2026-03-16)

### Seams renforcés
- **E4 badge_requirement_validation** : 8 tests ajoutés (consecutive_correct, max_time, consecutive_days, comeback_days — valid + invalid)
- **E5 db_utils** : 2 tests ajoutés (sync_db_session yields session, rollback on exception)

### Preuves ajoutées
- Couverture exhaustive des branches de validation badge (types précédemment non testés)
- Preuve directe que sync_db_session fournit une session utilisable et gère les exceptions

### Gate coverage
- **Recommandation** : Gate 63 % conservé. La mesure locale donne 71 % ; une hausse à 64 % serait techniquement défendable mais E6 n'a pas pour objectif de prouver une hausse de gate — les tests ajoutés prouvent des seams E4/E5, pas une hausse de couverture globale.

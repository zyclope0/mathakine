# Academic Backend Rigor, Replicability, and Operability - Detailed Archive

> Iteration `F`
> Closed: 17/03/2026

## Scope

Detailed execution notes for iteration `F`, whose purpose was to push the backend toward a more defensible state on:
- internal contract rigor
- hotspot decomposition
- scoped typing discipline
- runtime/data boundary formalization
- replicability and operability truth

## Archived Documents

| Document | Role |
|---|---|
| [PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_2026-03-16.md](./PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_2026-03-16.md) | master plan and iteration rules |
| [PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F1_RESIDUAL_WEAK_CONTRACTS_ELIMINATION_2026-03-16.md](./PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F1_RESIDUAL_WEAK_CONTRACTS_ELIMINATION_2026-03-16.md) | residual auth weak-contract elimination |
| [PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F2_BADGE_REQUIREMENT_ENGINE_REAL_DECOMPOSITION_2026-03-16.md](./PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F2_BADGE_REQUIREMENT_ENGINE_REAL_DECOMPOSITION_2026-03-16.md) | badge requirement engine volume-cluster decomposition |
| [PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F3_ADMIN_CONTENT_MUTATION_BOUNDARY_CLEANUP_2026-03-16.md](./PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F3_ADMIN_CONTENT_MUTATION_BOUNDARY_CLEANUP_2026-03-16.md) | admin badge create-flow decomposition |
| [PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F4_SCOPED_STRICT_TYPING_UPGRADE_2026-03-16.md](./PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F4_SCOPED_STRICT_TYPING_UPGRADE_2026-03-16.md) | scoped typing uplift on the admin badge seam |
| [PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F5_RUNTIME_DATA_BOUNDARY_FORMALIZATION_2026-03-16.md](./PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F5_RUNTIME_DATA_BOUNDARY_FORMALIZATION_2026-03-16.md) | runtime/data boundary formalization |
| [PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F6_REPLICABILITY_AND_OPERABILITY_CLOSURE_2026-03-16.md](./PILOTAGE_CURSOR_ACADEMIC_BACKEND_RIGOR_REPLICABILITY_AND_OPERABILITY_F6_REPLICABILITY_AND_OPERABILITY_CLOSURE_2026-03-16.md) | iteration closure, proved scope, and invariants |

## Final Verified Baseline

Iteration `F` closed with the following verified local reference:
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov` -> `936 passed, 2 skipped`
- `black app/ server/ tests/ --check` -> green
- `isort app/ server/ tests/ --check-only --diff` -> green
- `mypy app/ server/ --ignore-missing-imports` -> green
- `flake8 app/ server/ --select=E9,F63,F7,F82` -> green
- backend CI coverage gate -> `63 %`

## Active Sources Of Truth

This archive is traceability only.

For the current state, read:
- [../../POINTS_RESTANTS_2026-03-15.md](../../POINTS_RESTANTS_2026-03-15.md)
- [../../README.md](../../README.md)
- [../../../README_TECH.md](../../../README_TECH.md)
- [../../../INDEX.md](../../../INDEX.md)

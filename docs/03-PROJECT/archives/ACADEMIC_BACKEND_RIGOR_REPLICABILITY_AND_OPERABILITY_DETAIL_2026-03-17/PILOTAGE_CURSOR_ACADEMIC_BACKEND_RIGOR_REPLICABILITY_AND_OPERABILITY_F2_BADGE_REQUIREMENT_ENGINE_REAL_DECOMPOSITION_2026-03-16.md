# Lot F2 - Badge Requirement Engine Real Decomposition

> Iteration `F`
> Status: done

## Mission

Decompose a real cluster inside `badge_requirement_engine.py` by business responsibility, not by cosmetic helper extraction.

## Cluster Chosen

**Cluster attempts/volume** : `attempts_count`, `logic_attempts_count`, `mixte`

## Delivered

- `app/services/badge_requirement_volume.py` : checkers et progress getters du cluster
- Réduction de densité dans `badge_requirement_engine.py` (~110 lignes extraites)
- Logique partagée : `_make_count_checker`, `_make_count_progress` (count >= target, progression min(1,c/t))
- Tests dédiés : `tests/unit/test_badge_requirement_volume.py`

## Success Criteria

- visible reduction of density inside `badge_requirement_engine.py` ✓
- clearer grouping by business responsibility ✓
- stronger local tests ✓

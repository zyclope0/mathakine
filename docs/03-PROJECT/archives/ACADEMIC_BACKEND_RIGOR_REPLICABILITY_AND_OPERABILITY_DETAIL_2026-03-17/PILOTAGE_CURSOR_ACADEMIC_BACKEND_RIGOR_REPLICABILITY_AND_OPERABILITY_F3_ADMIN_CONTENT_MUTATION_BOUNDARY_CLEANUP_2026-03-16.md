# Lot F3 - Admin Content Mutation Boundary Cleanup

> Iteration `F`
> Status: done

## Mission

Decompose one dense admin-content mutation flow into explicit preparation, validation, persistence, and result mapping responsibilities.

## Flux Choisi

**create_badge_for_admin** — création d'un badge admin.

## Étapes Séparées

1. **Préparation** : `prepare_badge_create_data(data)` — normalisation code, name, champs optionnels
2. **Validation** : `validate_badge_create_pre_persist(prepared, db)` — champs requis, requirements (E4), unicité code
3. **Persistance** : `persist_badge_create(db, prepared, admin_user_id)` — création Achievement, log, commit
4. **Mapping** : `_achievement_to_detail(a)` — reste dans admin_content_service

## Délivré

- `app/services/admin_badge_create_flow.py`
- `create_badge_for_admin` réduit à ~10 lignes d'orchestration
- Tests : `tests/unit/test_admin_badge_create_flow.py`

## Success Criteria

- less inline mixed logic ✓
- cleaner mutation boundaries ✓
- unchanged external HTTP behavior ✓

## F3b — Gate formatting

- `black --check` : vert (test_admin_badge_create_flow.py formaté)
- full suite : 925 passed, 2 skipped

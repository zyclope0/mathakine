# Lot F4 - Scoped Strict Typing Upgrade

> Iteration `F`
> Status: done (2026-03-17)

## Mission

Push a bounded stricter typing discipline on the seams clarified by `E` and early `F`, without opening a global strict-mypy rewrite.

## Priority Targets

- modules clarified by `E1`, `E3b`, `E4`, and `F1` to `F3`

## Success Criteria

- stricter typed sub-scope with real proof
- no broad typing campaign without local gain

## Réalisation (2026-03-17)

**Sous-scope choisi** : seam admin badge create (`admin_badge_create_flow.py`, F3)

**Faiblesses traitées** :
- `Dict[str, Any]` pour les données préparées entre prepare → validate → persist
- `Tuple[Optional[str], int]` non documenté pour le résultat de validation

**Types renforcés** :
- `BadgeCreatePrepared` (TypedDict) dans `app/core/types.py` — structure fixe des données normalisées
- `ValidationResult` (alias) — `Tuple[Optional[str], int]` pour (error_message, status_code)
- Signatures : `prepare_badge_create_data(...) -> BadgeCreatePrepared`, `validate_badge_create_pre_persist(prepared: BadgeCreatePrepared, ...) -> ValidationResult`, `persist_badge_create(..., prepared: BadgeCreatePrepared, ...) -> Achievement`

**Hors scope** : seam auth, seam badge volume/validation — non modifiés.

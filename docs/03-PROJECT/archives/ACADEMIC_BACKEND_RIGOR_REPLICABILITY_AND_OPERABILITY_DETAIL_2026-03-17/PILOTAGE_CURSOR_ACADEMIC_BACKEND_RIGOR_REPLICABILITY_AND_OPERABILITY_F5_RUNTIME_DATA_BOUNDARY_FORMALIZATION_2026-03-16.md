# Lot F5 - Runtime Data Boundary Formalization

> Iteration `F`
> Status: done (2026-03-17)

## Mission

Clarify and tighten the active runtime/data boundary where the backend still feels pragmatic rather than explicit.

## Priority Targets

- bounded active seams between service orchestration and DB/session handling

## Success Criteria

- clearer runtime/data story
- less architectural ambiguity
- no repository-pattern rewrite

## Réalisation (2026-03-17)

**Seam choisi** : run_db_bound / sync_db_session (boundary handler → runtime → data)

**Ambiguïté initiale** : Le contrat était dispersé (runtime.py, db_utils.py, docstrings services). pas de référence canonique unique.

**Formalisation retenue** :
- `app/core/db_boundary.py` : module canonique avec contrat explicite, re-exports run_db_bound et sync_db_session, type alias DbBoundSyncCallable
- Cross-références dans runtime.py et db_utils.py
- Test `test_run_db_bound_with_sync_db_session_chain` prouvant la chaîne active
- Mise à jour ARCHITECTURE.md et README_TECH

**Hors scope** : enhanced_server_adapter, seam data dans F3/F4, changement des imports handlers.

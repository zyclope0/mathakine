# Lot 4 - Admin read boundary - 2026-03-10

## Mission
Rendre les handlers admin read-only beaucoup plus minces, sans toucher encore les mutations lourdes de contenu.

## Analyse actuelle
- `server/handlers/admin_handlers.py` ouvre directement `db_session` pour `overview`, `users`, `health`, `config get`, `reports`, `moderation`, `audit-log`, `ai-stats`, `generation-metrics`.
- `AdminService` est deja une facade, mais les handlers gardent l'ouverture DB et une partie du wiring query/pagination.

## Ce qui est mal place
- `async with db_session()` dans les handlers admin read
- orchestration pagination/filtres/wiring AdminService dans les handlers

## Ce qui est duplique
- pattern read-only admin repete sur plusieurs routes
- ouverture/fermeture de session repetees

## Decoupage cible
- creer `app/services/admin_application_service.py`
- ajouter `app/schemas/admin.py` seulement si des schemas query simples apportent un vrai gain
- laisser `AdminService` comme facade metier sous-jacente

## Fichiers a lire avant toute modification
- `server/handlers/admin_handlers.py`
- `server/handlers/admin_list_params.py`
- `app/services/admin_service.py`
- `app/services/admin_stats_service.py`
- `app/services/admin_user_service.py`
- `tests/api/test_admin_analytics.py`
- `tests/api/test_admin_ai_stats.py`
- `tests/api/test_admin_users_delete.py`

## Fichiers autorises
- `server/handlers/admin_handlers.py`
- `server/handlers/admin_list_params.py`
- `app/services/admin_application_service.py`
- `app/schemas/admin.py` si necessaire
- tests admin cibles si ajustement minimal necessaire

## Fichiers explicitement hors scope
- mutations admin `users/config`
- CRUD admin `exercises/challenges/badges`
- `badge`
- `challenge`

## Actions precises a effectuer
- sortir la lecture admin dans une facade applicative qui possede `db_session`
- reduire les handlers read a parse/call/JSONResponse
- ne pas changer les routes ni les payloads admin existants
- preparer une base saine pour les lots 5 et 6 sans re-ecrire `AdminService`

## Checks a lancer
- `pytest -q tests/api/test_admin_analytics.py tests/api/test_admin_ai_stats.py tests/api/test_admin_users_delete.py --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- si le lot force a toucher les mutations admin
- si une facade admin appliquee cree un doublon confus avec `AdminService`
- si le contrat read admin devrait changer

## Definition of Done
- plus de `db_session` direct dans les handlers admin du scope lot 4
- wiring query/read absorbe par une couche applicative
- tests read admin cibles verts

## Format de compte-rendu final
1. fichiers modifies
2. ce qui a ete sorti des handlers
3. nouveau decoupage service/schema
4. preuve que le contrat HTTP n'a pas change
5. checks executes et resultat
6. risques residuels
7. recommendation go / no-go pour le lot 5

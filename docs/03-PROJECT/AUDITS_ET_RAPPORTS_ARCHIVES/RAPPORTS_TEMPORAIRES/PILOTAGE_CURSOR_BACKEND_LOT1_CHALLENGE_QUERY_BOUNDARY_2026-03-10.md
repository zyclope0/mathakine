# Lot 1 - Challenge query boundary - 2026-03-10

## Mission
Rendre anemiques les handlers de lecture `challenge` sans toucher la soumission ni le stream IA.

## Analyse actuelle
- `server/handlers/challenge_handlers.py` ouvre directement `db_session` pour `get_challenges_list`, `get_challenge`, `get_challenge_hint`, `get_completed_challenges_ids`.
- Le handler combine parsing, locale, filtres, appels de services SQLAlchemy et formatage de reponse.
- `challenge_service.py` porte deja une partie de la logique query, mais elle est appelee directement depuis le handler.

## Ce qui est mal place
- acces DB direct dans les handlers
- logique de lecture et de filtrage dans les handlers
- resolution de hints et completed ids encore au niveau HTTP

## Ce qui est duplique
- lecture user/locale
- gestion des filtres et du format de reponse pagine
- pattern `async with db_session()` repete dans plusieurs routes challenge

## Decoupage cible
- creer `app/services/challenge_query_service.py`
- ajouter des schemas query dans `app/schemas/logic_challenge.py` si necessaire (`ChallengeListQuery`, `ChallengeHintQuery`)
- laisser `server/handlers/challenge_list_params.py` seulement comme compat si sa suppression elargit trop le diff

## Fichiers a lire avant toute modification
- `server/handlers/challenge_handlers.py`
- `server/handlers/challenge_list_params.py`
- `app/services/challenge_service.py`
- `app/services/logic_challenge_service.py`
- `app/schemas/logic_challenge.py`
- `tests/api/test_challenge_endpoints.py`
- `tests/api/test_challenges_flow.py`

## Fichiers autorises
- `server/handlers/challenge_handlers.py`
- `server/handlers/challenge_list_params.py`
- `app/services/challenge_query_service.py`
- `app/schemas/logic_challenge.py`
- tests challenge cibles si ajustement minimal necessaire

## Fichiers explicitement hors scope
- `submit_challenge_answer`
- `generate_ai_challenge_stream`
- `challenge_validator.py`
- `admin`
- `badge`

## Actions precises a effectuer
- sortir la lecture de liste, detail, hints et completed ids dans `challenge_query_service.py`
- faire porter au service la DB, les appels `challenge_service` et les transformations de sortie
- faire du handler un simple parse/validation/call/mapping
- conserver les routes, les payloads et les erreurs visibles

## Checks a lancer
- `pytest -q tests/api/test_challenge_endpoints.py tests/api/test_challenges_flow.py tests/unit/test_logic_challenge_service.py --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- si le lot force a toucher `submit_challenge_answer`
- si le lot force a toucher `generate_ai_challenge_stream`
- si le lot revele un arbitrage produit sur le contrat des hints ou du listing

## Definition of Done
- plus aucun `db_session` direct dans les handlers du scope lot 1
- query challenge sortie des handlers du scope
- tests cibles verts

## Format de compte-rendu final
1. fichiers modifies
2. ce qui a ete sorti des handlers
3. nouveau decoupage service/schema
4. preuve que le contrat HTTP n'a pas change
5. checks executes et resultat
6. risques residuels
7. recommendation go / no-go pour le lot 2

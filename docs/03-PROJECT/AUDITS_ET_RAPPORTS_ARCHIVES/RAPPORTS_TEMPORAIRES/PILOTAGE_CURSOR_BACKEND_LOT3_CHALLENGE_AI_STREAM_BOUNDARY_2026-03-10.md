# Lot 3 - Challenge AI stream boundary - 2026-03-10

## Mission
Sortir du handler `challenge` la preparation metier du flux SSE IA, sans rouvrir le coeur de `challenge_validator.py`.

## Analyse actuelle
- `generate_ai_challenge_stream` combine lecture request, prompt, locale, contexte user, choix age_group/difficulty et appel du stream.
- `challenge_ai_service.py` est deja lourd; le handler ne doit plus porter sa preparation metier.
- `challenge_validator.py` est un hotspot connu, mais pas le bon premier lot pour un grand refactor interne.

## Ce qui est mal place
- validation de prompt et preparation de contexte stream dans le handler
- resolution de parametres metier dans la couche HTTP

## Ce qui est duplique
- pattern similaire a celui ferme sur `exercise` avant cloture du lot 3 precedent
- preparation `Accept-Language`/locale/user scopee au handler alors qu'elle sert la logique metier du stream

## Decoupage cible
- creer `app/services/challenge_stream_service.py`
- ajouter si utile un schema `GenerateChallengeStreamQuery` dans `app/schemas/logic_challenge.py`
- conserver `StreamingResponse` et headers SSE dans le handler

## Fichiers a lire avant toute modification
- `server/handlers/challenge_handlers.py`
- `app/services/challenge_ai_service.py`
- `app/services/challenge_validator.py`
- `app/schemas/logic_challenge.py`
- `tests/api/test_challenge_endpoints.py`
- `tests/api/test_challenges_flow.py`

## Fichiers autorises
- `server/handlers/challenge_handlers.py`
- `app/services/challenge_stream_service.py`
- `app/schemas/logic_challenge.py`
- `app/services/challenge_ai_service.py` seulement si adaptation minimale necessaire
- tests challenge cibles si necessaire

## Fichiers explicitement hors scope
- refactor interne de `challenge_validator.py`
- query challenge du lot 1
- attempt challenge du lot 2
- `admin`
- `badge`

## Actions precises a effectuer
- sortir la preparation metier du flux SSE dans `challenge_stream_service.py`
- laisser au handler: lecture request, auth, `StreamingResponse`, headers SSE
- ne pas changer les messages SSE exposes ni les routes
- documenter explicitement le reliquat `challenge_validator.py` si le lot le touche seulement indirectement

## Checks a lancer
- `pytest -q tests/api/test_challenge_endpoints.py tests/api/test_challenges_flow.py --maxfail=20`
- `pytest -q --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- si le lot ouvre un grand chantier dans `challenge_validator.py`
- si le contrat SSE devrait changer
- si le lot force a toucher `admin` ou `badge`

## Definition of Done
- plus de preparation metier SSE dans le handler du scope
- contrat SSE inchange
- suite backend complete verte

## Format de compte-rendu final
1. fichiers modifies
2. ce qui a ete sorti du handler
3. nouveau decoupage service/schema
4. preuve que le contrat SSE n'a pas change
5. checks executes et resultat
6. risques residuels
7. recommendation go / no-go pour le lot 4

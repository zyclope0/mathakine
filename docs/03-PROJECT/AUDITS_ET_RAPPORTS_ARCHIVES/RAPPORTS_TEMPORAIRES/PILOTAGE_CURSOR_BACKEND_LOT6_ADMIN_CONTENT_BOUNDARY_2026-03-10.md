# Lot 6 - Admin content boundary - 2026-03-10

## Mission
Rendre les handlers admin de contenu plus minces sur `exercises`, `challenges`, `badges` et `export`, sans re-ecrire les sous-services admin.

## Analyse actuelle
- `server/handlers/admin_handlers.py` pilote encore directement les CRUD de contenu et ouvre la DB pour de nombreux endpoints.
- `AdminContentService` existe deja mais reste appele via le handler avec une forte orchestration HTTP autour.
- ce lot est a haut risque de debordement; il doit donc etre borne tres strictement.

## Ce qui est mal place
- acces DB direct dans les handlers de contenu admin
- orchestration create/put/patch/delete/duplicate/export dans la couche HTTP

## Ce qui est duplique
- pattern body parse + `AdminService.*_for_admin`
- recuperation repetitive de `admin_id`

## Decoupage cible
- etendre `app/services/admin_application_service.py` pour les operations contenu
- eventuellement ajouter `app/schemas/admin.py` si des payloads admin gagnent une validation claire sans changer le contrat

## Fichiers a lire avant toute modification
- `server/handlers/admin_handlers.py`
- `app/services/admin_service.py`
- `app/services/admin_content_service.py`
- `tests/api/test_admin_badges.py`
- `tests/api/test_challenge_endpoints.py`
- `tests/api/test_exercise_endpoints.py`

## Fichiers autorises
- `server/handlers/admin_handlers.py`
- `app/services/admin_application_service.py`
- `app/schemas/admin.py` si necessaire
- tests admin cibles si ajustement minimal necessaire

## Fichiers explicitement hors scope
- `challenge_validator.py`
- refactor interne de `AdminContentService`
- domaines `auth`, `exercise`, `user` hors admin

## Actions precises a effectuer
- sortir les CRUD admin de contenu et export dans la facade applicative
- garder les handlers a parse/call/JSONResponse/StreamingResponse selon le cas
- ne pas changer les endpoints ni les payloads exposes
- si l'export CSV demande un traitement HTTP specifique, ne sortir que la preparation metier et conserver le streaming HTTP cote handler

## Checks a lancer
- `pytest -q tests/api/test_admin_badges.py tests/api/test_challenge_endpoints.py tests/api/test_exercise_endpoints.py --maxfail=20`
- `pytest -q --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- si le lot force a re-ecrire `AdminContentService`
- si le lot ouvre des changements de contrat admin
- si l'export CSV impose un redesign non borne

## Definition of Done
- handlers admin de contenu du scope sans `db_session` direct
- export et CRUD mieux separes entre HTTP et orchestration
- suite backend complete verte

## Format de compte-rendu final
1. fichiers modifies
2. ce qui a ete sorti des handlers
3. nouveau decoupage service/schema
4. preuve que le contrat HTTP n'a pas change
5. checks executes et resultat
6. risques residuels
7. recommendation go / no-go pour le lot 7

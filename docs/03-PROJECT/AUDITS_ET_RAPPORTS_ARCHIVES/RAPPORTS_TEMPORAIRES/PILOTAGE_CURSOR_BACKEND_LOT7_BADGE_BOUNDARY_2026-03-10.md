# Lot 7 - Badge boundary - 2026-03-10

## Mission
Fermer la boundary `badge` en sortant les handlers utilisateur/publics de la DB et du wiring metier direct.

## Analyse actuelle
- `server/handlers/badge_handlers.py` ouvre encore `db_session` partout et construit `BadgeService` dans la couche HTTP.
- le domaine badge est riche et charge; le bon premier mouvement est de sortir le wiring HTTP, pas de refaire tout `BadgeService`.
- les endpoints couverts melangent public (`available`, `rarity`) et authentifie (`user`, `stats`, `pin`, `progress`, `check`).

## Ce qui est mal place
- instanciation de `BadgeService` dans les handlers
- `db_session` direct dans les handlers
- parsing `badge_ids` et validation transport encore colles a la logique metier

## Ce qui est duplique
- pattern `async with db_session() as db` repete sur tous les endpoints badge
- enveloppes `{success: True, data: ...}` reconstruites a la main dans la couche HTTP

## Decoupage cible
- creer `app/services/badge_application_service.py`
- ajouter un schema `PinnedBadgesRequest` si absent dans `app/schemas` et si le gain est clair
- laisser `BadgeService` comme moteur metier sous-jacent

## Fichiers a lire avant toute modification
- `server/handlers/badge_handlers.py`
- `app/services/badge_service.py`
- `app/services/badge_requirement_engine.py`
- `tests/api/test_admin_badges.py`
- `tests/unit/test_badge_requirement_engine.py`
- `tests/api/test_user_endpoints.py`

## Fichiers autorises
- `server/handlers/badge_handlers.py`
- `app/services/badge_application_service.py`
- `app/schemas/user.py` ou schema dedie si necessaire
- tests badge cibles si ajustement minimal necessaire

## Fichiers explicitement hors scope
- refactor profond de `badge_service.py`
- `admin`
- `challenge`
- `exercise`
- `auth`

## Actions precises a effectuer
- sortir les appels `BadgeService` des handlers dans une facade applicative
- sortir le `db_session` direct des handlers badge
- formaliser la payload `pin` si possible sans drift
- conserver strictement les enveloppes JSON publiques existantes

## Checks a lancer
- `pytest -q tests/api/test_admin_badges.py tests/unit/test_badge_requirement_engine.py tests/api/test_user_endpoints.py --maxfail=20`
- `pytest -q --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- si le lot force a refactorer le moteur de badges en profondeur
- si les contrats JSON publics doivent changer
- si le lot deborde sur `admin` ou `challenge`

## Definition of Done
- plus de `db_session` direct dans `badge_handlers.py`
- wiring badge sorti des handlers
- suite backend complete verte

## Format de compte-rendu final
1. fichiers modifies
2. ce qui a ete sorti des handlers
3. nouveau decoupage service/schema
4. preuve que le contrat HTTP n'a pas change
5. checks executes et resultat
6. risques residuels
7. recommendation go / no-go pour cloturer l'iteration

# Lot 5 - Admin user and config mutation boundary - 2026-03-10

## Mission
Sortir les mutations admin `users` et `config` des handlers, avec le plus petit diff defensible.

## Analyse actuelle
- `admin_users_patch`, `admin_users_send_reset_password`, `admin_users_resend_verification`, `admin_users_delete`, `admin_config_put` ouvrent la DB dans le handler et appellent `AdminService` directement.
- le domaine auth n'a pas a etre rouvert: l'admin doit seulement orchestrer proprement les actions deja supportees.

## Ce qui est mal place
- ouverture DB et orchestration de mutation dans le handler
- wiring admin/auth user encore trop haut dans la pile HTTP

## Ce qui est duplique
- pattern `parse body -> db_session -> AdminService -> api_error_response`
- extraction `admin_user_id` repetee

## Decoupage cible
- etendre `app/services/admin_application_service.py` pour porter les mutations `users/config`
- ajouter des schemas admin si necessaire et faibles en risque

## Fichiers a lire avant toute modification
- `server/handlers/admin_handlers.py`
- `app/services/admin_service.py`
- `app/services/admin_user_service.py`
- `app/services/admin_config_service.py`
- `tests/api/test_admin_users_delete.py`
- `tests/api/test_auth_flow.py`

## Fichiers autorises
- `server/handlers/admin_handlers.py`
- `app/services/admin_application_service.py`
- `app/schemas/admin.py` si necessaire
- tests admin/auth cibles si ajustement minimal necessaire

## Fichiers explicitement hors scope
- CRUD admin `exercises/challenges/badges`
- `middleware`
- `badge`
- `challenge`
- `exercise`

## Actions precises a effectuer
- sortir les mutations admin users/config dans la facade applicative
- garder dans le handler uniquement parse, auth, mapping erreurs HTTP
- ne pas rouvrir les boundaries `auth` ou `user` deja stabilisees
- conserver les messages et status codes existants

## Checks a lancer
- `pytest -q tests/api/test_admin_users_delete.py tests/api/test_auth_flow.py --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- si le lot force a rouvrir `auth`
- si le lot force a changer les messages admin ou les codes HTTP
- si le lot deborde sur les CRUD de contenu

## Definition of Done
- handlers admin du scope lot 5 sans `db_session` direct
- mutations users/config absorbees par la facade applicative
- tests cibles verts

## Format de compte-rendu final
1. fichiers modifies
2. ce qui a ete sorti des handlers
3. nouveau decoupage service/schema
4. preuve que le contrat HTTP n'a pas change
5. checks executes et resultat
6. risques residuels
7. recommendation go / no-go pour le lot 6

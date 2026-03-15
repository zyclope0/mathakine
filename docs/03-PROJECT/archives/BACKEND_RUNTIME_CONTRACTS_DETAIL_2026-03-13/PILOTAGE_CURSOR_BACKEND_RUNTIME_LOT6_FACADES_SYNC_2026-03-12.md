# Lot A6 - Harmonisation runtime facades sync

> Mise a jour : 13/03/2026
> Statut : valide en code, cloture documentaire corrigee

## Mission

Harmoniser le modele runtime sur les facades applicatives deja refactorees qui utilisaient encore le faux async DB.

## Scope runtime traite

### Services passes en sync + `sync_db_session()`

- `admin_application_service.py`
- `admin_read_service.py`
- `badge_application_service.py`
- `user_application_service.py`
- `challenge_query_service.py`
- `challenge_attempt_service.py`

### Handlers realignes sur `run_db_bound(...)`

- `admin_handlers.py` pour les appels admin DB-backed du scope A6
- `badge_handlers.py`
- `user_handlers.py`
- `challenge_handlers.py`
- `feedback_handlers.py` pour la lecture admin feedback du scope
- `analytics_handlers.py` pour la lecture admin analytics EdTech du scope

## Ce qui est prouve

- plus aucun `async with db_session()` dans les 6 facades du scope A6
- les handlers DB-backed du scope passent par `run_db_bound(...)`
- les contrats HTTP publics du scope sont restes inchanges

## Ce qui ne doit pas etre sur-vendu

Hors scope A6:
- `challenge_ai_service.py`
- `exercise_ai_service.py`
- `settings_reader.py`

Ces reliquats ont ete traites seulement au lot runtime final, pas dans A6.

## Risque residuel documente

`feedback_service.create_feedback_report_sync()` retourne encore un objet ORM `FeedbackReport`. `feedback_handlers.submit_feedback()` lit ensuite `report.id` apres retour du threadpool. Le comportement fonctionne probablement aujourd'hui car l'identifiant est materialise, mais la boundary reste plus fragile qu'un payload deja serialise.

## Validation de lot

- batterie A6 reportee documentairement : `220 passed` lors de la validation de cloture
- full suite hors faux gate : verte lors de la validation de cloture documentaire du lot
- `black --check` : vert
- `isort --check-only --diff` : vert

## Verdict

- runtime A6 : GO
- cloture documentaire A6 : GO

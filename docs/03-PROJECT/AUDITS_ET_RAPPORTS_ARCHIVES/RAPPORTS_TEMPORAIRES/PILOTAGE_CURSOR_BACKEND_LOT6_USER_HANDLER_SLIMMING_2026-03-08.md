# Lot 6 - User handler slimming

## Mission
- Rendre `server/handlers/user_handlers.py` anemique sur les flux `registration`, `stats`, `profile`, `leaderboard`, `sessions`, `export`.
- Cible finale: le handler ne garde que la validation HTTP, l'appel a un service applicatif, et le mapping de reponse HTTP.

## Analyse actuelle
- `server/handlers/user_handlers.py` porte encore:
  - validation manuelle
  - regex email
  - controles de longueur username
  - appels directs a `EnhancedServerAdapter`
  - parsing de query params
  - ouverture DB
  - orchestration registration/profile/sessions/export
- `app/services/user_service.py` existe, mais le handler le contourne encore partiellement.
- La baseline `auth + user` est verte avant refactor.

## Ce qui est mal place
- Validation d'inscription dans le handler alors que `UserCreate` existe.
- Stats dashboard via `EnhancedServerAdapter.get_user_stats_for_dashboard`.
- Orchestration de sessions, export et mise a jour profil directement dans le handler.
- Duplication des patterns `current_user`, `user_id`, parsing query params.

## Ce qui est duplique
- Validations manuelles deja exprimables par schemas.
- Extraction utilisateur courant et gestion des cas incomplets.
- Ouverture DB et mapping JSON sur plusieurs endpoints `user`.

## Decoupage cible
- Nouveau service facade: `app/services/user_application_service.py`
  - responsabilite: registration, dashboard stats, leaderboard, timeline, profile, password update, delete, export, sessions
- Schemas query complementaires dans `app/schemas/user.py` si necessaires
- `user_handlers.py`
  - devient simple controller HTTP
- `user_service.py`
  - reste la couche metier/data deja existante, reutilisee autant que possible

## Fichiers a lire avant toute modification
- `server/handlers/user_handlers.py`
- `app/services/user_service.py`
- `app/services/auth_service.py`
- `app/services/progress_timeline_service.py`
- `app/schemas/user.py`
- `tests/api/test_user_endpoints.py`
- `tests/api/test_user_delete_cascade.py`
- `tests/api/test_admin_users_delete.py`
- `tests/integration/test_user_exercise_flow.py`
- `tests/unit/test_user_service.py`

## Fichiers autorises
- `server/handlers/user_handlers.py`
- `app/services/user_service.py` (adaptation minimale si necessaire)
- `app/services/user_application_service.py` (creation)
- `app/schemas/user.py`
- `tests/api/test_user_endpoints.py`
- `tests/api/test_user_delete_cascade.py`
- `tests/api/test_admin_users_delete.py`
- `tests/integration/test_user_exercise_flow.py`
- `tests/unit/test_user_service.py`

## Fichiers explicitement hors scope
- `auth_handlers.py`
- `admin_handlers.py`
- tout fichier `badge`, `challenge`, `recommendation`, `middleware`
- rework produit du modele `User`

## Actions precises a effectuer
1. Creer `app/services/user_application_service.py` pour centraliser:
   - registration
   - dashboard stats
   - leaderboard
   - timeline
   - profile update
   - password update
   - delete user
   - export user data
   - sessions utilisateur
2. Faire passer `create_user_account` par `UserCreate` et le service applicatif, sans regex manuelle dans le handler.
3. Remplacer les appels directs `EnhancedServerAdapter` par `user_application_service.py` ou `UserService`.
4. Deplacer la logique de stats, leaderboard, timeline, sessions, export, update profil et password hors du handler.
5. Ajouter des schemas query Pydantic dans `app/schemas/user.py` seulement si necessaire pour supprimer le parsing manuel des query params.
6. Garder les decorators auth/role cote handler.
7. Conserver strictement les payloads exposes aux tests existants.

## Checks a lancer
- `pytest -q tests/api/test_user_endpoints.py tests/api/test_user_delete_cascade.py tests/unit/test_user_service.py tests/api/test_admin_users_delete.py tests/integration/test_user_exercise_flow.py --maxfail=20`
- `pytest -q --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- Si le lot force a modifier `admin_handlers.py` ou le middleware.
- Si le lot commence a redessiner le modele `User`.
- Si les payloads users testes commencent a changer.
- Si un bug produit de droit d'acces ou de session est revele: stop et rapport factuel.

## Definition of Done
- `user_handlers.py` n'embarque plus de validation metier manuelle ni d'acces DB direct.
- `create_user_account` passe par `UserCreate`.
- Les endpoints `users` restent compatibles avec les tests existants.
- `pytest -q --maxfail=20` reste vert a la fin du lot.
- `black app/ server/ tests/ --check` reste vert a la fin du lot.

## Format de compte-rendu final
1. Fichiers modifies
2. Ce qui a ete sorti des handlers user
3. Nouveau decoupage service/schema
4. Preuve que les payloads users n'ont pas change
5. Checks executes et resultat
6. Risques residuels
7. Recommandation go / no-go pour cloturer l'iteration

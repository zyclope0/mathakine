# Lot 3 - Exercise lecture, query params, interleaved, stats et SSE boundary

## Mission
- Sortir les acces DB et la logique non HTTP restants de `server/handlers/exercise_handlers.py` pour les routes de lecture, interleaved, stats et SSE.
- Cible finale: aucun import `db_session` dans `exercise_handlers.py`.

## Analyse actuelle
- `get_exercise`, `get_exercises_list`, `get_interleaved_plan_api`, `get_completed_exercises_ids`, `get_exercises_stats` ouvrent encore la DB directement depuis le handler.
- `generate_ai_exercise_stream` valide le prompt, normalise les parametres et prepare le contexte utilisateur/locale avant de construire la reponse SSE.
- `server/handlers/exercise_list_params.py` utilise un dataclass au lieu d'un schema Pydantic.

## Ce qui est mal place
- Acces DB direct dans les handlers query.
- Validation metier de prompt SSE dans le handler.
- Normalisation de query params hors schema Pydantic.

## Ce qui est duplique
- Extraction de `user_id` et gestion du cas utilisateur anonyme.
- Normalisation de query params et defaults.
- Ouverture de session DB pour des routes de lecture.
- Preparation du contexte SSE (locale, type, age_group, prompt, user_id).

## Decoupage cible
- Nouveau service: `app/services/exercise_query_service.py`
  - responsabilite: lecture exercice, liste, interleaved plan, completed ids, stats
- Nouveau service: `app/services/exercise_stream_service.py`
  - responsabilite: validation/normalisation/preparation du contexte stream
- Schemas Pydantic dans `app/schemas/exercise.py`
  - `ExerciseListQuery`
  - `InterleavedPlanQuery`
  - `GenerateExerciseStreamQuery`
- `server/handlers/exercise_list_params.py`
  - supprime si inutile, sinon reduit a compat technique minimale

## Fichiers a lire avant toute modification
- `server/handlers/exercise_handlers.py`
- `server/handlers/exercise_list_params.py`
- `app/services/exercise_service.py`
- `app/services/exercise_stats_service.py`
- `app/services/interleaved_practice_service.py`
- `app/services/exercise_ai_service.py`
- `app/schemas/exercise.py`
- `app/utils/prompt_sanitizer.py`
- `app/utils/sse_utils.py`
- `tests/unit/test_exercise_handlers.py`
- `tests/api/test_exercise_endpoints.py`
- `tests/integration/test_sse_auth.py`

## Fichiers autorises
- `server/handlers/exercise_handlers.py`
- `server/handlers/exercise_list_params.py`
- `app/schemas/exercise.py`
- `app/services/exercise_query_service.py` (creation)
- `app/services/exercise_stream_service.py` (creation)
- `tests/unit/test_exercise_handlers.py`
- `tests/api/test_exercise_endpoints.py`
- `tests/integration/test_sse_auth.py`

## Fichiers explicitement hors scope
- Generation d'exercice lot 1
- Soumission de reponse lot 2
- tout fichier `auth`, `user`, `admin`, `challenge`, `badge`, `recommendation`, `middleware`
- rework fonctionnel de `exercise_ai_service.py`

## Actions precises a effectuer
1. Ajouter les schemas query Pydantic dans `app/schemas/exercise.py`.
2. Creer `app/services/exercise_query_service.py` pour:
   - recuperer un exercice pour l'API
   - lister les exercices
   - calculer le plan interleaved
   - retourner les IDs completes
   - retourner les stats d'exercices
3. Creer `app/services/exercise_stream_service.py` pour:
   - valider la securite du prompt
   - normaliser `exercise_type` et `age_group`
   - preparer `locale` et `user_id`
   - retourner un contexte typed pour le handler SSE
4. Refactorer `exercise_handlers.py` pour que les routes query et interleaved passent toutes par `exercise_query_service.py`.
5. Refactorer `generate_ai_exercise_stream` pour garder seulement:
   - lecture de la requete
   - appel au service de preparation
   - construction de `StreamingResponse`
6. Eliminer l'import `db_session` de `exercise_handlers.py`.
7. Supprimer ou reduire `exercise_list_params.py` si les nouveaux schemas Pydantic couvrent proprement le besoin.
8. Ne pas changer les headers SSE, ni les messages d'erreur utilisateur, ni le comportement existant des routes.

## Checks a lancer
- `pytest -q tests/unit/test_exercise_handlers.py tests/api/test_exercise_endpoints.py tests/integration/test_sse_auth.py --maxfail=20`
- `pytest -q --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- Si le refactor force a changer les headers SSE.
- Si la suppression de `exercise_list_params.py` casse un autre domaine.
- Si une route `exercise` du scope doit encore ouvrir la DB depuis le handler.
- Si un changement requiert de toucher `middleware` ou d'autres domaines hors scope.

## Definition of Done
- `exercise_handlers.py` n'importe plus `db_session`.
- Toutes les routes `exercise` passent par services + schemas.
- Les comportements SSE restent compatibles.
- `pytest -q --maxfail=20` reste vert a la fin du lot.
- `black app/ server/ tests/ --check` reste vert a la fin du lot.

## Format de compte-rendu final
1. Fichiers modifies
2. Routes `exercise` migrees vers les services
3. Sort final de `exercise_list_params.py`
4. Preuve que le comportement SSE n'a pas change
5. Checks executes et resultat
6. Risques residuels
7. Recommandation go / no-go pour le lot 4

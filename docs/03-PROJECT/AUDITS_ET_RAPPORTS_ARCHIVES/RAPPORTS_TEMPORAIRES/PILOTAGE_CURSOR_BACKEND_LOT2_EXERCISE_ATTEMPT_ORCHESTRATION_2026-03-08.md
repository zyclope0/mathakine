# Lot 2 - Exercise soumission de reponse et effets metier

## Mission
- Extraire l'orchestration metier de `submit_answer` et de `ExerciseService.submit_answer_result` vers un service applicatif et un repository dedies.
- Cible finale: le handler `submit_answer` ne fait plus que parser, valider, appeler le service, puis traduire les exceptions metier en HTTP.

## Analyse actuelle
- `submit_answer` est deja plus propre que d'autres handlers, mais l'orchestration metier lourde est concentree dans `app/services/exercise_service.py`.
- `ExerciseService.submit_answer_result` combine:
  - chargement exercice
  - validation reponse
  - creation tentative
  - progression
  - badges
  - streak
  - daily challenge
  - transaction et commit
  - construction du DTO de reponse
- `record_attempt` cache en plus une mise a jour implicite de progression.

## Ce qui est mal place
- `ExerciseService.submit_answer_result` melange lecture, ecriture, orchestration de side effects et shape de reponse.
- `record_attempt` fait plus que persister une tentative.
- Les savepoints et effets metier non critiques vivent dans un service trop generique.

## Ce qui est duplique
- Recuperation exercice et validation metier melangees a la persistance.
- Regles de progression implicites dans `record_attempt`.
- Acces DB et orchestration transactionnelle dans les memes methodes.

## Decoupage cible
- Nouveau repository: `app/repositories/exercise_attempt_repository.py`
  - responsabilite: lecture exercice pour validation, creation tentative, update progression
- Nouveau service: `app/services/exercise_attempt_service.py`
  - responsabilite: orchestration metier de soumission + side effects rollbackables
- `app/services/exercise_service.py`
  - redevient service read/query ou facade minimale
- `server/handlers/exercise_handlers.py`
  - `submit_answer` devient un simple controller HTTP

## Fichiers a lire avant toute modification
- `server/handlers/exercise_handlers.py`
- `app/services/exercise_service.py`
- `app/schemas/exercise.py`
- `app/models/attempt.py`
- `app/models/progress.py`
- `app/services/badge_service.py`
- `app/services/streak_service.py`
- `app/services/daily_challenge_service.py`
- `tests/unit/test_exercise_service.py`
- `tests/unit/test_exercise_handlers.py`
- `tests/api/test_exercise_endpoints.py`

## Fichiers autorises
- `server/handlers/exercise_handlers.py`
- `app/services/exercise_service.py`
- `app/repositories/exercise_attempt_repository.py` (creation)
- `app/services/exercise_attempt_service.py` (creation)
- `tests/unit/test_exercise_service.py`
- `tests/unit/test_exercise_handlers.py`
- `tests/api/test_exercise_endpoints.py`

## Fichiers explicitement hors scope
- Generation d'exercice
- `generate_ai_exercise_stream`
- `get_interleaved_plan_api`
- `get_exercises_list`, `get_exercise`, `get_exercises_stats`, `get_completed_exercises_ids`
- tout fichier `auth`, `user`, `admin`, `challenge`, `badge` hors lecture necessaire du service badge

## Actions precises a effectuer
1. Creer `app/repositories/exercise_attempt_repository.py` pour:
   - charger l'exercice necessaire a la validation de reponse
   - creer un `Attempt`
   - mettre a jour `Progress`
2. Creer `app/services/exercise_attempt_service.py` pour:
   - determiner si la reponse est correcte
   - orchestrer transaction, badges, streak, daily challenge
   - construire le `SubmitAnswerResponse`
3. Deplacer `_check_answer_correct` vers `exercise_attempt_service.py`.
4. Deplacer `_update_user_statistics` vers `exercise_attempt_service.py` ou un helper local a ce service.
5. Faire en sorte que `record_attempt` ne fasse plus de side effect de progression cache.
6. Garder les side effects non critiques rollbackables comme aujourd'hui:
   - badges
   - streak
   - daily challenge
7. Refactorer le handler `submit_answer` pour qu'il ne fasse plus que:
   - lecture JSON
   - validation `SubmitAnswerRequest`
   - extraction `exercise_id` et `user_id`
   - appel `exercise_attempt_service`
   - mapping exceptions metier -> HTTP
8. Retirer l'usage du handler vers `ExerciseService.submit_answer_result`.
9. Conserver `SubmitAnswerRequest` et `SubmitAnswerResponse` tels qu'exposes a l'API.

## Checks a lancer
- `pytest -q tests/unit/test_exercise_service.py tests/unit/test_exercise_handlers.py tests/api/test_exercise_endpoints.py --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- Si le refactor force a changer le payload de `POST /api/exercises/{id}/attempt`.
- Si les side effects badges/streak/daily exigent une refonte transverse.
- Si le handler doit encore connaitre des details de transaction.
- Si un bug produit de notation ou de progression est revele: stop et compte-rendu factuel.

## Definition of Done
- `exercise_handlers.py` ne porte plus de logique de correction metier ni d'orchestration badges/streak.
- `ExerciseService.submit_answer_result` n'est plus appele par le handler.
- `record_attempt` n'embarque plus d'update implicite de progression.
- Le contrat de `POST /api/exercises/{id}/attempt` reste identique.
- Les tests `exercise` cibles restent verts.

## Format de compte-rendu final
1. Fichiers modifies
2. Ce qui a ete sorti de `ExerciseService`
3. Nouveau decoupage repository/service
4. Preuve que le contrat de soumission n'a pas change
5. Checks executes et resultat
6. Risques residuels
7. Recommandation go / no-go pour le lot 3

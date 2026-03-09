# Lot 1 - Exercise generation et persistance

## Mission
- Assainir les flux `generate_exercise` et `generate_exercise_api` pour sortir toute logique metier et tout acces DB de `server/handlers/exercise_handlers.py`.
- Cible finale: le handler ne fait plus que parser la requete HTTP, valider les inputs, appeler un service applicatif, et mapper la reponse HTTP (`303` HTML ou `200` JSON).

## Analyse actuelle
- `server/handlers/exercise_handlers.py` porte encore de la logique metier dans `_resolve_adaptive_age_group_if_needed`, `generate_exercise` et `generate_exercise_api`.
- Le handler choisit le mode AI/simple, resout la difficulte adaptative, extrait la locale, persiste l'exercice, puis gere des branches d'echec metier.
- Il existe une duplication forte entre les flux HTML et API sur:
  - normalisation des parametres
  - resolution adaptive de `age_group`
  - selection AI/simple
  - `ensure_explanation`
  - extraction de locale
  - sauvegarde via `EnhancedServerAdapter.create_generated_exercise`
- La baseline `exercise` est verte avant refactor.

## Ce qui est mal place
- `_resolve_adaptive_age_group_if_needed` depend du modele utilisateur et de la DB, donc ce n'est pas une responsabilite de handler.
- `generate_exercise` et `generate_exercise_api` prennent des decisions metier qui doivent vivre dans un service dedie.
- La persistance d'exercice genere via `EnhancedServerAdapter.create_generated_exercise` ne doit pas rester dans un handler.

## Ce qui est duplique
- Normalisation et validation des parametres de generation.
- Resolution adaptive de `age_group`.
- Construction du dictionnaire d'exercice genere.
- Extraction de locale.
- Sauvegarde conditionnelle et verification de l'`id` persiste.

## Decoupage cible
- Nouveau repository: `app/repositories/exercise_repository.py`
  - responsabilite: lecture utilisateur utile a l'adaptive + persistance d'exercice genere
- Nouveau service: `app/services/exercise_generation_service.py`
  - responsabilite: orchestration metier complete de la generation
- Schema Pydantic a ajouter dans `app/schemas/exercise.py`
  - `GenerateExerciseRequest`
  - `GenerateExerciseResult`
- `server/handlers/exercise_handlers.py`
  - garde les endpoints
  - ne garde plus ni `db_session` ni `EnhancedServerAdapter.create_generated_exercise` pour les routes de generation

## Fichiers a lire avant toute modification
- `server/handlers/exercise_handlers.py`
- `app/services/exercise_service.py`
- `app/schemas/exercise.py`
- `server/exercise_generator.py`
- `server/exercise_generator_validators.py`
- `app/services/adaptive_difficulty_service.py`
- `app/services/enhanced_server_adapter.py`
- `tests/unit/test_exercise_handlers.py`
- `tests/api/test_exercise_endpoints.py`

## Fichiers autorises
- `server/handlers/exercise_handlers.py`
- `app/schemas/exercise.py`
- `app/repositories/exercise_repository.py` (creation)
- `app/services/exercise_generation_service.py` (creation)
- `tests/unit/test_exercise_handlers.py`
- `tests/api/test_exercise_endpoints.py`

## Fichiers explicitement hors scope
- `submit_answer` et tout ce qui touche la soumission de reponse
- `get_interleaved_plan_api`
- `generate_ai_exercise_stream`
- `get_completed_exercises_ids`
- `get_exercises_stats`
- `app/services/exercise_service.py` hors adaptation minimale indispensable pour l'appel du nouveau service
- tout fichier `auth`, `user`, `admin`, `badge`, `challenge`, `recommendation`, `middleware`

## Actions precises a effectuer
1. Creer `GenerateExerciseRequest` dans `app/schemas/exercise.py` pour le flux API POST avec les champs utilises aujourd'hui: `exercise_type`, `age_group`, `ai`, `adaptive`, `save`.
2. Creer `GenerateExerciseResult` dans `app/schemas/exercise.py` avec un resultat type pour la generation, incluant les donnees d'exercice et l'`id` optionnel si persistence.
3. Creer `app/repositories/exercise_repository.py` pour:
   - recuperer un utilisateur par `user_id` pour la resolution adaptive
   - persister un exercice genere
4. Creer `app/services/exercise_generation_service.py` pour:
   - resoudre `age_group` si adaptive
   - normaliser et valider les parametres
   - generer l'exercice AI ou simple
   - garantir `ensure_explanation`
   - extraire/passer la locale
   - sauvegarder si demande
5. Refactorer `generate_exercise` pour qu'il n'orchestre plus que:
   - lecture des query params
   - construction du contexte HTTP
   - appel service
   - mapping vers `RedirectResponse` ou page erreur
6. Refactorer `generate_exercise_api` pour qu'il n'orchestre plus que:
   - parsing JSON
   - validation via `GenerateExerciseRequest`
   - appel service
   - mapping vers `JSONResponse`
7. Supprimer l'appel direct a `db_session` et a `EnhancedServerAdapter.create_generated_exercise` des handlers de generation.
8. Conserver le `303` du flux HTML et le `200` du flux API, sans changer le payload existant.
9. Adapter ou renforcer les tests uniquement si necessaire pour figer le boundary service/handler, sans changer le produit.

## Checks a lancer
- `pytest -q tests/unit/test_exercise_handlers.py tests/api/test_exercise_endpoints.py --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- Si le refactor force a toucher `submit_answer`, `interleaved` ou le SSE.
- Si la persistance d'exercice genere implique un changement de contrat HTTP.
- Si le diff commence a rewriter `exercise_service.py` au-dela du strict minimum de compatibilite.
- Si un bug produit est decouvert dans la logique adaptive ou la generation: stop, constat, risque, sous-lot recommande.

## Definition of Done
- Plus aucun `db_session` dans les handlers de generation.
- Plus aucun `EnhancedServerAdapter.create_generated_exercise` dans les handlers de generation.
- Plus aucune logique adaptive dans le handler.
- Le flux HTML garde `303`.
- Le flux API garde `200` et le meme shape JSON.
- Les tests `exercise` cibles restent verts.

## Format de compte-rendu final
1. Fichiers modifies
2. Ce qui a ete sorti du handler
3. Nouveau decoupage service/repository/schema
4. Preuve que les contrats HTTP n'ont pas change
5. Checks executes et resultat
6. Risques residuels
7. Recommandation go / no-go pour le lot 2

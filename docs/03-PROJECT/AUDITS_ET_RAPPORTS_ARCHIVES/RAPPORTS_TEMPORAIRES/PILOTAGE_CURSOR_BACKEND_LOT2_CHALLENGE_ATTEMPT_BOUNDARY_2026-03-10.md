# Lot 2 - Challenge attempt boundary - 2026-03-10

## Mission
Sortir la soumission de reponse `challenge` du handler et clarifier l'orchestration tentative/progression.

## Analyse actuelle
- `submit_challenge_answer` ouvre la DB et appelle directement `LogicChallengeService.submit_answer_result(...)`.
- le parsing `user_solution`, `time_spent`, `hints_used_count` reste dans le handler.
- `challenge_answer_service.py` existe deja comme moteur de comparaison et fournit un bon point d'appui.

## Ce qui est mal place
- ouverture de transaction dans le handler
- payload de tentative partiellement normalisee dans le handler
- orchestration encore trop coulee dans `LogicChallengeService`

## Ce qui est duplique
- pattern exercise-like de parse/call/JSONResponse sans vraie couche applicative
- logique de normalisation de tentative non formalisee par schema

## Decoupage cible
- creer `app/services/challenge_attempt_service.py`
- creer `app/repositories/challenge_attempt_repository.py` si necessaire pour la persistance de tentative/progression
- ajouter un schema minimal `ChallengeAttemptRequest` si absent dans `app/schemas/logic_challenge.py`

## Fichiers a lire avant toute modification
- `server/handlers/challenge_handlers.py`
- `app/services/logic_challenge_service.py`
- `app/services/challenge_answer_service.py`
- `app/services/challenge_service.py`
- `app/schemas/logic_challenge.py`
- `tests/api/test_challenge_endpoints.py`
- `tests/api/test_challenges_flow.py`
- `tests/unit/test_challenge_answer_service.py`
- `tests/unit/test_logic_challenge_service.py`

## Fichiers autorises
- `server/handlers/challenge_handlers.py`
- `app/services/challenge_attempt_service.py`
- `app/repositories/challenge_attempt_repository.py`
- `app/services/logic_challenge_service.py` au strict minimum
- `app/schemas/logic_challenge.py`
- tests challenge cibles

## Fichiers explicitement hors scope
- query challenge du lot 1
- stream IA du lot 3
- `challenge_validator.py`
- `admin`
- `badge`

## Actions precises a effectuer
- sortir la normalisation de payload et l'orchestration tentative dans un service applicatif dedie
- faire du handler une simple adaptation HTTP
- reutiliser `challenge_answer_service.py` pour la logique de comparaison, sans la dupliquer
- ne pas ouvrir un grand refactor de `LogicChallengeService`

## Checks a lancer
- `pytest -q tests/api/test_challenge_endpoints.py tests/api/test_challenges_flow.py tests/unit/test_challenge_answer_service.py tests/unit/test_logic_challenge_service.py --maxfail=20`
- `black app/ server/ tests/ --check`

## Stop conditions
- si le lot force a toucher le stream IA
- si un refactor large de `LogicChallengeService` devient necessaire
- si le contrat utilisateur de `attempt` devrait changer

## Definition of Done
- `submit_challenge_answer` ne porte plus la logique metier
- transaction et persistance sorties du handler
- tests metier et API cibles verts

## Format de compte-rendu final
1. fichiers modifies
2. ce qui a ete sorti du handler
3. nouveau decoupage service/repository/schema
4. preuve que le contrat HTTP n'a pas change
5. checks executes et resultat
6. risques residuels
7. recommendation go / no-go pour le lot 3

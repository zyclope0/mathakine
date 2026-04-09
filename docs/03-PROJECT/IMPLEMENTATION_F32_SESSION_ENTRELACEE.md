# Implementation F32 - Session entrelacee

## Statut

- Statut : implemente le 07/03/2026
- Durcissements post-implementation : 08/03/2026
- Mise a jour architecture/frontend : 10/04/2026
- Portee : MVP sans migration DB, session ephemere cote client, endpoint de plan dedie

## Role du document

Cette note reste utile comme trace d'implementation de F32.

Elle n'est pas un backlog actif. La verite d'execution courante reste :

- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`
- `.claude/session-plan.md`
- le code runtime

## Objectif produit

F32 introduit une pratique entrelacee simple et pedagogique :

- depuis le dashboard, l'utilisateur lance une session guidee
- la session enchaine des exercices de types differents
- la difficulte reste adaptative via le generateur existant
- la session doit rester lisible, simple et non punitive

Reference produit :

- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` -> F32

## Contrat fonctionnel toujours valide

Les points ci-dessous sont toujours vrais au 10/04/2026 :

1. le dashboard expose un CTA Quick Start dedie
2. le frontend appelle `GET /api/exercises/interleaved-plan?length=10`
3. le plan est stocke cote client dans `sessionStorage`
4. la page d'entree est `frontend/app/exercises/interleaved/page.tsx`
5. le premier exercice est genere via `POST /api/exercises/generate`
6. le solveur est visite avec `?session=interleaved`
7. l'utilisateur peut enchainer sur `Exercice suivant`
8. la session se termine par un ecran simple de fin

## Verite terrain actuelle

### Backend

Le plan entrelace reste porte par :

- route : `server/routes/exercises.py`
- handler : `server/handlers/exercise_handlers.py`
- schema query : `app/schemas/exercise.py`
- service : `app/services/exercises/interleaved_practice_service.py`
- facade query service : `app/services/exercises/exercise_query_service.py`

Contrat API attendu :

```text
GET /api/exercises/interleaved-plan?length=10
```

Comportement :

- auth requise
- calcule un plan ordonne de types eligibles
- ne genere pas les exercices lui-meme
- laisse la generation effective a `POST /api/exercises/generate`
- retourne `409` avec code metier `not_enough_variety` si moins de 2 types eligibles

### Frontend

Le contrat produit reste le meme, mais l'architecture frontend a evolue depuis le MVP initial.

La verite actuelle est :

- `frontend/components/dashboard/QuickStartActions.tsx`
  - point d'entree dashboard
- `frontend/app/exercises/interleaved/page.tsx`
  - page de bootstrap de session
- `frontend/components/exercises/ExerciseSolver.tsx`
  - facade de vue
- `frontend/hooks/useExerciseSolverController.ts`
  - runtime interleaved et spaced-review
- `frontend/lib/exercises/exerciseSolverSession.ts`
  - lecture/ecriture du mode et du payload de session
- `frontend/lib/exercises/exerciseSolverFlow.ts`
  - derivations pures de flux

### Ce qui a change depuis la note initiale

La note historique parlait de "ne pas refondre ExerciseSolver" et de faire une extension minimale dans le composant.

Ce n'est plus la bonne lecture en 2026-04-10 :

- `ExerciseSolver.tsx` reste une facade
- le runtime interleaved vit dans `useExerciseSolverController.ts`
- la source de verite pour `INTERLEAVED_STORAGE_KEY` vit dans `exerciseSolverSession.ts`
- la logique pure de fin de session, de persistence et de merge analytics vit dans `exerciseSolverFlow.ts`

Autrement dit :

- le comportement F32 est conserve
- l'architecture frontend n'est plus celle du lot initial

## Hypothese MVP retenue

Pour limiter le risque initial :

- pas de nouvelle table
- pas de persistance serveur de session
- pas d'IA streaming dans F32 v1
- reutilisation maximale des briques existantes :
  - `QuickStartActions`
  - `POST /api/exercises/generate`
  - solveur exercice existant
  - adaptation dynamique F05

La session reste ephemere cote client via `sessionStorage`.

## Durcissements post-implementation

Les durcissements appliques apres la livraison MVP ont cible les points les plus fragiles du flux :

- analytics EdTech `interleaved` : emission de `first_attempt` une seule fois par session
- persistance `analytics.firstAttemptTracked` dans `sessionStorage`
- robustesse `save=true` : erreur explicite si la sauvegarde echoue ou ne retourne pas d'id
- UX d'erreur : toast explicite + fallback vers `/exercises` a l'entree de session
- UX `Exercice suivant` : toast explicite et conservation de la session en cas d'echec
- DRY backend : resolution adaptive `age_group` factorisee

## Valeur pedagogique a conserver

Le coeur de F32 n'est pas "un bouton de plus".
La feature doit forcer le choix de strategie par alternance des types.

Principes a conserver :

- 3 a 4 types differents par session si possible
- pas de repetitions consecutives si evitables
- seulement des types deja pratiques par l'utilisateur
- seulement des types avec niveau suffisant pour eviter l'echec arbitraire
- micro-copy explicative : l'effort cognitif plus eleve est normal et utile

## Algorithme MVP recommande

### Eligibilite des types

Source de verite :

- `Attempt`
- `Exercise`

Fenetre :

- 7 derniers jours glissants

Un type est eligible si :

- il a au moins `2` tentatives sur 7 jours
- son taux de reussite est `>= 60%`
- il fait partie des types supportes par le generateur standard

### Construction du plan

Parametres MVP :

- longueur par defaut : `10`
- minimum de types distincts : `2`
- cible ideale : `3` ou `4`

Regles :

- trier les types eligibles par volume recent
- prendre jusqu'a 4 types
- construire un plan round-robin
- eviter deux memes types a la suite si possible

Exemple :

```json
{
  "length": 10,
  "eligible_types": ["addition", "multiplication", "division"],
  "plan": [
    "addition",
    "multiplication",
    "division",
    "addition",
    "multiplication",
    "division",
    "addition",
    "multiplication",
    "division",
    "addition"
  ]
}
```

### Cas limite

Si moins de 2 types sont eligibles :

- retourner `409`
- code metier conseille : `not_enough_variety`
- le frontend affiche un message non bloquant et redirige vers `/exercises`

## Fichiers reellement cibles

### Backend

- `app/services/exercises/interleaved_practice_service.py`
- `app/services/exercises/exercise_query_service.py`
- `app/schemas/exercise.py`
- `server/handlers/exercise_handlers.py`
- `server/routes/exercises.py`
- `tests/unit/test_interleaved_practice_service.py`
- `tests/api/test_exercise_endpoints.py`

### Frontend

- `frontend/components/dashboard/QuickStartActions.tsx`
- `frontend/app/exercises/interleaved/page.tsx`
- `frontend/components/exercises/ExerciseSolver.tsx`
- `frontend/hooks/useExerciseSolverController.ts`
- `frontend/lib/exercises/exerciseSolverSession.ts`
- `frontend/lib/exercises/exerciseSolverFlow.ts`
- `frontend/messages/fr.json`
- `frontend/messages/en.json`

## Solver - lecture correcte en 2026-04-10

Contrainte historique du lot initial :

- ne pas refondre `ExerciseSolver`
- faire une extension minimale

Verite terrain actuelle :

- la facade `ExerciseSolver.tsx` est conservee
- le runtime interleaved est porte par `useExerciseSolverController.ts`
- les helpers purs sont dans `exerciseSolverSession.ts` et `exerciseSolverFlow.ts`

Responsabilites fonctionnelles a conserver :

- detecter le mode `session=interleaved`
- afficher la progression de session
- afficher le bouton `Exercice suivant`
- afficher un ecran simple de fin quand la session est terminee

## UX et copy

Le message pedagogique doit rester simple, factuel et non infantilisant.

FR recommande :

- titre : `Session entrelacee`
- aide : `Ton cerveau doit reconnaitre la bonne strategie a chaque exercice. C'est plus exigeant, et c'est justement ce qui aide a memoriser.`

EN recommande :

- title : `Interleaved session`
- help : `Your brain has to identify the right strategy each time. It feels harder, and that is exactly what helps memory stick.`

## Criteres d'acceptation

1. Un troisieme CTA Quick Start apparait sur le dashboard.
2. Le clic lance une session entrelacee ou degrade proprement si impossible.
3. Le plan contient au moins 2 types differents eligibles.
4. Les exercices sont generes via l'API existante avec adaptation active.
5. L'utilisateur peut avancer exercice par exercice jusqu'a la fin.
6. Aucun changement de schema DB n'est necessaire.
7. Les messages FR/EN sont ajoutes proprement.

## Tests utiles aujourd'hui

### Backend

- service : selection des types eligibles
- service : construction du plan sans doublons consecutifs si possible
- endpoint : 200 avec plan valide
- endpoint : 409 quand pas assez de variete

### Frontend

- `frontend/__tests__/unit/app/exercises/InterleavedPage.test.tsx`
- `frontend/__tests__/unit/hooks/useExerciseSolverController.test.ts`
- `frontend/__tests__/unit/lib/exercises/exerciseSolverFlow.test.ts`
- `frontend/__tests__/unit/exercises/exerciseSolverSession.test.ts`

## Commandes de validation du lot initial

Backend :

```bash
pytest tests/unit/test_interleaved_practice_service.py tests/api/test_exercise_endpoints.py
black app/ server/ tests/ --check
```

Frontend :

```bash
cd frontend
npx tsc --noEmit
npm run test -- --runInBand
```

Si la suite complete est trop lourde, au minimum executer les tests cibles de la feature.

## Definition of done

F32 est termine si :

- le CTA dashboard est present
- l'endpoint de plan fonctionne
- le parcours complet session -> exercice -> suivant -> fin marche
- les tests cibles passent
- `tsc` et `black --check` passent avant commit

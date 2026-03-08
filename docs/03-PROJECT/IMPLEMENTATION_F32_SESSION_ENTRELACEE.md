# Implementation F32 - Session entrelacee

## Statut

- Statut : Implémente le 07/03/2026
- Durcissements post-implementation : 08/03/2026
- Portee : MVP sans migration DB, session ephemere cote client, endpoint de plan dedie

## Objectif

Implementer une version MVP de la feature backlog `F32 - Pratique Entrelacee` avec un risque technique modere et sans migration DB.

Objectif UX :

- depuis le dashboard, l'utilisateur lance une session guidee "Session entrelacee (10 min)"
- la session enchaine des exercices de types differents
- la difficulte reste adaptative via l'existant
- la session reste lisible, simple et non punitive

Reference produit :

- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` -> F32

## Hypothese MVP retenue

Pour limiter le risque :

- pas de nouvelle table
- pas de persistance serveur de session
- pas d'IA streaming dans F32 v1
- reutilisation maximale des briques existantes :
  - `QuickStartActions`
  - `POST /api/exercises/generate`
  - `ExerciseSolver`
  - adaptation dynamique F05

La session est ephemere cote client via `sessionStorage`.

## Durcissements post-implementation (08/03/2026)

Les lots de stabilisation appliques apres la livraison MVP ont cible les points
les plus fragiles du flux F32 :

- analytics EdTech `interleaved` : emission de `first_attempt` une seule fois
  par session, avec persistance `analytics.firstAttemptTracked` dans
  `sessionStorage`
- robustesse `save=true` : `POST /api/exercises/generate` renvoie maintenant
  une erreur `500` si la sauvegarde echoue ou ne retourne pas d'`id`
- UX d'erreur : toast explicite + fallback vers `/exercises` a l'entree de
  session ; toast explicite et conservation de la session lors de
  `Exercice suivant`
- DRY backend : resolution adaptive `age_group` factorisee dans
  `_resolve_adaptive_age_group_if_needed()` pour supprimer la duplication entre
  `generate_exercise` et `generate_exercise_api`
- hygiene quality gate : `black app/ server/ tests/ --check` remis au vert et
  nettoyage repo (`frontend/junit.xml`, `.gitignore`, import inutilise)

## Valeur pedagogique a respecter

Le coeur de la feature n'est pas "un bouton de plus". Il faut vraiment alterner les types pour forcer le choix de strategie.

Principes a conserver :

- 3 a 4 types differents par session
- pas de repetitions consecutives si evitables
- seulement des types deja pratiques par l'utilisateur
- seulement des types avec niveau suffisant pour eviter l'echec arbitraire
- micro-copy explicative : l'effort cognitif plus eleve est normal et utile

## Scope MVP

### Backend

Ajouter un endpoint dedie qui calcule un plan entrelace :

```text
GET /api/exercises/interleaved-plan?length=10
```

Comportement :

- auth requise
- retourne un plan ordonne de types d'exercices
- ne genere pas les exercices lui-meme
- laisse la generation reelle a `POST /api/exercises/generate`

Service dedie :

- `app/services/interleaved_practice_service.py`

Le handler ne doit contenir aucune logique SQL non triviale.

### Frontend

Ajouter un 3eme CTA dans le bloc dashboard Quick Start :

- label FR : `Session entrelacee`
- sous-texte : `Alterne plusieurs types pour mieux memoriser`

Flux :

1. L'utilisateur clique le CTA.
2. Le frontend appelle l'endpoint de plan.
3. Le plan est stocke en `sessionStorage`.
4. Le frontend ouvre une route dediee, par exemple :

```text
/exercises/interleaved
```

5. Cette page consomme le plan, genere le premier exercice via l'API existante, puis redirige vers :

```text
/exercises/{id}?session=interleaved
```

6. `ExerciseSolver` detecte le mode session et propose `Exercice suivant` apres soumission.
7. Au clic sur `Exercice suivant`, le prochain type du plan est genere puis affiche.
8. Quand le plan est vide, afficher un ecran simple de fin de session.

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

## Fichiers cibles probables

Backend :

- `app/services/interleaved_practice_service.py`
- `server/handlers/exercise_handlers.py`
- `server/routes/exercises.py`
- `tests/unit/test_interleaved_practice_service.py`
- `tests/api/test_exercise_endpoints.py`

Frontend :

- `frontend/components/dashboard/QuickStartActions.tsx`
- `frontend/hooks/useExercises.ts` ou nouveau hook dedie
- `frontend/app/exercises/interleaved/page.tsx`
- `frontend/components/exercises/ExerciseSolver.tsx`
- `frontend/messages/fr.json`
- `frontend/messages/en.json`
- tests frontend cibles si necessaire

## Contrat d'API recommande

Reponse succes :

```json
{
  "session_kind": "interleaved",
  "length": 10,
  "eligible_types": ["addition", "multiplication", "division"],
  "plan": ["addition", "multiplication", "division", "addition"],
  "message_key": "dashboard.quickStart.interleavedPedagogy"
}
```

Erreur metier :

```json
{
  "detail": {
    "code": "not_enough_variety",
    "message": "Pas assez de types pratiques recemment pour lancer une session entrelacee."
  }
}
```

## Reutilisation de l'existant

### Generation d'exercice

Pour chaque etape, reutiliser :

```text
POST /api/exercises/generate
```

Payload recommande :

```json
{
  "exercise_type": "addition",
  "adaptive": true,
  "save": true
}
```

Important :

- ne pas recalculer la difficulte dans F32
- laisser F05 faire son travail

### Solver

Ne pas refondre `ExerciseSolver`.

Faire une extension minimale :

- detecter le mode `session=interleaved`
- afficher progression de session
- afficher bouton `Exercice suivant`
- afficher ecran de fin simple quand la session est terminee

## Scope out

- aucune migration SQL
- aucune persistance de session en base
- aucun mode IA streaming
- aucun systeme de score dedie F32
- aucune refonte complete de la page `/exercises`
- aucun changement sur l'analytics F07 existant hors ajout minimal non bloquant

## UX et copy

Le message pedagogique doit etre simple, factuel et non infantilisant.

FR recommande :

- titre : `Session entrelacee`
- aide : `Ton cerveau doit reconnaitre la bonne strategie a chaque exercice. C'est plus exigeant, et c'est justement ce qui aide a memoriser.`

EN recommande :

- title : `Interleaved session`
- help : `Your brain has to identify the right strategy each time. It feels harder, and that is exactly what helps memory stick.`

## Criteres d'acceptation

1. Un 3eme CTA Quick Start apparait sur le dashboard.
2. Le clic lance une session entrelacee ou degrade proprement si impossible.
3. Le plan contient au moins 2 types differents eligibles.
4. Les exercices sont generes via l'API existante avec adaptation active.
5. L'utilisateur peut avancer exercice par exercice jusqu'a la fin.
6. Aucun changement de schema DB n'est necessaire.
7. Les messages FR/EN sont ajoutes proprement.

## Tests obligatoires

### Backend

- service : selection des types eligibles
- service : construction du plan sans doublons consecutifs si possible
- endpoint : 200 avec plan valide
- endpoint : 409 quand pas assez de variete

### Frontend

- test du flux de stockage / lecture du plan en `sessionStorage`
- test du CTA dashboard si possible
- test de la progression de session ou du helper associe

## Commandes de validation avant commit

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

## Contraintes pour Cursor

- faire F35 dans un commit separe avant F32
- ne pas inclure de refactor opportuniste hors scope
- pas de changements massifs sur `ExerciseSolver`
- pas de nouvelle dette i18n
- pas de break sur les analytics existantes Quick Start / first attempt

## Definition of done

F32 est termine si :

- le CTA dashboard est present
- l'endpoint de plan fonctionne
- le parcours complet session -> exercice -> suivant -> fin marche
- les tests cibles passent
- `tsc` et `black --check` passent avant commit

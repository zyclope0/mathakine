# F05 - Adaptation dynamique de difficulte

> Reference active
> Updated: 27/03/2026
> Statut: implemente, aligne sur F42

---

## 1. But

F05 regle aujourd'hui deux sujets complementaires :

1. resoudre une enveloppe pedagogique d'age
2. resoudre un second axe pedagogique de maitrise

Le modele canonique n'est plus "un seul niveau Star Wars".
La verite de difficulte fine est maintenant :

`age_group + pedagogical_band -> difficulty_tier`

Le tier F42 resultant sert ensuite a calibrer :
- la generation locale d'exercices
- la personnalisation des defis IA
- les recommandations
- certaines lectures API enrichies

Le detail technique transverse vit dans :
- [../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md](../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md)

Le guide simple equipe/produit vit dans :
- [DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md](DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md)

---

## 2. Modele actuel

### 2.1 Axe 1 - age pedagogique

Le systeme utilise un `age_group` canonique :
- `6-8`
- `9-11`
- `12-14`
- `15+`

Resolution preferentielle :
1. `users.age_group`
2. `preferred_difficulty` comme compatibilite
3. `grade_level`
4. fallback explicite `9-11` si aucun meilleur signal n'existe

Sources de verite :
- `app/core/user_age_group.py`
- `app/core/mastery_tier_bridge.py`

### 2.2 Axe 2 - bande pedagogique

La bande pedagogique est le second axe F42 :
- `discovery`
- `learning`
- `consolidation`

Elle provient principalement de signaux de progression et de diagnostic.

Mapping canonique actuel cote progression exercices :
- `mastery_level` 1-2 -> `discovery`
- `mastery_level` 3 -> `learning`
- `mastery_level` 4-5 -> `consolidation`

Source unique :
- `app/core/mastery_tier_bridge.py`

### 2.3 Tier F42

Le tier fin est calcule par la matrice F42 :

`difficulty_tier = age_band_index * 3 + pedagogical_band_index + 1`

Exemple :
- `9-11 + discovery` -> `4`
- `9-11 + learning` -> `5`
- `9-11 + consolidation` -> `6`

Source de verite :
- `app/core/difficulty_tier.py`

---

## 3. Flux runtime reel

### 3.1 Generation locale d'exercices

Le flux F42 actuel passe par :
- `app/services/exercises/exercise_generation_service.py`
- `app/services/exercises/adaptive_difficulty_service.py`

Le seam cle est `resolve_adaptive_context(...)`, qui retourne :
- `age_group`
- `pedagogical_band`
- `mastery_source`

Le comportement actuel est :
1. age stable resolu depuis le profil/fallback
2. bande resolue depuis `Progress.mastery_level` ou le diagnostic
3. fallback de bande a `learning` quand aucun signal plus fort n'est disponible
4. recalcul du `difficulty_tier` a partir de la vraie cellule `(age_group x band)`

Important :
- `resolve_adaptive_difficulty()` existe encore pour compatibilite legacy
- ce n'est plus la voie canonique de generation F42

### 3.2 Progression et evaluation

La base stocke encore des champs legacy :
- `Progress.mastery_level`
- `Progress.difficulty`
- `ChallengeProgress.mastery_level`
- difficulte legacy du diagnostic

Le bridge F42 projette ces champs vers :
- `canonical_age_group`
- `pedagogical_band`
- `difficulty_tier`

Source de verite :
- `app/core/mastery_tier_bridge.py`

### 3.3 Defis IA

Les defis IA reutilisent le contexte utilisateur F42 via :
- `app/services/challenges/challenge_generation_context.py`

Regle actuelle :
- si un age explicite est fourni, il gagne pour l'enveloppe
- si aucun age n'est fourni, le profil utilisateur est utilise
- la calibration pedagogique utilisateur reste injectee dans le prompt et la policy de difficulte

---

## 4. Place du legacy

Le legacy reste volontairement present, mais avec un role borne.

### 4.1 `difficulty`

Le champ legacy `difficulty` (`INITIE`, `PADAWAN`, `CHEVALIER`, `MAITRE`, `GRAND_MAITRE`) reste :
- en base
- dans certains contrats
- dans certains validateurs historiques

Il est acceptable comme couche de compatibilite.
Il ne doit plus etre considere comme la seule verite pedagogique.

### 4.2 `mastery_level`

Le `mastery_level` reste le signal source de progression.
Il n'est pas la verite finale de difficulte ; il est projete vers F42.

### 4.3 Difficultes du diagnostic

Le diagnostic IRT continue a stocker une difficulte legacy par type.
Cette representation est ensuite enrichie en F42 a la lecture.

---

## 5. QCM vs saisie libre

Le mode de reponse reste pilote par le diagnostic IRT par type.

Le frontend lit :
- `GET /api/diagnostic/status`

Et decide ensuite si le type peut passer en saisie libre.

Cette logique reste separee du tier F42 :
- le tier calibre la difficulte du contenu
- l'IRT par type calibre le mode de reponse

---

## 6. Ce qui est propre aujourd'hui

Le modele est considere propre si l'equipe respecte ces regles :

1. toute nouvelle logique fine part de `age_group`, `pedagogical_band` ou `difficulty_tier`
2. les champs legacy restent des adaptateurs de compatibilite
3. les libelles legacy ne sont pas exposes brut a l'utilisateur
4. les rangs publics de progression ne pilotent jamais la difficulte pedagogique

---

## 7. Ce qui reste volontairement non fait

Le systeme n'a pas encore cherche a :
- migrer la DB pour supprimer les champs legacy
- persister `pedagogical_band` partout comme champ canonique
- renommer tous les enums/colonnes historiques

Ce n'est pas un oubli : c'est un choix de transition maitrisee.

Le modele actuel est :
- viable en production
- propre pour le moyen terme
- evolutif tant que l'equipe ne recree pas une logique parallele

---

## 8. Fichiers de reference

### Backend

- `app/services/exercises/adaptive_difficulty_service.py`
- `app/core/mastery_tier_bridge.py`
- `app/core/difficulty_tier.py`
- `app/services/exercises/exercise_generation_service.py`
- `app/services/challenges/challenge_generation_context.py`
- `app/services/challenges/challenge_difficulty_policy.py`

### Frontend

- `frontend/hooks/useIrtScores.ts`
- `frontend/components/exercises/ExerciseSolver.tsx`
- `frontend/components/exercises/ExerciseModal.tsx`

### API

- `GET /api/diagnostic/status`
- `GET /api/users/me/progress`
- `GET /api/users/me/challenges/detailed-progress`

---

## 9. Reste eventuel a surveiller

Pas de blocage F05 immediat a ce stade.

Points a surveiller plus tard si l'adaptatif s'etend fortement :
- persistance plus large du canon F42
- analytics pedagogiques plus fines
- validation empirique des choix de fallback par tranche d'age

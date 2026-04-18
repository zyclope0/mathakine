# Plan Post-Beta - Feature B Exercise Skill State

> Plan actif post-beta
> Updated: 18/04/2026
> Statut: planifie, non lance

---

## 1. Decision

Feature B n'est **pas** lancee avant la beta.

Raison :
- la beta doit d'abord fermer les bugs visibles sur les exercices et les defis
- le cold start des types non IRT est deja couvert par Feature A
- Feature B ouvre un vrai chantier produit/backend :
  - migration DB
  - nouveau modele
  - nouveau service metier
  - cablage dans le flux de soumission
  - tests backend supplementaires

Conclusion :
- **avant beta** : stabilisation generation, validation, UX, bugs
- **apres beta** : fondation de l'etat adaptatif continu par type

---

## 2. But de Feature B

Passer d'un systeme base sur :
- diagnostic
- proxys
- seed profile
- progression recente

a un systeme avec etat adaptatif continu par `(user_id, exercise_type)` :
- `skill_score`
- `confidence`
- `attempts_count`
- `weighted_attempts`
- `source`

Important :
- ce state n'est **pas** expose tout de suite a l'utilisateur
- ce state n'est **pas** consomme tout de suite par `adaptive_difficulty_service.py`
- la premiere phase pose seulement la fondation robuste

---

## 3. Sequence recommandee

### Phase 0 - preconditions

Faire d'abord :
- correction des petits bugs exercices / defis
- lancement beta
- collecte de premiers retours terrain

### Phase 1 - fondation backend

Livrer :
- migration Alembic
- modele SQLAlchemy `ExerciseSkillState`
- service metier dedie
- mise a jour best-effort apres soumission d'exercice
- tests unitaires du service

Ne pas livrer encore :
- lecture du state dans la cascade adaptative
- affichage frontend
- promesse utilisateur de "niveau par type"

### Phase 2 - activation prudente

Quand la phase 1 est stable :
- lecture conditionnelle dans `adaptive_difficulty_service.py`
- seulement si `confidence` suffisante
- idealement derriere un flag de lecture

### Phase 3 - exposition produit

Uniquement apres donnees reelles stables :
- affichage pedagogique simplifie dans la progression
- jamais de jargon IRT
- jamais de score brut expose

---

## 4. Decisions de calibration retenues

### 4.1 Mapping tier -> item_difficulty_score

Convention interne, non calibree empiriquement :

```python
_TIER_TO_ITEM_DIFFICULTY = {
    "INITIE": 0.25,
    "PADAWAN": 1.0,
    "CHEVALIER": 2.0,
    "MAITRE": 3.0,
    "GRAND_MAITRE": 3.75,
}
```

### 4.2 Scale par type

```python
_TYPE_SCALE = {
    "addition": 0.75,
    "soustraction": 0.75,
    "multiplication": 0.80,
    "division": 0.80,
    "fractions": 1.00,
    "geometrie": 1.15,
    "texte": 1.40,
    "divers": 1.50,
}
```

### 4.3 Learning rate selon confiance

```python
def _learning_rate(confidence: float) -> float:
    if confidence < 0.33:
        return 0.35
    if confidence < 0.67:
        return 0.20
    return 0.10
```

### 4.4 Seeds initiaux

- `confidence = 0.20` pour un seed profil
- `confidence = 0.45` pour un seed issu d'un diagnostic deja disponible

### 4.5 Poids des tentatives

- `1.0` pour contenu nominal
- `0.6` pour exercice IA genere

---

## 5. Regle de mise a jour retenue

Forme cible :

```python
expected = sigmoid((state.skill_score - item_difficulty_score) / scale)
state.skill_score = clamp(
    state.skill_score + k * exercise_weight * (outcome - expected),
    0.0,
    4.0,
)
state.weighted_attempts += exercise_weight
state.attempts_count += 1
state.confidence = min(1.0, log1p(state.weighted_attempts) / log1p(25))
state.source = "observed"
```

Interpretation :
- reussir un exercice facile quand on est deja fort bouge peu
- rater un exercice facile fait baisser plus
- reussir un exercice difficile fait monter davantage
- rater un exercice difficile quand on est deja faible fait peu baisser

Ce modele est une fondation robuste pour l'apprentissage adaptatif continu.

---

## 6. Architecture recommandee

### 6.1 Table dediee

Ne pas etendre `Progress`.

Raison :
- `Progress` = historique de performance pedagogique
- `exercise_skill_states` = etat courant d'un estimateur adaptatif

Responsabilites distinctes.

### 6.2 Service dedie

Creer :

- `app/services/exercises/exercise_skill_state_service.py`

Responsabilites :
- lire l'etat existant
- l'initialiser si absent
- le mettre a jour apres une tentative
- resoudre un tier a partir de `skill_score`

### 6.3 Integration best-effort

Dans le flux de soumission :
- la tentative principale doit rester prioritaire
- si l'update du skill state casse :
  - log warning
  - ne pas casser la reponse utilisateur

Ce n'est pas du vrai "fire-and-forget".
C'est un side-effect **best-effort non bloquant** pour le metier principal.

---

## 7. Lot a faire en premier post-beta

### Lot 1 - fondation uniquement

Inclure :
- migration Alembic
- modele SQLAlchemy
- service metier
- tests unitaires
- hook apres soumission

Exclure :
- lecture dans `adaptive_difficulty_service.py`
- feature flag frontend
- affichage utilisateur
- refonte recommendation

C'est le meilleur premier lot :
- borne
- testable
- faible risque produit
- pas de changement UX

---

## 8. Ce qu'il ne faut pas faire dans le premier lot

- ne pas brancher tout de suite la lecture dans la cascade adaptative
- ne pas afficher les niveaux par type a l'utilisateur
- ne pas parler de "vraie calibration IRT" sur ces types
- ne pas dupliquer les mappings de calibration dans plusieurs services
- ne pas coupler ce state a `Progress`

---

## 9. Quand afficher les niveaux a l'utilisateur

Pas avant :
- existence de `skill_score + confidence`
- mise a jour sur plusieurs tentatives reelles
- seuil minimal de confiance

Et meme a ce stade :
- afficher une forme pedagogique simple
- ne pas afficher de score brut

Exemples acceptables :
- `Addition : a l'aise`
- `Texte : en progression`
- `Geometrie : a consolider`

Exemples a eviter :
- `theta = 1.84`
- `CHEVALIER 2.3`
- tout jargon psychometrique brut

---

## 10. Prompt Cursor recommande

```text
Contexte
Projet EdTech gamifie Next.js / Python. On veut preparer une Feature B post-beta : un systeme adaptatif continu par type d'exercice, base sur un etat de competence persistant par utilisateur et type (`skill_score`, `confidence`, etc.).

Important
- Ce lot est POST-BETA.
- Il ne faut PAS modifier l'UX frontend.
- Il ne faut PAS encore integrer la lecture de ce nouvel etat dans la selection adaptative globale.
- Le but de ce lot est uniquement de poser la fondation robuste :
  1. stockage
  2. service metier isole
  3. mise a jour best-effort apres une tentative
- Il ne faut PAS remplacer le systeme actuel `adaptive_difficulty_service.py` dans ce lot.

Pourquoi ce lot ne change pas le parcours utilisateur ni la logique metier visible
- aucune route frontend changee
- aucun ecran modifie
- aucune decision de difficulte visible encore branchee sur ce nouvel etat
- on ajoute seulement une couche de persistance et de calcul metier interne, prete pour une future activation

Objectif du lot
Implementer la fondation de Feature B :
- nouvelle table `exercise_skill_states`
- modele SQLAlchemy correspondant
- service metier isole `exercise_skill_state_service.py`
- mise a jour apres soumission d'exercice
- tests unitaires robustes

Regles d'architecture
- separation stricte des responsabilites
- pas de logique metier dans les handlers/controllers
- pas de duplication des constantes de mapping difficulte
- typage strict
- exceptions metier propres ou fail-open explicite quand l'update adaptatif est non critique
- zero changement frontend
- code production-ready

Decisions produit/techniques deja retenues
1. skill state par `(user_id, exercise_type)`
2. score continu interne : `skill_score` sur echelle `0.0 -> 4.0`
3. confiance interne : `confidence` sur `0.0 -> 1.0`
4. sources :
- `seeded`
- `diagnostic`
- `observed`

5. Mapping `tier -> item_difficulty_score`
- `INITIE = 0.25`
- `PADAWAN = 1.0`
- `CHEVALIER = 2.0`
- `MAITRE = 3.0`
- `GRAND_MAITRE = 3.75`

6. Scale par type
- `addition = 0.75`
- `soustraction = 0.75`
- `multiplication = 0.80`
- `division = 0.80`
- `fractions = 1.00`
- `geometrie = 1.15`
- `texte = 1.40`
- `divers = 1.50`

7. Learning rate selon confiance
- `confidence < 0.33 -> K = 0.35`
- `confidence < 0.67 -> K = 0.20`
- sinon `K = 0.10`

8. Seeds initiaux
- `confidence = 0.20` pour etat `seeded`
- `confidence = 0.45` pour etat initialise depuis un diagnostic deja existant

9. Poids tentative
- `1.0` si exercice non IA / nominal
- `0.6` si `exercise.is_ai_generated == True`

10. Update rule
- `expected = sigmoid((skill_score - item_difficulty_score) / scale)`
- `skill_score = clamp(skill_score + K * exercise_weight * (outcome - expected), 0.0, 4.0)`
- `weighted_attempts += exercise_weight`
- `attempts_count += 1`
- `confidence = min(1.0, log1p(weighted_attempts) / log1p(25))`
- apres premiere vraie reponse, `source = "observed"`

Perimetre strict
Modifier uniquement les zones necessaires parmi :
- modele SQLAlchemy / migration Alembic
- service metier exercices
- flux de soumission d'exercice backend
- tests unitaires backend

Ne pas modifier :
- frontend
- `adaptive_difficulty_service.py` pour lui faire consommer ce state
- logique de recommandation
- endpoint `irt-level`
- systeme challenge

Structure attendue

1. Migration Alembic
Creer une migration pour une table `exercise_skill_states` avec :
- `id` PK
- `user_id` FK `users.id` cascade delete
- `exercise_type` varchar(50) not null
- `skill_score` float not null default `1.0`
- `confidence` float not null default `0.20`
- `attempts_count` integer not null default `0`
- `weighted_attempts` float not null default `0.0`
- `source` varchar(20) not null default `seeded`
- `updated_at` timestamptz not null default `now()`
- unique constraint `(user_id, exercise_type)`
- index utile sur `(user_id, exercise_type)`

2. Modele SQLAlchemy
Creer / ajouter le modele `ExerciseSkillState` coherent avec les conventions du repo.
Prevoir un `__repr__` simple.
Pas de logique metier dans le modele.

3. Service metier dedie
Creer par exemple :
- `app/services/exercises/exercise_skill_state_service.py`

Ce service doit fournir au minimum :
- `get_or_init_state(db, user, exercise_type) -> ExerciseSkillState`
- `update_after_attempt(db, *, user, exercise, is_correct) -> ExerciseSkillState`
- `resolve_difficulty_from_state(state) -> str`

Responsabilites detaillees :

`get_or_init_state(...)`
- lit l'etat existant
- si absent :
  - initialise depuis diagnostic si signal exploitable
  - sinon seed profil/prior prudent
- persiste l'etat initial
- ne casse pas le flux metier si le seed echoue de maniere non critique : fail-open explicite et log propre

`update_after_attempt(...)`
- calcule `item_difficulty_score`
- calcule `scale` selon le type
- calcule `exercise_weight`
- applique la regle Rasch simplifiee
- met a jour `skill_score`, `confidence`, `weighted_attempts`, `attempts_count`, `source`
- clamp systematiquement les bornes
- met a jour `updated_at`

`resolve_difficulty_from_state(...)`
- convertit `skill_score` vers :
  - `INITIE`
  - `PADAWAN`
  - `CHEVALIER`
  - `MAITRE`
  - `GRAND_MAITRE`

4. Integration dans le flux de soumission
Localiser le flux metier ou une tentative d'exercice est validee et persistee.
Apres la persistance metier principale reussie, brancher une mise a jour best-effort :

- la tentative principale ne doit jamais etre annulee a cause du skill state
- si l'update du skill state echoue :
  - log warning explicite
  - ne pas remonter d'erreur utilisateur

Important :
- ne pas faire de faux async
- ne pas appeler ca "fire-and-forget"
- c'est un side-effect best-effort, non bloquant pour l'issue metier principale

5. Centralisation des constantes
Creer les constantes de calibration dans le service ou un mini module interne dedie.
Eviter toute duplication ulterieure.

6. Source initiale
Quand un etat est cree :
- si initialise depuis diagnostic reel -> `source="diagnostic"`
- sinon depuis profil / prior -> `source="seeded"`
- apres premiere tentative observee -> `source="observed"`

Tests attendus
Creer/adapter les tests unitaires backend pour couvrir au minimum :

A. Initialisation
1. etat absent + diagnostic disponible -> cree `source="diagnostic"` avec `confidence=0.45`
2. etat absent + pas de diagnostic -> cree `source="seeded"` avec `confidence=0.20`
3. etat existant -> pas de duplication

B. Update rule
4. reussir un exercice facile quand on est deja fort -> delta faible positif
5. rater un exercice facile quand on est fort -> delta negatif plus fort
6. reussir un exercice difficile quand on est plus faible -> delta positif significatif
7. rater un exercice difficile quand on est faible -> delta negatif faible
8. clamp score entre `0.0` et `4.0`
9. `source` passe bien a `observed`

C. Ponderation
10. exercice IA -> poids `0.6`
11. exercice non IA -> poids `1.0`

D. Conversion tier
12. `resolve_difficulty_from_state(...)` mappe correctement les plages

E. Integration
13. si update skill state leve une exception, la soumission principale reste valide

Contraintes fortes
- pas de lecture de ce state dans `adaptive_difficulty_service.py` dans ce lot
- pas de feature flag de lecture a implementer maintenant
- pas de changement frontend
- pas de `any`
- pas de refactor opportuniste large
- pas de duplication des mappings de difficulte existants si on peut factoriser proprement
- toute hypothese doit etre documentee brievement dans le code

Validation attendue
Dans `D:\\Mathakine` :
1. migration Alembic generee proprement
2. `python -m mypy ... --ignore-missing-imports` sur les fichiers modifies
3. `python -m black --check ...` sur les fichiers modifies
4. tests unitaires cibles verts
5. si la suite complete pytest locale reste lente, le signaler honnetement

Restitution attendue
- Resume court
- Fichiers crees / modifies
- Decisions de calibration implementees
- Resultats des checks
- Risques residuels
- Verdict : lot ferme ou non

Commit attendu
feat(adaptive): add persistent exercise skill state foundation
```

---

## 11. Decision actuelle

Ce plan est conserve pour l'apres-beta.

Ordre de priorite actuel :
1. finaliser les corrections de bugs exercices / defis
2. lancer la beta
3. collecter les retours reels
4. seulement ensuite lancer Feature B


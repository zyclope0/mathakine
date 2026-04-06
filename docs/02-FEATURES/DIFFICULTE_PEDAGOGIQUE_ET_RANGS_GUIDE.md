# Difficulté Pédagogique Et Rangs Publics — Guide Simple

> Date : 27/03/2026
> Statut : Référence active
> Complément métier du manifeste technique : [../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md](../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md)

---

## But

Ce document explique simplement comment fonctionne aujourd'hui :

1. la difficulté pédagogique du contenu
2. les rangs publics de progression

Il ne remplace pas le manifeste technique.

- ce guide = version simple, produit et équipe
- le manifeste = version technique, transverse et orientée code

---

## Règle Non Négociable

Il faut séparer strictement deux sujets :

### 1. Difficulté pédagogique

Elle sert à décider :

- quel contenu générer
- quel contenu recommander
- quel niveau proposer à un apprenant
- comment interpréter progression et diagnostic

### 2. Rang public de progression

Il sert à afficher :

- la progression du compte
- l'identité visible sur le profil
- le statut visible sur le dashboard, le classement et les badges

Le rang public ne doit jamais piloter la difficulté pédagogique.

---

## Le Schéma Simple

Le système de difficulté actuel repose sur 2 axes :

1. une tranche d'âge pédagogique
2. une bande pédagogique

Puis :

`age_group + pedagogical_band -> difficulty_tier`

En pratique :

- le profil utilisateur donne une enveloppe d'âge stable
- la progression réelle et le diagnostic donnent un signal pédagogique
- ce signal devient une bande :
  - `discovery`
  - `learning`
  - `consolidation`
- le croisement des deux donne un tier F42 de `1` à `12`

Ce tier est ensuite utilisé pour :

- la génération d'exercices
- la calibration des défis
- les recommandations
- certaines lectures API enrichies

Quand aucun signal de maîtrise plus fort n'existe encore, le fallback runtime actuel
reste volontairement neutre :

- `band fallback = learning`

Ce n'est pas une "vérité pédagogique absolue" ; c'est une décision de compatibilité
et de transition pour éviter un durcissement implicite du cold start.

---

## Exemple Concret

Pour un apprenant en `9-11` :

- `9-11 + discovery` -> tier `4`
- `9-11 + learning` -> tier `5`
- `9-11 + consolidation` -> tier `6`

Donc deux apprenants du même âge peuvent recevoir des contenus différents si leur bande pédagogique diffère.

---

## Ce Que Veut Dire Chaque Champ

| Champ                         | Signification                                                           | Statut actuel                     |
| ----------------------------- | ----------------------------------------------------------------------- | --------------------------------- |
| `age_group`                   | Enveloppe d'âge pédagogique                                             | Canonique                         |
| `pedagogical_band`            | Axe fin `discovery / learning / consolidation`                          | Canonique côté runtime            |
| `difficulty_tier`             | Cellule F42 finale `1..12`                                              | Canonique pour la difficulté fine |
| `difficulty`                  | Ancienne échelle `INITIE / PADAWAN / CHEVALIER / MAITRE / GRAND_MAITRE` | Legacy de compatibilité           |
| `mastery_level`               | Signal de progression `1..5`                                            | Legacy de compatibilité           |
| `difficulty_rating`           | Échelle publique `1.0..5.0` des défis                                   | Projection produit                |
| `current_level` / rang public | Progression du compte par points                                        | Gamification, pas difficulté      |

---

## Les Reliquats Legacy Qui Restent

Ils restent volontairement, mais avec un rôle limité.

### `difficulty = INITIE / PADAWAN / CHEVALIER / MAITRE / GRAND_MAITRE`

Ce champ reste :

- en base
- dans certains contrats API
- dans certains services historiques

Pourquoi c'est acceptable :

- il garantit la compatibilité
- il évite une migration immédiate risquée
- il sert encore de fallback dans certains modules

Ce qu'il ne faut plus faire :

- l'utiliser comme seule vérité métier de la difficulté
- en afficher la valeur brute à l'utilisateur

### `mastery_level = 1..5`

Ce champ reste pour la progression exercices.

Pourquoi c'est acceptable :

- le stockage historique reste stable
- le bridge F42 projette ce signal vers `pedagogical_band` puis `difficulty_tier`

### Difficulté legacy du diagnostic

Le diagnostic stocke encore une difficulté historique par type.

Pourquoi c'est acceptable :

- l'algorithme IRT existant reste simple
- la projection F42 se fait ensuite à la lecture

### `difficulty_rating` des défis

Ce champ reste aussi.

Pourquoi c'est acceptable :

- c'est une bonne échelle publique simple
- elle complète le tier au lieu de le remplacer

---

## Ce Qui Est Considéré Comme Propre Aujourd'hui

La solution actuelle est considérée comme propre si l'équipe respecte ces règles :

1. Toute nouvelle logique pédagogique part de `age_group`, `pedagogical_band` ou `difficulty_tier`
2. Le legacy reste un adaptateur de compatibilité
3. Les surfaces utilisateur affichent des libellés neutres, pas `PADAWAN` ou `MAITRE`
4. Les rangs publics ne sont jamais utilisés pour calibrer le contenu

---

## Est-Ce Suffisamment Clean ?

Réponse courte :

- oui pour la production actuelle
- oui pour le moyen terme
- non, ce n'est pas encore le modèle final idéal

La solution actuelle est viable parce que :

- il y a maintenant un centre de gravité clair : `age_group + band -> tier`
- les bridges legacy sont centralisés
- les boundaries importantes sont recâblées

Ce n'est pas encore parfait parce que :

- plusieurs représentations coexistent encore
- tout le canon F42 n'est pas persisté partout
- certains champs legacy restent dans la DB et les contrats

Conclusion pratique :

- pas de gros refactor urgent requis
- mais si le produit étend fortement l'adaptatif, l'analytics ou le reporting, un refactor plus fort deviendra utile

---

## Règles Pour Les Prochains Lots

### À faire

- utiliser `difficulty_tier` pour toute logique fine
- utiliser `pedagogical_band` pour le second axe pédagogique
- garder les labels legacy hors de l'UI apprenant

### À éviter

- créer une nouvelle logique parallèle de difficulté
- utiliser le rang public comme proxy de niveau scolaire
- exposer un champ legacy brut dans une nouvelle surface produit

---

## Ce Que Voit L’admin — Exercices (`/admin/content`)

État documenté après FFI-L14 (architecture frontend livrée, pas « produit final » sur la difficulté tant que le contrat liste est incomplet) :

- La **liste** n’affiche plus des libellés type Star Wars comme référence lisible : affichage **transitoire** (niveaux neutres ou `Palier n` si `difficulty_tier` est renvoyé par l’API liste).
- Les **modales** d’édition/création continuent d’utiliser les **valeurs legacy** attendues par l’API pour enregistrer la difficulté.
- Pour un alignement **définitif** avec le canon F42 (`difficulty_tier`), il faut que la **liste admin** expose ce champ de manière **fiable** ; sinon le gap reste côté **contrat/API**, pas un échec du découpage UI.

---

## Références Techniques

Pour la vérité technique complète :

- [../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md](../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md)
- [../../app/core/difficulty_tier.py](../../app/core/difficulty_tier.py)
- [../../app/core/mastery_tier_bridge.py](../../app/core/mastery_tier_bridge.py)
- [../../app/services/exercises/adaptive_difficulty_service.py](../../app/services/exercises/adaptive_difficulty_service.py)
- [../../app/services/challenges/challenge_generation_context.py](../../app/services/challenges/challenge_generation_context.py)

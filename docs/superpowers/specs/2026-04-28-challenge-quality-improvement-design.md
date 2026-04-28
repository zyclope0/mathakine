# Challenge Quality Improvement — Design Spec

> **[CLOS — livré 2026-04-28]** Toutes les tasks implémentées et vérifiées (commits `74ffb14`→`33bb325`). VarietySeed, 4 sections qualité, filtres âge, guard IndexError, déplacement VALID_CHALLENGE_TYPES.

**Date :** 2026-04-28
**Statut :** Approuvé par le founder — prêt pour implémentation

---

## Objectif

Améliorer la qualité pédagogique, l'engagement et la variété des défis générés par l'IA dans Mathakine, sans modifier l'architecture technique existante (générateurs, validators, renderers, schémas JSON).

Les dimensions ciblées, par ordre de priorité :

| Priorité | Dimension | Problème constaté |
|----------|-----------|-------------------|
| 50% | Engagement de la situation | Énoncés secs, contexte décoratif ou absent |
| 25% | Répétitivité cognitive | Même mécanique de résolution maquillée d'un décor différent |
| 15% | Qualité des distracteurs | Distracteurs arbitraires, non ancrés dans des erreurs réelles |
| 10% | Valeur pédagogique de la sortie | `solution_explanation` plate, indices sans direction |

---

## Architecture

Aucun changement aux schémas JSON, aux validators, ni aux renderers.

| Fichier | Action |
|---------|--------|
| `app/services/challenges/challenge_prompt_sections.py` | Modifier — 4 nouvelles sections qualité |
| `app/services/challenges/challenge_variety_seeds.py` | **Créer** — bibliothèque contextes + mécanismes |
| `app/services/challenges/challenge_prompt_composition.py` | Modifier — `build_challenge_user_prompt()` accepte un `VarietySeed` |
| `app/services/challenges/challenge_ai_service.py` | Modifier — appel `pick_variety_seed()` + log |

**Flux de génération (après implémentation) :**

```
challenge_ai_service.py
  → pick_variety_seed(challenge_type)   ──→  challenge_variety_seeds.py
  → build_challenge_system_prompt()     ──→  challenge_prompt_sections.py (enrichi)
  → build_challenge_user_prompt(seed=…) ──→  challenge_prompt_composition.py (injecte le seed)
  → appel OpenAI SSE
```

---

## Partie 1 — Nouvelles sections du prompt système

### 1.1 `TEXT_STORYTELLING_PRINCIPLES` *(remplace `TEXT_MATHLOG_CONTEXT`)*

```
STORYTELLING PÉDAGOGIQUE :
Chaque défi doit donner du sens aux données, pas simplement demander de calculer.
Le contexte doit rendre le raisonnement nécessaire — pas le décorer.

Formats de situations efficaces :
- Décision à prendre : quelle option est la plus avantageuse ?
- Comparaison surprenante : une réalité contre-intuitive à valider ou réfuter
- Mission concrète : une tâche claire avec un objectif défini
- Erreur à détecter : un résultat ou un raisonnement incorrect à identifier
- Stratégie à choisir : plusieurs chemins, un seul optimal
- Optimisation : comment faire mieux avec les contraintes données
- Paradoxe ou surprise : une situation qui défie l'intuition première

Domaines concrets recommandés : architecture, jeux de société, cuisine, musique,
sport, cryptographie, transport, bibliothèque, nature, construction, cartographie.

RÈGLE : éviter les contextes purement décoratifs (pirates, dragons, bonbons)
s'ils ne servent pas directement le raisonnement.
Si le contexte peut être supprimé sans changer le problème, il ne sert à rien.
```

### 1.2 `TEXT_ENGAGEMENT_PRINCIPLES` *(nouveau)*

```
ENGAGEMENT :
Le titre doit donner envie d'ouvrir le défi : question, mission, anomalie, paradoxe.
  ✅ BON  : "Qui a volé le code ?" / "Le pont le plus court" / "Trois couleurs suffisent ?"
  ❌ MAUVAIS : "Problème de probabilité" / "Suite logique 3" / "Défi de déduction"

La description pose la situation en 1-2 phrases : micro-contexte → données utiles → question.
Ne pas poser la question principale avant d'avoir donné les données nécessaires.
Elle doit rendre la question inévitable — l'apprenant doit vouloir résoudre.

La solution_explanation répond à "pourquoi ça marche", pas seulement "comment on calcule".
L'apprenant doit comprendre quelque chose de nouveau après l'avoir lue — même avec la bonne réponse.
```

### 1.3 `TEXT_ACCESSIBILITY_COGNITIVE` *(nouveau)*

```
ACCESSIBILITÉ COGNITIVE :
- 6-8 ans  : phrases ≤ 12 mots, 1 seule consigne, objets concrets uniquement
- 9-11 ans : phrases ≤ 20 mots, vocabulaire du quotidien, pas de termes techniques
- 12+ ans  : vocabulaire précis acceptable, mais une phrase par idée

Ordre recommandé : micro-contexte → données utiles → question.
Exceptions valides : une anomalie ou un paradoxe peut ouvrir le défi si ça renforce
l'engagement sans créer d'ambiguïté. La règle absolue est : ne jamais poser la question
principale avant d'avoir fourni les données nécessaires pour y répondre.

Test d'ambiguïté : si la question peut être lue de deux façons, réécrire
jusqu'à ce qu'il n'y ait qu'une seule interprétation possible.
```

### 1.4 `TEXT_DISTRACTOR_COGNITIVE` *(nouveau — complète la politique QCM existante)*

```
QUALITÉ DES DISTRACTEURS :
Chaque distracteur cible une erreur de raisonnement réelle — pas une valeur arbitraire.
Les distracteurs doivent provenir d'erreurs différentes, pas de variantes du même mauvais calcul.

Erreurs types à modéliser :
- Erreur d'opération : bon contexte, mauvaise opération (addition au lieu de ×)
- Erreur de lecture : données mal interprétées (total au lieu de favorable)
- Erreur d'étape : raisonnement correct mais incomplet (étape oubliée)
- Erreur d'intuition : réponse "qui semble juste" mais fausse (piège heuristique)

Contraintes de forme :
- Longueurs et formats identiques entre toutes les options
- Aucun distracteur éliminable par évidence de format ou syntaxe
```

### 1.5 Intégration dans `build_challenge_system_prompt()`

Ordre des sections après modification :

```python
parts = [
    TEXT_ROLE_HEADER,
    TEXT_TYPE_LOCK_TEMPLATE,
    _age_group_block(params),
    TEXT_TYPES_COMPACT,
    TEXT_STORYTELLING_PRINCIPLES,      # remplace TEXT_MATHLOG_CONTEXT
    TEXT_ENGAGEMENT_PRINCIPLES,        # nouveau
    TEXT_ACCESSIBILITY_COGNITIVE,      # nouveau
    TEXT_HINTS_RULES,
    TEXT_DISTRACTOR_COGNITIVE,         # nouveau
    VISUAL_DATA_SECTION_BY_TYPE.get(ct, TEXT_VISUAL_DATA_FALLBACK),
    TEXT_VAL_INTRO,
    type_validation,
    TEXT_VAL_FINAL,
    # TEXT_PATTERN_EXAMPLES si ct == "pattern"
    TEXT_LATEX_RULES,
    TEXT_JSON_CONTRACT_TEMPLATE,
    TEXT_DIFFICULTY_RULES,
]
```

---

## Partie 2 — Bibliothèque de seeds (`challenge_variety_seeds.py`)

### 2.1 Dataclass

```python
@dataclass(frozen=True)
class VarietySeed:
    narrative_context: str        # domaine situationnel
    resolution_mechanism: str     # famille de mécanisme cognitif
    cognitive_skill: str = ""     # future : déduction, inhibition, séquençage…
    min_level: str = ""           # future : beginner, intermediate, advanced, adult
```

### 2.2 `NARRATIVE_CONTEXTS`

18 domaines concrets couvrant des univers variés :

```python
NARRATIVE_CONTEXTS = [
    "une bibliothèque où les livres sont classés par code secret",
    "un atelier de menuiserie avec des planches de longueurs différentes",
    "une cuisine de restaurant avec des recettes et des contraintes d'ingrédients",
    "un réseau de pistes cyclables entre quartiers",
    "un entrepôt logistique avec des colis à acheminer",
    "une serre botanique avec des espèces et des conditions de culture",
    "un studio de musique avec des partitions et des rythmes",
    "un chantier de construction avec des matériaux et des plans",
    "une compétition sportive avec des résultats à analyser",
    "un atelier de cartographie avec des distances et des routes",
    "une salle des codes avec des messages à déchiffrer",
    "un club d'astronomie avec des trajectoires et des distances",
    "un marché alimentaire avec des prix, poids et quantités",
    "un atelier de robots avec des programmes à corriger",
    "un studio d'animation avec des séquences d'images",
    "une école d'architecture avec des plans et contraintes spatiales",
    "un réseau ferroviaire avec des horaires et correspondances",
    "un laboratoire avec des expériences à interpréter",
]
```

### 2.3 `RESOLUTION_MECHANISMS_BY_TYPE`

Mécanismes avancés conservés pour tous les types — la formulation dans le défi s'adapte
au niveau cible via les sections de calibrage du prompt système.

```python
RESOLUTION_MECHANISMS_BY_TYPE = {
    "coding": [
        "décalage de lettres (César, décalage non fourni)",
        "substitution alphabétique par mot-clé à déduire",
        "inversion partielle ou totale du message",
        "lecture en grille (transposition de colonnes)",
        "coordonnées dans un tableau comme index de lettres",
        "table de symboles personnalisés à reconstituer",
        "indices croisés entre deux messages partiels",
        "erreur à détecter dans un code presque correct",
        "code à compléter (début fourni, fin à retrouver)",
    ],
    "sequence": [
        "progression arithmétique à différences variables",
        "suite géométrique (×r, r non entier possible)",
        "suite récursive type Fibonacci ou variante",
        "alternance de deux sous-suites entrelacées",
        "suite quadratique (différences secondes constantes)",
        "suite de carrés ou cubes perturbée",
        "règle composite alternée (×2 puis +3)",
        "terme manquant au milieu de la suite (pas à la fin)",
        "plusieurs inconnues à retrouver simultanément",
    ],
    "pattern": [
        "Latin square (chaque symbole une fois par ligne et colonne)",
        "rotation cyclique (chaque ligne = précédente décalée)",
        "symétrie axiale à compléter",
        "règle composite (position ET couleur combinées)",
        "erreur à identifier dans une grille presque correcte",
        "progression de formes avec contrainte croisée",
    ],
    "deduction": [
        "bijection simple (2 catégories, déduction directe)",
        "bijection triple (3 catégories, élimination progressive)",
        "contraintes d'ordre temporel (avant/après uniquement)",
        "contraintes d'adjacence ou de voisinage",
        "indices négatifs seulement (aucun positif direct)",
        "mix positif/négatif avec un piège de symétrie",
    ],
    "probability": [
        "tirage sans remise en 1 étape",
        "double tirage indépendant (avec remise)",
        "probabilité conditionnelle (Bayes simplifié)",
        "urne choisie aléatoirement, tirage dedans",
        "événement complémentaire (P(pas A))",
        "problème inverse : trouver la composition, pas la proba",
    ],
    "graph": [
        "chemin le plus court avec poids (Dijkstra)",
        "arbre couvrant minimal (Kruskal/Prim)",
        "coloration minimale (nombre de couleurs)",
        "circuit : passer par chaque arête exactement une fois",
        "composantes connexes (graphe fragmenté)",
        "chemin hamiltonien (passer par chaque nœud une fois)",
    ],
    "chess": [
        "mat en 1 coup (tactique simple)",
        "mat en 2 coups avec ligne forcée",
        "fourchette (attaque simultanée deux pièces)",
        "clouage (pièce clouée contre le roi)",
        "promotion de pion avec conversion immédiate",
        "meilleur coup défensif (éviter le mat)",
    ],
    "visual": [
        "symétrie axiale (compléter le miroir)",
        "rotation (deviner l'orientation manquante)",
        "matrice de règles (lignes × colonnes → case ?)",
        "case manquante dans une séquence spatiale",
        "repérage d'une erreur dans une grille symétrique",
        "reconstruction d'un pattern partiellement caché",
    ],
    "puzzle": [
        "ordre chronologique par indices indirects",
        "tri par priorité avec contraintes combinées",
        "ordre logique cause → effet (chaîne de dépendances)",
        "reconstruction par exclusions uniquement",
    ],
    "riddle": [
        "contraintes numériques croisées (âge, date, valeur)",
        "raisonnement par l'absurde (éliminer l'impossible)",
        # Mécanismes avancés/adulte — réservés aux niveaux 12+ ou énigmes explicitement linguistiques
        "auto-référence (la réponse est cachée dans l'énoncé)",  # adulte / avancé
        "double sens à démêler",                                  # adulte / avancé
        "métaphore à interpréter puis résoudre",                  # adulte / avancé
    ],
}
```

**Note :** les mécanismes avancés (Dijkstra, Bayes, auto-référence…) restent dans la bibliothèque.
La règle d'adaptation est dans le prompt : *"le mécanisme peut être avancé — adapter la formulation,
le vocabulaire et la complexité au groupe d'âge cible."*

### 2.4 `pick_variety_seed()`

```python
def pick_variety_seed(challenge_type: str) -> VarietySeed:
    """Tire un seed aléatoire pour le type donné. Retourne un seed vide si le type est inconnu."""
    mechanisms = RESOLUTION_MECHANISMS_BY_TYPE.get(
        challenge_type.strip().lower(), []
    )
    if not mechanisms:
        return VarietySeed(narrative_context="", resolution_mechanism="")
    return VarietySeed(
        narrative_context=random.choice(NARRATIVE_CONTEXTS),
        resolution_mechanism=random.choice(mechanisms),
    )
```

---

## Partie 3 — Intégration dans le prompt utilisateur

### 3.1 Signature étendue de `build_challenge_user_prompt()`

```python
def build_challenge_user_prompt(
    challenge_type: str,
    age_group: str,
    prompt: str,
    locale: str = "fr",
    variety_seed: VarietySeed | None = None,   # nouveau paramètre optionnel
) -> str:
```

### 3.2 Bloc ORIENTATION DE VARIÉTÉ

Injecté après les contraintes obligatoires, **avant** la demande personnalisée utilisateur.
Le seed est une suggestion faible — la demande personnalisée reste prioritaire dans les limites
du type et du niveau cible.

```python
if variety_seed and (variety_seed.narrative_context or variety_seed.resolution_mechanism):
    user_prompt += "\n\nORIENTATION DE VARIÉTÉ (suggestions — type et niveau restent absolus) :"
    if variety_seed.narrative_context:
        user_prompt += f"\n- Contexte narratif : {variety_seed.narrative_context}"
    if variety_seed.resolution_mechanism:
        user_prompt += f"\n- Mécanisme de résolution : {variety_seed.resolution_mechanism}"
    user_prompt += (
        "\nEn cas de conflit :"
        "\n  - le type de défi et le groupe d'âge sont prioritaires ;"
        "\n  - la demande personnalisée utilisateur est prioritaire sur l'orientation de variété ;"
        "\n  - l'orientation de variété est une suggestion, jamais une obligation."
        f"\nIMPORTANT : le contrat visual_data du type {challenge_type} et le schéma JSON"
        " restent inchangés. Le seed oriente le contexte narratif et le raisonnement,"
        " pas la structure des données."
        "\nNote : le mécanisme peut être avancé — adapter la formulation, "
        "le vocabulaire et la complexité au groupe d'âge cible."
    )
```

### 3.3 Hiérarchie des contraintes

**Garde-fous permanents — non contournables par le seed ni par la demande utilisateur :**
- Sections qualité du prompt système (storytelling, accessibilité cognitive, distracteurs, engagement)
- Type de défi (verrou absolu)
- Groupe d'âge / niveau cible

**Suggestions runtime (du plus fort au plus faible) :**
```
1. Demande personnalisée utilisateur (dans les limites des garde-fous permanents)
2. Orientation de variété / seed (suggestion faible, jamais une obligation)
```

La demande utilisateur peut orienter le contexte ou le style, mais ne peut pas contourner
les règles d'accessibilité, de storytelling ou de qualité des distracteurs.

### 3.4 Appel dans `challenge_ai_service.py`

```python
from app.services.challenges.challenge_variety_seeds import pick_variety_seed

# Dans generate_challenge_stream(), avant build_challenge_user_prompt()
seed = pick_variety_seed(challenge_type)
logger.debug(
    "Challenge variety seed — type={} context={} mechanism={}",
    challenge_type,
    seed.narrative_context,
    seed.resolution_mechanism,
)
user_prompt = build_challenge_user_prompt(
    challenge_type, age_group, prompt, locale, variety_seed=seed
)
```

**Note logging :** utiliser les placeholders `{}` avec arguments positionnels. Ne pas utiliser `%s`.
Pour du contexte structuré, utiliser `logger.bind(...)`, pas `extra={…}` style stdlib
(celui-ci crée un champ imbriqué `extra["extra"]` non conforme à la convention projet).

---

## Risques et mitigations

### Risque 1 — Rejet du validateur

**Problème :** un seed pourrait suggérer un mécanisme que l'IA interprète comme nécessitant
une structure `visual_data` différente de celle attendue par le validator du type.
Exemple : seed "lecture en grille" pour coding → AI tente d'ajouter une structure grid
non conforme au schéma coding.

**Mitigation :**
- Le bloc ORIENTATION DE VARIÉTÉ doit inclure explicitement :
  `"Le contrat visual_data du type {challenge_type} et le schéma JSON restent inchangés.
  Le seed oriente le contexte narratif et le raisonnement, pas la structure des données."`
- Les mécanismes dans `RESOLUTION_MECHANISMS_BY_TYPE` doivent décrire des familles
  de raisonnement, pas des structures de données. Reformuler tout mécanisme qui
  implique un format visuel spécifique.
- Si le taux de rejet validator augmente après déploiement, désactiver le seed
  pour le type concerné via un flag dans `RESOLUTION_MECHANISMS_BY_TYPE`
  (liste vide = pas d'injection).

### Risque 2 — Taille du prompt et troncature JSON

**Problème :** le prompt système a été optimisé après des incidents de JSON tronqué.
Les 4 nouvelles sections ajoutent ~2 000–2 500 caractères (~500–600 tokens estimés).
Un dépassement de budget peut provoquer latence accrue ou troncature en fin de génération.

**Mitigation — mesure obligatoire avant et après :**

1. **Baseline avant implémentation** : capturer `challenge_system_prompt_stats()` pour
   tous les types × groupes d'âge avant toute modification.

2. **Budget delta max** : +20 % de caractères par rapport au baseline, ou +600 tokens
   absolus — le premier seuil atteint déclenche un échec de test.

3. **Test de garde** à ajouter dans `tests/unit/` :

```python
import pytest
from app.services.challenges.challenge_prompt_composition import (
    challenge_system_prompt_stats,
)

CHALLENGE_TYPES = [
    "sequence", "pattern", "visual", "puzzle", "graph",
    "riddle", "deduction", "probability", "coding", "chess",
]
AGE_GROUPS = ["6-8", "9-11", "12-14", "15-17", "adulte"]

# Seuil absolu — à recalibrer après mesure baseline
MAX_PROMPT_CHARS = 8_000

@pytest.mark.parametrize("challenge_type", CHALLENGE_TYPES)
@pytest.mark.parametrize("age_group", AGE_GROUPS)
def test_system_prompt_size_budget(challenge_type, age_group):
    stats = challenge_system_prompt_stats(challenge_type, age_group)
    assert stats["chars"] <= MAX_PROMPT_CHARS, (
        f"Prompt trop long pour {challenge_type}/{age_group} : "
        f"{stats['chars']} chars > {MAX_PROMPT_CHARS} limite. "
        "Réduire les nouvelles sections ou consolider des sections existantes."
    )
```

4. **Si le budget est dépassé** : consolider `TEXT_ACCESSIBILITY_COGNITIVE` et
   `TEXT_ENGAGEMENT_PRINCIPLES` en une section unique, ou réduire les exemples
   dans `TEXT_STORYTELLING_PRINCIPLES`. La règle est : qualité > volume de texte.

---

## Hors scope

- Schémas JSON des défis (aucun champ ajouté)
- Validators et renderers (inchangés)
- Prompt système par type (`VISUAL_DATA_SECTION_BY_TYPE`, `VALIDATION_SECTION_BY_TYPE`) — inchangés
- `challenge_generation_context.py` et calibration F42 — inchangés
- Tests de génération bout-en-bout (nécessitent des mocks OpenAI complexes)
- Interface utilisateur

---

## Extensions futures (non implémentées dans cette version)

| Champ | Usage prévu |
|-------|-------------|
| `VarietySeed.cognitive_skill` | Préciser la compétence cognitive mobilisée (déduction, inhibition, séquençage…) |
| `VarietySeed.min_level` | Filtrer les mécanismes avancés selon le niveau cible (beginner / adult) |

---

## Fichiers touchés — résumé

| Fichier | Lignes estimées |
|---------|-----------------|
| `challenge_prompt_sections.py` | +~80 lignes (4 nouvelles constantes + 1 liste mise à jour) |
| `challenge_variety_seeds.py` | ~100 lignes (nouveau fichier) |
| `challenge_prompt_composition.py` | +~20 lignes (signature + bloc d'injection) |
| `challenge_ai_service.py` | +~5 lignes (import + seed + log + appel) |

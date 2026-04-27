# Challenge Quality Improvement — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Améliorer la qualité pédagogique et la variété des défis générés par l'IA via enrichissement du prompt système (4 nouvelles sections) et injection dynamique d'un `VarietySeed` (contexte narratif + mécanisme cognitif) au moment de chaque appel.

**Architecture:** Approche hybride : sections qualité dans le prompt système (garde-fous permanents), seed aléatoire par type injecté dans le prompt utilisateur (suggestion faible). Nouveau fichier `challenge_variety_seeds.py` isolé. Modification légère de `build_challenge_user_prompt()` (paramètre optionnel). Service IA orchestre l'appel sans logique métier propre.

**Tech Stack:** Python 3.12, loguru, pytest, modules `challenge_prompt_sections.py`, `challenge_prompt_composition.py`, `challenge_ai_service.py`

---

## Baseline mesuré (2026-04-28, avant toute modification)

```
Chars min  : 7 074  (types courts, groupes standards)
Chars max  : 8 776  (chess / 9-11)
Tokens max : ~2 194
```

Budget autorisé après implémentation : **MAX_PROMPT_CHARS = 11 000** (+25 %).
Si une mesure post-implémentation dépasse 11 000, consolider `TEXT_ACCESSIBILITY_COGNITIVE`
et `TEXT_ENGAGEMENT_PRINCIPLES` en une seule section.

---

## Fichiers

| Fichier | Action | Rôle |
|---------|--------|------|
| `tests/unit/test_challenge_prompt_size_budget.py` | Créer | Guard test taille prompt — 50 combinaisons type × âge |
| `app/services/challenges/challenge_variety_seeds.py` | Créer | VarietySeed dataclass + bibliothèques + pick_variety_seed() |
| `app/services/challenges/challenge_prompt_sections.py` | Modifier | +4 constantes qualité |
| `app/services/challenges/challenge_prompt_composition.py` | Modifier | Nouvel ordre sections + paramètre variety_seed |
| `app/services/challenges/challenge_ai_service.py` | Modifier | Import + appel pick_variety_seed + log |

---

## Task 1 — Guard test taille du prompt

**Files:**
- Create: `tests/unit/test_challenge_prompt_size_budget.py`

Ce test mesure la taille du prompt système pour chaque combinaison type × groupe d'âge.
Il doit PASSER avant les modifications (baseline < 11 000) et PASSER après (delta contrôlé).
Il n'est pas un test TDD classique : c'est un garde-fou de régression de taille.

- [ ] **Step 1 : Écrire le test**

```python
# tests/unit/test_challenge_prompt_size_budget.py
"""Guard test — prompt système ne doit pas dépasser MAX_PROMPT_CHARS chars.

Baseline mesuré le 2026-04-28 avant implémentation :
  min=7074 chars, max=8776 chars (chess/9-11).
Budget post-implémentation : 11 000 chars (+25 %).
Si un type dépasse, consolider les nouvelles sections dans challenge_prompt_sections.py.
"""
import pytest

from app.services.challenges.challenge_prompt_composition import (
    challenge_system_prompt_stats,
)

CHALLENGE_TYPES = [
    "sequence", "pattern", "visual", "puzzle", "graph",
    "riddle", "deduction", "probability", "coding", "chess",
]
AGE_GROUPS = ["6-8", "9-11", "12-14", "15-17", "adulte"]

# Seuil = baseline_max(8776) × 1.25, arrondi au millier supérieur
MAX_PROMPT_CHARS = 11_000


@pytest.mark.parametrize("challenge_type", CHALLENGE_TYPES)
@pytest.mark.parametrize("age_group", AGE_GROUPS)
def test_system_prompt_size_budget(challenge_type: str, age_group: str) -> None:
    """Le prompt système ne doit pas dépasser MAX_PROMPT_CHARS caractères."""
    stats = challenge_system_prompt_stats(challenge_type, age_group)
    assert stats["chars"] <= MAX_PROMPT_CHARS, (
        f"Prompt trop long — {challenge_type}/{age_group} : "
        f"{stats['chars']} chars > {MAX_PROMPT_CHARS} limite. "
        "Réduire les nouvelles sections ou consolider dans challenge_prompt_sections.py."
    )
```

- [ ] **Step 2 : Vérifier que le test PASSE avec le code actuel (baseline)**

```bash
python -m pytest tests/unit/test_challenge_prompt_size_budget.py -v
```

Expected : **50 PASSED** (10 types × 5 âges). Tous sous 8 776 < 11 000.

- [ ] **Step 3 : Commit**

```bash
git add tests/unit/test_challenge_prompt_size_budget.py
git commit -m "test(prompt): add size budget guard — baseline max=8776 chars, limit=11000"
```

---

## Task 2 — Créer `challenge_variety_seeds.py`

**Files:**
- Create: `app/services/challenges/challenge_variety_seeds.py`

Module autonome, zéro dépendance sur le reste du projet (seulement `random` et `dataclasses`).

- [ ] **Step 1 : Créer le fichier**

```python
# app/services/challenges/challenge_variety_seeds.py
"""
Bibliothèque de seeds de variété pour la génération IA des défis (lot Qualité).

Chaque seed injecte deux suggestions dans le prompt utilisateur :
- narrative_context : domaine situationnel concret
- resolution_mechanism : famille de mécanisme cognitif propre au type

Le seed est une suggestion faible — type, âge et contrat visual_data restent absolus.
"""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class VarietySeed:
    narrative_context: str        # domaine situationnel
    resolution_mechanism: str     # famille de mécanisme cognitif
    cognitive_skill: str = ""     # future : déduction, inhibition, séquençage…
    min_level: str = ""           # future : beginner, intermediate, advanced, adult


NARRATIVE_CONTEXTS: list[str] = [
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

RESOLUTION_MECHANISMS_BY_TYPE: dict[str, list[str]] = {
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
        # Mécanismes avancés/adulte — réservés aux niveaux 12+ ou énigmes linguistiques
        "auto-référence (la réponse est cachée dans l'énoncé)",  # adulte / avancé
        "double sens à démêler",                                  # adulte / avancé
        "métaphore à interpréter puis résoudre",                  # adulte / avancé
    ],
}


def pick_variety_seed(challenge_type: str) -> VarietySeed:
    """Tire un seed aléatoire pour le type donné.

    Retourne un seed entièrement vide si le type n'a pas de mécanismes définis —
    build_challenge_user_prompt() n'injectera alors aucun bloc ORIENTATION.
    """
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

- [ ] **Step 2 : Vérifier l'import et le fallback**

```bash
python -c "
from app.services.challenges.challenge_variety_seeds import pick_variety_seed, VarietySeed
s = pick_variety_seed('coding')
assert s.narrative_context, 'narrative_context vide pour coding'
assert s.resolution_mechanism, 'resolution_mechanism vide pour coding'
empty = pick_variety_seed('type_inconnu')
assert empty.narrative_context == '' and empty.resolution_mechanism == ''
print('OK — coding seed:', s.resolution_mechanism[:40])
print('OK — fallback vide:', empty)
"
```

Expected :
```
OK — coding seed: <mécanisme coding quelconque>
OK — fallback vide: VarietySeed(narrative_context='', resolution_mechanism='', ...)
```

- [ ] **Step 3 : Commit**

```bash
git add app/services/challenges/challenge_variety_seeds.py
git commit -m "feat(quality): add challenge variety seeds library (VarietySeed + pick_variety_seed)"
```

---

## Task 3 — Ajouter 4 sections qualité dans `challenge_prompt_sections.py`

**Files:**
- Modify: `app/services/challenges/challenge_prompt_sections.py`

Ajouter les 4 nouvelles constantes après `TEXT_MATHLOG_CONTEXT` (ligne ~24).
`TEXT_MATHLOG_CONTEXT` est conservé (il est importé dans d'autres contextes potentiels)
mais ne sera plus référencé dans `build_challenge_system_prompt()` après Task 4.

- [ ] **Step 1 : Ajouter les 4 constantes à la fin du bloc "Toujours inclus"**

Insérer immédiatement après `TEXT_MATHLOG_CONTEXT` (après la ligne fermante `"""`
de ce bloc, vers la ligne 24 du fichier) :

```python
TEXT_STORYTELLING_PRINCIPLES = """STORYTELLING PÉDAGOGIQUE :
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
Si le contexte peut être supprimé sans changer le problème, il ne sert à rien."""

TEXT_ENGAGEMENT_PRINCIPLES = """ENGAGEMENT :
Le titre doit donner envie d'ouvrir le défi : question, mission, anomalie, paradoxe.
  \u2705 BON  : "Qui a volé le code ?" / "Le pont le plus court" / "Trois couleurs suffisent ?"
  \u274c MAUVAIS : "Problème de probabilité" / "Suite logique 3" / "Défi de déduction"

La description pose la situation en 1-2 phrases : micro-contexte \u2192 données utiles \u2192 question.
Ne pas poser la question principale avant d'avoir donné les données nécessaires.
Elle doit rendre la question inévitable — l'apprenant doit vouloir résoudre.

La solution_explanation répond à "pourquoi ça marche", pas seulement "comment on calcule".
L'apprenant doit comprendre quelque chose de nouveau après l'avoir lue — même avec la bonne réponse."""

TEXT_ACCESSIBILITY_COGNITIVE = """ACCESSIBILITÉ COGNITIVE :
- 6-8 ans  : phrases \u2264 12 mots, 1 seule consigne, objets concrets uniquement
- 9-11 ans : phrases \u2264 20 mots, vocabulaire du quotidien, pas de termes techniques
- 12+ ans  : vocabulaire précis acceptable, mais une phrase par idée

Ordre recommandé : micro-contexte \u2192 données utiles \u2192 question.
Exceptions valides : une anomalie ou un paradoxe peut ouvrir le défi si ça renforce
l'engagement sans créer d'ambiguïté. La règle absolue : ne jamais poser la question
principale avant d'avoir fourni les données nécessaires pour y répondre.

Test d'ambiguïté : si la question peut être lue de deux façons, réécrire
jusqu'à ce qu'il n'y ait qu'une seule interprétation possible."""

TEXT_DISTRACTOR_COGNITIVE = """QUALITÉ DES DISTRACTEURS :
Chaque distracteur cible une erreur de raisonnement réelle — pas une valeur arbitraire.
Les distracteurs doivent provenir d'erreurs différentes, pas de variantes du même mauvais calcul.

Erreurs types à modéliser :
- Erreur d'opération : bon contexte, mauvaise opération (addition au lieu de \u00d7)
- Erreur de lecture : données mal interprétées (total au lieu de favorable)
- Erreur d'étape : raisonnement correct mais incomplet (étape oubliée)
- Erreur d'intuition : réponse "qui semble juste" mais fausse (piège heuristique)

Contraintes de forme :
- Longueurs et formats identiques entre toutes les options
- Aucun distracteur éliminable par évidence de format ou syntaxe"""
```

- [ ] **Step 2 : Vérifier que les 4 constantes sont accessibles**

```bash
python -c "
from app.services.challenges.challenge_prompt_sections import (
    TEXT_STORYTELLING_PRINCIPLES,
    TEXT_ENGAGEMENT_PRINCIPLES,
    TEXT_ACCESSIBILITY_COGNITIVE,
    TEXT_DISTRACTOR_COGNITIVE,
)
for name, val in [
    ('STORYTELLING', TEXT_STORYTELLING_PRINCIPLES),
    ('ENGAGEMENT', TEXT_ENGAGEMENT_PRINCIPLES),
    ('ACCESSIBILITY', TEXT_ACCESSIBILITY_COGNITIVE),
    ('DISTRACTOR', TEXT_DISTRACTOR_COGNITIVE),
]:
    assert len(val) > 50, f'{name} trop court'
    print(f'OK {name}: {len(val)} chars')
"
```

Expected : 4 lignes `OK <NOM>: <N> chars`, toutes > 50.

- [ ] **Step 3 : Commit**

```bash
git add app/services/challenges/challenge_prompt_sections.py
git commit -m "feat(quality): add 4 pedagogical quality sections to challenge prompt"
```

---

## Task 4 — Mettre à jour `challenge_prompt_composition.py`

**Files:**
- Modify: `app/services/challenges/challenge_prompt_composition.py`

Deux sous-tâches : (A) remplacer `TEXT_MATHLOG_CONTEXT` par les 4 nouvelles sections dans
`build_challenge_system_prompt()`, (B) ajouter le paramètre `variety_seed` et le bloc
d'injection dans `build_challenge_user_prompt()`.

- [ ] **Step 1 : Mettre à jour les imports (lignes 14–30)**

Remplacer le bloc d'import depuis `challenge_prompt_sections` :

```python
from app.services.challenges.challenge_prompt_sections import (
    TEXT_ACCESSIBILITY_COGNITIVE,
    TEXT_DIFFICULTY_RULES,
    TEXT_DISTRACTOR_COGNITIVE,
    TEXT_ENGAGEMENT_PRINCIPLES,
    TEXT_HINTS_RULES,
    TEXT_JSON_CONTRACT_TEMPLATE,
    TEXT_LATEX_RULES,
    TEXT_PATTERN_EXAMPLES,
    TEXT_ROLE_HEADER,
    TEXT_STORYTELLING_PRINCIPLES,
    TEXT_TYPE_LOCK_TEMPLATE,
    TEXT_TYPES_COMPACT,
    TEXT_VAL_FINAL,
    TEXT_VAL_INTRO,
    TEXT_VISUAL_ADULT_RULE,
    TEXT_VISUAL_DATA_FALLBACK,
    VALIDATION_SECTION_BY_TYPE,
    VISUAL_DATA_SECTION_BY_TYPE,
)
```

*(Supprime `TEXT_MATHLOG_CONTEXT` de l'import — il n'est plus utilisé dans ce module.)*

- [ ] **Step 2 : Remplacer le bloc `parts` dans `build_challenge_system_prompt()` (lignes 112–120)**

```python
    parts: List[str] = [
        TEXT_ROLE_HEADER,
        TEXT_TYPE_LOCK_TEMPLATE.format(challenge_type=challenge_type),
        _age_group_block(params),
        TEXT_TYPES_COMPACT,
        TEXT_STORYTELLING_PRINCIPLES,    # remplace TEXT_MATHLOG_CONTEXT
        TEXT_ENGAGEMENT_PRINCIPLES,
        TEXT_ACCESSIBILITY_COGNITIVE,
        TEXT_HINTS_RULES,
        TEXT_DISTRACTOR_COGNITIVE,
        VISUAL_DATA_SECTION_BY_TYPE.get(ct, TEXT_VISUAL_DATA_FALLBACK),
    ]
```

- [ ] **Step 3 : Ajouter `variety_seed` à `build_challenge_user_prompt()`**

Remplacer la signature (ligne ~152) :

```python
def build_challenge_user_prompt(
    challenge_type: str, age_group: str, prompt: str, locale: str = "fr",
    variety_seed: "VarietySeed | None" = None,
) -> str:
```

Ajouter l'import en tête de fichier (après les imports existants) :

```python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.services.challenges.challenge_variety_seeds import VarietySeed
```

*(Le `TYPE_CHECKING` guard évite une dépendance circulaire potentielle et garde le type
disponible pour les annotations sans import runtime.)*

- [ ] **Step 4 : Injecter le bloc ORIENTATION après la langue, avant la demande personnalisée**

Dans `build_challenge_user_prompt()`, après le bloc `LANGUE DE SORTIE` et avant le bloc
`if prompt:`, ajouter :

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
            "\n  - la demande personnalisée utilisateur est prioritaire sur cette orientation ;"
            "\n  - cette orientation est une suggestion, jamais une obligation."
            f"\nIMPORTANT : le contrat visual_data du type {challenge_type} et le schéma JSON"
            " restent inchangés. Le seed oriente le contexte narratif et le raisonnement,"
            " pas la structure des données."
            "\nNote : le mécanisme peut être avancé — adapter la formulation,"
            " le vocabulaire et la complexité au groupe d'âge cible."
        )
```

- [ ] **Step 5 : Vérifier l'import du module et le prompt généré**

```bash
python -c "
from app.services.challenges.challenge_prompt_composition import (
    build_challenge_system_prompt,
    build_challenge_user_prompt,
    challenge_system_prompt_stats,
)
from app.services.challenges.challenge_variety_seeds import pick_variety_seed

# Vérifier que build_challenge_system_prompt fonctionne
p = build_challenge_system_prompt('coding', '9-11')
assert 'STORYTELLING' in p, 'TEXT_STORYTELLING_PRINCIPLES absent'
assert 'ENGAGEMENT' in p, 'TEXT_ENGAGEMENT_PRINCIPLES absent'
assert 'ACCESSIBILITÉ' in p, 'TEXT_ACCESSIBILITY_COGNITIVE absent'
assert 'DISTRACTEURS' in p, 'TEXT_DISTRACTOR_COGNITIVE absent'
assert 'MATHÉLOGIQUE' not in p, 'TEXT_MATHLOG_CONTEXT encore présent'
print('OK build_challenge_system_prompt:', len(p), 'chars')

# Vérifier l'injection seed
seed = pick_variety_seed('probability')
u = build_challenge_user_prompt('probability', '9-11', '', variety_seed=seed)
assert 'ORIENTATION DE VARIÉTÉ' in u, 'Bloc seed absent du prompt utilisateur'
print('OK build_challenge_user_prompt avec seed:', seed.resolution_mechanism[:40])

# Vérifier le fallback (seed vide = pas d'injection)
from app.services.challenges.challenge_variety_seeds import VarietySeed
empty_seed = VarietySeed(narrative_context='', resolution_mechanism='')
u2 = build_challenge_user_prompt('coding', '9-11', '', variety_seed=empty_seed)
assert 'ORIENTATION' not in u2, 'Seed vide ne doit pas injecter de bloc'
print('OK seed vide: pas de bloc ORIENTATION')
"
```

Expected : 3 lignes `OK ...`.

- [ ] **Step 6 : Lancer le guard test de taille**

```bash
python -m pytest tests/unit/test_challenge_prompt_size_budget.py -v
```

Expected : **50 PASSED**. Si un type échoue (> 11 000 chars), identifier le type concerné
et consolider `TEXT_ACCESSIBILITY_COGNITIVE` + `TEXT_ENGAGEMENT_PRINCIPLES` en une section.

- [ ] **Step 7 : Commit**

```bash
git add app/services/challenges/challenge_prompt_composition.py
git commit -m "feat(quality): update system prompt order + inject VarietySeed in user prompt"
```

---

## Task 5 — Intégrer dans `challenge_ai_service.py`

**Files:**
- Modify: `app/services/challenges/challenge_ai_service.py`

Deux lignes d'import + 3 lignes d'appel. La logique métier reste dans le module seeds.

- [ ] **Step 1 : Ajouter l'import de `pick_variety_seed` dans le bloc imports existant (lignes 38–42)**

Ajouter dans le bloc import qui importe déjà `build_challenge_user_prompt` :

```python
from app.services.challenges.challenge_prompt_composition import (
    AGE_GROUP_PARAMS,
    build_challenge_system_prompt,
    build_challenge_user_prompt,
)
from app.services.challenges.challenge_variety_seeds import pick_variety_seed
```

*(Ligne séparée hors du bloc existant pour ne pas perturber l'isort order.)*

- [ ] **Step 2 : Remplacer l'appel `build_challenge_user_prompt` (lignes 507–512)**

Avant l'appel existant, ajouter le tirage et le log. Remplacer :

```python
        user_prompt = build_challenge_user_prompt(
            challenge_type,
            age_group,
            prompt,
            locale=locale,
        )
```

Par :

```python
        _variety_seed = pick_variety_seed(challenge_type)
        logger.debug(
            "Challenge variety seed — type={} context={} mechanism={}",
            challenge_type,
            _variety_seed.narrative_context,
            _variety_seed.resolution_mechanism,
        )
        user_prompt = build_challenge_user_prompt(
            challenge_type,
            age_group,
            prompt,
            locale=locale,
            variety_seed=_variety_seed,
        )
```

- [ ] **Step 3 : Vérifier que le module s'importe sans erreur**

```bash
python -c "
from app.services.challenges.challenge_ai_service import generate_challenge_stream
print('OK — import challenge_ai_service sans erreur')
"
```

Expected : `OK — import challenge_ai_service sans erreur`

- [ ] **Step 4 : Lancer le guard test une dernière fois**

```bash
python -m pytest tests/unit/test_challenge_prompt_size_budget.py -v --tb=short
```

Expected : **50 PASSED**.

- [ ] **Step 5 : Commit**

```bash
git add app/services/challenges/challenge_ai_service.py
git commit -m "feat(quality): integrate pick_variety_seed into generate_challenge_stream"
```

---

## Vérification finale

- [ ] **Import complet — tous les modules chargent sans erreur**

```bash
python -c "
from app.services.challenges.challenge_prompt_sections import (
    TEXT_STORYTELLING_PRINCIPLES, TEXT_ENGAGEMENT_PRINCIPLES,
    TEXT_ACCESSIBILITY_COGNITIVE, TEXT_DISTRACTOR_COGNITIVE,
)
from app.services.challenges.challenge_variety_seeds import pick_variety_seed
from app.services.challenges.challenge_prompt_composition import (
    build_challenge_system_prompt, build_challenge_user_prompt,
)
from app.services.challenges.challenge_ai_service import generate_challenge_stream
print('OK — tous les imports résolus')
"
```

- [ ] **Guard test 50/50**

```bash
python -m pytest tests/unit/test_challenge_prompt_size_budget.py -v
```

Expected : 50 PASSED, 0 failed.

- [ ] **Présence des nouvelles sections dans le prompt système**

```bash
python -c "
from app.services.challenges.challenge_prompt_composition import build_challenge_system_prompt
p = build_challenge_system_prompt('sequence', '9-11')
for kw in ['STORYTELLING', 'ENGAGEMENT', 'ACCESSIBILITÉ', 'DISTRACTEURS']:
    assert kw in p, f'{kw} manquant'
    print(f'OK {kw} présent')
print('Total chars:', len(p))
"
```

- [ ] **Seed injecté et fallback correct**

```bash
python -c "
from app.services.challenges.challenge_prompt_composition import build_challenge_user_prompt
from app.services.challenges.challenge_variety_seeds import pick_variety_seed, VarietySeed
# Seed actif
s = pick_variety_seed('deduction')
u = build_challenge_user_prompt('deduction', '12-14', '', variety_seed=s)
assert 'ORIENTATION DE VARIÉTÉ' in u
print('OK seed actif injecté')
# Seed vide -> pas d'injection
e = VarietySeed(narrative_context='', resolution_mechanism='')
u2 = build_challenge_user_prompt('deduction', '12-14', '', variety_seed=e)
assert 'ORIENTATION' not in u2
print('OK seed vide: pas de bloc injecté')
# Demande personnalisée toujours en dernier
s2 = pick_variety_seed('coding')
u3 = build_challenge_user_prompt('coding', '9-11', 'défi sur le chiffre binaire', variety_seed=s2)
idx_seed = u3.find('ORIENTATION')
idx_custom = u3.find('DEMANDE PERSONNALISÉE')
assert idx_seed < idx_custom, 'Seed doit apparaître AVANT la demande personnalisée'
print('OK demande personnalisée après le seed (priorité correcte)')
"
```

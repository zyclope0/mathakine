# GAP-generation — Audit policy modèle IA par (type, difficulty)

> **Mise à jour 2026-04-28 :** Recommandations appliquées — défaut exercices et défis migré vers `o4-mini`. VarietySeed (injection variété défis) livré le 2026-04-28 (commits `74ffb14`→`33bb325`). Le contenu ci-dessous décrit l'état terrain au 2026-04-19 — les gaps identifiés ont été traités.

> Lot G — **Phase 1, read-only**. Date : 2026-04-19.
> Sources : `app/core/ai_generation_policy.py`, `app/core/ai_config.py`,
> `app/core/app_model_policy.py`, `app/services/challenges/challenge_ai_model_policy.py`,
> `app/services/exercises/exercise_ai_service.py` (`resolve_exercise_ai_model`).

## 1. Ce que fait aujourd'hui la résolution de modèle pour les exercices IA

`resolve_exercise_ai_model()` (`ai_generation_policy.py` l. 203-220) ignore **totalement**
`exercise_type` et `derived_difficulty`. Hiérarchie :

1. `OPENAI_MODEL_EXERCISES_OVERRIDE` (ops)
2. `OPENAI_MODEL_EXERCISES` (legacy)
3. Défaut applicatif : `DEFAULT_EXERCISES_AI_MODEL = "o3"`

Le point d'extension `resolve_exercise_ai_model_for_user(user_id, exercise_type)` ignore lui aussi ces deux paramètres et délègue à `resolve_exercise_ai_model()`.

**Conséquence** : les 45 cellules `(type × difficulty)` partagent **le même modèle**.

Paramètres dérivés côté runtime qui **dépendent du type** (mais pas de la difficulté) :

- `REASONING_EFFORT_BY_EXERCISE_TYPE` : `low` / `medium` / `high`
- `MAX_COMPLETION_TOKENS_BY_EXERCISE_TYPE` : 2800..5000
- `_EXERCISE_IA_GPT5_VERBOSITY` : `low` (fixe, toutes familles GPT-5)

## 2. Matrice effective par cellule

Modèle effectif : **`o3` (défaut) ou override env, identique partout**.
Cellules invalides selon Lot F (clamp) marquées `—` (hors plage `_TYPE_DIFFICULTY_BOUNDS`).

| Type \ Difficulté | INITIE | PADAWAN | CHEVALIER | MAITRE | GRAND_MAITRE | reasoning_effort | max_completion_tokens |
|---|---|---|---|---|---|---|---|
| addition        | o3 | o3 | o3 | — | — | **low**    | 2800 |
| soustraction    | o3 | o3 | o3 | — | — | **low**    | 2800 |
| multiplication  | — | o3 | o3 | o3 | — | **low**    | 2800 |
| division        | — | o3 | o3 | o3 | — | **low**    | 2800 |
| fractions       | — | o3 | o3 | o3 | o3 | medium     | 4500 |
| geometrie       | — | o3 | o3 | o3 | o3 | **low**    | 3200 |
| texte           | o3 | o3 | o3 | o3 | o3 | medium     | 4500 |
| mixte           | — | — | o3 | o3 | o3 | high       | 5000 |
| divers          | — | o3 | o3 | o3 | o3 | medium     | 4500 |

## 3. Combinaisons à risque (après clamp Lot F)

Le risque pertinent n'est pas le modèle lui-même (o3 est un bon modèle de raisonnement)
mais le **reasoning_effort trop bas** sur une difficulté haute :

- **`geometrie × {CHEVALIER, MAITRE, GRAND_MAITRE}`** — `reasoning_effort=low` alors que
  le type va jusqu'à GRAND_MAITRE (plafond Lot F). Risque principal : géométrie 3D /
  volumes / raisonnements multi-étapes produits en mode « rapide » par o3.
- **`addition × CHEVALIER`, `soustraction × CHEVALIER`** — `low` effort alors que la
  directive non-trivialité Lot C exige ≥ 2 étapes. La combinaison reste **rare après
  clamp** (plafond CHEVALIER) mais la qualité pédagogique peut être faible.
- **`multiplication × {CHEVALIER, MAITRE}`, `division × {CHEVALIER, MAITRE}`** —
  même logique, `low` effort pour des niveaux qui exigent un vrai raisonnement multi-étapes.

Les cellules à **risque faible ou nul** après clamp :
- mixte (`high` effort partout), fractions / texte / divers (`medium`).

## 4. Recommandation

**Patch léger ciblé, pas de refonte**. Deux options non exclusives :

### Option A — minimal (recommandée)
Passer `geometrie` de `low` à `medium` dans `REASONING_EFFORT_BY_EXERCISE_TYPE`.
Motif : unique cellule-type qui combine plafond `GRAND_MAITRE` autorisé et effort `low`.
Coût tokens modéré (geometrie a `max_completion_tokens=3200`). Pas de changement de modèle.

### Option B — plus ambitieuse (optionnelle)
Introduire une carte `REASONING_EFFORT_BY_TYPE_AND_DIFFICULTY` permettant
`(type, difficulty) → effort` : passer à `medium` pour `addition/soustraction × CHEVALIER`
et `multiplication/division × {CHEVALIER, MAITRE}`. Plus granulaire mais ajoute une
dimension à la policy ; pertinente seulement si la qualité observée sur ces cellules
après Lots C/E/F reste insuffisante.

### Hors scope audit
- Routage par modèle `(type × difficulty) → model` : **non justifié** aujourd'hui.
  `o3` est adapté aux 5 niveaux ; la variable d'ajustement naturelle reste le
  `reasoning_effort`, pas le choix de famille.
- Promotion vers `gpt-5.*` : documentée comme hors scope sans preuve harness
  (`app_model_policy.py` : « toute promotion vers GPT-5 hors preuve harness reste hors scope »).

## 5. Verdict

- **État actuel** : policy **saine** sur le choix du modèle, **granularité insuffisante**
  sur le `reasoning_effort` pour une seule cellule-type (`geometrie`).
- **Action** : **Phase 2 ciblée recommandée** — diff minimal sur
  `REASONING_EFFORT_BY_EXERCISE_TYPE` (`geometrie: low → medium`) + 2 tests unitaires
  dédiés. À n'exécuter qu'après accord explicite.
- **Pas de refonte** nécessaire.

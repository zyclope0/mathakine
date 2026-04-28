# Contrat défis IA9 — modalité de réponse et `choices`

> Lot IA9 — alignement prompt / validation / persistance / frontend.

## `response_mode` (GET `/api/challenges/{id}`)

Valeurs stables :

| Valeur | Usage UI |
|--------|-----------|
| `open_text` | Saisie libre (éventuellement avec visualisation informative). |
| `single_choice` | QCM : `choices` non vide **et** autorisé par la politique. |
| `interactive_visual` | Défis VISUAL (symétrie, formes) : interaction dédiée, pas de QCM implicite. |
| `interactive_order` | PUZZLE : ordre des pièces. |
| `interactive_grid` | PATTERN, SEQUENCE (séquence visuelle), DEDUCTION (logic_grid). |

Priorité backend : `generation_parameters.response_mode` si valide ; sinon recalcul (même logique que `compute_response_mode`).

## Politique `choices`

- **Interdit** : `DEDUCTION`, `CHESS`.
- **Facile uniquement** (`difficulty_rating` &lt; 2.0) : `VISUAL`, `PUZZLE`.
- **Optionnel** (QCM défendable) : `SEQUENCE`, `PATTERN`, `GRAPH`, `RIDDLE`, `PROBABILITY`, `CODING`.

Les `choices` sont filtrés côté API détail si la politique interdit le QCM (évite un QCM fantôme).

### IA9b — QCM legacy / exposition API

- ``sanitize_choices_for_delivery`` : policy type/difficulté **+** ``validate_challenge_choices`` (doublons, bonne réponse absente, etc.).
- Sur GET détail : seules les options **valides** sont exposées ; sinon liste vide.
- ``response_mode = single_choice`` n’est honoré depuis ``generation_parameters`` que si les choix sanitisés sont non vides (sinon recalcul, pas de QCM fantôme).

## VISUAL / symétrie (canonique)

```json
{
  "type": "symmetry",
  "symmetry_line": "vertical",
  "layout": [
    { "side": "left", "shape": "cercle", "color": "rouge", "question": false },
    { "side": "right", "shape": "?", "question": true }
  ]
}
```

`side` : `left` | `right` (minuscules après normalisation IA).

**Rendu (IA9b)** : grille verticale dynamique ``n_gauche + axe + n_droite`` ; ``symmetry_line: horizontal`` → bande haut (`left`) / axe / bas (`right`).

## Modèle IA

- Modèle actif : `o4-mini` (uniform, 10 types) — fallback `gpt-4o-mini`
- Format de réponse : encore `json_object` (migration `json_schema` / structured outputs **non démarrée** au 2026-04-28)
- Reasoning effort : `medium` max (jamais `high`)

## VarietySeed — orientation de variété (depuis commit `9b27a36`)

À chaque génération, un `VarietySeed` est injecté dans le prompt utilisateur pour diversifier les défis :

```python
@dataclass(frozen=True)
class VarietySeed:
    narrative_context: str   # ex. "histoire de cuisine"
    resolution_mechanism: str  # ex. "classification par catégories"
```

**Injection** : le bloc `ORIENTATION DE VARIÉTÉ` est ajouté en fin de prompt utilisateur si `narrative_context` ou `resolution_mechanism` est non vide.

**Suggestion forte** : le LLM PEUT ignorer ce bloc si le contexte pédagogique l'exige.

**Types ignorant le narrative context** : `chess`, `visual`, `pattern` (types visuels — `_TYPES_IGNORE_NARRATIVE`).

**Filtres âge** : groupes `6-8` et `9-11` ne reçoivent que les mécanismes de résolution adaptés (riddle : all-ages uniquement).

## Sections qualité du prompt système (depuis commit `74ffb14`)

Le prompt système inclut 4 sections pédagogiques additionnelles :

1. **STORYTELLING ET MISE EN SCÈNE** — ancrage narratif cohérent avec le niveau
2. **ENGAGEMENT ET ACCESSIBILITÉ** — adaptation cognitive au groupe d'âge
3. **INDICES PROGRESSIFS ET RÉTROACTION PÉDAGOGIQUE** — 3 niveaux d'indices
4. **ERREURS FRÉQUENTES ET DISTRACTEURS COGNITIFS** — distracteurs plausibles pour QCM

## Références code

- `app/services/challenges/challenge_contract_policy.py`
- `app/services/challenges/challenge_api_mapper.py` (`resolve_challenge_response_mode`)
- `app/services/challenges/challenge_variety_seeds.py` (VarietySeed, pick_variety_seed)
- `app/services/challenges/challenge_prompt_sections.py` (sections qualité)
- `frontend/lib/challenges/resolveChallengeResponseMode.ts`

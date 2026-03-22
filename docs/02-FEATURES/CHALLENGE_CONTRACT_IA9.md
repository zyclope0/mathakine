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

## Références code

- `app/services/challenges/challenge_contract_policy.py`
- `app/services/challenges/challenge_api_mapper.py` (`resolve_challenge_response_mode`)
- `frontend/lib/challenges/resolveChallengeResponseMode.ts`

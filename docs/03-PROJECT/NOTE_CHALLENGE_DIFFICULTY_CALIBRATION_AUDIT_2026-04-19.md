# Note audit — calibration descendante des défis

> Lot H — **read-only**. Date : 2026-04-19.
> Sources : `app/services/challenges/challenge_difficulty_policy.py`,
> `app/services/challenges/challenge_ai_service.py`,
> `app/services/challenges/challenge_validator.py`, commits `6a4c459`, `c55b967`.

## Question

`calibrate_challenge_difficulty` peut-il **baisser** un `difficulty_rating` LLM trop élevé,
ou est-il décoratif ?

**Réponse** : il peut **réellement baisser**. Le rating final traverse (1) un *snap à la
baseline âge* si l'écart dépasse ±1.5, puis (2) plusieurs **plafonds structurels**
appliqués après coup (variable `caps_applied`). Le plancher adulte (4.0) ne va, lui, que
vers le haut. Les commits `c55b967` (CODING) et `6a4c459` (SEQUENCE + rendu) ont ajouté
des caps et des validations structurelles depuis fin 2026-03.

## Règles descendantes par `challenge_type` (après Lots récents)

| Type | Règles descendantes en place | Règles manquantes |
|---|---|---|
| **SEQUENCE**    | `title_rule_leak_cap_3_0` (cap 3.0 si titre révèle la règle) ; **validations bloquantes** : `visual_data.pattern` exposé + rating ≥ 4.0, suite ≤ 6 éléments avec une seule inconnue + rating ≥ 4.0, progression arithmétique/géométrique simple + rating ≥ 4.0. | Pas de cap « calibrate-level » ciblé SEQUENCE (les invariants passent par le validator → rejet LLM / retry, non par un cap silencieux). Acceptable si le retry converge. |
| **PATTERN**     | `pattern_single_cell_cap` (cap 3.0 si ≤ 1 case `?`) ; validation bloquante correspondante. | — |
| **PUZZLE**      | `puzzle_small_piece_count_cap_3_0` (≤ 4 pièces + rating > 3.0) ; validation bloquante. | — |
| **DEDUCTION**   | `deduction_insufficient_clues_cap_2_5` (≥ 2 catégories + < 2 indices + rating > 2.5) ; validation bloquante. | — |
| **CODING**      | Trois caps explicites : `coding_binary_short_payload_cap_3_2`, `coding_caesar_explicit_shift_cap_3_0`, `coding_substitution_full_key_cap_3_2` ; validations bloquantes correspondantes ; `sanitize_leaky_title` sur titres trop explicites (`c55b967`). | — |
| **PROBABILITY** | Aucun cap. `validate_probability_challenge` vérifie la présence de quantités numériques mais **ne contrôle pas la cohérence rating ↔ structure** (ex. tirage trivial annoncé 4.5). | Cap « quantité de branches / complexité dénombrement » vs rating ≥ 4.0 absent. Petit gap, sans précédent opérationnel connu. |

Transverses (tous types) : `title_rule_leak_cap_3_0` + `age_baseline_snap` (si écart > 1.5)
+ `sanitize_leaky_title` (titre neutralisé si rating ≥ 4.0 et fuite de règle).

## Verdict

- **Non décoratif** : plusieurs chemins descendants réels, à la fois dans `calibrate`
  (caps silencieux) et dans `validate_*` (rejet + retry LLM).
- **Couverture suffisante en pré-invitation** sur SEQUENCE / PATTERN / PUZZLE /
  DEDUCTION / CODING après `6a4c459` et `c55b967`.
- **Unique gap identifié** : PROBABILITY n'a **aucun** garde-fou descendant de
  cohérence rating ↔ structure. Priorité **basse** tant qu'on n'observe pas de cas
  produit où un tirage simple est persisté ≥ 4.0 ; à réévaluer si la télémétrie
  `difficulty_calibration` en harness ou runtime révèle des outliers PROBABILITY.
- **Pas de durcissement nécessaire pour les 5 autres types listés** ; `calibrate`
  n'est pas un décor et le validator bloque ce qui doit l'être.

# R6 — Exercice : discovery alignée R3 + reasons structurées (2026-03-21)

## Objectif

- Intégrer la branche **discovery** au **même pipeline de classement** que les autres branches exercice (`select_top_ranked_exercises`, anti-répétition, tie-break stable).
- Remplacer les **textes FR** des raisons exercice par un **contrat** `reason_code` / `reason_params` + fallback `reason` (EN court), comme les défis en R5.
- **Pas de migration** : réutilisation des colonnes R5 existantes.

## Stratégie discovery (R6)

- Types « nouveaux » : `all_types` (distinct DB) − `practised_types` (Progress, clés canoniques R1).
- Pour chaque `nt` dans **`sorted(new_types)`** : pool borné `ORDER BY id DESC LIMIT MAX_CANDIDATES_TO_RANK`, puis `select_top_ranked_exercises(..., discovery_penalized, 1)` ; pénalités étendues après chaque choix.

## Reasons exercice

| `reason_code` | Usage |
|---------------|--------|
| `reco.exercise.improvement` | Stats récentes faibles |
| `reco.exercise.progression` | Niveau supérieur |
| `reco.exercise.maintenance` | Réactivation |
| `reco.exercise.discovery` | Nouveau type |
| `reco.exercise.fallback` | Liste vide → picks classés |

## Hors scope

- `practice_rhythm`, refonte UI, feedback au-delà de R4, refonte scoring défis.

## Clôture itération `R`

Gouvernance et vérité consolidée (réserve, non-claims, baseline) : [RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md](./RECOMMENDATION_R7_CLOSURE_ITERATION_R_2026-03-21.md).

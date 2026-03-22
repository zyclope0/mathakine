# IA11b — Campagne comparative live bornée (hybride IA11a)

## Rôle

Prolonge **IA11a** sans nouveau protocole parallèle :

- les **segments offline** sont ceux de `ia11a_offline_default` (même matrice, même harness) ;
- les **exécutions live** sont listées explicitement dans `tests/fixtures/ai_eval/campaigns/ia11b_live_bounded.json` (un passage par ligne, pas d’élargissement opportuniste du corpus).

**Décision produit** : aucun changement des défauts runtime (`exercises_ai`, `challenges_ai`, `assistant_chat`). Le champ `eval_model` sur le cas d’évaluation **patch** uniquement la résolution de modèle **dans le harness** (`runners` + `dispatch_live`).

## Pourquoi rester borné

- **Coût / quota** : chaque variante live = appel(s) API réels.
- **Confiance statistique** : avec **n=1** par variante sur le corpus actuel, les conclusions restent **faibles** ; le rapport exige un niveau de confiance explicite, pas un verdict fort.
- **Pas de score opaque** : métriques par workload / variante (`success`, `structural_ok`, `business_ok`, latence, tokens si présents, agrégats `token_tracker` documentés comme non isolés par variante).

## Prérequis

- `OPENAI_API_KEY` utilisable par l’app.
- Opt-in explicite : **`--live`** **ou** `MATHAKINE_AI_EVAL_LIVE=1`.

## Lancement

Référence offline (IA11a) — sans réseau :

```bash
python -m app.evaluation.comparative_campaign --campaign ia11a_offline_default
```

Hybride IA11b (offline IA11a + live borné) :

```bash
python -m app.evaluation.comparative_campaign --ia11b-bounded-live --live --ia11b-campaign ia11b_live_bounded
```

Options utiles : `--corpus PATH`, `--output-dir reports/ai_eval/campaigns`, `--stdout-json`.

## Sorties

- **JSON** : `comparative_campaign_ia11b_live_bounded_<ts>.json`
  - `segments[].harness_report` : segment **offline** (comme IA11a).
  - `segments[].live_executed_variants[]` : une entrée par variante live (rapport harness `mode: live`, `cases_total` typiquement 1).
  - `token_tracker_snapshot_post_live` : snapshot **après** toutes les variantes (agrégat processus).
  - `ia11b_recommendation_markdown` : même texte que la section recommandation du Markdown.
- **Markdown** : tableau offline + tableau live + recommandation documentaire.

## Limites

- `token_tracker` ne permet pas une attribution propre coût/tokens **par variante** dans un même processus : lire les champs par cas quand ils existent, et le snapshot global avec prudence.
- `simple_generator` n’a pas de variante live dans la matrice IA11b (référence offline uniquement).
- Si l’environnement empêche le live (pas de clé, refus réseau), **ne pas inventer** de résultats : la commande échoue avec l’exception / code harness habituel.

## Voir aussi

- `IA11A_COMPARATIVE_CAMPAIGN_OFFLINE.md`
- `AI_GENERATION_HARNESS.md`
- `tests/unit/test_comparative_campaign_ia11b.py`

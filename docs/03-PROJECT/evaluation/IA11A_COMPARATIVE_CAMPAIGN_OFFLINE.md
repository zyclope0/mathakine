# IA11a — Campagne comparative offline (protocole)

## Méthodologie (obligatoire)

Un benchmark utile **sépare** :

| Axe | Sens |
|-----|------|
| **Succès technique** | Pas d’exception, pipeline exécuté jusqu’au bout |
| **Succès métier** | Validateurs métier (`business_ok`, erreurs listées) |
| **Conformité au scénario** | `success` vs `expected_success` du corpus (positif = validateurs OK ; négatif = rejet observé) |
| **Structure** | `structural_ok` (exercices ; défis fixture : structure implicite) |
| **Coût / latence** | Latence **mesurable offline** ; coût/tokens **non disponibles** sans live |

**Pourquoi IA11a reste offline** : verrouiller le **protocole**, la **matrice** et les **sorties** avant toute dépense API. Aucune activation implicite via variable d’environnement pour ce chemin.

**Pourquoi pas de classement définitif** : les workloads ne partagent pas le même sous-ensemble de cas ni le même type de pipeline (générateur local vs fixtures vs futur SSE). Les tableaux sont **honest comparison prep**, pas un championnat.

**Candidats live** : intégrés à la matrice comme variantes **`planned_not_executed`** ; exécution réservée à **IA11b** sous confirmation humaine + opt-in harness live.

---

## Matrice offline retenue (`ia11a_offline_default`)

Fichier : `tests/fixtures/ai_eval/campaigns/ia11a_offline_default.json`

| Workload (concept) | Cible harness (`--target`) | Contenu offline |
|--------------------|----------------------------|-----------------|
| `simple_generator` | `simple` | Cas `simple_generator` du corpus |
| `exercises_ai` | `exercises_ai` | `template_exercise_generator` + `fixture_exercise_openai_shape` (hors `openai_exercise_stream`) |
| `challenges_ai` | `challenges_ai` | `fixture_challenge` uniquement (hors `openai_challenge_stream`) |

Variantes live **non exécutées** (IA11b) : SSE exercices / défis baseline **o3** (indicatif), décrites dans le JSON.

---

Suite : **IA11b** (live borné, même base de segments offline) — `docs/03-PROJECT/evaluation/IA11B_BOUNDED_LIVE_CAMPAIGN.md`.

## Lancement (offline uniquement)

```bash
# Depuis la racine du dépôt
python -m app.evaluation.comparative_campaign --campaign ia11a_offline_default
```

Options :

- `--corpus PATH` — corpus JSON (défaut : même que le harness)
- `--output-dir reports/ai_eval/campaigns` — JSON + Markdown horodatés
- `--stdout-json` — dump du payload sur stdout

**Garanties nominales IA11a** :

- Aucun `dispatch_live` : le code appelle uniquement `run_offline_harness_report` → `dispatch_offline`.
- Si `MATHAKINE_AI_EVAL_LIVE=1` est défini dans l’environnement, il est **ignoré** pour cette commande (message sur stderr).

Le harness classique reste disponible :

```bash
python -m app.evaluation.ai_generation_harness --mode offline --target exercises_ai
```

---

## Lecture des résultats

1. **Markdown** (`reports/ai_eval/campaigns/comparative_campaign_*.md`) : tableau par workload, variantes planifiées, prérequis IA11b.
2. **JSON** (`comparative_campaign_*.json`) :
   - `segments[].decision_metrics` — taux explicites, **sans score global**
   - `segments[].harness_report` — rapport harness complet (réutilisable / audit)
   - `non_measurable_offline` — rappel coût/tokens live
   - `live_executed: false`

Code de sortie CLI : `0` si chaque cas de chaque segment respecte le scénario (comme le harness), `1` sinon.

---

## Ce que IA11a prouve

- Les **pipelines offline** comparés **sur leurs propres cas** (validateurs, scénario corpus).
- La **traçabilité** : même moteur que `app.evaluation.ai_generation_harness` (pas de script parallèle).
- La **lisibilité décisionnelle** pour préparer une campagne live **contrôlée**.

## Ce que IA11a ne prouve pas

- Qualité des sorties **OpenAI** (non appelées).
- Coût réel, tokens, ni parité stricte avec un modèle en production.
- Efficacité pédagogique en classe.

---

## Préparation IA11b (live, hors ce lot)

À exécuter **après** validation humaine du protocole :

1. Lancer le harness **`--mode live`** avec opt-in explicite (`MATHAKINE_AI_EVAL_LIVE=1` ou `--live`) sur les sous-ensembles nommés dans la matrice.
2. Répéter les **mêmes axes de rapport** (pas d’agrégat opaque unique).
3. Comparer live vs offline sur des **sous-ensembles explicitement nommés** (éviter le mélange implicite des corpus).

---

## Persistance DB

La campagne comparative **n’écrit pas** en base par défaut (fichiers sous `reports/ai_eval/campaigns/`). Pour historiser un run harness classique : `python -m app.evaluation.ai_generation_harness --persist` (IA8).

---

## Voir aussi

- `docs/03-PROJECT/evaluation/AI_GENERATION_HARNESS.md`
- `docs/03-PROJECT/PILOTAGE_IA_GENERATION_EXERCICES_DEFIS_2026-03-21.md`
- `app/evaluation/comparative_campaign.py`, `app/evaluation/campaign_matrix.py`

# Harness d’évaluation — génération IA (IA7)

> ⚠️ OBSOLÈTE comme source de vérité runtime — ce document décrit le harness d'évaluation, pas les défauts modèle ni la hiérarchie des overrides en production.
> Référence runtime actuelle : [../../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../../00-REFERENCE/AI_MODEL_GOVERNANCE.md).

## Pourquoi ce harness existe

- **Plausible ≠ pédagogiquement correct** : un JSON valide ou un QCM « cohérent » peut rester trop difficile, ambigu ou hors niveau. Le harness ne remplace pas une revue humaine ou des tests utilisateurs.
- **Mesure de l’adéquation type / difficulté** : on réutilise les validateurs et heuristiques **déjà codés** (`validate_exercise_ai_output`, `validate_challenge_logic`, politiques de difficulté défis). Ce sont des **garde-fous explicites**, pas une preuve de qualité globale.
- **Éviter une évaluation flatteuse** : le corpus inclut des cas **négatifs** (`expected_success: false`) pour vérifier que les rejets attendus se produisent. Sans cela, un pipeline pourrait « réussir » en acceptant du contenu médiocre.

## Emplacement

- Code : `app/evaluation/`
- Corpus versionné : `tests/fixtures/ai_eval/corpus.json` + JSON de fixtures
- Rapports générés : `reports/ai_eval/` (par défaut)

## Modes

### Offline (CI, sans réseau)

- Générateur simple local : `generate_simple_exercise` — **structure + vérité métier** via `check_local_exercise_business_truth` (mêmes règles que `validate_exercise_ai_output`, sauf **indice** : si la clé `hint` est absente du payload, la contrainte de longueur sur l’indice ne s’applique pas, car les générateurs locaux ne le renseignent en général pas). **En plus**, pour `addition` / `soustraction` / `multiplication` / `division`, si `num1` et `num2` sont présents ou si la question suit le motif « Calcule a op b » (sortie standard du générateur), la **bonne réponse numérique** est recalculée et comparée à `correct_answer` (ex. `2+2=999` échoue même si le QCM est « propre »).
- Générateur template (narratif local, sans OpenAI) : `generate_ai_exercise` — idem (souvent `num1`/`num2` présents pour les types numériques).
- Fixtures « forme OpenAI » + validateur métier exercices IA
- Fixtures défis + `validate_challenge_logic` + signaux difficulté + `validate_challenge_choices` si QCM ; **`expected_success: false`** : succès du cas = **rejet** observé (validateurs / QCM), comme pour les fixtures exercices.

```bash
python -m app.evaluation.ai_generation_harness --mode offline --target all
```

### Live (opt-in, appels modèles réels)

Conditions **explicites** (au moins une) :

- variable d’environnement `MATHAKINE_AI_EVAL_LIVE=1`, **ou**
- flag CLI `--live`

Sans cela, le mode `live` refuse de s’exécuter.

Prérequis : `OPENAI_API_KEY` configurée (ex. via `.env` chargé par l’app).

```bash
set MATHAKINE_AI_EVAL_LIVE=1
python -m app.evaluation.ai_generation_harness --mode live --target openai_exercises --live
```

Sous-ensembles utiles : `openai_exercises`, `openai_challenges`, `all` (hors cas `live_only` filtrés en offline).

**Sémantique `expected_success` (live)** : alignée sur les fixtures — cas positif = validateurs OK ; cas négatif = **rejet** attendu (exercice / défi invalide, erreurs QCM défis, ou événement SSE `error` sans payload valide). Les **exceptions** réseau / code restent des échecs du run (`success: false`) pour signaler un problème d’infra.

## Métriques / flags (rapport JSON)

| Champ | Sens |
|--------|------|
| `success` | Résultat **conforme à l’attente** du cas (`expected_success`) — voir ci-dessous |
| `structural_ok` / `structural_errors` | Présence des champs minimaux (exercices) |
| `business_ok` / `business_errors` | Validateurs métier existants |
| `difficulty_flags` | Messages des heuristiques titre/structure vs `difficulty_rating` (défis) |
| `choices_flags` | Détails QCM / distracteurs quand applicable |
| `latency_ms` | Temps d’exécution du cas |
| `token_tracker_snapshot` | (live) agrégat mémoire `token_tracker` — pas une facturation officielle |
| `expected_success` | Si `false`, un cas **négatif** : succès = rejet observé (exercices **et** défis fixture) |

## Code de sortie CLI

- `0` : pour **chaque** cas, `success` est vrai (scénario respecté : positif = validateurs OK ; négatif = rejet observé), **ou** le cas est `live_skipped` en offline (pipeline réservé au live).
- `1` : au moins un cas a `success: false` (échec réel du scénario, y compris si un cas négatif passe les validateurs à tort).
- `2` : mode `live` demandé sans opt-in (`MATHAKINE_AI_EVAL_LIVE=1` ou `--live`).

## Persistance durable des runs (IA8, opt-in)

**Pourquoi** : un historique structuré permet de suivre l’évolution **technique** (validateurs, structure JSON) et **métier** (heuristiques locales / défis) dans le temps, et de repérer des **régressions invisibles** si l’on ne comparait que des rapports fichiers épars. Ce n’est **pas** une mesure pédagogique complète : on distingue explicitement conformité au **scénario du corpus** (`success` vs `expected_success`), validation **structurelle**, validation **métier**, sans prétendre couvrir curriculum, biais ou efficacité en classe.

- **Par défaut** (CI, offline) : aucune écriture en base — seuls les fichiers sous `reports/ai_eval/` sont produits.
- **Opt-in** : flag CLI `--persist` après génération des JSON/MD. Les données sont issues du **`HarnessReport` en mémoire** (`to_dict()`), pas d’un reparse Markdown.
- **Schéma** : tables `ai_eval_harness_runs` et `ai_eval_harness_case_results` (migration Alembic `20260322_ai_eval_harness`). Champs structurés (compteurs, chemins d’artefacts, `git_revision`, version app, flags par cas, etc.) + **snapshot JSON** complet du rapport pour audit / reproductibilité.
- > ⚠️ OBSOLÈTE — la mention "sans API HTTP dans ce lot" était vraie pendant IA8 uniquement.
- **Lecture** (CLI + admin read-only) :
  - `python -m app.evaluation.ai_generation_harness --show-run <UUID>`
  - `python -m app.evaluation.ai_generation_harness --list-persisted [--list-limit N]`
  - `GET /api/admin/ai-eval-harness-runs?limit=N`
  - ou `AiEvalHarnessPersistenceService` / `AiEvalHarnessRepository` en code.

Exemple :

```bash
python -m app.evaluation.ai_generation_harness --mode offline --target simple --persist
python -m app.evaluation.ai_generation_harness --show-run <UUID affiché>
```

Pré-requis DB : migration appliquée (`alembic upgrade head`) et `DATABASE_URL` / `TEST_DATABASE_URL` valides pour l’environnement cible.

**Tests pytest** : la fixture session `setup_test_environment` crée idempotemment `ai_eval_harness_runs` / `ai_eval_harness_case_results` sur l’engine de test (même principe que `daily_challenges` / `point_events`), pour que les tests unitaires ne dépendent pas d’un `alembic upgrade` manuel sur la base de test.

Sous **Windows**, si la console n’est pas en UTF-8, la CLI tente `stdout.reconfigure(encoding="utf-8")` puis retombe sur un JSON `ensure_ascii` si nécessaire — en cas de doute, utiliser `PYTHONUTF8=1` ou rediriger la sortie vers un fichier.

## Limites assumées

- La persistance ne remplace pas l’analyse humaine ni les tests utilisateurs ; les tendances dans le temps restent **indicatives** (garde-fous code + corpus), pas une « mesure pédagogique totale ».
- Pas d’évaluation frontend ni du chat assistant dans ce harness.
- Les coûts/tokens en live dépendent des estimations / `token_tracker` ; calibrage prix à maintenir avec la grille OpenAI.

## Campagne comparative offline (IA11a)

Objectif : **protocole** et **sorties comparatives** (JSON + Markdown) sans appel live, en réutilisant ce harness.

```bash
python -m app.evaluation.comparative_campaign --campaign ia11a_offline_default
```

- Matrice versionnée : `tests/fixtures/ai_eval/campaigns/ia11a_offline_default.json`
- Moteur : `run_offline_harness_report()` → `dispatch_offline` uniquement
- Détails : `docs/03-PROJECT/evaluation/IA11A_COMPARATIVE_CAMPAIGN_OFFLINE.md`

## Campagne comparative live bornée (IA11b)

Réutilise la **même** base offline IA11a + exécutions live listées dans `ia11b_live_bounded.json`. Opt-in **`--live`** ou `MATHAKINE_AI_EVAL_LIVE=1`.

```bash
python -m app.evaluation.comparative_campaign --ia11b-bounded-live --live --ia11b-campaign ia11b_live_bounded
```

- Helper harness : `run_live_harness_for_explicit_cases()` (cas enrichis, ex. `eval_model`).
- Détails : `docs/03-PROJECT/evaluation/IA11B_BOUNDED_LIVE_CAMPAIGN.md`

## Voir aussi

- `docs/03-PROJECT/PILOTAGE_IA_GENERATION_EXERCICES_DEFIS_2026-03-21.md`
- `docs/03-PROJECT/evaluation/IA11A_COMPARATIVE_CAMPAIGN_OFFLINE.md`
- `docs/03-PROJECT/evaluation/IA11B_BOUNDED_LIVE_CAMPAIGN.md`
- Tests : `tests/unit/test_ai_generation_harness.py`, `tests/unit/test_comparative_campaign_ia11a.py`, `tests/unit/test_comparative_campaign_ia11b.py`

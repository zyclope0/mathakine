# Runbook — Harness d'évaluation IA (IA7 / IA8)

> Scope : `app/evaluation/`
> Updated : 2026-03-27

---

## Objectif

Le harness d'évaluation IA mesure la conformité des réponses générées (exercices et défis) aux validateurs structurels et heuristiques métier codés dans le backend. Il opère en deux modes : **offline** (corpus fixe, sans appel OpenAI) et **live** (appels réels OpenAI, opt-in explicite).

Il ne mesure **pas** la qualité pédagogique réelle, l'alignement curriculum ou l'absence de biais. Un score « OK » peut masquer un énoncé ambigu ou inadapté à l'âge — limitation documentée dans le module.

---

## Architecture

```
app/evaluation/
├── __main__.py            Point d'entrée CLI (python -m app.evaluation)
├── ai_generation_harness.py  Orchestrateur principal (IA7)
├── schemas.py             Dataclasses CaseResult, HarnessReport
├── corpus_loader.py       Chargement du corpus JSON versionné
├── runners.py             Dispatch offline / live
├── checks.py              Validateurs structurels et heuristiques
├── reporting.py           Agrégats, résumé Markdown, write_report
├── campaign_matrix.py     Matrice de campagnes comparatives (IA11)
└── comparative_campaign.py  Campagnes comparatives multi-modèles
```

**Corpus** : `tests/fixtures/ai_eval/corpus.json`

**Persistance DB (IA8)** : `app/repositories/ai_eval_harness_repository.py` + table `ai_eval_harness_runs` (migration `20260322_ai_eval_harness_persistence.py`).

---

## Prérequis

| Condition | Vérification |
|-----------|-------------|
| Virtualenv activé | `which python` → `.venv/` |
| Base de données accessible | `DATABASE_URL` défini |
| Mode live uniquement : opt-in explicite | `MATHAKINE_AI_EVAL_LIVE=1` ou flag `--live` |
| Mode live uniquement : clé OpenAI | `OPENAI_API_KEY` défini |

---

## 1. Mode offline (par défaut)

Évalue le corpus contre les validateurs locaux sans appel OpenAI. Rapide, déterministe, utilisable en CI.

```bash
python -m app.evaluation.ai_generation_harness --mode offline
```

Avec cible spécifique :

```bash
python -m app.evaluation.ai_generation_harness --mode offline --target local_exercises
python -m app.evaluation.ai_generation_harness --mode offline --target local_challenges
```

Sortie attendue :

```
Running offline evaluation — corpus: tests/fixtures/ai_eval/corpus.json
Cases: 42 | Pipeline: local_exercises
[OK] case_001 structural=True business=True latency=12ms
[OK] case_002 structural=True business=True latency=8ms
[FAIL] case_015 structural=False business=None reason="missing field: choices"
...
Summary: 40/42 OK (95.2%) | 2 failed
Report written: reports/eval_offline_20260327_143012.md
```

---

## 2. Mode live (OpenAI réel)

Envoie les cas du corpus à OpenAI et mesure conformité + latence + coût estimé.

```bash
# Opt-in obligatoire via variable d'environnement
MATHAKINE_AI_EVAL_LIVE=1 python -m app.evaluation.ai_generation_harness --mode live --target openai_exercises

# Ou via flag
python -m app.evaluation.ai_generation_harness --mode live --live --target openai_exercises
```

> ⚠️ Chaque exécution en mode live génère des coûts OpenAI. Utiliser `--target` pour limiter le périmètre.

Sortie attendue :

```
Running live evaluation — target: openai_exercises
[LIVE] case_001 structural=True business=True latency=1842ms tokens=247 cost≈$0.0012
[LIVE] case_002 structural=True business=True latency=2103ms tokens=312 cost≈$0.0015
...
Summary: 38/40 OK (95.0%) | Total cost≈$0.048 | Avg latency=1950ms
```

---

## 3. Persistance DB (IA8)

Enregistre le rapport de run dans la table `ai_eval_harness_runs`.

```bash
# Ajouter --persist après une exécution offline ou live
python -m app.evaluation.ai_generation_harness --mode offline --persist
MATHAKINE_AI_EVAL_LIVE=1 python -m app.evaluation.ai_generation_harness --mode live --target openai_exercises --persist
```

Vérification en base :

```sql
SELECT id, pipeline, total_cases, ok_count, fail_count, created_at
FROM ai_eval_harness_runs
ORDER BY created_at DESC
LIMIT 5;
```

---

## 4. Campagnes comparatives (IA11)

Compare plusieurs modèles OpenAI sur le même corpus.

```bash
python -m app.evaluation.ai_generation_harness --mode comparative --campaign ia11a
python -m app.evaluation.ai_generation_harness --mode comparative --campaign ia11b
```

Les résultats sont agrégés dans `reports/comparative_*.md`.

---

## 5. Rapports générés

Les rapports sont écrits dans `reports/` (répertoire à la racine du dépôt).

| Fichier | Contenu |
|---------|---------|
| `eval_offline_YYYYMMDD_HHMMSS.md` | Résumé Markdown run offline |
| `eval_live_YYYYMMDD_HHMMSS.md` | Résumé Markdown run live |
| `comparative_*.md` | Comparatif multi-modèles |

---

## 6. Troubleshooting

### `FileNotFoundError: corpus.json`

Le corpus n'existe pas ou le chemin a changé.

```bash
ls tests/fixtures/ai_eval/
# Attendu : corpus.json (+ fixtures optionnelles)
```

Si absent, créer un corpus minimal :

```json
[
  {
    "case_id": "smoke_001",
    "pipeline": "local_exercises",
    "input": {"exercise_type": "addition", "difficulty_level": "INITIE"}
  }
]
```

### `MATHAKINE_AI_EVAL_LIVE not set`

Le mode live requiert un opt-in explicite. Ajouter `MATHAKINE_AI_EVAL_LIVE=1` en préfixe ou utiliser `--live`.

### `ExerciseAIModelNotAllowedError`

Le modèle spécifié dans `OPENAI_MODEL_EXERCISES_OVERRIDE` n'est pas dans l'allowlist. Vérifier `EXERCISES_AI_ALLOWED_MODEL_IDS` dans `app/core/ai_generation_policy.py`.

### Run persisté mais non visible en DB

Vérifier que la migration est appliquée :

```bash
alembic current
# Attendu : 20260322_ai_eval_harness_persistence (dans l'historique)
```

---

## 7. Limites documentées

- Mesure la conformité aux **validateurs existants**, pas la qualité pédagogique réelle.
- Un cas `OK` peut produire un énoncé ambigu ou inadapté à l'âge cible.
- Le corpus est figé : il ne couvre pas les cas de bord non anticipés.
- La campagne comparative ne mesure pas la cohérence pédagogique inter-modèles.
- Les coûts estimés en mode live sont des approximations (tarif au token, pas au call).

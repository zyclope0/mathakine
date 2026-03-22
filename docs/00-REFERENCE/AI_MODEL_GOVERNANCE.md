# Gouvernance des modeles IA - Mathakine

## 1. Vue d'ensemble

Mathakine gouverne trois workloads IA distincts : `assistant_chat`, `exercises_ai` et `challenges_ai`. La source de verite est le code type, pas un `.env` impose comme contrat produit. Les overrides environnement existent pour l'ops et la compatibilite legacy, mais les defauts produit restent codes dans les policies. L'observabilite runtime est separee entre metriques process en memoire et runs de harness persistables. Sources : `app/core/app_model_policy.py:1-32`, `app/core/ai_generation_policy.py:1-19`, `app/services/challenges/challenge_ai_model_policy.py:1-20`, `app/utils/token_tracker.py:167-221`, `app/utils/generation_metrics.py:123-136`, `app/evaluation/ai_generation_harness.py:128-199`.

## 2. Decision d'architecture

### Contexte avant refactor

Avant les lots IA10b et IA12, le chat pouvait encore etre influence par `OPENAI_MODEL`, les workloads pedagogiques n'etaient pas indexes par une reference transversale unique, et l'observabilite runtime n'etait pas explicitement separee des runs d'evaluation. Les variables legacy existent toujours dans `Settings`, mais elles sont documentees comme legacy ou overrides ops. Sources : `app/core/config.py:107-135`, `app/core/app_model_policy.py:9-28`, `app/core/ai_generation_policy.py:1-14`.

### Ce qui a ete choisi et pourquoi

- `assistant_chat` est gouverne par une allowlist fail-closed et un defaut produit explicite `gpt-5-mini`, avec un seam premium `gpt-5.4` et un fallback cheap `gpt-4o-mini`. Cela evite qu'un legacy env global pilote le chat par accident. Sources : `app/core/app_model_policy.py:61-73`, `app/core/app_model_policy.py:83-143`.
- `exercises_ai` garde `o3` comme defaut produit et delegue les families/kwargs a une policy dediee. Sources : `app/core/ai_generation_policy.py:39-64`, `app/core/ai_generation_policy.py:120-203`, `app/core/ai_generation_policy.py:203-235`.
- `challenges_ai` garde `o3` comme defaut produit, avec un fallback de stream `gpt-4o-mini` borne et une carte par type de defi. Sources : `app/services/challenges/challenge_ai_model_policy.py:39-59`, `app/services/challenges/challenge_ai_model_policy.py:74-112`.
- Les couts/tokens runtime et les metriques de qualite restent process-locales et bornees, alors que les runs d'evaluation peuvent etre persistables et relus separement. Sources : `app/utils/ai_workload_keys.py:25-36`, `app/utils/token_tracker.py:151-221`, `app/utils/token_tracker.py:313-332`, `app/utils/generation_metrics.py:33-53`, `app/utils/generation_metrics.py:123-136`, `app/utils/generation_metrics.py:231-240`, `app/evaluation/ai_generation_harness.py:128-199`.

### Alternatives rejetees

- Utiliser `OPENAI_MODEL` comme verite produit globale a ete rejete ; cette variable est legacy et explicitement ignoree pour `assistant_chat` si elle sort de l'allowlist. Sources : `app/core/config.py:107-118`, `app/core/app_model_policy.py:100-143`.
- Autoriser `o1` ou `o3` pour `assistant_chat` a ete rejete tant que le runtime chat ne supporte pas ces families dans son contrat courant. Sources : `app/core/app_model_policy.py:28-32`, `app/core/app_model_policy.py:67-90`, `app/services/communication/chat_service.py:345-397`.
- Presenter les couts admin comme une verite comptable a ete rejete ; `token_tracker` retourne explicitement des estimations basees sur une grille locale. Sources : `app/utils/token_tracker.py:88-128`, `app/utils/token_tracker.py:193-221`, `frontend/app/admin/ai-monitoring/page.tsx:81-127`.

## 3. Architecture actuelle

### Schema textuel du flux de decision modele

```text
requete frontend/backend
-> workload cible (`assistant_chat` | `exercises_ai` | `challenges_ai`)
-> policy de workload (defaut code + overrides ops/legacy bornes)
-> allowlist / family capabilities
-> construction des kwargs OpenAI adaptes
-> appel modele
-> token_tracker + generation_metrics
-> lecture admin read-only (`/api/admin/...`) ou harness persistable
```

References : `app/core/app_model_policy.py:100-187`, `app/core/ai_generation_policy.py:120-203`, `app/core/ai_generation_policy.py:203-262`, `app/services/challenges/challenge_ai_model_policy.py:74-112`, `app/services/communication/chat_service.py:257-397`, `server/handlers/chat_handlers.py:96-123`, `server/handlers/chat_handlers.py:201-238`, `server/handlers/admin_handlers.py:641-688`.

### Source de verite par workload

- `assistant_chat` : `app/core/app_model_policy.py:61-143` puis `app/services/communication/chat_service.py:257-397`.
- `exercises_ai` : `app/core/ai_generation_policy.py:39-64`, `app/core/ai_generation_policy.py:120-203`, `app/core/ai_generation_policy.py:203-262`.
- `challenges_ai` : `app/services/challenges/challenge_ai_model_policy.py:39-59`, `app/services/challenges/challenge_ai_model_policy.py:74-112`.
- Variables d'environnement supportees : `app/core/config.py:107-135`.

## 4. Modeles en production

| Workload | Modele par defaut | Allowlist / fallback | Fichier source |
|---|---|---|---|
| `assistant_chat` | `gpt-5-mini` | allowlist fail-closed : `gpt-5-mini`, `gpt-5.4`, `gpt-4o-mini`, `gpt-4o` ; fallback cheap controle `gpt-4o-mini` | `app/core/app_model_policy.py:61-73`, `app/core/app_model_policy.py:83-143` |
| `exercises_ai` | `o3` | allowlist `EXERCISES_AI_ALLOWED_MODEL_IDS` ; comportement par famille dans `MODEL_FAMILY_CAPABILITIES` | `app/core/ai_generation_policy.py:39-64`, `app/core/ai_generation_policy.py:120-203`, `app/core/ai_generation_policy.py:203-262` |
| `challenges_ai` | `o3` | allowlist heritee des exercices ; fallback stream `gpt-4o-mini` | `app/services/challenges/challenge_ai_model_policy.py:39-59`, `app/services/challenges/challenge_ai_model_policy.py:74-112` |

## 5. Observabilite runtime

### Ce qui est trace

- Tokens et cout estime OpenAI : `token_tracker.track_usage(...)` est alimente par le chat, les exercices IA et les defis IA. Sources : `server/handlers/chat_handlers.py:96-102`, `server/handlers/chat_handlers.py:201-207`, `app/services/exercises/exercise_ai_service.py:351-365`, `app/services/exercises/exercise_ai_service.py:397-398`, `app/services/exercises/exercise_ai_service.py:445-448`, `app/services/challenges/challenge_ai_service.py:385-391`, `app/services/challenges/challenge_ai_service.py:453-458`.
- Qualite runtime / succes / erreurs / duree : `generation_metrics.record_generation(...)` est alimente sur succes et erreurs des trois workloads. Sources : `server/handlers/chat_handlers.py:102-123`, `server/handlers/chat_handlers.py:207-238`, `app/services/exercises/exercise_ai_service.py:216-227`, `app/services/exercises/exercise_ai_service.py:269-321`, `app/services/exercises/exercise_ai_service.py:365-472`, `app/services/challenges/challenge_ai_service.py:250`, `app/services/challenges/challenge_ai_service.py:543`, `app/services/challenges/challenge_ai_service.py:581`.
- Classification par workload et retention bornee : `assistant_chat`, `exercises_ai`, `challenges_ai`, `unknown`, avec retention 90 jours / 2000 evenements par cle. Sources : `app/utils/ai_workload_keys.py:25-36`, `app/utils/ai_workload_keys.py:52-85`.
- Lecture admin read-only : endpoints `/api/admin/ai-stats`, `/api/admin/generation-metrics`, `/api/admin/ai-eval-harness-runs`, puis page frontend de monitoring. Sources : `server/routes/admin.py:149-157`, `server/handlers/admin_handlers.py:641-688`, `frontend/hooks/useAdminAiStats.ts:75-139`, `frontend/app/admin/ai-monitoring/page.tsx:60-127`, `frontend/app/admin/ai-monitoring/page.tsx:551-604`.
- Runs harness persistables et relisibles separement : service admin read-only + CLI harness. Sources : `app/services/admin/admin_read_service.py:214-229`, `app/evaluation/ai_generation_harness.py:128-199`, `app/evaluation/ai_generation_harness.py:341-360`.

### Comment lire les metriques

- `stats.by_workload` et `summary.by_workload` donnent la vue stable par workload ; `by_type` garde la granularite fine (`assistant_chat:simple`, `exercise_ai:addition`, etc.). Sources : `app/utils/token_tracker.py:207-221`, `app/utils/generation_metrics.py:123-158`, `frontend/app/admin/ai-monitoring/page.tsx:73-79`.
- La page admin rappelle explicitement que le chat est public, que les couts sont estimatifs et que la retention runtime est bornee. Sources : `frontend/app/admin/ai-monitoring/page.tsx:81-127`.
- Les runs harness persistants servent a relire des campagnes figees et ne doivent pas etre confondus avec les agregats process. Sources : `app/services/admin/admin_read_service.py:214-229`, `frontend/app/admin/ai-monitoring/page.tsx:551-604`.

### Limites explicites

- `token_tracker` et `generation_metrics` sont en memoire process, avec purge de retention ; ils ne survivent pas a un restart. Sources : `app/utils/token_tracker.py:167-221`, `app/utils/token_tracker.py:313-332`, `app/utils/generation_metrics.py:123-136`, `app/utils/generation_metrics.py:231-240`.
- Les couts sont des estimations basees sur une table locale, avec fallback `gpt-4o-mini` si un modele manque dans la grille. Sources : `app/utils/token_tracker.py:88-128`, `app/utils/token_tracker.py:193-221`.
- Les runs harness persistants sont un canal distinct et opt-in, pas une persistence generique de toutes les metriques runtime. Sources : `app/evaluation/ai_generation_harness.py:128-199`, `app/services/admin/admin_read_service.py:214-229`.

## 6. Comment modifier

### Changer le modele par defaut d'un workload

- Chat : modifier `DEFAULT_ASSISTANT_CHAT_MODEL`, puis verifier l'allowlist `ASSISTANT_CHAT_ALLOWED_MODEL_IDS` et la compatibilite des kwargs chat. Sources : `app/core/app_model_policy.py:61-73`, `app/core/app_model_policy.py:100-143`, `app/services/communication/chat_service.py:345-397`.
- Exercices : modifier `DEFAULT_EXERCISES_AI_MODEL`, puis verifier `MODEL_FAMILY_CAPABILITIES` et `build_openai_chat_completion_kwargs`. Sources : `app/core/ai_generation_policy.py:64`, `app/core/ai_generation_policy.py:120-203`, `app/core/ai_generation_policy.py:203-262`.
- Defis : modifier `DEFAULT_CHALLENGES_AI_MODEL`, puis verifier `CHALLENGE_MODEL_BY_TYPE` et le fallback stream. Sources : `app/services/challenges/challenge_ai_model_policy.py:39-59`, `app/services/challenges/challenge_ai_model_policy.py:74-112`.

### Ajouter un nouveau workload IA

1. Declarer une cle de workload stable et sa classification. Source : `app/utils/ai_workload_keys.py:25-81`.
2. Alimenter `token_tracker.track_usage(...)` et `generation_metrics.record_generation(...)` dans le service ou handler du workload. Sources de pattern : `server/handlers/chat_handlers.py:96-123`, `app/services/exercises/exercise_ai_service.py:351-472`, `app/services/challenges/challenge_ai_service.py:385-581`.
3. Exposer la lecture admin si la vue read-only doit le montrer. Sources : `server/handlers/admin_handlers.py:641-688`, `frontend/hooks/useAdminAiStats.ts:75-139`, `frontend/app/admin/ai-monitoring/page.tsx:60-127`.

### Ajouter un modele a l'allowlist

1. Modifier l'allowlist du workload concerne. Sources : `app/core/app_model_policy.py:67-90`, `app/core/ai_generation_policy.py:39-57`, `app/services/challenges/challenge_ai_model_policy.py:59-69`.
2. Si la famille implique des kwargs differents, mettre a jour la construction OpenAI correspondante. Sources : `app/services/communication/chat_service.py:345-397`, `app/core/ai_generation_policy.py:120-203`, `app/core/ai_generation_policy.py:252-321`.
3. Mettre a jour la table de prix locale si le workload est observe en cout runtime. Source : `app/utils/token_tracker.py:88-128`.

## 7. Verification

Executer au minimum apres toute modification de gouvernance IA :

```bash
python -m pytest tests/unit/test_app_model_policy.py tests/unit/test_chat_service.py tests/unit/test_exercise_ai_policy.py tests/unit/test_challenge_ia4_prompt_and_model_policy.py tests/unit/test_token_tracker.py tests/unit/test_generation_metrics.py tests/api/test_admin_ai_stats.py -q --tb=short
python -m black app/ server/ tests/ --check
python -m isort app/ server/ tests/ --check-only
```

Pour verifier la couche evaluation / campagnes :

```bash
python -m app.evaluation.ai_generation_harness --list-persisted
python -m app.evaluation.comparative_campaign --campaign ia11a_offline_default
```

References de validation : `tests/unit/test_app_model_policy.py`, `tests/unit/test_chat_service.py`, `tests/unit/test_exercise_ai_policy.py`, `tests/unit/test_token_tracker.py`, `tests/unit/test_generation_metrics.py`, `tests/api/test_admin_ai_stats.py`, `app/evaluation/ai_generation_harness.py:341-360`, `app/evaluation/comparative_campaign.py:219-236`, `app/evaluation/comparative_campaign.py:524-652`.

## 8. Limites et decisions assumees

- Chat public sans auth : les handlers chat sont exposes avec `@rate_limit_chat` mais sans `require_auth`, par decision produit. Sources : `server/handlers/chat_handlers.py:41`, `server/handlers/chat_handlers.py:133`.
- Couts = estimations, pas comptabilite : la page admin et `token_tracker` le disent explicitement. Sources : `app/utils/token_tracker.py:193-221`, `frontend/app/admin/ai-monitoring/page.tsx:81-127`.
- Runtime in-memory, pas persistant cross-restart : les agregats admin runtime viennent de structures process bornees. Sources : `app/utils/token_tracker.py:167-221`, `app/utils/token_tracker.py:313-332`, `app/utils/generation_metrics.py:123-136`, `app/utils/generation_metrics.py:231-240`.
- Les runs harness persistants ne remplacent pas les stats runtime ; ils servent aux campagnes figees et a la reproductibilite. Sources : `app/evaluation/ai_generation_harness.py:128-199`, `app/services/admin/admin_read_service.py:214-229`.

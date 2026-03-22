# Audit Couche IA -- Mathakine -- 2026-03-22
> ⚠️ OBSOLETE comme source de verite runtime - snapshot historique de revue conserve pour trace.
> La reference actuelle pour la gouvernance IA runtime et l'observabilite est [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md).

## Verdict global

| Workload | Score | Justification |
|---|---|---|
| **Challenges AI** | **8/10** | Pipeline le plus mature : retry tenacity, timeout explicite, fallback o3, auto-correction, validation profonde par type, contrat IA9 `response_mode`, calibration difficulte. Reste la fuite d'erreur API brute (voir C-1). |
| **Exercises AI** | **6.5/10** | Validation structurelle correcte, policy modele solide, mais **zero retry**, **zero timeout client**, pas d'auto-correction, observabilite incoherente avec les defis (`challenge_type` comme nom de parametre pour des exercices). |
| **Assistant Chat** | **5.5/10** | Observabilite cablee (bien), gouvernance modele propre, mais **zero retry**, **zero timeout client**, **zero validation du contenu genere**, rate limit par IP uniquement (pas par user\_id), DALL-E hors tracking tokens. |

**Verdict de coherence inter-workloads : 5/10.** Les trois workloads ont ete developpes a des moments differents avec des philosophies divergentes. Les defis ont servi de terrain d'innovation (retry, fallback, auto-correction, contrat IA9) sans que ces acquis soient repliques vers exercices et chat. Le socle d'observabilite est unifie (token\_tracker + generation\_metrics + ai\_workload\_keys), mais l'alimentation est asymetrique.

---

## Coherence inter-workloads

### Tableau comparatif

| Dimension | Challenges AI | Exercises AI | Assistant Chat |
|---|---|---|---|
| **Validation output** | `validate_challenge_logic` + `auto_correct_challenge` + contrat IA9 (choices, response\_mode, symmetrie) | `validate_exercise_ai_output` (longueurs, choix, numerique) -- pas d'auto-correction | Aucune validation du contenu -- seul `cleanup_markdown_images` |
| **Retry / resilience** | `tenacity` : 3 tentatives, backoff exponentiel, retry sur `RateLimitError`, `APIError`, `APITimeoutError` | **Aucun retry** | **Aucun retry** |
| **Timeout client** | `AsyncOpenAI(timeout=ai_params["timeout"])` -- 90s/180s selon type | **Aucun timeout explicite** (defaut SDK ~600s) | **Aucun timeout explicite** (defaut SDK) |
| **Fallback modele** | Oui : si o3 stream vide -> `resolve_challenge_ai_fallback_model` (gpt-4o-mini) | **Non** | **Non** |
| **Prompt sanitization** | Via `challenge_stream_service.prepare_stream_context` -> `sanitize_user_prompt` + `validate_prompt_safety` | Via `exercise_stream_service.prepare_stream_context` -> idem | Via handler direct -> `sanitize_user_prompt` + `validate_prompt_safety` |
| **Rate limiting** | `check_ai_generation_rate_limit(user_id)` -- 10/h, 50/j par user | `check_exercise_ai_generation_rate_limit(user_id)` -- 10/h, 50/j par user | `@rate_limit_chat` -- 15/min **par IP**, pas par user |
| **Observabilite tokens** | `token_tracker.track_usage(challenge_type=challenge_type)` | `token_tracker.track_usage(challenge_type=metrics_key)` avec prefix `exercise_ai:` | `token_tracker.track_usage(challenge_type=metrics_key)` avec prefix `assistant_chat:` |
| **Observabilite metriques** | `generation_metrics.record_generation` sur tous les chemins (succes, echec, validation, auto-correction) | `generation_metrics.record_generation` sur tous les chemins | `generation_metrics.record_generation` sur succes et echec |
| **Circuit-breaker** | Absent | Absent | Absent |
| **Erreurs exposees au frontend** | `sse_error_message(str(gen_error))` -- **fuite possible** d'exception brute | `str(gen_error)` direct dans SSE JSON -- **fuite possible** | `get_safe_error_message(error)` -- **filtre** |
| **Evenement SSE `done`** | Oui (explicite) | **Non** (fin implicite du stream) | Oui (explicite dans stream) |
| **Evenement SSE `chunk`** | Non (accumulation backend, envoi final) | Non (accumulation backend, envoi final) | Oui (chunks progressifs) |

### Prompt sanitization

Coherente sur les trois workloads : les trois passent par `validate_prompt_safety` + `sanitize_user_prompt`. Point positif.

### Rate limiting -- asymetrie assumee mais risquee

- Exercices et defis : par **user\_id** (10/h, 50/j). Protege bien contre l'abus connecte.
- Chat : par **IP** (15/min). Le chat est public (pas d'auth). Consequence : un utilisateur derriere un NAT partage son quota avec tous les autres utilisateurs du meme reseau. Un attaquant avec des IPs rotatives contourne entierement la limite.

Ce n'est pas une incoherence accidentelle -- c'est une decision produit (chat public). Mais le cout OpenAI du chat (modele `gpt-5-mini`) n'est pas negligeable, et l'absence de rate limit par session rend le chat plus exploitable que les deux autres workloads.

---

## Problemes residuels

### Critiques

**C-1 : Fuite d'exceptions internes dans les messages SSE (exercices + defis)**

```python
# exercise_ai_service.py ligne 405
yield f"data: {json.dumps({'type': 'error', 'message': str(gen_error)})}\n\n"

# challenge_ai_service.py ligne 508
yield sse_error_message(str(gen_error))

# challenge_ai_service.py ligne 316
yield sse_error_message(
    f"Erreur lors de la generation apres plusieurs tentatives: {str(api_error)}"
)
```

`str(gen_error)` peut contenir des tracebacks, des messages d'API OpenAI (incluant potentiellement des fragments de cle API dans certaines versions du SDK), ou des chemins serveur. Le chat utilise `get_safe_error_message()` -- les exercices et les defis ne le font pas. **C'est le seul probleme de securite reel de cet audit.**

**C-2 : Exercices AI sans retry ni timeout = generation silencieusement bloquee**

L'appel `await client.chat.completions.create(**api_kwargs)` dans `exercise_ai_service.py` n'a pas de retry tenacity ni de timeout client. Le timeout par defaut du SDK OpenAI est de ~10 minutes. Un appel qui echoue (rate limit temporaire, timeout reseau) ne sera pas retente. L'utilisateur recoit un message d'erreur generique apres un delai potentiellement tres long.

Les defis ont resolu ce probleme avec `create_stream_with_retry`. Les exercices ne l'ont pas replique.

### Majeurs

**M-1 : Le parametre `challenge_type` est encore utilise comme nom de parametre dans `token_tracker` et `generation_metrics` pour les trois workloads**

Le docstring de `generation_metrics.py` dit explicitement : _"The historical parameter name `challenge_type` is retained for backward compatibility, but now stores a generic AI metric key."_ Le nommage est trompeur : quand on trace un exercice, on appelle `challenge_type="exercise_ai:addition"`. Ce n'est pas un challenge. Le code fonctionne, mais tout contributeur futur sera induit en erreur. C'est un candidat IA14 (cleanup naming).

**M-2 : `AIConfig` (ai\_config.py) contient des constantes `ADVANCED_MODEL` et `BASIC_MODEL` orphelines**

```python
ADVANCED_MODEL: str = "gpt-5.1"
BASIC_MODEL: str = "gpt-5-mini"
```

Ces constantes ne sont referencees nulle part dans le flux de resolution de modele. Leur docstring dit _"Reference historique (non utilisee par le flux defis ; fallback vide o3 -> policy dediee)."_ Ce sont des vestiges qui creent de la confusion sur la source de verite. La source de verite reelle est `app_model_policy.py` + `ai_generation_policy.py` + `challenge_ai_model_policy.py`.

**M-3 : Le generateur local `generate_ai_exercise()` dans `exercise_generator.py` porte un nom trompeur**

La fonction `generate_ai_exercise()` n'appelle pas l'API OpenAI. C'est un generateur local deterministe avec des templates Star Wars. Le nom "ai" est trompeur car le vrai pipeline IA est dans `exercise_ai_service.py` (`generate_exercise_stream`). La distinction est explicitement documentee dans le code (`exercise_generation_policy.py` dit "non-LLM"), mais le nommage cree une ambiguite pour un nouveau contributeur.

**M-4 : DALL-E echappe au token\_tracker**

L'appel `await client.images.generate(model="dall-e-3", ...)` dans `chat_service.py` n'est pas trace dans `token_tracker`. C'est un appel payant ($0.04-0.08/image) qui n'apparait dans aucune metrique de cout. Pour un solo developer, c'est un trou dans l'observabilite budgetaire.

**M-5 : Exercices AI n'emettent pas d'evenement `done`**

Le stream exercices termine apres l'envoi de l'evenement `exercise` ou `error`. Les defis envoient explicitement `{"type": "done"}`. Le frontend exercices ne l'attend pas (pas de probleme fonctionnel), mais c'est une asymetrie de contrat SSE qui peut causer des bugs si le frontend evolue pour attendre un `done` explicite, ce qui est la convention dans les defis et le chat.

**M-6 : Token tracking conditionnel dans les defis vs inconditionnel dans les exercices**

Dans `challenge_ai_service.py`, `token_tracker.track_usage` n'est appele que si le challenge est persist avec succes (ligne 463). Dans `exercise_ai_service.py`, `_track_openai_cost()` est appele dans tous les cas (succes, echec validation, erreur JSON). Les tokens sont consommes et factures par OpenAI quelle que soit la persistance -- les defis sous-rapportent donc leur consommation reelle en cas d'echec de persistance ou de validation.

### Mineurs

**m-1 : Duplication de la logique `getBackendUrl()` dans les routes proxy Next.js**

Les fichiers `frontend/app/api/exercises/generate-ai-stream/route.ts` et `frontend/app/api/challenges/generate-ai-stream/route.ts` dupliquent mot pour mot la logique `BACKEND_URL` + `getBackendUrl()`. Le chat proxy fait la meme chose differemment (inline). Un utilitaire partage suffirait.

**m-2 : `stream_options: {"include_usage": True}` present dans les exercices, absent des defis**

`build_exercise_ai_stream_kwargs` ajoute `stream_options: {"include_usage": True}` pour recuperer les tokens reels en fin de stream. Le code des defis (`create_stream_with_retry`) ne le fait pas -- il utilise une estimation `len(full_response) // 4`. Les exercices ont donc des metriques de tokens plus fiables que les defis.

**m-3 : Default model dans `token_tracker.track_usage` est `gpt-4o-mini`**

Le parametre `model` a un defaut `"gpt-4o-mini"` dans la signature. Ce n'est plus le modele par defaut d'aucun workload (defaut exercises/challenges = `o3`, defaut chat = `gpt-5-mini`). Ce defaut n'est jamais utilise en pratique (tous les appelants passent le modele explicitement), mais il est trompeur.

**m-4 : Le chat stream passe `None` comme premier argument de `extract_chat_usage_estimate`**

Ligne 196-199 du chat handler stream : `extract_chat_usage_estimate(None, ...)`. La fonction gere ce cas (fallback estimation), mais le stream ne demande pas `include_usage` a l'API, donc les tokens reels ne sont jamais disponibles pour le chat stream.

---

## Incoherences philosophiques

### 1. Politique d'echec : fail-closed vs fail-open

Les **defis** adoptent une philosophie **fail-closed progressif** : si la validation echoue, on tente l'auto-correction. Si l'auto-correction echoue, on refuse de persister et on remonte une erreur. Mais si la persistance echoue, on envoie quand meme le challenge au frontend avec un warning -- c'est un **fail-open partiel**.

Les **exercices** sont strictement **fail-closed** : si la validation echoue, c'est un refus pur. Si la persistance echoue, c'est un refus pur. Pas de warning, pas de contenu non persiste.

Le **chat** est **fail-open** : si l'appel OpenAI echoue, le frontend Next.js retourne un message de fallback poli ("service non disponible"). Pas de code d'erreur HTTP, pas de `type: error` dans la reponse JSON.

Ce sont trois philosophies differentes pour trois workloads du meme produit. La question n'est pas laquelle est la bonne, mais pourquoi elles divergent sans que cette divergence soit documentee comme une decision produit.

### 2. Granularite de la policy modele : exercices vs defis

La policy modele des exercices (`ai_generation_policy.py`) a une architecture admirablement typee : `ExerciseAIModelFamily`, `ModelFamilyCapabilities`, matrice de capacites, `build_exercise_ai_stream_kwargs` qui compose les kwargs en fonction de la famille. C'est le modele a suivre.

La policy modele des defis (`ai_config.py` + `challenge_ai_model_policy.py`) reste procedurale : `if/elif` dans `create_stream_with_retry` pour determiner les kwargs, duplication de la logique `is_o1_model`/`is_o3_model`/`is_gpt5_model` entre `AIConfig` et `ai_generation_policy`. La resolution du modele est centralisee (`challenge_ai_model_policy`), mais la composition des kwargs ne l'est pas.

### 3. Evenements SSE : contrat implicite vs contrat explicite

Les exercices emettent : `status`, `exercise`, `error`. Jamais `warning`, jamais `done`, jamais `chunk`.
Les defis emettent : `status`, `challenge`, `error`, `done`. Jamais `chunk` (accumulation backend).
Le chat emet : `status`, `chunk`, `done`, `error`, `image`.

Le frontend gere les trois correctement, mais il n'y a pas de contrat SSE documente ou type qui garantit la coherence. Les dispatchers frontend (`dispatchExerciseAiSseEvent` et `dispatchChallengeAiSseEvent`) gerent `warning` et `done` de facon identique meme si le backend exercices ne les emet jamais. C'est du code defensif correct, mais symptomatique d'un contrat non formalise.

---

## Points solides

1. **Gouvernance modele centralisee et fail-closed.** La chaine `app_model_policy` -> `ai_generation_policy` -> `challenge_ai_model_policy` est bien conÃ§ue. Les allowlists sont explicites, les overrides sont hierarchiques et documentes, les familles o1/o3/gpt-5 sont correctement isolees par workload. Changer le modele par defaut des exercices est un changement en **1 endroit** (`DEFAULT_EXERCISES_AI_MODEL`). Changer celui des defis est en **1 endroit** (`DEFAULT_CHALLENGES_AI_MODEL` ou `CHALLENGE_MODEL_BY_TYPE`). Changer celui du chat est en **1 endroit** (`DEFAULT_ASSISTANT_CHAT_MODEL`).

2. **Observabilite par workload.** Le systeme `ai_workload_keys.py` avec `classify_ai_workload_key` est solide : il classe chaque cle metrique vers le bon bucket workload sans heuristique fragile. Le `daily_summary` couvre bien les trois workloads grace a la convention de prefixes (`exercise_ai:*`, `assistant_chat:*`, types defis nus).

3. **Validation contenu des defis.** La chaine `challenge_validator` -> `challenge_contract_policy` -> `challenge_difficulty_policy` -> `challenge_answer_quality` est la plus mature du projet. L'auto-correction par type (PATTERN, SEQUENCE, VISUAL, CODING/maze) est une force unique. Le contrat IA9 (`response_mode` dicte par le serveur) est bien implemente.

4. **Prompt composition modulaire pour les defis.** La separation `challenge_prompt_composition` / `challenge_prompt_sections` avec injection conditionnelle par type reduit le volume de tokens envoyes au LLM. C'est un bon pattern economique.

5. **Frontend symetrique.** Les hooks `useAIExerciseGenerator` et `useAIChallengeGenerator` partagent le meme socle (`postAiGenerationSse` + `consumeSseJsonEvents`) et les memes patterns (abort controller, isGenerating, cancel). Les dispatchers sont structurellement identiques. Les routes proxy sont quasi identiques. C'est facile a maintenir.

6. **Sanitization coherente.** Les trois workloads passent par `validate_prompt_safety` + `sanitize_user_prompt` avant tout appel LLM. Pas de chemin qui echappe a la sanitization.

---

## Plan de cloture recommande

### Priorite 1 -- Securite (avant toute mise en production)

| # | Action | Fichiers | Effort |
|---|---|---|---|
| **P1-1** | Remplacer `str(gen_error)` par `get_safe_error_message(gen_error)` dans les messages SSE exercices + defis | `exercise_ai_service.py:405`, `challenge_ai_service.py:316,508` | 15 min |

### Priorite 2 -- Resilience (prochaine iteration)

| # | Action | Fichiers | Effort |
|---|---|---|---|
| **P2-1** | Ajouter retry tenacity + timeout client au flux exercices AI (meme pattern que defis) | `exercise_ai_service.py` | 1h |
| **P2-2** | Ajouter retry + timeout au flux chat stream | `chat_handlers.py` | 1h |
| **P2-3** | Tracer les couts DALL-E dans `token_tracker` (prix par image, pas par token) | `chat_service.py`, `token_tracker.py` | 30 min |
| **P2-4** | Rendre le token tracking inconditionnel dans les defis (tracer meme si persistance echoue) | `challenge_ai_service.py` | 30 min |

### Priorite 3 -- Coherence technique (IA14 naming + contrat SSE)

| # | Action | Fichiers | Effort |
|---|---|---|---|
| **P3-1** | Renommer le parametre `challenge_type` en `metric_key` dans `token_tracker` et `generation_metrics` (backward-compat via alias) | `token_tracker.py`, `generation_metrics.py` + tous les appelants | 2h |
| **P3-2** | Emettre `done` dans le flux exercices AI pour symetrie avec defis et chat | `exercise_ai_service.py` | 15 min |
| **P3-3** | Ajouter `stream_options: {"include_usage": True}` dans le flux defis pour tokens reels | `challenge_ai_service.py` | 15 min |
| **P3-4** | Supprimer `ADVANCED_MODEL` et `BASIC_MODEL` orphelins dans `AIConfig` | `ai_config.py` | 5 min |
| **P3-5** | Renommer `generate_ai_exercise` en `generate_local_exercise` (ou `generate_template_exercise`) dans `exercise_generator.py` | `exercise_generator.py` + appelants | 1h |
| **P3-6** | Extraire `getBackendUrl()` dans un utilitaire partage frontend | `frontend/app/api/*/route.ts` | 30 min |
| **P3-7** | Changer le default model dans `token_tracker.track_usage` de `gpt-4o-mini` a une constante importee depuis la policy | `token_tracker.py` | 10 min |

### Priorite 4 -- Architecture (futur lot)

| # | Action | Justification | Effort |
|---|---|---|---|
| **P4-1** | Refactorer la composition des kwargs defis pour utiliser le pattern `ModelFamilyCapabilities` des exercices | Eliminer la duplication `if/elif is_o1/is_o3/is_gpt5` entre `create_stream_with_retry` et `build_exercise_ai_stream_kwargs` | 4h |
| **P4-2** | Formaliser le contrat SSE dans un schema partage (TypedDict backend, interface TypeScript frontend) | Les trois workloads emettent des evenements sans contrat type ; le frontend est defensif mais fragile | 3h |
| **P4-3** | Ajouter un circuit-breaker OpenAI partage (compteur d'echecs consecutifs -> temporisation automatique) | Absent des trois workloads ; risque en cas de panne OpenAI prolongee | 4h |
| **P4-4** | Ajouter rate limiting par session/fingerprint pour le chat (completer le rate limit par IP) | Le chat public est le workload le plus exposable actuellement | 2h |

---

## Annexe : verification de la source de verite modele

**Question : Si demain on veut changer de modele, est-ce un changement en 1 endroit ou N endroits ?**

- **Exercices AI** : 1 endroit (`DEFAULT_EXERCISES_AI_MODEL` dans `ai_generation_policy.py`). Override possible via env `OPENAI_MODEL_EXERCISES_OVERRIDE`.
- **Challenges AI** : 1 endroit (`DEFAULT_CHALLENGES_AI_MODEL` dans `challenge_ai_model_policy.py`), ou N endroits si on veut differencier par type (`CHALLENGE_MODEL_BY_TYPE`). Override possible via env `OPENAI_MODEL_CHALLENGES_OVERRIDE`.
- **Assistant Chat** : 1 endroit (`DEFAULT_ASSISTANT_CHAT_MODEL` dans `app_model_policy.py`). Override possible via env `OPENAI_MODEL_ASSISTANT_CHAT_OVERRIDE`.

Aucun modele n'est hardcode en dehors des fichiers de policy. `AIConfig.ADVANCED_MODEL` et `AIConfig.BASIC_MODEL` existent mais ne sont jamais utilises dans le flux de resolution. Pas de modele hardcode dans les handlers, les routes, ou le frontend.

Les allowlists exercices et defis sont identiques (`CHALLENGES_AI_ALLOWED_MODEL_IDS = EXERCISES_AI_ALLOWED_MODEL_IDS`). L'allowlist chat est separee et volontairement plus restrictive (pas d'o1/o3). C'est coherent avec la doctrine : raisonnement pour les workloads structures, chat classique pour l'assistant.

**Verdict gouvernance modeles : solide.**


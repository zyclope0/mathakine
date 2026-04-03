# Plan CC1 - Clean Code Pass post-F42/F43

**Date :** 2026-03-28
**Source :** rapport /octo:review working tree (Correctness + Architecture, AI-assisted)
**Execution :** Cursor Composer
**Validation :** `pytest -q --maxfail=20 --no-cov` + `black` + `isort` + `flake8` apres chaque lot

---

## Addendum Frontend - 2026-04-03

> Ce fichier garde l'historique du plan `CC1` backend.
> L'addendum ci-dessous sert de **session-plan courant** pour le frontend, afin d'eviter
> une divergence entre la memoire Claude et les audits projet.

### 0. Verite d'execution courante

**Source de verite frontend**

- `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`
- `docs/03-PROJECT/DEBAT_NEURO_INCLUSION_2026-03-30.md`
- `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` reste un audit historique, plus un plan actif

**Etat FFI (commite + pousse)**

- `FFI-L1` a `FFI-L9` : livres
- `FFI-L10` : prochain lot critique (`ChallengeSolver`)
- `FFI-L11` a `FFI-L13` : ouverts, apres stabilisation solver

**Etat NI (worktree local relu au 2026-04-03)**

- `NI-1` : fait localement
- `NI-2` : fait localement
- `NI-3` : fait localement
- `NI-4` : backlog
- `NI-5` : a faire
- `NI-6` : fait localement
- `NI-7` : fait localement
- `NI-8` : fait localement

### 1. Prochain ordre recommande

```text
1. Stabiliser / integrer proprement les travaux NI locaux si l'objectif est de les garder
2. FFI-L10 : split ChallengeSolver
3. FFI-L11 : couleurs semantiques hardcodees
4. FFI-L12 : split Header.tsx
5. FFI-L13 : doc design system + clarification chatbot
```

### 2. Gardes-fous frontend

1. **Ne pas sur-declarer "fait"** : distinguer explicitement `commite/pousse`, `local`, `backlog`.
2. **Dashboard != solver** : ne pas faire passer du hors-scope dashboard comme lot apprenant sans le documenter.
3. **Neuro-inclusion** : zero mouvement non essentiel pendant la phase de reflexion ; conserver les neutralisations `[data-learner-context]`.
4. **Industrialisation** : garder `FFI-Lx` comme ordre de reference, pas les anciens audits phase/par phase.
5. **Docs** : toute evolution NI/FFI doit realigner ces 3 fichiers en meme temps :
   - `DEBAT_NEURO_INCLUSION_2026-03-30.md`
   - `AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`
   - `AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md`

---

## 1. Contexte

Passe de nettoyage post-F42/F43 sur le projet Mathakine.
7 findings identifies, classes en 3 categories :

- **Bugs** (P0) : encoding corruption + clamp manquant
- **Code mort** (P1) : 2 suppressions sures
- **DRY** (P2) : 2 violations de coherence, differables

---

## 2. Sequencage

```text
[DONE] CC1-L1 : Bugs P0 + code mort P1 (lot atomique, 5 fichiers)
[DONE] CC1-L2 : DRY P2 - exercise_ai_service aligne sur sse_utils (1 fichier)
[DONE] CC1-L3 : DRY P2 - challenge dispatch extracted (scope borne, helper dedie)
[DONE] CC1-L4 : CLAUDE.md - supprimer P1 challenge_service deja resolu
```

---

## 3. Detail des lots

### CC1-L1 - Bugs + suppressions (priorite haute)

**Fichiers :** 5 fichiers backend

#### BUG-1 : Encoding `exercise_ai_service.py`

- **Fichier :** `app/services/exercises/exercise_ai_service.py`
- **Probleme :** le fichier contient une corruption UTF-8 -> Latin-1 sur des chaines francaises
  (`generation`, `evenements SSE`, `Bibliotheque`, etc.)
- **Action :** re-encoder le fichier proprement et corriger les chaines corrompues dans
  docstrings, messages d'erreur et prompts IA
- **Impact :** prompts IA degrades ; messages d'erreur illisibles

#### BUG-1b : Encoding `challenge_ai_service.py:84`

- **Fichier :** `app/services/challenges/challenge_ai_service.py`
- **Ligne :** 84
- **Action :** corriger la chaine du log (`Groupe d'age`, `non trouve`)

#### BUG-2 : Clamp manquant `mastery_tier_bridge.py`

- **Fichier :** `app/core/mastery_tier_bridge.py`
- **Fonction :** `project_challenge_progress_row_f42()` ligne 230
- **Probleme :** `compute_tier_from_age_group_and_band()` est appele sans clamp alors que
  `mastery_to_tier()` dans le meme fichier clamp + warn explicitement
- **Action :** ajouter clamp `max(DIFFICULTY_TIER_MIN, min(DIFFICULTY_TIER_MAX, raw))` +
  warning logger si out-of-bounds, en miroir de `mastery_to_tier()`
- **Risque si non corrige :** tier hors [1-12] silencieux cote defis

#### D1 : Dead attrs `AIConfig.ADVANCED_MODEL / BASIC_MODEL`

- **Fichier :** `app/core/ai_config.py` lignes 21-23
- **Preuve :** `test_challenge_ia4_prompt_and_model_policy.py:143` asserte
  `"ADVANCED_MODEL" not in src`
- **Action :** supprimer les 3 lignes (commentaire + 2 attributs)
- **Risque :** zero - aucun caller en dehors du test de non-utilisation

#### D2 : Dead function `experience_points_in_current_level()`

- **Fichier :** `app/services/gamification/compute.py` lignes 88-91
- **Preuve :** jamais importe ni appele (grep exhaustif, 0 resultat hors definition)
- **Corps :** alias d'une ligne de `level_and_xp_from_total_points()`
- **Action :** supprimer la fonction entiere
- **Risque :** zero - aucun caller

**Gate CC1-L1 :**

```powershell
D:\Mathakine\.venv\Scripts\python.exe -m pytest tests\ -q --tb=short --maxfail=20 --no-cov --ignore=tests\api\test_admin_auth_stability.py
D:\Mathakine\.venv\Scripts\python.exe -m black app/services/exercises/exercise_ai_service.py app/services/challenges/challenge_ai_service.py app/core/mastery_tier_bridge.py app/core/ai_config.py app/services/gamification/compute.py --check
D:\Mathakine\.venv\Scripts\python.exe -m isort app/services/exercises/exercise_ai_service.py app/services/challenges/challenge_ai_service.py app/core/mastery_tier_bridge.py app/core/ai_config.py app/services/gamification/compute.py --check-only
D:\Mathakine\.venv\Scripts\python.exe -m flake8 --select=E9,F63,F7,F82 app/services/exercises/exercise_ai_service.py app/services/challenges/challenge_ai_service.py app/core/mastery_tier_bridge.py app/core/ai_config.py app/services/gamification/compute.py
```

---

### CC1-L2 - DRY : aligner exercise_ai_service sur sse_utils (priorite moyenne)

**Fichier :** `app/services/exercises/exercise_ai_service.py`

`app/utils/sse_utils.py` expose `sse_error_message()` et `sse_status_message()` avec
docstring "DRY pour generation IA en streaming". `challenge_ai_service.py` l'utilise.
`exercise_ai_service.py` utilise des f-strings inline identiques partout.

**Action :**

1. Ajouter l'import `from app.utils.sse_utils import sse_error_message, sse_status_message`
2. Remplacer tous les `f"data: {json.dumps({'type': 'error', ...})}\n\n"` par `sse_error_message(...)`
3. Remplacer `f"data: {json.dumps({'type': 'status', ...})}\n\n"` par `sse_status_message(...)`
4. Laisser `_SSE_DONE` inline

**Benefice :** coherence maintenance - une seule definition du format SSE

---

### CC1-L3 - DRY : challenge dispatch model (realise)

**Contexte :** `challenge_ai_service.py:329-367` a sa propre logique de dispatch modele
(o1/o3/gpt5/fallback) inline dans `create_stream_with_retry()`. `ai_generation_policy.py`
a `build_exercise_ai_stream_kwargs()` qui fait la meme chose proprement.

**Recommandation :** creer `build_challenge_ai_stream_kwargs()` dans
`challenge_ai_model_policy.py` symetriquement a `build_exercise_ai_stream_kwargs()`.

**Decision initiale :** differe - scope plus large (fallback o3 + alignement `AIConfig.get_openai_params()`).
**Statut final :** realise avec helper borne, sans elargir le scope ni toucher au fallback non-stream.

**Analyse precise du differe :**

- c'est le **seul vrai differe** du plan CC1
- le lot ne doit pas devenir une refonte de toute la policy IA defis
- la source de verite actuelle des params reste `AIConfig.get_openai_params(challenge_type)`
- le helper a extraire doit seulement construire les kwargs OpenAI du **stream principal**
- le fallback stream vide (`resolve_challenge_ai_fallback_model`) reste hors lot

**Scope max effort applicable si le lot est reactive plus tard :**

1. **Fichiers autorises (stricts)**
   - `app/services/challenges/challenge_ai_service.py`
   - `app/services/challenges/challenge_ai_model_policy.py`
   - `tests/unit/test_challenge_ia4_prompt_and_model_policy.py`
   - `tests/unit/test_challenge_ai_usage_tracking.py`
   - `tests/unit/test_challenge_ai_safe_errors.py`
2. **Nouveau helper attendu**
   - `build_challenge_ai_stream_kwargs(*, model, system_content, user_content, ai_params) -> Dict[str, Any]`
   - emplacement : `challenge_ai_model_policy.py`
3. **Comportement a preserver strictement**
   - `response_format` absent pour `o1`
   - `max_completion_tokens` pour `o1`, `o3`, `gpt5`
   - `reasoning_effort` pour `o3` / `gpt5`
   - `verbosity` seulement pour `gpt5`
   - `temperature` seulement pour branche `gpt5` avec `reasoning_effort == "none"`
   - branche chat classique : `max_tokens` + `temperature`
   - log de diagnostic inchange dans son intention (`model`, `o1`, `o3`, `reasoning`)
4. **Hors scope explicite du lot**
   - ne pas remplacer `AIConfig.get_openai_params()`
   - ne pas deplacer `resolve_challenge_ai_model()`
   - ne pas toucher au fallback non-stream o3 vide
   - ne pas toucher au tracking tokens / metrics / circuit breaker
   - ne pas nettoyer les docstrings ou l'encoding de `challenge_ai_service.py` hors logique de dispatch
5. **Gate ciblee si reactive**
   - `pytest tests/unit/test_challenge_ia4_prompt_and_model_policy.py tests/unit/test_challenge_ai_usage_tracking.py tests/unit/test_challenge_ai_safe_errors.py tests/unit/test_challenge_ia5c_validation_hard_stop.py -q --tb=short --no-cov`
   - `black` / `isort` / `flake8` sur les fichiers touches

**Condition de GO future :**

- helper introduit sans changer le contrat OpenAI effectif
- `challenge_ai_service.py` ne porte plus de branchement inline famille/parms
- fallback o3 vide inchange
- tests de policy et de tracking verts

---

### CC1-L4 - CLAUDE.md cleanup (5 min)

**Fichier :** `CLAUDE.md`

Supprimer la ligne P1 challenge*service double filtrage : deja resolu
(`_apply_challenge_filters()` utilise `is_active.is*(True)`+`is*archived.is*(False)`).

```
| ~~P1~~ | ~~`app/services/challenges/challenge_service.py:353`~~ | ~~Double filtrage...~~ - **RESOLU** |
```

---

## 4. Findings hors scope

| Finding                                         | Raison                                                            |
| ----------------------------------------------- | ----------------------------------------------------------------- |
| `resolve_exercise_ai_model_for_user()` wrapper  | Extension future documentee + testee, pas du code mort accidentel |
| `DIFFICULTY_RANGES` dans exercise_ai_service.py | Utilise activement pour prompts                                   |
| `jedi_rank_for_level()` naming                  | F43-A3 migration contractuelle additive                           |
| `_LEGACY_PROGRESS_RANKS` dans compute.py        | Necessaire pour migration buckets legacy                          |

**Clarification importante :**

- `resolve_exercise_ai_model_for_user()` n'est **pas** un differe du plan ; il reste hors scope assume
- `DIFFICULTY_RANGES`, `jedi_rank_for_level()` et `_LEGACY_PROGRESS_RANKS` ne sont **pas** des nettoyages a programmer ici
- le rapport initial mentionnait plusieurs dettes legitimes ; `CC1-L3` a depuis ete traite et le plan CC1 est maintenant integralement consomme

---

## 5. Regles non negociables

1. **Lire avant d'ecrire** - verifier les lignes exactes avant modification.
2. **Un lot = un commit** atomique.
3. **Diff strictement borne** - aucun changement hors findings documentes.
4. **Gate tests verts** avant chaque commit.
5. **Pas de refactoring opportuniste** hors scope du rapport.

---

## 6. Ordre d'execution recommande dans Cursor

```text
1. CC1-L1 : lire les 5 fichiers -> appliquer les 5 corrections -> gate -> commit
2. CC1-L4 : CLAUDE.md -> commit rapide
3. CC1-L2 : aligner sse_utils (optionnel, independant) -> gate -> commit
4. CC1-L3 : extraire build_challenge_ai_stream_kwargs() -> gate -> commit
```

---

## 7. Dette documentee pour F43

| Item                                                        | Reference                              |
| ----------------------------------------------------------- | -------------------------------------- |
| Double systeme policy IA (ai_config + ai_generation_policy) | Architecture CLAUDE.md - dette assumee |

# Plan CC1 - Clean Code Pass post-F42/F43

**Date :** 2026-03-28
**Source :** rapport /octo:review working tree (Correctness + Architecture, AI-assisted)
**Execution :** Cursor Composer
**Validation :** `pytest -q --maxfail=20 --no-cov` + `black` + `isort` + `flake8` apres chaque lot

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
[TODO] CC1-L1 : Bugs P0 + code mort P1 (lot atomique, 5 fichiers)
[TODO] CC1-L2 : DRY P2 - exercise_ai_service aligne sur sse_utils (1 fichier)
[DIFF] CC1-L3 : DRY P2 - challenge dispatch extracted (effort > valeur court terme, differe)
[TODO] CC1-L4 : CLAUDE.md - supprimer P1 challenge_service deja resolu
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

### CC1-L3 - DRY : challenge dispatch model (differe)

**Contexte :** `challenge_ai_service.py:329-367` a sa propre logique de dispatch modele
(o1/o3/gpt5/fallback) inline dans `create_stream_with_retry()`. `ai_generation_policy.py`
a `build_exercise_ai_stream_kwargs()` qui fait la meme chose proprement.

**Recommandation :** creer `build_challenge_ai_stream_kwargs()` dans
`challenge_ai_model_policy.py` symetriquement a `build_exercise_ai_stream_kwargs()`.

**Decision :** differe - scope plus large (fallback o3 + alignement `AIConfig.get_openai_params()`).

---

### CC1-L4 - CLAUDE.md cleanup (5 min)

**Fichier :** `CLAUDE.md`

Supprimer la ligne P1 challenge_service double filtrage : deja resolu
(`_apply_challenge_filters()` utilise `is_active.is_(True)` + `is_archived.is_(False)`).

```
| ~~P1~~ | ~~`app/services/challenges/challenge_service.py:353`~~ | ~~Double filtrage...~~ - **RESOLU** |
```

---

## 4. Findings hors scope

| Finding | Raison |
|---------|--------|
| `resolve_exercise_ai_model_for_user()` wrapper | Extension future documentee + testee, pas du code mort accidentel |
| `DIFFICULTY_RANGES` dans exercise_ai_service.py | Utilise activement pour prompts |
| `jedi_rank_for_level()` naming | F43-A3 migration contractuelle additive |
| `_LEGACY_PROGRESS_RANKS` dans compute.py | Necessaire pour migration buckets legacy |
| CC1-L3 dispatch challenge DRY | Differe - scope plus large que l'utilite immediate |

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
```

---

## 7. Dette documentee pour F43

| Item | Reference |
|------|-----------|
| Dispatch modele defis DRY (CC1-L3) | Creer `build_challenge_ai_stream_kwargs()` dans `challenge_ai_model_policy.py` |
| Double systeme policy IA (ai_config + ai_generation_policy) | Architecture CLAUDE.md - dette assumee |

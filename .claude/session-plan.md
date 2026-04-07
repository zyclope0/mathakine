# Plan CC1 - Clean Code Pass post-F42/F43

**Date :** 2026-03-28
**Source :** rapport /octo:review working tree (Correctness + Architecture, AI-assisted)
**Execution :** Cursor Composer
**Validation :** `pytest -q --maxfail=20 --no-cov` + `black` + `isort` + `flake8` apres chaque lot

---

## Addendum Frontend Architecture - 2026-04-06

> Ce fichier garde l'historique du plan `CC1` backend.
> L'addendum ci-dessous devient la **source de verite d'execution frontend** pour
> l'industrialisation / standardisation architecture-first.

### 0. Perimetre actif

Objectif courant :

- **industrialiser** le frontend
- **standardiser** les patterns et contrats
- **eliminer la duplication residuelle**
- **sortir les monolithes runtime/pages**

Hors scope par defaut tant qu'ils ne bloquent pas l'architecture :

- retouches purement visuelles
- sweeps cosmetiques de tokens/couleurs
- nouvelles animations
- debates de theme / branding
- decisions produit sur la variabilite d'interaction des defis (`challenge_type` vs `response_mode`) tant qu'aucun lot dedie n'est ouvert

### 1. Sources de verite

1. `D:\\Mathakine\\.claude\\session-plan.md` = **plan actif**
2. `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md` = audit + feuille de route frontend a jour
3. `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` = photographie historique, utile pour le contexte mais **pas** comme plan d'execution ligne a ligne

En cas de divergence :

- suivre d'abord ce fichier
- puis realigner les 2 audits projet dans le meme lot documentaire

### 2. Verite terrain frontend au 2026-04-07

**Photographie tree**

- `174` fichiers composants sous `frontend/components`
- `52` hooks custom sous `frontend/hooks`
- `8` themes visibles
- boundary apprenant/adulte et roles canoniques deja stabilises

**Fondations deja livrees**

- `FFI-L1` a `FFI-L15` : livres cote architecture frontend ; push a confirmer selon l'etat Git courant
- roles canoniques + `NI-13` : livres et stabilises
- `AIGeneratorBase` existe et a retire le plus gros de la duplication brute
- `lib/validation/` est deja standardise (plus de split `validation/validations`)

**Seams architecture encore critiques**

- `frontend/components/profile/ProfileLearningPreferencesSection.tsx` ~`449` LOC
- `frontend/components/challenges/ChallengeSolverCommandBar.tsx` ~`446` LOC
- `frontend/components/layout/Header.tsx` ~`394` LOC
- recouvrement residuel `ChatbotFloating.tsx` / `ChatbotFloatingGlobal.tsx`

### 3. Ordre actif recommande

```text
1. FFI-L16 : split shell/navigation (Header + ownership chatbot flottant)
2. FFI-L17 : garde-fous architecture (tests, conventions, docs, contrats)
3. Ensuite : nouveaux seams shared ou domaines encore denses (si la revue structurelle les confirme)
4. Ensuite seulement : sweeps visuels secondaires (tokens/couleurs residuels)
```

### 3.1 Sidecar produit documente, hors sequence FFI

Point a ne pas perdre :

- **F44** - coherence interaction defis (`challenge_type` vs `response_mode`)

Verite terrain :

- le backend calcule `response_mode` apres policy type / difficulte / `choices` / `visual_data`
- un meme type visible peut donc encore render des interactions differentes (QCM, visuel, ordre, grille, texte libre)
- c'est **coherent machine**, mais **pas encore totalement coherent end-user**

Decision d'execution :

- **ne pas melanger ce sujet avec FFI-L11 a FFI-L17**
- le traiter comme **backlog produit / contrat** documente dans `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`
- ne l'ouvrir en implementation que lorsqu'un lot dedie clarifie la matrice cible par type

### 4. Definition concrete des lots actifs

#### FFI-L10 — Split `ChallengeSolver`

- but : appliquer au solver defi la discipline deja posee sur `ExerciseSolver`
- statut :
  - **livre**
  - helpers purs extraits dans `lib/challenges/challengeSolver.ts`
  - split `status / header / content / hints / feedback`
  - extraction `ChallengeSolverCommandBar.tsx`
  - extraction `useChallengeSolverController.ts`
- resultat :
  - `ChallengeSolver.tsx` ramene a un orchestrateur ~`188` LOC
  - `visualModel!` supprime
  - tests de non-regression solver/helpers/controller en place
- reliquat connu :
  - `ChallengeSolverCommandBar.tsx` reste un seam dense (~`446` LOC), mais le monolithe runtime critique est ferme

#### FFI-L11 — Modulariser `app/profile/page.tsx`

- but : sortir la plus grosse page UI du repo du mode "mega-page"
- statut :
  - **livre**
  - `app/profile/page.tsx` ramene a un container ~`191` LOC
  - extraction `useProfilePageController.ts`
  - extraction `lib/profile/profilePage.ts`
  - extraction des sections `components/profile/*`
  - tests reels en place : page profil + hook controller + helpers purs
- resultat :
  - le domaine profil est separe en couches lisibles (container / controller / sections / helpers)
  - la regression de validation mot de passe (`min 8`) a ete refermee apres refactor
  - la couverture hook n'est plus un faux positif base uniquement sur des helpers purs
- reliquat connu :
  - `ProfileLearningPreferencesSection.tsx` reste un sous-seam dense (~`449` LOC), mais la mega-page critique est fermee

#### FFI-L12 — Modulariser `app/badges/page.tsx`

- statut :
  - **livre**
  - `app/badges/page.tsx` ramene a un container ~`252` LOC
  - extraction `useBadgesPageController.ts`
  - extraction `lib/badges/badgesPage.ts`
  - extraction des sections `components/badges/*`
  - couverture reelle : page badges + hook controller + helpers purs
- resultat :
  - la mega-page badges n'est plus un seam runtime prioritaire
  - filtres, progression, stats, vitrines et collection sont maintenant separables et testables
  - la stabilite des tests page badges a ete reverrouillee
- reliquat connu :
  - `BadgesProgressTabsSection.tsx` reste une vue dense (~`250` LOC)
  - `BadgeCard.tsx` reste hors lot et demeure un candidat naturel pour une phase ulterieure

#### FFI-L13 — Modulariser `app/settings/page.tsx`

- statut :
  - **livre**
  - `app/settings/page.tsx` ramene a un container ~`133` LOC
  - extraction `useSettingsPageController.ts`
  - extraction `lib/settings/settingsPage.ts`
  - extraction des sections `components/settings/*`
  - couverture reelle : page settings + hook controller + helpers purs
- resultat :
  - la mega-page settings n'est plus un seam runtime prioritaire au niveau page
  - navigation sections, formulaires, sessions, diagnostic et donnees sont decouples en vues testables
- reliquat connu :
  - `SettingsSecuritySection.tsx` reste une vue dense (confidentialite + sessions actives sur une meme section), mais le container page n'est plus omnibus

#### FFI-L14 — Decouper `app/admin/content/page.tsx`

- statut :
  - **livre** cote industrialisation frontend (lots A + B + C)
- resultat :
  - `app/admin/content/page.tsx` container fin (~`50` LOC) + `useAdminContentPageController` + `lib/admin/content/adminContentPage.ts`
  - domaines dans `components/admin/content/*` (tabs shell, exercices, defis, badges)
  - liste exercices : affichage difficulte neutre transitoire (`Niveau 1..5` depuis legacy `difficulty`, `Palier n` si `difficulty_tier` present) — pas de vocabulaire Star Wars comme verite visible produit
  - audits / README / changelog / manifeste difficulte realignes (lot C)
- reliquat connu (hors echec du split frontend) :
  - **contrat / produit** : l'alignement final de la difficulte exercices admin sur `difficulty_tier` F42 n'est pas garanti tant que la **liste admin API** n'expose pas ce champ de facon systematique ; l'UI liste reste alors transitoire
  - **edition** : les modales exercices conservent les valeurs API legacy (`ADMIN_DIFFICULTIES`) pour compatibilite de persistance

#### FFI-L15 — Standardiser la plateforme content-list

- statut :
  - **livre**
- resultat :
  - extraction `useContentListPageController.ts` pour l'etat runtime partage des pages `Exercises` / `Challenges`
  - extraction `ContentListResultsHeader.tsx` + `ContentListResultsSection.tsx` pour la coquille visuelle shared des resultats
  - split interne de `ContentListProgressiveFilterToolbar.tsx` en sous-blocs (`SearchRow`, `TypeChips`, `Summary`, `AdvancedPanel`) avec facade publique stable
  - duplication page-specifique fortement reduite sans fusionner generators, cards ou modales domaine
- reliquat connu :
  - fermeture architecture faite ; une QA visuelle humaine reste utile avant cloture produit, mais aucun lot technique obligatoire ne reste sous le theme `FFI-L15`

#### FFI-L16 — Split shell/navigation

- but : reduire la dette de shell global
- scope :
  - `Header.tsx`
  - ownership de `ChatbotFloating.tsx` / `ChatbotFloatingGlobal.tsx`
  - clarifier ce qui appartient au shell, a la home, ou au domaine chatbot
- definition of done :
  - navigation desktop/mobile/menu utilisateur separes
  - plus de recouvrement fonctionnel entre floating chatbots

#### FFI-L17 — Garde-fous architecture

- but : verrouiller la derive
- cible :
  - conventions de taille composant/page
  - tests de non-regression structurels
  - documentation design system/runtime
  - regles d'ownership des helpers/constants
- definition of done :
  - docs actives alignees
  - nouveaux seams documentes avant de grossir
  - choix de patterns shared clairement explicités

### 5. Parent / roles / NI-13

Etat stable a ne pas rouvrir sans besoin produit explicite :

- roles actifs :
  - `apprenant`
  - `enseignant`
  - `moderateur`
  - `admin`
- `parent` reste documente comme **prochain ajout produit**, non implemente
- `/home-learner` reste la home principale apprenant
- `/dashboard` reste une surface secondaire discrete pour apprenant
- `proxy.ts` + `ProtectedRoute` + helpers de roles restent la base a reutiliser

Reference produit :

- `docs/02-FEATURES/PARENT_DASHBOARD_AND_CHILD_LINKS.md`

### 6. Gardes-fous d'execution

1. **Architecture avant apparence** : ne pas glisser un sweep visuel dans un lot FFI actif sans justification technique.
2. **Page/container fins** : toute page > ~700 LOC ou composant critique > ~400 LOC devient candidat explicite a extraction.
3. **Pas de duplication de contrat** : constantes, mappings, validation, labels derives ne doivent pas etre redefinis localement si une source centrale existe.
4. **Helpers de domaine > helpers anonymes inline** : preferer des helpers nommes ou hooks dedies quand une logique depasse quelques branches.
5. **Aucune reintroduction legacy** : pas de strings de roles legacy dans le code actif ; pas de retour a des contrats implicites.
6. **Docs frontend a realigner ensemble** pour toute evolution d'architecture :
   - `session-plan.md`
   - `AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`
   - `AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md`

### 7. Gate qualite minimale par lot frontend structurel

1. `cd frontend && npx tsc --noEmit`
2. `cd frontend && npm run lint`
3. `cd frontend && npx vitest run <tests touches>`
4. `cd frontend && npx prettier --check <fichiers touches>`
5. ajouter des tests de non-regression avant tout decoupage de monolithe critique

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

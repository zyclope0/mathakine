# Pilotage IA - Generation Exercices et Defis

> Date: 2026-03-21
> Type: diagnostic de reference + plan de refonte loti
> Portee: generation d'exercices et de defis pilotes par IA, cout, qualite, robustesse, gouvernance modele

> ⚠️ OBSOLÈTE — ce document reste le journal de pilotage et le ledger des lots IA, mais n'est plus la source de vérité runtime des modèles et de l'observabilité.
> Source de vérité actuelle : [../../../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../../../00-REFERENCE/AI_MODEL_GOVERNANCE.md).

---

## Statut consolide au 22/03/2026

Lots clos et verifies :

- IA10 / IA10b : gouvernance modele multi-workloads et assistant fail-closed
- IA11a / IA11b : campagne comparative offline puis live bornee
- IA12 : observabilite runtime et admin read-only IA
- IA13a / IA13b : architecture frontend IA (generation + chat)

Lots encore ouverts ou purement historiques :

- IA14 : cleanup de nomenclature / dead code
- les sections diagnostiques et ordres d'execution ci-dessous restent utiles comme historique de refonte, pas comme reference runtime actuelle

---

## Objet

Ce document fixe la verite projet pour le chantier "generation IA exercices / defis".

Il consolide:

- la cartographie runtime reelle
- les asymetries actuelles entre exercices et defis
- les decisions produit / architecture validees
- les risques connus
- le decoupage en lots a executer avec Cursor

La verite ultime reste le code dans `app/`, `server/` et `frontend/`.

---

## Resume executif

Le systeme actuel n'a pas une politique unifiee de generation IA.

Constat principal:

1. les exercices ont deux mondes distincts:
   - un generateur local non-LLM
   - un generateur IA OpenAI en SSE
2. les defis ont un pipeline IA plus robuste que les exercices, mais beaucoup plus lourd en prompt et donc potentiellement plus couteux
3. le runtime local utilise actuellement `o1` pour une partie des exercices IA, ce qui est trop cher pour la valeur rendue
4. la robustesse, l'observabilite et les validations metier sont asymetriques entre exercices et defis
5. les defis ne font pas "beaucoup d'appels IA" en nominal; le vrai cout vient surtout du volume de prompt, des retries et des fallbacks

Conclusion de pilotage:

- generation simple: garder un moteur local, le challenger et le renforcer
- generation IA pilotee par utilisateur: converger vers `o3`
- defis: garder `o3` a court terme, mais reduire les tokens, renforcer la validation et mieux piloter la difficulte
- evaluation: introduire un harness de benchmark qualite / cout / validite avant d'ouvrir davantage la generation IA

---

## Cartographie runtime validee

## Exercices

### Flux standard non-LLM

- frontend: `frontend/components/exercises/UnifiedExerciseGenerator.tsx`
- hook: `frontend/hooks/useExercises.ts`
- handler: `server/handlers/exercise_handlers.py`
- service applicatif: `app/services/exercises/exercise_generation_service.py`
- generateur local: `app/generators/exercise_generator.py`
- politique locale titres / formulations (lot **IA3**, qualite generateur simple) : `app/generators/exercise_generation_policy.py`
- plages numeriques par niveau derive de l'age : `DIFFICULTY_LIMITS` dans `app/core/constants.py` (source de verite inchangee)

Ce flux n'appelle pas OpenAI par defaut.

Point important:

- le nom `generate_ai_exercise()` dans `app/generators/exercise_generator.py` est trompeur
- il s'agit d'un generateur local Python, pas d'un appel modele externe

### Flux IA OpenAI

- frontend: `frontend/hooks/useAIExerciseGenerator.ts`
- endpoint SSE: `POST /api/exercises/generate-ai-stream` (corps JSON typÃ©, plus de prompt dans lâ€™URL)
- service: `app/services/exercises/exercise_ai_service.py`

Ce flux est active quand l'utilisateur choisit explicitement le mode IA.

## Defis

### Flux IA OpenAI

- frontend: `frontend/components/challenges/AIGenerator.tsx`
- endpoint SSE: `POST /api/challenges/generate-ai-stream` (corps JSON typÃ©, plus de prompt dans lâ€™URL)
- service de preparation: `app/services/challenges/challenge_stream_service.py`
- service IA: `app/services/challenges/challenge_ai_service.py`

Le nominal correspond a une requete frontend SSE et a un appel modele cote backend.

Le nombre d'appels modele peut augmenter uniquement en cas de:

- retry transitoire API
- fallback si reponse vide

---

## Etat runtime des modeles

> ⚠️ OBSOLÈTE — cette section contient un mélange de constats historiques pre/post-refactor.
> Pour les défauts de modèles, allowlists, hiérarchies d'override et limites assumées au 22/03/2026, utiliser [../../../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../../../00-REFERENCE/AI_MODEL_GOVERNANCE.md).

## Configuration locale constatee

Dans `D:\Mathakine\.env`:

- `OPENAI_MODEL=o1`
- `OPENAI_MODEL_REASONING=o3`

Dans `D:\Mathakine\.env.example` (apres lot IA1b) :

- `OPENAI_MODEL=gpt-4o-mini`
- `OPENAI_MODEL_EXERCISES_OVERRIDE` (optionnel, override ops exercices IA)
- `OPENAI_MODEL_EXERCISES` (legacy, si override vide)
- `OPENAI_MODEL_CHALLENGES_OVERRIDE` (optionnel, prioritaire sur la ligne suivante)
- `OPENAI_MODEL_REASONING=o3` (legacy : override global defis si override defis vide)

## Consequence reelle

### Exercices IA

**Comportement actuel (lot IA1b â€” policy applicative + matrice)** :

- Source de verite **defaut** : `DEFAULT_EXERCISES_AI_MODEL` (`o3`) dans `app/core/ai_generation_policy.py`.
- Resolution : `OPENAI_MODEL_EXERCISES_OVERRIDE` > `OPENAI_MODEL_EXERCISES` (legacy) > defaut applicatif `o3`.
- **Pas** d'utilisation de `OPENAI_MODEL` ni `OPENAI_MODEL_REASONING` pour choisir le modele exercices IA (evite le retour implicite vers `o1`).
- Allowlist explicite : `EXERCISES_AI_ALLOWED_MODEL_IDS` dans `ai_generation_policy.py` â€” typo ou ID inconnu -> erreur avant appel OpenAI (lot IA1c).
- `o1` / `o1-mini` : **option explicite** uniquement via override env ; jamais defaut.
- Parametres d'appel : `build_exercise_ai_stream_kwargs()` selon la **famille** de modele (o1 / o3 / gpt-5.x / chat classique) et la matrice `MODEL_FAMILY_CAPABILITIES`.
- Futur : `resolve_exercise_ai_model_for_user()` delÃ¨gue aujourd'hui au resolver global (abonnement plus tard).

**Historique (avant IA1)** : types Â« simples Â» utilisaient `OPENAI_MODEL` (souvent `o1` en local), types raisonnement `OPENAI_MODEL_REASONING` (`o3`).

### Defis IA

**Comportement actuel (lot IA4)** :

- Source de verite **defaut** : `DEFAULT_CHALLENGES_AI_MODEL` (`o3`) dans `app/services/challenges/challenge_ai_model_policy.py`.
- Resolution : `OPENAI_MODEL_CHALLENGES_OVERRIDE` > `OPENAI_MODEL_REASONING` (legacy) > `CHALLENGE_MODEL_BY_TYPE` (nominal : `o3` pour chaque type) > defaut `o3`.
- `AIConfig.get_model()` delegue a `resolve_challenge_ai_model()`.
- Allowlist : memes IDs que `EXERCISES_AI_ALLOWED_MODEL_IDS` (`ai_generation_policy.py`) â€” erreur avant appel si ID inconnu.
- Prompt : composition modulaire (`challenge_prompt_composition.py`, `challenge_prompt_sections.py`) â€” contrat `visual_data` + validations **par type** uniquement.
- Fallback stream vide (o3/o3-mini uniquement) : `resolve_challenge_ai_fallback_model()` â€” `OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE` > dÃ©faut `gpt-4o-mini` (allowlist), indÃ©pendant de l'override du modÃ¨le principal sauf que la branche ne s'exÃ©cute que pour une famille o3 vide.

---

## Diagnostic cout

## Exercices

- le flux standard ne coute pas de tokens OpenAI
- le flux IA ne devrait pas utiliser `o1` sur les types simples
- le cout actuel des exercices IA simples est donc inutilement eleve

## Defis

Le cout principal des defis vient de la taille du prompt.

Mesure locale indicative:

- **Avant IA4** â€” prompt defis monolithique : environ 23690 caracteres (~5920 tokens).
- **Apres IA4** â€” meme fonction `build_challenge_system_prompt` mais corps compose : typiquement ~4500â€“7500 caracteres selon le type (ex. `sequence` le plus leger, `coding`/`visual` plus fournis), soit ~40â€“70 % de reduction vs monolithique ; detail : `challenge_system_prompt_stats(type, age_group)`.
- `build_exercise_system_prompt(...)`: environ 2855 caracteres, soit environ 714 tokens

Conclusion:

- le probleme principal des defis n'est pas un fan-out d'appels
- le probleme principal est le volume de tokens par appel

Risques additionnels cote defis:

- retries API
- fallback vers un autre modÃ¨le si `o3`/`o3-mini` rÃ©pond vide (policy : `resolve_challenge_ai_fallback_model`, dÃ©faut `gpt-4o-mini`, override `OPENAI_MODEL_CHALLENGES_FALLBACK_OVERRIDE`)

---

## Diagnostic qualite / robustesse

> ⚠️ OBSOLÈTE — plusieurs faiblesses mentionnées dans cette section ont été fermées par IA10b, IA12, IA13a/b et les correctifs du 22/03/2026.
> Conserver cette section comme historique d'audit ; ne pas l'utiliser seule pour juger l'état runtime actuel.

## Exercices IA

Forces:

- domaine plus borne
- prompt plus court
- activation explicite par l'utilisateur

Faiblesses (mises a jour lot **IA2**, 2026-03-06) :

- pas de retry
- pas de fallback
- ~~pas de rate limit~~ : **rate limit dedie** utilisateur (`check_exercise_ai_generation_rate_limit`, cles Redis `rate_limit:exercise_ai_generation:*`, quotas distincts des defis)
- ~~pas de tracking cout/tokens~~ : **token_tracker** apres appel stream (`exercise_ai:{type}`), `stream_options.include_usage` dans `build_exercise_ai_stream_kwargs`
- ~~pas de generation metrics~~ : **generation_metrics** (succes / echec / `validation_passed` / duree / `error_type`, sans auto-correction fictive)
- ~~pas de validation metier forte post-generation~~ : **validate_exercise_ai_output** â€” echec => pas de persistance, erreur SSE explicite

Verdict:

- le pipeline exercices IA reste sans retry/fallback, mais la gouvernance cout/qualite/limites est alignee sur lâ€™intention produit (lot IA2)

## Defis IA

Forces:

- rate limiting
- retry sur erreurs transitoires
- fallback si reponse vide
- validation logique
- auto-correction locale
- token tracking
- generation metrics

Faiblesses:

- ~~prompt monolithique trop gros~~ (lot **IA4** : composition modulaire par type ; reste du raffinement qualite/cout possible)
- observabilite en memoire uniquement
- tracker cout incomplet pour les modeles GPT-5
- validation inegale selon les types

Point critique (mis a jour lot **IA5**) :

- ~~`DEDUCTION` sans validateur dedie~~ : `validate_deduction_challenge` branche dans `_VALIDATORS_BY_TYPE` (contrat structurel, pas preuve d'unicite logique).

Verdict:

- le pipeline defis est mieux industrialise que celui des exercices
- mais il reste trop couteux par prompt et incomplet sur certains garde-fous

---

## Etat des tests

Les chemins IA n'ont pas une couverture de service a la hauteur du cout qu'ils induisent.

Constats:

- il existe des tests d'endpoints et de composants annexes
- il existe des tests admin sur `ai-stats` et `generation-metrics`
- mais il manque une couverture forte et directe sur:
  - `exercise_ai_service`
  - `challenge_ai_service`
  - la validation metier post-generation
  - la coherence difficult / distracteurs

Conclusion:

- avant d'etendre la generation IA, il faut augmenter la preuve automatisee

---

## Appui academique et bonnes pratiques retenues

Ces points doivent guider la refonte:

1. le raisonnement explicite aide les taches symboliques et arithmetiques, mais ne suffit pas a garantir l'exactitude
2. la self-consistency peut ameliorer la qualite, mais augmente le cout et ne doit pas devenir le mode live par defaut
3. pour les taches mathematiques, le calcul et la verification doivent etre externalises dans du code
4. en generation d'items educatifs, la qualite apparente ne garantit pas l'adequation pedagogique; il faut des validateurs metier et un benchmark cible

References de travail:

- Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
- Wang et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models"
- Chen et al., "Program of Thoughts Prompting"
- Ma et al., "Automatic Generation of Inference Making Questions for Reading Comprehension Assessments"
- documentation OpenAI modele / pricing / reasoning

---

## Decisions validees

Ces decisions sont actees pour les prochains lots.

1. remplacer `o1` par `o3` pour la generation IA des exercices
2. conserver deux mondes pour les exercices:
   - generation simple locale
   - generation IA pilotee par utilisateur
3. renforcer l'instrumentation cout / qualite / validation des exercices IA
4. ajouter une validation metier forte post-generation pour les exercices IA
5. decouper le prompt monolithique des defis par type / famille
6. clarifier la politique modele des defis et supprimer les ambiguities d'override
7. ~~ajouter un validateur dedie pour `DEDUCTION`~~ (fait lot **IA5**)
8. faire evoluer les endpoints IA vers `POST` avec payload JSON et streaming reponse
9. introduire un harness d'evaluation qualite / cout / validite
10. differer la persistance durable des metriques a un lot ulterieur
11. renommer le faux `generate_ai_exercise()` local pour eliminer l'ambiguite architecturale
12. augmenter la variete des titres du generateur simple d'exercices
13. renforcer la gestion de la difficulte et la coherence des distracteurs dans les defis, avec possible granularite plus fine

---

## Principes de refonte

## Separation des mondes

### Generation simple

- pas de LLM
- robuste
- faible cout
- plus grande maitrise pedagogique

### Generation IA pilotee

- reservee a une demande explicite
- mode premium en cout cognitif et runtime
- davantage de validation et de gouvernance

## Politique modele

Index gouvernance multi-workloads (lot **IA10**, mars 2026) : `app/core/app_model_policy.py` â€” assistant_chat, delegation explicite vers exercices (`ai_generation_policy`) et defis (`challenge_ai_model_policy`). La verite produit est dans le code type ; les `.env` ne font qu'overrides ops / legacy bornes.

### Assistant (MaÃ®tre Kine / chat)

- defaut produit : `gpt-5-mini`
- palier premium (stub seam) : `gpt-5.4`
- fallback cheap documente : `gpt-4o-mini` (policy, pas le defaut nominal)
- pas de `gpt-3.5-turbo` comme cible implicite
- **IA10b (fail-closed)** : allowlist assistant = `gpt-5-mini`, `gpt-5.4`, `gpt-4o-mini`, `gpt-4o` uniquement (runtime Chat Completions actuel). **Pas** d'`o1` / `o3` sur lâ€™assistant ; ces familles restent sur exercises / defis.

### Exercices

- sortie de `o1`
- convergence vers `o3`
- `reasoning_effort` pilote par type

### Defis

- `o3` conserve a court terme
- optimisation d'abord par reduction de prompt et validation
- re-challenge modele seulement apres instrumentation et benchmark

## Verification algorithmique

- ne jamais faire confiance a la seule explication du modele
- recalculer / verifier ce qui peut l'etre en code

## Evaluation

- decision produit / modele / prompt uniquement apres benchmark sur corpus fige

---

## Lots proposes

> ⚠️ OBSOLÈTE — cette section est un plan historique.
> Les lots IA10b, IA11a, IA11b, IA12, IA13a et IA13b sont désormais réalisés.
> Les décisions runtime en vigueur sont consolidées dans [../../../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../../../00-REFERENCE/AI_MODEL_GOVERNANCE.md).

Les lots doivent etre traites separement, avec review systematique.

## IA1 - Exercices IA: alignement `o1` -> `o3`

Objectif:

- supprimer `o1` du flux exercices IA
- adapter `exercise_ai_service` a une politique `o3`
- regler `reasoning_effort` par type

Inclus:

- config runtime
- service exercices IA
- revue des parametres OpenAI
- tests causaux

## IA2 - Exercices IA: instrumentation et validation forte

Objectif:

- ajouter rate limit
- ajouter token tracking
- ajouter generation metrics
- ajouter validation metier post-generation

Inclus:

- coherence `correct_answer`
- coherence `choices`
- coherence `explanation`
- validations dediees fractions / texte / mixte / divers

## IA3 - Exercices simples: qualite du generateur local

Objectif:

- challenger le generateur simple
- verifier adaptation a la difficulte
- verifier robustesse algorithmique
- enrichir la variete des titres

Inclus:

- audit difficulte
- audit choix de reponse
- audit scenarios
- renommer le faux seam `generate_ai_exercise()`

## IA4 - Defis IA: decoupage prompts et politique modele

Objectif:

- casser le prompt monolithique
- specialiser les prompts par type / famille
- clarifier la politique modele

Inclus:

- sequence / pattern / visual / deduction / puzzle / graph / coding / chess / probability
- revue du rapport tokens / valeur

## IA5 - Defis IA: difficulte, distracteurs, validation

Statut : **implÃ©mente** (policy `challenge_difficulty_policy`, QCM `challenge_answer_quality`, validateur `DEDUCTION`, garde-fous dans `validate_challenge_logic`, prompt JSON `choices` / `difficulty_axes`, mÃ©tadonnÃ©es `difficulty_calibration` dans `generation_parameters`).

Objectif (rappel) :

- mieux calibrer la difficulte (caps structure + titre / coherence avec rating IA)
- granularite explicite via signaux + axes optionnels cote prompt
- choix (distracteurs) valides si `choices` fourni
- validateur `DEDUCTION` structurel

## IA6 - Endpoints IA et boundaries

Objectif:

- basculer de `GET` SSE vers `POST` + body JSON + streaming reponse
- reduire les limites / risques lies aux prompts en URL

## IA7 - Harness d'evaluation

Objectif:

- corpus de prompts fige
- benchmark cout / latence / validite / adequation pedagogique
- comparaison entre:
  - generation simple
  - exercices IA
  - defis IA

## IA8 - Metriques persistantes

Objectif:

- sortir des structures en memoire
- historiser les couts et les echantillons de qualite

Statut:

- valide, mais non prioritaire a court terme

## IA10 - Gouvernance modeles globale (assistant + exercices + defis)

Objectif:

- une seule lecture defendable des workloads `assistant_chat`, `exercises_ai`, `challenges_ai`
- defauts produit explicites dans la configuration type (`app_model_policy` + modules delegues)
- `.env` limite aux overrides ops et legacy documente, sans devenir la source principale

Inclus:

- `app/core/app_model_policy.py`
- branchement `chat_service.build_chat_config` sur la policy assistant
- consolidation documentation `.env.example` / `ENV_CHECK.md`
- tests causaux (priorites override, anti-legacy implicite)

Hors scope:

- prompts, contrats defis, harness, UI chat

Statut:

- realise (mars 2026) â€” exercices / defis restent sur `o3` par defaut jusqu'a preuve harness

### IA10b - Assistant chat fail-closed (alignement runtime)

Objectif:

- allowlist `assistant_chat` restreinte aux modeles **reellement supportes** par le runtime chat (pas d'extension o1/o3 cote assistant)
- `.env.example` sans activation par defaut de `OPENAI_MODEL_REASONING` (legacy defis seulement ; nominal = policy code)

Statut:

- realise (mars 2026)

### Audit post-refactor (2026-03-22)

Constats restants apres IA10b :

- le monitoring admin IA doit raisonner par **workload** (`assistant_chat`, `exercises_ai`, `challenges_ai`) et non plus seulement par "type de defi"
- les trackers runtime historiques (`token_tracker`, `generation_metrics`) restent nomenclaturalement centres sur `challenge_type`, alors qu'ils servent maintenant plusieurs workloads
- le **chatbot** doit etre observe comme un workload IA a part entiere (latence, erreurs, tokens/cout) ; le suivi DALL-E reste hors scope actuel
- la persistance du harness IA existe en base (IA8), mais n'est pas encore exposee dans l'admin read-only
- le faux seam local `generate_ai_exercise()` reste toujours mal nomme et continue d'entretenir la confusion entre generation locale et generation LLM
- le frontend IA reste heterogene :
  - chat : parser SSE bespoke (`frontend/lib/api/chat.ts`)
  - exercices : hook SSE avec logique d'orchestration locale
  - defis : dispatcher SSE dedie + helper partage
- les trackers runtime en memoire (token_tracker, generation_metrics) n'ont toujours pas de politique de retention / eviction ; risque de croissance memoire non bornee en process long-vivant
- classify_ai_workload_key() reste historiquement permissif : toute cle runtime non prefixee et non vide finit dans challenges_ai ; cela doit etre rendu explicite et surveille pour ne pas fausser l'admin si un nouveau workload apparait
- le chatbot public existe sur la home ; l'absence d'auth sur /api/chat n'est donc pas automatiquement un bug, mais cela doit devenir une decision de gouvernance explicite (public rate-limite vs authentifie vs mode hybride)
- le tracker cout runtime reste incomplet pour certaines references GPT-5.x ; ne pas prendre les dollars admin comme source comptable sans mise a jour explicite contre la doc OpenAI du moment

### IA11 - Evaluation comparative reelle

Decoupage:

- **IA11a (offline only, mars 2026)** : protocole + matrice + outillage comparatif **sans** appel OpenAI. Commande : `python -m app.evaluation.comparative_campaign --campaign ia11a_offline_default`. Doc : `docs/03-PROJECT/evaluation/IA11A_COMPARATIVE_CAMPAIGN_OFFLINE.md`. Matrice : `tests/fixtures/ai_eval/campaigns/ia11a_offline_default.json`. Pas de score global opaque ; variantes live declarees `planned_not_executed`.
- **IA11b (mars 2026, prolonge IA11a)** : meme protocole comparatif ; segments offline = matrice IA11a ; live borne liste dans `tests/fixtures/ai_eval/campaigns/ia11b_live_bounded.json`. Commande : `python -m app.evaluation.comparative_campaign --ia11b-bounded-live --live --ia11b-campaign ia11b_live_bounded`. Doc : `docs/03-PROJECT/evaluation/IA11B_BOUNDED_LIVE_CAMPAIGN.md`. Pas de changement des defaults produit ; recommandation documentaire uniquement.

Objectif global (apres IA11a + IA11b):

- exploiter le harness IA7/IA8 pour arbitrer modeles et pipelines sur corpus fige
- comparer `o3` vs alternatives **quand** le live aura ete valide humainement

Inclus (cible finale):

- campagnes offline (IA11a) puis live bornees (IA11b)
- lecture comparative des runs persistes
- recommandation produit explicite par workload (hors score unique)

### IA12 - Admin read-only IA et observabilite runtime

Objectif:

- aligner l'admin /admin/ai-monitoring sur les workloads reels
- exposer les nouveaux points suivis du refactor (chat, workload split, erreurs runtime, runs harness)
- garder une page read-only de pilotage, sans UI d'edition

Inclus:

- cout / tokens par workload et par modele
- succes / validation / auto-correction / erreurs par workload
- surface read-only des runs persistés du harness IA8
- clarification documentaire des limites (runtime en memoire vs evaluation persistee)
- politique de retention / eviction ou rollup pour token_tracker et generation_metrics afin de supprimer la croissance memoire non bornee
- gestion explicite des cles runtime inconnues (warning, bucket unknown ou regle documentee), au lieu d'un classement silencieux trompeur
- decision explicite sur la politique d'acces du chatbot:
  - **retenu produit** : public avec rate limiting ; pas d'auth sur `/api/chat` dans ce lot
  - authentifie / hybride : hors scope IA12

Statut:

- realise (mars 2026) : rétention in-memory bornée (`token_tracker`, `generation_metrics`), bucket `unknown` pour clés non reconnues, `GET /api/admin/ai-eval-harness-runs`, page admin avec disclaimers (coûts estimatifs, chat public), doc API mise à jour.

### IA13 - Frontend architecture (flux IA)

Objectif:

- unifier l'orchestration frontend des flux IA (`chat`, `exercises_ai`, `challenges_ai`)
- reduire la duplication SSE et la derive des state machines locales

Inclus:

- seam partage pour flux POST + SSE
- dispatch / parsing / erreurs homogenes
- clarification hooks vs composants vs clients API

**IA13a (mars 2026)** — widgets génération exercice / défi uniquement (hors chat, voir IA13b) :

- couche commune : `frontend/lib/ai/generation/` (`postAiGenerationSse`, dispatch SSE, `normalizeCreatedResourceId`) ; doc `frontend/lib/ai/generation/README.md`
- hooks : `useAIExerciseGenerator`, `useAIChallengeGenerator`
- CTA « Voir l’exercice / le défi » : uniquement si `id` persisté (évite bannière verte sans lien quand le backend envoie un challenge non sauvegardé)

### IA14 - Dead code et cleanup de nomenclature

Objectif:

- supprimer ou renommer les seams trompeurs herites du refactor
- eliminer le code mort / stubs dormants non justifies
- rendre les noms coherents avec les workloads reels

Inclus:

- renommer le generateur local generate_ai_exercise()
- challenger les stubs non branches / helpers non consommes
- aligner la terminologie challenge_type -> metric_key / workload quand le scope n'est plus defis-only
- nettoyer les seams futurs non branches si le produit ne les active pas (resolve_assistant_chat_model_for_user, fallback cheap assistant, etc.)

---

## Ordre recommande

> ⚠️ OBSOLÈTE — ordre de passage historique du chantier.
> L'ordre de travail restant doit désormais être piloté depuis les documents projet actifs et non depuis cette séquence initiale.

1. IA1
2. IA2
3. IA3
4. IA4
5. IA5
6. IA6
7. IA7
8. IA8
9. IA10 (gouvernance modeles ; peut suivre la stabilisation des policies IA4 / exercices)
10. IA11
11. IA12
12. IA13
13. IA14

Raison:

- corriger d'abord le surcout evident
- renforcer ensuite la fiabilite
- puis piloter la comparaison reelle
- puis aligner l'observabilite read-only
- puis nettoyer l'architecture frontend et les seams morts

---

## Regles de pilotage pour Cursor

Pour chaque lot:

1. perimetre strict
2. pas de lot mixte
3. checks causaux explicites
4. compte-rendu obligatoire avec ce qui est prouve et ce qui ne l'est pas
5. pas de GO si le lot remplace une faiblesse structurelle par un simple changement cosmetique

Pour ce chantier en particulier:

- le code local reste la verite ultime
- les changements de modele ne doivent jamais etre presentes comme une solution suffisante
- tout lot IA doit expliciter:
  - impact cout
  - impact qualite
  - impact latence
  - impact pedagogique

---

## Point de vigilance central

Le risque principal n'est pas uniquement le cout.

Le vrai risque produit est de produire:

- un contenu apparemment bon
- mais pedagogiquement mal cible
- logiquement incoherent
- ou trop facile / trop dur pour le public vise

La refonte doit donc viser un systeme:

- moins cher
- plus observable
- plus testable
- plus pedagogiquement defensable

---

## Cloture hardening SSE et resilience (2026-03-22)

Point ferme apres revue stricte:

- les flux SSE exercices / defis n'exposent plus de `str(exception)` brut vers le frontend
- le flux exercices aligne maintenant un `timeout` explicite et un retry borne sur les erreurs OpenAI transitoires

Ce que cela garantit:

- pas de detail technique brut remonte a l'utilisateur final
- meilleur comportement sous rate limit / timeout OpenAI cote exercices
- parite de resilience plus defendable entre exercices et defis

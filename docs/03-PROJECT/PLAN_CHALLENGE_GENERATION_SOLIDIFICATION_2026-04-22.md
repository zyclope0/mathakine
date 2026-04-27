# Plan de solidification - Generation des defis IA
**Date :** 2026-04-22
**Revision :** 2026-04-27
**Contexte :** Post-lot beta.3, puis correctifs successifs de solidification sur la generation, la validation et les contrats backend/frontend
**Contrainte :** Sans refonte totale, solo founder, 1-3 mois

**Note de revision :** Ce plan est relu apres la migration `o3 -> o4-mini`, le durcissement du flux SSE defis, plusieurs correctifs du solveur deduction, l'alignement puzzle backend/frontend sur des cles d'ordre stables, les lots Phase 1A/1B/2A/2B d'observabilite runtime, puis les tests Phase 3A/3B/3D.

---

## Origine

Debat structure 4 IA (Claude + Gemini + OpenCode + Codex) conduit apres la revue
du lot `fix(challenges)` origin/master..HEAD.

Depuis cette revue, une partie importante des correctifs immediats a effectivement
atterri dans le code :
- migration par defaut `o3 -> o4-mini` sur exercices et defis
- `stream_options.include_usage` sur les defis
- `auto_correct_challenge()` passe en deep copy
- persistance du `difficulty_tier` runtime
- suppression du double passage generique d'auto-correction
- flush du tracking tokens sur erreur fallback
- fallback o-series vide traite comme echec explicite, sans faux `record_success()` et avec liberation du circuit breaker half-open
- solveur deduction etendu (same-row naturel, ordering cross-secondary, negations directionnelles)
- validation puzzle alignee sur des cles stables `id` / `piece_id`
- statuts pipeline runtime (`accepted`, `repaired`, `repaired_by_ai`, `rejected`)
- codes d'erreur de validation stabilises et agreges en metriques runtime

Le plan doit donc maintenant distinguer clairement :
- ce qui est deja fait
- ce qui reste partiellement fait
- ce qui n'est pas encore commence

---

## Consensus du debat

> Les 4000 lignes de regles actuelles peuvent tenir si et seulement si elles sont
> mesurees, testees et echouent proprement. Sans instrumentation, chaque commit est un pari.

Points unanimes :
- Observabilite avant nouvelles regles
- Repair chess a conserver + metriques de declenchement
- `max_retries=1` chess + fallback propre = bon compromis solo founder
- Solveur deduction justifie mais necessite timeout + tests de perf

---

## Etat reel au 2026-04-27

### Deja fait

- **Phase 0 modele OpenAI** : realisee.
  Le defaut exercices + defis est maintenant `o4-mini`, l'allowlist inclut aussi
  `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, et les kwargs stream exposent
  `stream_options.include_usage`.
- **Hardening du flux defis** :
  fallback o-series mieux borne, tracking d'usage conserve meme si le fallback
  echoue, une seule passe generique d'auto-correction, persistance coherente
  du `difficulty_tier`. Le cas fallback sans contenu est maintenant un echec
  explicite `fallback_empty_response` et libere le circuit breaker si l'appel
  etait une sonde `HALF_OPEN`.
- **Phase 1A observabilite pipeline** : realisee.
  Les generations de defis portent un `generation_status` runtime :
  `accepted`, `repaired`, `repaired_by_ai` ou `rejected`. Ces statuts sont
  exposes dans `generation_metrics.get_summary()` via `generation_status_counts`
  global et par type.
- **Phase 1B codes d'erreur structures** : realisee.
  Les erreurs de validation sont mappees vers des codes stables dans
  `challenge_validation_error_codes.py`, en observabilite seulement. Les codes
  sont dedupliques, comptes dans `error_code_counts`, et loggues au niveau
  orchestration avec le statut pipeline et le type de repair.
- **Phase 2A metriques runtime** : realisee.
  `generation_metrics` expose latence p50/p95, compteurs chess repair,
  fallback stats, fallback causes et `repair_success_rate`.
- **Phase 2B generation_confidence** : realisee en log-only.
  Le score est calcule/journalise cote orchestration, sans migration DB.
- **Phase 3A golden tests** : realisee.
  Les fixtures regression par type valident payload, erreurs attendues et
  `response_mode` effectif.
- **Phase 3B contrats renderer/frontend** : realisee.
  Les formes `visual_data` attendues par les renderers sont couvertes par tests.
- **Phase 3D perf solveur deduction** : realisee.
  Les garde-fous de combinatoire et timeout solveur sont couverts.
- **Contrats backend/frontend** :
  la validation puzzle s'aligne desormais sur des cles d'ordre stables
  (`id` / `piece_id`) tout en conservant les labels visibles pour les explications.
- **Solveur deduction** :
  support etendu pour `same color/activity/group`, ordering structure sur refs
  secondaires, et parsing negatif directionnel `pas immediatement avant / apres`
  sans faux positif sur les formulations bilaterales non negatives.

### Partiellement fait

- **Solidification validator/solver** :
  plusieurs gaps critiques ont ete fermes et les filets de regression Phase 3A/3B/3D
  existent. Le shadow mode Phase 3C reste a faire avant de durcir de nouvelles regles.

### Pas fait

- **Structured Outputs stricts OpenAI (`json_schema`)** :
  les defis utilisent encore `response_format={"type": "json_object"}` ;
  aucune migration globale vers `json_schema` strict n'est faite a ce stade.
- **Shadow mode Phase 3C** :
  pas encore de mode shadow pour tester de nouvelles regles bloquantes sur un
  echantillon avant activation stricte.
- **Architecture legere Phase 4** :
  pas encore de `ValidatorResult` type ni de dispatch generique des repair handlers.

---

## Plan d'action par phase

### Phase 0 - Decision modele IA OpenAI (realisee)

#### Verite terrain

Le code Mathakine utilisait **o3** comme defaut reel pour les deux workloads pedagogiques :

| Workload | Defaut avant decision | Allowlist avant decision | Manque bloquant |
|----------|-----------------------|--------------------------|-----------------|
| Exercices IA | `o3` | `o1`, `o1-mini`, `o3`, `o3-mini`, `gpt-5*`, `gpt-4o*` | `o4-mini`, `gpt-4.1*` |
| Defis IA | `o3` pour tous les types | heritee des exercices | `o4-mini`, `gpt-4.1*` |
| Fallback defis | `gpt-4o-mini` | deja compatible | aucun |

Source prix a reverifier avant chaque changement majeur : page officielle OpenAI pricing. Au
2026-04-22, `o3` est liste a $2.00 input / $8.00 output par 1M tokens, tandis que
`o4-mini` est liste a $1.10 input / $4.40 output par 1M tokens.

#### Decision retenue

**Basculer le defaut exercices + defis de `o3` vers `o4-mini`.**

Raison :
- Le coeur produit est la generation fiable d'exercices et de defis ; il faut conserver un modele reasoning, pas descendre immediatement vers une famille chat classique.
- `o4-mini` garde les proprietes necessaires au pipeline actuel : structured JSON, streaming, `reasoning_effort`, couts reasoning trackables.
- Le cout attendu baisse d'environ 45 % par generation par rapport au defaut `o3`, sans integrer un nouveau provider ni modifier le flux SSE.
- La migration reste OpenAI-only, donc compatible avec l'architecture actuelle : allowlist, token tracking, circuit breaker, retry, fallback et tests existants.

#### Changements techniques associes

1. Ajouter `o4-mini` a `EXERCISES_AI_ALLOWED_MODEL_IDS`.
2. Classer `o4-mini` dans la famille reasoning o-series, avec les memes kwargs que `o3`
   (`response_format=json_object`, `max_completion_tokens`, `reasoning_effort`).
3. Passer `DEFAULT_EXERCISES_AI_MODEL` a `o4-mini`.
4. Passer `DEFAULT_CHALLENGES_AI_MODEL` et `CHALLENGE_MODEL_BY_TYPE` a `o4-mini`.
5. Garder `gpt-4o-mini` comme fallback de stream vide pour les defis.
6. Ajouter `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano` a l'allowlist uniquement comme overrides
   d'experimentation ; ne pas les router par defaut tant que les metriques Phase 2A ne sont pas actives.
7. Verifier le deploiement : si `OPENAI_MODEL_REASONING=o3` existe encore, il garde la priorite legacy
   sur la policy defis. Le corriger en le vidant ou en posant explicitement
   `OPENAI_MODEL_CHALLENGES_OVERRIDE=o4-mini`.

#### Decisions explicitement rejetees maintenant

- Pas d'integration Gemini/DeepSeek avant metriques qualite. Le gain cout est reel, mais necessite
  un provider complet : SDK, auth, JSON mode, streaming, token tracking, retry, circuit breaker,
  observabilite et tests contractuels.
- Pas de routage par type vers `gpt-4.1-mini` avant mesure. C'est potentiellement utile pour
  `riddle`, `puzzle` ou `sequence` simples, mais cette famille ne supporte pas `reasoning_effort`
  et peut degrader la coherence logique sans telemetrie.
- Pas de `gpt-5.4` par defaut. A reserver plus tard a un mode premium ou a une seconde passe si
  les metriques montrent un vrai besoin sur `chess`, `deduction`, `probability`.

#### Ordre d'execution

1. **Realise** : migration OpenAI-only `o3` -> `o4-mini` + tests policy/kwargs/token tracking.
2. **Apres Phase 2A** : comparer par type le taux d'acceptation, de repair, de rejet, la latence
   et le cout entre `o4-mini` et les overrides `gpt-4.1-mini`.
3. **Apres Phase 3C** : evaluer un pipeline 2-passes uniquement si les faux positifs des validateurs
   sont maitrises et si le volume justifie l'effort.

---

### Phase 1 - Semaine 1-2 : Filets de securite immediats

#### 1A. Statuts pipeline structures
**Statut : realise**
**Fichier :** `app/services/challenges/challenge_ai_service.py`  
**Fonction :** `generate_challenge_stream()`

Un statut interne explicite est maintenant defini apres validation :
```python
# Valeurs possibles
GENERATION_STATUS = Literal[
    "accepted",
    "repaired",
    "repaired_by_ai",
    "rejected",
]
```

- `accepted` : validation pass sans correction
- `repaired` : auto_correct_challenge() a corrige + validation pass
- `repaired_by_ai` : repair OpenAI chess declenche + validation pass
- `rejected` : echec apres toutes les tentatives -> SSE propre "defi indisponible"
- `fallback_served` : non implemente ; a reserver a un futur cache de defis prevalides

Un defi `rejected` ne part **jamais** au frontend silencieusement. Les statuts
sont enregistres dans `generation_metrics.record_generation()` et exposes via
`generation_status_counts`.

#### 1B. Codes d'erreur structures, logs au niveau orchestration
**Statut : realise**
**Fichiers :** `app/services/challenges/challenge_validation_error_codes.py`,
`app/services/challenges/challenge_ai_service.py`, `app/utils/generation_metrics.py`
**Principe realise :** les validateurs gardent leur contrat historique
`list[str]`. Une couche d'observabilite centralisee transforme ces messages en
codes stables sans modifier les regles metier.

```python
logger.info(
    "Challenge pipeline resolved: status={}, type={}, validation_passed={}, "
    "auto_corrected={}, error_codes={}, repair={}",
    status, challenge_type, validation_passed, auto_corrected, error_codes, repair_kind
)
```

Codes d'erreur normalises couverts :
- `malformed_choices`, `duplicate_choices`, `missing_correct_answer`,
  `missing_solution_explanation`
- `missing_visual_data`, `visual_data_malformed`
- `graph_nodes_missing`, `graph_edge_out_of_bounds`, `graph_answer_inconsistent`
- `chess_king_in_check`, `chess_board_malformed`, `chess_invalid_piece`,
  `chess_missing_kings`
- `probability_sum_not_one`, `probability_equivalent_choices`,
  `probability_answer_inconsistent`
- `deduction_no_unique_solution`, `deduction_no_solution`,
  `deduction_constraint_parse_failed`, `deduction_answer_mismatch`
- `pattern_unverifiable`, `pattern_answer_inconsistent`,
  `sequence_answer_inconsistent`
- `puzzle_missing_clues`, `puzzle_answer_inconsistent`,
  `coding_answer_inconsistent`
- `validation_unknown`

Les compteurs `error_code_counts` sont disponibles globalement et par type dans
`generation_metrics.get_summary()`. Le dashboard "top 10 erreurs par type" reste
a construire cote lecture/admin, mais les donnees runtime existent.

---

### Phase 2 - Semaine 3-4 : Mesure

#### 2A. Metriques par type de defi
**Statut : TERMINE (sprint beta stabilisation 2026-04-25)**
**Fichier :** `app/utils/generation_metrics.py`

Livre :
- `repair_success_rate` (repaired_by_ai / total_repaired * 100)
- `chess_repair_attempted / succeeded / failed` (compteurs explicites via `record_chess_repair()`)
  - Note : le cas `repaired_challenge is None` sans exception est maintenant aussi compte comme echec (commit 48fb8bf)
- `latency.p50_ms / p95_ms` (interpolation lineaire sur generaions reussies)
- `fallback_rate` (%) + `fallback_causes` dict + `fallback_count`
- `fallback_trigger_reason` instrumente dans `challenge_ai_service.py`

#### 2B. Score de confiance generation (log d'abord, DB ensuite)
**Statut : TERMINE log-only (sprint beta stabilisation 2026-04-25)**
**Fichier :** `app/services/challenges/challenge_ai_service.py`  
**Fonction :** `normalize_generated_challenge()`

Champ `generation_confidence` (0.0-1.0) calcule a la fin :
- -0.3 si repair declenche
- -0.1 par erreur corrigee par auto_correct
- -0.2 si difficulty clampee
- +0.1 si validation pass des le premier essai

Phase beta : logger ce score avec le statut pipeline, sans migration DB.  
Phase post-beta : persister dans `challenges.generation_confidence` seulement si le score permet
vraiment d'identifier les defis douteux dans les metriques Phase 2A.

#### Prochaine action recommandee

Phase 2A/2B et Phase 3A/3B/3D sont fermees. Prochaine etape si on continue ce plan : Phase 3C shadow mode, puis Phase 4 (`ValidatorResult` / repair handlers) ou migration progressive `json_schema`.

---

### Phase 3 - Mois 2 : Tests qui protegent les regles

#### 3A. Golden tests par type
**Statut : TERMINE (Phase 3A, beta.5)**
**Fichier :** `tests/challenges/test_regression_by_type.py`

Strategie : snapshots JSON de payloads reels (fixtures DB ou logs SSE captures)
```python
@pytest.mark.parametrize("fixture_file", glob("tests/fixtures/challenges/*.json"))
def test_challenge_regression(fixture_file):
    data = json.load(open(fixture_file))
    is_valid, errors = validate_challenge_logic(data["challenge"])
    assert is_valid == data["expected_valid"]
    assert set(errors) == set(data["expected_errors"])
```

Couvre : `validate_challenge_logic()`, `auto_correct_challenge()`,
assert structure + solution + `response_mode` effectif + erreurs connues.

#### 3B. Tests contrats IA9
**Statut : TERMINE (Phase 3B, beta.5)**
**Fichier :** `tests/challenges/test_contract_policy.py`

Verifie coherence `response_mode` vs type, presence/forme `choices`,
`visual_data`, compatibilite avec renderers frontend.

#### 3C. Shadow mode pour regles nouvelles
**Statut : NON DEMARRE**
**Principe :** avant de bloquer un defi sur les politiques les plus nouvelles
(deduction solver, probability QCM equivalences), logger sans bloquer
pendant N=200 generations.

```python
if SHADOW_MODE_ACTIVE["deduction_uniqueness"]:
    result = analyze_deduction_uniqueness(visual_data, correct_answer)
    logger.info("[Shadow] deduction_uniqueness result={}", result)
    # Ne pas rejeter
else:
    # Rejeter si non unique
```

Passer en mode bloquant quand faux-positifs mesures < 2%.

#### 3D. Tests perf solveur deduction
**Statut : TERMINE (Phase 3D, beta.5)**
**Fichier :** `tests/unit/test_challenge_deduction_solver.py`

Couvert :
- Test timeout explicite (`MAX_DEDUCTION_SOLVER_COMBINATIONS = 50_000`)
- Test unicite sur grille ambigue (> 1 solution)
- Test cas limite (valeurs dupliquees dans une categorie -> `_build_model` retourne None)
- Benchmark : temps sur grille 4x4 < 100ms

---

### Phase 4 - Mois 3 : Architecture legere

#### 4A. Interface ValidatorResult typee
**Principe :** avant de decouper `challenge_validator.py`, definir le contrat commun

```python
@dataclass
class ValidatorResult:
    is_valid: bool
    errors: list[str]
    challenge_type: str
    error_codes: list[str]  # codes normalises (Phase 1B)
    confidence_delta: float  # contribution au score Phase 2B
```

Toutes les fonctions `validate_*_challenge()` retournent ce type.
Decoupage physique par type (`challenge_validator_chess.py`, etc.) possible
ensuite sans risque de divergence des invariants communs.

#### 4B. Pattern repair generique
**Principe :** remplacer le `if CHESS` dans `challenge_ai_service.py` par un
dispatcheur d'erreurs cataloguees

```python
REPAIR_HANDLERS: dict[str, Callable] = {
    "chess_king_in_check": _repair_chess_validation_failure_with_openai,
    # Futurs : "deduction_no_unique_solution": _repair_deduction_...
}

async def _attempt_repair(challenge_type, errors, ...):
    for error_code in errors:
        handler = REPAIR_HANDLERS.get(error_code)
        if handler:
            return await handler(...)
    return None, None
```

Le repair chess devient une instance d'un pattern extensible,
pas une exception codee en dur.

#### 4C. Structured Outputs stricts OpenAI (`json_schema`)
**Statut :** non demarre
**Priorite :** apres stabilisation des lots deja fusionnes

Objectif : remplacer progressivement `response_format={"type": "json_object"}`
par des sorties structurees strictes OpenAI (`json_schema`) sur les workloads
ou le contrat JSON est suffisamment stable.

Perimetre vise :
- **Defis IA** : cible prioritaire
- **Exercices IA** : extension possible si le cout de maintenance du schema reste acceptable

Pre-conditions :
- les contrats de payload doivent etre geles type par type (ou au moins assez stables)
- les chemins fallback / retry / repair doivent etre compatibles avec un schema strict
- les validateurs existants restent la barriere metier ; le schema ne remplace pas la validation logique

Approche recommandee :
1. Introduire un schema strict d'abord sur 1-2 types robustes (ex. `sequence`, `coding`)
2. Mesurer le taux de refus API / erreurs de schema / latence
3. Etendre ensuite aux autres types si le contrat reste stable

Decision explicite :
- **Ne pas marquer ce lot comme fait** tant que les appels defis utilisent encore
  `response_format={"type": "json_object"}` dans les policies/services OpenAI.

---

## Sujets a surveiller par telemetrie (pas d'action immediate)

- **PROBABILITY** : caps structurels moins couverts - surveiller `validation_failure_rate` post-beta
- **RIDDLE** : validation legere - surveiller qualite via feedback utilisateur
- **PUZZLE** : aucun cap difficulty ajoute dans ce lot - stable mais non instrumente

---

## Anti-patterns a eviter (consensus debat)

- Ajouter des caps dans `challenge_difficulty_policy.py` sans test de non-regression
- Decouper `challenge_validator.py` avant de definir `ValidatorResult`
- Etendre le repair chess au-dela de l'erreur "roi en echec" avant telemetrie
- Augmenter `max_retries` chess sans mesurer l'impact latence SSE
- Ajouter de nouvelles regles bloquantes deduction sans shadow mode ou fixture de non-regression
- Pretendre que le lot `json_schema` est fait tant que le pipeline defis repose encore sur `json_object`

---

## Reference

- Revue lot defis : `docs/03-PROJECT/` (inline session Claude Code 2026-04-22)
- Audit difficulte exercices : `docs/03-PROJECT/AUDIT_AI_MODEL_POLICY_2026-04-19.md`
- Audit difficulte defis : `docs/03-PROJECT/NOTE_CHALLENGE_DIFFICULTY_CALIBRATION_AUDIT_2026-04-19.md`
- Roadmap produit : `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`

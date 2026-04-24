# Plan de solidification - Generation des defis IA
**Date :** 2026-04-22
**Revision :** 2026-04-24
**Contexte :** Post-lot beta.3, puis correctifs successifs de solidification sur la generation, la validation et les contrats backend/frontend
**Contrainte :** Sans refonte totale, solo founder, 1-3 mois

**Note de revision :** Ce plan est relu apres la migration `o3 -> o4-mini`, le durcissement du flux SSE defis, plusieurs correctifs du solveur deduction et l'alignement puzzle backend/frontend sur des cles d'ordre stables.

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
- solveur deduction etendu (same-row naturel, ordering cross-secondary, negations directionnelles)
- validation puzzle alignee sur des cles stables `id` / `piece_id`

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

## Etat reel au 2026-04-24

### Deja fait

- **Phase 0 modele OpenAI** : realisee.
  Le defaut exercices + defis est maintenant `o4-mini`, l'allowlist inclut aussi
  `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, et les kwargs stream exposent
  `stream_options.include_usage`.
- **Hardening du flux defis** :
  fallback o-series mieux borne, tracking d'usage conserve meme si le fallback
  echoue, une seule passe generique d'auto-correction, persistance coherente
  du `difficulty_tier`.
- **Contrats backend/frontend** :
  la validation puzzle s'aligne desormais sur des cles d'ordre stables
  (`id` / `piece_id`) tout en conservant les labels visibles pour les explications.
- **Solveur deduction** :
  support etendu pour `same color/activity/group`, ordering structure sur refs
  secondaires, et parsing negatif directionnel `pas immediatement avant / apres`
  sans faux positif sur les formulations bilaterales non negatives.

### Partiellement fait

- **Solidification validator/solver** :
  plusieurs gaps critiques ont ete fermes, mais l'observabilite structuree,
  le `generation_confidence`, les golden tests et le shadow mode restent a faire.
- **Repair chess** :
  la logique existe et reste pertinente, mais les metriques de declenchement /
  succes prevues par le plan ne sont pas encore en place.

### Pas fait

- **Structured Outputs stricts OpenAI (`json_schema`)** :
  les defis utilisent encore `response_format={"type": "json_object"}` ;
  aucune migration globale vers `json_schema` strict n'est faite a ce stade.
- **Observabilite Phase 1/2** :
  pas encore de statut pipeline type global, ni de codes d'erreur normalises
  exploites comme dashboard.
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
**Fichier :** `app/services/challenges/challenge_ai_service.py`  
**Fonction :** `generate_challenge_stream()`

Introduire un statut interne explicite apres validation :
```python
# Valeurs possibles
GENERATION_STATUS = Literal[
    "accepted",
    "repaired",
    "repaired_by_ai",
    "rejected",
    "fallback_served",
]
```

- `accepted` : validation pass sans correction
- `repaired` : auto_correct_challenge() a corrige + validation pass
- `repaired_by_ai` : repair OpenAI chess declenche + validation pass
- `rejected` : echec apres toutes les tentatives -> SSE propre "defi indisponible"
- `fallback_served` : defi pre-valide servi depuis cache (future)

Un defi `rejected` ne part **jamais** au frontend silencieusement.

#### 1B. Codes d'erreur structures, logs au niveau orchestration
**Fichiers :** `app/services/challenges/challenge_validator.py`,
`app/services/challenges/challenge_ai_service.py`  
**Principe :** les validateurs produisent des codes stables ; le service de generation loggue
une seule fois par tentative pour eviter le bruit et garder les validateurs proches de fonctions pures.

```python
logger.info(
    "[ChallengeGeneration] status={} type={} error_codes={} repair={} latency_ms={}",
    status, challenge_type, error_codes, repair_kind, latency_ms
)
```

Codes d'erreur normalises par type :
- `malformed_choices` / `duplicate_choices` / `missing_correct_answer`
- `inconsistent_graph_nodes` / `graph_edge_out_of_bounds`
- `chess_king_in_check` / `chess_board_malformed`
- `probability_sum_not_one` / `probability_equivalent_choices`
- `deduction_no_unique_solution` / `deduction_constraint_parse_failed`

Objectif : dashboard "top 10 erreurs par type" en lisant les logs.

---

### Phase 2 - Semaine 3-4 : Mesure

#### 2A. Metriques par type de defi
**Fichier :** `app/utils/generation_metrics.py` (existant) + extension

Ajouter par `challenge_type` :
- `validation_failure_rate` (%)
- `repair_success_rate` (%)
- `chess_repair_triggered` (count)
- `chess_repair_succeeded` (count)
- `generation_latency_ms` (P50/P95)
- `fallback_rate` (%)

Si `chess_repair_triggered / total_chess > 20%` -> signal que le prompt chess doit etre revu,
pas que le repair doit etre etendu.

#### 2B. Score de confiance generation (log d'abord, DB ensuite)
**Fichier :** `app/services/challenges/challenge_ai_service.py`  
**Fonction :** `normalize_generated_challenge()`

Ajouter champ `generation_confidence` (0.0-1.0) calcule a la fin :
- -0.3 si repair declenche
- -0.1 par erreur corrigee par auto_correct
- -0.2 si difficulty clampee
- +0.1 si validation pass des le premier essai

Phase beta : logger ce score avec le statut pipeline, sans migration DB.  
Phase post-beta : persister dans `challenges.generation_confidence` seulement si le score permet
vraiment d'identifier les defis douteux dans les metriques Phase 2A.

---

### Phase 3 - Mois 2 : Tests qui protegent les regles

#### 3A. Golden tests par type
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
assert structure + solution + response_mode + erreurs connues.

#### 3B. Tests contrats IA9
**Fichier :** `tests/challenges/test_contract_policy.py`

Verifier coherence `response_mode` vs type, presence/forme `choices`,
`visual_data`, compatibilite avec renderers frontend.
Ces contrats sont actuellement implicites et cassables sans alerte.

#### 3C. Shadow mode pour regles nouvelles
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
**Fichier :** `tests/unit/test_challenge_deduction_solver.py`

Ajouter :
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

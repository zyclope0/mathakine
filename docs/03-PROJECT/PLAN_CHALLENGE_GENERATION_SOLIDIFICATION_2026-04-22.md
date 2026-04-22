# Plan de solidification — Génération des défis IA
**Date :** 2026-04-22  
**Contexte :** Post-lot beta.3 (9 commits défis + corrections revue multi-LLM)  
**Contrainte :** Sans refonte totale, solo founder, 1-3 mois

---

## Origine

Débat structuré 4 IA (Claude + Gemini + OpenCode + Codex) conduit après la revue
du lot `fix(challenges)` origin/master..HEAD. Les corrections immédiate identifiées
lors de la revue (TS build, négation deduction, highlight chess, crash SVG GraphRenderer,
normalisation poids probability) sont supposées faites.

---

## Consensus du débat

> Les 4000 lignes de règles actuelles *peuvent* tenir si et seulement si elles sont
> mesurées, testées et échouent proprement. Sans instrumentation, chaque commit est un pari.

Points unanimes :
- Observabilité avant nouvelles règles
- Repair chess à conserver + métriques de déclenchement
- `max_retries=1` chess + fallback propre = bon compromis solo founder
- Solveur deduction justifié mais nécessite timeout + tests de perf

---

## Plan d'action par phase

### Phase 0 — Décision modèle IA OpenAI (immédiat, sans multi-provider)

#### Vérité terrain

Le code Mathakine utilisait **o3** comme défaut réel pour les deux workloads pédagogiques :

| Workload | Défaut avant décision | Allowlist avant décision | Manque bloquant |
|----------|-----------------------|--------------------------|-----------------|
| Exercices IA | `o3` | `o1`, `o1-mini`, `o3`, `o3-mini`, `gpt-5*`, `gpt-4o*` | `o4-mini`, `gpt-4.1*` |
| Défis IA | `o3` pour tous les types | héritée des exercices | `o4-mini`, `gpt-4.1*` |
| Fallback défis | `gpt-4o-mini` | déjà compatible | aucun |

Source prix à revérifier avant chaque changement majeur : page officielle OpenAI pricing. Au
2026-04-22, `o3` est listé à $2.00 input / $8.00 output par 1M tokens, tandis que
`o4-mini` est listé à $1.10 input / $4.40 output par 1M tokens.

#### Décision retenue

**Basculer le défaut exercices + défis de `o3` vers `o4-mini`.**

Raison :
- Le cœur produit est la génération fiable d'exercices et de défis ; il faut conserver un modèle
  reasoning, pas descendre immédiatement vers une famille chat classique.
- `o4-mini` garde les propriétés nécessaires au pipeline actuel : structured JSON, streaming,
  `reasoning_effort`, coûts reasoning trackables.
- Le coût attendu baisse d'environ 45 % par génération par rapport au défaut `o3`, sans intégrer
  un nouveau provider ni modifier le flux SSE.
- La migration reste OpenAI-only, donc compatible avec l'architecture actuelle : allowlist,
  token tracking, circuit breaker, retry, fallback et tests existants.

#### Changements techniques associés

1. Ajouter `o4-mini` à `EXERCISES_AI_ALLOWED_MODEL_IDS`.
2. Classer `o4-mini` dans la famille reasoning o-series, avec les mêmes kwargs que `o3`
   (`response_format=json_object`, `max_completion_tokens`, `reasoning_effort`).
3. Passer `DEFAULT_EXERCISES_AI_MODEL` à `o4-mini`.
4. Passer `DEFAULT_CHALLENGES_AI_MODEL` et `CHALLENGE_MODEL_BY_TYPE` à `o4-mini`.
5. Garder `gpt-4o-mini` comme fallback de stream vide pour les défis.
6. Ajouter `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano` à l'allowlist uniquement comme overrides
   d'expérimentation ; ne pas les router par défaut tant que les métriques Phase 2A ne sont pas actives.
7. Vérifier le déploiement : si `OPENAI_MODEL_REASONING=o3` existe encore, il garde la priorité legacy
   sur la policy défis. Le corriger en le vidant ou en posant explicitement
   `OPENAI_MODEL_CHALLENGES_OVERRIDE=o4-mini`.

#### Décisions explicitement rejetées maintenant

- Pas d'intégration Gemini/DeepSeek avant métriques qualité. Le gain coût est réel, mais nécessite
  un provider complet : SDK, auth, JSON mode, streaming, token tracking, retry, circuit breaker,
  observabilité et tests contractuels.
- Pas de routage par type vers `gpt-4.1-mini` avant mesure. C'est potentiellement utile pour
  `riddle`, `puzzle` ou `sequence` simples, mais cette famille ne supporte pas `reasoning_effort`
  et peut dégrader la cohérence logique sans télémétrie.
- Pas de `gpt-5.4` par défaut. À réserver plus tard à un mode premium ou à une seconde passe si
  les métriques montrent un vrai besoin sur `chess`, `deduction`, `probability`.

#### Ordre d'exécution

1. **Immédiat** : migration OpenAI-only `o3` → `o4-mini` + tests policy/kwargs/token tracking.
2. **Après Phase 2A** : comparer par type le taux d'acceptation, de repair, de rejet, la latence
   et le coût entre `o4-mini` et les overrides `gpt-4.1-mini`.
3. **Après Phase 3C** : évaluer un pipeline 2-passes uniquement si les faux positifs des validateurs
   sont maîtrisés et si le volume justifie l'effort.

---

### Phase 1 — Semaine 1-2 : Filets de sécurité immédiats

#### 1A. Statuts pipeline structurés
**Fichier :** `app/services/challenges/challenge_ai_service.py`  
**Fonction :** `generate_challenge_stream()`

Introduire un statut interne explicite après validation :
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
- `repaired` : auto_correct_challenge() a corrigé + validation pass
- `repaired_by_ai` : repair OpenAI chess déclenché + validation pass
- `rejected` : échec après toutes les tentatives → SSE propre "défi indisponible"
- `fallback_served` : défi pré-validé servi depuis cache (future)

Un défi `rejected` ne part **jamais** au frontend silencieusement.

#### 1B. Codes d'erreur structurés, logs au niveau orchestration
**Fichiers :** `app/services/challenges/challenge_validator.py`,
`app/services/challenges/challenge_ai_service.py`  
**Principe :** les validateurs produisent des codes stables ; le service de génération loggue
une seule fois par tentative pour éviter le bruit et garder les validateurs proches de fonctions pures.

```python
logger.info(
    "[ChallengeGeneration] status={} type={} error_codes={} repair={} latency_ms={}",
    status, challenge_type, error_codes, repair_kind, latency_ms
)
```

Codes d'erreur normalisés par type :
- `malformed_choices` / `duplicate_choices` / `missing_correct_answer`
- `inconsistent_graph_nodes` / `graph_edge_out_of_bounds`
- `chess_king_in_check` / `chess_board_malformed`
- `probability_sum_not_one` / `probability_equivalent_choices`
- `deduction_no_unique_solution` / `deduction_constraint_parse_failed`

Objectif : dashboard "top 10 erreurs par type" en lisant les logs.

---

### Phase 2 — Semaine 3-4 : Mesure

#### 2A. Métriques par type de défi
**Fichier :** `app/utils/generation_metrics.py` (existant) + extension

Ajouter par `challenge_type` :
- `validation_failure_rate` (%)
- `repair_success_rate` (%)
- `chess_repair_triggered` (count)
- `chess_repair_succeeded` (count)
- `generation_latency_ms` (P50/P95)
- `fallback_rate` (%)

Si `chess_repair_triggered / total_chess > 20%` → signal que le prompt chess doit être revu,
pas que le repair doit être étendu.

#### 2B. Score de confiance génération (log d'abord, DB ensuite)
**Fichier :** `app/services/challenges/challenge_ai_service.py`  
**Fonction :** `normalize_generated_challenge()`

Ajouter champ `generation_confidence` (0.0–1.0) calculé à la fin :
- -0.3 si repair déclenché
- -0.1 par erreur corrigée par auto_correct
- -0.2 si difficulty clampée
- +0.1 si validation pass dès le premier essai

Phase beta : logger ce score avec le statut pipeline, sans migration DB.  
Phase post-beta : persister dans `challenges.generation_confidence` seulement si le score permet
vraiment d'identifier les défis douteux dans les métriques Phase 2A.

---

### Phase 3 — Mois 2 : Tests qui protègent les règles

#### 3A. Golden tests par type
**Fichier :** `tests/challenges/test_regression_by_type.py`

Stratégie : snapshots JSON de payloads réels (fixtures DB ou logs SSE capturés)
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

Vérifier cohérence `response_mode` vs type, présence/forme `choices`,
`visual_data`, compatibilité avec renderers frontend.
Ces contrats sont actuellement implicites et cassables sans alerte.

#### 3C. Shadow mode pour règles nouvelles
**Principe :** avant de bloquer un défi sur les politiques les plus nouvelles
(deduction solver, probability QCM équivalences), logger sans bloquer
pendant N=200 générations.

```python
if SHADOW_MODE_ACTIVE["deduction_uniqueness"]:
    result = analyze_deduction_uniqueness(visual_data, correct_answer)
    logger.info("[Shadow] deduction_uniqueness result={}", result)
    # Ne pas rejeter
else:
    # Rejeter si non unique
```

Passer en mode bloquant quand faux-positifs mesurés < 2%.

#### 3D. Tests perf solveur deduction
**Fichier :** `tests/unit/test_challenge_deduction_solver.py`

Ajouter :
- Test timeout explicite (`MAX_DEDUCTION_SOLVER_COMBINATIONS = 50_000`)
- Test unicité sur grille ambiguë (> 1 solution)
- Test cas limite (valeurs dupliquées dans une catégorie → `_build_model` retourne None)
- Benchmark : temps sur grille 4×4 < 100ms

---

### Phase 4 — Mois 3 : Architecture légère

#### 4A. Interface ValidatorResult typée
**Principe :** avant de découper `challenge_validator.py`, définir le contrat commun

```python
@dataclass
class ValidatorResult:
    is_valid: bool
    errors: list[str]
    challenge_type: str
    error_codes: list[str]  # codes normalisés (Phase 1B)
    confidence_delta: float  # contribution au score Phase 2B
```

Toutes les fonctions `validate_*_challenge()` retournent ce type.
Découpage physique par type (`challenge_validator_chess.py`, etc.) possible
ensuite sans risque de divergence des invariants communs.

#### 4B. Pattern repair générique
**Principe :** remplacer le `if CHESS` dans `challenge_ai_service.py` par un
dispatcheur d'erreurs cataloguées

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
pas une exception codée en dur.

---

## Sujets à surveiller par télémétrie (pas d'action immédiate)

- **PROBABILITY** : caps structurels moins couverts — surveiller `validation_failure_rate` post-beta
- **RIDDLE** : validation légère — surveiller qualité via feedback utilisateur
- **PUZZLE** : aucun cap difficulty ajouté dans ce lot — stable mais non instrumenté

---

## Anti-patterns à éviter (consensus débat)

- ❌ Ajouter des caps dans `challenge_difficulty_policy.py` sans test de non-régression
- ❌ Découper `challenge_validator.py` avant de définir `ValidatorResult`
- ❌ Étendre le repair chess au-delà de l'erreur "roi en échec" avant télémétrie
- ❌ Augmenter `max_retries` chess sans mesurer l'impact latence SSE
- ❌ Ajouter de nouvelles règles bloquantes deduction sans shadow mode ou fixture de non-régression

---

## Référence

- Revue lot défis : `docs/03-PROJECT/` (inline session Claude Code 2026-04-22)
- Audit difficulté exercices : `docs/03-PROJECT/AUDIT_AI_MODEL_POLICY_2026-04-19.md`
- Audit difficulté défis : `docs/03-PROJECT/NOTE_CHALLENGE_DIFFICULTY_CALIBRATION_AUDIT_2026-04-19.md`
- Roadmap produit : `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`

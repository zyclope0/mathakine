# Plan — Qualité de génération défis IA & best practices LLM o-series

**Date :** 2026-04-28
**Auteur initial :** session Cursor + claude-opus-4-7 (founder = Yannick)
**Contexte :** Audit qualité de 10 défis générés post-refactor "Challenge Quality Improvement" (commits `dd3d1a5`→`9b27a36`, version `3.6.0-beta.5`).
**Contrainte :** Solo founder, pas en production, qualité primée sur effort.
**Statut :** PLANIFIÉ — en attente de démarrage Sprint 1.

---

## 1. Pourquoi ce plan

### 1.1 Déclencheur — audit qualité 10 défis (2026-04-28)

Sur 10 défis générés en série (1 par challenge_type, age 15-17 ans), tous validés par le pipeline backend, **3 défis sont en réalité cassés** (logique invalide ou auto-contradictoire) :

| Gen | Type | Bug |
|---|---|---|
| 3 | visual | Auto-contradictoire — la règle modulo-3 invoquée prédit "carré bleu" en pos 6, mais visual_data affiche "carré vert" |
| 4 | puzzle | **Insoluble** — l'indice "C juste avant F" exige F=C+1, mais la solution livrée place C en pos 2 et F en pos 6. Énumération exhaustive : aucune permutation des 7 éléments ne satisfait l'ensemble des contraintes |
| 10 | chess | Position contradictoire (description dame h6 vs board h3) + notation `Dxh7#g7#` invalide + aucun mat en 1 valide depuis cette position |

3 défis présentent des dégradations mineures (storytelling artificiel, fuite linguistique EN/FR, variety seed ignoré). 4 défis sont valides voire excellents (gen 7 probability, gen 8 graph notamment).

**Constat principal du founder :** *"le but premier est de pas avoir de mauvaise génération et en second de les détecter — il faut chercher dans les meilleures pratiques le fonctionnement des LLM type o4 le mieux pour optimiser la génération et éviter les dérives"*.

➡️ **Priorité : GÉNÉRATION > DÉTECTION.**

### 1.2 Issue Sentry à intégrer

**Sentry 115344051** (release `4fcdcb22`, environnement development) — *"Puzzle: éléments manquants dans correct_answer: {'\\\\ln(x)', 'e^x', '\\\\sqrt{x}',..."*.

Cause : mismatch LaTeX (`\ln(x)`) vs Unicode (`ln(x)`) entre `visual_data.pieces` et `correct_answer`. **Fix actif** : `canonical_token` (commit `9b27a36`) normalise NFKC + super/subscripts + opérateurs Unicode AVANT comparaison set dans `validate_puzzle_challenge`.

⚠️ Aucun des 10 défis de l'audit ne contient de math LaTeX dans `pieces` → la série ne valide PAS le fix par cas concret. **Test de non-régression à ajouter** dans le plan (B4).

---

## 2. Vérité terrain — best practices LLM o-series

### 2.1 OpenAI officiel (sources vérifiées 2026)

| Pratique | État Mathakine | Source |
|---|---|---|
| **Structured Outputs `json_schema strict:true`** (constrained decoding, 100% conformité schéma) | ❌ Pas activé — schéma décrit en prose dans le prompt | [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs) |
| **Prompts simples et directs** — pas de "step by step" ni "VALIDATION LOGIQUE étape 1, 2, 3..." | ❌ Le system prompt actuel force du chain-of-thought explicite | [Reasoning best practices](https://developers.openai.com/api/docs/guides/reasoning-best-practices) |
| **Zero-shot first** (les modèles raisonnement n'ont pas besoin de few-shot) | ✅ Pas de few-shot | OpenAI |
| **Responses API + `previous_response_id`** — cache 40→80%, reasoning items persistants → +3% SWE-bench | ❌ On utilise Chat Completions stateless | [Cookbook Responses API](https://developers.openai.com/cookbook/examples/responses_api/reasoning_items/) |
| **Décrire le but final, pas le chemin** — laisser le modèle choisir le chemin | ❌ Le prompt actuel dicte la procédure pas-à-pas | OpenAI |
| **`Formatting re-enabled`** sur la première ligne pour autoriser markdown dans la réponse | ❌ Non déclaré | OpenAI |

### 2.2 Pathologies o4-mini documentées (SATBench, EMNLP 2025)

> *o4-mini achieves only 65.0% accuracy on hard UNSAT problems, close to the random baseline of 50%.*

Trois dérives systématiques identifiées dans la littérature :

- **Satisfiability bias** — préférence pour produire une solution même quand le problème est insoluble. ➡️ **Explique gen 4** (puzzle insoluble livré avec une "solution").
- **Context inconsistency** — divergence entre prose narrative et données structurées. ➡️ **Explique gen 10** (description "dame en h6" vs board en h3).
- **Condition omission** — oubli silencieux d'une contrainte invoquée. ➡️ **Explique gen 3** (règle modulo-3 appliquée à pos 5 mais oubliée pour pos 6).

### 2.3 Techniques de réduction d'erreur à la source

1. **Constrained decoding** (Structured Outputs strict) — élimine 100% des erreurs de schéma JSON via constrained sampling token par token.
2. **Self-Consistency (SC)** — N générations en parallèle + vote majoritaire ; ConVerTest mesure +39% validity vs baseline.
3. **Chain-of-Verification (CoVe)** — génère, formule des questions de vérification ciblées, répond, recombine.
4. **Backward generation** — pour les puzzles à contraintes : générer la solution d'abord, dériver les indices ensuite (PuzzleClone, arxiv 2508.15180).
5. **Round-trip / solver-based validation** AVANT publication (Z3, python-chess, énumération combinatoire) — bouclier final.

### 2.4 Sources documentaires (à citer dans les commits)

- `https://developers.openai.com/api/docs/guides/reasoning-best-practices`
- `https://developers.openai.com/cookbook/examples/responses_api/reasoning_items/`
- `https://platform.openai.com/docs/guides/structured-outputs`
- `https://developers.openai.com/api/docs/guides/latest-model` (GPT-5.5 best practices)
- `https://arxiv.org/html/2505.14615v2` (SATBench — limites o4-mini sur SAT/UNSAT)
- `https://aclanthology.org/2025.emnlp-main.1716/` (publication SATBench)
- `https://arxiv.org/html/2508.15180v1` (PuzzleClone — backward generation + Z3)
- `https://arxiv.org/html/2602.10522v1` (ConVerTest — Self-Consistency + CoVe)

---

## 3. Décisions founder actées (2026-04-28)

| # | Décision | Conséquence sur le plan |
|---|---|---|
| 1 | Casser rétrocompat schéma OK (pas en prod, défis existants supprimables) | A1 sans guards de migration BDD |
| 2 | Solution max qualité, effort secondaire | Tout passer en Responses API, pas de fallback hybride |
| 3 | `python-chess` validé comme dépendance | B2 utilise python-chess directement |
| 4 | Self-Consistency 2-sampling acceptable côté budget | C2 promu en P1 (pas optionnel) |
| 5 | Réutiliser l'infra `generation_metrics` + `token_tracker` existante | C1/C2 = simple **extension** des compteurs déjà ventilés par type, pas de nouveau dashboard |

---

## 4. Plan détaillé

### Phase A — Génération max qualité (P0)

#### A1. Structured Outputs strict (`json_schema strict:true`) 🔴 CRITIQUE
- **Schémas Pydantic v2 par challenge_type**, discriminés sur `challenge_type` :
  - `SequenceChallenge`, `PatternChallenge`, `VisualChallenge`, `PuzzleChallenge`, `DeductionChallenge`, `RiddleChallenge`, `ProbabilityChallenge`, `GraphChallenge`, `CodingChallenge`, `ChessChallenge`.
  - Chaque schéma type son `visual_data` strictement (`PuzzleVisualData(pieces: list[str], hints: list[str], ...)`, etc.).
  - Bornes natives : `difficulty_rating: confloat(ge=1.0, le=5.0)`, `hints: conlist(str, min_length=3, max_length=5)`, `correct_answer: constr(min_length=1)`.
- Fichier nouveau : `app/services/challenges/challenge_schemas.py`.
- Modifier `challenge_ai_service.py` : passer `text.format = {"type": "json_schema", "strict": True, "schema": SchemaForType.model_json_schema()}`.
- **Suppression** de `auto_correct_challenge` pour les erreurs purement structurelles (devenues impossibles).
- **Suppression** de la section "Retourne uniquement le défi au format JSON valide avec ces champs" du system prompt (A2 le rend redondant).

#### A2. Simplifier le system prompt (anti-pattern o-series) 🔴
- Retirer toute la section *"VALIDATION LOGIQUE (obligatoire avant de retourner le JSON) : 1. ... 2. SEQUENCE: ..."* — chain-of-thought explicite documenté comme dégradant pour o-series.
- Retirer `IMPORTANT: Vérifie TOUJOURS la cohérence logique`, `Recalcule mentalement`, `Calcule différences entre termes consécutifs`.
- Convertir les règles procédurales en **contraintes déclaratives** :
  - "La solution doit être unique" (au lieu de "1. Calcule... 2. Vérifie...").
  - "Le titre ne révèle pas la règle pour `difficulty_rating ≥ 4`".
  - "Aucun élément du visual_data ne peut contredire solution_explanation".
- Garder les sections pédagogiques : `STORYTELLING_PRINCIPLES`, `ENGAGEMENT_AND_ACCESSIBILITY`, `DISTRACTOR_COGNITIVE`, calibrage par âge.
- Plus besoin de décrire le format JSON dans le prompt (A1 le force).
- Ajouter `Formatting re-enabled` en première ligne du developer message si on veut autoriser LaTeX dans `solution_explanation`.

#### A3. Migrer vers Responses API + reasoning items persistants 🟡
- Bascule complète `chat.completions.create` → `responses.create` avec :
  - `store=True`
  - `previous_response_id` lors d'un retry/repair
  - `reasoning.summary="auto"` pour log dans `generation_metrics` (champ optionnel `reasoning_summary` à ajouter)
- Bénéfices mesurés OpenAI : cache 40→80%, coût input cached −75%, +3% accuracy SWE-bench.
- **Pas de fallback Chat Completions** (décision 2).
- Vérifier impact sur `app/services/exercises/exercise_ai_service.py` et `server/handlers/chat_handlers.py` (alignement obligatoire).

#### A4. Backward generation pour puzzle/deduction/riddle 🟡
- Reformuler le user prompt pour ces 3 types :
  - *"Génère d'abord la solution finale (`correct_answer`), puis dérive un ensemble minimal d'indices qui rend cette solution UNIQUE et invalide pour toute autre permutation."*
- Évite la classe d'erreurs gen 4 (puzzle insoluble livré comme s'il l'était).
- Pour `riddle`, dériver les contraintes textuelles par chiffre/élément depuis la solution.

#### A5. `visual_data` AVANT prose pour types à double représentation 🟡
- Pour `chess`, `graph`, `puzzle` : forcer dans le schéma A1 que `visual_data` apparaît AVANT `description`/`question` dans le JSON output (extension du pattern déjà appliqué à `solution_explanation`).
- Ajouter au prompt une contrainte : *"Toute position/valeur citée dans la prose doit être lue depuis visual_data, pas inventée."*
- Cible la classe d'erreurs gen 10 (description dame h6 vs board h3).

#### A6. Self-Consistency 2-sampling sur défis difficiles 🟡 (ex-C2 promu en A)
- Pour `difficulty_rating ≥ 4.0` (le segment où les dérives sont concentrées) :
  - Générer **2 candidats en parallèle** (`asyncio.gather`).
  - **Sélection par consensus structurel** :
    - Si les deux passent la validation → garder celui avec `solution_explanation` la plus courte (anti-padding).
    - Si un seul passe → garder le valide.
    - Si aucun ne passe → repair loop standard sur le moins défaillant.
- Coût : ×2 sur le segment difficile uniquement (≈25-30% du volume) — net négatif vs cache Responses API (A3).
- Métrique nouvelle (cf. C2) : `self_consistency_attempts_resolved` et `self_consistency_both_failed`.

### Phase B — Détection (filet de sécurité) (P1)

#### B1. Solver de satisfiabilité minimal pour puzzle/riddle d'ordre 🔴
- Parser indices structurables (regex tolérant FR) :
  - `"X juste après Y"`, `"X juste avant Y"`, `"X k positions avant Y"`, `"X (n')est (pas) en position N"`, `"X et Y consécutifs"`, `"X (n')est (pas) la première opération"`.
- Validation par énumération (≤ 9! ≈ 360k, faisable en <100ms ; pour > 9 éléments, basculer sur `python-constraint` pure-Python ou Z3).
- Vérifier **satisfiabilité ET unicité** de la solution (la solution doit être l'unique permutation valide).
- Nouveaux codes d'erreur : `puzzle_constraints_unsatisfiable`, `puzzle_solution_not_unique`.
- Fichier : `app/services/challenges/puzzle_satisfiability.py`.
- Test de référence : gen 4 doit être rejetée par ce solver.

#### B2. Chess validator avec `python-chess` 🔴
- Dans `validate_chess_challenge` (existant, à étendre) :
  1. Construire `chess.Board()` depuis `visual_data.board` (8×8).
  2. **Cohérence prose↔board** : extraire mentions `[a-h][1-8]` de description/question, vérifier que chaque position citée correspond à une pièce du même camp/type que mentionné.
  3. Parser `correct_answer` en notation SAN (`board.parse_san()`) — bloque les notations invalides type `Dxh7#g7#`.
  4. Si `objective: mat_en_1` : `board.push_san(move); assert board.is_checkmate()`.
  5. Si `objective: capture/échec/clouage` : vérifier la condition correspondante.
- Nouveaux codes d'erreur : `chess_move_illegal`, `chess_not_checkmate`, `chess_position_inconsistent_prose`, `chess_invalid_san_notation`.
- Dépendance : `python-chess` (pure-Python, MIT, ~700KB).
- Fichier : `app/services/challenges/chess_engine_validator.py`.
- Test de référence : gen 10 doit être rejetée sur les 4 axes (notation, mat absent, position contradictoire, fou ne contrôle pas g7).

#### B3. Self-check de règle pour visual/sequence/pattern 🟡
- Extraire la règle invoquée dans `solution_explanation` (heuristiques sur regex : `modulo N`, `cycle de longueur N`, `+k`, `×k`, `n²`, `Fibonacci`).
- Appliquer la règle à **toutes** les positions remplies du `visual_data`, pas seulement la position interrogée.
- Si une seule position remplie contredit la règle invoquée → rejet (`rule_self_check_failed`).
- Cible gen 3 (carré vert en pos 6 contredit la règle modulo 3).
- **Approche progressive** :
  - Phase 1 (1 semaine) : log warning + métrique seulement.
  - Phase 2 (après calibration) : blocage effectif.

#### B4. Test non-régression Sentry 115344051 (LaTeX/Unicode puzzle) 🔴 **AJOUT EXPLICITE**
- Test d'intégration `tests/integration/test_sentry_115344051_latex_unicode_puzzle.py` :
  - **Cas 1 (Sentry réel)** : `pieces = ["\\ln(x)", "e^x", "\\sqrt{x}", "x^2"]` + `correct_answer = "ln(x), eˣ, √x, x²"` (Unicode) → **doit valider sans erreur**.
  - **Cas 2 (symétrique)** : pieces Unicode + answer LaTeX → doit valider.
  - **Cas 3 (vrai manquant)** : `pieces = ["\\ln(x)", "e^x"]` mais `correct_answer = "ln(x)"` → doit rejeter avec `puzzle_answer_pieces_missing`.
  - **Cas 4 (sentinel direct)** : assertions élémentaires :
    - `canonical_token("\\ln(x)") == canonical_token("ln(x)")`
    - `canonical_token("\\sqrt{x}") == canonical_token("√x")`
    - `canonical_token("x^2") == canonical_token("x²")`
    - `canonical_token("e^x") == canonical_token("eˣ")`
- **Bonus (P2)** : test de propriété (Hypothesis) générant des paires LaTeX/Unicode aléatoires pour vérifier idempotence et symétrie de `canonical_token`.
- **Critère de succès** : avant tout autre changement de Sprint 1, ces tests doivent passer sur la base actuelle (vérifier que le fix `9b27a36` est bien intact).

### Phase C — Observabilité (extension de l'existant) (P2)

> ⚠️ **Important** : l'infra `GenerationMetrics` (`app/utils/generation_metrics.py`) et `token_tracker` (`app/utils/token_tracker.py`) ont déjà :
> - `_get_summary_by_type` qui ventile success_rate, validation_failure_rate, error_code_counts par challenge_type
> - `_get_summary_by_workload`, `error_code_counts`, `generation_status_counts`, `chess_repair_stats`, `fallback_stats`, `repair_success_rate`, latency P50/P95
> - Endpoints exposés : `/api/admin/ai-stats` (coûts) et `/api/admin/generation-metrics` (qualité, ventilé par type)
>
> ➡️ **Pas de nouveau dashboard**. On étend les compteurs existants.

#### C1. Étendre `generation_metrics` avec les nouveaux codes d'erreur 🟢
- **Pas de changement de structure** — réutilise `error_code_counts` déjà ventilé par type via `_get_summary_by_type`.
- Étendre `classify_challenge_validation_error` (`app/services/challenges/challenge_validation_error_codes.py`) pour reconnaître les nouvelles familles de message :
  - `puzzle_constraints_unsatisfiable`
  - `puzzle_solution_not_unique`
  - `chess_move_illegal`
  - `chess_not_checkmate`
  - `chess_position_inconsistent_prose`
  - `chess_invalid_san_notation`
  - `rule_self_check_failed`
- Tests unitaires correspondants dans `tests/unit/test_challenge_validation_error_codes.py`.

#### C2. Métriques Self-Consistency (réutilise `record_generation`) 🟢
- Ajouter un champ optionnel à `record_generation` : `self_consistency_attempts: int | None` (1 si SC désactivé pour ce défi, 2 si activé).
- Le coût ×2 est déjà capté par `token_tracker` (chaque call OpenAI logue son coût) → **visible dans `/api/admin/ai-stats` aujourd'hui**, segmenté par `challenge_type`.
- Ajouter dans `get_summary` un nouveau bloc cohérent avec le pattern existant (`fallback_stats`, `chess_repair_stats`) :
  ```
  self_consistency_stats = {
    "enabled_count": N,        # défis pour lesquels SC a été activé (difficulty ≥ 4.0)
    "consensus_resolved": M,   # désaccords résolus en faveur du candidat valide
    "both_failed": K,          # cas où les 2 candidats ont échoué la validation
  }
  ```

#### C3. Vue admin coût/défi validé (P3) 🟢
- Frontend admin : ajouter une colonne "coût/défi validé" = `daily_cost_by_type / success_count_by_type`.
- Aucun changement backend — combine les deux endpoints existants côté UI.
- KPI ROI : permet de prioriser les futures optimisations sur les types les plus chers à valider.

---

## 5. Séquencement final

```
Sprint 1 — Génération max qualité (semaine 1-2)
  A1 Structured Outputs strict + schémas Pydantic par type
  A2 Refactor system prompt (retire chain-of-thought, contraintes déclaratives)
  B4 Test non-régression Sentry 115344051 (LaTeX/Unicode)

Sprint 2 — Détection bouclier (semaine 2-3)
  B2 Chess validator python-chess        ← gen 10 réparé
  B1 Puzzle satisfiability solver         ← gen 4 réparé
  B3 Rule self-check (warning mode)
  C1 Extension error codes dans generation_metrics

Sprint 3 — Optimisation (semaine 3-4)
  A3 Migration Responses API
  A4 Backward generation puzzle/deduction/riddle
  A5 Anti-dérive contextuelle visual_data-first
  A6 Self-Consistency 2-sampling difficulty ≥ 4.0
  C2 Métriques Self-Consistency

Sprint 4 — Polish
  C3 Vue admin coût/défi validé
  B3 Rule self-check passe en mode bloquant (après calibration métrique)
```

---

## 6. KPIs cibles (mesurables sur `/api/admin/generation-metrics`)

| KPI | Baseline (à mesurer) | Cible |
|---|---|---|
| Validation au 1er essai (`success_rate`) | ?% | **≥ 95%** après Phase A |
| Défis cassés en prod (Sentry validation_logic) | ?/sem | **≤ 0.2%** sur 7 jours glissants |
| Coût par défi validé (`daily_cost / success_count`) | ?€/défi | **−40 à −50%** (cache Responses API −75% sur input cached, contre +50% pour SC = net négatif) |
| Latence P95 (`latency.p95_ms`) | ?ms | Maintien ou amélioration (moins de retries) |

**Mesure baseline obligatoire** avant Sprint 1 : capturer une semaine de métriques actuelles via `/api/admin/generation-metrics?days=7` et `/api/admin/ai-stats?days=7`.

---

## 7. État d'avancement

> Mettre à jour cette section à chaque commit qui touche au plan.

| Sprint | Item | Statut | Commit | Date |
|---|---|---|---|---|
| 0 | Plan rédigé et validé | ✅ DONE | (non commité) | 2026-04-28 |
| 1 | A1 Structured Outputs | ⏳ À faire | — | — |
| 1 | A2 Simplification prompt | ⏳ À faire | — | — |
| 1 | B4 Test non-régression Sentry | ⏳ À faire | — | — |
| 2 | B2 Chess validator | ⏳ À faire | — | — |
| 2 | B1 Puzzle solver | ⏳ À faire | — | — |
| 2 | B3 Rule self-check | ⏳ À faire | — | — |
| 2 | C1 Extension error codes | ⏳ À faire | — | — |
| 3 | A3 Responses API | ⏳ À faire | — | — |
| 3 | A4 Backward generation | ⏳ À faire | — | — |
| 3 | A5 visual_data-first | ⏳ À faire | — | — |
| 3 | A6 Self-Consistency | ⏳ À faire | — | — |
| 3 | C2 Métriques SC | ⏳ À faire | — | — |
| 4 | C3 Vue coût/validé | ⏳ À faire | — | — |
| 4 | B3 mode bloquant | ⏳ À faire | — | — |

---

## 8. Annexes

### 8.1 Findings audit 10 défis (référence détaillée)

L'audit complet des 10 défis (verdicts, feedbacks OpenAI à coller, vérifications mathématiques par défi) est conservé dans le transcript de session du 2026-04-28. Si besoin de le récupérer : chercher dans le transcript par mots-clés `"Génération 4"`, `"insoluble"`, `"Dxh7#g7#"`, `"carré vert"`.

### 8.2 Prompt actuel — sections à conserver vs supprimer

**À conserver** (contraintes pédagogiques utiles) :
- `STORYTELLING_PRINCIPLES`
- `ENGAGEMENT_AND_ACCESSIBILITY` (et alias rétro `ENGAGEMENT_PRINCIPLES`, `ACCESSIBILITY_COGNITIVE`)
- `DISTRACTOR_COGNITIVE`
- Calibrage par âge (6-8, 9-11, 12-14, 15-17, adulte)
- `RÈGLES DE DIFFICULTÉ` et `CALIBRATION STRICTE`
- `CALIBRAGE APPRENANT (F42)`
- Politique CHOIX/QCM par type (`IA9`)
- Variety seed injection (déjà bien fait dans `challenge_prompt_composition.py`)

**À supprimer** (anti-patterns o-series) :
- Section `VALIDATION LOGIQUE (obligatoire avant de retourner le JSON) : 1. ... 2. SEQUENCE: ...`
- `IMPORTANT : Vérifie TOUJOURS la cohérence logique avant de retourner le JSON.`
- `Recalcule mentalement : correct_answer et solution_explanation alignés.`
- `RÈGLE IMPORTANTE POUR LES INDICES :` (peut rester en version raccourcie déclarative)
- Description du format JSON champ par champ (rendue redondante par A1)
- `CONTRAINTE DE SORTIE JSON :` section (rendue redondante)

### 8.3 Sources techniques externes (à citer dans commits)

Voir §2.4. À citer en footer de chaque commit Sprint 1-3 sous la forme :
```
Refs:
- OpenAI reasoning best practices: developers.openai.com/api/docs/guides/reasoning-best-practices
- SATBench (limites o4-mini SAT/UNSAT): arxiv.org/html/2505.14615v2
```

---

## 9. Maintenance de ce plan

- **Auteur :** founder (Yannick) + IA en session.
- **Mise à jour de la table §7** : à chaque commit touchant au plan, ajouter le hash et la date.
- **Clôture du plan** : quand tous les items sont DONE, déplacer dans `docs/03-PROJECT/archive/` ou marquer "DONE" en tête. Mettre à jour `AGENTS.md` pour retirer la référence active.
- **Si pivot stratégique** : ne pas écraser ce plan — créer un nouveau `PLAN_*_2026-MM-DD.md` et marquer celui-ci `SUPERSEDED BY`.

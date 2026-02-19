# Analyse — Génération IA des défis logiques

> **Date :** Fév. 2026  
> **Type :** Analyse technique et audit  
> **Objectif :** Identifier bugs, incohérences et optimisations pour une exploitation en production

---

## 1. Flux de génération

```
Frontend (AIGenerator) 
  → GET /api/challenges/generate-ai-stream?challenge_type=X&age_group=Y
  → Backend (challenge_handlers.generate_ai_challenge_stream)
  → OpenAI API (stream, response_format: json_object)
  → Collecte full_response (pas de streaming des chunks au client)
  → Parse JSON (avec fallbacks: extraction {…}, nettoyage commentaires, complétion)
  → Validation (challenge_validator.validate_challenge_logic)
  → Auto-correction si possible (auto_correct_challenge)
  → Normalisation + create_challenge (DB)
  → SSE: challenge + done
```

---

## 2. Bugs et incohérences identifiés

### 2.1 ~~Critique — challenge_type en base~~ ✅ Corrigé

| Fichier | Problème |
|---------|----------|
| ~~`challenge_handlers.py` L1194~~ | ~~`normalized_challenge["challenge_type"] = challenge_type.upper()`~~ |
| `challenge_handlers.py` L1556 | ✅ `normalized_challenge["challenge_type"] = challenge_type` (minuscules, L874) |

---

### 2.2 ~~Affichage âge dans le prompt~~ ✅ Corrigé

| Ligne | Actuel |
|-------|--------|
| 963 | ✅ `age_display = params["display"]` → "9-11 ans", "adultes", "tous âges" |

---

### 2.3 Validations manquantes (partiellement corrigé)

Les types **RIDDLE** et **DEDUCTION** n'ont pas de fonction `validate_*` dédiée ; les règles sont dans le prompt. **CHESS** et **PROBABILITY** ont désormais `validate_chess_challenge` et `validate_probability_challenge`.

---

### 2.4 Séquence : analyse limitée

`analyze_sequence()` ne gère que :
- Séquences arithmétiques (différence constante)
- Une variante avec différences croissantes (+2, +3, +4…)

Non géré : géométrique (2, 4, 8, 16), Fibonacci, motifs alternés complexes.

---

### 2.5 Schémas manquants pour RIDDLE et PROBABILITY

Le prompt système définit des schémas pour SEQUENCE, PATTERN, PUZZLE, GRAPH, DEDUCTION, VISUAL, CODING, CHESS. **RIDDLE** et **PROBABILITY** n'ont pas de structure `visual_data` explicite.

**Impact :** L’IA invente des formats qui peuvent être incompatibles avec les renderers frontend.

---

### 2.6 Rendu frontend sans visual_data

| Composant | Comportement |
|-----------|--------------|
| `ChallengeVisualRenderer` | `if (!challenge.visual_data) return null` |
| `ChallengeSolver` | `{challenge.visual_data && <ChallengeVisualRenderer />}` |

Si `visual_data` est `{}` ou vide, aucune visualisation n’est affichée. Pour RIDDLE textuel, la description/question restent visibles, mais l’UX peut être limitée.

---

### 2.7 Gestion du stream SSE

Le backend accumule toute la réponse avant de parser le JSON. Le client ne reçoit que :
1. `status` (génération en cours…)
2. `challenge` (à la fin)
3. `done`

Pas de streaming du texte généré → pas d’effet "typing" côté client.

---

## 3. Alignement prompt ↔ renderers

| Type | Attendu par le prompt | Attendu par le renderer | Statut |
|------|-----------------------|--------------------------|--------|
| SEQUENCE | `{sequence: [...], pattern: "n+2"}` | `sequence` ou `items` | OK |
| PATTERN | `{grid: [...], size: 3}` | `grid` | OK |
| VISUAL | `shapes`, `symmetry` (layout, symmetry_line) | `shapes`, `layout`, `grid` | OK |
| PUZZLE | `{pieces, hints, description}` | `pieces`/`items`, `hints`/`rules`/`clues` | OK |
| GRAPH | `{nodes, edges}` | `nodes`, `edges` | OK |
| DEDUCTION | `{type: "logic_grid", entities, clues}` | `entities`, `clues`, `type` | OK |
| CODING | `type` caesar/substitution/binary/symbols/maze | idem + `maze`, `encoded_message` | OK |
| CHESS | `{board, turn, objective}` | `board`, `turn`, `knight_position` | Partiel (cas "mat") |
| RIDDLE | Aucun schéma | `clues`, `riddle`, `grid`, `pots`, `plaque` | Risque d’incompatibilité |
| PROBABILITY | Aucun schéma | `*_bonbons`, `*_billes`, etc. | Risque d’incompatibilité |

---

## 4. Optimisations proposées

### Priorité haute

1. **Corriger challenge_type pour la DB** — Passer la valeur lowercase à `create_challenge`.
2. **Corriger l’affichage âge** — Utiliser `params["display"]` dans le prompt.
3. **Ajouter des schémas RIDDLE et PROBABILITY** dans le prompt système.

### Priorité moyenne

4. **Valider DEDUCTION** — Format `correct_answer` (`A:B:C,D:E:F`), cohérence avec `entities` et `clues`.
5. **Enrichir analyze_sequence** — Séquences géométriques, Fibonacci.
6. **Valider CHESS** — Présence de `board`, `turn`, `objective`, `highlight_positions` valides.

### Priorité basse

7. **Validation RIDDLE** — Présence de `clues` ou `context` ou `riddle`.
8. **Validation PROBABILITY** — Présence de quantités (bonbons, billes, etc.) et cohérence avec `correct_answer`.
9. **Streaming partiel** — Envoyer des chunks de texte au client avant le JSON final (optionnel).

---

## 5. Fichiers concernés

| Fichier | Rôle |
|---------|------|
| `server/handlers/challenge_handlers.py` | Génération, prompt, normalisation |
| `app/services/challenge_validator.py` | Validation logique, auto-correction |
| `app/services/challenge_service.py` | CRUD, mapping age_group |
| `frontend/components/challenges/visualizations/*.tsx` | Rendu par type |
| `frontend/components/challenges/ChallengeSolver.tsx` | Affichage défi complet |
| `frontend/components/challenges/AIGenerator.tsx` | Appel API, parsing SSE |

---

## 6. Corrections appliquées (session courante)

Voir les commits associés pour les modifications concrètes.

---

## 7. Audit post-optimisation (15/02/2026)

> **Contexte :** Tous les types de défis ont été optimisés (prompts, validations, comparaisons, renderers).  
> **Objectif :** Vérifier la cohérence globale avant push/commit.

### 7.1 Synthèse par type

| Type | Config IA | Validation | Comparaison | Renderer | Statut |
|------|-----------|------------|-------------|----------|--------|
| **PROBABILITY** | BASIC_MODEL, low | `validate_probability_challenge` | Fractions (6/10, 0.6, 60%) | ProbabilityRenderer | ✅ OK |
| **GRAPH** | ADVANCED_MODEL, medium | `validate_graph_challenge` | Ensemble (ordre libre) ou chemin (ordonné) | GraphRenderer + positions | ✅ OK |
| **CODING** | ADVANCED_MODEL, medium | `validate_coding_challenge` | Défaut (texte exact) | CodingRenderer (César + partial_key) | ✅ OK |
| **CHESS** | ADVANCED_MODEL, 14k tokens, medium | `validate_chess_challenge` | FR/EN, duals (\|), numéros de coups | ChessRenderer (légende, coordonnées) | ✅ OK |
| **DEDUCTION** | ADVANCED_MODEL, high | Règles dans prompt (pas de fonction dédiée) | Associations (A:B, C:D) | DeductionRenderer | ⚠️ Val. basique |
| **PATTERN** | ADVANCED_MODEL, high | `validate_pattern_challenge` + auto_correct | Grille = source de vérité | PatternRenderer | ✅ OK |
| **SEQUENCE** | BASIC_MODEL, low | `validate_sequence_challenge` + auto_correct | Défaut | SequenceRenderer | ✅ OK |
| **PUZZLE** | BASIC_MODEL, low | `validate_puzzle_challenge` | Défaut | PuzzleRenderer | ✅ OK |
| **VISUAL** | ADVANCED_MODEL, high | `validate_visual_challenge` | Multi-position, synonymes | VisualRenderer | ✅ OK |
| **RIDDLE** | BASIC_MODEL, low | Règles dans prompt (clues/context) | Défaut | RiddleRenderer | ⚠️ Val. basique |

### 7.2 Points vérifiés (corrections antérieures)

| Point | Statut |
|-------|--------|
| `challenge_type` pour DB | ✅ Utilise `challenge_type` (déjà lowercasé L874) |
| Affichage âge dans prompt | ✅ `params["display"]` (L963) → "9-11 ans", "adultes", "tous âges" |
| Fallback o3 si réponse vide | ✅ Relance avec `gpt-5.1` (L1374–1395) |
| Règles de validation dans prompt | ✅ PROBABILITY (pt 9), GRAPH (pt 10), CHESS (pt 7), CODING César (pt 6) |

### 7.3 Flux de génération (rappel)

1. Frontend → `GET /api/challenges/generate-ai-stream`
2. `challenge_type` lowercasé, `age_group` normalisé
3. Config IA via `AIConfig.get_openai_params(challenge_type)` (MODEL_MAP, MAX_TOKENS_MAP, etc.)
4. Stream OpenAI → `full_response`
5. Si o3 et réponse vide → fallback `gpt-5.1`
6. Parse JSON → validation (`validate_challenge_logic`) → auto_correct si PATTERN/SEQUENCE/VISUAL
7. `create_challenge` → DB (challenge_type en minuscules conforme à l’enum)

### 7.4 Points d’attention restants (non bloquants)

- **RIDDLE / DEDUCTION :** Pas de `validate_*` dédié dans `challenge_validator` ; les règles sont dans le prompt. Suffisant pour MVP.
- **SEQUENCE :** `analyze_sequence` ne gère pas géométrique/Fibonacci ; cas limites possibles.
- **Streaming :** Pas de "typing effect" côté client (le client reçoit le challenge à la fin).

### 7.5 Verdict

**État : OK pour push/commit**

- Prompts, config IA, validations et comparaisons sont alignés.
- Fallback o3 opérationnel.
- Tous les types ont un renderer et une logique de comparaison.

**Recommandation :** Tester manuellement 1 génération par type (chess, probability, graph, coding) avant merge en prod pour valider les cas réels.

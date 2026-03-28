# Audit Documentation Mathakine — 2026-03-27

**Périmètre :** global (pas uniquement F42)
**Méthode :** 4 agents parallèles (docs, backend, frontend, tests/infra)
**Score global :** 8.5/10 (gouvernance mature, lacunes ciblées)

---

## 1. Cartographie — ce qui existe

### Documentation écrite (docs/)

| Dossier | Fichiers .md | Qualité |
|---------|-------------|---------|
| `docs/00-REFERENCE/` | ~8 (manifestes, références techniques) | Bonne — F42 manifest complet |
| `docs/01-GUIDES/` | 17 guides | Bonne — déploiement, dev, testing présents |
| `docs/02-FEATURES/` | ~12 (roadmap, features, API ref) | Moyenne — roadmap à jour, ADR manquants |
| `docs/03-PROJECT/` | 19 (governance, audits, pilotage) | Très bonne — audits récents (2026-03-22) |
| `docs/04-FRONTEND/` | ~4 (architecture, composants) | Partielle — hooks et lib/ non couverts |

**Total estimé :** 277+ fichiers .md dans l'ensemble du projet (README, CHANGELOG, docs intégrées)

---

### Code documenté vs non documenté

#### Backend (190 fichiers Python)

| Domaine | Fichiers clés | Documenté |
|---------|--------------|-----------|
| Config (`app/core/`) | config.py, types.py, ai_config.py, mastery_tier_bridge.py | ✅ Manifeste F42 + ADR informel |
| Services exercices | exercise_ai_service.py, adaptive_difficulty_service.py | ✅ Partiellement (F42 manifest) |
| Services défis | challenge_ai_service.py, challenge_contract_policy.py, challenge_ai_model_policy.py | ⚠️ Partiellement — 3 policy files sans doc dédiée |
| Services gamification | gamification_service.py, level_titles.py, badge_gamification_updates.py | ⚠️ Partiellement — concurrence et ledger non formalisés en ADR |
| Services recommandations | recommendation_service.py | ⚠️ Partiel — asymétrie exercices/défis non documentée |
| Services auth | auth_session_service.py | ✅ Auth JWT documenté |
| Evaluation harness | `app/evaluation/`, ai_eval_harness_repository.py | ❌ **Non documenté** |
| Analytics | (service analytics) | ❌ Non documenté |
| Circuit breaker OpenAI | openai_circuit_breaker (référencé tests) | ❌ Non documenté |
| Repositories | 10+ fichiers | ⚠️ Aucune doc dédiée couche data |
| ORM Models (17) | user.py, exercise.py, logic_challenge.py, point_event.py... | ⚠️ Schémas non cartographiés dans les docs |
| Migrations (33 versions) | 20260327_add_content_difficulty_tier.py ... | ❌ **Pas de guide migration DB** |
| Scripts ops (18 fichiers) | cleanup, backup, audit, debug, fix | ❌ **Pas de doc scripts** |

#### Frontend (Next.js 15)

| Couche | Fichiers | Documenté |
|--------|---------|-----------|
| Pages (34) | exercises, challenges, dashboard, profile, leaderboard... | ⚠️ Architecture décrite, pages individuelles non |
| Composants (150+) | ExerciseCard, ChallengeCard, LevelIndicator, ContentListProgressiveFilterToolbar... | ⚠️ Architecture seule |
| Hooks (47) | useExercises, usePaginatedContent, useRecommendations, useAIExerciseGenerator... | ❌ **37/47 sans tests, aucun catalogue doc** |
| API routes (7) | exercises/generate-ai-stream, challenges/generate-ai-stream, chat, chat/stream... | ⚠️ `/api/chat` et `/api/chat/stream` sans auth (P1 connu) |
| Lib utils | exportExcel, exportPDF, ssePostStream, headerTimeRangeScope... | ❌ Non documenté |
| i18n (fr/en) | messages/fr.json, messages/en.json | ⚠️ Pas de guide contribution i18n |

#### Tests / Infra

| Aspect | Nombre | Documenté |
|--------|--------|-----------|
| Tests unit backend | 86 fichiers | ✅ Convention testée (TESTING.md) |
| Tests API | 25 fichiers | ✅ |
| Tests integration | 7 fichiers | ✅ |
| Tests frontend (unit + e2e + a11y) | 57 fichiers | ⚠️ Partiel |
| Nouveaux tests IA (untracked) | 12 fichiers (test_ai_eval_harness*, test_challenge_ia4-5-9*, test_gamification*, test_exercise_ia2b*) | ❌ **Non référencés** |
| CI/CD workflow | tests.yml (3 jobs : test + lint + frontend) | ✅ CICD_DEPLOY.md |
| Scripts ops (18) | data, backup, debug, fix, maintenance | ❌ **0 documentation** |
| Migrations DB (33) | 20260327... jusqu'à initial_snapshot | ❌ **Pas de guide runbook migration** |
| Coverage backend gate | 63% minimum (CI enforce) | ✅ |
| Coverage frontend | ~35% (en progression) | ⚠️ Non documenté comme objectif |

---

## 2. Lacunes priorisées

### P0 — Bloquant (risque opérationnel immédiat)

| # | Lacune | Fichier cible | Impact |
|---|--------|--------------|--------|
| ~~P0-1~~ | ~~REDIS_URL absente de render.yaml~~ | `render.yaml` | **LIVRÉ** 2026-03-27 |
| ~~P0-2~~ | ~~Guide migration DB absent~~ | `docs/01-GUIDES/DATABASE_MIGRATIONS.md` | **LIVRÉ** 2026-03-27 |

### P1 — Important (dette technique documentaire active)

| # | Lacune | Fichier cible | Impact |
|---|--------|--------------|--------|
| ~~P1-1~~ | ~~ADR-001 : Route chat publique sans auth~~ | `docs/05-ADR/ADR-002-chat-assistant-public-boundary.md` | **LIVRÉ** 2026-03-27 |
| ~~P1-2~~ | ~~ADR-002 : Gamification concurrence (with_for_update)~~ | `docs/05-ADR/ADR-003-gamification-concurrency-model.md` | **LIVRÉ** 2026-03-27 |
| ~~P1-3~~ | ~~ADR-003 : AI model policy layering (deux systèmes)~~ | `docs/05-ADR/ADR-004-ai-model-policy-architecture.md` | **LIVRÉ** 2026-03-27 |
| ~~P1-4~~ | ~~Catalogue hooks frontend (41 hooks)~~ | `docs/04-FRONTEND/HOOKS_CATALOGUE.md` | **LIVRÉ** 2026-03-27 |
| ~~P1-5~~ | ~~Documentation evaluation harness IA~~ | `docs/02-FEATURES/AI_EVAL_HARNESS.md` | **LIVRÉ** 2026-03-27 |
| ~~P1-6~~ | ~~Documentation scripts ops~~ | `docs/01-GUIDES/SCRIPTS_UTILITIES.md` | **LIVRÉ** 2026-03-27 |
| ~~P1-7~~ | ~~Asymétrie reco exercices/défis~~ | `docs/02-FEATURES/RECOMMENDATIONS_ALGORITHM.md` | **LIVRÉ** 2026-03-27 |

### P2 — Nice-to-have (amélioration qualité doc)

| # | Lacune | Fichier cible | Impact |
|---|--------|--------------|--------|
| P2-1 | Catalogue composants React (150+) | `docs/04-FRONTEND/COMPONENTS_CATALOGUE.md` | Onboarding coûteux |
| P2-2 | Guide contribution i18n (fr/en) | `docs/01-GUIDES/I18N_CONTRIBUTION.md` | Risques d'incohérence traductions |
| P2-3 | Doc circuit breaker OpenAI | `docs/02-FEATURES/OPENAI_CIRCUIT_BREAKER.md` | Comportement en panne OpenAI non documenté |
| P2-4 | Guide analytics service | `docs/02-FEATURES/ANALYTICS_SERVICE.md` | Service existant mais invisible dans docs |
| P2-5 | Cartographie ORM models (17 entités) | `docs/00-REFERENCE/DATA_MODEL.md` | Navigabilité DB difficile sans ERD |
| P2-6 | Référence API routes frontend (7 routes) | `docs/04-FRONTEND/API_ROUTES.md` | `/api/chat` sans auth visible nulle part |
| P2-7 | Guide runbook migration Alembic | `docs/01-GUIDES/DATABASE_MIGRATIONS.md` (commandes + checklist prod) | Complète P0-2 |
| P2-8 | Doc nouveaux tests IA non trackés (12) | Référencer dans `docs/01-GUIDES/TESTING.md` | Tests invisibles = jamais maintenus |

---

## 3. Structure documentaire cible

```
docs/
├── 00-REFERENCE/              ✅ Manifestes
│   ├── DIFFICULTY_AND_RANKS_MANIFEST.md  ✅



│   └── DATA_MODEL.md          ← P2-5 (ERD 17 entités)
│
├── 01-GUIDES/                 ✅ Guides opérationnels
│   ├── DEPLOYMENT_ENV.md      ✅ (mettre à jour REDIS_URL)
│   ├── DATABASE_MIGRATIONS.md ✅ LIVRÉ
│   ├── SCRIPTS_UTILITIES.md   ✅ LIVRÉ
│   ├── TESTING.md             ✅ (référencer 12 tests IA non trackés)
│   └── I18N_CONTRIBUTION.md   ← P2-2
│
├── 02-FEATURES/               ⚠️ Features + algorithmes
│   ├── ROADMAP_FONCTIONNALITES.md  ✅
│   ├── API_QUICK_REFERENCE.md ✅
│   ├── CHALLENGE_CONTRACT_IA9.md ✅
│   ├── DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md ✅
│   ├── RECOMMENDATIONS_ALGORITHM.md ← P1-7 À CRÉER
│   ├── AI_EVAL_HARNESS.md     ← P1-5 À CRÉER
│   ├── OPENAI_CIRCUIT_BREAKER.md ← P2-3
│   └── ANALYTICS_SERVICE.md   ← P2-4
│
├── 03-PROJECT/                ✅ Gouvernance
│   └── (complet — audits récents à jour)
│
└── 04-FRONTEND/               ⚠️ Architecture partielle
    ├── ARCHITECTURE.md        ✅
    ├── HOOKS_CATALOGUE.md     ← P1-4 À CRÉER
    ├── COMPONENTS_CATALOGUE.md ← P2-1
    └── API_ROUTES.md          ← P2-6
```

---

## 4. Docs obsolètes ou désalignées

| Document | Problème | Action |
|----------|---------|--------|
| `docs/03-PROJECT/POINTS_RESTANTS_2026-03-15.md` | Référence des items maintenant résolus (F42-C1A...C4 DONE) | Archiver dans `AUDITS_ET_RAPPORTS_ARCHIVES/` |
| `docs/02-FEATURES/README.md` | Peut référencer des features pré-F42 (à vérifier) | Relire et aligner sur roadmap courante |
| `app/schemas/exercise.py` docstrings "Épreuves Jedi" | Résidus Star Wars — neutralisés en F42-C1B | ✅ Déjà traité |
| `app/schemas/logic_challenge.py` star_wars_title | Champ nullable legacy — dette documentée, acceptable | Vérifier dans prochaine revue contrat |
| `.env.example` REDIS_URL (commentée) | Commentaire ne suffit pas si ENVIRONMENT=production | Décommenter + noter dans DEPLOYMENT_ENV.md |
| `render.yaml` REDIS_URL absente | Variable manquante = crash prod silencieux | Ajouter dans render.yaml (P0-1) |
| `docs/03-PROJECT/IMPLEMENTATION_F07*.md` et `F32*.md` | Features anciennes — probablement archivables | Vérifier si encore actives avant archivage |

---

## 5. Synthèse exécutive

### Ce qui est mature (ne pas toucher)

- Gouvernance projet : 8.5/10, audits réguliers, pilotage Cursor bien documenté
- Architecture backend : patterns clairs, CLAUDE.md complet, conventions appliquées
- CI/CD : tests.yml complet, 3 jobs, coverage gate 63%, Codecov intégré
- F42 manifest : complet et aligné avec le code livré
- Auth JWT : bien documenté

### Ce qui est fragile (agir)

1. **REDIS_URL production** (P0) — une ligne dans render.yaml évite un crash
2. **3 ADRs manquants** (P1) — décisions prises, jamais tracées formellement
3. **37/47 hooks frontend sans tests** (P1) — risque de régression invisible
4. **18 scripts sans documentation** (P1) — risque opérateur en maintenance
5. **Evaluation harness IA totalement invisible** dans les docs (P1)

### Modules backend sans couverture de tests

| Module | Type | Risque |
|--------|------|--------|
| `challenge_query_service.py` | Service requêtes défis | Moyen |
| `challenge_stream_service.py` | Stream SSE défis | Élevé |
| `exercise_stream_service.py` | Stream SSE exercices | Élevé |
| `exercise_attempt_service.py` | Tentatives exercices | Élevé |
| `gamification_service.py` (complet) | Points/levels | Élevé |
| 8+ services admin | Admin backoffice | Moyen |
| `analytics_service.py` | Analytics | Faible |
| `mastery_tier_bridge.py` | Bridge F42 | Élevé |
| Repositories (exercise, ai_eval_harness) | Couche data | Moyen |

### Hooks frontend sans tests (10 principaux)

- `useAIExerciseGenerator.ts` — générateur IA exercices (critique)
- `useExercises.ts` — hook principal exercices (critique)
- `useRecommendations.ts` — recommendations
- Pages : exercises, challenges, dashboard, profile (aucun test unitaire)
- Composants : AIGenerator, ChallengeSolver (aucun test)

### Estimation effort

| Priorité | Items | Effort estimé |
|----------|-------|---------------|
| P0 (2) | REDIS_URL + guide migration | ~1h |
| P1 (7) | 3 ADR + 4 docs métier | ~4-6h |
| P2 (8) | Catalogues + guides complémentaires | ~8-12h |

---

*Rapport généré par audit 4 agents parallèles — 2026-03-27*
*Agents : docs-cartography, backend-cartography, frontend-cartography, tests-infra*

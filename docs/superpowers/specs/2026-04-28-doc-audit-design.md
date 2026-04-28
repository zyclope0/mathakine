# Documentation Alignment Audit — Design Spec

**Date :** 2026-04-28
**Statut :** Approuvé par le founder — prêt pour implémentation
**Périmètre :** ~60 fichiers Markdown actifs (hors `_ARCHIVE_2026/`, `.venv/`, `frontend/`)
**Contexte :** La dernière revue documentaire date du commit `536e7b6` (~50 commits). Depuis, beta.5 a été stabilisée, les phases 1A–3D des défis IA ont été livrées, et plusieurs corrections de sécurité ont été appliquées.

---

## Objectif

Aligner **toute** la documentation active sur la réalité du terrain au commit `33bb325` (v3.6.0-beta.5). Aucun fichier n'est exclu a priori — chaque doc est challengée contre le code actif.

---

## Architecture générale

```
Phase 1 — Extraction ground-truth
  Lire le code actif (routes, services, modèles, config, CHANGELOG)
  → Produire docs/superpowers/specs/2026-04-28-ground-truth-snapshot.md
  → Commit : docs(audit): add ground-truth snapshot v3.6.0-beta.5

Phase 2 — Sweep documentaire (7 groupes)
  Pour chaque doc : comparer contre la fiche de référence
  Identifier les écarts : obsolète / faux / manquant / correct

Phase 3 — Corrections in-place + commits par groupe
  Corriger chaque doc directement
  Ajouter bandeau [ROADMAP] sur les docs planifiées
  Un commit par groupe : docs(audit): align <groupe> to ground-truth v3.6.0-beta.5
```

---

## Fiche ground-truth — 7 domaines

| Domaine | Ce qu'on extrait |
|---------|-----------------|
| **Version** | Tag courant, état beta, CHANGELOG dernière entrée |
| **Runtime backend** | Entrypoint ASGI, serveur, port, workers |
| **Routes actives** | Tous les endpoints (méthode + path + handler), groupés par domaine |
| **Architecture** | Couches (routes → handlers → services), repos actifs, modèles ORM |
| **IA** | Modèles par type de défi, fallback, effort reasoning, circuit breaker |
| **Auth** | Mécanisme JWT, durées tokens, cookies, rôles |
| **Patterns de code** | Conventions actives (settings.X, loguru {}, .is_(True), no Star Wars) |

La fiche est produite par lecture directe des fichiers sources — aucune déduction.
Elle reste dans le repo après le chantier comme référence datée.

---

## Règles de correction

| Cas rencontré | Action |
|---------------|--------|
| Référence à FastAPI | Remplacer par Starlette |
| Mauvais numéro de version | Corriger vers 3.6.0-beta.5 |
| Endpoint inexistant ou path erroné | Corriger ou supprimer |
| Feature décrite comme "planifiée" mais livrée | Retirer la mention "planifié", décrire l'état livré |
| Feature décrite comme livrée mais absente du terrain | Marquer `[NON LIVRÉ — à vérifier]` |
| Doc roadmap (feature future) | Ajouter bandeau `[ROADMAP — pas encore implémenté]` en tête + vérifier points partiellement livrés |
| Plan/spec superpowers clos | Ajouter statut `[CLOS]` en tête |
| Information correcte | Laisser telle quelle — pas de réécriture inutile |

---

## Groupes de sweep — ordre et périmètre

### Groupe 1 — Racine (4 fichiers)
`AGENTS.md`, `CLAUDE.md`, `README_TECH.md`, `CHANGELOG.md`
Priorité haute — lus à chaque session IA.

### Groupe 2 — `docs/00-REFERENCE/` (7 fichiers)
`ARCHITECTURE.md`, `DATA_MODEL.md`, `AI_MODEL_GOVERNANCE.md`,
`DIFFICULTY_AND_RANKS_MANIFEST.md`, `GETTING_STARTED.md`,
`USER_ROLE_NOMENCLATURE.md`, `README.md`
Priorité haute — référence stable supposée exacte.

### Groupe 3 — `docs/02-FEATURES/` (20 fichiers)
`API_QUICK_REFERENCE.md`, `AUTH_FLOW.md`, `CHALLENGE_CONTRACT_IA9.md`,
`GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md`, `OPENAI_CIRCUIT_BREAKER.md`,
`ADMIN_FEATURE_SECURITE.md`, `AI_EVAL_HARNESS.md`, `ANALYTICS_SERVICE.md`,
`EDTECH_ANALYTICS.md`, `I18N.md`, `RECOMMENDATIONS_ALGORITHM.md`, `THEMES.md`,
`DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md`, `README.md`,
`ROADMAP_FONCTIONNALITES.md`,
+ docs roadmap : `F02_DEFIS_QUOTIDIENS.md`, `F03_DIAGNOSTIC_INITIAL.md`,
`F04_REVISIONS_ESPACEES.md`, `F05_ADAPTATION_DYNAMIQUE.md`,
`PARENT_DASHBOARD_AND_CHILD_LINKS.md`
Les 5 docs roadmap reçoivent le bandeau + vérification points livrés.

### Groupe 4 — `docs/01-GUIDES/` (19 fichiers)
`DEPLOYMENT_ENV.md`, `DEVELOPMENT.md`, `TESTING.md`, `PRODUCTION_RUNBOOK.md`,
`MAINTENANCE.md`, `CONTRIBUTING.md`, `DATABASE_MIGRATIONS.md`,
`CREATE_TEST_DATABASE.md`, `LANCER_SERVEUR_TEST.md`, `TROUBLESHOOTING.md`,
`SCRIPTS_UTILITIES.md`, `SENTRY_MONITORING.md`, `TESTER_MODIFICATIONS_SECURITE.md`,
`CONFIGURER_EMAIL.md`, `ENV_CHECK.md`, `ESLINT_PRETTIER_FRONTEND.md`,
`GUIDE_UTILISATEUR_MVP.md`, `I18N_CONTRIBUTION.md`, `QU_EST_CE_QUE_VENV.md`,
`README.md`

### Groupe 5 — `docs/03-PROJECT/` (12 fichiers)
`README.md`, `PLAN_CHALLENGE_GENERATION_SOLIDIFICATION_2026-04-22.md`,
`AUDIT_FRONTEND_INDUSTRIALISATION_2026-04-09.md`,
`AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`,
`AUDIT_AI_MODEL_POLICY_2026-04-19.md`,
`ANALYSE_DEPENDANCES_ET_OPPORTUNITES_2026-04-13.md`,
`NOTE_CHALLENGE_DIFFICULTY_CALIBRATION_AUDIT_2026-04-19.md`,
`PLAN_FEATURE_B_EXERCISE_SKILL_STATE_POST_BETA_2026-04-18.md`,
`POLITIQUE_REDACTION_LOGS_PII.md`, `RAPPORT_REVUE_DOCUMENTAIRE_2026-04-16.md`,
`CICD_DEPLOY.md`, `CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md`,
`DEBAT_NEURO_INCLUSION_2026-03-30.md`

### Groupe 6 — `docs/superpowers/` (9 fichiers)
Plans et specs superpowers — vérifier statut ouvert/clos, ajouter `[CLOS]` si livré.
`specs/` (4) + `plans/` (5)

### Groupe 7 — Fichiers isolés (2 fichiers)
`.github/copilot-instructions.md`, `.impeccable.md`

---

## Hors scope

- `_ARCHIVE_2026/` — intentionnellement gelé
- `.claude/archive/` — notes founder locales non poussées
- `frontend/` — docs frontend traitées séparément (ACTIF-04)

---

## Stratégie de commit

```
docs(audit): add ground-truth snapshot v3.6.0-beta.5
docs(audit): align root docs to ground-truth v3.6.0-beta.5
docs(audit): align 00-REFERENCE to ground-truth v3.6.0-beta.5
docs(audit): align 02-FEATURES to ground-truth v3.6.0-beta.5
docs(audit): align 01-GUIDES to ground-truth v3.6.0-beta.5
docs(audit): align 03-PROJECT to ground-truth v3.6.0-beta.5
docs(audit): align superpowers specs/plans to ground-truth v3.6.0-beta.5
docs(audit): align isolated docs to ground-truth v3.6.0-beta.5
```

---

## Artefacts produits

| Fichier | Rôle |
|---------|------|
| `docs/superpowers/specs/2026-04-28-ground-truth-snapshot.md` | Référence terrain datée — reste dans le repo |
| Corrections in-place dans les ~60 docs | Aucun rapport séparé |

---

## Implémentation recommandée

Groupes 3 et 4 (02-FEATURES et 01-GUIDES) peuvent être traités en parallèle par deux sous-agents indépendants. Les groupes 1 et 2 (racine + 00-REFERENCE) doivent précéder car ils contiennent la vérité canonique que les autres docs référencent.

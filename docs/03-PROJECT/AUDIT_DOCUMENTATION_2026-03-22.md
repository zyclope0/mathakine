# Audit Documentaire — Mathakine — 2026-03-22

**Date :** Mars 2026
**Type :** Audit
**Statut :** Actif
**Perimetre :** Tous les dossiers `docs/`, `README.md`, `README_TECH.md`, `frontend/README.md`, `frontend/TROUBLESHOOTING.md`

---

## 1. Score global

**Score initial : 72 / 100**
**Score apres corrections du 2026-03-22 : 82 / 100**

La documentation est globalement coherente avec l'architecture reelle. Les documents de reference actifs (`ARCHITECTURE.md`, `AI_MODEL_GOVERNANCE.md`, `API_QUICK_REFERENCE.md`, `AUTH_FLOW.md`) sont maintenus et pointent vers le code source. Suite aux corrections appliquees le 2026-03-22, les 6 non-conformites factuelles principales ont ete resolues (chemins auth, variables env, version, encodage, fastapi→starlette). Les 5 points restants concernent des ecarts de contenu moins critiques (baseline tests, guides anciens, API gamification).

---

## 2. Tableau recapitulatif par document

| Document | Statut | Problemes identifies |
|---|---|---|
| `docs/INDEX.md` | OK | Contenu a jour, banniere obsolescence presente. |
| `docs/CONVENTION_DOCUMENTATION.md` | OK | Structure valide, coherente avec l'organisation actuelle. |
| `docs/00-REFERENCE/ARCHITECTURE.md` | OK | Contenu exact. Avertissement obsolescence bien positionne en section 3. |
| `docs/00-REFERENCE/AI_MODEL_GOVERNANCE.md` | A_CORRIGER (enrichi) | Existait mais manquait les sections SSE POST, contrat IA9 et risque TokenTracker. Enrichi lors de cet audit. |
| `docs/00-REFERENCE/GETTING_STARTED.md` | ~~A_CORRIGER~~ **CORRIGE** | ~~Version produit `3.1.0-alpha.8` stale~~ → `3.3.0-alpha.1`. ~~`ALLOWED_ORIGINS`~~ → `BACKEND_CORS_ORIGINS`. Corrige 2026-03-22. |
| `docs/01-GUIDES/TESTING.md` | A_CORRIGER | Baseline citee `962 passed` (post-iteration I, 19/03/2026) ; la baseline R7 (`991 passed`) n'est pas mentionnee. |
| `docs/01-GUIDES/DEVELOPMENT.md` | OK | Contenu correct et a jour. |
| `docs/01-GUIDES/DEPLOYMENT_ENV.md` | OK | Correct et complet (updated 15/03/2026). |
| `docs/01-GUIDES/ENV_CHECK.md` | A_CORRIGER | Section historique marquee OBSOLETE mais toujours presente sans redirection claire. Variable `OPENAI_MODEL` listee comme legacy encore visible dans snapshot. |
| `docs/01-GUIDES/TROUBLESHOOTING.md` | ~~A_CORRIGER~~ **CORRIGE** | ~~`ALLOWED_ORIGINS`~~ → `BACKEND_CORS_ORIGINS`. Corrige 2026-03-22. |
| `docs/01-GUIDES/MAINTENANCE.md` | A_CORRIGER | Version `1.0.0` du document datee decembre 2025 ; contenu non mis a jour depuis. Emojis dans les titres (inconventionnel). |
| `docs/01-GUIDES/CONTRIBUTING.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/CONFIGURER_EMAIL.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/CREATE_TEST_DATABASE.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/QU_EST_CE_QUE_VENV.md` | ~~STALE~~ **CORRIGE** | ~~`fastapi 0.121.0`~~ → `starlette 0.52.1` dans les exemples d'arbres venv. Corrige 2026-03-22. |
| `docs/01-GUIDES/LANCER_SERVEUR_TEST.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/SENTRY_MONITORING.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/ESLINT_PRETTIER_FRONTEND.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/TESTER_MODIFICATIONS_SECURITE.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/GUIDE_UTILISATEUR_MVP.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/02-FEATURES/README.md` | OK | Index clair et correctement tenu. |
| `docs/02-FEATURES/API_QUICK_REFERENCE.md` | A_CORRIGER | Manque les endpoints gamification (`/api/badges/stats` present mais `point_events` ledger et `apply_points` absents, signale dans AUDIT_TECHNIQUE_2026-03-22). |
| `docs/02-FEATURES/AUTH_FLOW.md` | ~~A_CORRIGER~~ **CORRIGE** | ~~`app/services/auth_*.py`~~ → `app/services/auth/auth_*.py` (3 chemins corriges). Corrige 2026-03-22. |
| `docs/02-FEATURES/CHALLENGE_CONTRACT_IA9.md` | OK | Contenu correct et compact. |
| `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` | ~~A_CORRIGER~~ **CORRIGE** | ~~Artefacts d'encodage mojibake generalisés.~~ 1133 sequences double-encodees corrigees (UTF-8/CP1252). Corrige 2026-03-22. |
| `docs/02-FEATURES/F02_DEFIS_QUOTIDIENS.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/02-FEATURES/F03_DIAGNOSTIC_INITIAL.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/02-FEATURES/F04_REVISIONS_ESPACEES.md` | OK | Marque "future spec" dans le README features. |
| `docs/02-FEATURES/F05_ADAPTATION_DYNAMIQUE.md` | A_CORRIGER | Artefacts mojibake dans quelques passages. |
| `docs/02-FEATURES/EDTECH_ANALYTICS.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/02-FEATURES/ADMIN_FEATURE_SECURITE.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/02-FEATURES/ADMIN_ESPACE_PROPOSITION.md` | OK | Marque "Partial / mixed" dans README features. |
| `docs/02-FEATURES/BADGES_AMELIORATIONS.md` | OK | Marque "Historical + partial reference". |
| `docs/02-FEATURES/ANALYTICS_PROGRESSION.md` | OK | Marque "Historical / partially superseded". |
| `docs/02-FEATURES/WORKFLOW_EDUCATION_REFACTORING.md` | OK | Marque "Historical design reference". |
| `docs/02-FEATURES/I18N.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/02-FEATURES/THEMES.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/02-FEATURES/NIVEAUX_DIFFICULTE_NORMALISATION.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/03-PROJECT/README.md` | OK | Index gouvernance correct, bien tenu. |
| `docs/03-PROJECT/CODE_REVIEW_2026-03-22.md` | OK | Snapshot historique, banniere OBSOLETE presente. |
| `docs/03-PROJECT/AUDIT_TECHNIQUE_2026-03-22.md` | OK | Snapshot historique, banniere OBSOLETE presente. |
| `docs/03-PROJECT/AUDIT_IA_LAYER_2026-03-22.md` | OK | Snapshot historique, banniere OBSOLETE presente. |
| `docs/03-PROJECT/POINTS_RESTANTS_2026-03-15.md` | OK | Seul tracker actif, bien tenu. |
| `docs/03-PROJECT/PILOTAGE_IA_GENERATION_EXERCICES_DEFIS_2026-03-21.md` | OK | Banniere OBSOLETE presente, renvoie vers `AI_MODEL_GOVERNANCE.md`. |
| `docs/03-PROJECT/CICD_DEPLOY.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/03-PROJECT/evaluation/AI_GENERATION_HARNESS.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/04-FRONTEND/ARCHITECTURE.md` | ~~A_CORRIGER~~ **CORRIGE** | ~~`NEXT_PUBLIC_API_URL`~~ → `NEXT_PUBLIC_API_BASE_URL` dans la section Variables d'environnement. Corrige 2026-03-22. |
| `docs/04-FRONTEND/DESIGN_SYSTEM.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/04-FRONTEND/ACCESSIBILITY.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/04-FRONTEND/ANIMATIONS.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/04-FRONTEND/PWA.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/06-WIDGETS/` (5 fichiers) | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `README.md` (racine) | OK | A jour, version `3.3.0-alpha.1`, stack Starlette correctement citee. |
| `README_TECH.md` | OK | A jour, contenu technique correct. |
| `frontend/README.md` | A_CORRIGER | Version `3.2.0-alpha.1` stale (actuelle : `3.3.0-alpha.1`). Status "Production Ready ~95%" non aligne avec l'etat alpha. Derniere MAJ : 22/02/2026. Variable `NEXT_PUBLIC_API_URL` citee seule (sans mention `NEXT_PUBLIC_API_BASE_URL`). |
| `frontend/TROUBLESHOOTING.md` | A_CORRIGER | Reference `BACKEND_CORS_ORIGINS` correcte dans le corps, mais contenu OK sinon. |

---

## 3. Details des problemes par fichier

### ~~P1~~ ✅ CORRIGE — `docs/00-REFERENCE/GETTING_STARTED.md`

| # | Ligne approx. | Nature | Etat |
|---|---|---|---|
| 1 | 5 | Version produit `3.1.0-alpha.8` stale | **Corrige** → `3.3.0-alpha.1` (2026-03-22) |
| 2 | 47 | `ALLOWED_ORIGINS=http://localhost:3000` | **Corrige** → `BACKEND_CORS_ORIGINS` (2026-03-22) |

### ~~P2~~ ✅ CORRIGE — `docs/01-GUIDES/TROUBLESHOOTING.md`

| # | Ligne approx. | Nature | Etat |
|---|---|---|---|
| 1 | 36 | `ALLOWED_ORIGINS=http://localhost:3000` | **Corrige** → `BACKEND_CORS_ORIGINS` (2026-03-22) |

### P3 — `docs/01-GUIDES/TESTING.md`

| # | Ligne approx. | Nature | Correction recommandee |
|---|---|---|---|
| 1 | 104 | Baseline `962 passed` citee comme "verified state" sans mention de la baseline R7 (`991 passed`) | Ajouter une note sur la baseline R7 (2026-03-21) au-dessus ou remplacer par la plus recente |

### ~~P4~~ ✅ CORRIGE — `docs/01-GUIDES/QU_EST_CE_QUE_VENV.md`

| # | Ligne approx. | Nature | Etat |
|---|---|---|---|
| 1 | 29, 46 | `fastapi 0.121.0` dans exemples d'arbres venv | **Corrige** → `starlette 0.52.1` (2026-03-22) |

### ~~P5~~ ✅ CORRIGE — `docs/02-FEATURES/AUTH_FLOW.md`

| # | Ligne approx. | Nature | Etat |
|---|---|---|---|
| 1 | 129 | `app/services/auth_session_service.py` | **Corrige** → `app/services/auth/auth_session_service.py` (2026-03-22) |
| 2 | 130 | `app/services/auth_recovery_service.py` | **Corrige** → `app/services/auth/auth_recovery_service.py` (2026-03-22) |
| 3 | 131 | `app/services/auth_service.py` | **Corrige** → `app/services/auth/auth_service.py` (2026-03-22) |

### ~~P6~~ ✅ CORRIGE — `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`

| # | Nature | Etat |
|---|---|---|
| 1 | Artefacts d'encodage mojibake generalises (Ã, â€", â€œ, Â§, etc.) | **Corrige** — 1133 sequences double-encodees restaurees via substitution byte-level CP1252 → UTF-8 (2026-03-22) |

### ~~P7~~ ✅ CORRIGE — `docs/04-FRONTEND/ARCHITECTURE.md`

| # | Ligne approx. | Nature | Etat |
|---|---|---|---|
| 1 | 224-225 | `NEXT_PUBLIC_API_URL=http://localhost:10000` cite comme variable principale | **Corrige** → `NEXT_PUBLIC_API_BASE_URL` (2026-03-22) |

### P8 — `frontend/README.md`

| # | Ligne approx. | Nature | Correction recommandee |
|---|---|---|---|
| 1 | 3 | Version `3.2.0-alpha.1` stale | Aligner sur `3.3.0-alpha.1` (source : `frontend/package.json`) |
| 2 | 4 | Statut "Production Ready (~95% complete)" | Adapter au statut alpha reel ; eviter les affirmations de production readiness non validees |
| 3 | 233-234 | `NEXT_PUBLIC_API_URL=http://localhost:10000` cite seul | Utiliser `NEXT_PUBLIC_API_BASE_URL` (variable principale) |
| 4 | 569 | `Derniere mise a jour : 22/02/2026` | Mettre a jour la date lors de la prochaine revision |

### P9 — `docs/02-FEATURES/API_QUICK_REFERENCE.md`

| # | Nature | Correction recommandee |
|---|---|---|
| 1 | Les endpoints de lecture du ledger `point_events` et l'action `apply_points` ne sont pas documentes | Ajouter une section Gamification une fois les endpoints exposes (F38 — en backlog) |

---

## 4. Coherence avec la stack reelle

### Conformites verifiees

| Aspect | Etat |
|---|---|
| Backend cite comme Starlette (pas FastAPI) dans les docs actifs | Conforme |
| Routes actives dans `server/routes/` (pas `app/api/endpoints/`) | Conforme |
| JWT access 15min + refresh 7j | Conforme (`AUTH_FLOW.md`) |
| Redis requis en production | Conforme (`DEPLOYMENT_ENV.md`, `ARCHITECTURE.md`) |
| Gamification : ledger `point_events` + badges + `jedi_rank` | Partiellement conforme (`API_QUICK_REFERENCE.md` cite `jedi_rank` mais pas le ledger) |
| SSE migre GET -> POST | Conforme (`API_QUICK_REFERENCE.md`, sections exercices et defis) |
| Gouvernance modeles : `app_model_policy.py` + `ai_workload_keys.py` | Conforme (`AI_MODEL_GOVERNANCE.md`) |

### Non-conformites actives (apres corrections 2026-03-22)

| Document | Variable/Chemin incorrect | Valeur correcte |
|---|---|---|
| `frontend/README.md` l.233 | `NEXT_PUBLIC_API_URL` (seul) | `NEXT_PUBLIC_API_BASE_URL` (principal) |

> **Resolues le 2026-03-22 :** `ALLOWED_ORIGINS` (×2), `app/services/auth_*.py` (×3), `NEXT_PUBLIC_API_URL` dans `04-FRONTEND/ARCHITECTURE.md`, `fastapi 0.121.0` dans `QU_EST_CE_QUE_VENV.md`.

### Artefacts stale identifies (apres corrections 2026-03-22)

| Document | Artefact |
|---|---|
| `frontend/README.md` | Version `3.2.0-alpha.1` stale (actuelle : `3.3.0-alpha.1`) |
| `TESTING.md` | Baseline `962 passed` presentee comme "current" sans mention de la baseline R7 (`991 passed`) |
| `MAINTENANCE.md` | Version document `1.0.0` datee decembre 2025, jamais revue |

> **Resolus le 2026-03-22 :** version `3.1.0-alpha.8` dans `GETTING_STARTED.md`, mojibake `ROADMAP_FONCTIONNALITES.md` (1133 sequences).

---

## 5. Documents manquants prioritaires

| Priorite | Document | Justification |
|---|---|---|
| P1 | `docs/05-ADR/` (dossier ADRs) | Recommande dans `AUDIT_TECHNIQUE_2026-03-22.md`. Decisions cles non documentees : choix Starlette vs FastAPI, absence de `with_for_update` dans gamification, chat public sans auth, coexistence de deux systemes de policy IA. |
| P2 | Runbook operationnel | Aucune procedure de demarrage d'urgence, de rollback de migration Alembic, ni de procedure de rotation de cle `SECRET_KEY` en production. `MAINTENANCE.md` est trop generique. |
| P2 | Documentation gamification complete | Le moteur `GamificationService` (F38), le ledger `point_events`, les niveaux Jedi et les endpoints associes ne sont pas documentes dans une reference autonome. |
| P3 | `docs/05-ADR/ADR-001-starlette-vs-fastapi.md` | Le choix Starlette est mentionne partout mais jamais justifie formellement. |

---

## 6. Documents a archiver selon la convention

D'apres `CONVENTION_DOCUMENTATION.md`, les documents suivants devraient etre evalues pour archivage :

| Document | Motif | Action recommandee |
|---|---|---|
| `docs/03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md` | Protocole de validation d'une periode passee | Garder en racine si toujours utilise ; sinon deplacer dans `RAPPORTS_TEMPORAIRES/` |
| `docs/03-PROJECT/REFACTOR_DASHBOARD_2026-03.md` | Note de refactoring | Verifier si les actions sont terminees ; archiver dans `AUDITS_IMPLEMENTES/` si oui |
| `docs/01-GUIDES/MAINTENANCE.md` | Version 1.0.0 de decembre 2025, jamais mise a jour | Mettre a jour ou marquer explicitement comme "snapshot historique" |

---

## 7. Bilan par dossier

| Dossier | Nb docs audites | OK | A_CORRIGER | STALE | NON_VERIFIE |
|---|---|---|---|---|---|
| `docs/00-REFERENCE/` | 3 | **3** *(+1)* | 0 *(−1)* | 0 | 0 |
| `docs/01-GUIDES/` | 5 | **3** *(+2)* | 2 *(−1)* | 0 *(−1)* | 10 |
| `docs/02-FEATURES/` | 10 | **8** *(+2)* | 1 *(−2)* | 0 | 7 |
| `docs/03-PROJECT/` | 8 | 7 | 0 | 0 | 1 |
| `docs/04-FRONTEND/` | 1 | **1** *(+1)* | 0 *(−1)* | 0 | 4 |
| `docs/06-WIDGETS/` | 0 | 0 | 0 | 0 | 5 |
| Racine + frontend/ | 4 | 2 | 2 | 0 | 0 |
| **Total** | **31** | **24** *(+6)* | **5** *(−5)* | **0** *(−1)* | **27** |

> **Corrections appliquees le 2026-03-22 :** 6 documents passes de A_CORRIGER/STALE a OK.

#  Audit Documentaire — Mathakine — 2026-03-22

**Date d’audit initial :** 22/03/2026  
**Dernière mise à jour de ce fichier :** 23/03/2026 (alignement post-restauration + suivi des corrections encore ouvertes)  
**Type :** Audit documentaire  
**Statut :** Actif — checklist d’audit ; le code et `docs/INDEX.md` restent la vérité opérationnelle.

**Périmètre :** dossiers `docs/`, `README.md`, `README_TECH.md`, `frontend/README.md`, `frontend/TROUBLESHOOTING.md`.

> **Note de lecture :** le titre du fichier reste `AUDIT_DOCUMENTATION_2026-03-22` pour l’historique. La version restaurée de ce rapport contenait des dates internes incohérentes ; ce document doit donc être lu comme une checklist d’écarts et de corrections, pas comme une chronologie fiable.

## 0. Compléments traités

### 23/03/2026 — lot initial

- `frontend/README.md` : références principales basculées sur `NEXT_PUBLIC_API_BASE_URL` (local, production, checklist).
- `docs/01-GUIDES/QU_EST_CE_QUE_VENV.md` : exemples `fastapi` remplacés par `starlette`.
- Rationalisation structurelle : `docs/investor_deck/` sorti de `docs/`, docs widgets re-rangées sous `docs/04-FRONTEND/DASHBOARD_WIDGETS/`, `docs/06-WIDGETS/` converti en redirects legacy, `F34_SCIENCES_PROTOTYPE.html` déplacé dans `docs/assets/prototypes/`.
- Le présent audit est requalifié en **checklist** documentaire ; les documents actifs dans `docs/INDEX.md` restent la source de vérité.

### 23/03/2026 — lot complémentaire session P0/P1

- **`docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`** : ajout statuts `[DONE]` / `[PARTIAL]` / `[BACKLOG]` dans la matrice + **Section 8 « Features implementees (historique) »** (8.1 livrées avec dates/références, 8.2 fondations partielles). F39 [LEGAL] ajouté (refonte rangs + suppression IP Star Wars). Nouveau document challenger **`ROADMAP_MVP_CHALLENGE_2026-03.md`** créé (3 horizons H1/H2/H3, focus solo founder).
- **`tests/conftest.py`** : garde sécurité DB renforcée — détection host externe (`render.com`, `amazonaws.com`…) ajoutée dans les 3 checks (auto-dérivation, SECURITE 1 engine URL, SECURITE 3 TEST==DATABASE). Corrige le faux positif `mathakine_test_gii8` (nom contient "test" mais est une base Render de production).
- **`docs/03-PROJECT/AUDIT_TECHNIQUE_2026-03-22.md`** : section 0 ajoutée avec suivi des corrections post-audit (T1, A4, P4, D5, D6 résolus ; D8, B1, B2, B4, B6 encore ouverts). Plan d'action mis à jour avec colonne statut.

---

## 1. Score global

**Score initial : 72 / 100**  
**Score après corrections 2026-03-22 : 82 / 100**  
**Score après corrections complémentaires 2026-03-06 : ~88 / 100** (estimation — baseline tests, ENV redirect, MAINTENANCE, API gamification, F05 mojibake, `frontend/README` + `frontend/TROUBLESHOOTING`)

La documentation est globalement cohérente avec l’architecture réelle. Les documents de référence actifs (`ARCHITECTURE.md`, `AI_MODEL_GOVERNANCE.md`, `API_QUICK_REFERENCE.md`, `AUTH_FLOW.md`) sont maintenus et pointent vers le code source. Corrections du **2026-03-22** : chemins auth, variables env, version, encodage roadmap, fastapi→starlette. Complément **2026-03-06** : baseline R7 dans `TESTING.md`, redirection explicite dans `ENV_CHECK.md`, section gamification / `point_events` dans `API_QUICK_REFERENCE.md`, révision `MAINTENANCE.md` (titres sans emoji, version 1.1.0), correction mojibake `F05_ADAPTATION_DYNAMIQUE.md`, alignement `frontend/README.md` + en-tête `frontend/TROUBLESHOOTING.md`. Reste surtout du **NON_VERIFIE** dans le tableau (guides non parcourus) et les sujets **P1/P2** (ADR, runbook) de la §5.

---

## 2. Tableau recapitulatif par document

| Document | Statut | Problemes identifies |
|---|---|---|
| `docs/INDEX.md` | OK | Contenu a jour, banniere obsolescence presente. |
| `docs/CONVENTION_DOCUMENTATION.md` | OK | Structure valide, coherente avec l'organisation actuelle. |
| `docs/00-REFERENCE/ARCHITECTURE.md` | OK | Contenu exact. Avertissement obsolescence bien positionne en section 3. |
| `docs/00-REFERENCE/AI_MODEL_GOVERNANCE.md` | OK | Référence à jour : §8 pattern SSE POST, §9 contrat IA9 (`response_mode`), §10 risques TokenTracker / métriques runtime. Vérifié 06/03/2026. |
| `docs/00-REFERENCE/GETTING_STARTED.md` | ~~A_CORRIGER~~ **CORRIGE** | ~~Version produit `3.1.0-alpha.8` stale~~ → `3.3.0-alpha.1`. ~~`ALLOWED_ORIGINS`~~ → `BACKEND_CORS_ORIGINS`. Corrige 2026-03-22. |
| `docs/01-GUIDES/TESTING.md` | ~~A_CORRIGER~~ **CORRIGE** | Baseline R7 (`991 passed, 2 skipped`) + baseline I historique (`962 passed, 3 skipped`). Corrige 2026-03-06. |
| `docs/01-GUIDES/DEVELOPMENT.md` | OK | Contenu correct et a jour. |
| `docs/01-GUIDES/DEPLOYMENT_ENV.md` | OK | Correct et complet (updated 15/03/2026). |
| `docs/01-GUIDES/ENV_CHECK.md` | ~~A_CORRIGER~~ **CORRIGE** | Redirection explicite vers DEPLOYMENT_ENV + AI_MODEL_GOVERNANCE + `.env.example`. Nuance `OPENAI_MODEL` (legacy chat / allowlist). Corrige 2026-03-06. |
| `docs/01-GUIDES/TROUBLESHOOTING.md` | ~~A_CORRIGER~~ **CORRIGE** | ~~`ALLOWED_ORIGINS`~~ → `BACKEND_CORS_ORIGINS`. Corrige 2026-03-22. |
| `docs/01-GUIDES/MAINTENANCE.md` | ~~A_CORRIGER~~ **CORRIGE** | Version 1.1.0, date mars 2026, titres sans emoji (convention doc). Corrige 2026-03-06. |
| `docs/01-GUIDES/CONTRIBUTING.md` | ~~NON_VERIFIE~~ **CORRIGE** | Workflow Git aligne sur `master` + `feat/*` / `codex/*`, checks frontend confirmes (`lint:ci`, `test`). Controle 2026-03-23. |
| `docs/01-GUIDES/CONFIGURER_EMAIL.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/CREATE_TEST_DATABASE.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/QU_EST_CE_QUE_VENV.md` | ~~STALE~~ **CORRIGE** | ~~`fastapi 0.121.0`~~ → `starlette 0.52.1` dans les exemples d'arbres venv ; `pip install loguru fastapi` → `pip install loguru starlette`. Corrigé 2026-03-23. |
| `docs/01-GUIDES/LANCER_SERVEUR_TEST.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/SENTRY_MONITORING.md` | OK | Controle 2026-03-23 : fichiers de config Sentry, tunnel `/monitoring`, `request_id`, route `frontend/app/api/sentry-status/route.ts` et variables d'env coherents avec le runtime actuel. |
| `docs/01-GUIDES/ESLINT_PRETTIER_FRONTEND.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/TESTER_MODIFICATIONS_SECURITE.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/01-GUIDES/GUIDE_UTILISATEUR_MVP.md` | NON_VERIFIE | Non parcouru en detail dans cet audit. |
| `docs/02-FEATURES/README.md` | OK | Index clair et correctement tenu. |
| `docs/02-FEATURES/API_QUICK_REFERENCE.md` | ~~A_CORRIGER~~ **CORRIGE** | Section **Gamification (points ledger)** : `point_events` / `apply_points` serveur uniquement, exposition via `/me` et `/api/badges/stats`. Corrige 2026-03-06. |
| `docs/02-FEATURES/AUTH_FLOW.md` | ~~A_CORRIGER~~ **CORRIGE** | ~~`app/services/auth_*.py`~~ → `app/services/auth/auth_*.py` (3 chemins corriges). Corrige 2026-03-22. |
| `docs/02-FEATURES/CHALLENGE_CONTRACT_IA9.md` | OK | Contenu correct et compact. |
| `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` | ~~A_CORRIGER~~ **CORRIGE** | ~~Artefacts d'encodage mojibake generalisés.~~ 1133 sequences double-encodees corrigees (UTF-8/CP1252). Corrige 2026-03-22. |
| `docs/02-FEATURES/F02_DEFIS_QUOTIDIENS.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/02-FEATURES/F03_DIAGNOSTIC_INITIAL.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/02-FEATURES/F04_REVISIONS_ESPACEES.md` | OK | Marque "future spec" dans le README features. |
| `docs/02-FEATURES/F05_ADAPTATION_DYNAMIQUE.md` | ~~A_CORRIGER~~ **CORRIGE** | Fichier re-encode en UTF-8 (mojibake supprime). Corrige 2026-03-06. |
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
| `docs/03-PROJECT/CICD_DEPLOY.md` | OK | Controle 2026-03-23 : workflow `.github/workflows/tests.yml`, jobs backend/lint/frontend, smoke `/health` et gates de reference conformes. |
| `docs/03-PROJECT/evaluation/AI_GENERATION_HARNESS.md` | NON_VERIFIE | Non relu dans ce passage. |
| `docs/04-FRONTEND/ARCHITECTURE.md` | ~~A_CORRIGER~~ **CORRIGE** | ~~`NEXT_PUBLIC_API_URL`~~ → `NEXT_PUBLIC_API_BASE_URL` dans la section Variables d'environnement. Corrige 2026-03-22. |
| `docs/04-FRONTEND/DESIGN_SYSTEM.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/04-FRONTEND/ACCESSIBILITY.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/04-FRONTEND/ANIMATIONS.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/04-FRONTEND/PWA.md` | NON_VERIFIE | Non parcouru en detail. |
| `docs/04-FRONTEND/DASHBOARD_WIDGETS/` (canonique) + `docs/06-WIDGETS/` (redirects legacy) | ~~NON_VERIFIE~~ **VERIFIE** | Controle 2026-03-23 : les docs widgets sont maintenant rangees sous `04-FRONTEND/DASHBOARD_WIDGETS/`; `06-WIDGETS/` ne sert plus que de redirection de compatibilite. |
| `README.md` (racine) | OK | A jour, version `3.3.0-alpha.1`, stack Starlette correctement citee. |
| `README_TECH.md` | OK | A jour, contenu technique correct. |
| `frontend/README.md` | ~~A_CORRIGER~~ **CORRIGE** | Version `3.3.0-alpha.1`, statut alpha explicite, `NEXT_PUBLIC_API_BASE_URL` en local/production/checklist, date MAJ. Corrigé 2026-03-23. |
| `frontend/TROUBLESHOOTING.md` | ~~A_CORRIGER~~ **CORRIGE** | En-tete date + renvoi doc backend ; deja conforme sur CORS / `NEXT_PUBLIC_API_BASE_URL`. Corrige 2026-03-06. |

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

### ~~P3~~ ✅ CORRIGE — `docs/01-GUIDES/TESTING.md`

| # | Nature | Etat |
|---|---|---|
| 1 | Baseline R7 (`991 passed, 2 skipped`) + conservation baseline I (`962 passed`) en historique | **Corrige** 2026-03-06 |

### ~~P4~~ ✅ CORRIGE — `docs/01-GUIDES/QU_EST_CE_QUE_VENV.md`

| # | Ligne approx. | Nature | Etat |
|---|---|---|---|
| 1 | 29, 46, 79, 126 | `fastapi 0.121.0` / exemples `fastapi` dans les arbres et commandes venv | **Corrigé** → `starlette 0.52.1` / `pip install loguru starlette` (2026-03-23) |

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

### ~~P8~~ ✅ CORRIGE — `frontend/README.md`

| # | Nature | Etat |
|---|---|---|
| 1–4 | Version `3.3.0-alpha.1`, statut alpha, `NEXT_PUBLIC_API_BASE_URL` (local, prod, checklist), date MAJ | **Corrigé** 2026-03-23 |

### ~~P9~~ ✅ CORRIGE — `docs/02-FEATURES/API_QUICK_REFERENCE.md`

| # | Nature | Etat |
|---|---|---|
| 1 | Section **Gamification (points ledger)** : `point_events` / `apply_points` (serveur), exposition `/me` + `/api/badges/stats`, renvoi backlog F38 | **Corrige** 2026-03-06 |

---

## 4. Coherence avec la stack reelle

### Conformites verifiees

| Aspect | Etat |
|---|---|
| Backend cite comme Starlette (pas FastAPI) dans les docs actifs | Conforme |
| Routes actives dans `server/routes/` (pas `app/api/endpoints/`) | Conforme |
| JWT access 15min + refresh 7j | Conforme (`AUTH_FLOW.md`) |
| Redis requis en production | Conforme (`DEPLOYMENT_ENV.md`, `ARCHITECTURE.md`) |
| Gamification : ledger `point_events` + badges + `jedi_rank` | Conforme (`API_QUICK_REFERENCE.md` § Gamification + `/me` ; ledger documente comme serveur-only) |
| SSE migre GET -> POST | Conforme (`API_QUICK_REFERENCE.md`, sections exercices et defis) |
| Gouvernance modeles : `app_model_policy.py` + `ai_workload_keys.py` | Conforme (`AI_MODEL_GOVERNANCE.md`) |

### Non-conformites actives (apres corrections 2026-03-06)

Aucune non-conformite **factuelle** restante parmi les points P3/P8/P9/ENV/MAINTENANCE/F05/TROUBLESHOOTING_FRONT listes dans cet audit.

> **Resolues le 2026-03-22 :** `ALLOWED_ORIGINS` (×2), `app/services/auth_*.py` (×3), `NEXT_PUBLIC_API_URL` dans `04-FRONTEND/ARCHITECTURE.md`, `fastapi 0.121.0` dans `QU_EST_CE_QUE_VENV.md`.  
> **Resolues le 2026-03-06 :** `TESTING.md` (R7), `ENV_CHECK.md`, `API_QUICK_REFERENCE.md` (gamification), `MAINTENANCE.md`, `F05_ADAPTATION_DYNAMIQUE.md`, `frontend/README.md`, `frontend/TROUBLESHOOTING.md`.

### Artefacts stale (suivi)

| Document | Artefact |
|---|---|
| *(aucun parmi les lignes ci-dessus encore ouvert)* | — |

> **Resolus le 2026-03-22 :** version `3.1.0-alpha.8` dans `GETTING_STARTED.md`, mojibake `ROADMAP_FONCTIONNALITES.md` (1133 sequences).  
> **Resolus le 2026-03-06 :** stales `frontend/README`, `TESTING` baseline, `MAINTENANCE` date/version, mojibake F05.

---

## 5. Documents manquants prioritaires

| Priorite | Document | Etat au 23/03/2026 |
|---|---|---|
| P1 | `docs/05-ADR/` (dossier ADRs) | **Traite** — dossier cree avec [README](D:/Mathakine/docs/05-ADR/README.md). Le besoin reste ouvert uniquement pour des ADRs supplementaires si de nouvelles decisions structurelles doivent etre formalisees. |
| P2 | Runbook operationnel | **Traite** — [PRODUCTION_RUNBOOK.md](D:/Mathakine/docs/01-GUIDES/PRODUCTION_RUNBOOK.md) couvre demarrage d'urgence, healthchecks, migrations Alembic, rotation `SECRET_KEY`, verifications IA/runtime. |
| P2 | Documentation gamification « longue forme » | **Traite** — [GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md](D:/Mathakine/docs/02-FEATURES/GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md) documente le ledger `point_events`, les ecritures serveur et les surfaces de lecture. |
| P3 | `docs/05-ADR/ADR-001-starlette-vs-fastapi.md` | **Traite** — ADR formel cree et indexe. |

> **Bilan :** les manques prioritaires identifies dans l'audit initial sont maintenant couverts. Les prochains ajouts documentaires relèvent d'un enrichissement de gouvernance, pas d'un trou critique de reference.

---

## 6. Documents a archiver selon la convention

D'apres `CONVENTION_DOCUMENTATION.md`, les documents suivants devraient etre evalues pour archivage :

| Document | Motif | Etat au 23/03/2026 |
|---|---|---|
| `docs/03-PROJECT/CURSOR_MAX_EFFORT_BACKEND_PROTOCOL_2026-03-11.md` | Protocole de validation d'une periode passee | **Conserve en racine** : encore reference par les guides de developpement/contribution et plusieurs notes projet ; archivage premature tant qu'il reste une consigne active. |
| `docs/03-PROJECT/REFACTOR_DASHBOARD_2026-03.md` | Note de refactoring historique | **Traite** — deplace vers [AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/REFACTOR_DASHBOARD_2026-03.md](D:/Mathakine/docs/03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/REFACTOR_DASHBOARD_2026-03.md), avec liens references mis a jour. |
| `docs/01-GUIDES/MAINTENANCE.md` | Guide de maintenance general | **Conserve** — reste utile comme guide general ; [PRODUCTION_RUNBOOK.md](D:/Mathakine/docs/01-GUIDES/PRODUCTION_RUNBOOK.md) couvre le besoin incident/urgence plus specifique. |

> **Bilan :** le seul archivage concret a effectuer dans ce cycle etait la note `REFACTOR_DASHBOARD_2026-03.md`; il est desormais realise.

---

## 7. Bilan par dossier

| Dossier | Situation au 23/03/2026 | Note |
|---|---|---|
| `docs/00-REFERENCE/` | **Stabilise** | Nouveau pivot [AI_MODEL_GOVERNANCE.md](D:/Mathakine/docs/00-REFERENCE/AI_MODEL_GOVERNANCE.md) + nouveau dossier [05-ADR](D:/Mathakine/docs/05-ADR/README.md) pour les decisions formelles. |
| `docs/01-GUIDES/` | **Ameliore** | `ENV_CHECK`, `TESTING`, `MAINTENANCE`, `QU_EST_CE_QUE_VENV` corriges ; [PRODUCTION_RUNBOOK.md](D:/Mathakine/docs/01-GUIDES/PRODUCTION_RUNBOOK.md) ajoute. Plusieurs guides restent `NON_VERIFIE`. |
| `docs/02-FEATURES/` | **Ameliore** | `API_QUICK_REFERENCE`, `AUTH_FLOW`, `ROADMAP_FONCTIONNALITES`, `F05` corriges ; [GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md](D:/Mathakine/docs/02-FEATURES/GAMIFICATION_LEDGER_AND_ACCOUNT_PROGRESS.md) ajoute. |
| `docs/03-PROJECT/` | **Clarifie** | Les snapshots historiques sont marques, la note dashboard a ete archivee, et le pilotage IA renvoie vers la gouvernance active. |
| `docs/04-FRONTEND/` | **A jour sur les references clefs** | `ARCHITECTURE.md` corrige pour `NEXT_PUBLIC_API_BASE_URL`. Les autres docs frontend restent hors perimetre de verification detaillee. |
| `docs/04-FRONTEND/DASHBOARD_WIDGETS/` | **Verifie sur les points critiques** | Endpoints dashboard, widgets actifs et references internes controles ; c est maintenant l emplacement canonique de cette documentation. |
| Racine + `frontend/` | **A jour sur les points critiques** | `README.md`, `README_TECH.md`, `frontend/README.md`, `frontend/TROUBLESHOOTING.md` sont coherents avec la version et les variables d'env actuelles. |

> **Lecture correcte :** le tableau quantitatif de l'audit initial n'est plus la meilleure representation depuis les ajouts documentaires du 23/03/2026. Cette section sert maintenant de bilan qualitatif consolide.

---

## 8. Prochaines actions suggérées (hors scope audit initial)

| Priorité | Action |
|----------|--------|
| P1 | Parcourir les guides **NON_VERIFIE** restants du §2 au fil des besoins (email, create test DB, lancer serveur test, sécurité, certains docs frontend secondaires, harness) et fermer progressivement ces lignes. |
| P2 | Ajouter de nouveaux ADRs uniquement si une decision durable le justifie vraiment (ex. chat public sans auth, absence de `with_for_update` dans le ledger, layering des policies IA). |
| P3 | Completer le runbook et la doc gamification au fil des incidents ou evolutions produit reelles, plutot que d'anticiper abstraitement des sections inutiles. |




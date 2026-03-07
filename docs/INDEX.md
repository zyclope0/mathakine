# 📚 Documentation Mathakine

> Point d'entrée unique — Mise à jour au 07/03/2026  
> **Convention :** [CONVENTION_DOCUMENTATION.md](CONVENTION_DOCUMENTATION.md) — inclut la **revue trimestrielle** (vérité terrain) §7

---

## 🚀 Démarrage rapide

**Nouveau sur le projet ?** Commencez par ces 3 documents dans l'ordre :

1. **[README.md](../README.md)** (racine) - Vue d'ensemble et installation
2. **[README_TECH.md](../README_TECH.md)** (racine) - Documentation technique complète
3. **[GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md)** - Installation pas-à-pas

---

## 📁 Structure de la documentation

```
docs/
├── 00-REFERENCE/          # 📘 Référence technique
│   └── GETTING_STARTED.md      # Installation et premiers pas
│
├── 01-GUIDES/             # 📗 Guides pratiques
│   ├── DEVELOPMENT.md          # Workflow développement
│   ├── TESTING.md              # Tests (pytest, vitest, playwright)
│   ├── TROUBLESHOOTING.md      # Dépannage
│   ├── MAINTENANCE.md          # Maintenance
│   ├── CONTRIBUTING.md         # Comment contribuer
│   ├── CREATE_TEST_DATABASE.md # Créer base de test
│   ├── CONFIGURER_EMAIL.md     # Configurer envoi emails (forgot-password, verify-email)
│   ├── DEPLOYMENT_ENV.md       # Variables d'environnement Render (prod)
│   ├── ENV_CHECK.md            # Checklist .env et Render (dev local)
│   ├── LANCER_SERVEUR_TEST.md  # Lancer serveur local
│   ├── TESTER_MODIFICATIONS_SECURITE.md  # Tests sécurité
│   ├── QU_EST_CE_QUE_VENV.md   # Guide Python venv
│   ├── GUIDE_UTILISATEUR_MVP.md  # Guide utilisateur (cible, rétention, parcours)
│   ├── ESLINT_PRETTIER_FRONTEND.md  # ESLint + Prettier
│   └── SENTRY_MONITORING.md  # Monitoring Sentry
│
├── 02-FEATURES/           # 📙 Fonctionnalités
│   ├── ROADMAP_FONCTIONNALITES.md  # ⭐ BACKLOG & PRIORISATION (document vivant — source de vérité)
│   ├── F02_DEFIS_QUOTIDIENS.md     # Référence F02 : défis quotidiens, flux transactionnels clarifiés
│   ├── BADGES_AMELIORATIONS.md    # Fondements psychologiques badges + backlog améliorations
│   ├── ANALYTICS_PROGRESSION.md  # Spécifications graphiques de progression (futures)
│   ├── WORKFLOW_EDUCATION_REFACTORING.md # Workflow utilisateur + éducation (référence)
│   ├── NIVEAUX_DIFFICULTE_NORMALISATION.md # Feature : sortir de la nomenclature Star Wars
│   ├── AUTH_FLOW.md              # Référence : flux auth complet
│   ├── ADMIN_ESPACE_PROPOSITION.md # Référence : périmètre et benchmark admin
│   ├── ADMIN_FEATURE_SECURITE.md  # Référence : RBAC (require_admin, rôles)
│   ├── API_QUICK_REFERENCE.md    # Référence : cheat sheet endpoints API
│   ├── EDTECH_ANALYTICS.md       # Référence : analytics EdTech (implémenté)
│   ├── THEMES.md                 # Référence : 7 thèmes visuels, themeStore
│   ├── I18N.md                   # Référence : internationalisation next-intl
│   ├── F03_DIAGNOSTIC_INITIAL.md # Référence F03 : test IRT adaptatif
│   ├── F04_REVISIONS_ESPACEES.md # Spécification F04 (SM-2, non implémenté)
│   └── F05_ADAPTATION_DYNAMIQUE.md # Référence F05 : adaptation difficulté
│   (archivés → 03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/)
│   ├── PLAN_REFONTE_BADGES.md    # Archivé — Lots A-B-C ✅ tous implémentés
│   ├── B4_REFORMULATION_BADGES.md  # Archivé — B4 ✅ implémenté
│   └── SITUATION_FEATURES.md    # Archivé — supersédé par ROADMAP_FONCTIONNALITES.md
│
├── 03-PROJECT/            # 📕 Gestion projet
│   ├── README.md          # ⭐ Index maître audits/rapports
│   ├── REFACTOR_STATUS_2026-02.md  # État refactor + stabilisation pré-backlog (B1/B2/F2 + F1.1/F1.2 traités, F1.3/F1.4 restants)
│   ├── PLAN_STABILISATION_PRE_BACKLOG_2026-03-06.md  # Stabilisation pré-backlog, B1/B2/F2 traités, F1.1/F1.2 faits, validation ciblée verte
│   ├── EVALUATION_PROJET_2026-02-07.md  # Référence actuelle (évaluation factuelle)
│   ├── AUDIT_DASHBOARD_2026-02.md  # Audit dashboard (recos partielles)
│   ├── REFACTOR_DASHBOARD_2026-03.md  # Refactor onglets (Vue d'ensemble, Progression, Mon Profil)
│   ├── AUDIT_ARCHITECTURE_BACKEND_2026-03.md  # Audit architecture SOLID/Clean Code/Industrialisation (22/02)
│   ├── AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md  # Audit backend + plan itérations Dev/Test/Prod
│   ├── AUDIT_SENTRY_2026-02.md  # Configuration Sentry (référence)
│   ├── ANALYSE_DUPLICATION_DRY_2026-02.md  # DRY (~90% traité, vérité terrain 28/02)
│   ├── CICD_DEPLOY.md  # CI/CD, smoke test, migrations, rollback
│   ├── POLITIQUE_REDACTION_LOGS_PII.md  # Règles PII/secrets dans les logs
│   ├── ENDPOINTS_NON_INTEGRES.md  # Endpoints à intégrer
│   └── AUDITS_ET_RAPPORTS_ARCHIVES/  # 📦 Audits implémentés + rapports temporaires
│       ├── PLACEHOLDERS_ET_TODO.md  # Endpoints à implémenter (archivé avec rapports)
│       ├── README.md  # Index du dossier
│       ├── AUDITS_IMPLEMENTES/  # Recos toutes appliquées (Backend Alpha2, Dette qual., etc.)
│       │   ├── INDEX.md  # Index des audits complétés
│       │   ├── CLOTURE_AUDIT_BACKEND_ALPHA2_2026-02-22.md  # Clôture audit Backend Alpha 2 (28/02)
│       │   ├── AUDIT_TECHNIQUE_BACKEND_ALPHA2_2026-02-27.md  # Audit technique factuel
│       │   ├── PRIORISATION_AUDIT_BACKEND_ALPHA2_2026-02-28.md
│       │   ├── CHALLENGE_AUDIT_TECHNIQUE_BACKEND_2026-02-28.md
│       │   ├── AUDIT_SECURITE_APPLICATIVE_2026-02.md  # OWASP (archivé)
│       │   ├── ANALYSE_THEMES_UX_2026-02.md
│       │   ├── CONTRAST_FIXES.md
│       │   ├── THEMES_TEST_RESULTS.md
│       │   ├── REFACTORING_SUMMARY.md
│       │   ├── REMAINING_TASKS.md
│       │   ├── INDEX_DB_MANQUANTS_2026-02-06.md
│       │   └── AUDIT_FINAL_DOCS_GITIGNORE_2026-02-06.md
│       └── RAPPORTS_TEMPORAIRES/  # Rapports situationnels + historique
│           ├── INDEX.md
│           ├── DEPLOIEMENT_2026-02-06.md  # Rapport déploiement 06/02
│           ├── SUIVI_MIGRATION_ALEMBIC_22-02.md  # Récap migration DDL → Alembic
│           ├── BILAN_COMPLET.md  # ⚠️ Historique phases 1-6 (nov. 2025)
│           ├── RAPPORT_VERIFICATION_CHALLENGES.md  # Vérification 29/11/2025
│           ├── PHASES/  # Documentation phases historiques
│           │   ├── RECAP_PHASES.md
│           │   ├── PHASE6_PLAN.md
│           │   └── PHASE6_RESULTAT.md
│           ├── MISSION_COMPLETE_2026-02-06.md
│           ├── RECAP_FINAL_2026-02-06.md
│           ├── RATIONALISATION_DOCS_2026-02-06.md
│           ├── PLAN_ACTION_2026-02-06.md
│           ├── MIGRATION_INDEX_ROLLBACK_PLAN.md
│           ├── COMMIT_FIXES_FRONTEND_2026-02-20.md
│           ├── ANALYSE_GENERATION_IA_EXERCICES.md
│           ├── ANALYSE_GENERATION_IA_CHALLENGES.md
│           ├── ANALYSE_DEPENDABOT_2026-02-20.md
│           ├── SECURITY_AUDIT_REPORT.md
│           ├── BADGES_AUDIT_PAUFINAGE.md
│           ├── REFACTO_*_HANDLERS.md  # Plans complétés
│           ├── *_MIGRATION_ALEMBIC*.md  # Migration DDL → Alembic
│           └── CONTEXTE_PROJET_REEL.md
│
├── 04-FRONTEND/           # 🖥️ Documentation frontend (22/02/2026)
│   ├── ARCHITECTURE.md         # Structure, stack, patterns Next.js
│   ├── DESIGN_SYSTEM.md        # Composants layout standardisés (PageLayout, PageHeader…)
│   ├── ACCESSIBILITY.md        # WCAG 2.1 AAA, 5 modes (Focus TSA/TDAH, contraste…)
│   ├── PWA.md                  # Progressive Web App (manifest, SW, offline)
│   └── ANIMATIONS.md           # Composants spatiaux (Starfield, Planet, Particles…)
│
└── 06-WIDGETS/            # 🎨 Widgets Dashboard (Nouveau 06/02/2026)
    ├── INTEGRATION_PROGRESSION_WIDGETS.md  # Guide d'intégration
    ├── ENDPOINTS_PROGRESSION.md            # API endpoints utilisés
    ├── DESIGN_SYSTEM_WIDGETS.md            # Design system et patterns
    └── CORRECTIONS_WIDGETS.md              # Corrections appliquées
```

---

## 🎯 Navigation par besoin

### Je veux démarrer le projet
1. [README.md](../README.md) - Installation rapide
2. [GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md) - Pas-à-pas détaillé
3. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md) - Workflow dev

### Je veux travailler sur le frontend
1. [ARCHITECTURE.md](04-FRONTEND/ARCHITECTURE.md) - Stack, routes, composants, hooks
2. [DESIGN_SYSTEM.md](04-FRONTEND/DESIGN_SYSTEM.md) - Composants standardisés, patterns de page
3. [ACCESSIBILITY.md](04-FRONTEND/ACCESSIBILITY.md) - WCAG AAA, modes accessibilité
4. [PWA.md](04-FRONTEND/PWA.md) - Progressive Web App
5. [ANIMATIONS.md](04-FRONTEND/ANIMATIONS.md) - Composants spatiaux

### Je veux comprendre l'architecture
1. **[README_TECH.md](../README_TECH.md)** ⭐ - **Document de référence unique**
   - Stack technique
   - Architecture backend (Starlette)
   - Architecture frontend (Next.js 16)
   - voir server/routes/ (get_routes())
   - Modèles de données
   - Génération IA (OpenAI)

### Je veux développer une fonctionnalité
1. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md) - Conventions et workflow
2. [README_TECH.md](../README_TECH.md) - API et patterns
3. [ROADMAP_FONCTIONNALITES.md](02-FEATURES/ROADMAP_FONCTIONNALITES.md) - Backlog & priorités (source de vérité)
4. [02-FEATURES/](02-FEATURES/) - Docs fonctionnalités existantes
5. [F03_DIAGNOSTIC_INITIAL.md](02-FEATURES/F03_DIAGNOSTIC_INITIAL.md) - Référence F03 (test IRT adaptatif, diagnostic_results)
6. [F04_REVISIONS_ESPACEES.md](02-FEATURES/F04_REVISIONS_ESPACEES.md) - Spécification F04 (SM-2, non implémenté)
7. [F05_ADAPTATION_DYNAMIQUE.md](02-FEATURES/F05_ADAPTATION_DYNAMIQUE.md) - Référence F05 (adaptation difficulté, IRT, QCM vs saisie libre)

### Je veux créer un nouveau widget dashboard
1. [DESIGN_SYSTEM_WIDGETS.md](06-WIDGETS/DESIGN_SYSTEM_WIDGETS.md) - Template et patterns
2. [INTEGRATION_PROGRESSION_WIDGETS.md](06-WIDGETS/INTEGRATION_PROGRESSION_WIDGETS.md) - Exemple complet

### Je veux accéder à l'espace admin
1. [ADMIN_ESPACE_PROPOSITION.md](02-FEATURES/ADMIN_ESPACE_PROPOSITION.md) — Périmètre, itérations, vision
2. [ADMIN_FEATURE_SECURITE.md](02-FEATURES/ADMIN_FEATURE_SECURITE.md) — RBAC, décorateurs
3. [API_QUICK_REFERENCE.md](02-FEATURES/API_QUICK_REFERENCE.md) — Section Admin (25 endpoints)

### Je veux déployer ou gérer CI/CD
1. [CICD_DEPLOY.md](03-PROJECT/CICD_DEPLOY.md) - CI automatique, smoke test /health, migrations, rollback manuel
2. [DEPLOYMENT_ENV.md](01-GUIDES/DEPLOYMENT_ENV.md) - Variables d'environnement Render (prod)
3. [ENV_CHECK.md](01-GUIDES/ENV_CHECK.md) - Checklist .env et Render (dev local)

### Je veux consulter l'état du refactor
1. [AUDIT_ARCHITECTURE_BACKEND_2026-03.md](03-PROJECT/AUDIT_ARCHITECTURE_BACKEND_2026-03.md) — Audit SOLID/Clean Code 5 phases (22/02)
2. [REFACTOR_STATUS_2026-02.md](03-PROJECT/REFACTOR_STATUS_2026-02.md) — État Clean Code P1–P3 + Architecture Ph1–Ph3
3. [PLAN_CLEAN_CODE_ET_DTO](03-PROJECT/PLAN_CLEAN_CODE_ET_DTO_2026-02.md) — Détail DTO, exceptions, typage
4. [PLAN_REFACTO_ARCHITECTURE](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/PLAN_REFACTO_ARCHITECTURE_2026-02.md) — Phases routes, handlers, services

### Je veux consulter des audits/rapports
1. [03-PROJECT — Index maître](03-PROJECT/README.md) - Taxonomie audits, recommandations, rapports
2. [AUDITS_ET_RAPPORTS_ARCHIVES](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/README.md) - Audits implémentés + rapports situationnels

### Je veux tester mes modifications
1. [TESTING.md](01-GUIDES/TESTING.md) - Guide tests complet
2. [TESTER_MODIFICATIONS_SECURITE.md](01-GUIDES/TESTER_MODIFICATIONS_SECURITE.md) - Tests sécurité
3. [AUDIT_SECURITE_APPLICATIVE_2026-02.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/AUDIT_SECURITE_APPLICATIVE_2026-02.md) - Audit OWASP (archivé, recos appliquées)

### J'ai un problème
1. [TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md) - Solutions problèmes courants
2. [README_TECH.md](../README_TECH.md) - Section "Incohérences résolues"

### Je veux contribuer
1. [CONTRIBUTING.md](01-GUIDES/CONTRIBUTING.md) - Workflow contribution
2. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md) - Standards et conventions

### Je suis parent ou utilisateur final
1. **[/docs](https://mathakine.fun/docs)** (sur le site) — Guide d'utilisation intégré (parcours, FAQ, accessibilité)
2. **[GUIDE_UTILISATEUR_MVP.md](01-GUIDES/GUIDE_UTILISATEUR_MVP.md)** — Source détaillée (personas, analyse psychologique, rétention)

---

## 📊 Documents par priorité

### 🔴 Priorité HAUTE (lecture obligatoire)
- [README.md](../README.md) - Point d'entrée
- **[README_TECH.md](../README_TECH.md)** ⭐ - **Référence technique unique**
- [GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md) - Installation

### 🟡 Priorité MOYENNE (recommandé)
- [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md) - Workflow dev
- [TESTING.md](01-GUIDES/TESTING.md) - Tests
- [TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md) - Dépannage

### 🟢 Priorité BASSE (selon besoin)
- [02-FEATURES/](02-FEATURES/) - Fonctionnalités spécifiques
- [03-PROJECT/](03-PROJECT/) - Historique projet
- [06-WIDGETS/](06-WIDGETS/) - Design system widgets

---

## 📝 Principes de documentation

### Document unique de référence
**README_TECH.md** est le **document de référence unique** pour toute la partie technique :
- Architecture backend et frontend
- API (voir server/routes/)
- Modèles de données
- Stack technique
- Conventions de code
- Incohérences connues

**Tous les autres documents** sont des **guides pratiques** ou des **documentations de fonctionnalités spécifiques**.

### Pas de duplication
- ✅ Une seule source de vérité par sujet
- ✅ Les guides renvoient vers README_TECH.md
- ✅ Pas de copie/coller entre documents

### Documentation vivante
- ✅ Mise à jour à chaque changement majeur
- ✅ Date de dernière mise à jour visible
- ✅ Suppression des informations obsolètes

---

## 🔄 Dernières mises à jour

### 07/03/2026 — F33 Growth Mindset implémenté + backlog mis à jour
- 📝 **[ROADMAP_FONCTIONNALITES.md](02-FEATURES/ROADMAP_FONCTIONNALITES.md)** — F33 marqué ✅ implémenté (matrice, section F33, historique des features)
- 🧩 **Implémentation frontend** — feedback d’échec harmonisé (Exercise/Modal/Challenge/Diagnostic) + composant partagé `GrowthMindsetHint` (industrialisation/no-DRY)
- 📝 **Backlog sécurité** — F35 conservé en P2 (redaction secrets logs DB, non implémenté)

### 06/03/2026 — F02 Défis quotidiens + Refactor Dashboard + Documentation
- 📙 **[F02_DEFIS_QUOTIDIENS.md](02-FEATURES/F02_DEFIS_QUOTIDIENS.md)** — Référence F02 : modèle, API, service, câblage progression
- 📙 **[F02_DAILY_CHALLENGES_WIDGET.md](06-WIDGETS/F02_DAILY_CHALLENGES_WIDGET.md)** — Widget DailyChallengesWidget, design Anti-Cheap
- 📕 **[REFACTOR_DASHBOARD_2026-03.md](03-PROJECT/REFACTOR_DASHBOARD_2026-03.md)** — Réorganisation onglets : Vue d'ensemble (Défis+Série), Progression (4 graphiques), Mon Profil (Niveau, badges, stats, tempo, journal)
- 📝 **INTEGRATION_PROGRESSION_WIDGETS** — Structure actuelle, DailyChallengesWidget, Leaderboard retiré
- 📝 **ROADMAP_FONCTIONNALITES** — F02 marqué implémenté
- 📝 **API_QUICK_REFERENCE** — Section Daily Challenges (F02)
- 📝 **ENDPOINTS_PROGRESSION** — GET /api/daily-challenges
- 📝 **INDEX** — F02, REFACTOR_DASHBOARD, F02_DAILY_CHALLENGES_WIDGET

### 06/03/2026 — Documentation F03, F04, F05 + audit cohérence docs
- 📙 **[F03_DIAGNOSTIC_INITIAL.md](02-FEATURES/F03_DIAGNOSTIC_INITIAL.md)** — Référence F03 : algorithme IRT adaptatif, table `diagnostic_results`, endpoints, intégration F05
- 📙 **[F04_REVISIONS_ESPACEES.md](02-FEATURES/F04_REVISIONS_ESPACEES.md)** — Spécification F04 (SM-2, non implémenté) : modèle de données, intégration prévue
- 📙 **[F05_ADAPTATION_DYNAMIQUE.md](02-FEATURES/F05_ADAPTATION_DYNAMIQUE.md)** — Référence F05 : cascade IRT, proxys MIXTE/FRACTIONS, mode QCM vs saisie libre
- 📝 **ROADMAP_FONCTIONNALITES** — Liens vers F03, F04, F05 ; F05 corrigé (is_open_answer côté frontend)
- 📝 **WORKFLOW_EDUCATION** — F03 et F05 marqués implémentés
- 📝 **06-WIDGETS** — LevelEstablishedWidget documenté
- 📝 **API_QUICK_REFERENCE** — Section Diagnostic (F03), lien PLACEHOLDERS corrigé
- 📝 **INDEX** — Numérotation refactor corrigée (1–4), structure 02-FEATURES (F03/F04/F05), PLACEHOLDERS dans arborescence, lien AUDIT_DETTE_QUALITE
- 📝 **ENDPOINTS_NON_INTEGRES** — Section Diagnostic intégré, date 06/03

### 03/03/2026 — Audit architecture backend
- 📐 **[AUDIT_ARCHITECTURE_BACKEND_2026-03.md](03-PROJECT/AUDIT_ARCHITECTURE_BACKEND_2026-03.md)** — Audit complet SOLID, Clean Code, performances, sécurité, industrialisation. 36 constats (4 critiques, 10 high). Plan 5 phases priorisé (~15 jours). Complémentaire à l'audit Cleanup du 01/03.

### 28/02/2026 — Refactor + documentation alignée
- 📐 **Refactor terminé** : Clean Code P1–P3, Architecture Ph1–Ph3. Voir [REFACTOR_STATUS_2026-02.md](03-PROJECT/REFACTOR_STATUS_2026-02.md).
- 📝 **Documentation alignée** : Toutes les refs `server/routes.py` → `server/routes/`. README_TECH, INDEX, DEVELOPMENT, CONVENTION, TROUBLESHOOTING, etc.
- 📝 **ANALYSE_DUPLICATION_DRY** : P3 exceptions et SubmitAnswerResponse ajoutés aux réalisations.

### 15/02/2026 — Documentation (mise en ordre)
- 📁 **Réorganisation** : DEPLOIEMENT et SUIVI_MIGRATION → RAPPORTS_TEMPORAIRES ; ENV_CHECK → 01-GUIDES ; CICD_DEPLOY, POLITIQUE_REDACTION_LOGS_PII dans README 03-PROJECT.
- 📝 **CICD_DEPLOY.md** : CI automatique, smoke test /health, migrations, rollback. [Lire →](03-PROJECT/CICD_DEPLOY.md)

### 15/02/2026 (qualité frontend)
- ✅ **Refactor qualité** : Typage TypeScript strict sur tous les renderers de visualisation (ChessRenderer, CodingRenderer, DeductionRenderer, GraphRenderer, etc.), useAccessibleAnimation (Variants/Transition), validation dashboard, vitest.setup. Exclusion `scripts/` du lint.
- ✅ **Build + tests unitaires** : 31 tests Vitest OK (dont 11 sur safeValidateUserStats). E2E : `npx playwright install` requis.
- 📝 **TESTING.md** : Section « Priorités de couverture frontend » + tests régression dashboard. [Lire →](01-GUIDES/TESTING.md#priorites-couverture)
- 📝 **AUDIT_DETTE_QUALITE_FRONTEND** : Section « Corrections appliquées » documentée. [Lire →](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/AUDIT_DETTE_QUALITE_FRONTEND_2026-02-20.md)

### 18/02/2026
- 📄 **POINT_SITUATION_2026-02-18.md** — Bilan projet (fonctionnalités, priorités, références). [Lire →](03-PROJECT/POINT_SITUATION_2026-02-18.md)
- ✅ **Badges — Finalisation** : Fix N+1 sur `/api/challenges/badges/progress` (stats_cache pré-fetch, ~12 requêtes fixes). Filtre « Proches (>50%) » visible uniquement sur onglet À débloquer. Script `scripts/delete_test_badges.py` pour hard delete badges test.
- 📝 **Docs** : PLAN_REFONTE_BADGES (§ 10 post-livraison), SITUATION_FEATURES (badges finalisés), nettoyage fichiers temporaires.

### 17/02/2026
- ✅ **Badges B4** : Reformulation 17 badges (name, description, star_wars_title, catégories, points). Script `scripts/update_badges_b4.py`. Contexte challenge documenté dans B4_REFORMULATION_BADGES.
- ✅ **Badges psycho/rétention** : 12 badges add_badges_psycho + 3 add_badges_recommandations (guardian_150, marathon, comeback). **32 badges**, 4 secrets. Vigilance 35–40 max.
- ✅ **Badges Lot C-1** : Moteur générique `badge_requirement_engine.py` (registry 10 types), refactor `_check_badge_requirements`. Terrain B5 : checkers `logic_attempts_count`, `mixte` ; validation admin ; BadgeCreateModal/BadgeEditModal exemples défis/mixte ; `submit_challenge_answer` appelle `check_and_award_badges`.
- ✅ **Badges Lot C-2** : `get_requirement_progress` (10 types) dans engine, refactor `_get_badge_progress`. Tests `test_badge_requirement_engine.py`.
- ✅ **Badges Lot B-5** : Goal-gradient (« Plus que X »), loss aversion (« Tu approches »), champ icon_url admin (emoji/URL), BadgeCard affiche icon_url, principes psychologiques enrichis, audit nombre badges § 5.3.3.

### 16/02/2026
- ✅ **Quick wins 1-4** : (1) maintenance_mode + registration_enabled appliqués, (2) handle_recommendation_complete, (3) get_user_badges_progress, (4) is_current dans /api/users/me/sessions
- ✅ **Admin — Paramètres globaux** : page `/admin/config`, `GET/PUT /api/admin/config`, paramètres maintenance, inscriptions, feature flags, limites (table `settings`)
- ✅ **Admin — Fix** : normalisation booléens (is_archived, is_active) dans PUT exercices/challenges
- 📝 **Docs** : ADMIN_ESPACE_PROPOSITION (itération 14), API_QUICK_REFERENCE (25 routes admin), ENDPOINTS_NON_INTEGRES (section Admin)
- 📝 **Mise à jour docs suite implémentations** : README_TECH (API, hooks, maintenance, sessions), AUTH_FLOW (sessions, maintenance, registration_enabled), ROADMAP_FONCTIONNALITES (endpoints 16/02), INTEGRATION_PROGRESSION_WIDGETS (Recommendations complete)

### 15/02/2026 (features)
- ✅ **Leaderboard** : `GET /api/users/leaderboard`, page `/leaderboard`, widget top 5 sur dashboard Vue d'ensemble
- ✅ **Dashboard réorganisé** : Vue d'ensemble allégée (KPIs + streak + classement), Progression (défis + précision + graphiques), Détails (performance + activité), timestamp relatif formaté
- ✅ **Prompt IA fractions** : Règles renforcées (moitié/tiers cohérents, pas d'erreur fictive)
- 📝 **ROADMAP_FONCTIONNALITES** : Leaderboard et Streak marqués implémentés
- 📝 **ENDPOINTS_NON_INTEGRES** : Leaderboard, PUT /api/users/me et /password documentés
- 📝 **06-WIDGETS** : LeaderboardWidget ajouté à INTEGRATION_PROGRESSION_WIDGETS

### 15/02/2026
- 📙 **02-FEATURES** : API_QUICK_REFERENCE (cheat sheet endpoints), AUTH_FLOW (flux inscription/login/reset), THEMES (7 thèmes, themeStore, ajout)
- 📁 **Réorganisation docs** : Audits implémentés regroupés dans `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/` — ajout de CONTRAST_FIXES, THEMES_TEST_RESULTS, REFACTORING_SUMMARY, REMAINING_TASKS (ex-frontend/docs)
- 📝 **AUDITS_IMPLEMENTES/INDEX.md** : Index des 7 documents d'audits complétés

### 15/02/2026 (soir)
- 🎨 **Thèmes** : 7 thèmes (Dune, Forêt, Lumière, Dinosaures) — ANALYSE_THEMES_UX et THEMES_TEST_RESULTS mis à jour
- 📐 **Standardisation docs** : En-têtes harmonisés (Date, Type, Statut), CONVENTION enrichie, taxonomie clarifiée
- 📁 **Documentation projet** : 03-PROJECT/README.md (index maître), CONVENTION_DOCUMENTATION.md, standardisation audits/rapports

### 12/02/2026
- ✅ **Énigmes (RiddleRenderer)** : Rendu correct des champs `pots` et `plaque` (plus de JSON brut), masquage de l’ascii_art redondant
- ✅ **Échecs (ChessRenderer)** : Highlights uniquement sur les pièces, affichage tour/objectif (mat en X coups), format de réponse attendu, prompt IA pour positions tactiques réalistes
- ✅ **Auth production (cross-domain)** : await sync au login, `ensureFrontendAuthCookie()` avant génération IA, routes `/api/auth/sync-cookie` et `/api/auth/check-cookie` pour diagnostic
- 📝 **TROUBLESHOOTING.md** : Section « Cookie manquant » en production enrichie

### 03/03/2026 — Audit Architecture Backend (Phases 0→4)
- 🛡️ **Phase 0 — Sécurité** : Bypass CSRF `TESTING` supprimé, injection SQL `safe_delete` bloquée, validation `POSTGRES_PASSWORD` prod, credentials DB masquées dans les logs, `except` inatteignables corrigés.
- 📐 **Phase 1 — Standardisation** : Parsing body unifié (`parse_json_body`), réponses erreur unifiées (`api_error_response`), 26 `traceback.print_exc()` → `logger.error(exc_info=True)`, CORS source unique, CSRF frozenset pré-calculé, `_ROUTE_REGISTRY` central.
- 🔧 **Phase 2 — Services légers** : User lookups centralisés dans `UserService`, `auth_service.py` sans `HTTPException`, `_apply_challenge_filters()` extrait, `queries.py` supprimé (403 lignes dead code), `TypedDict` introduits (`app/core/types.py`).
- 🏗️ **Phase 3 — God objects** : `ChallengeAnswerService` extrait, `ChatService` extrait, `AdminService` → 4 services (`AdminConfigService`, `AdminStatsService`, `AdminUserService`, `AdminContentService`) + façade, `exercise_generator_helpers.py` enrichi.
- 🏭 **Phase 4 — Industrialisation** : TypedDict complets, `constants_challenge.py` extrait, `format_paginated_response` adopté, `enum_mapping.py` adopté, `safe_delete`/`safe_archive` → exceptions (`DatabaseOperationError`).
- 📋 **Référence** : [AUDIT_ARCHITECTURE_BACKEND_2026-03.md](03-PROJECT/AUDIT_ARCHITECTURE_BACKEND_2026-03.md) — 472 tests, 0 failures.

### 27/02/2026
- ✅ **Refactor admin_handlers — AdminService (étape 1)** *(décomposé en 4 services le 03/03/2026 — voir ci-dessus)* : Toute la logique DB déplacée dans `app/services/admin_service.py` (users, badges, exercises, challenges, export CSV). Handlers minces sans requêtes directes. Voir [INVENTAIRE_HANDLERS_DB_DIRECTE](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INVENTAIRE_HANDLERS_DB_DIRECTE.md), [REFACTO_ADMIN_HANDLERS](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/REFACTO_ADMIN_HANDLERS.md).
- ✅ **Fix admin modération** : Bouton « Éditer » ouvre la modal d’édition in-place au lieu de rediriger vers la page Contenu.

### 21/02/2026
- ✅ **Refactor exercise_generator (PR#1)** : Extraction des validateurs dans `server/exercise_generator_validators.py` (normalize_exercise_type, normalize_difficulty, normalize_and_validate_exercise_params, get_difficulty_from_age_group) — compatibilite preservee via re-exports
- ✅ **Refactor exercise_generator (PR#2)** : Extraction des helpers dans `server/exercise_generator_helpers.py` (`generate_smart_choices`) — `generate_contextual_question` supprimée (H9 audit, jamais appelée)
- ✅ **Refactor admin_handlers (PR#1)** : Extraction des utils dans `server/handlers/admin_handlers_utils.py` (CONFIG_SCHEMA, _log_admin_action, _parse_setting_value, _serialize_value)

### 11/02/2026
- ✅ **Documentation tests** : TESTING.md, tests/README.md. CI : test:coverage, Codecov.

### 09/02/2026
- ✅ **Vulnérabilités npm** (3→0), **décorateurs auth** (@require_auth, etc.), **exportExcel** (exceljs).

### 08/02/2026
- ✅ **Dependabot**, **GitHub Actions v6**, **CI fiabilisée**, **tests httpx.AsyncClient**.

### 07/02/2026
- ✅ **Settings page** complète. **EVALUATION_PROJET_2026-02-07.md** — référence qualité.

### 06/02/2026 (soir)
- ✅ **Index DB appliqués** : 13 index de performance créés et déployés
- ✅ **Accessibilité refactorisée** : Toolbar en React Portal (bottom-left)
- ✅ **Fix génération IA** : Authentification exercices + dépendance openai>=1.40.0
- ✅ **Fix dark mode** : Sélecteurs CSS corrigés
- ✅ **Thème simplifié** : Suppression références Star Wars (droits d'auteur)
- ✅ **Fix endpoint stats** : `/api/exercises/stats` avec challenges
- 📝 **ANALYTICS_PROGRESSION.md** : Idées de graphiques de progression

### 06/02/2026 (matin)
- ✅ **Unification Starlette**, **6-WIDGETS/**, **rationalisation docs** (~200 archivés).

*Historique antérieur : voir `git log`.*

---

## 📚 Documents racine (hors docs/)

| Fichier | Description | Statut |
|---------|-------------|--------|
| **README.md** | Point d'entrée projet (français) | ✅ À mettre à jour |
| **README_TECH.md** | Documentation technique complète | ✅ À jour (06/03/2026) |

---

## 🎯 Statistiques

- **Documents actifs** : ~55 docs (guides, features, projet, widgets)
- **Cohérence** : Validée vs code réel — revue trimestrielle (CONVENTION §7)
- **Dernière vérification** : 03/03/2026 (Audit Architecture Phases 0→4, 472 tests)

---

## 💡 Besoin d'aide ?

1. **Question technique** → [README_TECH.md](../README_TECH.md)
2. **Installation** → [GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md)
3. **Problème** → [TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md)
4. **Contribution** → [CONTRIBUTING.md](01-GUIDES/CONTRIBUTING.md)

**Prêt à coder !** 🚀

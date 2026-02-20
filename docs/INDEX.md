# 📚 Documentation Mathakine

> Point d'entrée unique — Mise à jour au 17/02/2026  
> **Convention :** [CONVENTION_DOCUMENTATION.md](CONVENTION_DOCUMENTATION.md)

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
├── 01-GUIDES/             # 📗 Guides pratiques (9 guides)
│   ├── DEVELOPMENT.md          # Workflow développement
│   ├── TESTING.md              # Tests (pytest, vitest, playwright)
│   ├── TROUBLESHOOTING.md      # Dépannage
│   ├── MAINTENANCE.md          # Maintenance
│   ├── CONTRIBUTING.md         # Comment contribuer
│   ├── CREATE_TEST_DATABASE.md # Créer base de test
│   ├── CONFIGURER_EMAIL.md     # Configurer envoi emails (forgot-password, verify-email)
│   ├── LANCER_SERVEUR_TEST.md  # Lancer serveur local
│   ├── TESTER_MODIFICATIONS_SECURITE.md  # Tests sécurité
│   ├── QU_EST_CE_QUE_VENV.md  # Guide Python venv
│   ├── GUIDE_UTILISATEUR_MVP.md  # 🆕 Guide utilisateur (cible, rétention, parcours)
│   ├── ESLINT_PRETTIER_FRONTEND.md  # ESLint + Prettier
│   └── SENTRY_MONITORING.md  # Monitoring Sentry
│
├── 02-FEATURES/           # 📙 Fonctionnalités
│   ├── SITUATION_FEATURES.md     # ⭐ Point de situation + priorités implémentation
│   ├── I18N.md                 # Internationalisation (next-intl)
│   ├── API_QUICK_REFERENCE.md   # Cheat sheet endpoints API
│   ├── AUTH_FLOW.md            # Flux inscription → login → reset password
│   ├── THEMES.md               # 7 thèmes visuels, themeStore, ajout thème
│   ├── ANALYTICS_PROGRESSION.md  # Graphiques progression
│   ├── BADGES_AMELIORATIONS.md   # Roadmap badges (P0 progression implémentée)
│   ├── PLAN_REFONTE_BADGES.md   # Plan refonte + Admin CRUD + Lot C (C-1 fait)
│   ├── B4_REFORMULATION_BADGES.md  # Specs reformulation 17 badges
│   ├── ADMIN_FEATURE_SECURITE.md  # RBAC admin (require_admin)
│   ├── ADMIN_ESPACE_PROPOSITION.md # Proposition espace admin (benchmark, périmètre, plan)
│   └── ROADMAP_FONCTIONNALITES.md # Roadmap globale fonctionnalités
│
├── 03-PROJECT/            # 📕 Gestion projet
│   ├── README.md          # ⭐ Index maître audits/rapports
│   ├── EVALUATION_PROJET_2026-02-07.md  # Référence actuelle (évaluation factuelle)
│   ├── AUDIT_DASHBOARD_2026-02.md  # Audit dashboard (recos partielles)
│   ├── AUDIT_SENTRY_2026-02.md  # Configuration Sentry (référence)
│   ├── AUDIT_SECURITE_APPLICATIVE_2026-02.md  # Audit OWASP (référence)
│   ├── ANALYSE_DUPLICATION_DRY_2026-02.md  # DRY (~70-80% traité)
│   ├── DEPLOIEMENT_2026-02-06.md  # Guide déploiement
│   ├── ENDPOINTS_NON_INTEGRES.md  # Endpoints à intégrer
│   ├── ANALYSE_GENERATION_IA_CHALLENGES.md  # Audit génération IA défis (bugs, optimisations)
│   ├── PLACEHOLDERS_ET_TODO.md  # Endpoints à implémenter
│   └── AUDITS_ET_RAPPORTS_ARCHIVES/  # 📦 Audits implémentés + rapports temporaires
│       ├── README.md  # Index du dossier
│       ├── AUDITS_IMPLEMENTES/  # Recos toutes appliquées
│       │   ├── INDEX.md  # Index des 7 audits
│       │   ├── ANALYSE_THEMES_UX_2026-02.md
│       │   ├── CONTRAST_FIXES.md
│       │   ├── THEMES_TEST_RESULTS.md
│       │   ├── REFACTORING_SUMMARY.md
│       │   ├── REMAINING_TASKS.md
│       │   ├── INDEX_DB_MANQUANTS_2026-02-06.md
│       │   └── AUDIT_FINAL_DOCS_GITIGNORE_2026-02-06.md
│       └── RAPPORTS_TEMPORAIRES/  # Rapports situationnels + historique
│           ├── INDEX.md
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
│           └── MIGRATION_INDEX_ROLLBACK_PLAN.md
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

### Je veux comprendre l'architecture
1. **[README_TECH.md](../README_TECH.md)** ⭐ - **Document de référence unique**
   - Stack technique
   - Architecture backend (Starlette)
   - Architecture frontend (Next.js 16)
   - 86 endpoints API
   - Modèles de données
   - Génération IA (OpenAI)

### Je veux développer une fonctionnalité
1. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md) - Conventions et workflow
2. [README_TECH.md](../README_TECH.md) - API et patterns
3. [SITUATION_FEATURES.md](02-FEATURES/SITUATION_FEATURES.md) - Point de situation + priorités
4. [02-FEATURES/](02-FEATURES/) - Docs fonctionnalités existantes

### Je veux créer un nouveau widget dashboard
1. [DESIGN_SYSTEM_WIDGETS.md](06-WIDGETS/DESIGN_SYSTEM_WIDGETS.md) - Template et patterns
2. [INTEGRATION_PROGRESSION_WIDGETS.md](06-WIDGETS/INTEGRATION_PROGRESSION_WIDGETS.md) - Exemple complet

### Je veux accéder à l'espace admin
1. [ADMIN_ESPACE_PROPOSITION.md](02-FEATURES/ADMIN_ESPACE_PROPOSITION.md) — Périmètre, itérations, vision
2. [ADMIN_FEATURE_SECURITE.md](02-FEATURES/ADMIN_FEATURE_SECURITE.md) — RBAC, décorateurs
3. [API_QUICK_REFERENCE.md](02-FEATURES/API_QUICK_REFERENCE.md) — Section Admin (25 endpoints)

### Je veux consulter des audits/rapports
1. [03-PROJECT — Index maître](03-PROJECT/README.md) - Taxonomie audits, recommandations, rapports
2. [AUDITS_ET_RAPPORTS_ARCHIVES](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/README.md) - Audits implémentés + rapports situationnels

### Je veux tester mes modifications
1. [TESTING.md](01-GUIDES/TESTING.md) - Guide tests complet
2. [TESTER_MODIFICATIONS_SECURITE.md](01-GUIDES/TESTER_MODIFICATIONS_SECURITE.md) - Tests sécurité
3. [AUDIT_SECURITE_APPLICATIVE_2026-02.md](03-PROJECT/AUDIT_SECURITE_APPLICATIVE_2026-02.md) - Audit OWASP (failles, remédiations)

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
- API (86 endpoints)
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

### 11/02/2026
- ✅ **Documentation tests mise à jour** : TESTING.md (Vitest, couverture, CI), tests/README.md, PLAN_TESTS_AMELIORATION.md
- ✅ **Corrections test_user_exercise_flow** : POST /api/exercises/generate, paramètre answer, GET /api/users/stats
- ✅ **Tests frontend** : ExerciseCard (NextIntl + QueryClient wrappers), AccessibilityToolbar (userEvent, aria-label)
- ✅ **CI** : test:coverage frontend avant build, Codecov backend + frontend
- ⚠️ **CORRECTION_PLAN.md** : Marqué obsolète (état Mai 2025)

### 09/02/2026
- ✅ **Vulnerabilites npm corrigees** (3→0) : jspdf mis a jour v4.1.0, xlsx (vulnerable) remplace par exceljs + file-saver
- ✅ **Decorateurs auth** : `@require_auth`, `@optional_auth`, `@require_auth_sse` dans `server/auth.py` - eliminent 40+ blocs d'authentification dupliques dans 6 fichiers handlers
- ✅ **exportExcel.ts** refactorise pour utiliser exceljs au lieu de xlsx
- 📝 **EVALUATION_PROJET** mis a jour avec les actions completees

### 08/02/2026
- ✅ **Dependabot configure** : `.github/dependabot.yml` (GitHub Actions hebdo + npm hebdo, groupement React/Next.js)
- ✅ **GitHub Actions mises a jour** : checkout v6, upload/download-artifact v6/v7, codecov v5, setup-python v6
- ✅ **CI fiabilise** : `continue-on-error: true` retire, Flake8 F821 corrige, test data fixtures corrigees (`age_group` NOT NULL)
- ✅ **Tests backend migres** vers httpx.AsyncClient (Starlette natif, 396 tests collectes)
- ✅ **Dependabot groupement** : React/React-DOM/types groupes pour eviter conflits peer dependencies

### 07/02/2026
- ✅ **Settings page complete** : 5 sections activees (suppression, export, notifications, langue, confidentialite)
- ✅ **Fix SQLAlchemy JSON** : Mutation tracking corrige (dict copy)
- 📝 **EVALUATION_PROJET_2026-02-07.md** : Audit qualite factuel (supersede BILAN_COMPLET.md)

### 06/02/2026 (soir)
- ✅ **Index DB appliqués** : 13 index de performance créés et déployés
- ✅ **Accessibilité refactorisée** : Toolbar en React Portal (bottom-left)
- ✅ **Fix génération IA** : Authentification exercices + dépendance openai>=1.40.0
- ✅ **Fix dark mode** : Sélecteurs CSS corrigés
- ✅ **Thème simplifié** : Suppression références Star Wars (droits d'auteur)
- ✅ **Fix endpoint stats** : `/api/exercises/stats` avec challenges
- 📝 **ANALYTICS_PROGRESSION.md** : Idées de graphiques de progression

### 06/02/2026 (matin)
- ✅ **Unification Starlette** : FastAPI archivé, architecture simplifiée
- ✅ **3 nouveaux widgets dashboard** : Série, Défis, Précision
- ✅ **Documentation rationalisée** : ~200 docs archivés supprimés
- ✅ **README_TECH.md** : Mis à jour pour refléter architecture actuelle
- ✅ **Nouveau dossier 06-WIDGETS/** : Documentation widgets dashboard

### 20/11/2025
- Phase 6 complétée (nommage et lisibilité)
- Documentation phases consolidée

---

## 📚 Documents racine (hors docs/)

| Fichier | Description | Statut |
|---------|-------------|--------|
| **README.md** | Point d'entrée projet (français) | ✅ À mettre à jour |
| **README_TECH.md** | Documentation technique complète | ✅ À jour (06/02/2026) |

---

## 🎯 Statistiques

- **Documents actifs** : ~50 docs (backend, frontend, widgets, projet)
- **Réduction initiale** : -92% de documentation (200+ → ~15 actifs en nov. 2025)
- **Cohérence** : Validee vs code reel
- **Dernière vérification** : 17/02/2026

---

## 💡 Besoin d'aide ?

1. **Question technique** → [README_TECH.md](../README_TECH.md)
2. **Installation** → [GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md)
3. **Problème** → [TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md)
4. **Contribution** → [CONTRIBUTING.md](01-GUIDES/CONTRIBUTING.md)

**Prêt à coder !** 🚀

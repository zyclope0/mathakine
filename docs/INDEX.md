# Ã°Å¸â€œÅ¡ Documentation Mathakine

> Point d'entree unique - Mise a jour au 09/03/2026 (iteration backend `exercise/auth/user` cloturee, archivee et documentee)  
> **Convention :** [CONVENTION_DOCUMENTATION.md](CONVENTION_DOCUMENTATION.md) Ã¢â‚¬â€ inclut la **revue trimestrielle** (vÃƒÂ©ritÃƒÂ© terrain) Ã‚Â§7

---

## Ã°Å¸Å¡â‚¬ DÃƒÂ©marrage rapide

**Nouveau sur le projet ?** Commencez par ces 3 documents dans l'ordre :

1. **[README.md](../README.md)** (racine) - Vue d'ensemble et installation
2. **[README_TECH.md](../README_TECH.md)** (racine) - Documentation technique complÃƒÂ¨te
3. **[GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md)** - Installation pas-ÃƒÂ -pas

---

## Ã°Å¸â€œÂ Structure de la documentation

```
docs/
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ 00-REFERENCE/          # Ã°Å¸â€œËœ RÃƒÂ©fÃƒÂ©rence technique
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ GETTING_STARTED.md      # Installation et premiers pas
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ ARCHITECTURE.md         # Architecture globale (frontend + backend)
Ã¢â€â€š
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ 01-GUIDES/             # Ã°Å¸â€œâ€” Guides pratiques
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ DEVELOPMENT.md          # Workflow dÃƒÂ©veloppement
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ TESTING.md              # Tests (pytest, vitest, playwright)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ TROUBLESHOOTING.md      # DÃƒÂ©pannage
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ MAINTENANCE.md          # Maintenance
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ CONTRIBUTING.md         # Comment contribuer
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ CREATE_TEST_DATABASE.md # CrÃƒÂ©er base de test
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ CONFIGURER_EMAIL.md     # Configurer envoi emails (forgot-password, verify-email)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ DEPLOYMENT_ENV.md       # Variables d'environnement Render (prod)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ENV_CHECK.md            # Checklist .env et Render (dev local)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ LANCER_SERVEUR_TEST.md  # Lancer serveur local
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ TESTER_MODIFICATIONS_SECURITE.md  # Tests sÃƒÂ©curitÃƒÂ©
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ QU_EST_CE_QUE_VENV.md   # Guide Python venv
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ GUIDE_UTILISATEUR_MVP.md  # Guide utilisateur (cible, rÃƒÂ©tention, parcours)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ESLINT_PRETTIER_FRONTEND.md  # ESLint + Prettier
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ SENTRY_MONITORING.md  # Monitoring Sentry
Ã¢â€â€š
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ 02-FEATURES/           # Ã°Å¸â€œâ„¢ FonctionnalitÃƒÂ©s
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ROADMAP_FONCTIONNALITES.md  # Ã¢Â­Â BACKLOG & PRIORISATION (document vivant Ã¢â‚¬â€ source de vÃƒÂ©ritÃƒÂ©)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ F02_DEFIS_QUOTIDIENS.md     # RÃƒÂ©fÃƒÂ©rence F02 : dÃƒÂ©fis quotidiens, flux transactionnels clarifiÃƒÂ©s
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ BADGES_AMELIORATIONS.md    # Fondements psychologiques badges + backlog amÃƒÂ©liorations
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ANALYTICS_PROGRESSION.md  # SpÃƒÂ©cifications graphiques de progression (futures)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ WORKFLOW_EDUCATION_REFACTORING.md # Workflow utilisateur + ÃƒÂ©ducation (rÃƒÂ©fÃƒÂ©rence)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ NIVEAUX_DIFFICULTE_NORMALISATION.md # Feature : sortir de la nomenclature Star Wars
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ AUTH_FLOW.md              # RÃƒÂ©fÃƒÂ©rence : flux auth complet
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ADMIN_ESPACE_PROPOSITION.md # RÃƒÂ©fÃƒÂ©rence : pÃƒÂ©rimÃƒÂ¨tre et benchmark admin
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ADMIN_FEATURE_SECURITE.md  # RÃƒÂ©fÃƒÂ©rence : RBAC (require_admin, rÃƒÂ´les)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ API_QUICK_REFERENCE.md    # RÃƒÂ©fÃƒÂ©rence : cheat sheet endpoints API
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ EDTECH_ANALYTICS.md       # RÃƒÂ©fÃƒÂ©rence : analytics EdTech (implÃƒÂ©mentÃƒÂ©)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ THEMES.md                 # RÃƒÂ©fÃƒÂ©rence : 7 thÃƒÂ¨mes visuels, themeStore
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ I18N.md                   # RÃƒÂ©fÃƒÂ©rence : internationalisation next-intl
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ F03_DIAGNOSTIC_INITIAL.md # RÃƒÂ©fÃƒÂ©rence F03 : test IRT adaptatif
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ F04_REVISIONS_ESPACEES.md # SpÃƒÂ©cification F04 (SM-2, non implÃƒÂ©mentÃƒÂ©)
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ F05_ADAPTATION_DYNAMIQUE.md # RÃƒÂ©fÃƒÂ©rence F05 : adaptation difficultÃƒÂ©
Ã¢â€â€š   (archivÃƒÂ©s Ã¢â€ â€™ 03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ PLAN_REFONTE_BADGES.md    # ArchivÃƒÂ© Ã¢â‚¬â€ Lots A-B-C Ã¢Å“â€¦ tous implÃƒÂ©mentÃƒÂ©s
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ B4_REFORMULATION_BADGES.md  # ArchivÃƒÂ© Ã¢â‚¬â€ B4 Ã¢Å“â€¦ implÃƒÂ©mentÃƒÂ©
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ SITUATION_FEATURES.md    # ArchivÃƒÂ© Ã¢â‚¬â€ supersÃƒÂ©dÃƒÂ© par ROADMAP_FONCTIONNALITES.md
Ã¢â€â€š
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ 03-PROJECT/            # Ã°Å¸â€œâ€¢ Gestion projet
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ README.md          # Ã¢Â­Â Index maÃƒÂ®tre audits/rapports
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ REFACTOR_STATUS_2026-02.md  # Ãƒâ€°tat refactor + stabilisation prÃƒÂ©-backlog (B1/B2/F2 + F1.1/F1.2 traitÃƒÂ©s, F1.3/F1.4 restants)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ PLAN_STABILISATION_PRE_BACKLOG_2026-03-06.md  # Stabilisation prÃƒÂ©-backlog, B1/B2/F2 traitÃƒÂ©s, F1.1/F1.2 faits, validation ciblÃƒÂ©e verte
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ EVALUATION_PROJET_2026-02-07.md  # RÃƒÂ©fÃƒÂ©rence actuelle (ÃƒÂ©valuation factuelle)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ AUDIT_DASHBOARD_2026-02.md  # Audit dashboard (recos partielles)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ REFACTOR_DASHBOARD_2026-03.md  # Refactor onglets (Vue d'ensemble, Progression, Mon Profil)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ AUDIT_ARCHITECTURE_BACKEND_2026-03.md  # Audit architecture SOLID/Clean Code/Industrialisation (22/02)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md  # Audit backend + plan itÃƒÂ©rations Dev/Test/Prod
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ AUDIT_SENTRY_2026-02.md  # Configuration Sentry (rÃƒÂ©fÃƒÂ©rence)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ANALYSE_DUPLICATION_DRY_2026-02.md  # DRY (~90% traitÃƒÂ©, vÃƒÂ©ritÃƒÂ© terrain 28/02)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ CICD_DEPLOY.md  # CI/CD, smoke test, migrations, rollback
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ POLITIQUE_REDACTION_LOGS_PII.md  # RÃƒÂ¨gles PII/secrets dans les logs
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ IMPLEMENTATION_F32_SESSION_ENTRELACEE.md  # Dossier d'implÃƒÂ©mentation F32 (session entrelacÃƒÂ©e)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ IMPLEMENTATION_F35_REDACTION_LOGS_DB.md  # Dossier d'implÃƒÂ©mentation F35 (redaction logs DB)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md  # Bilan final de l'iteration backend cloturee
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ DELTA_RESTANT_POST_ITERATION_BACKEND_2026-03-09.md  # Reliquat rationalise post-iteration
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ENDPOINTS_NON_INTEGRES.md  # Endpoints ÃƒÂ  intÃƒÂ©grer
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ AUDITS_ET_RAPPORTS_ARCHIVES/  # Ã°Å¸â€œÂ¦ Audits implÃƒÂ©mentÃƒÂ©s + rapports temporaires
Ã¢â€â€š       Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ PLACEHOLDERS_ET_TODO.md  # Endpoints ÃƒÂ  implÃƒÂ©menter (archivÃƒÂ© avec rapports)
Ã¢â€â€š       Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ README.md  # Index du dossier
Ã¢â€â€š       Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ AUDITS_IMPLEMENTES/  # Recos toutes appliquÃƒÂ©es (Backend Alpha2, Dette qual., etc.)
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ INDEX.md  # Index des audits complÃƒÂ©tÃƒÂ©s
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ CLOTURE_AUDIT_BACKEND_ALPHA2_2026-02-22.md  # ClÃƒÂ´ture audit Backend Alpha 2 (28/02)
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ AUDIT_TECHNIQUE_BACKEND_ALPHA2_2026-02-27.md  # Audit technique factuel
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ PRIORISATION_AUDIT_BACKEND_ALPHA2_2026-02-28.md
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ CHALLENGE_AUDIT_TECHNIQUE_BACKEND_2026-02-28.md
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ AUDIT_SECURITE_APPLICATIVE_2026-02.md  # OWASP (archivÃƒÂ©)
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ANALYSE_THEMES_UX_2026-02.md
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ CONTRAST_FIXES.md
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ THEMES_TEST_RESULTS.md
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ REFACTORING_SUMMARY.md
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ REMAINING_TASKS.md
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ INDEX_DB_MANQUANTS_2026-02-06.md
Ã¢â€â€š       Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ AUDIT_FINAL_DOCS_GITIGNORE_2026-02-06.md
Ã¢â€â€š       Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ RAPPORTS_TEMPORAIRES/  # Rapports situationnels + historique
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ INDEX.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ DEPLOIEMENT_2026-02-06.md  # Rapport dÃƒÂ©ploiement 06/02
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ SUIVI_MIGRATION_ALEMBIC_22-02.md  # RÃƒÂ©cap migration DDL Ã¢â€ â€™ Alembic
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ BILAN_COMPLET.md  # Ã¢Å¡Â Ã¯Â¸Â Historique phases 1-6 (nov. 2025)
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ RAPPORT_VERIFICATION_CHALLENGES.md  # VÃƒÂ©rification 29/11/2025
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ PHASES/  # Documentation phases historiques
Ã¢â€â€š           Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ RECAP_PHASES.md
Ã¢â€â€š           Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ PHASE6_PLAN.md
Ã¢â€â€š           Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ PHASE6_RESULTAT.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ MISSION_COMPLETE_2026-02-06.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ RECAP_FINAL_2026-02-06.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ RATIONALISATION_DOCS_2026-02-06.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ PLAN_ACTION_2026-02-06.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ MIGRATION_INDEX_ROLLBACK_PLAN.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ COMMIT_FIXES_FRONTEND_2026-02-20.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ANALYSE_GENERATION_IA_EXERCICES.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ANALYSE_GENERATION_IA_CHALLENGES.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ANALYSE_DEPENDABOT_2026-02-20.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ SECURITY_AUDIT_REPORT.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ BADGES_AUDIT_PAUFINAGE.md
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ CLOTURE_ITERATION_STABILISATION_POST_FEATURES_2026-03-08.md  # Cloture archivee de l'iteration Cursor
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ GUIDAGE_CURSOR_ALIGNEMENT_POST_IMPL_2026-03-08.md  # Guidage Cursor archive
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ PILOTAGE_CURSOR_STABILISATION_POST_FEATURES_2026-03-08.md  # Document maitre archive
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ PILOTAGE_CURSOR_LOT*.md  # Lots 1, 1 bis, 2, 3, 4 archives
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ REFACTO_*_HANDLERS.md  # Plans complÃƒÂ©tÃƒÂ©s
Ã¢â€â€š           Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ *_MIGRATION_ALEMBIC*.md  # Migration DDL Ã¢â€ â€™ Alembic
Ã¢â€â€š           Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ CONTEXTE_PROJET_REEL.md
Ã¢â€â€š
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ 04-FRONTEND/           # Ã°Å¸â€“Â¥Ã¯Â¸Â Documentation frontend (22/02/2026)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ARCHITECTURE.md         # Structure, stack, patterns Next.js
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ DESIGN_SYSTEM.md        # Composants layout standardisÃƒÂ©s (PageLayout, PageHeaderÃ¢â‚¬Â¦)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ACCESSIBILITY.md        # WCAG 2.1 AAA, 5 modes (Focus TSA/TDAH, contrasteÃ¢â‚¬Â¦)
Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ PWA.md                  # Progressive Web App (manifest, SW, offline)
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ ANIMATIONS.md           # Composants spatiaux (Starfield, Planet, ParticlesÃ¢â‚¬Â¦)
Ã¢â€â€š
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ 06-WIDGETS/            # Ã°Å¸Å½Â¨ Widgets Dashboard (Nouveau 06/02/2026)
    Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ INTEGRATION_PROGRESSION_WIDGETS.md  # Guide d'intÃƒÂ©gration
    Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ENDPOINTS_PROGRESSION.md            # API endpoints utilisÃƒÂ©s
    Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ DESIGN_SYSTEM_WIDGETS.md            # Design system et patterns
    Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ CORRECTIONS_WIDGETS.md              # Corrections appliquÃƒÂ©es
```

---

## Ã°Å¸Å½Â¯ Navigation par besoin

### Je veux dÃƒÂ©marrer le projet
1. [README.md](../README.md) - Installation rapide
2. [GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md) - Pas-ÃƒÂ -pas dÃƒÂ©taillÃƒÂ©
3. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md) - Workflow dev

### Je veux travailler sur le frontend
1. [ARCHITECTURE.md](04-FRONTEND/ARCHITECTURE.md) - Stack, routes, composants, hooks
2. [DESIGN_SYSTEM.md](04-FRONTEND/DESIGN_SYSTEM.md) - Composants standardisÃƒÂ©s, patterns de page
3. [ACCESSIBILITY.md](04-FRONTEND/ACCESSIBILITY.md) - WCAG AAA, modes accessibilitÃƒÂ©
4. [PWA.md](04-FRONTEND/PWA.md) - Progressive Web App
5. [ANIMATIONS.md](04-FRONTEND/ANIMATIONS.md) - Composants spatiaux

### Je veux comprendre l'architecture
1. **[README_TECH.md](../README_TECH.md)** Ã¢Â­Â - **Document de rÃƒÂ©fÃƒÂ©rence unique**
   - Stack technique
   - Architecture backend (Starlette)
   - Architecture frontend (Next.js 16)
   - voir server/routes/ (get_routes())
   - ModÃƒÂ¨les de donnÃƒÂ©es
   - GÃƒÂ©nÃƒÂ©ration IA (OpenAI)

### Je veux dÃƒÂ©velopper une fonctionnalitÃƒÂ©
1. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md) - Conventions et workflow
2. [README_TECH.md](../README_TECH.md) - API et patterns
3. [ROADMAP_FONCTIONNALITES.md](02-FEATURES/ROADMAP_FONCTIONNALITES.md) - Backlog & prioritÃƒÂ©s (source de vÃƒÂ©ritÃƒÂ©)
4. [API_QUICK_REFERENCE.md](02-FEATURES/API_QUICK_REFERENCE.md) - Section Admin (34 endpoints)
5. [F03_DIAGNOSTIC_INITIAL.md](02-FEATURES/F03_DIAGNOSTIC_INITIAL.md) - Reference F03 (test IRT adaptatif, diagnostic_results)
6. [F04_REVISIONS_ESPACEES.md](02-FEATURES/F04_REVISIONS_ESPACEES.md) - Specification F04 (SM-2, non implemente)
7. [F05_ADAPTATION_DYNAMIQUE.md](02-FEATURES/F05_ADAPTATION_DYNAMIQUE.md) - Reference F05 (adaptation difficulte, IRT, QCM vs saisie libre)

### Je veux crÃƒÂ©er un nouveau widget dashboard
1. [DESIGN_SYSTEM_WIDGETS.md](06-WIDGETS/DESIGN_SYSTEM_WIDGETS.md) - Template et patterns
2. [INTEGRATION_PROGRESSION_WIDGETS.md](06-WIDGETS/INTEGRATION_PROGRESSION_WIDGETS.md) - Exemple complet

### Je veux accÃƒÂ©der ÃƒÂ  l'espace admin
1. [ADMIN_ESPACE_PROPOSITION.md](02-FEATURES/ADMIN_ESPACE_PROPOSITION.md) Ã¢â‚¬â€ PÃƒÂ©rimÃƒÂ¨tre, itÃƒÂ©rations, vision
2. [ADMIN_FEATURE_SECURITE.md](02-FEATURES/ADMIN_FEATURE_SECURITE.md) Ã¢â‚¬â€ RBAC, dÃƒÂ©corateurs
3. [API_QUICK_REFERENCE.md](02-FEATURES/API_QUICK_REFERENCE.md) Ã¢â‚¬â€ Section Admin (25 endpoints)

### Je veux dÃƒÂ©ployer ou gÃƒÂ©rer CI/CD
1. [CICD_DEPLOY.md](03-PROJECT/CICD_DEPLOY.md) - CI automatique, smoke test /health, migrations, rollback manuel
2. [DEPLOYMENT_ENV.md](01-GUIDES/DEPLOYMENT_ENV.md) - Variables d'environnement Render (prod)
3. [ENV_CHECK.md](01-GUIDES/ENV_CHECK.md) - Checklist .env et Render (dev local)

### Je veux consulter l'ÃƒÂ©tat du refactor
1. [AUDIT_ARCHITECTURE_BACKEND_2026-03.md](03-PROJECT/AUDIT_ARCHITECTURE_BACKEND_2026-03.md) Ã¢â‚¬â€ Audit SOLID/Clean Code 5 phases (22/02)
2. [BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md](03-PROJECT/BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md) - Bilan final de l'iteration backend `exercise/auth/user`
1. [AUDIT_ARCHITECTURE_BACKEND_2026-03.md](03-PROJECT/AUDIT_ARCHITECTURE_BACKEND_2026-03.md) - Audit SOLID/Clean Code 5 phases (22/02)
2. [BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md](03-PROJECT/BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md) - Bilan final de l'iteration backend `exercise/auth/user`
3. [DELTA_RESTANT_POST_ITERATION_BACKEND_2026-03-09.md](03-PROJECT/DELTA_RESTANT_POST_ITERATION_BACKEND_2026-03-09.md) - Ce qu'il reste a faire apres la cloture de l'iteration
4. [PILOTAGE_CURSOR_BACKEND_REFACTOR_EXERCISE_AUTH_USER_2026-03-08.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/PILOTAGE_CURSOR_BACKEND_REFACTOR_EXERCISE_AUTH_USER_2026-03-08.md) - Pilotage maitre archive
5. [VERSIONING_BACKEND_REFACTOR_EXERCISE_AUTH_USER_2026-03-08.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/VERSIONING_BACKEND_REFACTOR_EXERCISE_AUTH_USER_2026-03-08.md) - Versioning interne archive, iteration cloturee en `1.0.0`
6. [CHANGELOG.md](../CHANGELOG.md) - Changelog racine, avec release `3.1.0-alpha.7`
7. [REFACTOR_STATUS_2026-02.md](03-PROJECT/REFACTOR_STATUS_2026-02.md) - Etat Clean Code P1-P3 + Architecture Ph1-Ph3
8. [PLAN_CLEAN_CODE_ET_DTO](03-PROJECT/PLAN_CLEAN_CODE_ET_DTO_2026-02.md) - Detail DTO, exceptions, typage
9. [PLAN_REFACTO_ARCHITECTURE](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/PLAN_REFACTO_ARCHITECTURE_2026-02.md) - Phases routes, handlers, services
### Je veux tester mes modifications
1. [TESTING.md](01-GUIDES/TESTING.md) - Guide tests complet
2. [TESTER_MODIFICATIONS_SECURITE.md](01-GUIDES/TESTER_MODIFICATIONS_SECURITE.md) - Tests sÃƒÂ©curitÃƒÂ©
3. [AUDIT_SECURITE_APPLICATIVE_2026-02.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/AUDIT_SECURITE_APPLICATIVE_2026-02.md) - Audit OWASP (archivÃƒÂ©, recos appliquÃƒÂ©es)

### J'ai un problÃƒÂ¨me
1. [TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md) - Solutions problÃƒÂ¨mes courants
2. [README_TECH.md](../README_TECH.md) - Section "IncohÃƒÂ©rences rÃƒÂ©solues"

### Je veux contribuer
1. [CONTRIBUTING.md](01-GUIDES/CONTRIBUTING.md) - Workflow contribution
2. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md) - Standards et conventions

### Je suis parent ou utilisateur final
1. **[/docs](https://mathakine.fun/docs)** (sur le site) Ã¢â‚¬â€ Guide d'utilisation intÃƒÂ©grÃƒÂ© (parcours, FAQ, accessibilitÃƒÂ©)
2. **[GUIDE_UTILISATEUR_MVP.md](01-GUIDES/GUIDE_UTILISATEUR_MVP.md)** Ã¢â‚¬â€ Source dÃƒÂ©taillÃƒÂ©e (personas, analyse psychologique, rÃƒÂ©tention)

---

## Ã°Å¸â€œÅ  Documents par prioritÃƒÂ©

### Ã°Å¸â€Â´ PrioritÃƒÂ© HAUTE (lecture obligatoire)
- [README.md](../README.md) - Point d'entrÃƒÂ©e
- **[README_TECH.md](../README_TECH.md)** Ã¢Â­Â - **RÃƒÂ©fÃƒÂ©rence technique unique**
- [GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md) - Installation

### Ã°Å¸Å¸Â¡ PrioritÃƒÂ© MOYENNE (recommandÃƒÂ©)
- [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md) - Workflow dev
- [TESTING.md](01-GUIDES/TESTING.md) - Tests
- [TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md) - DÃƒÂ©pannage

### Ã°Å¸Å¸Â¢ PrioritÃƒÂ© BASSE (selon besoin)
- [02-FEATURES/](02-FEATURES/) - FonctionnalitÃƒÂ©s spÃƒÂ©cifiques
- [03-PROJECT/](03-PROJECT/) - Historique projet
- [06-WIDGETS/](06-WIDGETS/) - Design system widgets

---

## Ã°Å¸â€œÂ Principes de documentation

### Document unique de rÃƒÂ©fÃƒÂ©rence
**README_TECH.md** est le **document de rÃƒÂ©fÃƒÂ©rence unique** pour toute la partie technique :
- Architecture backend et frontend
- API (voir server/routes/)
- ModÃƒÂ¨les de donnÃƒÂ©es
- Stack technique
- Conventions de code
- IncohÃƒÂ©rences connues

**Tous les autres documents** sont des **guides pratiques** ou des **documentations de fonctionnalitÃƒÂ©s spÃƒÂ©cifiques**.

### Pas de duplication
- Ã¢Å“â€¦ Une seule source de vÃƒÂ©ritÃƒÂ© par sujet
- Ã¢Å“â€¦ Les guides renvoient vers README_TECH.md
- Ã¢Å“â€¦ Pas de copie/coller entre documents

### Documentation vivante
- Ã¢Å“â€¦ Mise ÃƒÂ  jour ÃƒÂ  chaque changement majeur
- Ã¢Å“â€¦ Date de derniÃƒÂ¨re mise ÃƒÂ  jour visible
- Ã¢Å“â€¦ Suppression des informations obsolÃƒÂ¨tes

---

### 09/03/2026 - Cloture de l'iteration backend exercise/auth/user
- [BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md](03-PROJECT/BILAN_FINAL_ITERATION_BACKEND_EXERCISE_AUTH_USER_2026-03-09.md) - verdict final, version retenue, reliquats et prochaine iteration backend
- [CHANGELOG.md](../CHANGELOG.md) - release `3.1.0-alpha.7` pour la stabilisation backend `exercise/auth/user`
- [DELTA_RESTANT_POST_ITERATION_BACKEND_2026-03-09.md](03-PROJECT/DELTA_RESTANT_POST_ITERATION_BACKEND_2026-03-09.md) - delta restant apres cloture : UX frontend auth, prochaine iteration backend, docs de second rang
- [PILOTAGE_CURSOR_BACKEND_REFACTOR_EXERCISE_AUTH_USER_2026-03-08.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/PILOTAGE_CURSOR_BACKEND_REFACTOR_EXERCISE_AUTH_USER_2026-03-08.md) - pilotage maitre archive
- [VERSIONING_BACKEND_REFACTOR_EXERCISE_AUTH_USER_2026-03-08.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/VERSIONING_BACKEND_REFACTOR_EXERCISE_AUTH_USER_2026-03-08.md) - iteration backend cloturee en `1.0.0` puis archivee

## Ã°Å¸â€â€ž DerniÃƒÂ¨res mises ÃƒÂ  jour

### 08/03/2026 Ã¢â‚¬â€ Cloture iteration Cursor backend
- Ã°Å¸â€œËœ **[CLOTURE_ITERATION_STABILISATION_POST_FEATURES_2026-03-08.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/CLOTURE_ITERATION_STABILISATION_POST_FEATURES_2026-03-08.md)** Ã¢â‚¬â€ cloture archivee de l'iteration post-features : lots 1, 2, 1 bis, 3, 4, gates techniques verts, reliquat non bloquant
- Ã°Å¸â€œâ„¢ **[GUIDAGE_CURSOR_ALIGNEMENT_POST_IMPL_2026-03-08.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/GUIDAGE_CURSOR_ALIGNEMENT_POST_IMPL_2026-03-08.md)** Ã¢â‚¬â€ guidage Cursor post-audit archive apres execution
- Ã°Å¸â€”â€šÃ¯Â¸Â **[PILOTAGE_CURSOR_STABILISATION_POST_FEATURES_2026-03-08.md](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/PILOTAGE_CURSOR_STABILISATION_POST_FEATURES_2026-03-08.md)** Ã¢â‚¬â€ document maitre archive ; les lots 1, 1 bis, 2, 3 et 4 sont conserves dans le meme dossier d'archives
### 07/03/2026 Ã¢â‚¬â€ F32 Session entrelacee + F35 securite logs DB
- Ã°Å¸â€œÂ **[ROADMAP_FONCTIONNALITES.md](02-FEATURES/ROADMAP_FONCTIONNALITES.md)** Ã¢â‚¬â€ F32 et F35 marquÃƒÂ©s Ã¢Å“â€¦ implÃƒÂ©mentÃƒÂ©s (matrice, sections, historique)
- Ã°Å¸â€œÂ **[API_QUICK_REFERENCE.md](02-FEATURES/API_QUICK_REFERENCE.md)** Ã¢â‚¬â€ endpoint F32 `GET /api/exercises/interleaved-plan?length=10` + contrat `POST /api/exercises/generate` clarifiÃƒÂ© (`adaptive`, `age_group?`)
- Ã°Å¸â€œÂ **[EDTECH_ANALYTICS.md](02-FEATURES/EDTECH_ANALYTICS.md)** Ã¢â‚¬â€ analytics Quick Start ÃƒÂ©tendue au type `interleaved`
- Ã°Å¸â€œâ„¢ **[IMPLEMENTATION_F32_SESSION_ENTRELACEE.md](03-PROJECT/IMPLEMENTATION_F32_SESSION_ENTRELACEE.md)** Ã¢â‚¬â€ cadrage et choix MVP implÃƒÂ©mentÃƒÂ©s
- Ã°Å¸â€œâ„¢ **[IMPLEMENTATION_F35_REDACTION_LOGS_DB.md](03-PROJECT/IMPLEMENTATION_F35_REDACTION_LOGS_DB.md)** Ã¢â‚¬â€ hardening sÃƒÂ©curitÃƒÂ© logs DB implÃƒÂ©mentÃƒÂ©

### 06/03/2026 Ã¢â‚¬â€ F02 DÃƒÂ©fis quotidiens + Refactor Dashboard + Documentation
- Ã°Å¸â€œâ„¢ **[F02_DEFIS_QUOTIDIENS.md](02-FEATURES/F02_DEFIS_QUOTIDIENS.md)** Ã¢â‚¬â€ RÃƒÂ©fÃƒÂ©rence F02 : modÃƒÂ¨le, API, service, cÃƒÂ¢blage progression
- Ã°Å¸â€œâ„¢ **[F02_DAILY_CHALLENGES_WIDGET.md](06-WIDGETS/F02_DAILY_CHALLENGES_WIDGET.md)** Ã¢â‚¬â€ Widget DailyChallengesWidget, design Anti-Cheap
- Ã°Å¸â€œâ€¢ **[REFACTOR_DASHBOARD_2026-03.md](03-PROJECT/REFACTOR_DASHBOARD_2026-03.md)** Ã¢â‚¬â€ RÃƒÂ©organisation onglets : Vue d'ensemble (DÃƒÂ©fis+SÃƒÂ©rie), Progression (4 graphiques), Mon Profil (Niveau, badges, stats, tempo, journal)
- Ã°Å¸â€œÂ **INTEGRATION_PROGRESSION_WIDGETS** Ã¢â‚¬â€ Structure actuelle, DailyChallengesWidget, Leaderboard retirÃƒÂ©
- Ã°Å¸â€œÂ **ROADMAP_FONCTIONNALITES** Ã¢â‚¬â€ F02 marquÃƒÂ© implÃƒÂ©mentÃƒÂ©
- Ã°Å¸â€œÂ **API_QUICK_REFERENCE** Ã¢â‚¬â€ Section Daily Challenges (F02)
- Ã°Å¸â€œÂ **ENDPOINTS_PROGRESSION** Ã¢â‚¬â€ GET /api/daily-challenges
- Ã°Å¸â€œÂ **INDEX** Ã¢â‚¬â€ F02, REFACTOR_DASHBOARD, F02_DAILY_CHALLENGES_WIDGET

### 06/03/2026 Ã¢â‚¬â€ Documentation F03, F04, F05 + audit cohÃƒÂ©rence docs
- Ã°Å¸â€œâ„¢ **[F03_DIAGNOSTIC_INITIAL.md](02-FEATURES/F03_DIAGNOSTIC_INITIAL.md)** Ã¢â‚¬â€ RÃƒÂ©fÃƒÂ©rence F03 : algorithme IRT adaptatif, table `diagnostic_results`, endpoints, intÃƒÂ©gration F05
- Ã°Å¸â€œâ„¢ **[F04_REVISIONS_ESPACEES.md](02-FEATURES/F04_REVISIONS_ESPACEES.md)** Ã¢â‚¬â€ SpÃƒÂ©cification F04 (SM-2, non implÃƒÂ©mentÃƒÂ©) : modÃƒÂ¨le de donnÃƒÂ©es, intÃƒÂ©gration prÃƒÂ©vue
- Ã°Å¸â€œâ„¢ **[F05_ADAPTATION_DYNAMIQUE.md](02-FEATURES/F05_ADAPTATION_DYNAMIQUE.md)** Ã¢â‚¬â€ RÃƒÂ©fÃƒÂ©rence F05 : cascade IRT, proxys MIXTE/FRACTIONS, mode QCM vs saisie libre
- Ã°Å¸â€œÂ **ROADMAP_FONCTIONNALITES** Ã¢â‚¬â€ Liens vers F03, F04, F05 ; F05 corrigÃƒÂ© (is_open_answer cÃƒÂ´tÃƒÂ© frontend)
- Ã°Å¸â€œÂ **WORKFLOW_EDUCATION** Ã¢â‚¬â€ F03 et F05 marquÃƒÂ©s implÃƒÂ©mentÃƒÂ©s
- Ã°Å¸â€œÂ **06-WIDGETS** Ã¢â‚¬â€ LevelEstablishedWidget documentÃƒÂ©
- Ã°Å¸â€œÂ **API_QUICK_REFERENCE** Ã¢â‚¬â€ Section Diagnostic (F03), lien PLACEHOLDERS corrigÃƒÂ©
- Ã°Å¸â€œÂ **INDEX** Ã¢â‚¬â€ NumÃƒÂ©rotation refactor corrigÃƒÂ©e (1Ã¢â‚¬â€œ4), structure 02-FEATURES (F03/F04/F05), PLACEHOLDERS dans arborescence, lien AUDIT_DETTE_QUALITE
- Ã°Å¸â€œÂ **ENDPOINTS_NON_INTEGRES** Ã¢â‚¬â€ Section Diagnostic intÃƒÂ©grÃƒÂ©, date 06/03

### 03/03/2026 Ã¢â‚¬â€ Audit architecture backend
- Ã°Å¸â€œÂ **[AUDIT_ARCHITECTURE_BACKEND_2026-03.md](03-PROJECT/AUDIT_ARCHITECTURE_BACKEND_2026-03.md)** Ã¢â‚¬â€ Audit complet SOLID, Clean Code, performances, sÃƒÂ©curitÃƒÂ©, industrialisation. 36 constats (4 critiques, 10 high). Plan 5 phases priorisÃƒÂ© (~15 jours). ComplÃƒÂ©mentaire ÃƒÂ  l'audit Cleanup du 01/03.

### 28/02/2026 Ã¢â‚¬â€ Refactor + documentation alignÃƒÂ©e
- Ã°Å¸â€œÂ **Refactor terminÃƒÂ©** : Clean Code P1Ã¢â‚¬â€œP3, Architecture Ph1Ã¢â‚¬â€œPh3. Voir [REFACTOR_STATUS_2026-02.md](03-PROJECT/REFACTOR_STATUS_2026-02.md).
- Ã°Å¸â€œÂ **Documentation alignÃƒÂ©e** : Toutes les refs `server/routes.py` Ã¢â€ â€™ `server/routes/`. README_TECH, INDEX, DEVELOPMENT, CONVENTION, TROUBLESHOOTING, etc.
- Ã°Å¸â€œÂ **ANALYSE_DUPLICATION_DRY** : P3 exceptions et SubmitAnswerResponse ajoutÃƒÂ©s aux rÃƒÂ©alisations.

### 15/02/2026 Ã¢â‚¬â€ Documentation (mise en ordre)
- Ã°Å¸â€œÂ **RÃƒÂ©organisation** : DEPLOIEMENT et SUIVI_MIGRATION Ã¢â€ â€™ RAPPORTS_TEMPORAIRES ; ENV_CHECK Ã¢â€ â€™ 01-GUIDES ; CICD_DEPLOY, POLITIQUE_REDACTION_LOGS_PII dans README 03-PROJECT.
- Ã°Å¸â€œÂ **CICD_DEPLOY.md** : CI automatique, smoke test /health, migrations, rollback. [Lire Ã¢â€ â€™](03-PROJECT/CICD_DEPLOY.md)

### 15/02/2026 (qualitÃƒÂ© frontend)
- Ã¢Å“â€¦ **Refactor qualitÃƒÂ©** : Typage TypeScript strict sur tous les renderers de visualisation (ChessRenderer, CodingRenderer, DeductionRenderer, GraphRenderer, etc.), useAccessibleAnimation (Variants/Transition), validation dashboard, vitest.setup. Exclusion `scripts/` du lint.
- Ã¢Å“â€¦ **Build + tests unitaires** : 31 tests Vitest OK (dont 11 sur safeValidateUserStats). E2E : `npx playwright install` requis.
- Ã°Å¸â€œÂ **TESTING.md** : Section Ã‚Â« PrioritÃƒÂ©s de couverture frontend Ã‚Â» + tests rÃƒÂ©gression dashboard. [Lire Ã¢â€ â€™](01-GUIDES/TESTING.md#priorites-couverture)
- Ã°Å¸â€œÂ **AUDIT_DETTE_QUALITE_FRONTEND** : Section Ã‚Â« Corrections appliquÃƒÂ©es Ã‚Â» documentÃƒÂ©e. [Lire Ã¢â€ â€™](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/AUDIT_DETTE_QUALITE_FRONTEND_2026-02-20.md)

### 18/02/2026
- Ã°Å¸â€œâ€ž **POINT_SITUATION_2026-02-18.md** Ã¢â‚¬â€ Bilan projet (fonctionnalitÃƒÂ©s, prioritÃƒÂ©s, rÃƒÂ©fÃƒÂ©rences). [Lire Ã¢â€ â€™](03-PROJECT/POINT_SITUATION_2026-02-18.md)
- Ã¢Å“â€¦ **Badges Ã¢â‚¬â€ Finalisation** : Fix N+1 sur `/api/challenges/badges/progress` (stats_cache prÃƒÂ©-fetch, ~12 requÃƒÂªtes fixes). Filtre Ã‚Â« Proches (>50%) Ã‚Â» visible uniquement sur onglet Ãƒâ‚¬ dÃƒÂ©bloquer. Script `scripts/delete_test_badges.py` pour hard delete badges test.
- Ã°Å¸â€œÂ **Docs** : PLAN_REFONTE_BADGES (Ã‚Â§ 10 post-livraison), SITUATION_FEATURES (badges finalisÃƒÂ©s), nettoyage fichiers temporaires.

### 17/02/2026
- Ã¢Å“â€¦ **Badges B4** : Reformulation 17 badges (name, description, star_wars_title, catÃƒÂ©gories, points). Script `scripts/update_badges_b4.py`. Contexte challenge documentÃƒÂ© dans B4_REFORMULATION_BADGES.
- Ã¢Å“â€¦ **Badges psycho/rÃƒÂ©tention** : 12 badges add_badges_psycho + 3 add_badges_recommandations (guardian_150, marathon, comeback). **32 badges**, 4 secrets. Vigilance 35Ã¢â‚¬â€œ40 max.
- Ã¢Å“â€¦ **Badges Lot C-1** : Moteur gÃƒÂ©nÃƒÂ©rique `badge_requirement_engine.py` (registry 10 types), refactor `_check_badge_requirements`. Terrain B5 : checkers `logic_attempts_count`, `mixte` ; validation admin ; BadgeCreateModal/BadgeEditModal exemples dÃƒÂ©fis/mixte ; `submit_challenge_answer` appelle `check_and_award_badges`.
- Ã¢Å“â€¦ **Badges Lot C-2** : `get_requirement_progress` (10 types) dans engine, refactor `_get_badge_progress`. Tests `test_badge_requirement_engine.py`.
- Ã¢Å“â€¦ **Badges Lot B-5** : Goal-gradient (Ã‚Â« Plus que X Ã‚Â»), loss aversion (Ã‚Â« Tu approches Ã‚Â»), champ icon_url admin (emoji/URL), BadgeCard affiche icon_url, principes psychologiques enrichis, audit nombre badges Ã‚Â§ 5.3.3.

### 16/02/2026
- Ã¢Å“â€¦ **Quick wins 1-4** : (1) maintenance_mode + registration_enabled appliquÃƒÂ©s, (2) handle_recommendation_complete, (3) get_user_badges_progress, (4) is_current dans /api/users/me/sessions
- Ã¢Å“â€¦ **Admin Ã¢â‚¬â€ ParamÃƒÂ¨tres globaux** : page `/admin/config`, `GET/PUT /api/admin/config`, paramÃƒÂ¨tres maintenance, inscriptions, feature flags, limites (table `settings`)
- Ã¢Å“â€¦ **Admin Ã¢â‚¬â€ Fix** : normalisation boolÃƒÂ©ens (is_archived, is_active) dans PUT exercices/challenges
- Ã°Å¸â€œÂ **Docs** : ADMIN_ESPACE_PROPOSITION (itÃƒÂ©ration 14), API_QUICK_REFERENCE (25 routes admin), ENDPOINTS_NON_INTEGRES (section Admin)
- Ã°Å¸â€œÂ **Mise ÃƒÂ  jour docs suite implÃƒÂ©mentations** : README_TECH (API, hooks, maintenance, sessions), AUTH_FLOW (sessions, maintenance, registration_enabled), ROADMAP_FONCTIONNALITES (endpoints 16/02), INTEGRATION_PROGRESSION_WIDGETS (Recommendations complete)

### 15/02/2026 (features)
- Ã¢Å“â€¦ **Leaderboard** : `GET /api/users/leaderboard`, page `/leaderboard`, widget top 5 sur dashboard Vue d'ensemble
- Ã¢Å“â€¦ **Dashboard rÃƒÂ©organisÃƒÂ©** : Vue d'ensemble allÃƒÂ©gÃƒÂ©e (KPIs + streak + classement), Progression (dÃƒÂ©fis + prÃƒÂ©cision + graphiques), DÃƒÂ©tails (performance + activitÃƒÂ©), timestamp relatif formatÃƒÂ©
- Ã¢Å“â€¦ **Prompt IA fractions** : RÃƒÂ¨gles renforcÃƒÂ©es (moitiÃƒÂ©/tiers cohÃƒÂ©rents, pas d'erreur fictive)
- Ã°Å¸â€œÂ **ROADMAP_FONCTIONNALITES** : Leaderboard et Streak marquÃƒÂ©s implÃƒÂ©mentÃƒÂ©s
- Ã°Å¸â€œÂ **ENDPOINTS_NON_INTEGRES** : Leaderboard, PUT /api/users/me et /password documentÃƒÂ©s
- Ã°Å¸â€œÂ **06-WIDGETS** : LeaderboardWidget ajoutÃƒÂ© ÃƒÂ  INTEGRATION_PROGRESSION_WIDGETS

### 15/02/2026
- Ã°Å¸â€œâ„¢ **02-FEATURES** : API_QUICK_REFERENCE (cheat sheet endpoints), AUTH_FLOW (flux inscription/login/reset), THEMES (7 thÃƒÂ¨mes, themeStore, ajout)
- Ã°Å¸â€œÂ **RÃƒÂ©organisation docs** : Audits implÃƒÂ©mentÃƒÂ©s regroupÃƒÂ©s dans `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/` Ã¢â‚¬â€ ajout de CONTRAST_FIXES, THEMES_TEST_RESULTS, REFACTORING_SUMMARY, REMAINING_TASKS (ex-frontend/docs)
- Ã°Å¸â€œÂ **AUDITS_IMPLEMENTES/INDEX.md** : Index des 7 documents d'audits complÃƒÂ©tÃƒÂ©s

### 15/02/2026 (soir)
- Ã°Å¸Å½Â¨ **ThÃƒÂ¨mes** : 7 thÃƒÂ¨mes (Dune, ForÃƒÂªt, LumiÃƒÂ¨re, Dinosaures) Ã¢â‚¬â€ ANALYSE_THEMES_UX et THEMES_TEST_RESULTS mis ÃƒÂ  jour
- Ã°Å¸â€œÂ **Standardisation docs** : En-tÃƒÂªtes harmonisÃƒÂ©s (Date, Type, Statut), CONVENTION enrichie, taxonomie clarifiÃƒÂ©e
- Ã°Å¸â€œÂ **Documentation projet** : 03-PROJECT/README.md (index maÃƒÂ®tre), CONVENTION_DOCUMENTATION.md, standardisation audits/rapports

### 12/02/2026
- Ã¢Å“â€¦ **Ãƒâ€°nigmes (RiddleRenderer)** : Rendu correct des champs `pots` et `plaque` (plus de JSON brut), masquage de lÃ¢â‚¬â„¢ascii_art redondant
- Ã¢Å“â€¦ **Ãƒâ€°checs (ChessRenderer)** : Highlights uniquement sur les piÃƒÂ¨ces, affichage tour/objectif (mat en X coups), format de rÃƒÂ©ponse attendu, prompt IA pour positions tactiques rÃƒÂ©alistes
- Ã¢Å“â€¦ **Auth production (cross-domain)** : await sync au login, `ensureFrontendAuthCookie()` avant gÃƒÂ©nÃƒÂ©ration IA, routes `/api/auth/sync-cookie` et `/api/auth/check-cookie` pour diagnostic
- Ã°Å¸â€œÂ **TROUBLESHOOTING.md** : Section Ã‚Â« Cookie manquant Ã‚Â» en production enrichie

### 03/03/2026 Ã¢â‚¬â€ Audit Architecture Backend (Phases 0Ã¢â€ â€™4)
- Ã°Å¸â€ºÂ¡Ã¯Â¸Â **Phase 0 Ã¢â‚¬â€ SÃƒÂ©curitÃƒÂ©** : Bypass CSRF `TESTING` supprimÃƒÂ©, injection SQL `safe_delete` bloquÃƒÂ©e, validation `POSTGRES_PASSWORD` prod, credentials DB masquÃƒÂ©es dans les logs, `except` inatteignables corrigÃƒÂ©s.
- Ã°Å¸â€œÂ **Phase 1 Ã¢â‚¬â€ Standardisation** : Parsing body unifiÃƒÂ© (`parse_json_body`), rÃƒÂ©ponses erreur unifiÃƒÂ©es (`api_error_response`), 26 `traceback.print_exc()` Ã¢â€ â€™ `logger.error(exc_info=True)`, CORS source unique, CSRF frozenset prÃƒÂ©-calculÃƒÂ©, `_ROUTE_REGISTRY` central.
- Ã°Å¸â€Â§ **Phase 2 Ã¢â‚¬â€ Services lÃƒÂ©gers** : User lookups centralisÃƒÂ©s dans `UserService`, `auth_service.py` sans `HTTPException`, `_apply_challenge_filters()` extrait, `queries.py` supprimÃƒÂ© (403 lignes dead code), `TypedDict` introduits (`app/core/types.py`).
- Ã°Å¸Ââ€”Ã¯Â¸Â **Phase 3 Ã¢â‚¬â€ God objects** : `ChallengeAnswerService` extrait, `ChatService` extrait, `AdminService` Ã¢â€ â€™ 4 services (`AdminConfigService`, `AdminStatsService`, `AdminUserService`, `AdminContentService`) + faÃƒÂ§ade, `exercise_generator_helpers.py` enrichi.
- Ã°Å¸ÂÂ­ **Phase 4 Ã¢â‚¬â€ Industrialisation** : TypedDict complets, `constants_challenge.py` extrait, `format_paginated_response` adoptÃƒÂ©, `enum_mapping.py` adoptÃƒÂ©, `safe_delete`/`safe_archive` Ã¢â€ â€™ exceptions (`DatabaseOperationError`).
- Ã°Å¸â€œâ€¹ **RÃƒÂ©fÃƒÂ©rence** : [AUDIT_ARCHITECTURE_BACKEND_2026-03.md](03-PROJECT/AUDIT_ARCHITECTURE_BACKEND_2026-03.md) Ã¢â‚¬â€ 472 tests, 0 failures.

### 27/02/2026
- Ã¢Å“â€¦ **Refactor admin_handlers Ã¢â‚¬â€ AdminService (ÃƒÂ©tape 1)** *(dÃƒÂ©composÃƒÂ© en 4 services le 03/03/2026 Ã¢â‚¬â€ voir ci-dessus)* : Toute la logique DB dÃƒÂ©placÃƒÂ©e dans `app/services/admin_service.py` (users, badges, exercises, challenges, export CSV). Handlers minces sans requÃƒÂªtes directes. Voir [INVENTAIRE_HANDLERS_DB_DIRECTE](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INVENTAIRE_HANDLERS_DB_DIRECTE.md), [REFACTO_ADMIN_HANDLERS](03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/REFACTO_ADMIN_HANDLERS.md).
- Ã¢Å“â€¦ **Fix admin modÃƒÂ©ration** : Bouton Ã‚Â« Ãƒâ€°diter Ã‚Â» ouvre la modal dÃ¢â‚¬â„¢ÃƒÂ©dition in-place au lieu de rediriger vers la page Contenu.

### 21/02/2026
- Ã¢Å“â€¦ **Refactor exercise_generator (PR#1)** : Extraction des validateurs dans `server/exercise_generator_validators.py` (normalize_exercise_type, normalize_difficulty, normalize_and_validate_exercise_params, get_difficulty_from_age_group) Ã¢â‚¬â€ compatibilite preservee via re-exports
- Ã¢Å“â€¦ **Refactor exercise_generator (PR#2)** : Extraction des helpers dans `server/exercise_generator_helpers.py` (`generate_smart_choices`) Ã¢â‚¬â€ `generate_contextual_question` supprimÃƒÂ©e (H9 audit, jamais appelÃƒÂ©e)
- Ã¢Å“â€¦ **Refactor admin_handlers (PR#1)** : Extraction des utils dans `server/handlers/admin_handlers_utils.py` (CONFIG_SCHEMA, _log_admin_action, _parse_setting_value, _serialize_value)

### 11/02/2026
- Ã¢Å“â€¦ **Documentation tests** : TESTING.md, tests/README.md. CI : test:coverage, Codecov.

### 09/02/2026
- Ã¢Å“â€¦ **VulnÃƒÂ©rabilitÃƒÂ©s npm** (3Ã¢â€ â€™0), **dÃƒÂ©corateurs auth** (@require_auth, etc.), **exportExcel** (exceljs).

### 08/02/2026
- Ã¢Å“â€¦ **Dependabot**, **GitHub Actions v6**, **CI fiabilisÃƒÂ©e**, **tests httpx.AsyncClient**.

### 07/02/2026
- Ã¢Å“â€¦ **Settings page** complÃƒÂ¨te. **EVALUATION_PROJET_2026-02-07.md** Ã¢â‚¬â€ rÃƒÂ©fÃƒÂ©rence qualitÃƒÂ©.

### 06/02/2026 (soir)
- Ã¢Å“â€¦ **Index DB appliquÃƒÂ©s** : 13 index de performance crÃƒÂ©ÃƒÂ©s et dÃƒÂ©ployÃƒÂ©s
- Ã¢Å“â€¦ **AccessibilitÃƒÂ© refactorisÃƒÂ©e** : Toolbar en React Portal (bottom-left)
- Ã¢Å“â€¦ **Fix gÃƒÂ©nÃƒÂ©ration IA** : Authentification exercices + dÃƒÂ©pendance openai>=1.40.0
- Ã¢Å“â€¦ **Fix dark mode** : SÃƒÂ©lecteurs CSS corrigÃƒÂ©s
- Ã¢Å“â€¦ **ThÃƒÂ¨me simplifiÃƒÂ©** : Suppression rÃƒÂ©fÃƒÂ©rences Star Wars (droits d'auteur)
- Ã¢Å“â€¦ **Fix endpoint stats** : `/api/exercises/stats` avec challenges
- Ã°Å¸â€œÂ **ANALYTICS_PROGRESSION.md** : IdÃƒÂ©es de graphiques de progression

### 06/02/2026 (matin)
- Ã¢Å“â€¦ **Unification Starlette**, **6-WIDGETS/**, **rationalisation docs** (~200 archivÃƒÂ©s).

*Historique antÃƒÂ©rieur : voir `git log`.*

---

## Ã°Å¸â€œÅ¡ Documents racine (hors docs/)

| Fichier | Description | Statut |
|---------|-------------|--------|
| **README.md** | Point d'entrÃƒÂ©e projet (franÃƒÂ§ais) | Ã¢Å“â€¦ Ãƒâ‚¬ mettre ÃƒÂ  jour |
| **README_TECH.md** | Documentation technique complÃƒÂ¨te | Ã¢Å“â€¦ Ãƒâ‚¬ jour (07/03/2026) |

---

## Ã°Å¸Å½Â¯ Statistiques

- **Documents actifs** : ~48 docs (guides, features, projet, widgets)
- **CohÃƒÂ©rence** : ValidÃƒÂ©e vs code rÃƒÂ©el Ã¢â‚¬â€ revue trimestrielle (CONVENTION Ã‚Â§7)
- **DerniÃƒÂ¨re vÃƒÂ©rification** : 07/03/2026 (synchronisation documentaire F32/F35 + README_TECH)

---

## Ã°Å¸â€™Â¡ Besoin d'aide ?

1. **Question technique** Ã¢â€ â€™ [README_TECH.md](../README_TECH.md)
2. **Installation** Ã¢â€ â€™ [GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md)
3. **ProblÃƒÂ¨me** Ã¢â€ â€™ [TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md)
4. **Contribution** Ã¢â€ â€™ [CONTRIBUTING.md](01-GUIDES/CONTRIBUTING.md)

**PrÃƒÂªt ÃƒÂ  coder !** Ã°Å¸Å¡â‚¬


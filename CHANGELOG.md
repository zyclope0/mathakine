# Changelog

Toutes les modifications notables du projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et le projet adhère au [Semantic Versioning](https://semver.org/lang/fr/) avec suffixe `-alpha.N` pour les versions alpha.

## [2.2.0-alpha.6] - 2026-02-22

### Changed

- **Formatage** : Black et isort — alignement de 9 fichiers (Black), 4 fichiers (isort) pour passer la CI

---

## [2.2.0-alpha.5] - 2026-02-25

### Added

- **Analytics EdTech — instrumentation et admin**
  - Instrumentation : `trackDashboardView`, `trackQuickStartClick`, `trackFirstAttempt` (lib/analytics/edtech.ts)
  - Clic Quick Start → POST /api/analytics/event (quick_start_click) — CTR, % guidé
  - 1er attempt (exercice/défi) → POST /api/analytics/event (first_attempt) — temps vers 1er attempt, conversion
  - Table `edtech_events` (migration 20260225), persistance en BDD
  - Page admin `/admin/analytics` : KPIs, agrégats, liste événements (filtres 7d/30d, type)
  - API admin GET /api/admin/analytics/edtech
  - Documentation : docs/02-FEATURES/EDTECH_ANALYTICS.md

### Changed

- **Init DB** : test_create_tables vérifie l'appel à Alembic upgrade (mock)

### Tests

- tests/api/test_admin_analytics.py : accès archiviste, paramètre period, 403 padawan, POST event → visible admin
- frontend QuickStartActions : trackDashboardView au montage, trackQuickStartClick au clic

---

## [2.2.0-alpha.4] - 2026-02-22

### Added

- **Parcours guidé (P1)** : bloc « Que veux-tu faire ? » en tête du dashboard
  - 2 CTA : Un exercice / Un défi — liens vers recommandation prioritaire si dispo, sinon /exercises et /challenges
  - Composant `QuickStartActions`, priorisation par `priority` desc
  - `data-quick-start-*` pour instrumentation (CTR, temps vers 1er attempt)

### Changed

- **Tests recommandations** : alignement sur les routes réelles GET /api/recommendations, POST /api/recommendations/complete
  - `test_get_recommendations`, `test_mark_recommendation_as_completed`, `test_get_recommendations_returns_exercise_and_challenge_ids`
  - Nouveau test parcours guidé : vérifie `exercise_id` et `challenge_id` dans la réponse (QuickStartActions)
  - Skip `test_mark_recommendation_as_clicked` (route POST /api/recommendations/{id}/clicked non exposée)
- **Test frontend QuickStartActions** : 4 tests Vitest (titre + CTA, liens fallback, liens guidés, data-quick-start)

### Changed

- **Init DB tests** : `create_tables_with_test_data` utilise Alembic (`alembic upgrade head`) au lieu de `create_all`, garantissant un schéma à jour (grade_system, onboarding, etc.)
- **Recommandations** : personnalisation via onboarding et profil
  - `preferred_difficulty` (groupe d'âge) : filtre exercices et défis par âge
  - `grade_level` : dérive le groupe d'âge si preferred_difficulty vide (1-3→6-8, 4-6→9-11, etc.)
  - `learning_goal` : priorité renforcée pour `preparer_exam` (domaines faibles), `samuser` (défis)
  - Sans onboarding : pas de filtre âge (comportement inchangé)

### Fixed

- **Recommandations** : les exercices archivés/inactifs et défis archivés ne sont plus proposés (QuickStartActions, parcours guidé)
  - Filtrage côté API lors de la sérialisation des recommandations
  - Test `test_get_recommendations_excludes_archived_challenge`

---

## [2.2.0-alpha.3] - 2026-02-22

### Added

- **Quick Win #2 — Onboarding pédagogique** : mini-diagnostic après inscription/connexion
  - Page `/onboarding` : classe, groupe d'âge, objectif (réviser, préparer_exam, etc.), rythme (10 min/jour, etc.)
  - Champs BDD : `onboarding_completed_at`, `learning_goal`, `practice_rhythm`
  - Redirection post-login vers `/onboarding` si non complété, sinon vers dashboard/exercises
  - Protection dashboard : redirection vers onboarding si `onboarding_completed_at` null
- **Système scolaire au choix** : Suisse romand (1H-11H) ou unifié (1-12)
  - Champ BDD `grade_system` (« suisse » | « unifie »)
  - Sélecteur dans l'onboarding et stockage pour contenu adaptatif futur

### Changed

- **Profil et paramètres accessibles aux utilisateurs non vérifiés** : ne bloque plus l'accès si email non vérifié
  - Pages profil et paramètres sans `requireFullAccess` (permettent de modifier email, renvoyer lien vérification)
  - APIs PUT /me, GET /users/stats, GET /badges/user sans `require_full_access`
- Tests `test_unverified_access` : stats et badges/user retournent 200 au lieu de 403 (profil accessible)

---

## [2.2.0-alpha.2] - 2026-02-23

### Added

- **Quick Win #1 — First Exercise < 90s** : accès immédiat après inscription
  - Auto-login après inscription + redirection vers `/dashboard`
  - Période de grâce 45 min pour utilisateurs non vérifiés (accès complet)
  - Au-delà : accès aux exercices uniquement (dashboard, défis, badges, classement restreints)
  - Bandeau « Vérifiez votre email » pour débloquer les fonctionnalités
  - Navigation conditionnelle : liens masqués selon `access_scope`
  - `access_scope` et `is_email_verified` dans les réponses login/me
- Tests backend : 16 tests (unit + API) pour unverified access

### Fixed

- Ordre des décorateurs : `@require_auth` avant `@require_full_access` pour les routes protégées

### Changed

- Inscription : connexion automatique au lieu de redirection vers login
- Routes dashboard, badges, challenges, leaderboard, profile, settings : redirection vers `/exercises` si `access_scope === "exercises_only"`

---

## [2.2.0-alpha.1] - 2026-02-22

### Added

- Pages À propos, Contact, Politique de confidentialité (RGPD)
- Bouton de signalement (FeedbackFab) : exercices, défis, bugs — icône drapeau rouge
- Filtre par groupe d'âge sur le classement
- Widget temps moyen par session sur le tableau de bord
- Recommandations : exclusion des exercices et défis déjà réussis

### Fixed

- Chevauchement footer / chatbot / FeedbackFab (z-index)

### Changed

- Footer : nouveaux liens rapides (À propos, Contact, Politique de confidentialité)

---

## [2.1.0] - 2026-02-06

### Added

- Ordre aléatoire et option « Masquer les réussis » pour exercices et défis
- Refonte badges : onglets En cours / À débloquer, rareté, épinglage
- Défis : parsing tolérant, types VISUAL multi-position
- Thèmes : Dune, Forêt, Lumière, Dinosaures
- Classement (leaderboard)
- Export PDF/Excel des données
- Assistant mathématique (chatbot IA)
- Espace admin : contenu, modération, paramètres globaux, audit
- Monitoring Sentry, Prometheus
- Options d'accessibilité (contraste, texte, animations, mode Focus TSA/TDAH)

### Security

- CSRF, rate limiting, CORS, SecureHeaders
- Validation JWT (type=access)

---

## [2.0.0] et antérieur

Historique condensé : exercices adaptatifs, défis logiques, authentification, vérification email, badges, tableau de bord de base.

---

## Convention de versioning (alpha)

- **Format** : `MAJOR.MINOR.PATCH-alpha.N` (ex. `2.2.0-alpha.1`)
- **Alpha** : fonctionnalités instables, changements fréquents
- **Incrément** : `alpha.N` à chaque release alpha significative
- **Sortie alpha** : retirer le suffixe (ex. `2.2.0`)

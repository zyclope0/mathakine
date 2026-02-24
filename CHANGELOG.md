# Changelog

Toutes les modifications notables du projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et le projet adhère au [Semantic Versioning](https://semver.org/lang/fr/) avec suffixe `-alpha.N` pour les versions alpha.

## [2.2.1-alpha.2] - 2026-02-25

Regroupement des avancées depuis 2.2.0-alpha.1.

### Added

- **Quick Win #1 — First Exercise < 90s** : accès immédiat après inscription
  - Auto-login après inscription + redirection vers `/dashboard`
  - Période de grâce 45 min pour utilisateurs non vérifiés (accès complet)
  - Au-delà : accès aux exercices uniquement (dashboard, défis, badges, classement restreints)
  - Bandeau « Vérifiez votre email » pour débloquer les fonctionnalités
  - Navigation conditionnelle : liens masqués selon `access_scope`
  - `access_scope` et `is_email_verified` dans les réponses login/me
- **Quick Win #2 — Onboarding pédagogique** : mini-diagnostic après inscription/connexion
  - Page `/onboarding` : classe, groupe d'âge, objectif, rythme
  - Champs BDD : `onboarding_completed_at`, `learning_goal`, `practice_rhythm`
  - Redirection post-login vers `/onboarding` si non complété
  - Système scolaire : Suisse romand (1H-11H) ou unifié (1-12), champ `grade_system`
- **Parcours guidé (P1)** : bloc « Que veux-tu faire ? » en tête du dashboard
  - 2 CTA : Un exercice / Un défi — liens vers recommandation prioritaire ou fallback
  - Composant `QuickStartActions`, personnalisation via onboarding (âge, objectif)
  - Recommandations : exclusion des exercices/défis archivés
- **Analytics EdTech** : instrumentation et admin
  - `trackDashboardView`, `trackQuickStartClick`, `trackFirstAttempt`
  - POST /api/analytics/event, table `edtech_events`
  - Page admin `/admin/analytics` : KPIs, agrégats, filtres 7d/30d
  - Documentation : docs/02-FEATURES/EDTECH_ANALYTICS.md

### Changed

- Profil et paramètres accessibles aux utilisateurs non vérifiés (modification email, renvoi lien)
- Init DB : `create_tables_with_test_data` utilise Alembic (`alembic upgrade head`)
- Formatage : Black et isort — alignement des fichiers pour la CI

### Fixed

- Ordre des décorateurs : `@require_auth` avant `@require_full_access`
- Recommandations : exercices et défis archivés exclus du parcours guidé

### Tests

- tests/api/test_unverified_access.py, test_admin_analytics.py
- frontend QuickStartActions.test.tsx (trackDashboardView, trackQuickStartClick)

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

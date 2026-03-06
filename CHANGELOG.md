# Changelog

Toutes les modifications notables du projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et le projet adhère au [Semantic Versioning](https://semver.org/lang/fr/) avec suffixe `-alpha.N` pour les versions alpha.

## [3.1.0-alpha.3] - 2026-03-06

### Added
- Documentation technique de référence complète pour les modules F03 (Test de diagnostic initial), F04 (Révisions espacées) et F05 (Adaptation dynamique de difficulté).
- Audit complet de la documentation (`INDEX.md`, `ROADMAP_FONCTIONNALITES`, etc.) pour refléter l'état réel du code et archiver les anciens documents dans `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/`.

### Fixed
- L'adaptation dynamique de la génération d'exercices (F05) prend désormais correctement en compte les proxies pour les opérations `MIXTE` et `FRACTIONS`.
- Le mode de réponse "QCM" ou "Saisie Libre" est maintenant déterminé par le Frontend en fonction du niveau IRT prouvé de l'utilisateur (`useIrtScores()`), et non plus par la difficulté théorique de l'exercice, garantissant un "scaffolding" pédagogique correct.
- Les endpoints manquants dans la documentation ont été ajoutés et validés (Endpoints Diagnostic, Admin, Sessions).

### Changed
- Refactor des règles de documentation : La vérité terrain est le code. Centralisation des documentations d'architecture dans `README_TECH.md`.

---

## [3.0.0-alpha.3] - 2026-03-04

### Added
- F03 — Test de diagnostic initial adaptatif (IRT) : 10 questions sur 4 types, algo adaptatif, résultats par type, page `/diagnostic`, section dans les Paramètres
- Intégration diagnostic → recommandations (difficulté médiane calculée après évaluation)

### Fixed
- `[TEST-ZAXXON]` affiché dans les titres et explications d'exercices (préfixe technique supprimé)
- Choix dupliqués dans les exercices de division (ex: deux "11") — déduplication via `generate_smart_choices`
- Erreur 500 à la fin du diagnostic (`DetachedInstanceError` SQLAlchemy) — données extraites dans le contexte de session
- Table `diagnostic_results` absente en base de données — migration `20260304_diagnostic` appliquée
- `chat_service.py` — `NameError: name 'x' is not defined` dans la f-string du prompt LaTeX (accolades et backslashes échappés)

### Changed
- Environnements de résolution (ExerciseSolver, ChallengeSolver, DiagnosticSolver, ExerciseModal) : couleurs hardcodées (`bg-slate-900`, `text-white`, `bg-white/5`…) remplacées par variables sémantiques (`bg-card`, `text-foreground`, `bg-secondary/50`…) — compatibilité avec tous les thèmes
- `MathText.tsx` : `prose-invert` → `prose-neutral dark:prose-invert` + `text-inherit` — le texte hérite la couleur du thème courant

---

## [2.5.0-alpha.2] - 2026-03-04

### Mission Anti-Cheap — Refonte UI Premium EdTech (Pages Exercice, Défi & Modal)

#### Nouveaux composants
- `UnifiedExerciseGenerator` : générateur Rapide/IA unifié avec switch « Mode IA ✨ » (Progressive Disclosure) — remplace les deux générateurs séparés
- `CompactListItem` : composant partagé pour la vue liste exercices/défis — élimine la duplication
- `useAIExerciseGenerator` : hook SSE encapsulant toute la logique de génération IA streaming
- `lib/utils/animation.ts` : utilitaire `getStaggerDelay()` pour les animations en cascade
- `lib/utils/format.ts` : helper `isAiGenerated()` — détection unifiée des contenus IA

#### ExerciseSolver — Page Exercice pleine page
- **Focus Board** : conteneur glassmorphism central (`bg-slate-900/60 backdrop-blur-xl border-white/20 rounded-3xl`) qui sort le contenu du fond spatial
- **Header** : bouton retour discret en haut à gauche, tags centrés, titre `text-3xl` centré
- **Tuiles de réponse** : `bg-white/10 border-white/20`, hover avec élévation, glow violet sur la sélection
- **Bouton Valider** : état désactivé smart (`bg-slate-800 text-slate-400`) / état actif primary avec glow
- **Success state** : vert emerald vibrant (`bg-emerald-500/20 border-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.3)]`), explication en « fiche de savoir » (`border-l-4 border-primary`), boutons hiérarchisés (primaire / secondaire discret)

#### ChallengeSolver — Page Défi pleine page
- **Focus Board** : même style glassmorphism, `rounded-t-3xl` (collé à la Command Bar)
- **Header** : `Défi #XXXX` discret (`text-sm font-mono`), titre star `text-3xl md:text-4xl font-bold text-white`
- **Boîtes internes** : description, question, visualisations dans `bg-white/5 border-white/10 rounded-xl`
- **Command Bar** : zone de réponse collée au Focus Board (`bg-slate-950/80 rounded-b-3xl border-t-0`) — plus de flottement
- **Bouton Valider** : même logique disabled/primary que ExerciseSolver
- **Bouton Indice** : style « bouée de sauvetage » (`border-amber-500/30 text-amber-400 hover:bg-amber-500/10`)

#### ExerciseModal
- Fermeture au clic sur le backdrop (`onPointerDownOutside`) — comportement natif Dialog Radix restauré
- Bouton X intégré dans le flex header (suppression de `absolute`)

#### Fix critique DnD — `FocusBoard` hors composant
- `FocusBoard` déclaré au niveau module (pas inline dans la fonction) dans `ChallengeSolver`
- Corrige un bug de remontage React qui détruisait le `DndContext` dnd-kit à chaque re-render, cassant le drag & drop des puzzles

#### Nettoyage DRY
- Suppression `ExerciseGenerator.tsx` (code mort remplacé par `UnifiedExerciseGenerator`)
- Suppression `CHALLENGE_TYPES` obsolète dans `exercises.ts`
- `debugLog`/`debugError` uniformisés dans les générateurs IA

---

## [2.4.0-alpha.2] - 2026-03-04

### Added
- `LogoMathakine` : composant React inline SVG — thémisation complète via CSS vars (`--logo-text`, `--logo-highlight`, `--logo-glow`, `--logo-accents`) définies dans `globals.css` pour chaque thème (light, dark, dune, forêt, dino…)
- `public/logo-m.svg` : icône M autonome (viewBox 100×100) — fond sombre, gradient violet (`#c4b5fd` → `#7c3aed`), point doré lumineux, reflet blanc — compatible format maskable PWA
- `manifest.json` : entrée SVG en tête (`"sizes": "any"`, `"purpose": "any maskable"`) — les navigateurs modernes (Chrome 93+, Firefox, Safari 16+) l'utilisent en priorité pour icône PWA et onglets
- Favicon SVG prioritaire dans `app/layout.tsx` (avant les fallbacks PNG 192/512)
- `.badge-card-glass` dans `globals.css` : glassmorphism sur les cartes badges — `bg-card/60`, `backdrop-blur-md`, bordure `white/8`, override `card-spatial-depth` background
- `.badge-icon-glow` dans `globals.css` : halo radial derrière l'icône des badges obtenus (gradient violet/amber)

### Changed
- `Header.tsx` : texte gradient "Mathakine" remplacé par `<LogoMathakine className="h-8 w-auto" />` — logo complet thémisé dans la navbar
- `app/page.tsx` (hero) : `<h1>Mathakine</h1>` remplacé par `<LogoMathakine>` responsive (`w-72` mobile → `w-[480px]` desktop)
- `BadgeCard.tsx` (earned compact) : layout refactorisé en `flex-col` centré — grande icône `size="md"`, nom tronqué sur 1 ligne, médaille + points en dessous, cœur/coche en overlay `absolute top-right`
- `BadgeCard.tsx` (locked) : overlay `<Lock>` Lucide centré en `absolute inset-0` sur `BadgeIcon` pour signaler visuellement les badges verrouillés
- `BadgeCard.tsx` : taille des icônes cœur et coche portée à `h-3.5 w-3.5` pour meilleure lisibilité

---

## [2.4.0-alpha.1] - 2026-03-04

### Added
- Bandeau motivationnel sur la page badges (message adapté au % de progression, 5 niveaux)
- Confetti au premier chargement après obtention d'un nouveau badge (canvas-confetti, localStorage)
- Widget "À portée de main" : top 3 badges en cours à ≥50% de progression, visible sans naviguer
- Composant `DifficultyMedal` extrait de `BadgeCard` — élimine la répétition `if bronze/silver/gold`

### Changed
- Cartes "Ma collection" : layout "list-item" compact (icône | nom+pts | actions) — alignement vertical, nom tronqué sur 1 ligne
- Icône Pin remplacée par Cœur (rempli si épinglé, disparaît au survol sinon)
- Date "obtenu le" déplacée en zone dépliable (survol uniquement, plus dans la vue miniature)
- Grille badges earned : `gap-3` au lieu de `gap-4`
- `BadgeGrid` : prop `compactEarned` pour activer le mode liste
- Médaille difficulté dans la vue compacte : taille `h-4 w-4` pour meilleure lisibilité

### Fixed
- `leaderboard/page.tsx` : état vide/erreur migré vers `EmptyState` (cohérence design system)
- `challenges/page.tsx` : badge compteur filtres actifs incluait `orderFilter` + `hideCompleted`
- `globals.css` : animations `animate-fade-in-up-delay-4` et `-delay-5` manquantes ajoutées

## [2.3.0] - 2026-03-03

### Audit Frontend Industrialisation — Clôture (Phases 0→4 complètes)

Audit frontend lancé le 22/02/2026, finalisé le 03/03/2026.
**Résultat final : 61 tests Vitest, 0 failures. tsc 0 erreurs. ESLint clean.**

#### Phase 0 — DRY & Design System (constantes + inputs)

- **Centralisation constantes** : `lib/constants/exercises.ts`, `challenges.ts`, `badges.ts` — plus de hardcoding dans les modales admin et filtres de page
- **Variables CSS sidebar/charts** : `--sidebar-*`, `--chart-1..5` mappés dans `globals.css` (cohérence light/dark)
- **Inputs shadcn/ui** : remplacement de tous les `<input>` raw par `<Input>` dans les renderers de défis visuels (`PatternRenderer`, etc.)
- **EmptyState badges** : gestion d'erreur standardisée + clés i18n FR/EN sur la page `/badges`

#### Phase 1 — Skeleton loaders & tokens sémantiques

- **DashboardWidgetSkeleton** : composant générique dans `DashboardSkeletons.tsx` — tous les widgets dashboard migrent vers ce squelette
- **Tokens sémantiques** : `--warning`, `--success`, `--info` ajoutés à `globals.css`, composants `feedback.tsx`, `ChatbotFloating.tsx` mis à jour
- **Dossier renommé** : `lib/validations/` → `lib/validation/` (nomenclature singulier)

#### Phase 2 — Import cn standardisé + lazy loading + AIGeneratorBase

- **Import cn unifié** : `import { cn } from "@/lib/utils"` partout (~37 fichiers) — `@/lib/utils/cn` n'est plus importé directement
- **Validation dérivée** : `lib/validation/exercise.ts` dérive ses arrays depuis `lib/constants/exercises.ts` via `Object.values()`
- **Skeleton lazy loading** : `app/page.tsx` — les composants `dynamic()` ont désormais des skeletons dimensionnés (plus de `loading: () => null`)
- **AIGeneratorBase** : composant UI partagé `components/shared/AIGeneratorBase.tsx` — les `AIGenerator.tsx` exercises + challenges en sont des wrappers fins

#### Phase 3 — Polish visual + i18n

- **Flip icon** : `VisualRenderer.tsx` — icône Lucide `FlipHorizontal` à la place du caractère `↔`
- **aria-label i18n** : boutons vue grille/liste dans `/exercises` et `/challenges` utilisent `t("viewGrid")` / `t("viewList")`
- **DefaultRenderer** : type badge + coloration syntaxique légère pour les données structurées
- **Animations charts** : `ProgressChart.tsx` + `DailyExercisesChart.tsx` — `isAnimationActive={!shouldReduceMotion}` (Recharts, contrôlé par `useAccessibleAnimation`)
- **Feature cards** : classe `card-spatial-depth` sur les cartes de fonctionnalités de la page d'accueil

#### Phase 3.5 — Thématisation charts

- **ProgressChart.tsx** : toutes les couleurs hardcodées (`#7c3aed`, `rgba(18,18,26,0.95)`…) remplacées par CSS variables (`var(--color-chart-1)`, `var(--color-border)`, `var(--color-popover)`, `var(--color-muted-foreground)`)
- **DailyExercisesChart.tsx** : idem — couleurs backend ignorées, chart 100% thématisé

#### Phase 4 — Accessibilité

- **Alt badges** : `BadgeCard.tsx` + `app/badges/page.tsx` — `alt=""` → `alt={badge.name || badge.code || "Badge"}` (texte descriptif)
- **DeductionRenderer.tsx** : `useAccessibleAnimation` intégré — `transition-colors` conditionnel
- **GraphRenderer.tsx** : animations Framer Motion entrée (nœuds/arêtes SVG) + stagger, contrôlées par `shouldReduceMotion` ; couleurs CSS variables
- **CSS contraste élevé** : `accessibility.css` nettoyé — bloc `.high-contrast` et doublons supprimés ; `@media (prefers-contrast: high)` aligné sur les tokens shadcn/ui dans `globals.css`

---

## [2.3.0] - 2026-02-22

### Audit Architecture Backend — Clôture (Phases 0→4 complètes)

Audit architecture backend lancé le 03/03/2026, challengé et finalisé le 22/02/2026.
**Résultat final : 472 tests, 0 failures. black + isort + flake8 clean. mypy 0 erreurs.**

#### Challenge Phase 4.5 — Corrections post-audit

- **Imports top-level** : `DatabaseOperationError` déplacé de inline vers top-level dans `transaction.py`. `logger` réordonné après imports (E402) dans `transaction.py` et `adapter.py`.
- **Signatures black** : `safe_delete`/`safe_archive` reformatées (lignes > 88 chars).
- **isort** : tri corrigé sur `user_service.py`, `user_handlers.py`, `adapter.py`.
- **`enhanced_server_adapter`** : `archive_exercise` signature corrigée (`return bool` → `None`, docstring `Returns` → `Raises`).
- **Imports inline résiduels** supprimés dans `exercise_service.py` et `logic_challenge_service.py`.

#### Dette technique documentée

Points non finalisés documentés dans `docs/03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/PLACEHOLDERS_ET_TODO.md` :
- `constants.py` découpage partiel (challenge extrait, exercise/user restent)
- Couverture test intégration `DELETE /api/users/me` erreur DB

---

## [2.3.0-alpha.3] - 2026-02-22

### Refactored — Phase 4.5 : safe_delete/safe_archive → exceptions

- **4.5 API exception-based** : `safe_delete`/`safe_archive` dans `transaction.py` lèvent `DatabaseOperationError` (plus de `return False`). `DatabaseAdapter.delete/archive` propagent l'exception. `exercise_service.py` et `logic_challenge_service.py` lèvent `ExerciseNotFoundError`/`ChallengeNotFoundError` pour entité introuvable.
- **Tests alignés** : `test_logic_challenge_service.py` — 6 tests migrés vers `pytest.raises(ChallengeNotFoundError/DatabaseOperationError)`. 82 tests unitaires verts.

---

## [2.3.0-alpha.2] - 2026-03-03

### Refactored — Phase 4 : Industrialisation (4.1-4.4)

- **4.1 TypedDict complétés** : 8 nouveaux TypedDict dans `app/core/types.py` — `UserProgressDict`, `ChallengesProgressDict`, `ChallengeStatsDict`, `AuditLogPageDict`, `ModerationDict`, `AdminReportDict`, `AdminUserItemDict`, `AdminUserListDict`. Appliqués à `admin_stats_service`, `challenge_service`, `user_service`, `admin_user_service`.
- **4.2 `constants.py` découpé** : `app/core/constants_challenge.py` extrait (challenge types, aliases, `normalize_challenge_type`, `AGE_GROUPS_DB`). `constants.py` devient un hub re-exportant pour la compatibilité ascendante.
- **4.3 `format_paginated_response` adopté** : `exercise_service.py` et `challenge_handlers.py` utilisent l'utilitaire centralisé. Duplication page/has_more éliminée.
- **4.4 `enum_mapping.py` adopté** : `challenge_handlers.py` → `age_group_exercise_from_api`. `challenge_list_params.py` → `challenge_type_from_api` + `age_group_challenge_from_api`. Import différé `normalize_age_group_for_db` éliminé.

---

## [2.3.0-alpha.1] - 2026-03-03

Audit architecture backend complet — Phases 0 à 3.
Résultat : 651 tests, 0 failures. Black OK. Aucune régression fonctionnelle.

### Security (Phase 0)

- **S1 — CSRF bypass supprimé** : suppression du kill-switch `TESTING` env var dans `middleware.py` et `csrf.py`. Les tests utilisent désormais `unittest.mock.patch` session-scoped dans `conftest.py`. Test de régression `test_testing_env_does_not_bypass_csrf` ajouté.
- **S2 — Injection SQL neutralisée** : garde `isalnum()` ajoutée sur `__tablename__` dans `safe_delete` fallback SQL de `app/db/transaction.py`.
- **S3 — Credentials DB par défaut bloquées** : `POSTGRES_PASSWORD` ajouté à `_validate_production_settings` — valeurs `""`, `"postgres"`, `"password"` rejetées en production.
- **S4 — DATABASE_URL masquée dans les logs** : `urlparse` utilisé pour logger uniquement `host:port/db`, credentials jamais exposées.
- **S5 — Except handlers auth réordonnés** : `ExpiredSignatureError` en premier (message précis). `InvalidSignatureError` supprimé (inexistant dans python-jose). Messages d'erreur spécifiques à l'expiration.

### Refactored — Phase 1 : Standardisation des patterns

- **CC1** : Parsing body unifié — `parse_json_body`/`parse_json_body_any` partout. 5 `await request.json()` bruts remplacés.
- **CC2** : Réponses erreur unifiées — `api_error_response()` partout. 2 `JSONResponse({error:...})` ad-hoc éliminés.
- **CC3** : 26 `traceback.print_exc()` → `logger.error(..., exc_info=True)` dans 7 fichiers handlers.
- **CC4** : Type hints `-> JSONResponse`/`-> Response` ajoutés sur ~80 handlers.
- **CC5** : `get_cookie_config()` extraite dans `app/core/security.py` — 4 duplications éliminées.
- **CC6** : `validate_password_strength()` extraite dans `app/core/security.py` — 4 duplications éliminées.
- **A6** : `_ROUTE_REGISTRY` unique dans `middleware.py` — auth-whitelist et CSRF-exempt dérivés automatiquement, plus de dérive entre registres.
- **P1** : CORS origins unifié → `settings.BACKEND_CORS_ORIGINS` comme source unique.
- **P2+P3** : `normalize_age_group` O(n×m) → O(1) via dict pré-calculé. `_CSRF_EXEMPT_NORMALIZED` frozenset constant.
- **I3** : `AdminService` — 28 imports inline → 1 import top-level dans `admin_handlers.py`.

### Refactored — Phase 2 : Services légers

- **2.1** : User lookups consolidés — 3 fonctions `auth_service.py` délèguent à `UserService`. 9 `db.query(User).filter(...)` inline → `UserService.get_user()`.
- **2.2+2.8** : `auth_service.py` découplé de FastAPI — `fastapi.HTTPException` éliminé, retours en tuples `(result, error, status)`. 33 tests adaptés.
- **2.3** : `_apply_challenge_filters()` extraite dans `challenge_service.py` — 2×40 lignes dupliquées → 1 fonction partagée.
- **2.4** : `get_user_stats_for_dashboard` (~200 lignes) → orchestrateur + 4 sous-méthodes privées.
- **2.5** : Suppression `app/db/queries.py` (403 lignes dead code legacy) et `tests/unit/test_queries.py` (13 tests obsolètes).
- **2.6** : Suppression `LoggingLevels` et `ExerciseStatus` (dead code dans `constants.py`).
- **2.7** : `VALID_THEMES`/`VALID_LEARNING_STYLES` → `constants.py` (frozenset). `FRONTEND_URL` → champ Pydantic `config.py`. 8 `os.getenv` dupliqués éliminés.
- **2.9** : Nouveau module `app/core/types.py` avec 7 TypedDict (`TokenResponse`, `DashboardStats`, `ChartData`, `PaginatedResponse`, etc.).

### Refactored — Phase 3 : Refactoring des God Objects

- **3.1 — ChallengeAnswerService** : 7 algorithmes de comparaison (SEQUENCE, DEDUCTION, PROBABILITY, CHESS, GRAPH, VISUAL, PATTERN) + 4 helpers extraits de `challenge_handlers.py` vers `app/services/challenge_answer_service.py`. Handler réduit à délégateur. +47 tests de caractérisation.
- **3.2 — ChatService** : 120 lignes dupliquées entre `chat_api` et `chat_api_stream` extraites dans `app/services/chat_service.py` (`detect_image_request`, `generate_image`, `build_chat_config`, `cleanup_markdown_images`). Import `AsyncOpenAI`/`OPENAI_AVAILABLE` sécurisé via `try/except ImportError`. +19 tests de caractérisation.
- **3.3 — AdminService** : God class 1585 lignes → façade ~65 lignes + 4 sous-services spécialisés (`AdminConfigService`, `AdminStatsService`, `AdminUserService`, `AdminContentService`) + `admin_helpers.py`. Compatibilité `admin_handlers.py` préservée (Strangler Fig).
- **3.4 — exercise_generator** : 4 helpers partagés extraits dans `exercise_generator_helpers.py` (`init_exercise_context`, `build_base_exercise_data`, `default_addition_fallback`, `apply_test_title`). Duplication blocs d'initialisation et fallbacks éliminée. +25 tests de caractérisation.

### Tests

- +91 tests ajoutés (47 challenge, 25 exercise generator, 19 chat service)
- Total : 651 tests, 0 failures, 2 skips
- Suppression 13 tests obsolètes (`test_queries.py`)

### Removed

- `app/db/queries.py` — 403 lignes de dead code legacy non référencées
- `server/handlers/admin_handlers_utils.py` — fichier fantôme déjà remplacé par `admin_helpers.py`
- `tests/unit/test_queries.py` — 13 tests sur code supprimé

---

## [2.2.2-alpha.1] - 2026-02-26

### Fixed

- **LocalProtocolError sur POST /api/recommendations/generate** : `RequestIdMiddleware` converti de `BaseHTTPMiddleware` en middleware ASGI pur pour éviter l'erreur "Can't send data when our state is ERROR" (problème connu BaseHTTPMiddleware + streaming/déconnexion client).

### Changed — Refactoring handlers → services

- **auth_handlers** : `verify_email` et `api_reset_password` passent par `AuthService` (verify_email_token, reset_password_with_token) — plus d'accès DB direct
- **user_handlers** : Réponse `PUT /api/users/me` inclut `is_email_verified` pour éviter la bannière « compte non validé » après mise à jour du profil

### Tests

- `test_verify_email_success`, `test_verify_email_invalid_token` (test_auth_flow.py)
- `test_update_user` : assertion régression sur `is_email_verified`

### Documentation

- `docs/03-PROJECT/INVENTAIRE_HANDLERS_DB_DIRECTE.md` : auth_handlers marqué refactoré (26/02)

---

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

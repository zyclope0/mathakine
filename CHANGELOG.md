# Changelog

Toutes les modifications notables du projet sont documentÃ©es dans ce fichier.

Le format est basÃ© sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et le projet adhÃ¨re au [Semantic Versioning](https://semver.org/lang/fr/) avec suffixe `-alpha.N` pour les versions alpha.

## Jalons internes du refactor backend (hors release produit)

- Cette section suit l'itÃ©ration interne de refactor backend centrÃ©e sur
  `exercise`, `auth` et `user`.
- Ces versions ne remplacent pas les versions produit publiees ci-dessous.
- Iteration `exercise/auth/user` cloturee en `1.0.0`.
- Iteration `challenge/admin/badge` cloturee en `1.0.0`.
- References detaillees :
  - [`exercise/auth/user`](docs/03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/VERSIONING_BACKEND_REFACTOR_EXERCISE_AUTH_USER_2026-03-08.md)
  - [`challenge/admin/badge`](docs/03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/VERSIONING_BACKEND_REFACTOR_CHALLENGE_ADMIN_BADGE_2026-03-10.md)

## [Unreleased]

### Notes
- Rien pour le moment.

## [3.1.0-alpha.8] - 2026-03-11

### Changed
- Release de consolidation backend centree sur `challenge`, `admin` et `badge`, avec handlers aminci et facades applicatives explicites sur les boundaries HTTP du scope.
- Les endpoints admin de lecture, de mutation users/config, de contenu et les endpoints badge publics/utilisateur passent desormais par des services applicatifs dedies, sans changer les contrats HTTP publics.
- Les tests API de preuve ont ete completes sur les endpoints admin content et badge afin de verifier le wiring reel des routes mutate/public du scope.

### Fixed
- La collision entre fixtures auth/admin et cleanup global des tests a ete supprimee; les namespaces de fixtures reserves ne sont plus captures par le nettoyage generique.
- Les tests challenge qui dependaient d'une selection non deterministe de `challenges[0]` utilisent desormais une fixture stable avec `correct_answer` connu.
- La stabilite locale du tree a ete retablie en excluant `tests/api/test_admin_auth_stability.py` des gates standard tant qu'il lance `pytest` dans `pytest` avec couverture.

### Notes
- Cette release reste en `alpha` : l'iteration backend `challenge/admin/badge` est cloturee en interne, mais le produit continue d'evoluer et garde des hotspots structurels hors scope (`challenge_validator.py`, `badge_service.py`, `admin_content_service.py`, `admin_stats_service.py`).

## [3.1.0-alpha.7] - 2026-03-09

### Changed
- Release de fiabilisation backend centree sur `exercise`, `auth` et `user`,
  avec handlers aminci, services applicatifs clarifies et boundaries HTTP
  preserves.
- Gestion du compte plus robuste : profil, sessions, export RGPD et suppression
  de compte passent desormais derriere une boundary `user` plus propre.
- Authentification plus robuste : login, refresh, verification, forgot/reset et
  invalidation post-reset ou post-changement de mot de passe ont ete
  reindustrialises sans changer les contrats HTTP publics.

### Fixed
- Reset password : les anciens `access_token` et `refresh_token` emis avant la
  reinitialisation sont desormais rejetes.
- Reset password : les autres sessions actives de l'utilisateur sont
  revoquees, et un ancien onglet doit se reconnecter au prochain controle
  protege.
- Changement de mot de passe depuis le profil : alignement sur le meme
  mecanisme de revocation (`password_changed_at` + rejet des anciens tokens).
- `POST /api/auth/resend-verification` revient a une reponse generique
  compatible sur email mal forme, sans fuite d'information par validation.
- `GET /api/users/me/export` est recable sur le bon handler HTTP et couvre
  desormais explicitement par un test API.

### Notes
- Cette release reste en `alpha` : l'iteration backend `exercise/auth/user` est
  maintenant cloturee en interne, mais le produit continue d'evoluer vite et
  garde encore des reliquats UX et des chantiers backend pour l'iteration
  suivante.

## [3.1.0-alpha.6] - 2026-03-07

### Added
- F07 â€” Courbe d'Ã©volution temporelle : endpoint `GET /api/users/me/progress/timeline?period=7d|30d`, widget Â« Ã‰volution temporelle Â» dans l'onglet Progression du dashboard (tendance succÃ¨s %, volume tentatives, sÃ©lecteur 7j/30j)
- API `by_category` : champs `attempts` et `correct` pour le graphique volume
- F32 â€” Session entrelacÃ©e (interleaving) : endpoint `GET /api/exercises/interleaved-plan`, service dÃ©diÃ©, CTA Quick Start, flux session (`/exercises/interleaved` puis `/exercises/{id}?session=interleaved`)
- F35 â€” SÃ©curitÃ© logs DB : redaction des secrets sur l'URL SQLAlchemy loggÃ©e au dÃ©marrage (`redact_database_url_for_log()`), couverture unitaire dÃ©diÃ©e

### Changed
- Dashboard Progression : Â« Progression par type Â» remplacÃ© par Â« Volume par type d'exercice Â» (bar chart horizontal, tentatives par type)
- Ã‰volution temporelle : dates lisibles sans chevauchement (labels horizontaux, interval adaptatif 7j/30j, tooltip date complÃ¨te)
- `POST /api/exercises/generate` : auth optionnelle pour permettre la rÃ©solution adaptative de `age_group` quand `adaptive=true` (correctif de non-rÃ©gression F05/F32)

---

## [3.1.0-alpha.5] - 2026-03-07

### Fixed
- `test_create_user_token` : TypeError `int(None)` â€” test utilise dÃ©sormais un utilisateur persistÃ© via `db_session`
- `create_user_token` : garde dÃ©fensive si `user.id` est None
- CI : black (latex_utils.py), prettier (10 fichiers frontend)

### Changed
- Hero page d'accueil : LogoBadge, slogan Â« Apprendre sÃ©rieusement, sans perdre le plaisir Â», 2 CTAs, cartes glassmorphism
- Header : bouton Assistant dans la navigation
- Pages Exercices et DÃ©fis : toolbars compactes pour filtres et gÃ©nÃ©rateur
- Modal exercice : hiÃ©rarchie visuelle, contraste bouton Valider, scrollbar et espacement
- Sanitisation LaTeX : correction `\frac{1}{8}81` â†’ `\frac{1}{8} 81` (espace manquant)
- F33 Growth Mindset : copywriting feedback d'Ã©chec harmonisÃ© FR/EN (effort + stratÃ©gie) sur ExerciseSolver, ExerciseModal, ChallengeSolver, DiagnosticSolver
- F33 Growth Mindset : factorisation UI avec composant partagÃ© `GrowthMindsetHint` (rÃ©duction duplication/no-DRY)

---

## [3.1.0-alpha.4] - 2026-03-07

### Added
- F02 â€” DÃ©fis quotidiens : 3 objectifs par jour (volume, type spÃ©cifique, dÃ©fis logiques), widget sur le dashboard, bonus XP Ã  la complÃ©tion
- Documentation technique F02 (F02_DEFIS_QUOTIDIENS.md, F02_DAILY_CHALLENGES_WIDGET.md)

### Changed
- Refactor dashboard : Vue d'ensemble allÃ©gÃ©e (DÃ©fis du jour + SÃ©rie en cours cÃ´te Ã  cÃ´te), Progression (4 graphiques uniquement), nouvel onglet Mon Profil (Niveau, badges, stats, tempo, journal)
- Onglet DÃ©tails renommÃ© en Mon Profil
- DailyChallengesWidget : design Anti-Cheap (fonds neutres, accent sur icÃ´nes, pluralisation correcte, badges XP stylisÃ©s)
- Uniformisation hauteur des widgets DÃ©fis du jour et SÃ©rie en cours (grille flex)

### Removed
- LeaderboardWidget retirÃ© de la Vue d'ensemble (dÃ©jÃ  accessible via navbar)
- LevelEstablishedWidget et bloc Stats dÃ©placÃ©s vers l'onglet Mon Profil
- LevelIndicator dÃ©placÃ© de Progression vers Mon Profil

---

## [3.1.0-alpha.3] - 2026-03-06

### Added
- Documentation technique de rÃ©fÃ©rence complÃ¨te pour les modules F03 (Test de diagnostic initial), F04 (RÃ©visions espacÃ©es) et F05 (Adaptation dynamique de difficultÃ©).
- Audit complet de la documentation (`INDEX.md`, `ROADMAP_FONCTIONNALITES`, etc.) pour reflÃ©ter l'Ã©tat rÃ©el du code et archiver les anciens documents dans `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/`.

### Fixed
- L'adaptation dynamique de la gÃ©nÃ©ration d'exercices (F05) prend dÃ©sormais correctement en compte les proxies pour les opÃ©rations `MIXTE` et `FRACTIONS`.
- Le mode de rÃ©ponse "QCM" ou "Saisie Libre" est maintenant dÃ©terminÃ© par le Frontend en fonction du niveau IRT prouvÃ© de l'utilisateur (`useIrtScores()`), et non plus par la difficultÃ© thÃ©orique de l'exercice, garantissant un "scaffolding" pÃ©dagogique correct.
- Les endpoints manquants dans la documentation ont Ã©tÃ© ajoutÃ©s et validÃ©s (Endpoints Diagnostic, Admin, Sessions).

### Changed
- Refactor des rÃ¨gles de documentation : La vÃ©ritÃ© terrain est le code. Centralisation des documentations d'architecture dans `README_TECH.md`.

---

## [3.0.0-alpha.3] - 2026-03-04

### Added
- F03 â€” Test de diagnostic initial adaptatif (IRT) : 10 questions sur 4 types, algo adaptatif, rÃ©sultats par type, page `/diagnostic`, section dans les ParamÃ¨tres
- IntÃ©gration diagnostic â†’ recommandations (difficultÃ© mÃ©diane calculÃ©e aprÃ¨s Ã©valuation)

### Fixed
- `[TEST-ZAXXON]` affichÃ© dans les titres et explications d'exercices (prÃ©fixe technique supprimÃ©)
- Choix dupliquÃ©s dans les exercices de division (ex: deux "11") â€” dÃ©duplication via `generate_smart_choices`
- Erreur 500 Ã  la fin du diagnostic (`DetachedInstanceError` SQLAlchemy) â€” donnÃ©es extraites dans le contexte de session
- Table `diagnostic_results` absente en base de donnÃ©es â€” migration `20260304_diagnostic` appliquÃ©e
- `chat_service.py` â€” `NameError: name 'x' is not defined` dans la f-string du prompt LaTeX (accolades et backslashes Ã©chappÃ©s)

### Changed
- Environnements de rÃ©solution (ExerciseSolver, ChallengeSolver, DiagnosticSolver, ExerciseModal) : couleurs hardcodÃ©es (`bg-slate-900`, `text-white`, `bg-white/5`â€¦) remplacÃ©es par variables sÃ©mantiques (`bg-card`, `text-foreground`, `bg-secondary/50`â€¦) â€” compatibilitÃ© avec tous les thÃ¨mes
- `MathText.tsx` : `prose-invert` â†’ `prose-neutral dark:prose-invert` + `text-inherit` â€” le texte hÃ©rite la couleur du thÃ¨me courant

---

## [2.5.0-alpha.2] - 2026-03-04

### Mission Anti-Cheap â€” Refonte UI Premium EdTech (Pages Exercice, DÃ©fi & Modal)

#### Nouveaux composants
- `UnifiedExerciseGenerator` : gÃ©nÃ©rateur Rapide/IA unifiÃ© avec switch Â« Mode IA âœ¨ Â» (Progressive Disclosure) â€” remplace les deux gÃ©nÃ©rateurs sÃ©parÃ©s
- `CompactListItem` : composant partagÃ© pour la vue liste exercices/dÃ©fis â€” Ã©limine la duplication
- `useAIExerciseGenerator` : hook SSE encapsulant toute la logique de gÃ©nÃ©ration IA streaming
- `lib/utils/animation.ts` : utilitaire `getStaggerDelay()` pour les animations en cascade
- `lib/utils/format.ts` : helper `isAiGenerated()` â€” dÃ©tection unifiÃ©e des contenus IA

#### ExerciseSolver â€” Page Exercice pleine page
- **Focus Board** : conteneur glassmorphism central (`bg-slate-900/60 backdrop-blur-xl border-white/20 rounded-3xl`) qui sort le contenu du fond spatial
- **Header** : bouton retour discret en haut Ã  gauche, tags centrÃ©s, titre `text-3xl` centrÃ©
- **Tuiles de rÃ©ponse** : `bg-white/10 border-white/20`, hover avec Ã©lÃ©vation, glow violet sur la sÃ©lection
- **Bouton Valider** : Ã©tat dÃ©sactivÃ© smart (`bg-slate-800 text-slate-400`) / Ã©tat actif primary avec glow
- **Success state** : vert emerald vibrant (`bg-emerald-500/20 border-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.3)]`), explication en Â« fiche de savoir Â» (`border-l-4 border-primary`), boutons hiÃ©rarchisÃ©s (primaire / secondaire discret)

#### ChallengeSolver â€” Page DÃ©fi pleine page
- **Focus Board** : mÃªme style glassmorphism, `rounded-t-3xl` (collÃ© Ã  la Command Bar)
- **Header** : `DÃ©fi #XXXX` discret (`text-sm font-mono`), titre star `text-3xl md:text-4xl font-bold text-white`
- **BoÃ®tes internes** : description, question, visualisations dans `bg-white/5 border-white/10 rounded-xl`
- **Command Bar** : zone de rÃ©ponse collÃ©e au Focus Board (`bg-slate-950/80 rounded-b-3xl border-t-0`) â€” plus de flottement
- **Bouton Valider** : mÃªme logique disabled/primary que ExerciseSolver
- **Bouton Indice** : style Â« bouÃ©e de sauvetage Â» (`border-amber-500/30 text-amber-400 hover:bg-amber-500/10`)

#### ExerciseModal
- Fermeture au clic sur le backdrop (`onPointerDownOutside`) â€” comportement natif Dialog Radix restaurÃ©
- Bouton X intÃ©grÃ© dans le flex header (suppression de `absolute`)

#### Fix critique DnD â€” `FocusBoard` hors composant
- `FocusBoard` dÃ©clarÃ© au niveau module (pas inline dans la fonction) dans `ChallengeSolver`
- Corrige un bug de remontage React qui dÃ©truisait le `DndContext` dnd-kit Ã  chaque re-render, cassant le drag & drop des puzzles

#### Nettoyage DRY
- Suppression `ExerciseGenerator.tsx` (code mort remplacÃ© par `UnifiedExerciseGenerator`)
- Suppression `CHALLENGE_TYPES` obsolÃ¨te dans `exercises.ts`
- `debugLog`/`debugError` uniformisÃ©s dans les gÃ©nÃ©rateurs IA

---

## [2.4.0-alpha.2] - 2026-03-04

### Added
- `LogoMathakine` : composant React inline SVG â€” thÃ©misation complÃ¨te via CSS vars (`--logo-text`, `--logo-highlight`, `--logo-glow`, `--logo-accents`) dÃ©finies dans `globals.css` pour chaque thÃ¨me (light, dark, dune, forÃªt, dinoâ€¦)
- `public/logo-m.svg` : icÃ´ne M autonome (viewBox 100Ã—100) â€” fond sombre, gradient violet (`#c4b5fd` â†’ `#7c3aed`), point dorÃ© lumineux, reflet blanc â€” compatible format maskable PWA
- `manifest.json` : entrÃ©e SVG en tÃªte (`"sizes": "any"`, `"purpose": "any maskable"`) â€” les navigateurs modernes (Chrome 93+, Firefox, Safari 16+) l'utilisent en prioritÃ© pour icÃ´ne PWA et onglets
- Favicon SVG prioritaire dans `app/layout.tsx` (avant les fallbacks PNG 192/512)
- `.badge-card-glass` dans `globals.css` : glassmorphism sur les cartes badges â€” `bg-card/60`, `backdrop-blur-md`, bordure `white/8`, override `card-spatial-depth` background
- `.badge-icon-glow` dans `globals.css` : halo radial derriÃ¨re l'icÃ´ne des badges obtenus (gradient violet/amber)

### Changed
- `Header.tsx` : texte gradient "Mathakine" remplacÃ© par `<LogoMathakine className="h-8 w-auto" />` â€” logo complet thÃ©misÃ© dans la navbar
- `app/page.tsx` (hero) : `<h1>Mathakine</h1>` remplacÃ© par `<LogoMathakine>` responsive (`w-72` mobile â†’ `w-[480px]` desktop)
- `BadgeCard.tsx` (earned compact) : layout refactorisÃ© en `flex-col` centrÃ© â€” grande icÃ´ne `size="md"`, nom tronquÃ© sur 1 ligne, mÃ©daille + points en dessous, cÅ“ur/coche en overlay `absolute top-right`
- `BadgeCard.tsx` (locked) : overlay `<Lock>` Lucide centrÃ© en `absolute inset-0` sur `BadgeIcon` pour signaler visuellement les badges verrouillÃ©s
- `BadgeCard.tsx` : taille des icÃ´nes cÅ“ur et coche portÃ©e Ã  `h-3.5 w-3.5` pour meilleure lisibilitÃ©

---

## [2.4.0-alpha.1] - 2026-03-04

### Added
- Bandeau motivationnel sur la page badges (message adaptÃ© au % de progression, 5 niveaux)
- Confetti au premier chargement aprÃ¨s obtention d'un nouveau badge (canvas-confetti, localStorage)
- Widget "Ã€ portÃ©e de main" : top 3 badges en cours Ã  â‰¥50% de progression, visible sans naviguer
- Composant `DifficultyMedal` extrait de `BadgeCard` â€” Ã©limine la rÃ©pÃ©tition `if bronze/silver/gold`

### Changed
- Cartes "Ma collection" : layout "list-item" compact (icÃ´ne | nom+pts | actions) â€” alignement vertical, nom tronquÃ© sur 1 ligne
- IcÃ´ne Pin remplacÃ©e par CÅ“ur (rempli si Ã©pinglÃ©, disparaÃ®t au survol sinon)
- Date "obtenu le" dÃ©placÃ©e en zone dÃ©pliable (survol uniquement, plus dans la vue miniature)
- Grille badges earned : `gap-3` au lieu de `gap-4`
- `BadgeGrid` : prop `compactEarned` pour activer le mode liste
- MÃ©daille difficultÃ© dans la vue compacte : taille `h-4 w-4` pour meilleure lisibilitÃ©

### Fixed
- `leaderboard/page.tsx` : Ã©tat vide/erreur migrÃ© vers `EmptyState` (cohÃ©rence design system)
- `challenges/page.tsx` : badge compteur filtres actifs incluait `orderFilter` + `hideCompleted`
- `globals.css` : animations `animate-fade-in-up-delay-4` et `-delay-5` manquantes ajoutÃ©es

## [2.3.0] - 2026-03-03

### Audit Frontend Industrialisation â€” ClÃ´ture (Phases 0â†’4 complÃ¨tes)

Audit frontend lancÃ© le 22/02/2026, finalisÃ© le 03/03/2026.
**RÃ©sultat final : 61 tests Vitest, 0 failures. tsc 0 erreurs. ESLint clean.**

#### Phase 0 â€” DRY & Design System (constantes + inputs)

- **Centralisation constantes** : `lib/constants/exercises.ts`, `challenges.ts`, `badges.ts` â€” plus de hardcoding dans les modales admin et filtres de page
- **Variables CSS sidebar/charts** : `--sidebar-*`, `--chart-1..5` mappÃ©s dans `globals.css` (cohÃ©rence light/dark)
- **Inputs shadcn/ui** : remplacement de tous les `<input>` raw par `<Input>` dans les renderers de dÃ©fis visuels (`PatternRenderer`, etc.)
- **EmptyState badges** : gestion d'erreur standardisÃ©e + clÃ©s i18n FR/EN sur la page `/badges`

#### Phase 1 â€” Skeleton loaders & tokens sÃ©mantiques

- **DashboardWidgetSkeleton** : composant gÃ©nÃ©rique dans `DashboardSkeletons.tsx` â€” tous les widgets dashboard migrent vers ce squelette
- **Tokens sÃ©mantiques** : `--warning`, `--success`, `--info` ajoutÃ©s Ã  `globals.css`, composants `feedback.tsx`, `ChatbotFloating.tsx` mis Ã  jour
- **Dossier renommÃ©** : `lib/validations/` â†’ `lib/validation/` (nomenclature singulier)

#### Phase 2 â€” Import cn standardisÃ© + lazy loading + AIGeneratorBase

- **Import cn unifiÃ©** : `import { cn } from "@/lib/utils"` partout (~37 fichiers) â€” `@/lib/utils/cn` n'est plus importÃ© directement
- **Validation dÃ©rivÃ©e** : `lib/validation/exercise.ts` dÃ©rive ses arrays depuis `lib/constants/exercises.ts` via `Object.values()`
- **Skeleton lazy loading** : `app/page.tsx` â€” les composants `dynamic()` ont dÃ©sormais des skeletons dimensionnÃ©s (plus de `loading: () => null`)
- **AIGeneratorBase** : composant UI partagÃ© `components/shared/AIGeneratorBase.tsx` â€” les `AIGenerator.tsx` exercises + challenges en sont des wrappers fins

#### Phase 3 â€” Polish visual + i18n

- **Flip icon** : `VisualRenderer.tsx` â€” icÃ´ne Lucide `FlipHorizontal` Ã  la place du caractÃ¨re `â†”`
- **aria-label i18n** : boutons vue grille/liste dans `/exercises` et `/challenges` utilisent `t("viewGrid")` / `t("viewList")`
- **DefaultRenderer** : type badge + coloration syntaxique lÃ©gÃ¨re pour les donnÃ©es structurÃ©es
- **Animations charts** : `ProgressChart.tsx` + `DailyExercisesChart.tsx` â€” `isAnimationActive={!shouldReduceMotion}` (Recharts, contrÃ´lÃ© par `useAccessibleAnimation`)
- **Feature cards** : classe `card-spatial-depth` sur les cartes de fonctionnalitÃ©s de la page d'accueil

#### Phase 3.5 â€” ThÃ©matisation charts

- **ProgressChart.tsx** : toutes les couleurs hardcodÃ©es (`#7c3aed`, `rgba(18,18,26,0.95)`â€¦) remplacÃ©es par CSS variables (`var(--color-chart-1)`, `var(--color-border)`, `var(--color-popover)`, `var(--color-muted-foreground)`)
- **DailyExercisesChart.tsx** : idem â€” couleurs backend ignorÃ©es, chart 100% thÃ©matisÃ©

#### Phase 4 â€” AccessibilitÃ©

- **Alt badges** : `BadgeCard.tsx` + `app/badges/page.tsx` â€” `alt=""` â†’ `alt={badge.name || badge.code || "Badge"}` (texte descriptif)
- **DeductionRenderer.tsx** : `useAccessibleAnimation` intÃ©grÃ© â€” `transition-colors` conditionnel
- **GraphRenderer.tsx** : animations Framer Motion entrÃ©e (nÅ“uds/arÃªtes SVG) + stagger, contrÃ´lÃ©es par `shouldReduceMotion` ; couleurs CSS variables
- **CSS contraste Ã©levÃ©** : `accessibility.css` nettoyÃ© â€” bloc `.high-contrast` et doublons supprimÃ©s ; `@media (prefers-contrast: high)` alignÃ© sur les tokens shadcn/ui dans `globals.css`

---

## [2.3.0] - 2026-02-22

### Audit Architecture Backend â€” ClÃ´ture (Phases 0â†’4 complÃ¨tes)

Audit architecture backend lancÃ© le 03/03/2026, challengÃ© et finalisÃ© le 22/02/2026.
**RÃ©sultat final : 472 tests, 0 failures. black + isort + flake8 clean. mypy 0 erreurs.**

#### Challenge Phase 4.5 â€” Corrections post-audit

- **Imports top-level** : `DatabaseOperationError` dÃ©placÃ© de inline vers top-level dans `transaction.py`. `logger` rÃ©ordonnÃ© aprÃ¨s imports (E402) dans `transaction.py` et `adapter.py`.
- **Signatures black** : `safe_delete`/`safe_archive` reformatÃ©es (lignes > 88 chars).
- **isort** : tri corrigÃ© sur `user_service.py`, `user_handlers.py`, `adapter.py`.
- **`enhanced_server_adapter`** : `archive_exercise` signature corrigÃ©e (`return bool` â†’ `None`, docstring `Returns` â†’ `Raises`).
- **Imports inline rÃ©siduels** supprimÃ©s dans `exercise_service.py` et `logic_challenge_service.py`.

#### Dette technique documentÃ©e

Points non finalisÃ©s documentÃ©s dans `docs/03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/PLACEHOLDERS_ET_TODO.md` :
- `constants.py` dÃ©coupage partiel (challenge extrait, exercise/user restent)
- Couverture test intÃ©gration `DELETE /api/users/me` erreur DB

---

## [2.3.0-alpha.3] - 2026-02-22

### Refactored â€” Phase 4.5 : safe_delete/safe_archive â†’ exceptions

- **4.5 API exception-based** : `safe_delete`/`safe_archive` dans `transaction.py` lÃ¨vent `DatabaseOperationError` (plus de `return False`). `DatabaseAdapter.delete/archive` propagent l'exception. `exercise_service.py` et `logic_challenge_service.py` lÃ¨vent `ExerciseNotFoundError`/`ChallengeNotFoundError` pour entitÃ© introuvable.
- **Tests alignÃ©s** : `test_logic_challenge_service.py` â€” 6 tests migrÃ©s vers `pytest.raises(ChallengeNotFoundError/DatabaseOperationError)`. 82 tests unitaires verts.

---

## [2.3.0-alpha.2] - 2026-03-03

### Refactored â€” Phase 4 : Industrialisation (4.1-4.4)

- **4.1 TypedDict complÃ©tÃ©s** : 8 nouveaux TypedDict dans `app/core/types.py` â€” `UserProgressDict`, `ChallengesProgressDict`, `ChallengeStatsDict`, `AuditLogPageDict`, `ModerationDict`, `AdminReportDict`, `AdminUserItemDict`, `AdminUserListDict`. AppliquÃ©s Ã  `admin_stats_service`, `challenge_service`, `user_service`, `admin_user_service`.
- **4.2 `constants.py` dÃ©coupÃ©** : `app/core/constants_challenge.py` extrait (challenge types, aliases, `normalize_challenge_type`, `AGE_GROUPS_DB`). `constants.py` devient un hub re-exportant pour la compatibilitÃ© ascendante.
- **4.3 `format_paginated_response` adoptÃ©** : `exercise_service.py` et `challenge_handlers.py` utilisent l'utilitaire centralisÃ©. Duplication page/has_more Ã©liminÃ©e.
- **4.4 `enum_mapping.py` adoptÃ©** : `challenge_handlers.py` â†’ `age_group_exercise_from_api`. `challenge_list_params.py` â†’ `challenge_type_from_api` + `age_group_challenge_from_api`. Import diffÃ©rÃ© `normalize_age_group_for_db` Ã©liminÃ©.

---

## [2.3.0-alpha.1] - 2026-03-03

Audit architecture backend complet â€” Phases 0 Ã  3.
RÃ©sultat : 651 tests, 0 failures. Black OK. Aucune rÃ©gression fonctionnelle.

### Security (Phase 0)

- **S1 â€” CSRF bypass supprimÃ©** : suppression du kill-switch `TESTING` env var dans `middleware.py` et `csrf.py`. Les tests utilisent dÃ©sormais `unittest.mock.patch` session-scoped dans `conftest.py`. Test de rÃ©gression `test_testing_env_does_not_bypass_csrf` ajoutÃ©.
- **S2 â€” Injection SQL neutralisÃ©e** : garde `isalnum()` ajoutÃ©e sur `__tablename__` dans `safe_delete` fallback SQL de `app/db/transaction.py`.
- **S3 â€” Credentials DB par dÃ©faut bloquÃ©es** : `POSTGRES_PASSWORD` ajoutÃ© Ã  `_validate_production_settings` â€” valeurs `""`, `"postgres"`, `"password"` rejetÃ©es en production.
- **S4 â€” DATABASE_URL masquÃ©e dans les logs** : `urlparse` utilisÃ© pour logger uniquement `host:port/db`, credentials jamais exposÃ©es.
- **S5 â€” Except handlers auth rÃ©ordonnÃ©s** : `ExpiredSignatureError` en premier (message prÃ©cis). `InvalidSignatureError` supprimÃ© (inexistant dans python-jose). Messages d'erreur spÃ©cifiques Ã  l'expiration.

### Refactored â€” Phase 1 : Standardisation des patterns

- **CC1** : Parsing body unifiÃ© â€” `parse_json_body`/`parse_json_body_any` partout. 5 `await request.json()` bruts remplacÃ©s.
- **CC2** : RÃ©ponses erreur unifiÃ©es â€” `api_error_response()` partout. 2 `JSONResponse({error:...})` ad-hoc Ã©liminÃ©s.
- **CC3** : 26 `traceback.print_exc()` â†’ `logger.error(..., exc_info=True)` dans 7 fichiers handlers.
- **CC4** : Type hints `-> JSONResponse`/`-> Response` ajoutÃ©s sur ~80 handlers.
- **CC5** : `get_cookie_config()` extraite dans `app/core/security.py` â€” 4 duplications Ã©liminÃ©es.
- **CC6** : `validate_password_strength()` extraite dans `app/core/security.py` â€” 4 duplications Ã©liminÃ©es.
- **A6** : `_ROUTE_REGISTRY` unique dans `middleware.py` â€” auth-whitelist et CSRF-exempt dÃ©rivÃ©s automatiquement, plus de dÃ©rive entre registres.
- **P1** : CORS origins unifiÃ© â†’ `settings.BACKEND_CORS_ORIGINS` comme source unique.
- **P2+P3** : `normalize_age_group` O(nÃ—m) â†’ O(1) via dict prÃ©-calculÃ©. `_CSRF_EXEMPT_NORMALIZED` frozenset constant.
- **I3** : `AdminService` â€” 28 imports inline â†’ 1 import top-level dans `admin_handlers.py`.

### Refactored â€” Phase 2 : Services lÃ©gers

- **2.1** : User lookups consolidÃ©s â€” 3 fonctions `auth_service.py` dÃ©lÃ¨guent Ã  `UserService`. 9 `db.query(User).filter(...)` inline â†’ `UserService.get_user()`.
- **2.2+2.8** : `auth_service.py` dÃ©couplÃ© de FastAPI â€” `fastapi.HTTPException` Ã©liminÃ©, retours en tuples `(result, error, status)`. 33 tests adaptÃ©s.
- **2.3** : `_apply_challenge_filters()` extraite dans `challenge_service.py` â€” 2Ã—40 lignes dupliquÃ©es â†’ 1 fonction partagÃ©e.
- **2.4** : `get_user_stats_for_dashboard` (~200 lignes) â†’ orchestrateur + 4 sous-mÃ©thodes privÃ©es.
- **2.5** : Suppression `app/db/queries.py` (403 lignes dead code legacy) et `tests/unit/test_queries.py` (13 tests obsolÃ¨tes).
- **2.6** : Suppression `LoggingLevels` et `ExerciseStatus` (dead code dans `constants.py`).
- **2.7** : `VALID_THEMES`/`VALID_LEARNING_STYLES` â†’ `constants.py` (frozenset). `FRONTEND_URL` â†’ champ Pydantic `config.py`. 8 `os.getenv` dupliquÃ©s Ã©liminÃ©s.
- **2.9** : Nouveau module `app/core/types.py` avec 7 TypedDict (`TokenResponse`, `DashboardStats`, `ChartData`, `PaginatedResponse`, etc.).

### Refactored â€” Phase 3 : Refactoring des God Objects

- **3.1 â€” ChallengeAnswerService** : 7 algorithmes de comparaison (SEQUENCE, DEDUCTION, PROBABILITY, CHESS, GRAPH, VISUAL, PATTERN) + 4 helpers extraits de `challenge_handlers.py` vers `app/services/challenge_answer_service.py`. Handler rÃ©duit Ã  dÃ©lÃ©gateur. +47 tests de caractÃ©risation.
- **3.2 â€” ChatService** : 120 lignes dupliquÃ©es entre `chat_api` et `chat_api_stream` extraites dans `app/services/chat_service.py` (`detect_image_request`, `generate_image`, `build_chat_config`, `cleanup_markdown_images`). Import `AsyncOpenAI`/`OPENAI_AVAILABLE` sÃ©curisÃ© via `try/except ImportError`. +19 tests de caractÃ©risation.
- **3.3 â€” AdminService** : God class 1585 lignes â†’ faÃ§ade ~65 lignes + 4 sous-services spÃ©cialisÃ©s (`AdminConfigService`, `AdminStatsService`, `AdminUserService`, `AdminContentService`) + `admin_helpers.py`. CompatibilitÃ© `admin_handlers.py` prÃ©servÃ©e (Strangler Fig).
- **3.4 â€” exercise_generator** : 4 helpers partagÃ©s extraits dans `exercise_generator_helpers.py` (`init_exercise_context`, `build_base_exercise_data`, `default_addition_fallback`, `apply_test_title`). Duplication blocs d'initialisation et fallbacks Ã©liminÃ©e. +25 tests de caractÃ©risation.

### Tests

- +91 tests ajoutÃ©s (47 challenge, 25 exercise generator, 19 chat service)
- Total : 651 tests, 0 failures, 2 skips
- Suppression 13 tests obsolÃ¨tes (`test_queries.py`)

### Removed

- `app/db/queries.py` â€” 403 lignes de dead code legacy non rÃ©fÃ©rencÃ©es
- `server/handlers/admin_handlers_utils.py` â€” fichier fantÃ´me dÃ©jÃ  remplacÃ© par `admin_helpers.py`
- `tests/unit/test_queries.py` â€” 13 tests sur code supprimÃ©

---

## [2.2.2-alpha.1] - 2026-02-26

### Fixed

- **LocalProtocolError sur POST /api/recommendations/generate** : `RequestIdMiddleware` converti de `BaseHTTPMiddleware` en middleware ASGI pur pour Ã©viter l'erreur "Can't send data when our state is ERROR" (problÃ¨me connu BaseHTTPMiddleware + streaming/dÃ©connexion client).

### Changed â€” Refactoring handlers â†’ services

- **auth_handlers** : `verify_email` et `api_reset_password` passent par `AuthService` (verify_email_token, reset_password_with_token) â€” plus d'accÃ¨s DB direct
- **user_handlers** : RÃ©ponse `PUT /api/users/me` inclut `is_email_verified` pour Ã©viter la banniÃ¨re Â« compte non validÃ© Â» aprÃ¨s mise Ã  jour du profil

### Tests

- `test_verify_email_success`, `test_verify_email_invalid_token` (test_auth_flow.py)
- `test_update_user` : assertion rÃ©gression sur `is_email_verified`

### Documentation

- `docs/03-PROJECT/INVENTAIRE_HANDLERS_DB_DIRECTE.md` : auth_handlers marquÃ© refactorÃ© (26/02)

---

## [2.2.1-alpha.2] - 2026-02-25

Regroupement des avancÃ©es depuis 2.2.0-alpha.1.

### Added

- **Quick Win #1 â€” First Exercise < 90s** : accÃ¨s immÃ©diat aprÃ¨s inscription
  - Auto-login aprÃ¨s inscription + redirection vers `/dashboard`
  - PÃ©riode de grÃ¢ce 45 min pour utilisateurs non vÃ©rifiÃ©s (accÃ¨s complet)
  - Au-delÃ  : accÃ¨s aux exercices uniquement (dashboard, dÃ©fis, badges, classement restreints)
  - Bandeau Â« VÃ©rifiez votre email Â» pour dÃ©bloquer les fonctionnalitÃ©s
  - Navigation conditionnelle : liens masquÃ©s selon `access_scope`
  - `access_scope` et `is_email_verified` dans les rÃ©ponses login/me
- **Quick Win #2 â€” Onboarding pÃ©dagogique** : mini-diagnostic aprÃ¨s inscription/connexion
  - Page `/onboarding` : classe, groupe d'Ã¢ge, objectif, rythme
  - Champs BDD : `onboarding_completed_at`, `learning_goal`, `practice_rhythm`
  - Redirection post-login vers `/onboarding` si non complÃ©tÃ©
  - SystÃ¨me scolaire : Suisse romand (1H-11H) ou unifiÃ© (1-12), champ `grade_system`
- **Parcours guidÃ© (P1)** : bloc Â« Que veux-tu faire ? Â» en tÃªte du dashboard
  - 2 CTA : Un exercice / Un dÃ©fi â€” liens vers recommandation prioritaire ou fallback
  - Composant `QuickStartActions`, personnalisation via onboarding (Ã¢ge, objectif)
  - Recommandations : exclusion des exercices/dÃ©fis archivÃ©s
- **Analytics EdTech** : instrumentation et admin
  - `trackDashboardView`, `trackQuickStartClick`, `trackFirstAttempt`
  - POST /api/analytics/event, table `edtech_events`
  - Page admin `/admin/analytics` : KPIs, agrÃ©gats, filtres 7d/30d
  - Documentation : docs/02-FEATURES/EDTECH_ANALYTICS.md

### Changed

- Profil et paramÃ¨tres accessibles aux utilisateurs non vÃ©rifiÃ©s (modification email, renvoi lien)
- Init DB : `create_tables_with_test_data` utilise Alembic (`alembic upgrade head`)
- Formatage : Black et isort â€” alignement des fichiers pour la CI

### Fixed

- Ordre des dÃ©corateurs : `@require_auth` avant `@require_full_access`
- Recommandations : exercices et dÃ©fis archivÃ©s exclus du parcours guidÃ©

### Tests

- tests/api/test_unverified_access.py, test_admin_analytics.py
- frontend QuickStartActions.test.tsx (trackDashboardView, trackQuickStartClick)

---

## [2.2.0-alpha.1] - 2026-02-22

### Added

- Pages Ã€ propos, Contact, Politique de confidentialitÃ© (RGPD)
- Bouton de signalement (FeedbackFab) : exercices, dÃ©fis, bugs â€” icÃ´ne drapeau rouge
- Filtre par groupe d'Ã¢ge sur le classement
- Widget temps moyen par session sur le tableau de bord
- Recommandations : exclusion des exercices et dÃ©fis dÃ©jÃ  rÃ©ussis

### Fixed

- Chevauchement footer / chatbot / FeedbackFab (z-index)

### Changed

- Footer : nouveaux liens rapides (Ã€ propos, Contact, Politique de confidentialitÃ©)

---

## [2.1.0] - 2026-02-06

### Added

- Ordre alÃ©atoire et option Â« Masquer les rÃ©ussis Â» pour exercices et dÃ©fis
- Refonte badges : onglets En cours / Ã€ dÃ©bloquer, raretÃ©, Ã©pinglage
- DÃ©fis : parsing tolÃ©rant, types VISUAL multi-position
- ThÃ¨mes : Dune, ForÃªt, LumiÃ¨re, Dinosaures
- Classement (leaderboard)
- Export PDF/Excel des donnÃ©es
- Assistant mathÃ©matique (chatbot IA)
- Espace admin : contenu, modÃ©ration, paramÃ¨tres globaux, audit
- Monitoring Sentry, Prometheus
- Options d'accessibilitÃ© (contraste, texte, animations, mode Focus TSA/TDAH)

### Security

- CSRF, rate limiting, CORS, SecureHeaders
- Validation JWT (type=access)

---

## [2.0.0] et antÃ©rieur

Historique condensÃ© : exercices adaptatifs, dÃ©fis logiques, authentification, vÃ©rification email, badges, tableau de bord de base.

---

## Convention de versioning (alpha)

- **Format** : `MAJOR.MINOR.PATCH-alpha.N` (ex. `2.2.0-alpha.1`)
- **Alpha** : fonctionnalitÃ©s instables, changements frÃ©quents
- **IncrÃ©ment** : `alpha.N` Ã  chaque release alpha significative
- **Sortie alpha** : retirer le suffixe (ex. `2.2.0`)


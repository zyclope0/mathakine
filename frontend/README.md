# 🚀 Frontend Mathakine - Next.js

**Version produit visible** : 3.4.0-alpha.1 (alignée sur `frontend/package.json`)  
**Statut** : **alpha** — fonctionnel en démo / préprod ; l’appellation « production ready » n’est pas utilisée tant que la release n’est pas sortie d’alpha.  
**Framework** : Next.js 16.1.6 avec App Router  
**Language** : TypeScript (strict mode)

---

## 📋 **Table des Matières**

- [Installation](#installation)
- [Démarrer le Projet](#démarrer-le-projet)
- [Structure du Projet](#structure-du-projet)
- [Scripts Disponibles](#scripts-disponibles)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Composants](#composants)
- [Hooks](#hooks)
- [Stores](#stores)
- [Internationalisation (i18n)](#internationalisation-i18n)
- [Accessibilité](#accessibilité)
- [Thèmes](#thèmes)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [Contribution](#contribution)

---

## 🚀 **Installation**

### **Prérequis**

- Node.js 18+ (recommandé : 20+)
- npm ou yarn
- Backend Mathakine démarré sur `http://localhost:10000`

### **Installation des Dépendances**

```bash
cd frontend
npm install
```

### **Configuration**

Créer un fichier `.env.local` à la racine du dossier `frontend` :

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:10000
```

---

## 🎯 **Démarrer le Projet**

### **Mode Développement**

```bash
npm run dev
```

Le serveur démarrera sur **http://localhost:3000**

### **Build Production**

```bash
npm run build
npm start
```

### **Linter**

```bash
npm run lint
```

---

## 📁 **Structure du Projet**

```
frontend/
├── app/                          # Next.js App Router (routes plates)
│   ├── admin/                    # Espace admin (rôle archiviste)
│   ├── dashboard/                # Tableau de bord
│   ├── exercises/ + [id]/        # Exercices
│   ├── challenges/ + challenge/[id]/  # Défis
│   ├── badges/                   # Badges
│   ├── leaderboard/              # Classement
│   ├── profile/ + settings/      # Profil et préférences
│   ├── api/                      # API Routes Next.js (proxy backend + streaming)
│   ├── layout.tsx                # Layout racine
│   ├── page.tsx                  # Page d'accueil
│   └── globals.css               # Styles globaux + variables CSS thèmes
│
├── components/                    # Composants React
│   ├── ui/                       # Composants shadcn/ui
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   ├── exercises/                # Composants exercices
│   │   ├── ExerciseCard.tsx
│   │   ├── ExerciseGenerator.tsx
│   │   ├── ExerciseSolver.tsx
│   │   ├── ExerciseModal.tsx
│   │   └── AIGenerator.tsx
│   ├── challenges/               # Composants défis logiques
│   │   ├── ChallengeCard.tsx
│   │   ├── ChallengeSolver.tsx
│   │   ├── ChallengeModal.tsx
│   │   └── visualizations/       # Renderers visuels
│   ├── badges/                   # Composants badges
│   │   ├── BadgeCard.tsx
│   │   └── BadgeGrid.tsx
│   ├── dashboard/                # Composants dashboard
│   │   ├── StatsCard.tsx
│   │   ├── SpacedRepetitionSummaryWidget.tsx  # F04 — résumé révisions (lecture /api/users/stats)
│   │   ├── ProgressChart.tsx
│   │   ├── Recommendations.tsx
│   │   └── ...
│   ├── accessibility/            # Composants accessibilité
│   │   ├── AccessibilityToolbar.tsx
│   │   └── WCAGAudit.tsx
│   ├── layout/                   # Composants layout
│   │   ├── Header.tsx
│   │   └── Footer.tsx
│   ├── theme/                     # Composants thèmes
│   │   └── ThemeSelector.tsx
│   └── locale/                    # Composants i18n
│       └── LanguageSelector.tsx
│
├── hooks/                         # 35 custom hooks (React Query)
│   ├── useAuth.ts, useProfile.ts, useSettings.ts
│   ├── useExercises.ts, useExercise.ts, useSubmitAnswer.ts
│   ├── useChallenges.ts, useChallenge.ts, usePaginatedContent.ts
│   ├── useBadges.ts, useBadgesProgress.ts
│   ├── useUserStats.ts, useProgressStats.ts
│   ├── useRecommendations.ts, useLeaderboard.ts, useChat.ts
│   └── useAdmin*.ts              # 12 hooks admin
│
├── lib/                          # Utilitaires et configs
│   ├── api/                      # Clients API
│   │   └── client.ts             # Client API principal
│   ├── stores/                   # Zustand stores
│   │   ├── accessibilityStore.ts
│   │   ├── themeStore.ts
│   │   └── localeStore.ts
│   ├── hooks/                    # Hooks utilitaires
│   │   ├── useAccessibleAnimation.ts
│   │   └── useKeyboardNavigation.ts
│   ├── utils/                    # Utilitaires
│   │   ├── cn.ts                 # clsx + tailwind-merge
│   │   ├── exportPDF.ts         # Export PDF
│   │   └── exportExcel.ts       # Export Excel
│   └── constants/                # Constantes
│       ├── exercises.ts
│       └── challenges.ts
│
├── messages/                     # Traductions next-intl
│   ├── fr.json                   # Français
│   └── en.json                   # Anglais
│
├── types/                         # Types TypeScript
│   └── api.ts                    # Types API
│
├── scripts/                       # Scripts utilitaires
│   └── i18n/                     # Scripts i18n
│       ├── check-translations.js
│       ├── extract-hardcoded.js
│       └── validate-structure.js
│
├── __tests__/                     # Tests
│   ├── unit/                     # Tests unitaires
│   ├── integration/             # Tests d'intégration
│   └── e2e/                      # Tests E2E
│
├── styles/                        # Styles globaux
│   └── accessibility.css         # Styles accessibilité
│
├── public/                        # Assets statiques
│   └── ...
│
├── .env.local                    # Variables d'environnement
├── next.config.ts                # Config Next.js
├── tailwind.config.js            # Config Tailwind (via CSS)
├── tsconfig.json                 # Config TypeScript strict
└── package.json
```

---

## 📜 **Scripts Disponibles**

### **Développement**

```bash
npm run dev          # Démarrer serveur développement (Turbopack)
npm run build        # Build production
npm start            # Démarrer serveur production
npm run lint         # Linter ESLint
```

### **Tests**

```bash
npm run test              # Tests unitaires (Vitest)
npm run test:ui           # Tests avec UI interactive
npm run test:coverage    # Tests avec couverture
npm run test:e2e         # Tests E2E (Playwright)
npm run test:e2e:ui      # Tests E2E avec UI
npm run test:all         # Tous les tests
```

### **i18n**

```bash
npm run i18n:check       # Vérifier cohérence traductions
npm run i18n:extract     # Extraire textes hardcodés
npm run i18n:validate    # Valider structure JSON
npm run i18n:all         # Toutes les vérifications i18n
```

---

## ⚙️ **Configuration**

### **Variables d'Environnement**

Créer `.env.local` :

```env
# URL du backend API (variable principale utilisée par le client)
NEXT_PUBLIC_API_BASE_URL=http://localhost:10000

# Ancien nom encore accepté en secours dans le code : NEXT_PUBLIC_API_URL
# Pour production Render, pointer vers l’URL publique du backend.
```

### **TypeScript**

Configuration stricte dans `tsconfig.json` :

- `strict: true`
- `noUncheckedIndexedAccess: true`
- `noImplicitOverride: true`
- `exactOptionalPropertyTypes: true`

### **Next.js**

Configuration dans `next.config.ts` :

- Headers sécurité (X-Content-Type-Options, X-Frame-Options)
- Images optimisées (AVIF, WebP)
- Code splitting automatique
- Optimisation imports packages

### **Tailwind CSS**

Configuration via CSS dans `app/globals.css` :

- 7 thèmes (Spatial, Minimaliste, Océan, Dune, Forêt, Lumière, Dinosaures)
- Variables CSS pour couleurs
- Support dark mode

---

## 🏗️ **Architecture**

### **Stack Technique**

- **Framework** : Next.js 16.1.6 (App Router)
- **Language** : TypeScript (strict mode)
- **Styling** : Tailwind CSS v4 + shadcn/ui
- **State Management** :
  - TanStack Query v5 (server state)
  - Zustand (client state)
- **Animations** : Framer Motion (avec garde-fous neuro-inclusifs)
- **i18n** : next-intl
- **Tests** : Vitest (unit) + Playwright (E2E)

### **Patterns Utilisés**

- **Server Components** : Par défaut dans App Router
- **Client Components** : Avec `'use client'` pour interactivité
- **React Query** : Cache et synchronisation données serveur
- **Zustand** : État client léger (thèmes, accessibilité, locale)
- **Composition** : Composants réutilisables et composables

---

## 🧩 **Composants**

### **Composants UI (shadcn/ui)**

Tous les composants sont dans `components/ui/` :

- `Button` : Boutons avec variants (default, outline, ghost, link)
- `Card` : Cartes avec header, content, footer
- `Dialog` : Modales
- `Input` : Champs de saisie
- `Select` : Sélecteurs
- `Badge` : Badges
- `Progress` : Barres de progression

### **Composants Métier**

Voir [Architecture Frontend](../docs/04-FRONTEND/ARCHITECTURE.md) pour la documentation complète.

---

## 🪝 **Hooks**

### **Hooks API**

- `useAuth()` : Authentification (login, register, logout)
- `useExercises(filters?)` : Liste exercices avec filtres
- `useExercise(id)` : Exercice individuel
- `useChallenges(filters?)` : Liste défis logiques
- `useChallenge(id)` : Défi individuel
- `useBadges()` : Badges utilisateur et disponibles
- `useUserStats()` : Statistiques utilisateur
- `useRecommendations()` : Recommandations personnalisées

### **Hooks Utilitaires**

- `useAccessibleAnimation()` : Animations avec garde-fous accessibilité
- `useKeyboardNavigation()` : Navigation clavier

Voir [Architecture Frontend](../docs/04-FRONTEND/ARCHITECTURE.md) pour la liste complète des 35 hooks.

---

## 🗄️ **Stores**

### **Zustand Stores**

- `useAccessibilityStore()` : Préférences accessibilité
  - `highContrast`, `largeText`, `reducedMotion`, `dyslexiaMode`, `focusMode`
- `useThemeStore()` : Thème actuel
  - `theme`, `setTheme()`
- `useLocaleStore()` : Langue actuelle
  - `locale`, `setLocale()`

Tous les stores utilisent `persist` middleware pour sauvegarder dans `localStorage`.

---

## 🌐 **Internationalisation (i18n)**

### **Configuration**

- **Bibliothèque** : `next-intl`
- **Langues supportées** : FR (par défaut), EN
- **Fichiers** : `messages/fr.json`, `messages/en.json`
- **Provider** : `NextIntlProvider` dans `app/layout.tsx`

### **Utilisation**

```typescript
import { useTranslations } from 'next-intl';

function MyComponent() {
  const t = useTranslations('namespace');
  return <h1>{t('key')}</h1>;
}
```

### **Traduction des Données**

Les données (exercices, défis, badges) sont traduites via PostgreSQL JSONB :

- Colonnes `*_translations` dans les tables
- Extraction automatique selon `Accept-Language` header
- Fallback vers français si traduction manquante

Voir [Guide i18n](../docs/02-FEATURES/I18N.md) pour la documentation complète.

---

## ♿ **Accessibilité**

### **Standards**

- **WCAG 2.1 AAA** compliance
- Support lecteurs d'écran (ARIA labels, roles)
- Navigation clavier complète
- Contraste AAA (4.5:1 minimum)

### **Modes Disponibles**

- **Contraste élevé** : Améliore le contraste des couleurs
- **Texte agrandi** : Augmente la taille du texte
- **Réduction animations** : Désactive les animations
- **Mode dyslexie** : Police adaptée pour dyslexie
- **Mode Focus TSA/TDAH** : Réduit les distractions

### **Composants**

- `AccessibilityToolbar` : Barre d'outils flottante
- `WCAGAudit` : Audit automatique avec @axe-core/react

Voir [Guide Accessibilité](../docs/04-FRONTEND/ACCESSIBILITY.md) pour la documentation complète.

---

## 🎨 **Thèmes**

### **Thèmes Disponibles**

1. **Spatial** (par défaut) : Thème spatial avec couleurs violettes
2. **Minimaliste** : Design épuré noir et blanc
3. **Océan** : Tons bleus apaisants
4. **Dune** : Sable/ambre, réduction fatigue visuelle
5. **Forêt** : Verts doux, calme et focus
6. **Lumière** : Tons pêche/orangé, énergie douce
7. **Dinosaures** : Jungle préhistorique, verts lime

### **Utilisation**

```typescript
import { useThemeStore } from '@/lib/stores/themeStore';

function MyComponent() {
  const { theme, setTheme } = useThemeStore();
  return <button onClick={() => setTheme('ocean')}>Océan</button>;
}
```

Les thèmes sont appliqués via `data-theme` sur `<html>` et persistés dans `localStorage`.

---

## 🧪 **Tests**

### **Structure**

```
__tests__/
├── unit/              # Tests unitaires (Vitest)
├── integration/       # Tests d'intégration
└── e2e/               # Tests E2E (Playwright)
```

### **Exécution**

```bash
npm run test           # Tests unitaires
npm run test:e2e       # Tests E2E
npm run test:all       # Tous les tests
```

### **Couverture**

```bash
npm run test:coverage  # Générer rapport couverture
```

Voir [Guide Tests](./__tests__/README.md) pour la documentation complète.

---

## 🚀 **Déploiement**

### **Build Production**

```bash
npm run build
```

Le build génère un dossier `.next/` optimisé.

### **Variables d'Environnement Production**

```env
NEXT_PUBLIC_API_BASE_URL=https://mathakine.onrender.com
```

### **Render.com**

Le projet est configuré pour Render.com :

- Build command : `cd frontend && npm install && npm run build`
- Start command : `cd frontend && npm start`

---

## 🤝 **Contribution**

### **Workflow**

1. Créer une branche depuis `main`
2. Faire les modifications
3. Tester (`npm run test:all`)
4. Vérifier i18n (`npm run i18n:all`)
5. Créer une Pull Request

### **Standards de Code**

- TypeScript strict mode
- ESLint configuré
- Composants avec `'use client'` si nécessaire
- Accessibilité WCAG AAA
- Tests pour nouvelles fonctionnalités

### **Ajouter un Composant shadcn/ui**

```bash
npx shadcn@latest add [component-name]
```

---

## 📚 **Documentation Complémentaire**

La documentation frontend est centralisée dans `docs/04-FRONTEND/` :

- [Architecture](../docs/04-FRONTEND/ARCHITECTURE.md) — structure, stack, patterns
- [Design System](../docs/04-FRONTEND/DESIGN_SYSTEM.md) — composants layout standardisés
- [Accessibilité](../docs/04-FRONTEND/ACCESSIBILITY.md) — WCAG AAA, 5 modes
- [Animations](../docs/04-FRONTEND/ANIMATIONS.md) — composants spatiaux
- [PWA](../docs/04-FRONTEND/PWA.md) — Progressive Web App
- [Thèmes](../docs/02-FEATURES/THEMES.md) — 7 thèmes, variables CSS
- [i18n](../docs/02-FEATURES/I18N.md) — internationalisation next-intl

---

## 🐛 **Dépannage**

### **Erreurs Courantes**

**Erreur : `MISSING_MESSAGE`**

- Vérifier que la clé existe dans `messages/fr.json` et `messages/en.json`
- Exécuter `npm run i18n:check`

**Erreur : `Cannot find module`**

- Vérifier les paths alias dans `tsconfig.json`
- Redémarrer le serveur de développement

**Erreur : API non accessible**

- Vérifier `NEXT_PUBLIC_API_BASE_URL` dans `.env.local`
- Vérifier que le backend est démarré

---

## 📝 **Changelog**

### **v0.1.0** (Novembre 2025)

- ✅ Setup complet Next.js 16
- ✅ Authentification complète
- ✅ Pages principales (exercices, défis, dashboard, badges)
- ✅ i18n complet (interface + données)
- ✅ Accessibilité WCAG AAA
- ✅ 7 thèmes disponibles
- ✅ Tests unitaires et E2E

---

## 📄 **License**

Propriétaire - Mathakine

---

**Dernière mise à jour** : 06/03/2026

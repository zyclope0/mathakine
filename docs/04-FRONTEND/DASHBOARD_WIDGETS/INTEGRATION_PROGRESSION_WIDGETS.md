# Intégration des widgets de progression dans le dashboard

> Complété le 06/02/2026 — **MAJ 06/03/2026** (refactor onglets + F02)

## 📋 Résumé

Les endpoints de progression (`/api/users/me/progress`, `/api/users/me/challenges/progress`, `GET /api/daily-challenges`, `GET /api/diagnostic/status`) ont été intégrés dans le dashboard frontend.

**Structure actuelle (06/03/2026)** — Voir [REFACTOR_DASHBOARD_2026-03.md](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/REFACTOR_DASHBOARD_2026-03.md) :

**Onglet Vue d'ensemble :**
1. **QuickStartActions** — Parcours guidé "Que veux-tu faire ?"
2. **DailyChallengesWidget** (F02) — 3 défis du jour — col-span-8
3. **StreakWidget** — Série en cours — col-span-4 (à côté des défis)

**Onglet Progression :**
- **ChallengesProgressWidget** — Progression des défis logiques
- **CategoryAccuracyChart** — Précision par catégorie
- **ProgressChartLazy**, **DailyExercisesChartLazy** — Graphiques

**Onglet Mon Profil** (ex-Détails) :
- **LevelIndicator** — Niveau actuel (barre XP)
- **LevelEstablishedWidget** — Profil mathématique (badges IRT)
- **StatsCard** × 3 — Exercices, Taux, Défis
- **AverageTimeWidget** — Tempo moyen
- **RecentActivity** — Journal d'activité

**Retirés de la Vue d'ensemble :** LeaderboardWidget (déjà dans navbar), LevelEstablishedWidget, bloc Stats

**Composants liés (16/02, MAJ 24/03/2026)** :
- **Recommendations** (onglet Recommandations) — bouton ✓ « Marquer comme fait » via `POST /api/recommendations/complete`, hook `useRecommendations` (mutation `complete`), affichage initial borne a 6 cartes avec toggle local `Voir plus / Voir moins`

---

## 📁 Fichiers créés

### Hooks React Query

#### `frontend/hooks/useProgressStats.ts`
Hook pour récupérer les statistiques de progression exercices depuis `GET /api/users/me/progress`.

**Interface TypeScript :**
```typescript
interface ProgressStats {
  total_attempts: number;
  correct_attempts: number;
  accuracy: number;
  average_time: number;
  exercises_completed: number;
  highest_streak: number;
  current_streak: number;
  by_category: Record<string, {
    completed: number;
    accuracy: number;
  }>;
}
```

**Configuration :**
- Cache (staleTime): 2 minutes
- Refetch on window focus: activé

---

#### `frontend/hooks/useChallengesProgress.ts`
Hook pour récupérer la progression des défis depuis `GET /api/users/me/challenges/progress`.

**Interface TypeScript :**
```typescript
interface ChallengesProgress {
  completed_challenges: number;
  total_challenges: number;
  success_rate: number;
  average_time: number;
  challenges: Array<{
    id: number;
    title: string;
    is_completed: boolean;
    attempts: number;
    best_time: number | null;
  }>;
}
```

**Configuration :**
- Cache (staleTime): 2 minutes
- Refetch on window focus: activé

---

### Composants UI

#### `frontend/components/dashboard/StreakWidget.tsx`
Widget affichant la série actuelle et le record.

**Props :**
```typescript
interface StreakWidgetProps {
  currentStreak: number;
  highestStreak: number;
  isLoading?: boolean;
}
```

**Fonctionnalités :**
- Affichage du nombre de jours consécutifs
- Badge "Nouveau record !" si streak actuel = record
- Design gradient orange-rouge avec icône flamme
- Animation pulse pendant le chargement
- Message d'encouragement si streak > 0

---

#### `frontend/components/dashboard/DailyChallengesWidget.tsx` (06/03/2026)
Widget F02 — Affiche les 3 défis quotidiens (volume, type spécifique, défis logiques).

**Hook :** `useDailyChallenges()` — lit `GET /api/daily-challenges`

**Fonctionnalités :**
- 3 cartes par défi avec icônes (Calculator, Target, Swords, CheckCircle2)
- Progression X/Y, badge XP bonus, CTA "S'entraîner maintenant"
- Design Anti-Cheap : fonds neutres, accent uniquement sur icônes, pluralisation ICU

**Référence :** [F02_DAILY_CHALLENGES_WIDGET.md](F02_DAILY_CHALLENGES_WIDGET.md), [F02_DEFIS_QUOTIDIENS.md](../02-FEATURES/F02_DEFIS_QUOTIDIENS.md)

---

#### `frontend/components/dashboard/LevelEstablishedWidget.tsx` (06/03/2026)
Widget F05 — Affiche le statut du niveau IRT établi (diagnostic F03).

**Hook :** `useIrtScores()` — lit `GET /api/diagnostic/status`

**Fonctionnalités :**
- Si diagnostic complété : « Ton Profil Mathématique » + badges par type (Addition · Grand Maître, etc.)
- Si non : CTA « Faire l'évaluation »
- Badges : icônes Lucide (Plus, Minus, X, Divide), niveau en gras + fond `bg-primary/5`
- Design : `bg-card border-primary/20 shadow-sm rounded-xl`, bouton secondaire « Refaire l'évaluation »

**Emplacement :** Onglet Mon Profil (ex-Détails)

**Référence :** [F05_ADAPTATION_DYNAMIQUE.md](../02-FEATURES/F05_ADAPTATION_DYNAMIQUE.md)

---

#### `frontend/components/dashboard/ChallengesProgressWidget.tsx`
Widget affichant la progression des défis logiques.

**Props :**
```typescript
interface ChallengesProgressWidgetProps {
  completedChallenges: number;
  totalChallenges: number;
  successRate: number;
  averageTime: number;
  isLoading?: boolean;
}
```

**Fonctionnalités :**
- Barre de progression visuelle (X/Y défis)
- Pourcentage de complétion
- Taux de réussite avec icône cible
- Temps moyen avec icône horloge
- Message d'encouragement si aucun défi complété

---

#### `frontend/components/dashboard/CategoryAccuracyChart.tsx`
Widget affichant la précision par catégorie d'exercices.

**Props :**
```typescript
interface CategoryAccuracyChartProps {
  categoryData: Record<string, {
    completed: number;
    accuracy: number;
  }>;
  isLoading?: boolean;
}
```

**Fonctionnalités :**
- Barres de progression colorées par précision :
  - 90%+ : Vert (Excellent)
  - 70-89% : Bleu (Bien)
  - 50-69% : Jaune (Moyen)
  - < 50% : Rouge
- Tri par nombre d'exercices complétés (décroissant)
- Affichage du nombre d'exercices par catégorie
- Légende des couleurs

---

#### `frontend/components/dashboard/LeaderboardWidget.tsx` (15/02/2026)
Widget affichant le top 5 du classement par points.

**Données :** `useLeaderboard(5)` → `GET /api/users/leaderboard?limit=5`

**Fonctionnalités :**
- Top 5 avec rang (🥇🥈🥉), username, total_points
- Surlignage de l'utilisateur connecté ("Vous")
- Lien "Voir tout" vers page `/leaderboard`
- États loading et vide

**Emplacement :** Retiré du dashboard (06/03/2026) — classement accessible via navbar `/leaderboard`

---

## 🌍 Traductions ajoutées

### `frontend/messages/fr.json`

```json
{
  "dashboard": {
    "streak": {
      "title": "Série en cours",
      "days": "{count, plural, =0 {jour} =1 {jour} other {jours}}",
      "best": "Meilleure série",
      "record": "Nouveau record !",
      "keepGoing": "Continue comme ça ! Reviens demain pour maintenir ta série."
    },
    "challengesProgress": {
      "title": "Progression des défis",
      "completed": "complétés",
      "successRate": "Taux de réussite",
      "avgTime": "Temps moyen",
      "noChallengesYet": "Commence par relever ton premier défi !"
    },
    "categoryAccuracy": {
      "title": "Précision par catégorie",
      "noData": "Aucune donnée disponible. Commence à résoudre des exercices !",
      "exercises": "exerc.",
      "excellent": "Excellent",
      "good": "Bien",
      "fair": "Moyen"
    }
  }
}
```

### `frontend/messages/en.json`

Traductions anglaises équivalentes ajoutées.

---

## 🎨 Intégration dans le Dashboard

### Modification de `frontend/app/dashboard/page.tsx`

**Imports ajoutés :**
```typescript
import { useProgressStats } from '@/hooks/useProgressStats';
import { useChallengesProgress } from '@/hooks/useChallengesProgress';
import { StreakWidget } from '@/components/dashboard/StreakWidget';
import { ChallengesProgressWidget } from '@/components/dashboard/ChallengesProgressWidget';
import { CategoryAccuracyChart } from '@/components/dashboard/CategoryAccuracyChart';
```

**Hooks utilisés :**
```typescript
const { data: progressStats, isLoading: isLoadingProgress } = useProgressStats();
const { data: challengesProgress, isLoading: isLoadingChallenges } = useChallengesProgress();
```

**Placement des widgets (06/03/2026) :**
Voir [REFACTOR_DASHBOARD_2026-03.md](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/REFACTOR_DASHBOARD_2026-03.md) pour la structure complète.

**Vue d'ensemble — grille Défis + Série :**
```tsx
<div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-stretch">
  <div className="md:col-span-8 flex flex-col min-h-0">
    <DailyChallengesWidget />
  </div>
  <div className="md:col-span-4 flex flex-col min-h-0">
    <StreakWidget ... />
  </div>
</div>
```

**Layout responsive :**
- Mobile : 1 colonne (empilés)
- Desktop (md+) : Défis 8/12, Série 4/12, hauteur uniforme

---

## ✅ Tests effectués

### Build frontend
```bash
cd frontend && npm run build
```

**Résultat :** ✅ Build réussi en 55.5s
- ✅ TypeScript compilation : OK
- ✅ Pages générées : 19/19
- ✅ Aucune erreur ESLint
- ✅ Aucun warning TypeScript

### Endpoints backend
Les endpoints sont **déjà opérationnels** (implémentés lors de l'unification Starlette) :
- ✅ `GET /api/users/me/progress` → Handler `get_all_user_progress` dans `server/handlers/user_handlers.py`
- ✅ `GET /api/users/me/challenges/progress` → Handler `get_challenges_progress` dans `server/handlers/user_handlers.py`

---

## 🎯 Fonctionnalités implémentées

### 1. Série de jours consécutifs (Streak)
- ✅ Affichage du streak actuel
- ✅ Affichage du meilleur streak
- ✅ Badge "Nouveau record !" si streak actuel = record
- ✅ Message d'encouragement
- ✅ **Design adapté au thème** : Card avec bordure orange accentuée si streak > 0, compatible multi-thème (dark/light)
- ✅ **Animation Framer Motion** : Rotation de l'icône flamme au chargement
- ✅ **Accessibility** : Reduced motion respecté

### 2. Progression des défis
- ✅ Barre de progression visuelle (complétés/total) avec `Progress` de shadcn/ui
- ✅ Pourcentage de complétion
- ✅ Taux de réussite global dans box colorée (vert avec opacité)
- ✅ Temps moyen dans box colorée (bleu avec opacité)
- ✅ Message d'encouragement si 0 défi complété
- ✅ **Design cohérent** : Card standard avec `bg-card border-primary/20`
- ✅ **Animation** : Rotation de l'icône Trophy

### 3. Précision par catégorie
- ✅ Barres de progression avec `Progress` component de shadcn/ui
- ✅ **Badges colorés** par catégorie avec opacité (style cohérent avec `PerformanceByType`)
- ✅ Code couleur : Vert (90%+), Bleu (70-89%), Jaune (50-69%), Rouge (<50%)
- ✅ Tri par nombre d'exercices complétés
- ✅ Badge "Excellent" pour accuracy >= 90%
- ✅ Légende explicative avec points colorés
- ✅ Traduction des noms de catégories via `next-intl`
- ✅ Recalcul des libelles au changement de langue apres le premier rendu (non-regression testee)
- ✅ **Multi-thème** : Classes CSS variables qui s'adaptent automatiquement

---

## 📊 Architecture technique

### Flux de données

```
┌─────────────────────────────────────────────────┐
│ Backend (Starlette - Port 10000)                │
│                                                 │
│ server/handlers/user_handlers.py                │
│   ├─ get_all_user_progress()                   │
│   │   → Query Attempt + Exercise               │
│   │   → Calcule streaks, accuracy, by_category │
│   │                                             │
│   └─ get_challenges_progress()                 │
│       → Query LogicChallengeAttempt            │
│       → Calcule completed, success_rate, times │
└─────────────────────────────────────────────────┘
                     │
                     │ HTTP/JSON
                     ▼
┌─────────────────────────────────────────────────┐
│ Frontend (Next.js 16)                           │
│                                                 │
│ hooks/                                          │
│   ├─ useProgressStats.ts                       │
│   │   → React Query (cache 2min)               │
│   │   → GET /api/users/me/progress             │
│   │                                             │
│   └─ useChallengesProgress.ts                  │
│       → React Query (cache 2min)               │
│       → GET /api/users/me/challenges/progress  │
│                                                 │
│ components/dashboard/                           │
│   ├─ StreakWidget.tsx                          │
│   ├─ ChallengesProgressWidget.tsx              │
│   └─ CategoryAccuracyChart.tsx                 │
│                                                 │
│ app/dashboard/page.tsx                          │
│   → Intègre les 3 widgets                      │
└─────────────────────────────────────────────────┘
```

### Stratégie de cache

- **React Query** : Cache 2 minutes (staleTime)
- **Refetch** : Automatique au focus de la fenêtre
- **Optimisation** : Requêtes indépendantes en parallèle

---

## 🚀 Utilisation

### Pour l'utilisateur final

1. Accéder au dashboard : `/dashboard`
2. Les widgets s'affichent automatiquement
3. Pas de configuration nécessaire

### Pour le développeur

**Ajouter un nouveau widget :**

1. Créer le hook React Query dans `frontend/hooks/`
2. Créer le composant dans `frontend/components/dashboard/`
3. Ajouter les traductions dans `frontend/messages/{fr,en}.json`
4. Intégrer dans `frontend/app/dashboard/page.tsx`

**Exemple d'ajout de traductions :**
```json
{
  "dashboard": {
    "nouveauWidget": {
      "title": "Mon nouveau widget",
      "description": "Description du widget"
    }
  }
}
```

---

## 🔍 Points d'attention

### Gestion des états
- ✅ Loading state (skeleton animé)
- ✅ Empty state (messages d'encouragement)
- ✅ Valeurs par défaut (|| 0 pour éviter undefined)

### Performance
- ✅ Cache React Query 2min
- ✅ Requêtes parallélisées
- ✅ Animations CSS (pas de JS)

### Accessibilité
- ✅ Icônes avec aria-hidden
- ✅ Labels descriptifs
- ✅ Contraste de couleurs respecté
- ✅ Texte lisible (taille minimale 14px)

### Responsive
- ✅ Layout adaptatif (1/2/3 colonnes)
- ✅ Composants optimisés mobile
- ✅ Spacing cohérent

---

## 📝 Maintenance future

### Optimisations possibles

1. **Lazy loading des widgets** : Charger les widgets uniquement quand ils deviennent visibles (Intersection Observer)
2. **Websocket pour temps réel** : Mettre à jour les stats en temps réel sans polling
3. **Animation des barres** : Ajouter des transitions animées sur les barres de progression
4. **Graphiques historiques** : Ajouter des graphiques d'évolution du streak/accuracy dans le temps
5. **Filtres temporels** : Permettre de filtrer par période (7j/30j/90j/all)

### Extensions possibles

- **Widget badges** : Afficher les badges débloqués récemment
- **Widget leaderboard** : Afficher le classement des utilisateurs
- **Widget recommandations** : Suggérer des exercices basés sur la progression
- **Widget achievements** : Afficher les réalisations et objectifs

---

## 🎉 Résultat

Le dashboard affiche maintenant **3 nouveaux widgets** qui exploitent les endpoints de progression :

1. **Série de jours** → Gamification (encourager la régularité)
2. **Progression défis** → Suivi des challenges (motivation)
3. **Précision par catégorie** → Insight pédagogique (identifier les points forts/faibles)

**Impact utilisateur :**
- ✅ Meilleure visibilité sur la progression
- ✅ Gamification accrue (streaks, défis)
- ✅ Feedback pédagogique actionnable

**Impact technique :**
- ✅ Endpoints de progression maintenant utilisés
- ✅ Architecture propre et maintenable
- ✅ Prêt pour extensions futures


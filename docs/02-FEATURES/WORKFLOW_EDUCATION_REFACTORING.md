# Workflow utilisateur & Éducation — Vue d'ensemble et refactoring

> **Objectif** : Contexte global du parcours utilisateur et de la partie éducation, pour guider les refactorings tout en gardant la cohérence.
> **Date** : Février 2026

---

## 1. Vue d'ensemble du parcours actuel

### 1.1 Flux utilisateur (schéma)

```
Accueil (/) 
    │
    ├── Non connecté → Register → Verify email → Login
    │
    └── Connecté 
            │
            ├── /dashboard (4 onglets : Vue d'ensemble, Recommandations, Progression, Détails)
            │       ├── Recommandations → lien vers /exercises/[id] ou /challenge/[id]
            │       └── Stats, Streak, Classement, Graphiques
            │
            ├── /exercises (liste paginée, filtres, ordre random, masquer réussis)
            │       └── Clic carte → ExerciseSolver ou modal
            │
            ├── /challenges (idem structure)
            │       └── Clic carte → ChallengeModal → ChallengeSolver
            │
            ├── /badges (En cours / À débloquer)
            ├── /leaderboard (classement, filtre âge)
            ├── /profile
            └── /settings
```

### 1.2 Composants clés

| Domaine | Hooks / Services | Pages |
|---------|------------------|-------|
| Auth | `useAuth` | login, register, verify-email, forgot-password, reset-password |
| Stats | `useUserStats`, `useProgressStats`, `useChallengesProgress` | dashboard |
| Recommandations | `useRecommendations` (generate, complete) | dashboard (onglet) |
| Exercices | `useExercises`, `useCompletedExercises` | exercises |
| Défis | `useChallenges`, `useCompletedChallenges` | challenges |
| Badges | `useBadgesProgress` | badges |
| Contenu | `usePaginatedContent` (DRY) | exercises, challenges |

---

## 2. Points d'amélioration identifiés

### 2.1 Workflow utilisateur

| Amélioration | Complexité | Impact | Priorité |
|--------------|------------|--------|----------|
| **Onboarding premier login** | Moyenne | Élevé | P0 |
| **Parcours guidé** (Dashboard → Exercice/Défi en 1 clic) | Faible | Moyen | P1 |
| **Recommandations cliquables** | — | — | ✅ Déjà fait (lien exercice/défi) |
| **Breadcrumb / contexte** ("Tu es ici") | Faible | Moyen | P2 |
| **Retour après résolution** (retour intelligent au dashboard ou liste) | Moyenne | Moyen | P1 |
| **Dashboard parent** (vue distincte) | Élevée | Élevé | P2 (roadmap) |

### 2.2 Partie éducation

| Amélioration | Complexité | Impact | Priorité |
|--------------|------------|--------|----------|
| **Révisions espacées** (spaced repetition) | Élevée | Élevé | P2 |
| **Test diagnostic initial** | Élevée | Élevé | P2 |
| **Défis quotidiens** (objectif du jour) | Moyenne | Élevé | P1 |
| **Objectifs personnalisés** (ex: "3 exercices/jour") | Moyenne | Moyen | P2 |
| **Feedback pédagogique enrichi** (explication des erreurs) | Moyenne | Moyen | P1 |
| **Adaptation difficulté** (basée sur succès/échecs) | Élevée | Élevé | P2 |

### 2.3 Refactorings techniques (sans changer UX)

| Amélioration | Complexité | Impact |
|--------------|------------|--------|
| **DRY exercices/challenges** (ContentCardBase, usePaginatedContent) | Partiel déjà fait | Bonne base |
| **Centraliser la logique "completed"** (useCompletedItems) | Faible | Déjà en place |
| **Unifier les filtres** (exercises/challenges) en composant réutilisable | Faible | Lisibilité |
| **handleRefresh dashboard** (invalidation complète) | Faible | Corrigé |

---

## 3. Complexité estimée par type

- **Faible** : 1–2 jours, peu de risque de régression
- **Moyenne** : 3–5 jours, tests + documentation
- **Élevée** : 1–2 semaines, changement de modèle ou nouveau flux

---

## 4. Principes pour les implémentations

1. **Garder le contexte** : Toute modification dans exercises, challenges, dashboard ou recommendations doit considérer le flux complet (accueil → contenu → retour).
2. **Éviter les silos** : Les hooks (useRecommendations, useExercises, etc.) partagent des queryKey React Query ; penser à l'invalidation croisée.
3. **Respecter les personas** : Lucas 8 ans (TDAH), Emma 14 ans (dyscalculie), Marine parent — cf. GUIDE_UTILISATEUR_MVP.md.
4. **Accessibilité** : Mode Focus, reduced motion, contraste — déjà en place via useAccessibleAnimation.
5. **i18n** : Toujours passer par les clés `messages/fr.json` et `en.json`.

---

## 5. Références

- [GUIDE_UTILISATEUR_MVP.md](../01-GUIDES/GUIDE_UTILISATEUR_MVP.md) — Cible, personas, parcours
- [SITUATION_FEATURES.md](SITUATION_FEATURES.md) — État des fonctionnalités
- [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md) — Priorités produit
- [AUDIT_DASHBOARD_2026-02.md](../03-PROJECT/AUDIT_DASHBOARD_2026-02.md) — Corrections restantes dashboard
- [06-WIDGETS/](../06-WIDGETS/) — Design system widgets

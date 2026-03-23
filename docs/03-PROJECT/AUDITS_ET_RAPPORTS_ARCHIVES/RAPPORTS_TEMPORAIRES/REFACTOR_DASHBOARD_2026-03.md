# Refactor Dashboard — Réorganisation des onglets

> **Date :** 06/03/2026  
> **Type :** Implémentation  
> **Statut :** Historique - applique, archive le 23/03/2026
> **Objectif :** Réduire la charge cognitive (Syndrome du Mille-feuille)

> Snapshot de refactor UI applique. Ce document reste utile pour comprendre la structure du dashboard au 06/03/2026, mais n'est plus un tracker actif.

---

## 1. Résumé des changements

### 1.1 Vue d'ensemble (nettoyée)

| Avant | Après |
|-------|-------|
| QuickStartActions | QuickStartActions |
| DailyChallengesWidget | DailyChallengesWidget (col-span-8) |
| LevelEstablishedWidget | Retiré → Mon Profil |
| Bloc 3 Stats (Exercices, Taux, Défis) | Retiré → Mon Profil |
| StreakWidget + LeaderboardWidget (grille 2 col) | StreakWidget (col-span-4) à côté de Défis |
| — | LeaderboardWidget retiré (déjà dans navbar) |

**Layout :** Grille `grid-cols-12` — Défis du jour (8) + Série en cours (4), hauteur uniforme via `flex-1 min-h-0`.

### 1.2 Progression (nettoyée)

| Avant | Après |
|-------|-------|
| LevelIndicator (Niveau actuel) | Retiré → Mon Profil |
| ChallengesProgressWidget | Conservé |
| CategoryAccuracyChart | Conservé |
| ProgressChartLazy | Conservé |
| DailyExercisesChartLazy | Conservé |

**Contenu :** 4 graphiques uniquement.

### 1.3 Mon Profil (ex-Détails)

| Onglet | Avant | Après |
|--------|-------|-------|
| Nom | Détails | **Mon Profil** |
| Ordre contenu | Tempo moyen, Journal d'activité | 1. Niveau actuel (LevelIndicator) |
| | | 2. Ton Profil Mathématique (LevelEstablishedWidget) |
| | | 3. Bloc 3 Stats (Exercices, Taux, Défis) |
| | | 4. Tempo moyen (AverageTimeWidget) |
| | | 5. Journal d'activité (RecentActivity) |

---

## 2. Fichiers modifiés

| Fichier | Changement |
|---------|------------|
| `frontend/app/dashboard/page.tsx` | Réorganisation des onglets, grille Défis+Série |
| `frontend/messages/fr.json` | `tabs.profile`, `tabs.profileShort` |
| `frontend/messages/en.json` | Idem |
| `frontend/components/dashboard/DailyChallengesWidget.tsx` | `flex-1 min-h-0` pour hauteur uniforme |
| `frontend/components/dashboard/StreakWidget.tsx` | `flex-1 min-h-0` sur motion.div et Card |
| `frontend/components/dashboard/LevelEstablishedWidget.tsx` | Suppression `mt-8` (espacement) |

---

## 3. Traductions

| Clé | FR | EN |
|-----|----|----|
| `tabs.profile` | Mon Profil | My Profile |
| `tabs.profileShort` | Profil | Profile |

---

## 4. Références

- **F02 :** [F02_DEFIS_QUOTIDIENS.md](../02-FEATURES/F02_DEFIS_QUOTIDIENS.md)
- **Widget :** [F02_DAILY_CHALLENGES_WIDGET.md](../06-WIDGETS/F02_DAILY_CHALLENGES_WIDGET.md)
- **Intégration widgets :** [INTEGRATION_PROGRESSION_WIDGETS.md](../06-WIDGETS/INTEGRATION_PROGRESSION_WIDGETS.md)


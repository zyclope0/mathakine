# Integration des widgets de progression dans le dashboard

> Updated : 2026-04-10

## Resume

Le dashboard frontend exploite plusieurs endpoints de progression et de gamification
deja disponibles cote backend.

Surfaces principales :

- Vue d'ensemble
- Progression
- Mon profil

Reference historique de refactor :

- [REFACTOR_DASHBOARD_2026-03.md](../../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/REFACTOR_DASHBOARD_2026-03.md)

---

## Sources de verite runtime

### Hooks

- `frontend/hooks/useProgressStats.ts`
- `frontend/hooks/useChallengesProgress.ts`
- `frontend/hooks/useDailyChallenges.ts`
- `frontend/hooks/useIrtScores.ts`

### Composants dashboard

- `frontend/components/dashboard/DailyChallengesWidget.tsx`
- `frontend/components/dashboard/StreakWidget.tsx`
- `frontend/components/dashboard/ChallengesProgressWidget.tsx`
- `frontend/components/dashboard/CategoryAccuracyChart.tsx`
- `frontend/components/dashboard/LevelEstablishedWidget.tsx`

### Page

- `frontend/app/dashboard/page.tsx`

---

## Endpoints relies

- `GET /api/daily-challenges`
- `GET /api/users/stats`
- `GET /api/users/me/progress`
- `GET /api/users/me/progress/timeline`
- `GET /api/users/me/challenges/progress`
- `GET /api/users/me/challenges/detailed-progress`
- `GET /api/diagnostic/status`

Reference contrats :

- [API_QUICK_REFERENCE.md](../../02-FEATURES/API_QUICK_REFERENCE.md)
- [F02_DEFIS_QUOTIDIENS.md](../../02-FEATURES/F02_DEFIS_QUOTIDIENS.md)
- [F05_ADAPTATION_DYNAMIQUE.md](../../02-FEATURES/F05_ADAPTATION_DYNAMIQUE.md)

---

## Structure actuelle

### Onglet Vue d'ensemble

- `QuickStartActions`
- `DailyChallengesWidget`
- `StreakWidget`

### Onglet Progression

- `ChallengesProgressWidget`
- `CategoryAccuracyChart`
- graphiques de progression differes

### Onglet Mon profil

- `LevelIndicator`
- `LevelEstablishedWidget`
- `StatsCard`
- `AverageTimeWidget`
- `RecentActivity`

---

## Notes de maintenance

- garder les hooks fins et les composants dashboard focalises sur l'affichage
- verifier les contrats API actifs dans `server/routes/` et `server/handlers/`
- ne pas deduire une integration runtime depuis un ancien doc archive

# Catalogue des hooks React â€” Mathakine

> Scope : `frontend/hooks/`
> Updated : 2026-04-07
> Total : 52 fichiers hooks (dont `hooks/chat/`)

---

## Conventions de lecture

| Colonne                | Signification                                   |
| ---------------------- | ----------------------------------------------- |
| **Test**               | âœ… test unitaire prÃ©sent / âŒ absent          |
| **DÃ©pendances clÃ©s** | endpoints backend appelÃ©s ou stores consommÃ©s |
| **React Query**        | utilise `useQuery` / `useMutation` / aucun      |

---

## CatÃ©gorie 1 â€” Exercices

| Hook                        | RÃ´le                                              | Test | RQ       | DÃ©pendances clÃ©s                             |
| --------------------------- | -------------------------------------------------- | ---- | -------- | ---------------------------------------------- |
| `useExercises.ts`           | Liste paginÃ©e d'exercices avec filtres            | âŒ   | Query    | `GET /api/exercises`                           |
| `useExercise.ts`            | DÃ©tail d'un exercice par ID                       | âŒ   | Query    | `GET /api/exercises/:id`                       |
| `useSubmitAnswer.ts`        | Soumettre une rÃ©ponse Ã  un exercice              | âŒ   | Mutation | `POST /api/exercises/:id/submit`               |
| `useAIExerciseGenerator.ts` | GÃ©nÃ©ration SSE d'exercice via IA                 | âŒ   | Aucun    | `POST /api/exercises/generate-ai-stream` (SSE) |
| `useCompletedItems.ts`      | IDs des exercices/dÃ©fis complÃ©tÃ©s (cache local) | âœ…  | Aucun    | localStorage + state                           |

---

## CatÃ©gorie 2 â€” DÃ©fis logiques

| Hook                              | RÃ´le                                 | Test | RQ    | DÃ©pendances clÃ©s                              |
| --------------------------------- | ------------------------------------- | ---- | ----- | ----------------------------------------------- |
| `useChallenges.ts`                | Liste paginÃ©e de dÃ©fis avec filtres | âŒ   | Query | `GET /api/challenges`                           |
| `useChallenge.ts`                 | DÃ©tail d'un dÃ©fi par ID             | âŒ   | Query | `GET /api/challenges/:id`                       |
| `useChallengeSolverController.ts` | Runtime local du solver de dÃ©fi      | ✅   | Aucun | helpers solver + mutations `useChallenges`      |
| `useAIChallengeGenerator.ts`      | GÃ©nÃ©ration SSE de dÃ©fi via IA      | âŒ   | Aucun | `POST /api/challenges/generate-ai-stream` (SSE) |
| `useChallengesProgress.ts`        | Progression dÃ©fis de l'utilisateur   | âŒ   | Query | `GET /api/challenges/progress`                  |
| `useChallengesStats.ts`           | Statistiques dÃ©fis (taux, types)     | âœ…  | Query | `GET /api/challenges/stats`                     |
| `useDailyChallenges.ts`           | DÃ©fis quotidiens du jour             | âŒ   | Query | `GET /api/daily-challenges`                     |

---

## CatÃ©gorie 3 â€” Profil, Dashboard & Progression

| Hook                          | RÃ´le                                                              | Test | RQ    | DÃ©pendances clÃ©s                                  |
| ----------------------------- | ------------------------------------------------------------------ | ---- | ----- | --------------------------------------------------- |
| `useProfilePageController.ts` | Runtime local de la page profil (sections, formulaires, resets)    | ✅   | Aucun | `useProfile`, `useThemeStore`, `useAgeGroupDisplay` |
| `useProfile.ts`               | Profil complet de l'utilisateur connectÃ©                          | âŒ   | Query | `GET /api/users/me`                                 |
| `useUserStats.ts`             | Stats globales dashboard, incluant le bloc F04 `spaced_repetition` | âŒ   | Query | `GET /api/users/stats`                              |
| `useNextReview.ts`            | Lecture one-shot de la prochaine revision F04 et du resume associe | âŒ   | Aucun | `GET /api/users/me/reviews/next`                    |
| `useProgressStats.ts`         | Stats de progression par pÃ©riode                                  | âŒ   | Query | `GET /api/progress/stats`                           |
| `useProgressTimeline.ts`      | Timeline de progression historique                                 | âœ…  | Query | `GET /api/progress/timeline`                        |
| `usePaginatedContent.ts`      | Pagination gÃ©nÃ©rique rÃ©utilisable                               | âœ…  | Aucun | abstraction interne                                 |
| `useIrtScores.ts`             | Scores IRT (thÃ©orie de rÃ©ponse Ã  l'item)                        | âŒ   | Query | `GET /api/progress/irt`                             |

---

## CatÃ©gorie 4 â€” Recommandations

| Hook                                | RÃ´le                                       | Test | RQ    | DÃ©pendances clÃ©s         |
| ----------------------------------- | ------------------------------------------- | ---- | ----- | -------------------------- |
| `useRecommendations.ts`             | Recommandations personnalisÃ©es (liste)     | âŒ   | Query | `GET /api/recommendations` |
| `useRecommendationsReason.ts` (lib) | Traduit les codes raison i18n cÃ´tÃ© client | âœ…  | Aucun | `next-intl`                |

---

## CatÃ©gorie 5 â€” Gamification & Badges

| Hook                         | RÃ´le                               | Test | RQ    | DÃ©pendances clÃ©s                       |
| ---------------------------- | ----------------------------------- | ---- | ----- | ---------------------------------------- |
| `useBadges.ts`               | Liste des badges obtenus            | âŒ   | Query | `GET /api/badges`                        |
| `useBadgesProgress.ts`       | Progression vers badges non obtenus | âŒ   | Query | `GET /api/badges/progress`               |
| `useBadgesPageController.ts` | Runtime local de la page badges     | ✅   | Aucun | helpers badges + localStorage + confetti |
| `useLeaderboard.ts`          | Classement public paginÃ©           | âŒ   | Query | `GET /api/leaderboard`                   |
| `useMyLeaderboardRank.ts`    | Rang de l'utilisateur courant       | âŒ   | Query | `GET /api/leaderboard/me`                |

---

## CatÃ©gorie 6 â€” Authentification

| Hook                           | RÃ´le                                                                                   | Test | RQ       | DÃ©pendances clÃ©s                                       |
| ------------------------------ | --------------------------------------------------------------------------------------- | ---- | -------- | -------------------------------------------------------- |
| `useAuth.ts`                   | Session utilisateur, login, logout, refresh                                             | âŒ   | Mutation | `POST /api/auth/login`, `POST /api/auth/logout`          |
| `useSettings.ts`               | PrÃ©fÃ©rences utilisateur                                                               | âŒ   | Mutation | `PUT /api/users/me`, export, delete, sessions            |
| `useSettingsPageController.ts` | Ã‰tat local page settings (sync user, sessions, diagnostic, `visibleSessions` dÃ©rivÃ©) | âœ…  | Mutation | `useAuth` + `useSettings` + `GET /api/diagnostic/status` |

---

## CatÃ©gorie 7 â€” Chat & IA

| Hook              | RÃ´le                                       | Test    | RQ    | DÃ©pendances clÃ©s                   |
| ----------------- | ------------------------------------------- | ------- | ----- | ------------------------------------ |
| `useChat.ts`      | Session chat avec l'assistant               | âœ…     | Aucun | `POST /api/chat` (via route Next.js) |
| `chat/` (dossier) | Hooks internes du chat (streaming, history) | Partiel | Aucun | SSE + localStorage                   |

---

## CatÃ©gorie 8 â€” Admin

| Hook                               | RÃ´le                                         | Test | RQ               | DÃ©pendances clÃ©s                      |
| ---------------------------------- | --------------------------------------------- | ---- | ---------------- | --------------------------------------- |
| `useAdminOverview.ts`              | Vue d'ensemble admin                          | âŒ   | Query            | `GET /api/admin/overview`               |
| `useAdminUsers.ts`                 | Gestion utilisateurs admin                    | âŒ   | Query + Mutation | `GET/DELETE /api/admin/users`           |
| `useAdminExercises.ts`             | Gestion exercices admin                       | âŒ   | Query + Mutation | `GET/POST/DELETE /api/admin/exercises`  |
| `useAdminContentPageController.ts` | Shell query `tab` / `edit` page contenu admin | âœ…  | Aucun            | Parse URL uniquement (FFI-L14)          |
| `useAdminChallenges.ts`            | Gestion dÃ©fis admin                          | âŒ   | Query + Mutation | `GET/POST/DELETE /api/admin/challenges` |
| `useAdminBadges.ts`                | Gestion badges admin                          | âŒ   | Query + Mutation | `GET/POST /api/admin/badges`            |
| `useAdminAiStats.ts`               | Statistiques IA (usage, modÃ¨les, coÃ»t)      | âŒ   | Query            | `GET /api/admin/ai-stats`               |
| `useAdminEdTechAnalytics.ts`       | Analytics EdTech admin                        | âŒ   | Query            | `GET /api/admin/analytics`              |
| `useAdminFeedback.ts`              | Feedbacks utilisateurs admin                  | âŒ   | Query            | `GET /api/admin/feedback`               |
| `useAdminModeration.ts`            | ModÃ©ration contenu admin                     | âŒ   | Query + Mutation | `GET/POST /api/admin/moderation`        |
| `useAdminConfig.ts`                | Configuration plateforme admin                | âŒ   | Query + Mutation | `GET/PUT /api/admin/config`             |
| `useAdminReports.ts`               | Rapports admin (exports)                      | âŒ   | Query            | `GET /api/admin/reports`                |
| `useAdminAuditLog.ts`              | Journal d'audit admin                         | âŒ   | Query            | `GET /api/admin/audit-log`              |

---

## CatÃ©gorie 9 â€” Divers

| Hook                               | RÃ´le                                                    | Test | RQ    | DÃ©pendances clÃ©s                                             |
| ---------------------------------- | -------------------------------------------------------- | ---- | ----- | -------------------------------------------------------------- |
| `useAcademyStats.ts`               | Stats globales de l'acadÃ©mie (public)                   | âŒ   | Query | `GET /api/stats/academy`                                       |
| `useDiagnostic.ts`                 | RÃ©sultats diagnostic initial                            | âŒ   | Query | `GET /api/diagnostic`                                          |
| `useContentListPageController.ts`  | Etat runtime shared des pages `Exercises` / `Challenges` | ✅   | Aucun | `useContentListViewControls` + `useContentListOrderPreference` |
| `useContentListOrderPreference.ts` | Persistance locale du tri liste contenu                  | ❌   | Aucun | localStorage                                                   |
| `useContentListViewControls.ts`    | Etat vue liste/grille et controles associes              | ❌   | Aucun | state local + localStorage                                     |

---

## Bilan couverture tests

| Statut                 | Nombre |
| ---------------------- | ------ |
| âœ… Avec test unitaire | 9      |
| âŒ Sans test unitaire  | ~43    |
| **Total**              | **52** |

### Hooks critiques sans tests (prioritÃ© haute)

| Hook                         | Pourquoi critique                                                   |
| ---------------------------- | ------------------------------------------------------------------- |
| `useAIExerciseGenerator.ts`  | Orchestre le flux SSE exercice â€” chemin principal de gÃ©nÃ©ration |
| `useAIChallengeGenerator.ts` | Orchestre le flux SSE dÃ©fi â€” chemin principal de gÃ©nÃ©ration    |
| `useExercises.ts`            | Hook principal de la page exercices                                 |
| `useAuth.ts`                 | Gestion de session â€” impact sÃ©curitÃ©                            |
| `useRecommendations.ts`      | Affiche les recommandations personnalisÃ©es                         |
| `useSubmitAnswer.ts`         | Validation des rÃ©ponses â€” impact gamification                    |

---

## RÃ¨gle d'ajout

Tout nouveau hook doit :

1. Figurer dans ce catalogue avec sa catÃ©gorie, son rÃ´le et ses dÃ©pendances.
2. Avoir un fichier de test dans `frontend/__tests__/unit/hooks/`.
3. Preferer React Query (`useQuery` / `useMutation`) pour tout appel reseau partage/cache ; une exception one-shot sans cache est acceptable si elle est documentee (ex: `useNextReview.ts` pour la session F04).

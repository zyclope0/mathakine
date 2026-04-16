# Catalogue des hooks React - Mathakine

> Scope : `frontend/hooks/`
> Updated : 2026-04-16
> Total : 58 hooks source (tests exclus)
> Couverture terrain : 34 hooks avec test co-localise, 24 sans test co-localise

---

## Conventions de lecture

| Colonne | Signification |
| ------- | ------------- |
| **Test** | `oui` = test co-localise present (`*.test.ts` ou `*.test.tsx`) |
| **RQ** | usage principal React Query (`query`, `mutation`, `mixte`, `aucun`) |
| **Notes** | dependances majeures ou statut particulier |

---

## Exercices

| Hook | Role | Test | RQ | Notes |
| ---- | ---- | ---- | -- | ----- |
| `useExercises.ts` | liste paginee d'exercices avec filtres | non | query | `GET /api/exercises` |
| `useExercise.ts` | detail exercice par ID | non | query | `GET /api/exercises/:id` |
| `useSubmitAnswer.ts` | soumission de reponse exercice | oui | mutation | `POST /api/exercises/:id/submit` |
| `useAIExerciseGenerator.ts` | generation SSE d'exercice | oui | aucun | `POST /api/exercises/generate-ai-stream` |
| `useExerciseSolverController.ts` | runtime solver exercice | oui | aucun | F04 / session entrelacee |
| `useCompletedItems.ts` | IDs completes et cache local | oui | aucun | localStorage / state |

---

## Defis

| Hook | Role | Test | RQ | Notes |
| ---- | ---- | ---- | -- | ----- |
| `useChallenges.ts` | liste paginee de defis | oui | query | `GET /api/challenges` |
| `useChallenge.ts` | detail defi par ID | non | query | `GET /api/challenges/:id` |
| `useAIChallengeGenerator.ts` | generation SSE de defi | oui | aucun | `POST /api/challenges/generate-ai-stream` |
| `useChallengeSolverController.ts` | runtime solver defi | oui | aucun | solver local |
| `useChallengesProgress.ts` | progression defis utilisateur | non | query | `GET /api/challenges/progress` |
| `useChallengesStats.ts` | statistiques defis | oui | query | `GET /api/challenges/stats` |
| `useChallengeTranslations.ts` | mapping / labels challenge | oui | aucun | i18n / helpers |
| `useDailyChallenges.ts` | defis quotidiens | non | query | `GET /api/daily-challenges` |

---

## Profil, dashboard et progression

| Hook | Role | Test | RQ | Notes |
| ---- | ---- | ---- | -- | ----- |
| `useProfile.ts` | profil complet utilisateur | oui | query | `GET /api/users/me` |
| `useProfilePageController.ts` | runtime page profil | oui | aucun | sections / formulaires |
| `useDashboardPageController.ts` | runtime page dashboard | oui | aucun | tabs / export / shell state |
| `useUserStats.ts` | stats dashboard globales | non | query | `GET /api/users/stats` |
| `useNextReview.ts` | prochaine revision F04 | non | aucun | `GET /api/users/me/reviews/next` |
| `useProgressStats.ts` | stats progression par periode | non | query | `GET /api/progress/stats` |
| `useProgressTimeline.ts` | timeline de progression | oui | query | `GET /api/progress/timeline` |
| `useProgressionArc.ts` | arc de progression persistant | oui | aucun | constellation / UI progression |
| `usePaginatedContent.ts` | pagination generique reutilisable | oui | aucun | abstraction locale |
| `useIrtScores.ts` | scores IRT | oui | query | `GET /api/diagnostic/status` |
| `useFirstVisitHint.ts` | hints de premiere visite | non | aucun | localStorage |

---

## Recommandations, contenu et diagnostic

| Hook | Role | Test | RQ | Notes |
| ---- | ---- | ---- | -- | ----- |
| `useRecommendations.ts` | recommandations personnalisees | non | query | `GET /api/recommendations` |
| `useContentListOrderPreference.ts` | persistance locale du tri liste | non | aucun | localStorage |
| `useContentListViewControls.ts` | etat vue liste/grille | non | aucun | state local |
| `useContentListPageController.ts` | runtime shared `Exercises` / `Challenges` | oui | aucun | toolbar / order / filters |
| `useDiagnostic.ts` | diagnostic initial | oui | query | `GET /api/diagnostic` |
| `useRecommendationsReason.ts` | helper libelle raison reco | oui | aucun | `next-intl` |

---

## Badges et leaderboard

| Hook | Role | Test | RQ | Notes |
| ---- | ---- | ---- | -- | ----- |
| `useBadges.ts` | badges obtenus | oui | query | `GET /api/badges` |
| `useBadgesProgress.ts` | progression vers badges | non | query | `GET /api/badges/progress` |
| `useBadgesPageController.ts` | runtime page badges | oui | aucun | FFI-L12 |
| `useLeaderboard.ts` | classement public | non | query | `GET /api/leaderboard` |
| `useMyLeaderboardRank.ts` | rang utilisateur courant | non | query | `GET /api/leaderboard/me` |

---

## Authentification et parametres

| Hook | Role | Test | RQ | Notes |
| ---- | ---- | ---- | -- | ----- |
| `useAuth.ts` | facade auth | oui | mixte | login / logout / register / forgot-password |
| `useSettings.ts` | preferences utilisateur | oui | mixte | `PUT /api/users/me`, export, sessions |
| `useSettingsPageController.ts` | etat page settings | oui | aucun | sync user / sessions / diagnostic |
| `useAccessibleAnimation.ts` | helper animation accessibilite | oui | aucun | implementation cible `frontend/lib/hooks/` |

---

## Chat et assistant

| Hook | Role | Test | RQ | Notes |
| ---- | ---- | ---- | -- | ----- |
| `chat/useChat.ts` | session chat avec assistant | oui | aucun | hook principal |
| `chat/useChatAutoScroll.ts` | auto-scroll messages chat | non | aucun | UI only |
| `chat/useGuestChatAccess.ts` | quota invite 5 messages / session | oui | aucun | `sessionStorage` |
| `useChat.ts` | re-export legacy du hook chat | non | aucun | wrapper `export { useChat } from "./chat/useChat"` |

---

## Admin

| Hook | Role | Test | RQ | Notes |
| ---- | ---- | ---- | -- | ----- |
| `useAdminOverview.ts` | vue d'ensemble admin | non | query | `GET /api/admin/overview` |
| `useAdminUsers.ts` | gestion utilisateurs admin | oui | mixte | `GET/DELETE /api/admin/users` |
| `useAdminUsersPageController.ts` | runtime page admin users | oui | aucun | page mince |
| `useAdminExercises.ts` | gestion exercices admin | oui | mixte | `GET/POST/DELETE /api/admin/exercises` |
| `useAdminChallenges.ts` | gestion defis admin | oui | mixte | `GET/POST/DELETE /api/admin/challenges` |
| `useAdminBadges.ts` | gestion badges admin | non | mixte | `GET/POST /api/admin/badges` |
| `useAdminContentPageController.ts` | shell page contenu admin | oui | aucun | query params / tabs |
| `useAdminAiStats.ts` | stats IA admin | oui | query | `GET /api/admin/ai-stats` |
| `useAdminAiMonitoringPageController.ts` | runtime page ai-monitoring | oui | aucun | `days`, agrégats, harness=25 |
| `useAdminEdTechAnalytics.ts` | analytics EdTech admin | non | query | `GET /api/admin/analytics` |
| `useAdminFeedback.ts` | feedbacks utilisateurs admin | non | query | `GET /api/admin/feedback` |
| `useAdminModeration.ts` | moderation admin | oui | mixte | `GET/POST /api/admin/moderation` |
| `useAdminConfig.ts` | configuration plateforme admin | non | mixte | `GET/PUT /api/admin/config` |
| `useAdminReports.ts` | rapports admin | non | query | `GET /api/admin/reports` |
| `useAdminAuditLog.ts` | journal d'audit admin | oui | query | `GET /api/admin/audit-log` |

---

## Divers

| Hook | Role | Test | RQ | Notes |
| ---- | ---- | ---- | -- | ----- |
| `useAcademyStats.ts` | stats academie publiques | non | query | `GET /api/stats/academy` |

---

## Hooks sans test co-localise (etat 2026-04-16)

- `chat/useChatAutoScroll.ts`
- `useAcademyStats.ts`
- `useAdminBadges.ts`
- `useAdminConfig.ts`
- `useAdminEdTechAnalytics.ts`
- `useAdminFeedback.ts`
- `useAdminOverview.ts`
- `useAdminReports.ts`
- `useBadgesProgress.ts`
- `useChallenge.ts`
- `useChallengesProgress.ts`
- `useChat.ts`
- `useContentListOrderPreference.ts`
- `useContentListViewControls.ts`
- `useDailyChallenges.ts`
- `useExercise.ts`
- `useExercises.ts`
- `useFirstVisitHint.ts`
- `useLeaderboard.ts`
- `useMyLeaderboardRank.ts`
- `useNextReview.ts`
- `useProgressStats.ts`
- `useRecommendations.ts`
- `useUserStats.ts`

---

## Bilan

| Statut | Nombre |
| ------ | ------ |
| Avec test co-localise | 34 |
| Sans test co-localise | 24 |
| Total | 58 |

## Regle d'ajout

Tout nouveau hook doit :

1. figurer dans ce catalogue avec role, dependances et statut de test
2. avoir un test co-localise a proximite du hook source quand le hook porte un comportement non trivial
3. preferer React Query pour tout acces reseau partage/cache
4. documenter explicitement les wrappers legacy ou re-exports (`useChat.ts`) pour eviter les faux doublons

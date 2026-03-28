# Catalogue des hooks React — Mathakine

> Scope : `frontend/hooks/`
> Updated : 2026-03-27
> Total : 41 fichiers hooks + 1 dossier `chat/`

---

## Conventions de lecture

| Colonne | Signification |
|---------|--------------|
| **Test** | ✅ test unitaire présent / ❌ absent |
| **Dépendances clés** | endpoints backend appelés ou stores consommés |
| **React Query** | utilise `useQuery` / `useMutation` / aucun |

---

## Catégorie 1 — Exercices

| Hook | Rôle | Test | RQ | Dépendances clés |
|------|------|------|----|-----------------|
| `useExercises.ts` | Liste paginée d'exercices avec filtres | ❌ | Query | `GET /api/exercises` |
| `useExercise.ts` | Détail d'un exercice par ID | ❌ | Query | `GET /api/exercises/:id` |
| `useSubmitAnswer.ts` | Soumettre une réponse à un exercice | ❌ | Mutation | `POST /api/exercises/:id/submit` |
| `useAIExerciseGenerator.ts` | Génération SSE d'exercice via IA | ❌ | Aucun | `POST /api/exercises/generate-ai-stream` (SSE) |
| `useCompletedItems.ts` | IDs des exercices/défis complétés (cache local) | ✅ | Aucun | localStorage + state |

---

## Catégorie 2 — Défis logiques

| Hook | Rôle | Test | RQ | Dépendances clés |
|------|------|------|----|-----------------|
| `useChallenges.ts` | Liste paginée de défis avec filtres | ❌ | Query | `GET /api/challenges` |
| `useChallenge.ts` | Détail d'un défi par ID | ❌ | Query | `GET /api/challenges/:id` |
| `useAIChallengeGenerator.ts` | Génération SSE de défi via IA | ❌ | Aucun | `POST /api/challenges/generate-ai-stream` (SSE) |
| `useChallengesProgress.ts` | Progression défis de l'utilisateur | ❌ | Query | `GET /api/challenges/progress` |
| `useChallengesStats.ts` | Statistiques défis (taux, types) | ✅ | Query | `GET /api/challenges/stats` |
| `useDailyChallenges.ts` | Défis quotidiens du jour | ❌ | Query | `GET /api/daily-challenges` |

---

## Catégorie 3 — Dashboard & Progression

| Hook | Rôle | Test | RQ | Dépendances clés |
|------|------|------|----|-----------------|
| `useProfile.ts` | Profil complet de l'utilisateur connecté | ❌ | Query | `GET /api/users/me` |
| `useUserStats.ts` | Stats globales (points, niveau, streak) | ❌ | Query | `GET /api/users/me/stats` |
| `useProgressStats.ts` | Stats de progression par période | ❌ | Query | `GET /api/progress/stats` |
| `useProgressTimeline.ts` | Timeline de progression historique | ✅ | Query | `GET /api/progress/timeline` |
| `usePaginatedContent.ts` | Pagination générique réutilisable | ✅ | Aucun | abstraction interne |
| `useIrtScores.ts` | Scores IRT (théorie de réponse à l'item) | ❌ | Query | `GET /api/progress/irt` |

---

## Catégorie 4 — Recommandations

| Hook | Rôle | Test | RQ | Dépendances clés |
|------|------|------|----|-----------------|
| `useRecommendations.ts` | Recommandations personnalisées (liste) | ❌ | Query | `GET /api/recommendations` |
| `useRecommendationsReason.ts` (lib) | Traduit les codes raison i18n côté client | ✅ | Aucun | `next-intl` |

---

## Catégorie 5 — Gamification & Badges

| Hook | Rôle | Test | RQ | Dépendances clés |
|------|------|------|----|-----------------|
| `useBadges.ts` | Liste des badges obtenus | ❌ | Query | `GET /api/badges` |
| `useBadgesProgress.ts` | Progression vers badges non obtenus | ❌ | Query | `GET /api/badges/progress` |
| `useLeaderboard.ts` | Classement public paginé | ❌ | Query | `GET /api/leaderboard` |
| `useMyLeaderboardRank.ts` | Rang de l'utilisateur courant | ❌ | Query | `GET /api/leaderboard/me` |

---

## Catégorie 6 — Authentification

| Hook | Rôle | Test | RQ | Dépendances clés |
|------|------|------|----|-----------------|
| `useAuth.ts` | Session utilisateur, login, logout, refresh | ❌ | Mutation | `POST /api/auth/login`, `POST /api/auth/logout` |
| `useSettings.ts` | Préférences utilisateur | ❌ | Mutation | `GET/PUT /api/users/me/settings` |

---

## Catégorie 7 — Chat & IA

| Hook | Rôle | Test | RQ | Dépendances clés |
|------|------|------|----|-----------------|
| `useChat.ts` | Session chat avec l'assistant | ✅ | Aucun | `POST /api/chat` (via route Next.js) |
| `chat/` (dossier) | Hooks internes du chat (streaming, history) | Partiel | Aucun | SSE + localStorage |

---

## Catégorie 8 — Admin

| Hook | Rôle | Test | RQ | Dépendances clés |
|------|------|------|----|-----------------|
| `useAdminOverview.ts` | Vue d'ensemble admin | ❌ | Query | `GET /api/admin/overview` |
| `useAdminUsers.ts` | Gestion utilisateurs admin | ❌ | Query + Mutation | `GET/DELETE /api/admin/users` |
| `useAdminExercises.ts` | Gestion exercices admin | ❌ | Query + Mutation | `GET/POST/DELETE /api/admin/exercises` |
| `useAdminChallenges.ts` | Gestion défis admin | ❌ | Query + Mutation | `GET/POST/DELETE /api/admin/challenges` |
| `useAdminBadges.ts` | Gestion badges admin | ❌ | Query + Mutation | `GET/POST /api/admin/badges` |
| `useAdminAiStats.ts` | Statistiques IA (usage, modèles, coût) | ❌ | Query | `GET /api/admin/ai-stats` |
| `useAdminEdTechAnalytics.ts` | Analytics EdTech admin | ❌ | Query | `GET /api/admin/analytics` |
| `useAdminAnalytics.ts` | Analytics généraux admin | ❌ | Query | `GET /api/admin/analytics` |
| `useAdminFeedback.ts` | Feedbacks utilisateurs admin | ❌ | Query | `GET /api/admin/feedback` |
| `useAdminModeration.ts` | Modération contenu admin | ❌ | Query + Mutation | `GET/POST /api/admin/moderation` |
| `useAdminConfig.ts` | Configuration plateforme admin | ❌ | Query + Mutation | `GET/PUT /api/admin/config` |
| `useAdminReports.ts` | Rapports admin (exports) | ❌ | Query | `GET /api/admin/reports` |
| `useAdminAuditLog.ts` | Journal d'audit admin | ❌ | Query | `GET /api/admin/audit-log` |

---

## Catégorie 9 — Divers

| Hook | Rôle | Test | RQ | Dépendances clés |
|------|------|------|----|-----------------|
| `useAcademyStats.ts` | Stats globales de l'académie (public) | ❌ | Query | `GET /api/stats/academy` |
| `useDiagnostic.ts` | Résultats diagnostic initial | ❌ | Query | `GET /api/diagnostic` |
| `useChallengeTranslations.ts` | Traductions i18n pour les défis | ❌ | Aucun | `next-intl` |

---

## Bilan couverture tests

| Statut | Nombre |
|--------|--------|
| ✅ Avec test unitaire | 7 |
| ❌ Sans test unitaire | ~34 |
| **Total** | **41** |

### Hooks critiques sans tests (priorité haute)

| Hook | Pourquoi critique |
|------|-----------------|
| `useAIExerciseGenerator.ts` | Orchestre le flux SSE exercice — chemin principal de génération |
| `useAIChallengeGenerator.ts` | Orchestre le flux SSE défi — chemin principal de génération |
| `useExercises.ts` | Hook principal de la page exercices |
| `useAuth.ts` | Gestion de session — impact sécurité |
| `useRecommendations.ts` | Affiche les recommandations personnalisées |
| `useSubmitAnswer.ts` | Validation des réponses — impact gamification |

---

## Règle d'ajout

Tout nouveau hook doit :
1. Figurer dans ce catalogue avec sa catégorie, son rôle et ses dépendances.
2. Avoir un fichier de test dans `frontend/__tests__/unit/hooks/`.
3. Utiliser React Query (`useQuery` / `useMutation`) pour tout appel réseau — pas de `fetch` direct dans un hook.

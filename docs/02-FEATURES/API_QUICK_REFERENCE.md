# API QUICK REFERENCE - MATHAKINE

> Reference condensee des endpoints actifs
> Mise a jour : 13/03/2026
> Source de verite runtime : `server/routes/`

## Regles de lecture

- ce document resume les routes actives montees dans Starlette
- la verite terrain reste `server/routes/` + `server/handlers/`
- `app/api/endpoints/` n'est pas monte dans le runtime actif
- le handler HTML `generate_exercise` existe encore mais n'est pas une route Starlette active

## Auth

| Methode | Endpoint | Notes |
|---|---|---|
| POST | `/api/auth/login` | login + cookies auth |
| GET | `/api/auth/csrf` | recupere le token CSRF |
| POST | `/api/auth/validate-token` | validation de token |
| POST | `/api/auth/refresh` | refresh via cookie/body |
| POST | `/api/auth/logout` | supprime les cookies |
| POST | `/api/auth/forgot-password` | message generique |
| POST | `/api/auth/reset-password` | revoque anciens tokens et sessions |
| GET | `/api/auth/verify-email` | verification email |
| POST | `/api/auth/resend-verification` | message generique aussi sur email inconnu/mal forme |

## Users

| Methode | Endpoint | Notes |
|---|---|---|
| POST | `/api/users/` | inscription |
| GET | `/api/users/` | placeholder / en developpement |
| GET | `/api/users/me` | utilisateur courant |
| PUT | `/api/users/me` | mise a jour profil |
| PUT | `/api/users/me/password` | changement mot de passe + revocation |
| DELETE | `/api/users/me` | suppression compte courant |
| GET | `/api/users/me/export` | export RGPD |
| GET | `/api/users/me/sessions` | sessions actives |
| DELETE | `/api/users/me/sessions/{session_id}` | revoke session |
| GET | `/api/users/me/progress/timeline` | timeline progression |
| GET | `/api/users/me/progress` | progression globale |
| GET | `/api/users/me/challenges/progress` | progression defis |
| GET | `/api/users/stats` | stats utilisateur |
| GET | `/api/users/leaderboard` | leaderboard |
| DELETE | `/api/users/{user_id}` | route active mais renvoie vers `/api/users/me` pour self-delete |

## Daily challenge

| Methode | Endpoint | Notes |
|---|---|---|
| GET | `/api/daily-challenges` | 3 defis du jour pour l'utilisateur |

## Diagnostic

| Methode | Endpoint | Notes |
|---|---|---|
| GET | `/api/diagnostic/status` | dernier score / etat |
| POST | `/api/diagnostic/start` | demarre une session |
| POST | `/api/diagnostic/question` | prochaine question |
| POST | `/api/diagnostic/answer` | soumet une reponse intermediaire |
| POST | `/api/diagnostic/complete` | persiste le resultat |

## Exercises

| Methode | Endpoint | Notes |
|---|---|---|
| GET | `/api/exercises` | liste / filtres / hide_completed |
| GET | `/api/exercises/stats` | stats accueil |
| GET | `/api/exercises/interleaved-plan` | plan entrelace |
| GET | `/api/exercises/{exercise_id}` | detail exercice |
| POST | `/api/exercises/generate` | generation active montee runtime |
| GET | `/api/exercises/generate-ai-stream` | SSE generation IA |
| GET | `/api/exercises/completed-ids` | ids completes |
| POST | `/api/exercises/{exercise_id}/attempt` | soumission reponse |

## Challenges

| Methode | Endpoint | Notes |
|---|---|---|
| GET | `/api/challenges` | liste / filtres / hide_completed |
| GET | `/api/challenges/{challenge_id}` | detail defi |
| POST | `/api/challenges/{challenge_id}/attempt` | soumission reponse |
| GET | `/api/challenges/{challenge_id}/hint` | indice |
| GET | `/api/challenges/completed-ids` | ids completes |
| GET | `/api/challenges/generate-ai-stream` | SSE generation IA |
| GET | `/api/challenges/badges/progress` | progression badges challenge |

## Badges

| Methode | Endpoint | Notes |
|---|---|---|
| GET | `/api/badges/user` | badges utilisateur |
| GET | `/api/badges/available` | badges publics |
| POST | `/api/badges/check` | verification badges |
| GET | `/api/badges/stats` | stats gamification |
| GET | `/api/badges/rarity` | stats rarete |
| PATCH | `/api/badges/pin` | badge_ids a epingler |
| GET | `/api/challenges/badges/progress` | progression badges challenge |

## Admin

| Methode | Endpoint | Notes |
|---|---|---|
| GET | `/api/admin/health` | health admin |
| GET | `/api/admin/overview` | overview |
| GET | `/api/admin/users` | liste users |
| PATCH | `/api/admin/users/{user_id}` | mutation user |
| POST | `/api/admin/users/{user_id}/send-reset-password` | envoi reset |
| POST | `/api/admin/users/{user_id}/resend-verification` | renvoi verification |
| DELETE | `/api/admin/users/{user_id}` | suppression admin |
| GET | `/api/admin/exercises` | liste exercises |
| POST | `/api/admin/exercises` | creation exercise |
| POST | `/api/admin/exercises/{exercise_id}/duplicate` | duplication exercise |
| GET | `/api/admin/exercises/{exercise_id}` | detail exercise |
| PUT | `/api/admin/exercises/{exercise_id}` | mise a jour complete |
| PATCH | `/api/admin/exercises/{exercise_id}` | patch exercise |
| GET | `/api/admin/challenges` | liste challenges |
| POST | `/api/admin/challenges` | creation challenge |
| POST | `/api/admin/challenges/{challenge_id}/duplicate` | duplication challenge |
| GET | `/api/admin/challenges/{challenge_id}` | detail challenge |
| PUT | `/api/admin/challenges/{challenge_id}` | mise a jour complete |
| PATCH | `/api/admin/challenges/{challenge_id}` | patch challenge |
| GET | `/api/admin/reports` | reports |
| GET | `/api/admin/feedback` | feedback admin |
| GET | `/api/admin/audit-log` | audit log |
| GET | `/api/admin/moderation` | moderation |
| GET | `/api/admin/config` | lecture config |
| PUT | `/api/admin/config` | ecriture config |
| GET | `/api/admin/export` | export CSV |
| GET | `/api/admin/badges` | liste badges |
| POST | `/api/admin/badges` | creation badge |
| GET | `/api/admin/badges/{badge_id}` | detail badge |
| PUT | `/api/admin/badges/{badge_id}` | mise a jour badge |
| DELETE | `/api/admin/badges/{badge_id}` | soft delete badge |
| GET | `/api/admin/analytics/edtech` | analytics EdTech |
| GET | `/api/admin/ai-stats` | stats IA |
| GET | `/api/admin/generation-metrics` | metriques generation |

## Misc

| Methode | Endpoint | Notes |
|---|---|---|
| POST | `/api/analytics/event` | analytics applicatif |
| POST | `/api/feedback` | creation feedback |
| GET | `/api/recommendations` | recommandations |
| POST | `/api/recommendations/generate` | genere recommandations |
| POST | `/api/recommendations/complete` | complete recommandation |
| POST | `/api/chat` | chat public |
| POST | `/api/chat/stream` | chat SSE |
| GET | `/health` | health backend |
| GET | `/robots.txt` | robots |
| GET | `/metrics` | metriques Prometheus |

## References

- [AUTH_FLOW.md](AUTH_FLOW.md)
- [../00-REFERENCE/ARCHITECTURE.md](../00-REFERENCE/ARCHITECTURE.md)
- [../03-PROJECT/ENDPOINTS_NON_INTEGRES.md](../03-PROJECT/ENDPOINTS_NON_INTEGRES.md)

# ENDPOINTS PROGRESSION - DASHBOARD ET WIDGETS

> Mise a jour : 15/03/2026
> Source de verite runtime : `server/routes/`

## Objectif

Lister les endpoints de progression effectivement exploitables par le frontend dashboard/widgets, sans melanger routes actives, placeholders et hypotheses de design.

## Endpoints actifs utiles

### `GET /api/daily-challenges`

Usage:

- hook `useDailyChallenges`
- widget daily challenges

Contrat general:

- auth requise
- renvoie `{challenges: [...]}`
- cree les defis du jour si necessaire

### `GET /api/users/stats`

Usage:

- hook `useUserStats`
- dashboard stats utilisateur

Contrat general:

- auth requise
- supporte `timeRange=7|30|90|all`
- renvoie statistiques agregees utilisateur

### `GET /api/users/me/progress`

Usage possible:

- widgets de progression globale
- streak / progression par categorie

### `GET /api/users/me/progress/timeline`

Usage possible:

- timeline de progression
- vue periodique `7d` / `30d`

### `GET /api/users/me/challenges/progress`

Usage possible:

- progression defis
- widgets challenge dashboard

## Endpoints badges/progression lies

### `GET /api/badges/stats`

Usage possible:

- stats gamification utilisateur

### `GET /api/challenges/badges/progress`

Usage possible:

- progression badges lies aux defis

## Regles d'integration frontend

- verifier le contrat actif dans `server/routes/` et `server/handlers/` avant toute integration
- ne pas deduire un endpoint d'un ancien doc FastAPI
- ne pas traiter une route placeholder comme feature exploitable sans verifier la reponse runtime

## Notes techniques

- backend actif: Starlette, port dev par defaut `10000` (`enhanced_server.py`)
- authentification supportee selon endpoint: cookie `access_token` et/ou bearer token
- `app/api/endpoints/*` est archive dans `_ARCHIVE_2026/`; la source de verite active reste `server/routes/` + `server/handlers/`

## References

- [../../02-FEATURES/API_QUICK_REFERENCE.md](../../02-FEATURES/API_QUICK_REFERENCE.md)
- [../../02-FEATURES/F02_DEFIS_QUOTIDIENS.md](../../02-FEATURES/F02_DEFIS_QUOTIDIENS.md)
- [../../02-FEATURES/AUTH_FLOW.md](../../02-FEATURES/AUTH_FLOW.md)

# Lot A2 - Auth Session Execution

## Mission

Passer la boundary `auth/session` sur le modele `async HTTP / sync DB in threadpool`, avec handlers minces et use cases sync executes via helper unique.

## Contexte actuel prouve

- `auth/session` est deja relativement bien decouple via `auth_session_service.py`
- le risque actuel est l'execution DB sync en handler async
- la surface critique concerne: login, refresh, validate-token, current-user, logout

## Faux positifs a eviter

- ne pas rouvrir `auth recovery`
- ne pas changer cookies, routes ou payloads
- ne pas refaire `auth_service.py` si le helper suffit

## Ce qui est mal place

- appels sync DB enclenches directement depuis une couche HTTP async

## Ce qui est duplique ou fragile

- logique d'execution encore implicite selon les endpoints

## Decoupage cible

- handler async mince
- `run_db_bound(auth_session_service.<use_case>, ...)`
- services auth restent sync

## Exemples avant/apres

### Avant

```py
async def api_refresh_token(request):
    async with db_session() as db:
        result = perform_refresh(db, ...)
```

### Apres

```py
async def api_refresh_token(request):
    result = await run_db_bound(auth_session_service.perform_refresh, ...)
```

## Fichiers a lire avant toute modification

- `server/handlers/auth_handlers.py`
- `app/services/auth_session_service.py`
- `app/services/auth_recovery_service.py`
- `app/services/auth_service.py`
- `server/auth.py`
- `tests/api/test_auth_flow.py`
- `tests/integration/test_auth_cookies_only.py`
- `tests/integration/test_auth_no_fallback.py`

## Scope autorise

- `server/handlers/auth_handlers.py`
- `app/services/auth_session_service.py`
- `app/services/auth_recovery_service.py` si strictement necessaire
- `app/services/auth_service.py` au strict minimum
- helper runtime deja cree au lot A1
- tests auth strictement necessaires

## Scope interdit

- `challenge`
- `exercise`
- `admin`
- `badge`
- cookies/routes/payloads

## Checks exacts

1. `git status --short`
2. `git diff --name-only`
3. run 1 auth cible
4. run 2 auth cible
5. full suite sans faux gate
6. `black app/ server/ tests/ --check`

## Exigences de validation

- prouver qu'aucun handler du scope n'ouvre directement la DB
- lister les routes auth/session touchees
- full suite obligatoire

## Stop conditions

- si auth recovery doit etre rouverte massivement
- si cookies/contracts devraient changer

## Format de compte-rendu final

1. Fichiers modifies
2. Routes touchees
3. Ce qui a quitte les handlers
4. Ce qui a ete prouve
5. Ce qui n'a pas ete prouve
6. Resultat run 1
7. Resultat run 2
8. Resultat full suite
9. Risques residuels
10. GO / NO-GO

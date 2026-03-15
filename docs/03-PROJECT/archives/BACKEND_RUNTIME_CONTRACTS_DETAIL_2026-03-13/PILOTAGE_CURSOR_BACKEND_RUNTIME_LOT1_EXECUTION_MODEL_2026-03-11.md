# Lot A1 - Execution Model

## Mission

Introduire un helper unique `run_db_bound(...)` pour executer les use cases sync et les acces DB sync hors de l'event loop, puis l'appliquer a un vertical pilote `auth/session`.

## Contexte actuel prouve

- `app/utils/db_utils.py` expose un `asynccontextmanager`
- ce contexte ouvre en realite une `SessionLocal` synchrone
- les handlers Starlette sont `async`, donc la DB peut encore bloquer l'event loop
- `auth/session` est le bon vertical pilote: surface critique, deja bien testee, perimetre borne

## Faux positifs a eviter

- ne pas lancer une migration globale `AsyncSession`
- ne pas retoucher toutes les verticales du backend dans ce lot
- ne pas confondre `helper threadpool` avec une couche repository complete

## Ce qui est mal place

- `db_session()` donne l'impression d'un modele async natif alors que l'execution reste sync
- les handlers `async` pilotent encore directement de la DB sync

## Ce qui est duplique ou fragile

- patterns `async with db_session()` disperses
- absence de point unique pour la politique d'execution sync/async

## Decoupage cible

- nouveau helper central dans `app/core/runtime.py` ou fichier equivalent
- signature cible example:

```py
async def run_db_bound(func, *args, **kwargs):
    ...
```

- helper reutilisable par les handlers refactores
- `auth/session` sert de vertical pilote

## Exemples avant/apres

### Avant

```py
async def api_login(request):
    data = await request.json()
    async with db_session() as db:
        result = AuthService.authenticate_user_with_session(db, ...)
    return JSONResponse(result)
```

### Apres

```py
async def api_login(request):
    data = await request.json()
    result = await run_db_bound(auth_session_service.perform_login, ...)
    return JSONResponse(result)
```

## Fichiers a lire avant toute modification

- `app/utils/db_utils.py`
- `app/db/base.py`
- `server/handlers/auth_handlers.py`
- `app/services/auth_session_service.py`
- `app/services/auth_recovery_service.py`
- `app/services/auth_service.py`
- `tests/api/test_auth_flow.py`
- `tests/integration/test_auth_cookies_only.py`
- `tests/integration/test_auth_no_fallback.py`

## Scope autorise

- `app/utils/db_utils.py`
- nouveau helper runtime
- `server/handlers/auth_handlers.py`
- `app/services/auth_session_service.py`
- `app/services/auth_recovery_service.py`
- `app/services/auth_service.py` au strict minimum necessaire
- tests auth strictement necessaires

## Scope interdit

- migration globale `AsyncSession`
- `challenge`
- `exercise`
- `admin`
- `badge`
- `frontend`

## Checks exacts

1. `git status --short`
2. `git diff --name-only`
3. run 1 auth cible
4. run 2 auth cible
5. `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py`
6. `black app/ server/ tests/ --check`

## Exigences de validation

- montrer ou `run_db_bound(...)` vit
- lister les handlers auth passes sur ce modele
- distinguer runtime/tests
- full suite obligatoire car runtime touche

## Stop conditions

- si la migration vers le helper impose une refonte globale auth
- si un redesign `AsyncSession` devient indispensable pour finir ce lot

## Format de compte-rendu final

1. Fichiers modifies
2. Fichiers runtime modifies
3. Fichiers tests modifies
4. Routes touchees
5. Ce qui a ete prouve
6. Ce qui n'a pas ete prouve
7. Comment `run_db_bound(...)` a ete introduit
8. Resultat run 1
9. Resultat run 2
10. Resultat full suite
11. Risques residuels
12. GO / NO-GO

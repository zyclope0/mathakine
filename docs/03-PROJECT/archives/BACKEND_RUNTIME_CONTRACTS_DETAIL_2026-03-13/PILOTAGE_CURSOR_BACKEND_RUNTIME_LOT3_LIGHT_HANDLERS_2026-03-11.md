# Lot A3 - Lightweight Handlers

## Mission

Finir les handlers legers encore hybrides: analytics, feedback, daily challenge, diagnostic.

## Contexte actuel prouve

- ces domaines portent encore des `async with db_session()` dans les handlers
- leur logique metier est plus petite que `challenge` ou `exercise`, donc le ROI de completion est eleve

## Faux positifs a eviter

- ne pas rouvrir le read path admin deja stabilise
- ne pas ouvrir les domaines exercise/challenge massifs dans ce lot

## Ce qui est mal place

- DB dans les handlers
- validation payload partielle ou absente
- wiring service + logique HTTP melanges

## Ce qui est duplique ou fragile

- parsing payload / query params dans les handlers
- patterns d'erreur heterogenes

## Decoupage cible

- chaque handler async devient parse -> validate -> `run_db_bound(use_case, ...)` -> response
- nouveaux petits services applicatifs si necessaire

## Exemples avant/apres

```py
# avant
async def post_feedback(request):
    data = await request.json()
    async with db_session() as db:
        return JSONResponse(FeedbackService.create_feedback(db, data))

# apres
async def post_feedback(request):
    body = FeedbackCreateRequest.model_validate(await request.json())
    result = await run_db_bound(feedback_application_service.create_feedback, body)
    return JSONResponse(result)
```

## Fichiers a lire avant toute modification

- `server/handlers/analytics_handlers.py`
- `server/handlers/feedback_handlers.py`
- `server/handlers/daily_challenge_handlers.py`
- `server/handlers/diagnostic_handlers.py`
- services associes
- tests associes

## Scope autorise

- handlers/services des 4 domaines cibles
- schemas Pydantic manquants si necessaires
- helper runtime deja cree
- tests cibles

## Scope interdit

- `challenge`
- `exercise`
- `admin`
- `badge`
- `frontend`

## Checks exacts

1. `git status --short`
2. `git diff --name-only`
3. run 1 batterie cible
4. run 2 batterie cible
5. full suite si runtime touche
6. `black app/ server/ tests/ --check`

## Exigences de validation

- lister les handlers qui n'ouvrent plus la DB
- distinguer runtime/tests
- prouver les endpoints reels touches

## Stop conditions

- si un domaine force un refactor metier profond
- si les payloads publics devraient changer

## Format de compte-rendu final

1. Fichiers modifies
2. Endpoints touches
3. Ce qui a quitte les handlers
4. Ce qui a ete prouve
5. Ce qui n'a pas ete prouve
6. Resultat run 1
7. Resultat run 2
8. Resultat full suite
9. Risques residuels
10. GO / NO-GO

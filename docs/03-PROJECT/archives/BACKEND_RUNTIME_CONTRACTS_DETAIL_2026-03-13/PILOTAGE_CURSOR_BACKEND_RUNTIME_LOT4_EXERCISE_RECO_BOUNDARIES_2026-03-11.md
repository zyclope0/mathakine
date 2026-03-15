# Lot A4 - Exercise Recommendation Daily Boundaries

## Mission

Homogeneiser les zones encore hybrides dans `exercise`, `recommendation` et les reliquats `daily_challenge`, sans reouvrir les lots deja fermes.

## Contexte actuel prouve

- le domaine `exercise` a beaucoup progresse mais pas partout
- `recommendation_service.py` reste aussi un hotspot de requetes et de wiring
- `daily_challenge` contient encore des handlers a finir

## Faux positifs a eviter

- ne pas refaire les lots exercise deja stabilises
- ne pas lancer ici le chantier de performance SQL profond

## Ce qui est mal place

- derniers acces DB dans les handlers
- adapter/db wiring encore visibles

## Ce qui est duplique ou fragile

- queries params et mapping de payloads selon les domaines

## Decoupage cible

- completion des boundaries via helper runtime et services applicatifs sync

## Exemples avant/apres

```py
# avant
async def get_recommendations(request):
    async with db_session() as db:
        return JSONResponse(RecommendationService.get_for_user(db, ...))

# apres
async def get_recommendations(request):
    result = await run_db_bound(recommendation_application_service.get_for_user, ...)
    return JSONResponse(result)
```

## Fichiers a lire avant toute modification

- handlers/services `exercise`
- handlers/services `recommendation`
- handlers/services `daily_challenge`
- tests associes

## Scope autorise

- handlers/services des domaines cibles
- helper runtime deja cree
- schemas manquants strictement necessaires
- tests cibles

## Scope interdit

- `admin`
- `challenge`
- `badge`
- migration `AsyncSession`
- `frontend`

## Checks exacts

1. `git status --short`
2. `git diff --name-only`
3. run 1 batterie cible
4. run 2 batterie cible
5. full suite si runtime touche
6. `black app/ server/ tests/ --check`

## Exigences de validation

- lister les handlers completes
- prouver qu'ils n'ouvrent plus la DB
- signaler ce qui reste hors perimetre
- toute reserve runtime restante doit etre nommee avec fichiers + endpoints impactes

## Reserve reportee vers A5 (obligatoire)

La reserve suivante est explicitement hors cloture A4 et doit etre fermee en A5:
- `server/handlers/exercise_handlers.py`: `generate_exercise`, `generate_exercise_api`
- `app/services/exercise_generation_service.py`
- raison: vertical de generation encore non aligne sur le modele cible `run_db_bound(...)` + service sync

## Stop conditions

- si un hotspot force un refactor metier large
- si la perf SQL devient le vrai sujet du lot

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

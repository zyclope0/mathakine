# PILOTAGE_CURSOR_BACKEND_CONTRACTS_LOT2_ADMIN_BADGE_USE_CASES_2026-03-11

## Mission
Transformer les facades `admin` et `badge` actuelles en vrais use cases applicatifs types, sans reouvrir les handlers ni refaire le moteur metier sous-jacent.

## Contexte actuel prouve
- `D:\Mathakine\app\services\admin_application_service.py` et `D:\Mathakine\app\services\admin_read_service.py` ont sorti le wiring HTTP et la DB des handlers, mais utilisent encore des tuples `(result, err, code)` et beaucoup de `dict` non structures.
- `D:\Mathakine\app\services\badge_application_service.py` est une facade utile, mais encore principalement un pass-through de `BadgeService`.
- Les handlers associes sont deja nettement plus minces. Le prochain gain doit venir des contrats de service, pas d'un nouveau deplacement de wiring.
- Les checks des iterations precedentes ont montre que le runtime de ces zones est localement stable. Le lot vise donc un gain de lisibilite, de typage et de robustesse de contrat.

## Faux positifs a eviter
- Ne pas reouvrir `admin_handlers.py` ou `badge_handlers.py` pour du simple re-cablage HTTP.
- Ne pas attribuer a ce lot des rougeurs venant de `tests/api/test_admin_auth_stability.py`, faux gate connu.
- Ne pas transformer le lot en refactor global de `AdminService` ou `BadgeService`.
- Ne pas introduire de DTOs verbeux sans gain reel; le but est de remplacer les tuples et `Dict[str, Any]`, pas d'ajouter du bruit.

## Ce qui est mal place
- Les services applicatifs retournent encore parfois des tuples ambigus `(..., err, code)` plutot que des resultats types ou des exceptions metier.
- Les erreurs de domaine `admin` et `badge` restent insuffisamment explicites.
- Les enveloppes de resultat existent surtout au niveau HTTP, pas encore au niveau use case.

## Ce qui est duplique ou fragile
- Mapping repetitif de tuples de service vers HTTP dans plusieurs handlers.
- `Dict[str, Any]` qui masquent le contrat reel des mutations et lectures admin.
- Pass-through de badge qui laisse les attentes du handler implicites.

## Decoupage cible
- Introduire des objets de commande/resultat types pour `admin` et `badge` dans les services applicatifs.
- Introduire des exceptions metier explicites a la place des tuples `(result, err, code)`.
- Garder `AdminService` et `BadgeService` comme moteurs sous-jacents, mais faire des facades applicatives de vrais use cases.

## Exemples avant/apres
```py
# Mauvais: contrat ambigu
result, err, code = admin_application_service.patch_user(...)
if err:
    return api_error_response(code, err)
return JSONResponse(result)

# Bon: use case type + exceptions metier
result = admin_application_service.update_user(command)
return JSONResponse(result.model_dump())
```

```py
# Mauvais: tuple et dict
result, err, code = badge_application_service.pin_badges(...)

# Bon: contrat type
class PinBadgesResult(BaseModel):
    pinned_badge_ids: list[int]
```

## Fichiers a lire avant toute modification
- `D:\Mathakine\app\services\admin_application_service.py`
- `D:\Mathakine\app\services\admin_read_service.py`
- `D:\Mathakine\app\services\badge_application_service.py`
- `D:\Mathakine\app\services\admin_service.py`
- `D:\Mathakine\app\services\badge_service.py`
- `D:\Mathakine\server\handlers\admin_handlers.py`
- `D:\Mathakine\server\handlers\badge_handlers.py`
- `D:\Mathakine\tests\api\test_admin_badges.py`
- `D:\Mathakine\tests\api\test_badge_endpoints.py`

## Scope autorise
- `D:\Mathakine\app\services\admin_application_service.py`
- `D:\Mathakine\app\services\admin_read_service.py`
- `D:\Mathakine\app\services\badge_application_service.py`
- schemas/types associes si vraiment necessaires
- tests admin/badge strictement necessaires

## Scope interdit
- `D:\Mathakine\app\services\admin_content_service.py`
- `D:\Mathakine\app\services\admin_stats_service.py`
- refactor profond de `BadgeService`
- refactor des handlers HTTP
- `challenge`
- `exercise`
- `auth`
- `frontend`

## Checks exacts
- `git status --short`
- `git diff --name-only`
- `pytest -q tests/api/test_admin_badges.py tests/api/test_badge_endpoints.py --maxfail=20`
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py`
- `black app/ server/ tests/ --check`

## Exigences de validation
- 2 reruns de la batterie cible si le runtime est touche.
- Full suite si le runtime est touche.
- Distinguer `runtime` et `tests` dans le compte-rendu.
- Lister les endpoints reels touches.
- Lister ce qui est prouve et ce qui ne l'est pas.
- Pas de `GO` si le vert n'est pas reproductible.

## Stop conditions
- Si le lot exige un refactor profond de `AdminService` ou `BadgeService`.
- Si le lot deborde sur le read path admin ou sur `challenge`.
- Si les contrats types imposent un changement de payload HTTP public.

## Format de compte-rendu final
1. Fichiers modifies
2. Fichiers runtime modifies
3. Fichiers de test modifies
4. Endpoints reellement touches
5. Ce qui a ete sorti du tuple / dict implicite
6. Nouveaux contrats types / exceptions metier
7. Ce qui a ete prouve
8. Ce qui n'a pas ete prouve
9. Resultat run 1 checks cibles
10. Resultat run 2 checks cibles
11. Resultat full suite
12. Risques residuels
13. Recommendation go / no-go pour le lot suivant

# Cursor Max Effort Backend Protocol

> Date: 11/03/2026
> Statut: actif
> Objectif: fournir un protocole unique pour les lots backend executes en mode quality-first.

## Principe

Un lot backend n'est valide que si 4 choses sont vraies en meme temps:

1. le code touche est relu factuellement
2. le wiring reel est verifie
3. les checks sont reproductibles
4. les endpoints reels modifies sont explicitement prouves

Un lot n'est jamais `GO` sur la seule base d'une suite verte non reproduite.

## Faux gate connu

Le fichier suivant ne doit pas etre utilise comme gate standard tant qu'il lance `pytest` dans `pytest` avec couverture:

- `tests/api/test_admin_auth_stability.py`

## Standard de validation

Chaque lot doit distinguer explicitement:
- fichiers runtime modifies
- fichiers de test modifies
- endpoints reels touches
- ce qui a ete prouve
- ce qui n'a pas ete prouve
- risques residuels

### Gate standard

1. `git status --short`
2. `git diff --name-only`
3. `run 1` de la batterie cible
4. `run 2` de la meme batterie
5. `full suite` si runtime touche
6. `black app/ server/ tests/ --check`
7. `isort app/ server/ --check-only --diff` si le lot touche Python backend

## Regles de verdict

- `GO` seulement si le vert est reproductible
- `NO-GO` si un `run 2` recasse
- `NO-GO` si le code touche n'a pas ete relu factuellement
- `NO-GO` si les endpoints reels modifies ne sont pas listes
- `NO-GO` si le report conclut sans distinguer runtime et tests

## Regle anti-boucle

Quand un meme symptome revient sur plusieurs tours, on ne continue pas indefiniment en micro-correctifs sans preuve nouvelle.

Regle imposee:
1. au premier echec: diagnostiquer et corriger si la cause est prouvee
2. au deuxieme echec sur le meme symptome: recontroler le tree courant, verifier si le lot est reellement en cause, verifier faux gates et environnement
3. au troisieme tour sans causalite nouvelle: STOP, produire un document de diagnostic/cadrage, puis requalifier le probleme

## Verification prealable avant verdict

Avant de conclure `GO` ou `NO-GO`, verifier:

1. la verite du tree courant
2. la validite de l'environnement de preuve
3. la difference entre probleme du scope et bruit de baseline

### Environnement de preuve

Toujours verifier:
- base de donnees disponible
- faux gate connu ou non
- contention `.coverage`, locks Windows, parallelisme parasite
- execution concurrente de plusieurs `pytest` avec couverture

Regle explicite:
- sur Windows, ne pas lancer plusieurs commandes `pytest` avec `pytest-cov` en parallele
- un lock `.coverage` est un faux positif de tooling tant qu'il n'y a pas d'echec metier associe
- ce faux positif ne doit pas etre confondu avec un rouge runtime

## Attribution causale obligatoire

Chaque rouge observe doit etre classe dans une seule categorie:
1. regression runtime du lot
2. bruit de baseline preexistant
3. faux gate / harnais de test invalide
4. probleme d'environnement
5. hypothese non prouvee

Regles:
- ne jamais attribuer un echec a un lot sans lien causal explicite
- ne jamais utiliser un echec hors scope comme preuve suffisante contre le lot
- si un echec vient d'un faux gate, le signaler comme tel et l'exclure de la decision
- si un echec vient d'un probleme d'environnement, conclure `NO-GO environnement`, pas `NO-GO runtime`

## Exemple handler cible

### Mauvais

```py
@require_auth
async def analytics_event(request):
    body = await request.json()
    async with db_session() as db:
        ok = AnalyticsService.record_edtech_event(db, ...)
        return JSONResponse({"ok": ok})
```

### Bon

```py
@require_auth
async def analytics_event(request):
    body = EventRequest.model_validate(await request.json())
    result = await run_db_bound(
        analytics_application_service.record_event,
        body,
        request.state.user["id"],
    )
    return JSONResponse(result)
```

## Exemple de mauvais report

```text
GO.
Tous les tests passent.
Aucun risque identifie.
```

Pourquoi c'est invalide:
- aucune distinction runtime/tests
- aucun endpoint liste
- aucun rerun prouve
- aucune attribution causale
- aucune verification du tree courant

## Exemple de bon report

```text
1. Fichiers modifies
2. Fichiers runtime modifies
3. Fichiers de test modifies
4. Endpoints reellement touches
5. Ce qui a ete prouve
6. Ce qui n'a pas ete prouve
7. Cause exacte ou meilleure explication defendable
8. Correctif applique et pourquoi il est borne
9. Resultat run 1
10. Resultat run 2
11. Resultat full suite
12. Resultat black
13. Resultat isort
14. Risques residuels
15. Recommendation GO / NO-GO
```

## Mode d'execution backend retenu

Le cycle runtime part du principe suivant:
- handlers HTTP async
- services/repositories sync
- acces DB sync executes via un helper threadpool unique
- pas de migration globale `AsyncSession` dans cette iteration

## Regle finale

Le but n'est pas de faire passer des tests.
Le but est de rendre la base defendable, lisible et stable.

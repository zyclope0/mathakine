# PILOTAGE_CURSOR_BACKEND_CONTRACTS_LOT4_SQL_PERFORMANCE_2026-03-11

## Mission
Traiter les hotspots SQL les plus couteux sans ouvrir de refactor de domaine large, en ciblant d'abord les requetes les plus instables ou les plus gourmandes.

## Contexte actuel prouve
- `D:\Mathakine\app\services\challenge_service.py` conserve un fallback `func.random()` pour certains parcours de selection.
- `D:\Mathakine\app\services\recommendation_service.py` contient encore des requetes dans des boucles et des parcours aleatoires difficiles a stabiliser.
- Le backend a progresse en architecture, mais les hotspots de perf restent principalement herites de l'ancienne structure.
- Les gains de perf reels viendront surtout de la reduction des round-trips SQL et de la suppression des parcours non deterministes couteux.

## Faux positifs a eviter
- Ne pas lancer un "lot perf" sans requetes clairement identifiees.
- Ne pas confondre optimisation SQL et changement de logique metier.
- Ne pas attaquer `challenge_validator.py` dans ce lot.
- Ne pas ouvrir un chantier de cache global sans mesure minimale.

## Ce qui est mal place
- Selection aleatoire directement en SQL sur des ensembles potentiellement grands.
- Requetes executees dans des boucles Python.
- Aggregations qui pourraient vivre cote DB mais restent dispersees en Python.

## Ce qui est duplique ou fragile
- Fallbacks random peu previsibles.
- Recherche repetee d'entites ou de stats deja recuperables en batch.
- Couplage entre strategie de recommandation et mode d'acces DB.

## Decoupage cible
- Traiter `challenge_service.py` et `recommendation_service.py` en sous-lots separes.
- Introduire des helpers de requetage ou prefetch explicites.
- Mesurer au moins le nombre de requetes ou l'elimination du pattern cible, meme sans bench lourd.

## Exemples avant/apres
```py
# Mauvais
query.order_by(func.random()).limit(1)

# Mieux
count = ...
offset = seeded_offset(..., count)
query.offset(offset).limit(1)
```

```py
# Mauvais
for item in recommendations:
    db.query(...)

# Mieux
ids = [...]
rows = db.query(...).filter(Model.id.in_(ids)).all()
```

## Fichiers a lire avant toute modification
- `D:\Mathakine\app\services\challenge_service.py`
- `D:\Mathakine\app\services\recommendation_service.py`
- tests associes a ces parcours

## Scope autorise
- `challenge_service.py` ou `recommendation_service.py`, un sous-probleme cible a la fois
- helpers/repositories associes si necessaires
- tests cibles associes

## Scope interdit
- `challenge_validator.py`
- refactor complet du domaine recommendation
- changement de contrat HTTP
- `frontend`

## Checks exacts
- `git status --short`
- `git diff --name-only`
- batterie cible du sous-probleme choisi
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py`
- `black app/ server/ tests/ --check`

## Exigences de validation
- Nommer la requete/pattern supprime ou reduit.
- Donner la preuve minimum du gain (nombre de requetes, disparition du `func.random()`, batch au lieu de boucle, etc.).
- 2 reruns si runtime touche.
- Full suite si runtime touche.

## Stop conditions
- Si le sous-probleme choisi force un redesign metier.
- Si l'optimisation modifie la logique fonctionnelle sans validation explicite.
- Si le lot part vers du cache global ou de l'infra hors scope.

## Format de compte-rendu final
1. Hotspot traite
2. Pattern SQL/perf cible
3. Fichiers modifies
4. Fichiers runtime modifies
5. Fichiers de test modifies
6. Ce qui a ete optimise
7. Preuve minimale du gain
8. Ce qui a ete prouve
9. Ce qui n'a pas ete prouve
10. Resultat run 1 checks cibles
11. Resultat run 2 checks cibles
12. Resultat full suite
13. Risques residuels
14. Recommendation go / no-go pour le hotspot suivant

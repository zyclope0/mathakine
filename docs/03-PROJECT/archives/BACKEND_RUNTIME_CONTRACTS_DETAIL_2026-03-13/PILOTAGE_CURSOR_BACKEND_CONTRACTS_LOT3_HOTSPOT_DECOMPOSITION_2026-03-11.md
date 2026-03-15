# PILOTAGE_CURSOR_BACKEND_CONTRACTS_LOT3_HOTSPOT_DECOMPOSITION_2026-03-11

## Mission
Decouper les hotspots de services encore monolithiques en sous-responsabilites defendables, avec un ordre strict de priorisation et sans ouvrir de grand refactor flou.

## Contexte actuel prouve
- `D:\Mathakine\app\services\challenge_validator.py` reste un hotspot majeur, malgre l'extraction `maze` deja realisee.
- `D:\Mathakine\app\services\badge_service.py`, `D:\Mathakine\app\services\admin_content_service.py` et `D:\Mathakine\app\services\admin_stats_service.py` restent volumineux et fortement couplés.
- Les iterations recentes ont surtout sorti le wiring des handlers; la prochaine etape est de reduire le blast radius a l'interieur des services.
- La couverture globale a monte, mais plusieurs de ces hotspots restent faiblement couverts.

## Faux positifs a eviter
- Ne pas repartir sur un grand refactor global "service par service".
- Ne pas toucher plusieurs hotspots dans un meme lot d'execution.
- Ne pas confondre extraction structurelle et changement de comportement.
- Ne pas utiliser un decoupage artificiel juste pour faire baisser le nombre de lignes.

## Ce qui est mal place
- Un seul service porte encore plusieurs politiques, requetes et side effects.
- Les hotspots combinent souvent logique pure, orchestration, SQL et transformation d'output.
- Les tests caracterisation ne couvrent pas encore assez les seams internes de ces services.

## Ce qui est duplique ou fragile
- Requetes de selection/transformation repetees.
- Calculs metier caches dans des branches volumineuses.
- Dependances implicites entre sections d'un meme service.

## Decoupage cible
- Travailler par seam explicite, une seule par lot d'execution.
- Introduire sous-services/policies/helpers nommes par responsabilite.
- Garder les contrats publics des services et des handlers stables pendant les extractions.

## Exemples avant/apres
```py
# Mauvais: un service unique pour tout
class ChallengeValidator:
    def validate(...):
        ... pattern ...
        ... sequence ...
        ... maze ...
        ... auto-correct ...

# Bon: seams explicites
class MazeValidationPolicy: ...
class SequenceValidationPolicy: ...
class PatternValidationPolicy: ...
```

```py
# Mauvais: admin content mixe SQL + validation + mapping
class AdminContentService:
    ...

# Bon: decomposition cible
class ExerciseContentWriter: ...
class ChallengeContentWriter: ...
class BadgeContentWriter: ...
```

## Fichiers a lire avant toute modification
- `D:\Mathakine\app\services\challenge_validator.py`
- `D:\Mathakine\app\services\badge_service.py`
- `D:\Mathakine\app\services\admin_content_service.py`
- `D:\Mathakine\app\services\admin_stats_service.py`
- tests cibles associes selon le hotspot choisi

## Scope autorise
- un seul hotspot par execution
- fichiers de tests cibles associes
- nouveaux sous-services/helpers associes au hotspot choisi

## Scope interdit
- refactor simultane de plusieurs hotspots
- changement de contrats HTTP
- refactor transversal admin/challenge/badge a la fois
- `frontend`

## Checks exacts
- `git status --short`
- `git diff --name-only`
- batterie cible du hotspot choisi
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py`
- `black app/ server/ tests/ --check`

## Exigences de validation
- Une seule seam par lot.
- Tests de caracterisation avant extraction si besoin.
- 2 reruns sur la batterie cible si runtime touche.
- Full suite si runtime touche.
- Lister la seam choisie, les preuves et les risques restants.

## Stop conditions
- Si l'extraction force plusieurs hotspots a la fois.
- Si le contrat public doit changer.
- Si le comportement n'est pas suffisamment verrouille par tests.

## Format de compte-rendu final
1. Hotspot traite
2. Seam choisie
3. Fichiers modifies
4. Fichiers runtime modifies
5. Fichiers de test modifies
6. Ce qui a ete extrait
7. Ce qui reste dans le hotspot
8. Ce qui a ete prouve
9. Ce qui n'a pas ete prouve
10. Resultat run 1 checks cibles
11. Resultat run 2 checks cibles
12. Resultat full suite
13. Risques residuels
14. Recommendation go / no-go pour la seam suivante

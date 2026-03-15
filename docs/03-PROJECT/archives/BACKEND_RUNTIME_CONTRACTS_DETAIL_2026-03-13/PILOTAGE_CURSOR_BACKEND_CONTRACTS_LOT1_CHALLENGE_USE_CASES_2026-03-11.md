# Lot B1 - Challenge Use Cases

## Mission

Transformer les facades challenge en vrais use cases types et reduire le couplage de `challenge_attempt_service.py`.

## Contexte actuel prouve

- `challenge_attempt_service.py` est mieux place qu'avant mais encore trop central
- `challenge_query_service.py` et `challenge_stream_service.py` portent encore des contrats faibles
- `Dict[str, Any]` et tuples restent dominants

## Faux positifs a eviter

- ne pas reouvrir la boundary HTTP deja stabilisee
- ne pas ouvrir `challenge_validator.py` dans ce lot

## Ce qui est mal place

- contrats non explicites
- orchestration attempt encore trop couplee

## Ce qui est duplique ou fragile

- resultats sous forme de dictionnaires libres
- erreurs remontees par conventions implicites

## Decoupage cible

- commandes/resultats Pydantic ou DTO types
- exceptions metier dediees
- `challenge_attempt_service` reduit en use case clair

## Exemples avant/apres

### Avant

```py
result: Dict[str, Any] = {
    "is_correct": is_correct,
    "new_badges": new_badges,
}
```

### Apres

```py
result = SubmitChallengeAttemptResult(
    is_correct=is_correct,
    explanation=explanation,
    new_badges=new_badges,
    progress_notification=progress_notification,
    hints_remaining=hints_remaining,
)
```

## Fichiers a lire avant toute modification

- `app/services/challenge_attempt_service.py`
- `app/services/challenge_query_service.py`
- `app/services/challenge_stream_service.py`
- `app/services/logic_challenge_service.py`
- `app/schemas/logic_challenge.py`
- tests challenge associes

## Scope autorise

- fichiers challenge ci-dessus
- schemas/DTO necessaires
- tests challenge associes

## Scope interdit

- `challenge_validator.py`
- `admin`
- `badge`
- `frontend`

## Checks exacts

1. `git status --short`
2. `git diff --name-only`
3. run 1 batterie challenge
4. run 2 batterie challenge
5. full suite si runtime touche
6. `black app/ server/ tests/ --check`

## Exigences de validation

- lister les nouveaux DTO/Result
- lister les tuples supprimes
- montrer les exceptions metier creees ou reutilisees

## Stop conditions

- si `challenge_validator.py` devient necessaire
- si le lot implique un redesign du contrat public

## Format de compte-rendu final

1. Fichiers modifies
2. Contrats types introduits
3. Tuples supprimes
4. Ce qui a ete prouve
5. Ce qui n'a pas ete prouve
6. Resultat run 1
7. Resultat run 2
8. Resultat full suite
9. Risques residuels
10. GO / NO-GO

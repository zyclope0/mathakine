# Preuve complementaire sur erreurs fines - 2026-03-14

## Statut

Implante sur un scope volontairement borne.

## Objectif

Ajouter une preuve directe sur quelques branches d'erreur encore surtout
couvertees indirectement, sans ouvrir une matrice exhaustive de tests.

## Scope retenu

- `GET /api/admin/challenges/{id}`
- `POST /api/feedback`
- `POST /api/analytics/event`

## Resultat reel

### 1. `GET /api/admin/challenges/{id}`

Deja couvert directement avant ce lot :

- nominal
- `404`

Fichier :
- `tests/api/test_admin_content.py`

### 2. `POST /api/feedback`

Deja couvert directement avant ce lot :

- nominal
- `400` sur `feedback_type` invalide
- `401` sans authentification

Fichier :
- `tests/api/test_feedback_endpoints.py`

### 3. `POST /api/analytics/event`

Branche d'erreur manquante completee dans ce lot :

- ajout d'un test direct sur `event` invalide -> `400`

Fichier :
- `tests/api/test_admin_analytics.py`

## Pourquoi le scope est borne

Les deux autres endpoints recommandes avaient deja une preuve d'erreur directe.
Le seul manque reel etait donc `POST /api/analytics/event` sur payload invalide.

## Validation

Commande rejouee deux fois :

```powershell
pytest -q tests/api/test_admin_content.py tests/api/test_feedback_endpoints.py tests/api/test_admin_analytics.py --maxfail=20
```

Resultat :

- run 1 : `22 passed`
- run 2 : `22 passed`

Checks complementaires :

- `black app/ server/ tests/ --check` -> vert
- `isort app/ server/ --check-only --diff` -> vert

## Conclusion

Le lot reste petit et causal :

- pas de runtime modifie
- une seule branche d'erreur vraiment manquante ajoutee
- pas d'explosion du perimetre de tests

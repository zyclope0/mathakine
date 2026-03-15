# B5.6 - Premier durcissement mypy sur petits services stabilisés

Date : 2026-03-14
Statut : clos localement

## Objectif

Etendre la strategie `mypy` module-par-module a un scope de faible blast radius :

- `app/services/analytics_service.py`
- `app/services/feedback_service.py`
- `app/services/daily_challenge_service.py`
- `app/services/diagnostic_service.py`

## Configuration retenue

Nouvel override mypy dedie dans `pyproject.toml` :

- `no_implicit_optional = true`
- `check_untyped_defs = true`
- `assignment` retire du `disable_error_code`

Le reste de la configuration globale du projet est inchangé.

## Scope strict retenu

Modules passes en scope plus strict :

- `app.services.analytics_service`
- `app.services.feedback_service`
- `app.services.daily_challenge_service`
- `app.services.diagnostic_service`

Modules explicitement hors scope :

- handlers associes
- `recommendation_service.py`
- `auth_service.py`
- tout autre domaine backend

## Corrections de code appliquees

Aucune.

Le scope passait deja `mypy` avec les contraintes ci-dessus. Le lot a seulement ajoute l'override dedie pour formaliser et verrouiller ce perimetre.

## Commande de validation

```bash
mypy app/services/analytics_service.py app/services/feedback_service.py app/services/daily_challenge_service.py app/services/diagnostic_service.py
```

## Resultat local

- run 1 : `Success: no issues found in 4 source files`
- run 2 : `Success: no issues found in 4 source files`

Validation complementaire si fichiers Python modifies :

```bash
pytest -q tests/api/test_diagnostic_endpoints.py tests/api/test_feedback_endpoints.py tests/api/test_admin_analytics.py tests/unit/test_badge_requirement_engine.py --maxfail=20
```

## Notes

- `feedback_service.py` conserve son contrat `Tuple[Optional[FeedbackReport], Optional[str]]` : acceptable pour ce lot, car aucun refactor contractuel n'etait recherche.
- `diagnostic_service.py` reste plus dense que les trois autres, mais ne necessitait pas de deborder sur `recommendation_service.py`.
- Le lot prouve seulement un nouvel ilot `mypy` plus strict, pas un durcissement global du projet.

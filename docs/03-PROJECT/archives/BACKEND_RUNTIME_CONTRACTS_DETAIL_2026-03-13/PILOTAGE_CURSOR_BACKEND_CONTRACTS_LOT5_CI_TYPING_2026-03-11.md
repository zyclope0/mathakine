# PILOTAGE_CURSOR_BACKEND_CONTRACTS_LOT5_CI_TYPING_2026-03-11

## Mission
Durcir l'industrialisation backend par une progression controlee sur la couverture, le typage et les gates CI, sans casser la cadence de delivery.

## Contexte actuel prouve
- La CI execute bien les tests, mais n'impose pas encore de `--cov-fail-under` bloquant.
- `pytest.ini` et `.github/workflows/tests.yml` restent permissifs sur ce point.
- `mypy` reste tres relache dans `D:\Mathakine\pyproject.toml`, avec plusieurs exclusions larges et `disable_error_code` massifs.
- La couverture globale a monte, mais plusieurs modules critiques restent faiblement couverts (`challenge_validator`, `badge_requirement_engine`, `admin_stats_service`, `diagnostic_service`, `email_service`).

## Faux positifs a eviter
- Ne pas monter brutalement les seuils de couverture si cela casse toute la CI sans plan.
- Ne pas activer `strict = true` sur tout le repo d'un coup.
- Ne pas confondre couverture globale et couverture utile sur les hotspots critiques.
- Ne pas toucher `frontend` ou les workflows non backend.

## Ce qui est mal place
- La CI collecte la couverture mais ne l'utilise pas encore comme garde-fou bloquant.
- `mypy` autorise encore trop d'erreurs implicites pour guider les futures refontes.
- Les exclusions temporaires ne sont pas suffisamment explicites ou hierarchisees.

## Ce qui est duplique ou fragile
- Meme logique de gate re-exprimee entre docs et workflow.
- Dettes de typage masquees par des `Dict[str, Any]` et des options permissives globales.
- Modules critiques peu couverts malgre une couverture globale honorable.

## Decoupage cible
- Introduire `--cov-fail-under=65`, puis planifier 70 dans la doc si 65 est stable.
- Durcir `mypy` module par module, avec liste explicite des zones encore exclues.
- Prioriser d'abord les modules critiques les plus utilises.

## Exemples avant/apres
```yaml
# Mauvais
- pytest

# Bon
- pytest --cov=app --cov=server --cov-fail-under=65
```

```toml
# Mauvais
ignore_missing_imports = true

# Mieux
[[tool.mypy.overrides]]
module = ["app.services.challenge_validator"]
ignore_errors = true  # temporaire, documente
```

## Fichiers a lire avant toute modification
- `D:\Mathakine\pytest.ini`
- `D:\Mathakine\.github\workflows\tests.yml`
- `D:\Mathakine\pyproject.toml`
- rapport coverage courant si present
- docs d'architecture/versioning si besoin pour documenter le palier

## Scope autorise
- `pytest.ini`
- `.github/workflows/tests.yml`
- `pyproject.toml`
- docs techniques associees si necessaires pour expliquer le palier choisi
- tests ponctuels si necessaires pour faire passer un nouveau gate bloqueur raisonnable

## Scope interdit
- refactor runtime large backend
- `frontend`
- changement de contrat HTTP
- lot de perf ou de decomposition de service

## Checks exacts
- `git status --short`
- `git diff --name-only`
- commande CI ciblee locale si faisable
- `pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py`
- `black app/ server/ tests/ --check`

## Exigences de validation
- Le nouveau seuil doit etre justifie et atteignable sur le tree courant.
- Les exclusions mypy doivent etre documentees, pas implicites.
- Pas de `GO` si la CI locale representative rouge par effet de seuil non maitrise.

## Stop conditions
- Si monter le seuil coverage exige un chantier de tests beaucoup plus large.
- Si durcir mypy casse massivement le repo sans plan incremental defendable.
- Si le lot derive en refactor runtime large.

## Format de compte-rendu final
1. Fichiers modifies
2. Gates CI/typing modifies
3. Nouveau seuil coverage
4. Nouvelles regles mypy
5. Ce qui a ete prouve
6. Ce qui n'a pas ete prouve
7. Resultat des checks locaux
8. Risques residuels
9. Recommendation go / no-go pour cloturer l'iteration B

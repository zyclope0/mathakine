# Tests Mathakine

Updated : 2026-04-10

Ce dossier contient la suite backend Python (`pytest`) et les utilitaires associes.

## Commandes

```bash
# Tous les tests backend
python -m pytest tests/ -v

# Avec couverture
python -m pytest tests/ --cov=app --cov=server --cov-report=term-missing --cov-report=html

# Tests unitaires uniquement
python -m pytest tests/unit/ -v

# Tests API
python -m pytest tests/api/ -v

# Exclure les tests lents
python -m pytest tests/ -v -m "not slow"
```

## Structure

```text
tests/
|-- api/
|-- unit/
|-- integration/
|-- functional/
|-- fixtures/
|-- utils/
`-- conftest.py
```

## Source de verite

Ne pas figer ici un nombre de tests ou un pourcentage de couverture.

La verite active des commandes, conventions et prerequis de test est :

- `docs/01-GUIDES/TESTING.md`
- `docs/01-GUIDES/CREATE_TEST_DATABASE.md`

## Points importants

1. `TEST_DATABASE_URL` doit etre defini dans l'environnement de test.
2. utiliser les helpers de donnees de test pour eviter les collisions.
3. le nettoyage est gere par les fixtures et utilitaires du repo.
4. les tests async backend utilisent `httpx.AsyncClient` et `pytest-asyncio`.

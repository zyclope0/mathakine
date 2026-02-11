# Tests Mathakine

**Dernière mise à jour** : 11 février 2026

## État actuel

- **368 tests passent**, 18 skippés
- **~48 % couverture** (app + server)
- **CI** : pytest + coverage, upload Codecov

## Commandes

```bash
# Tous les tests
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

```
tests/
├── api/           # Tests des endpoints REST
├── unit/          # Tests unitaires (services, modèles, utils)
├── integration/   # Tests d'intégration (auth cookies, exercise workflow, etc.)
├── functional/   # Tests fonctionnels (challenges isolés avec DB)
├── fixtures/     # Fixtures partagées
├── utils/        # Utilitaires (nettoyage données, helpers)
└── conftest.py   # Configuration pytest, fixtures globales
```

## Documentation

- **[docs/01-GUIDES/TESTING.md](../docs/01-GUIDES/TESTING.md)** – Guide complet des tests
- **[PLAN_TESTS_AMELIORATION.md](PLAN_TESTS_AMELIORATION.md)** – Plan et corrections appliquées
- **[CREATE_TEST_DATABASE.md](../docs/01-GUIDES/CREATE_TEST_DATABASE.md)** – Configuration base de test

## Points importants

1. **TEST_DATABASE_URL** obligatoire (voir CREATE_TEST_DATABASE.md)
2. **Données de test** : utiliser `unique_username()` / `unique_email()` pour éviter les conflits
3. **Nettoyage** : `TestDataManager` nettoie automatiquement les données de test après chaque run
4. **Tests async** : tous les tests API/integration utilisent `httpx.AsyncClient` + `pytest-asyncio`

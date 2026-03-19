# CREER UNE BASE DE TEST - MATHAKINE

> Guide de preparation de la base backend de test
> Mise a jour : 18/03/2026

## Objectif

Les tests backend doivent tourner sur une base PostgreSQL separee de la base de developpement et de toute base de production.

Configuration cible locale:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mathakine
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_mathakine
TESTING=true
```

## Methode recommandee

### 1. Verifier PostgreSQL local et preparer la base de test

```bash
python scripts/check_local_db.py
```

Ce script:
- verifie PostgreSQL sur `localhost:5432`
- cree `test_mathakine` si besoin
- applique schema + seed selon la configuration

### 2. Lancer un run backend complet local

```bash
python scripts/test_backend_local.py
```

Ce script:
- demarre PostgreSQL via Docker si besoin
- prepare la base `test_mathakine`
- initialise le schema
- lance `pytest`

## Alternative Docker locale

Si PostgreSQL n'est pas disponible:

```bash
docker run -d --name pg-mathakine -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15
python scripts/check_local_db.py
```

## Regles de securite

- `TEST_DATABASE_URL` doit etre different de `DATABASE_URL`
- les tests ne doivent jamais retomber sur la base de dev ou de prod
- la base de test doit contenir `test` dans son nom
- ne jamais lancer un script de cleanup de test contre une base non test

## Verification rapide

```bash
pytest -q tests/api/test_auth_flow.py --maxfail=20
```

Puis gate backend standard:

```bash
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py --no-cov
```

## Probleme courant

### `connection refused localhost:5432`

PostgreSQL n'est pas disponible. Refaire:

```bash
python scripts/check_local_db.py
```

### `TEST_DATABASE_URL` absent

Definir explicitement la variable dans l'environnement ou dans `.env` avant de lancer `pytest`.

### Faux positif `.coverage`

Si plusieurs commandes `pytest-cov` tournent en parallele sur Windows, un lock `.coverage` peut produire un faux rouge. Relancer les tests en serie.

## References

- [TESTING.md](TESTING.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [../../README_TECH.md](../../README_TECH.md)

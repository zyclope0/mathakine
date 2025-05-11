# Contexte du projet Mathakine

Ce document sert de point d'entrée rapide pour comprendre l'état actuel du projet, son historique récent et les principales ressources. Il est conçu pour fournir un contexte immédiat.

## État actuel

Généré automatiquement le 08/05/2025

## Activité récente du code

### Derniers commits
- a7b2c9d - Implémentation d'Alembic pour la gestion des migrations de base de données (0 hours ago)
- f6b9af5 - Ajout de l'interface graphique avec templates et fichiers statiques (10 hours ago)
- 2f48ba9 - Fix: Amélioration de la compatibilité PostgreSQL dans app/db/base.py et ajout de script de test (10 hours ago)
- 45829a5 - Fix: Mise à jour du script de démarrage Render pour utiliser PostgreSQL au lieu de SQLite + script de test de connexion (11 hours ago)
- 24b8f85 - Ajout de psycopg2-binary pour la connexion PostgreSQL (11 hours ago)
- 6f2a948 - Mise à jour de la documentation pour le support PostgreSQL et le déploiement sur Render (11 hours ago)
- 676a119 - Ajout de la prise en charge PostgreSQL pour Render et migration des données (11 hours ago)
- ac90d94 - feat: Implémentation de la migration vers PostgreSQL (12 hours ago)
- 1bf97c5 - docs: Correction de la section de renommage dans le README pour éviter toute confusion (12 hours ago)
- 9fa35b8 - feat: Implémentation de la normalisation des données, séparation des endpoints et amélioration des tests (12 hours ago)
- 306833b - docs: Mise à jour complète de la documentation avec normalisation des données (12 hours ago)

## Architecture technique

### Stack technologique
- **Backend**: FastAPI (Python)
- **Base de données**: PostgreSQL (production), SQLite (développement)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Frontend**: Templates HTML avec JavaScript
- **Déploiement**: Render

### Structure simplifiée
```
app/                # Code principal de l'application
├── api/            # Endpoints API
├── models/         # Modèles de données SQLAlchemy
├── schemas/        # Schémas Pydantic
├── core/           # Configuration centrale
└── db/             # Gestion de base de données

templates/          # Templates HTML frontend
static/             # Ressources statiques (CSS, JS, images)
tests/              # Tests (unitaires, API, intégration, fonctionnels)
scripts/            # Scripts utilitaires
docs/               # Documentation
```

## Points d'entrée importants

### Documentation essentielle
- **Vue d'ensemble**: [../README.md](../README.md)
- **Mises à jour récentes**: [docs/CHANGELOG.md](CHANGELOG.md)
- **Résolution de problèmes**: [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Guide de démarrage**: [../GETTING_STARTED.md](../GETTING_STARTED.md)

### Fichiers clés
- **Point d'entrée principal**: `app/main.py`
- **Endpoints exercices**: `app/api/endpoints/exercises.py`
- **Modèle exercices**: `app/models/exercise.py`
- **Frontend exercices**: `templates/exercises.html`

## Principaux défis actuels

1. **Gestion des types PostgreSQL** - Certaines opérations complexes dans SQLAlchemy ont été contournées avec des requêtes SQL directes.
2. **Migrations de base de données** - L'implémentation d'Alembic permet désormais une gestion professionnelle des migrations tout en préservant les tables héritées.
3. **Gestion des transactions** - Des problèmes avec le cycle de vie des transactions SQLAlchemy ont nécessité une refonte des opérations de suppression.
4. **Cohérence des données d'énumération** - Les valeurs de type enum sont maintenant standardisées en minuscules.

## Comment maintenir le contexte dans le futur

1. **Mettre à jour ce fichier** - Actualiser ce document après chaque changement significatif
2. **Consulter les logs git** - Utiliser `git log --oneline --since="2 weeks ago"` pour voir les changements récents
3. **Vérifier l'état des tickets** - Examiner périodiquement les issues GitHub
4. **Utiliser les tags git** - Consulter les tags pour voir les versions stables

## Variables d'environnement importantes

- `DATABASE_URL` - URL de connexion à la base de données
- `DEBUG` - Mode de débogage (true/false)
- `ENVIRONMENT` - Environnement d'exécution (dev/test/prod)
- `SECRET_KEY` - Clé secrète pour les jetons JWT

## Commandes essentielles

```bash
# Démarrer le serveur
python -m app.main

# Exécuter les tests
pytest tests/

# Initialiser la base de données
python scripts/init_db.py

# Migrer vers PostgreSQL
python scripts/migrate_to_postgres.py

# Initialiser Alembic
python scripts/init_alembic.py

# Générer une nouvelle migration
python scripts/generate_migration.py "Description de la migration"

# Appliquer les migrations
alembic upgrade head
```

---

*Ce document doit être mis à jour après chaque changement significatif dans l'architecture ou les fonctionnalités.*

*Dernière mise à jour: 12/05/2025* 
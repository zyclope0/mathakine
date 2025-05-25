# Documentation Mathakine

Bienvenue dans la documentation de Mathakine. Cette documentation est organisée en trois sections principales pour faciliter la navigation et la compréhension du projet.

## 📚 Structure de la Documentation

```mermaid
graph TB
    A[Documentation] --> B[Core]
    A --> C[Tech]
    A --> D[Features]
    A --> E[Assets]
    A --> F[Archive]
```

## 🚀 Documents Principaux (Core/)

- [Guide de démarrage rapide](Core/QUICKSTART.md)
- [Guide de contribution](Core/CONTRIBUTING.md)
- [Diagrammes d'architecture](Core/ARCHITECTURE_DIAGRAMS.md)
- [FAQ](Core/FAQ.md)

## 💻 Documentation Technique (Tech/)

- [Guide de la base de données](Tech/DATABASE.md)
- [Guide des tests](Tech/TESTING.md)
- [Guide de déploiement](Tech/DEPLOYMENT.md)
- [Guide des API](Tech/API.md)
- [Guide de sécurité](Tech/SECURITY.md)

## ✨ Documentation Fonctionnelle (Features/)

- [Exercices mathématiques](Features/EXERCISES.md)
- [Système de progression](Features/PROGRESSION.md)
- [Système de récompenses](Features/REWARDS.md)
- [Mode hors-ligne](Features/OFFLINE.md)
- [Analytics](Features/ANALYTICS.md)

## 📦 Ressources

- [Changelog](CHANGELOG.md)
- [Glossaire](GLOSSARY.md)
- [Licence](../LICENSE)

## 🔍 Navigation Rapide

### Pour les Nouveaux Utilisateurs
1. [Guide de démarrage rapide](Core/QUICKSTART.md)
2. [FAQ](Core/FAQ.md)
3. [Guide des exercices](Features/EXERCISES.md)

### Pour les Développeurs
1. [Guide de contribution](Core/CONTRIBUTING.md)
2. [Architecture](Core/ARCHITECTURE_DIAGRAMS.md)
3. [Guide technique](Tech/DEVELOPMENT.md)

### Pour les Administrateurs
1. [Guide de déploiement](Tech/DEPLOYMENT.md)
2. [Guide de sécurité](Tech/SECURITY.md)
3. [Guide des opérations](Tech/OPERATIONS.md)

## 📅 Mises à jour

La documentation est mise à jour régulièrement. Consultez le [CHANGELOG.md](CHANGELOG.md) pour suivre les modifications.

## 🤝 Contribution

Nous encourageons les contributions à la documentation. Consultez le [guide de contribution](Core/CONTRIBUTING.md) pour plus d'informations.

## 📫 Contact

Pour toute question sur la documentation :
- Ouvrir une issue avec le label `documentation`
- Email : docs@mathakine.fr
- Discord : [canal #documentation](https://discord.mathakine.fr)

---

© 2024-2025 Équipe Mathakine - [mathakine.fr](https://mathakine.fr)

# Mathakine - Plateforme d'apprentissage des mathématiques

## Important: Base de données PostgreSQL

Mathakine utilise **exclusivement PostgreSQL** comme système de gestion de base de données.
SQLite n'est plus supporté pour le développement ou les tests.

## Configuration de la base de données

### Prérequis
- PostgreSQL 13+ installé
- Un utilisateur et une base de données créés

### Configuration de l'environnement
Copiez le fichier `.env.example` en `.env` et configurez les variables suivantes:

```
DATABASE_URL=postgresql://user:password@localhost/mathakine
TEST_DATABASE_URL=postgresql://user:password@localhost/test_mathakine
```

### Création des bases de données

```bash
# Connectez-vous à PostgreSQL
psql -U postgres

# Créez les bases de données
CREATE DATABASE mathakine;
CREATE DATABASE test_mathakine;

# Créez un utilisateur (optionnel)
CREATE USER mathakine_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE mathakine TO mathakine_user;
GRANT ALL PRIVILEGES ON DATABASE test_mathakine TO mathakine_user;
```

## Migrations de base de données

Les migrations sont gérées avec Alembic:

```bash
# Appliquer toutes les migrations
alembic upgrade head

# Créer une nouvelle migration
alembic revision --autogenerate -m "Description de la migration"
```

## Tests

Les tests utilisent également PostgreSQL:

```bash
# Exécuter tous les tests
python -m pytest

# Exécuter un test spécifique
python -m pytest tests/test_enum_adaptation.py -v
```

## Types d'énumération PostgreSQL

PostgreSQL utilise des types d'énumération stricts qui nécessitent une gestion spéciale.
Voir `docs/ENUM_COMPATIBILITY.md` pour plus de détails sur la gestion des énumérations.

## Développement

### Installer les dépendances

```bash
pip install -r requirements.txt
```

### Lancer le serveur de développement

```bash
python mathakine_cli.py run
```
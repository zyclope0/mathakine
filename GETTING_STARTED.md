# Guide de démarrage rapide - Mathakine

Ce guide fournit les instructions pour installer, configurer et exécuter le projet Mathakine pour les nouveaux développeurs.

## Prérequis

- Python 3.10+ (Python 3.13 recommandé)
- pip (gestionnaire de paquets Python)
- Accès à un terminal/ligne de commande
- Git

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-organisation/math-trainer-backend.git
cd math-trainer-backend
```

### 2. Créer un environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Créer un fichier .env

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```
DEBUG=true
ENVIRONMENT=dev
SECRET_KEY=votre_clé_secrète_ici
DATABASE_URL=sqlite:///./mathakine.db
```

Pour PostgreSQL (optionnel) :
```
DATABASE_URL=postgresql://utilisateur:mot_de_passe@localhost:5432/mathakine
```

### 2. Initialiser la base de données

```bash
# Windows
scripts\init_db.bat

# Linux/MacOS
python scripts/init_db.py
```

## Démarrage de l'application

### Méthode 1 : Utiliser le script principal

```bash
# Windows
scripts.bat
# Puis sélectionner l'option 1 dans le menu

# Linux/MacOS
python -m app.main
```

### Méthode 2 : Utiliser la CLI

```bash
python mathakine_cli.py run
```

L'application sera accessible à l'adresse : http://localhost:8000

## Accès à l'API Swagger

L'interface Swagger/OpenAPI est disponible à : http://localhost:8000/docs

## Exécution des tests

```bash
# Exécuter tous les tests (méthode recommandée)
python tests/run_tests.py

# Alternative avec pytest direct
pytest tests/

# Exécuter une catégorie spécifique
pytest tests/api/
pytest tests/unit/
pytest tests/functional/
pytest tests/integration/
```

## Scripts utilitaires

Le dossier `scripts/` contient plusieurs utilitaires pour faciliter le développement :

### Gestion de base de données
- `scripts/toggle_database.py` : Basculer entre SQLite et PostgreSQL
- `scripts/migrate_to_postgres.py` : Migrer les données vers PostgreSQL

### Vérification de qualité
- `scripts/check_project.py` : Vérifier la santé globale du projet
- `scripts/fix_style.py` : Corriger automatiquement les problèmes de style courants
- `scripts/fix_advanced_style.py` : Corriger les problèmes de style plus complexes

### Documentation et maintenance
- `scripts/validate_docs.py` : Valider la documentation du projet
- `scripts/generate_context.py` : Générer le résumé du contexte du projet
- `scripts/detect_obsolete_files.py` : Détecter les fichiers obsolètes

## Menu principal

Le script `scripts.bat` (Windows) ou `Scripts-Menu.ps1` (PowerShell) fournit un menu interactif pour accéder aux principales fonctionnalités :

1. Démarrer l'application
2. Initialiser la base de données
3. Exécuter les tests
4. Accéder au menu de configuration
5. Accéder au menu de documentation
6. Déployer l'application
7. Vérifier la santé du projet

## Problèmes courants

### Problème de connexion à la base de données
Vérifiez que le fichier `.env` est correctement configuré et que les variables d'environnement sont chargées.

### Erreurs de migration PostgreSQL
Assurez-vous que PostgreSQL est installé et en cours d'exécution. Vérifiez les informations de connexion.

### Problèmes d'encodage (Windows)
Utilisez `chcp 65001` dans votre terminal pour passer à l'encodage UTF-8.

### Problèmes de style de code
Utilisez `python scripts/fix_style.py` pour corriger automatiquement la plupart des problèmes de style.

## Ressources supplémentaires

- [Documentation complète](docs/CONTEXT.md)
- [Architecture du projet](docs/ARCHITECTURE.md)
- [Guide de migration PostgreSQL](docs/POSTGRESQL_MIGRATION.md)
- [Guide de dépannage](docs/TROUBLESHOOTING.md)
- [Résumé des améliorations récentes](docs/CLEANUP_SUMMARY.md)

---

*Pour toute question supplémentaire, consultez la documentation complète dans le dossier `docs/` ou contactez l'équipe de développement.*
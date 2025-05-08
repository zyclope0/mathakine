# Math Trainer - Guide de démarrage

Ce document explique comment installer et lancer l'application Math Trainer Backend selon les meilleures pratiques académiques.

## Installation

### Prérequis

- Python 3.8 à 3.13
- pip (gestionnaire de paquets Python)
- Un terminal PowerShell ou CMD (Windows)

> **Note**: Avec Python 3.13, certaines dépendances nécessitent des versions spécifiques:
> - SQLAlchemy 2.0.27+
> - Pydantic 2.0.0+ avec pydantic-settings
> - FastAPI 0.100.0+
>
> Consultez le guide de compatibilité dans `docs/validation/COMPATIBILITY.md` pour plus de détails.

### Installation des dépendances

Pour installer les dépendances requises et configurer l'environnement :

1. Exécutez le script `scripts/setup.bat` à la racine du projet
2. Suivez les instructions à l'écran

```bash
./scripts/setup.bat
```

Alternativement, vous pouvez installer manuellement les dépendances Python :

```bash
pip install -r requirements.txt
```

## Usage

Pour démarrer le serveur Math Trainer :

1. Exécutez le script `run_server.bat` à la racine du projet
2. Le script détecte automatiquement votre environnement (PowerShell ou CMD)
3. Suivez les instructions à l'écran pour choisir le type de serveur à lancer

```bash
./run_server.bat
```

### Options de serveur

Lors du démarrage, vous aurez les options suivantes :

- **Serveur minimal** : API simple sans interface graphique (pour les tests ou l'intégration)
- **Serveur amélioré** : Version complète avec interface graphique interactive
- **Configuration** : Configurer les variables d'environnement avant le lancement

## Configuration

### Profils d'environnement

L'application utilise trois profils d'environnement prédéfinis :

| Profil | Description | Port | Debug | 
|--------|-------------|------|-------|
| dev    | Développement local | 8081 | activé |
| test   | Environnement de test | 8082 | activé |
| prod   | Production | 8080 | désactivé |

Pour modifier les profils, vous pouvez éditer le fichier `scripts/utils/profiles.json`.

### Variables d'environnement

Les principales variables d'environnement configurables sont :

| Variable | Description | Valeurs possibles |
|----------|-------------|-------------------|
| MATH_TRAINER_DEBUG | Active/désactive le mode debug | true/false |
| MATH_TRAINER_PORT | Port d'écoute du serveur | 1024-65535 |
| MATH_TRAINER_LOG_LEVEL | Niveau de logs | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| MATH_TRAINER_PROFILE | Profil actif | dev, test, prod |

Ces variables peuvent être modifiées via les scripts de configuration ou en modifiant directement le fichier `.env` à la racine du projet.

## Gestion de la base de données

### Base de données SQLite locale

L'application utilise SQLite en développement local. Le fichier de base de données (`math_trainer.db`) est automatiquement exclu du contrôle de version (via `.gitignore`).

#### Initialisation de la base de données

Pour initialiser la base de données locale :

```bash
# En batch
scripts/init_db.bat

# En PowerShell
scripts/Initialize-Database.ps1
```

#### Réinitialisation de la base de données

Si vous souhaitez repartir d'une base de données propre :

1. Supprimez le fichier `math_trainer.db` existant
2. Réexécutez le script d'initialisation ci-dessus

#### Structure de la base de données

La base de données contient les tables principales suivantes :

- `users` : Informations des utilisateurs (nom, email, role, niveau, thème préféré)
- `exercises` : Exercices mathématiques (exercise_type, difficulté, question, réponse, choix)
- `logic_challenges` : Défis logiques (type, groupe d'âge, description, solution)
- `settings` : Paramètres système et utilisateur (nom de l'app, version, thème)

Les données initiales incluent :
- Un utilisateur administrateur (Maître Yoda)
- Des exercices d'exemple
- Des défis logiques de démonstration
- Les paramètres système de base

## Structure du projet

Le projet est organisé selon une structure modulaire pour faciliter la maintenance :

```
math-trainer-backend/
├── run_server.bat              # Script de lancement unifié
├── scripts/setup.bat           # Script d'installation unifié
├── GETTING_STARTED.md          # Ce guide
├── README.md                   # Documentation générale
├── minimal_server.py           # Implémentation du serveur minimal
├── enhanced_server.py          # Implémentation du serveur complet
├── requirements.txt            # Dépendances Python
├── scripts/
│   ├── server/                 # Scripts de démarrage du serveur
│   │   ├── start_math_trainer.bat  # Version batch
│   │   └── Run-MathTrainer.ps1     # Version PowerShell
│   ├── utils/                  # Utilitaires pour la gestion des environnements
│   │   ├── env_manager.bat     # Gestion des variables en batch
│   │   ├── env_manager.ps1     # Gestion des variables en PowerShell
│   │   ├── load_profiles.py    # Chargement des profils
│   │   ├── validate_env.py     # Validation des variables
│   │   └── profiles.json       # Définitions des profils
│   ├── setup/                  # Scripts d'installation
│   │   ├── clean_install.bat   # Installation en batch
│   │   └── Install-Dependencies.ps1  # Installation en PowerShell
│   └── tests/                  # Scripts pour exécuter les tests
├── tests/                      # Tests unitaires et d'intégration
├── templates/                  # Templates pour l'interface web
├── static/                     # Fichiers statiques
└── app/                        # Code de l'application
```

## Validation et correction automatique

Le système inclut une validation automatique des variables d'environnement pour s'assurer que les valeurs sont correctes.

Pour valider les variables d'environnement :

```bash
# En batch
scripts/utils/env_manager.bat --validate

# En PowerShell
scripts/utils/env_manager.ps1 -Validate
```

Pour corriger automatiquement les variables invalides :

```bash
# En batch
scripts/utils/env_manager.bat --validate --fix

# En PowerShell
scripts/utils/env_manager.ps1 -Validate -Fix
```

## Exécution des tests

Pour exécuter les tests automatisés :

```bash
# En batch
scripts/tests/run_tests.bat

# En PowerShell
scripts/tests/Run-Tests.ps1
```

## Gestion de la base de données SQLite

La gestion de la base de données SQLite est une partie importante du backend. Voici comment vous pouvez configurer et utiliser la base de données :

### Configuration de la base de données

Pour configurer la base de données, vous devez éditer le fichier `config.py` dans le répertoire `app/`. Vous pouvez spécifier le chemin de la base de données, les paramètres de connexion, etc.

### Utilisation de la base de données

Pour utiliser la base de données, vous pouvez utiliser des outils comme `sqlite3` pour interagir directement avec la base de données, ou des bibliothèques Python comme `sqlite3` pour interagir avec la base de données à partir de votre application.

Pour interagir avec la base de données à partir de votre application, vous pouvez utiliser le module `sqlite3` de Python. Voici un exemple d'utilisation :

```python
import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('math_trainer.db')
cursor = conn.cursor()

# Exécution d'une requête SQL
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# Affichage des résultats
for row in rows:
    print(row)

# Fermeture de la connexion
conn.close()
```

## Système d'Auto-Validation

Le projet intègre un système complet d'auto-validation qui permet de vérifier l'intégrité et la compatibilité du projet. Ce système offre plusieurs niveaux de validation adaptés à différents besoins.

### Configuration de l'environnement de validation

Avant d'utiliser les scripts de validation, configurez l'environnement :

```bash
# En batch
tests/setup_validation.bat

# Directement en Python
python tests/setup_validation.py
```

### Niveaux de validation

#### 1. Validation complète

Exécute tous les tests unitaires, API, d'intégration et fonctionnels :

```bash
# En batch
tests/auto_validate.bat

# Directement en Python
python tests/auto_validation.py
```

#### 2. Validation légère

Vérifie la structure du projet sans dépendances complexes :

```bash
python tests/simple_validation.py
```

#### 3. Validation très simplifiée

Pour diagnostics rapides :

```bash
python tests/simplified_validation.py
```

#### 4. Vérification de compatibilité

Vérifie la compatibilité avec Python 3.13 :

```bash
python tests/compatibility_check.py
```

### Génération de rapports

Pour générer un rapport complet sur l'état du projet :

```bash
python tests/generate_report.py
```

Pour plus d'informations sur le système d'auto-validation, consultez la documentation dans `docs/validation/README.md`.

## Déploiement

Le projet est configuré pour être déployé sur Render. Le fichier `Procfile` contient la commande de démarrage pour Render.

## Contribution

Veuillez consulter les guidelines de contribution avant de soumettre des pull requests.
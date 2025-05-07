# Math Trainer - Guide de démarrage

Ce document explique comment installer et lancer l'application Math Trainer Backend selon les meilleures pratiques académiques.

## Installation

Pour installer les dépendances requises et configurer l'environnement :

1. Exécutez le script `setup.bat` à la racine du projet
2. Suivez les instructions à l'écran

```bash
./setup.bat
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

## Structure du projet

Le projet est organisé selon une structure modulaire pour faciliter la maintenance :

```
math-trainer-backend/
├── run_server.bat              # Script de lancement unifié
├── setup.bat                   # Script d'installation unifié
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
scripts\utils\env_manager.bat --validate

# En PowerShell
scripts\utils\env_manager.ps1 -Validate
```

Pour corriger automatiquement les variables invalides :

```bash
# En batch
scripts\utils\env_manager.bat --validate --fix

# En PowerShell
scripts\utils\env_manager.ps1 -Validate -Fix
```

## Exécution des tests

Pour exécuter les tests automatisés :

```bash
# En batch
scripts\tests\run_tests.bat

# En PowerShell
scripts\tests\Run-Tests.ps1
``` 
# Scripts de Math Trainer Backend

Ce répertoire contient tous les scripts utilitaires pour installer, configurer, exécuter et tester l'application Math Trainer.

## Structure des répertoires

- **`/setup/`** - Scripts d'installation et de configuration initiale
- **`/server/`** - Scripts pour démarrer le serveur (minimal ou amélioré)
- **`/tests/`** - Scripts pour exécuter les tests
- **`/utils/`** - Scripts utilitaires divers (gestion d'environnement, encodage, etc.)

## Points d'entrée principaux

Depuis la racine du projet :

- **`scripts.bat`** - Menu principal en mode batch (CMD)
- **`Scripts-Menu.ps1`** - Menu principal en PowerShell
- **`run_ps1.bat`** - Utilitaire pour exécuter des scripts PowerShell sans restriction

## Scripts de configuration

- **`config_menu.bat`** - Menu de configuration en mode batch
- **`Config-Menu.ps1`** - Menu de configuration en PowerShell

## Gestion des environnements

Les variables d'environnement sont gérées avec :

- **`utils/env_manager.bat`** - Gestionnaire d'environnement en batch
- **`utils/env_manager.ps1`** - Gestionnaire d'environnement en PowerShell
- **`utils/load_env.bat`** - Chargement des variables dans batch
- **`utils/Load-Env.ps1`** - Chargement des variables dans PowerShell

## Profils disponibles

Le système supporte trois profils d'environnement :

- **`dev`** - Environnement de développement (debug activé, port 8000)
- **`test`** - Environnement de test (debug activé, port 8080)
- **`prod`** - Environnement de production (debug désactivé, port 80)

## Documentation supplémentaire

- **`utils/README_ENV.md`** - Documentation du système d'environnement
- **`utils/README_POWERSHELL.md`** - Guide de syntaxe PowerShell vs Batch
- **`utils/ENCODING_GUIDE.md`** - Guide sur la gestion des encodages

## Note sur les encodages

Les scripts batch (.bat) utilisent l'encodage ANSI/ASCII pour éviter les problèmes avec les caractères accentués.
Les scripts PowerShell (.ps1) utilisent l'encodage UTF-8 avec BOM.

## Exemples d'utilisation

### Installation complète
```
scripts\setup\install_and_run.bat
```

### Démarrer le serveur
```
scripts\server\start_math_trainer.bat
```

### Exécuter les tests
```
scripts\tests\run_tests.bat
```

### Configurer l'environnement
```
scripts\config_menu.bat
``` 
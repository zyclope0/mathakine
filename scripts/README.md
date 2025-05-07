# Scripts de Mathakine Backend

Ce répertoire contient tous les scripts utilitaires pour installer, configurer, exécuter et tester l'application Mathakine.

## Structure des répertoires

- **`/scripts/`** - Scripts d'installation, de configuration, de lancement serveur, etc.
- **`/scripts/utils/`** - Scripts utilitaires divers (gestion d'environnement, encodage, etc.)

## Points d'entrée principaux

Depuis la racine du projet :

- **`scripts/scripts.bat`** - Menu principal en mode batch (CMD)
- **`../Scripts-Menu.ps1`** - Menu principal en PowerShell

## Scripts de configuration

- **`scripts/config_menu.bat`** - Menu de configuration en mode batch
- **`scripts/Config-Menu.ps1`** - Menu de configuration en PowerShell

## Gestion des environnements

Les variables d'environnement sont gérées avec :

- **`scripts/utils/env_manager.bat`** - Gestionnaire d'environnement en batch
- **`scripts/utils/env_manager.ps1`** - Gestionnaire d'environnement en PowerShell

## Profils disponibles

Le système supporte trois profils d'environnement :

- **`dev`** - Environnement de développement
- **`test`** - Environnement de test
- **`prod`** - Environnement de production

## Documentation supplémentaire

- **`scripts/utils/README_ENV.md`** - Documentation du système d'environnement
- **`scripts/utils/README_POWERSHELL.md`** - Guide de syntaxe PowerShell vs Batch
- **`scripts/utils/ENCODING_GUIDE.md`** - Guide sur la gestion des encodages

## Exemples d'utilisation

### Installation complète
```
scripts/setup.bat
```

### Démarrer le serveur
```
scripts/start_render.sh
```

### Exécuter les tests
```
scripts/tests/run_tests.bat
```

### Configurer l'environnement
```
scripts/config_menu.bat
``` 
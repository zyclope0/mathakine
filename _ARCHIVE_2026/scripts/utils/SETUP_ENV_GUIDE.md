# Guide de configuration du système d'environnement

Ce guide décrit comment configurer et utiliser le système de gestion des environnements dans un nouveau projet.

## Étape 1 : Installation des scripts

Pour installer le système de gestion des environnements dans votre projet, copiez les fichiers suivants depuis `scripts/utils/` :

- `env_manager.bat` - Gestionnaire d'environnement pour CMD
- `env_manager.ps1` - Gestionnaire d'environnement pour PowerShell
- `load_env.bat` - Chargeur de variables pour CMD
- `Load-Env.ps1` - Chargeur de variables pour PowerShell

## Étape 2 : Personnalisation des profils

Modifiez les profils d'environnement selon les besoins de votre projet :

### Dans env_manager.bat :

```batch
if /i "%PROFILE%"=="dev" (
    set "MY_APP_DEBUG=true"
    set "MY_APP_PORT=8081"
    set "MY_APP_LOG_LEVEL=DEBUG"
    set "MY_APP_TEST_MODE=true"
) else if /i "%PROFILE%"=="test" (
    ...
)
```

### Dans env_manager.ps1 :

```powershell
$envProfiles = @{
    "dev" = @{
        "MY_APP_DEBUG" = "true"
        "MY_APP_PORT" = "8081"
        "MY_APP_LOG_LEVEL" = "DEBUG"
        "MY_APP_TEST_MODE" = "true"
    }
    "test" = @{
        ...
    }
}
```

## Étape 3 : Création du menu de configuration

Si vous souhaitez un menu interactif, copiez et adaptez les fichiers suivants :

- `config_menu.bat` - Menu de configuration pour CMD
- `Config-Menu.ps1` - Menu de configuration pour PowerShell

## Étape 4 : Utilisation dans vos scripts

### Dans un script Batch (.bat)

```batch
@echo off
REM Charger les variables d'environnement
call scripts\utils\load_env.bat dev

REM Utiliser les variables
echo Port: %MY_APP_PORT%
echo Mode debug: %MY_APP_DEBUG%

REM Démarrer votre application
python app.py
```

### Dans un script PowerShell (.ps1)

```powershell
# Charger les variables d'environnement (important : utiliser le dot sourcing)
. ./scripts/utils/Load-Env.ps1 -Profile dev

# Utiliser les variables
Write-Host "Port: $MY_APP_PORT"
Write-Host "Mode debug: $MY_APP_DEBUG"

# Démarrer votre application
python app.py
```

## Étape 5 : Intégration dans votre code source

Pour utiliser les variables d'environnement dans votre code Python :

```python
import os

# Récupérer les variables d'environnement avec valeurs par défaut
DEBUG = os.environ.get("MY_APP_DEBUG", "false").lower() == "true"
PORT = int(os.environ.get("MY_APP_PORT", "8080"))
LOG_LEVEL = os.environ.get("MY_APP_LOG_LEVEL", "INFO")

print(f"Démarrage en mode debug: {DEBUG}")
print(f"Port: {PORT}")
print(f"Niveau de log: {LOG_LEVEL}")
```

## Bonnes pratiques

1. **Versionnage** : Incluez les fichiers `*.bat` et `*.ps1` dans votre contrôle de version, mais pas le fichier `.env`

2. **Gitignore** : Ajoutez `.env` à votre fichier `.gitignore` :
   ```
   # Ignorer les fichiers d'environnement
   .env
   ```

3. **Documentation** : Créez un `README_ENV.md` pour documenter les variables d'environnement utilisées par votre application

4. **CI/CD** : Utilisez les profils appropriés dans vos pipelines d'intégration continue et de déploiement :
   ```batch
   REM Dans votre script de CI
   call scripts\utils\env_manager.bat --profile test --export
   call scripts\tests\run_tests.bat
   ```

5. **Sécurité** : Ne stockez jamais de secrets (mots de passe, clés API) directement dans les profils, utilisez le fichier `.env` local à chaque environnement 
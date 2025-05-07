# Système de Gestion des Environnements

Ce système permet de gérer facilement les variables d'environnement pour différents contextes 
(développement, test, production) dans Math Trainer.

## Profils disponibles

Le système propose trois profils prédéfinis :

1. **DEV** (développement) - Pour le développement local
   - Debug activé, logs détaillés, port 8081
   - Idéal pour le développement et le débogage

2. **TEST** - Pour les tests et la validation
   - Debug activé, logs modérés, port 8082
   - Utilisé pour les tests automatisés

3. **PROD** (production) - Pour le déploiement final
   - Debug désactivé, logs minimaux, port 8080
   - Optimisé pour la performance

## Utilisation des scripts

### Menu interactif

Le moyen le plus simple d'utiliser ce système est via les menus interactifs :

```
scripts/config_menu.bat         # Version CMD
scripts/Config-Menu.ps1         # Version PowerShell
```

Ces menus permettent de :
- Afficher la configuration actuelle
- Changer de profil
- Modifier des variables individuelles
- Configurer la clé API OpenAI
- Réinitialiser le fichier .env

### Scripts en ligne de commande

#### Gestion des environnements (CMD)

```bash
# Afficher les variables du profil actuel
scripts/utils/env_manager.bat --list

# Exporter les variables du profil dev dans un fichier .env
scripts/utils/env_manager.bat --profile dev --export

# Exporter les variables du profil prod dans un fichier .env
scripts/utils/env_manager.bat --profile prod --export

# Définir une variable spécifique
scripts/utils/env_manager.bat --key MATH_TRAINER_PORT --value 8088 --export
```

#### Gestion des environnements (PowerShell)

```powershell
# Afficher les variables du profil actuel
./scripts/utils/env_manager.ps1 -List

# Exporter les variables du profil dev dans un fichier .env
./scripts/utils/env_manager.ps1 -Profile dev -Export

# Exporter les variables du profil prod dans un fichier .env
./scripts/utils/env_manager.ps1 -Profile prod -Export

# Définir une variable spécifique
./scripts/utils/env_manager.ps1 -Key MATH_TRAINER_PORT -Value 8088 -Export
```

### Charger les variables dans vos scripts

Pour utiliser les variables d'environnement dans vos propres scripts :

#### Dans un script Batch (.bat)

```bash
@echo off
REM Charger les variables d'environnement (profil dev par défaut)
call scripts\utils\load_env.bat

REM Ou spécifier un profil particulier
call scripts\utils\load_env.bat prod

REM Utiliser les variables chargées
echo Port: %MATH_TRAINER_PORT%
echo Mode debug: %MATH_TRAINER_DEBUG%
```

#### Dans un script PowerShell (.ps1)

```powershell
# Charger les variables d'environnement (important : utiliser le dot sourcing)
. ./scripts/utils/Load-Env.ps1 -Profile dev

# Utiliser les variables chargées
Write-Host "Port: $MATH_TRAINER_PORT"
Write-Host "Mode debug: $MATH_TRAINER_DEBUG"
```

## Variables disponibles

Les variables principales gérées par ce système sont :

| Variable               | Description                         | Valeurs possibles          |
|------------------------|-------------------------------------|----------------------------|
| MATH_TRAINER_DEBUG     | Active/désactive le mode debug      | true, false                |
| MATH_TRAINER_PORT      | Port du serveur web                 | 8080, 8081, 8082, etc.     |
| MATH_TRAINER_LOG_LEVEL | Niveau de détail des logs           | DEBUG, INFO, WARNING, ERROR |
| MATH_TRAINER_TEST_MODE | Active/désactive le mode test       | true, false                |
| OPENAI_API_KEY         | Clé API pour l'intégration OpenAI   | [clé API]                  |
| MATH_TRAINER_PROFILE   | Profil actif                        | dev, test, prod            |

## Bonnes pratiques

1. **Ne jamais committer de clés API** dans le fichier .env
   - Le fichier .env est déjà dans .gitignore

2. **Utiliser le profil approprié** selon le contexte
   - DEV pour le développement local
   - TEST pour les tests automatisés
   - PROD pour le déploiement

3. **Toujours charger les variables** au début des scripts

4. **Se méfier des sessions PowerShell et CMD**
   - Les variables sont disponibles uniquement dans la session courante
   - Utilisez `load_env.bat` ou `Load-Env.ps1` dans chaque script qui en a besoin 

## Fichier d'exemple .env.example

Un fichier d'exemple `.env.example` est fourni pour vous aider à configurer votre environnement. Ce fichier contient toutes les variables utilisées dans le projet avec des valeurs par défaut.

### Comment l'utiliser

1. Copiez ce fichier vers `.env` à la racine du projet :
   ```bash
   copy .env.example .env
   ```
   ou en PowerShell :
   ```powershell
   Copy-Item .env.example .env
   ```

2. Modifiez les valeurs dans ce fichier selon vos besoins

3. Si le fichier `.env.example` n'existe pas, vous pouvez le créer avec les scripts :
   ```bash
   scripts\utils\create_env_example.bat
   ```
   ou en PowerShell :
   ```powershell
   .\scripts\utils\Create-EnvExample.ps1
   ```

Le fichier `.env.example` est un modèle documenté qui aide les nouveaux développeurs à comprendre rapidement les variables d'environnement nécessaires et leurs valeurs possibles. 
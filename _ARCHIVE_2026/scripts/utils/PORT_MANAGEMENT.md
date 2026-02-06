# Gestion des ports dans Math Trainer

Ce document explique comment sont gérés les ports dans l'application Math Trainer, et comment résoudre les problèmes potentiels.

## Ports par défaut

Chaque environnement utilise un port spécifique:

| Environnement | Port | Variable d'environnement |
|---------------|------|--------------------------|
| Développement (`dev`) | 8081 | `MATH_TRAINER_PORT=8081` |
| Test (`test`) | 8082 | `MATH_TRAINER_PORT=8082` |
| Production (`prod`) | 8080 | `MATH_TRAINER_PORT=8080` |

Ces valeurs sont définies dans le fichier `profiles.json` et sont appliquées automatiquement lorsque vous changez de profil.

## Problèmes courants

### 1. Port occupé

Si le port par défaut est déjà utilisé par une autre application, le serveur tentera de démarrer sur le port 8080 comme alternative.

Exemple d'erreur:
```
Port 8081 déjà utilisé, utilisation du port 8080
```

### 2. Incohérence entre profil et port

Il peut arriver que le port configuré ne corresponde pas au profil:

- Vous avez modifié manuellement la variable `MATH_TRAINER_PORT`
- Vous avez changé de profil mais le serveur utilise toujours l'ancien port
- Le serveur a été relancé sur un port alternatif à cause d'un conflit

## Outils de validation et correction

### Script de validation des ports

Utilisez ce script pour vérifier et corriger les incohérences entre le profil et le port:

**En Batch:**
```
scripts\utils\validate_server_port.bat --check
```

**En PowerShell:**
```
.\scripts\utils\Validate-ServerPort.ps1 -Check
```

### Options disponibles

| Option | Description |
|--------|-------------|
| `--check` / `-Check` | Vérifier sans modifier (mode par défaut) |
| `--fix` / `-Fix` | Corriger automatiquement les problèmes détectés |
| `--verbose` / `-Verbose` | Afficher plus de détails pendant la vérification |
| `--help` / `-Help` | Afficher l'aide |

### Résolution des problèmes courants

#### Cas 1: Serveur non démarré

Le script vérifie si le port configuré correspond au profil:
```
[AVERTISSEMENT] Le port configuré (8080) ne correspond pas au profil (dev).
Pour corriger, utilisez l'option --fix.
```

Correction:
```
scripts\utils\validate_server_port.bat --fix
[OK] Port corrigé dans le fichier .env.
```

#### Cas 2: Serveur démarré avec un profil différent

Le script détecte l'incohérence:
```
[AVERTISSEMENT] Le serveur utilise un profil (prod) différent du profil actuel (dev).
Pour adapter l'environnement au serveur, utilisez l'option --fix.
```

Correction:
```
scripts\utils\validate_server_port.bat --fix
[OK] Environnement adapté au serveur en cours d'exécution.
```

#### Cas 3: Serveur démarré avec le bon profil mais mauvais port

Le script signale le problème:
```
[AVERTISSEMENT] Le serveur utilise le bon profil mais le mauvais port.
Pour résoudre ce problème, redémarrez le serveur.
```

Solution: Redémarrer le serveur pour qu'il utilise le bon port.

## Intégration dans les scripts de démarrage

Le script de validation est automatiquement appelé par les scripts de démarrage du serveur pour garantir une cohérence entre le profil et le port utilisé.

## Recommandations

1. **Utilisez toujours les menus officiels** (via `scripts.bat` ou `Scripts-Menu.ps1`) pour changer de profil et démarrer le serveur
2. **Ne modifiez pas manuellement** la variable `MATH_TRAINER_PORT` dans le fichier `.env`
3. **Exécutez le validateur** avant de démarrer le serveur en cas de doute
4. **Vérifiez les ports utilisés** en cas d'erreur de connexion au serveur 
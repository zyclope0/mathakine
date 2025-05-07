# Conventions de nommage des variables d'environnement

Ce document définit les conventions de nommage pour les variables d'environnement utilisées dans le projet Math Trainer.

## Préfixe

Toutes les variables d'environnement spécifiques au projet doivent utiliser le préfixe `MATH_TRAINER_` pour éviter les conflits avec d'autres variables d'environnement système ou d'autres applications.

## Format de nommage

Les variables d'environnement doivent respecter les règles suivantes :
- Utiliser uniquement des majuscules
- Utiliser le caractère underscore (`_`) comme séparateur de mots
- Être aussi descriptives que possible tout en restant concises
- Utiliser des noms en anglais

Exemple : `MATH_TRAINER_DEBUG`, `MATH_TRAINER_PORT`

## Catégories de variables

### Configuration du serveur
- `MATH_TRAINER_DEBUG` - Active/désactive le mode debug (true/false)
- `MATH_TRAINER_PORT` - Port du serveur web
- `MATH_TRAINER_LOG_LEVEL` - Niveau de logs (DEBUG, INFO, WARNING, ERROR)
- `MATH_TRAINER_TEST_MODE` - Active/désactive le mode test (true/false)
- `MATH_TRAINER_PROFILE` - Profil actif (dev, test, prod)

### Base de données
- `MATH_TRAINER_DB_PATH` - Chemin vers le fichier de base de données
- `MATH_TRAINER_DB_TYPE` - Type de base de données (sqlite, postgres, mysql)
- `MATH_TRAINER_DB_USER` - Utilisateur de la base de données
- `MATH_TRAINER_DB_PASSWORD` - Mot de passe de la base de données
- `MATH_TRAINER_DB_HOST` - Hôte de la base de données
- `MATH_TRAINER_DB_NAME` - Nom de la base de données

### Intégration IA
- `OPENAI_API_KEY` - Clé API pour OpenAI (exception à la règle du préfixe car standard pour OpenAI)
- `MATH_TRAINER_AI_MODEL` - Modèle IA à utiliser
- `MATH_TRAINER_AI_ENABLED` - Active/désactive l'utilisation de l'IA

### Sécurité
- `MATH_TRAINER_SECRET_KEY` - Clé secrète pour la signature des tokens
- `MATH_TRAINER_ALLOWED_HOSTS` - Liste des hôtes autorisés à accéder à l'application

## Valeurs par défaut

Chaque variable d'environnement doit avoir une valeur par défaut raisonnable définie dans le code. Ces valeurs par défaut doivent être documentées dans le fichier `.env.example`.

## Profils prédéfinis

Trois profils prédéfinis sont disponibles, chacun avec des valeurs par défaut spécifiques :

### Profil DEV
```
MATH_TRAINER_DEBUG=true
MATH_TRAINER_PORT=8081
MATH_TRAINER_LOG_LEVEL=DEBUG
MATH_TRAINER_TEST_MODE=true
MATH_TRAINER_PROFILE=dev
```

### Profil TEST
```
MATH_TRAINER_DEBUG=true
MATH_TRAINER_PORT=8082
MATH_TRAINER_LOG_LEVEL=INFO
MATH_TRAINER_TEST_MODE=true
MATH_TRAINER_PROFILE=test
```

### Profil PROD
```
MATH_TRAINER_DEBUG=false
MATH_TRAINER_PORT=8080
MATH_TRAINER_LOG_LEVEL=WARNING
MATH_TRAINER_TEST_MODE=false
MATH_TRAINER_PROFILE=prod
```

## Bonnes pratiques

1. **Ne jamais stocker de secrets dans le code** - Les variables sensibles comme les clés API ou les mots de passe doivent toujours être chargées depuis l'environnement.

2. **Utiliser la validation des variables** - Vérifier que les variables requises sont présentes et valides au démarrage de l'application.

3. **Documenter toutes les variables** - Chaque variable doit être documentée dans le fichier `.env.example`.

4. **Prévoir des valeurs par défaut sécurisées** - Les valeurs par défaut doivent être sécurisées par défaut, surtout en production.

5. **Éviter les dépendances circulaires** - Ne pas créer de dépendances circulaires entre les variables d'environnement. 
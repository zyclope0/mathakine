# Commandes d'Administration Mathakine

Ce document liste les commandes essentielles pour administrer l'application Mathakine après le refactoring de centralisation.

## Commandes de base

### Lancer le serveur
```bash
python enhanced_server.py
```

### Lancer le serveur avec l'interface CLI
```bash
python mathakine_cli.py run
```

### Initialiser/réinitialiser la base de données
```bash
python mathakine_cli.py init
```

## Tester les composants centralisés

### Tester les constantes
```bash
python -c "from app.core.constants import ExerciseTypes, DifficultyLevels; print(f'Types d\'exercices: {ExerciseTypes.ALL_TYPES}\\nNiveaux de difficulté: {DifficultyLevels.ALL_LEVELS}')"
```

### Tester les messages
```bash
python -c "from app.core.messages import SystemMessages; print(f'Message d\'erreur: {SystemMessages.ERROR_EXERCISE_NOT_FOUND}')"
```

### Tester les requêtes SQL
```bash
python -c "from app.db.queries import ExerciseQueries; print(f'Requête de création de table: {ExerciseQueries.CREATE_TABLE}')"
```

## Générer des exercices

### Générer un exercice standard
```bash
curl "http://localhost:8000/api/exercises/generate?exercise_type=addition&difficulty=padawan"
```

### Générer un exercice IA
```bash
curl "http://localhost:8000/api/exercises/generate?ai=true&exercise_type=multiplication&difficulty=chevalier"
```

## Vérifier la base de données

### Examiner la structure de la base de données
```bash
python -c "import psycopg2; from dotenv import load_dotenv; import os; load_dotenv(); conn = psycopg2.connect(os.environ.get('DATABASE_URL')); cursor = conn.cursor(); cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\' ORDER BY table_name;'); [print(row[0]) for row in cursor.fetchall()]; conn.close()"
```

### Lister les derniers exercices
```bash
python -c "import psycopg2; from dotenv import load_dotenv; import os; load_dotenv(); conn = psycopg2.connect(os.environ.get('DATABASE_URL')); cursor = conn.cursor(); cursor.execute('SELECT id, title, exercise_type, difficulty FROM exercises ORDER BY id DESC LIMIT 10;'); [print(row) for row in cursor.fetchall()]; conn.close()"
```

## Conseils pour le débogage

### Vérifier les importations
Si vous rencontrez des erreurs d'importation après avoir modifié les fichiers de constantes, essayez :
```bash
python -c "import sys; print(sys.path)"
```

### Afficher les constantes disponibles
```bash
python -c "from app.core.constants import *; import inspect; [print(f'{name}: {value}') for name, value in inspect.getmembers(sys.modules[__name__]) if not name.startswith('_') and not inspect.ismodule(value)]"
```

### Tester la normalisation
```bash
python -c "from enhanced_server import normalize_exercise_type, normalize_difficulty; print(f'Normalisation de \"addition\": {normalize_exercise_type(\"addition\")}\\nNormalisation de \"initie\": {normalize_difficulty(\"initie\")}')"
```

## Maintenance des constants

### Localiser toutes les mentions d'un type d'exercice spécifique
```bash
grep -r "addition" --include="*.py" .
```

### Vérifier toutes les références aux constantes centralisées
```bash
grep -r "from app.core.constants import" --include="*.py" .
```

### Lister tous les fichiers modifiés
```bash
git diff --name-only HEAD~1
```

## Conseils pour les déploiements

1. Assurez-vous que tous les fichiers de constantes sont bien inclus dans votre package de déploiement
2. Vérifiez que les chemins d'importation fonctionnent correctement dans l'environnement de déploiement
3. Après le déploiement, testez rapidement les fonctionnalités qui utilisent des constantes centralisées
4. Si vous modifiez des constantes existantes, vérifiez l'impact sur les données déjà en base 
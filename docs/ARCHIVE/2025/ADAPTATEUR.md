# Adaptateur pour Enhanced Server

Ce document décrit l'adaptateur `EnhancedServerAdapter` qui permet d'intégrer progressivement le nouveau système de transaction avec le serveur Starlette existant (`enhanced_server.py`).

## Introduction

Le projet Mathakine dispose de deux backends:
1. **app/main.py (FastAPI)** - API REST moderne avec SQLAlchemy pour les modèles et les requêtes
2. **enhanced_server.py (Starlette)** - Serveur avec interface web qui utilise des requêtes SQL directes

Pour unifier l'approche et faciliter la maintenance, nous avons mis en place:
- Un système de gestion de transaction unifié avec `TransactionManager`
- Un adaptateur de base de données (`DatabaseAdapter`) 
- Des services métier (`ExerciseService`, `UserService`, etc.)

L'adaptateur `EnhancedServerAdapter` permet de connecter ces composants à `enhanced_server.py` sans avoir à tout réécrire d'un coup.

## Fonctionnement de l'adaptateur

`EnhancedServerAdapter` est une classe qui convertit les opérations SQL directes d'`enhanced_server.py` en appels aux services métier avec le système de transaction. Son rôle est de:

1. Fournir des méthodes qui correspondent aux opérations courantes effectuées dans enhanced_server.py
2. Utiliser les services métier pour effectuer ces opérations
3. Gérer la conversion entre les objets SQLAlchemy et les dictionnaires attendus par enhanced_server.py
4. Gérer les sessions de base de données de manière cohérente

## Utilisation de l'adaptateur

Pour utiliser l'adaptateur dans `enhanced_server.py`, suivez ces étapes:

### 1. Importer l'adaptateur

```python
from app.services.enhanced_server_adapter import EnhancedServerAdapter
```

### 2. Remplacer les connexions directes à la base de données

**Avant**:
```python
conn = get_db_connection()
cursor = conn.cursor()
# ... code utilisant cursor ...
conn.close()
```

**Après**:
```python
db = EnhancedServerAdapter.get_db_session()
try:
    # ... code utilisant l'adaptateur ...
finally:
    EnhancedServerAdapter.close_db_session(db)
```

### 3. Remplacer les opérations CRUD

**Avant**:
```python
cursor.execute(ExerciseQueries.GET_BY_ID, (exercise_id,))
row = cursor.fetchone()
if not row:
    # gestion des erreurs
exercise = dict(zip(columns, row))
```

**Après**:
```python
exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise_id)
if not exercise:
    # gestion des erreurs
```

## Exemples d'utilisation

### Récupérer un exercice par ID

```python
# Obtenir une session
db = EnhancedServerAdapter.get_db_session()
try:
    # Récupérer l'exercice
    exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise_id)
    if not exercise:
        # Gérer le cas où l'exercice n'existe pas
        return JSONResponse({"error": "Exercice introuvable"}, status_code=404)
    
    # Utiliser l'exercice...
    
finally:
    # Fermer la session
    EnhancedServerAdapter.close_db_session(db)
```

### Lister des exercices avec filtrage

```python
db = EnhancedServerAdapter.get_db_session()
try:
    exercises = EnhancedServerAdapter.list_exercises(
        db,
        exercise_type=exercise_type,
        difficulty=difficulty,
        limit=None  # Gestion manuelle de la pagination
    )
    
    # Pagination manuelle
    total = len(exercises)
    paginated_exercises = exercises[skip:skip+limit] if skip < total else []
    
    return JSONResponse({
        "items": paginated_exercises,
        "total": total,
        "skip": skip,
        "limit": limit
    })
finally:
    EnhancedServerAdapter.close_db_session(db)
```

### Enregistrer une tentative

```python
db = EnhancedServerAdapter.get_db_session()
try:
    attempt_data = {
        "user_id": user_id,
        "exercise_id": exercise_id,
        "user_answer": selected_answer,
        "is_correct": is_correct,
        "time_spent": time_spent
    }
    
    attempt = EnhancedServerAdapter.record_attempt(db, attempt_data)
    if not attempt:
        # Gérer l'erreur
        return JSONResponse({"error": "Erreur lors de l'enregistrement"}, status_code=500)
finally:
    EnhancedServerAdapter.close_db_session(db)
```

## Avantages de l'approche

1. **Migration progressive** - Permet de migrer progressivement enhanced_server.py vers le nouveau système
2. **Code plus propre** - Supprime les requêtes SQL directes pour utiliser des services métier testables
3. **Meilleure gestion des erreurs** - Utilisation du système de transactions unifié pour garantir la cohérence
4. **Facilitation de la maintenance** - Centralisation de la logique métier dans les services
5. **Performances optimisées** - Utilisation du système de session SQLAlchemy avec ses optimisations internes

## Points d'attention

1. **Compatibilité descendante** - L'adaptateur doit convertir correctement entre le format des services et celui attendu par enhanced_server.py
2. **Gestion des sessions** - Toujours fermer les sessions avec un bloc try/finally
3. **Transactions** - Les services utilisent déjà le TransactionManager, pas besoin de gérer manuellement les commit/rollback
4. **Migration complète** - À terme, l'objectif est que toutes les requêtes SQL directes soient remplacées par des appels aux services

## Fonctions disponibles

L'adaptateur propose de nombreuses méthodes pour couvrir les besoins courants d'enhanced_server.py:

### Gestion des sessions
- `get_db_session()` - Obtient une nouvelle session SQLAlchemy
- `close_db_session(db)` - Ferme une session

### Opérations sur les exercices
- `get_exercise_by_id(db, exercise_id)` - Récupère un exercice par son ID
- `list_exercises(db, exercise_type, difficulty, limit)` - Liste les exercices avec filtrage
- `create_exercise(db, exercise_data)` - Crée un nouvel exercice
- `update_exercise(db, exercise_id, exercise_data)` - Met à jour un exercice existant
- `archive_exercise(db, exercise_id)` - Archive un exercice (is_archived=true)

### Opérations sur les tentatives
- `record_attempt(db, attempt_data)` - Enregistre une tentative de résolution d'exercice

### Opérations sur les utilisateurs 
- `get_user_stats(db, user_id)` - Récupère les statistiques d'un utilisateur

### Opérations génériques
- `execute_raw_query(db, query, params)` - Pour les cas exceptionnels nécessitant une requête SQL directe 
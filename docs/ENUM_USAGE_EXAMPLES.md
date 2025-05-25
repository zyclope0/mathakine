# Exemples d'utilisation des fonctions d'aide pour les énumérations

Ce document illustre comment utiliser les fonctions d'aide du module `app.core.enum_helpers` pour manipuler les énumérations de manière sécurisée dans Mathakine.

## Importation du module

```python
from app.core.enum_helpers import (
    get_enum_value,
    get_enum_name,
    validate_enum_value,
    enum_to_dict,
    is_valid_enum_value,
    get_enum_by_name,
    enum_values_list,
    enum_names_list
)
from app.models.user import UserRole
from app.models.exercise import DifficultyLevel, ExerciseType
from app.models.logic_challenge import LogicChallengeType, AgeGroup
```

## Récupération sécurisée des valeurs d'énumération

### Avant (problématique):

```python
# Risque de chaînes comme UserRole.PADAWAN.value
user_role = UserRole.PADAWAN.value
```

### Après (sécurisé):

```python
# Toujours une valeur simple, même si appelé sur UserRole.PADAWAN.value
user_role = get_enum_value(UserRole.PADAWAN)
```

## Validation des valeurs d'énumération

### Avant:

```python
# Pas de validation, erreurs silencieuses possibles
def create_exercise(exercise_type: str, difficulty: str):
    exercise = Exercise(
        exercise_type=exercise_type,
        difficulty=difficulty,
        # Autres attributs...
    )
    return exercise
```

### Après:

```python
# Validation avec message d'erreur explicite
def create_exercise(exercise_type: str, difficulty: str):
    # Valide les entrées
    valid_type = validate_enum_value(ExerciseType, exercise_type)
    valid_difficulty = validate_enum_value(DifficultyLevel, difficulty)
    
    exercise = Exercise(
        exercise_type=get_enum_value(valid_type),
        difficulty=get_enum_value(valid_difficulty),
        # Autres attributs...
    )
    return exercise
```

## Vérification de valeurs sans erreur

```python
# Vérifier si une valeur est valide sans déclencher d'erreur
if is_valid_enum_value(UserRole, "invalid_role"):
    # Ce code ne sera pas exécuté
    pass
else:
    # Gérer le cas invalide
    print("Rôle invalide")
```

## Conversion en dictionnaire pour les API

```python
# Envoyer toutes les difficultés possibles à l'interface utilisateur
@router.get("/difficulty-levels")
def get_difficulty_levels():
    return {
        "levels": enum_to_dict(DifficultyLevel)
    }
    # Retourne: {"levels": {"INITIE": "initie", "PADAWAN": "padawan", ...}}
```

## Obtenir un élément d'énumération par son nom

```python
# Recherche par nom avec gestion des cas où le nom n'existe pas
role_name = "PADAWAN"
role = get_enum_by_name(UserRole, role_name)

if role:
    print(f"Rôle trouvé: {get_enum_value(role)}")
else:
    print(f"Rôle '{role_name}' non trouvé")
```

## Récupérer les listes de valeurs ou de noms

```python
# Obtenir la liste des valeurs possibles pour les types d'exercice
exercise_types = enum_values_list(ExerciseType)
# Retourne: ["addition", "soustraction", "multiplication", ...]

# Obtenir la liste des noms pour les groupes d'âge
age_group_names = enum_names_list(AgeGroup)
# Retourne: ["ENFANT", "ADOLESCENT", "ADULTE", ...]
```

## Exemples de cas réels

### Création d'un nouvel utilisateur

```python
from app.models.user import User, UserRole
from app.core.enum_helpers import get_enum_value, validate_enum_value

def create_user(username: str, email: str, password: str, role_str: str = "padawan"):
    # Valider le rôle
    try:
        role = validate_enum_value(UserRole, role_str)
    except ValueError:
        # Utiliser PADAWAN par défaut si invalide
        role = UserRole.PADAWAN
    
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=get_enum_value(role)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

### Filtrage d'exercices par type et difficulté

```python
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.core.enum_helpers import get_enum_value, is_valid_enum_value

def filter_exercises(exercise_type=None, difficulty=None):
    query = db.query(Exercise)
    
    if exercise_type and is_valid_enum_value(ExerciseType, exercise_type):
        query = query.filter(Exercise.exercise_type == exercise_type)
    
    if difficulty and is_valid_enum_value(DifficultyLevel, difficulty):
        query = query.filter(Exercise.difficulty == difficulty)
    
    return query.all()
```

### Endpoint de recommandation avec filtre par difficulté

```python
from app.models.exercise import DifficultyLevel
from app.core.enum_helpers import validate_enum_value, get_enum_value

@router.get("/recommendations")
def get_recommendations(difficulty: str = None):
    if difficulty:
        try:
            difficulty_enum = validate_enum_value(DifficultyLevel, difficulty)
            return {"recommendations": get_exercises_by_difficulty(get_enum_value(difficulty_enum))}
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Difficulté invalide: {difficulty}"
            )
    else:
        return {"recommendations": get_all_recommendations()}
```

## Bonnes pratiques

1. **Toujours utiliser `get_enum_value()`** plutôt que d'accéder directement à `.value`
2. **Valider les entrées** avec `validate_enum_value()` pour les données provenant de l'extérieur
3. **Vérifier la validité sans erreur** avec `is_valid_enum_value()` pour le filtrage ou les conditions
4. **Utiliser les listes et dictionnaires** dans les endpoints pour exposer les options disponibles
5. **Fournir des messages d'erreur clairs** pour aider au débogage 
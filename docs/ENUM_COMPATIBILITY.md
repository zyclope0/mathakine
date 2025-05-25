# Guide de gestion des énumérations PostgreSQL

## Problématique

PostgreSQL utilise des types d'énumération stricts qui n'acceptent que les valeurs définies lors de la création du type. Cela nécessite une gestion rigoureuse des valeurs d'énumération dans l'application pour garantir leur compatibilité avec la base de données.

## Solution : Système de mapping d'énumération

Le projet Mathakine implémente un système de mapping qui assure la conversion correcte des valeurs d'énumération Python vers les valeurs attendues par PostgreSQL.

### Module de mapping (`app/utils/db_helpers.py`)

Le module fournit les fonctions suivantes :

- `get_enum_value(enum_class, value) -> str` : Convertit une valeur d'énumération Python en valeur PostgreSQL.
- `adapt_enum_for_db(enum_name: str, value: str) -> str` : Convertit une valeur textuelle en valeur PostgreSQL.
- `get_all_enum_values() -> Dict[str, Any]` : Fournit toutes les valeurs d'énumération adaptées.

### Utilisation dans le code

#### 1. Création d'objets avec énumérations

```python
from app.models.user import User, UserRole
from app.utils.db_helpers import get_enum_value

def create_user(db: Session, username: str, role_enum: UserRole):
    # Convertir la valeur de l'énumération pour PostgreSQL
    adapted_role = get_enum_value(UserRole, role_enum)
    
    # Créer l'utilisateur avec la valeur adaptée
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password="password_hash",
        role=adapted_role
    )
    
    db.add(user)
    db.commit()
    return user
```

#### 2. Recherche avec filtres sur énumérations

```python
from app.models.exercise import Exercise, ExerciseType
from app.utils.db_helpers import get_enum_value

def get_exercises_by_type(db: Session, exercise_type: ExerciseType):
    # Convertir la valeur de l'énumération pour PostgreSQL
    adapted_type = get_enum_value(ExerciseType, exercise_type)
    
    # Utiliser la valeur adaptée dans la requête
    exercises = db.query(Exercise).filter(Exercise.exercise_type == adapted_type).all()
    return exercises
```

#### 3. Utilisation dans les tests

```python
def test_create_logic_challenge(db_session, db_enum_values):
    """Test de création d'un défi logique avec valeurs adaptées."""
    # Utiliser les valeurs adaptées depuis la fixture db_enum_values
    challenge = LogicChallenge(
        title="Test Challenge",
        challenge_type=db_enum_values["challenge_types"]["sequence"],
        age_group=db_enum_values["age_groups"]["age_9_12"],
        description="Test challenge",
        correct_answer="42",
        solution_explanation="Solution"
    )
    
    db_session.add(challenge)
    db_session.commit()
    
    # Vérifier que le défi a été créé avec les bonnes valeurs
    retrieved = db_session.query(LogicChallenge).filter_by(id=challenge.id).first()
    assert retrieved.challenge_type == db_enum_values["challenge_types"]["sequence"]
    assert retrieved.age_group == db_enum_values["age_groups"]["age_9_12"]
```

## Fixtures de test

Pour faciliter les tests, des fixtures sont disponibles dans `tests/conftest.py` :

- `db_enum_values` : Fournit toutes les valeurs d'énumération adaptées.
- `logic_challenge_data` : Fournit des données pour les défis logiques avec valeurs adaptées.
- `user_data` : Fournit des données pour les utilisateurs avec valeurs adaptées.

Exemple d'utilisation :

```python
def test_user_creation(db_session, user_data):
    """Test de création d'utilisateur avec rôle adapté."""
    # Les données sont déjà adaptées pour PostgreSQL
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    
    # Test avec valeurs PostgreSQL correctes
    retrieved = db_session.query(User).filter_by(username=user_data["username"]).first()
    assert retrieved is not None
    assert retrieved.role == user_data["role"]
```

## Correction des données existantes

Pour corriger les valeurs d'énumération dans une base de données existante, un script utilitaire est disponible :

```bash
# Mode simulation (affiche les modifications sans les appliquer)
python scripts/fix_enum_values.py

# Application des corrections
python scripts/fix_enum_values.py --apply

# Utilisation d'une URL de base de données spécifique
python scripts/fix_enum_values.py --apply --database-url postgresql://user:password@host/dbname
```

## Règles de bonnes pratiques

1. **Toujours utiliser `get_enum_value`** pour convertir les valeurs d'énumération avant de les stocker en base de données.
2. **Utiliser les fixtures de test** pour obtenir des valeurs d'énumération adaptées dans les tests.
3. **Ne pas hardcoder les valeurs d'énumération** dans les requêtes SQL ou les filtres ORM.
4. **Ne pas supposer** que les valeurs en base de données correspondent exactement aux valeurs des énumérations Python.

## Mappings d'énumération

Les mappings entre les valeurs Python et PostgreSQL sont définis dans `app/utils/db_helpers.py` :

```python
ENUM_MAPPING = {
    # UserRole
    ("UserRole", "padawan"): "padawan",
    ("UserRole", "maitre"): "maitre",
    # etc.
    
    # LogicChallengeType
    ("LogicChallengeType", "sequence"): "SEQUENCE",
    ("LogicChallengeType", "puzzle"): "PUZZLE",
    # etc.
}
```

Pour ajouter de nouveaux mappings :

1. Identifier les valeurs exactes utilisées dans PostgreSQL (`SELECT enum_range(NULL::typenom)`)
2. Ajouter les mappings correspondants dans `ENUM_MAPPING`
3. Exécuter les tests pour vérifier la compatibilité

## Dépannage

### Erreurs courantes d'énumération

Symptôme : `invalid input value for enum type_enum: "value"`

Solution :
1. Vérifier que la valeur est bien dans le mapping d'énumération
2. Utiliser `get_enum_value` pour convertir la valeur
3. Vérifier les valeurs exactes acceptées par PostgreSQL avec :
   ```sql
   SELECT unnest(enum_range(NULL::logicchallengetype));
   ```

### Erreurs de référence d'énumération malformée

Symptôme : `AttributeError: type object 'UserRole' has no attribute 'PADAWAN_value'`

Solution :
1. Corriger les références d'énumération dans le code
2. Utiliser `UserRole.PADAWAN` au lieu de `UserRole.PADAWAN.value`
3. Laisser le système de mapping se charger de la conversion 
# Migration et compatibilité dans Mathakine

Ce document décrit les problèmes de compatibilité identifiés dans le projet Mathakine et les solutions mises en œuvre pour les résoudre.

## 1. Incompatibilité PostgreSQL vs SQLite

### Problème identifié

Dans le cadre de la migration complète vers PostgreSQL (abandonnant SQLite), nous avons identifié un problème majeur lié à l'utilisation des énumérations:

- **PostgreSQL** stocke les énumérations comme des types spécifiques et nécessite que les valeurs soient passées avec `.value`
- **SQLite** est plus permissif et accepte les énumérations directement, sans l'usage de `.value`

Ce problème a affecté de nombreux fichiers de test et a causé des échecs lors de l'exécution des tests avec PostgreSQL.

### Solution implémentée

1. **Script automatisé**: Création de `scripts/fix_enum_compatibility.py` qui:
   - Analyse tous les fichiers Python du projet
   - Détecte les occurrences d'énumérations sans `.value`
   - Corrige automatiquement le code
   - Génère un rapport détaillé

2. **Résultats**:
   - 25 fichiers analysés et corrigés
   - 463 occurrences d'énumérations problématiques corrigées
   - Types corrigés: UserRole, ExerciseType, DifficultyLevel, LogicChallengeType, AgeGroup

3. **Principaux fichiers impactés**:
   - `tests/integration/test_complete_exercise_workflow.py` (65 corrections)
   - `tests/unit/test_recommendation_service.py` (52 corrections)
   - `tests/unit/test_logic_challenge_service.py` (50 corrections)
   - `tests/unit/test_exercise_service.py` (36 corrections)

### Utilisation correcte des énumérations

Toujours utiliser `.value` avec les énumérations pour assurer la compatibilité avec PostgreSQL:

```python
# Incorrect (fonctionnera avec SQLite mais pas avec PostgreSQL)
user = User(role=UserRole.PADAWAN)

# Correct (compatible avec PostgreSQL et SQLite)
user = User(role=UserRole.PADAWAN.value)
```

## 2. Migration Pydantic v1 → v2

### Problèmes identifiés

Pydantic v2 a introduit des changements importants qui affectent notre code:

1. **Méthodes dépréciées**:
   - `.dict()` → `.model_dump()`
   - `.json()` → `.model_dump_json()`
   - `.parse_obj()` → `.model_validate()`
   - `.parse_raw()` → `.model_validate_json()`

2. **Imports changés**:
   - `pydantic.validator` → `pydantic.field_validator`
   - `pydantic.root_validator` → `pydantic.model_validator`

3. **Comportement modifié**:
   - Validation plus stricte
   - Performances améliorées mais comportement parfois différent

### Solution implémentée

1. **Script automatisé**: Création de `scripts/fix_pydantic_v2_compatibility.py` qui:
   - Analyse le code pour détecter les méthodes dépréciées
   - Propose des corrections automatiques
   - Fournit un rapport détaillé des changements nécessaires

2. **Documentation**: Ce document sert de guide pour les développeurs sur les changements à effectuer.

### Guide de migration

#### Remplacement des méthodes dépréciées

```python
# Pydantic v1 (déprécié)
user_dict = user.dict()
user_json = user.json()
parsed_user = UserModel.parse_obj(data)
parsed_user_json = UserModel.parse_raw(json_str)

# Pydantic v2 (nouveau)
user_dict = user.model_dump()
user_json = user.model_dump_json()
parsed_user = UserModel.model_validate(data)
parsed_user_json = UserModel.model_validate_json(json_str)
```

#### Mise à jour des imports pour les validateurs

```python
# Pydantic v1 (déprécié)
from pydantic import validator, root_validator

class User(BaseModel):
    @validator('email')
    def validate_email(cls, v):
        return v
        
    @root_validator
    def validate_password(cls, values):
        return values

# Pydantic v2 (nouveau)
from pydantic import field_validator, model_validator

class User(BaseModel):
    @field_validator('email')
    def validate_email(cls, v):
        return v
        
    @model_validator(mode='before')
    def validate_password(cls, values):
        return values
```

## 3. Conseils pour assurer la compatibilité

### Tests

1. **Exécuter les tests avec les deux moteurs de base de données**:
   ```bash
   # SQLite (développement)
   python scripts/toggle_database.py --sqlite
   python -m pytest tests/
   
   # PostgreSQL (production)
   python scripts/toggle_database.py --postgres
   python -m pytest tests/
   ```

2. **Utiliser les scripts de validation**:
   ```bash
   # Vérifier les problèmes d'énumération
   python scripts/fix_enum_compatibility.py --check-only
   
   # Vérifier les problèmes Pydantic
   python scripts/fix_pydantic_v2_compatibility.py --check-only
   ```

### Développement

- **Énumérations**: Toujours utiliser `.value` lors de l'assignation à des champs de modèle
- **Pydantic**: Utiliser les nouvelles méthodes (model_dump, model_validate, etc.)
- **Tests**: Vérifier la compatibilité avec PostgreSQL pour tous les nouveaux tests

## 4. Prochaines étapes

1. **Automatisation**:
   - Intégrer les vérifications dans le processus CI/CD
   - Ajouter des hooks pre-commit pour détecter les problèmes

2. **Documentation**:
   - Mettre à jour les guides existants
   - Créer des exemples et des templates pour les nouveaux développeurs

3. **Formation**:
   - Session de formation pour l'équipe sur les bonnes pratiques
   - Revues de code ciblées sur ces aspects 
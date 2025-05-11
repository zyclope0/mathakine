# Migration vers Pydantic v2

Ce document détaille les modifications apportées au projet pour migrer de Pydantic v1 vers Pydantic v2.

## Contexte

Pydantic a introduit une version majeure (v2) qui comprend plusieurs changements d'API incompatibles avec la version v1. Les avertissements de dépréciation apparaissaient dans les tests, et nous avons mis à jour tous les modèles pour utiliser la nouvelle API et éliminer ces avertissements.

## Principaux changements

### 1. Remplacement de `@validator` par `@field_validator`

Dans Pydantic v2, le décorateur `@validator` est déprécié au profit de `@field_validator`. De plus, les validateurs doivent maintenant être des méthodes de classe.

**Avant (v1) :**
```python
from pydantic import BaseModel, validator

class User(BaseModel):
    username: str
    
    @validator('username')
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères")
        return v
```

**Après (v2) :**
```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    username: str
    
    @field_validator('username')
    @classmethod
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères")
        return v
```

### 2. Changement de l'accès aux données dans les validateurs

Dans Pydantic v1, les validateurs recevaient directement les valeurs via l'argument `values`. Dans v2, cet argument est remplacé par un objet `info` contenant une propriété `data`.

**Avant (v1) :**
```python
@validator('choices')
def validate_choices(cls, v, values):
    if 'correct_answer' in values and values['correct_answer'] not in v:
        raise ValueError("La réponse correcte doit être présente dans les choix")
    return v
```

**Après (v2) :**
```python
@field_validator('choices')
@classmethod
def validate_choices(cls, v, info):
    values = info.data
    if 'correct_answer' in values and values['correct_answer'] not in v:
        raise ValueError("La réponse correcte doit être présente dans les choix")
    return v
```

### 3. Remplacement de `Config` par `model_config`

Dans v2, la classe interne `Config` est remplacée par une variable de classe `model_config` initialisée avec `ConfigDict`.

**Avant (v1) :**
```python
class User(BaseModel):
    # champs...
    
    class Config:
        orm_mode = True
```

**Après (v2) :**
```python
from pydantic import ConfigDict

class User(BaseModel):
    # champs...
    
    model_config = ConfigDict(from_attributes=True)
```

Notez également le renommage de `orm_mode` vers `from_attributes`.

## Fichiers modifiés

Les fichiers suivants ont été mis à jour pour se conformer à Pydantic v2 :

1. `app/schemas/user.py` - Modèles d'utilisateurs et authentification
2. `app/schemas/exercise.py` - Modèles pour les exercices mathématiques
3. `app/schemas/logic_challenge.py` - Modèles pour les défis logiques
4. `app/schemas/attempt.py` - Modèles pour les tentatives d'exercices
5. `app/schemas/progress.py` - Modèles pour le suivi de la progression
6. `app/schemas/setting.py` - Modèles pour les paramètres d'application

## Avantages de la migration

1. **Performances améliorées** : Pydantic v2 est significativement plus rapide que v1.
2. **Meilleure intégration avec les outils modernes** : Compatibilité améliorée avec FastAPI et autres bibliothèques.
3. **Types plus précis** : Meilleur support pour la vérification de type et l'auto-complétion.
4. **Élimination des avertissements** : Plus d'avertissements de dépréciation lors de l'exécution des tests.

## Ressources supplémentaires

- [Guide officiel de migration vers Pydantic v2](https://docs.pydantic.dev/latest/migration/)
- [Documentation de field_validator](https://docs.pydantic.dev/latest/api/functional_validators/#pydantic.functional_validators.field_validator)
- [Documentation de ConfigDict](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict)

## Date de migration

Cette migration a été effectuée le 8 septembre 2024. 
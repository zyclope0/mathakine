# Différences entre PostgreSQL et SQLite : Guide pour les tests

## Introduction

Ce document explique les différences importantes entre PostgreSQL et SQLite, particulièrement concernant la gestion des types enum. Ces différences ont un impact significatif sur les tests automatisés et la portabilité du code entre les environnements de développement et de production.

## Types enum dans PostgreSQL vs SQLite

### SQLite: Souplesse des types

SQLite utilise un système de typage dynamique et est très permissif concernant les types de données:

- Les enum sont traités comme de simples chaînes de caractères
- Aucune vérification stricte des valeurs n'est effectuée
- SQLite acceptera n'importe quelle chaîne de caractères pour un champ sans vérifier sa validité par rapport à l'enum

### PostgreSQL: Typage strict et enums comme types distincts

PostgreSQL implémente les enum comme des types de données distincts:

- Chaque enum est un type défini dans le schéma de la base de données
- Les valeurs doivent correspondre exactement à celles définies dans le type
- PostgreSQL rejette toute valeur qui ne fait pas partie de l'enum avec une erreur `invalid input value for enum`

## Problèmes courants et solutions

### Problème 1: Utilisation des valeurs d'enum vs noms d'enum

#### Problème
```python
# Définition de l'enum dans app/models/logic_challenge.py
class LogicChallengeType(enum.Enum):
    SEQUENCE = "sequence"  # "SEQUENCE" est le nom, "sequence" est la valeur

# Dans le code de test (fonctionnera avec SQLite mais échouera avec PostgreSQL)
challenge = LogicChallenge(
    challenge_type="sequence"  # ❌ Échoue avec PostgreSQL: "invalid input value for enum"
)
```

#### Solution
Pour PostgreSQL, utiliser la valeur exacte telle que stockée dans la base de données:
```python
# Version compatible avec PostgreSQL
challenge = LogicChallenge(
    challenge_type="SEQUENCE"  # ✅ Fonctionne car correspond au nom de l'enum
)
```

### Problème 2: Incohérences dans le nommage des enums

#### Problème
Les noms et valeurs des enums peuvent parfois porter à confusion:

```python
class AgeGroup(enum.Enum):
    AGE_9_12 = "9-12"      # Le nom est AGE_9_12, la valeur est "9-12"
    AGE_13_PLUS = "13+"    # Le nom est AGE_13_PLUS, la valeur est "13+"

# Dans PostgreSQL, l'enum peut être défini différemment
# Par exemple: GROUP_10_12 au lieu de AGE_9_12
```

#### Solution
Vérifier directement les valeurs acceptées dans PostgreSQL:

```python
# Exécution d'une requête directe pour voir les valeurs d'enum acceptées
import psycopg2
conn = psycopg2.connect(CONNECTION_STRING)
cursor = conn.cursor()
cursor.execute('SELECT unnest(enum_range(NULL::agegroup))::text')
values = [row[0] for row in cursor.fetchall()]
# values = ['GROUP_10_12', 'GROUP_13_15', 'ALL_AGES']
```

Puis utiliser ces valeurs exactes dans les tests:
```python
challenge = LogicChallenge(
    age_group="GROUP_10_12"  # ✅ Valeur exacte acceptée par PostgreSQL
)
```

### Problème 3: Champs obligatoires non évidents

PostgreSQL est plus strict sur les contraintes `NOT NULL`. Un champ requis dans la définition du modèle mais qui semble optionnel pourrait provoquer des erreurs.

#### Solution
Toujours fournir tous les champs obligatoires, même dans les tests:

```python
# Version complète avec tous les champs obligatoires
challenge = LogicChallenge(
    title="Test Challenge",
    description="Description",
    challenge_type="SEQUENCE",
    age_group="GROUP_10_12",
    correct_answer="42",
    solution_explanation="Explication obligatoire",  # ✅ Champ obligatoire
    ...
)
```

## Bonnes pratiques pour les tests

### 1. Détection du moteur de base de données

Créez une fonction d'aide pour détecter le moteur de base de données et adapter les valeurs d'enum:

```python
def get_db_engine(db_session):
    """Détecte le moteur de base de données (SQLite ou PostgreSQL)."""
    engine = db_session.bind.engine.name
    return engine

def get_enum_value(enum_class, enum_member, db_session):
    """Retourne la valeur appropriée selon le moteur de base de données."""
    engine = get_db_engine(db_session)
    
    if engine == 'postgresql':
        # Utiliser le nom de l'enum pour PostgreSQL
        return enum_member.name
    else:
        # Utiliser la valeur de l'enum pour SQLite
        return enum_member.value
```

### 2. Tests conditionnels

Adaptez vos tests en fonction du moteur de base de données:

```python
import pytest

def test_create_challenge(db_session):
    engine = get_db_engine(db_session)
    
    # Skip sur PostgreSQL si nécessaire
    if engine == 'postgresql' and not has_postgresql_enums():
        pytest.skip("Ce test nécessite la configuration des enums PostgreSQL")
    
    challenge_type = "SEQUENCE" if engine == 'postgresql' else "sequence"
    age_group = "GROUP_10_12" if engine == 'postgresql' else "9-12"
    
    challenge = LogicChallenge(
        challenge_type=challenge_type,
        age_group=age_group,
        ...
    )
```

### 3. Fixtures spécifiques au moteur

Créez des fixtures adaptées à chaque moteur:

```python
@pytest.fixture
def challenge_data(db_session):
    """Renvoie les données de test pour un défi logique adaptées au moteur DB."""
    engine = get_db_engine(db_session)
    
    if engine == 'postgresql':
        return {
            "challenge_type": "SEQUENCE",
            "age_group": "GROUP_10_12",
            "role": "maitre"
        }
    else:
        return {
            "challenge_type": "sequence",
            "age_group": "9-12",
            "role": "teacher"
        }
```

## Documenter les valeurs d'enum

Créez un document de référence listant toutes les valeurs d'enum pour les deux bases de données:

| Enum | Nom Python | Valeur Python | PostgreSQL | SQLite |
|------|------------|--------------|------------|--------|
| LogicChallengeType | SEQUENCE | "sequence" | "SEQUENCE" | "sequence" |
| LogicChallengeType | PATTERN | "pattern" | "PATTERN" | "pattern" |
| LogicChallengeType | PUZZLE | "puzzle" | "PUZZLE" | "puzzle" |
| AgeGroup | AGE_9_12 | "9-12" | "GROUP_10_12" | "9-12" |
| AgeGroup | AGE_13_PLUS | "13+" | "GROUP_13_15" | "13+" |
| UserRole | ADMIN | "admin" | "admin" | "admin" |
| UserRole | TEACHER | "teacher" | "maitre" | "teacher" |
| UserRole | STUDENT | "student" | "padawan" | "student" |

## Solution avancée: Utilisation de mocks pour les tests unitaires

### Pourquoi utiliser des mocks?

L'adaptation des valeurs d'enum en fonction du moteur de base de données est une approche viable, mais elle présente certaines limitations:

1. Complexité accrue des tests avec des conditions spécifiques au moteur
2. Potentiel d'erreurs lors de la maintenance des tests
3. Temps d'exécution plus long dû à la dépendance à une base de données réelle
4. Difficulté à tester certains scénarios limites

Pour ces raisons, une approche basée sur les mocks peut être préférable pour les tests unitaires.

### Principe des mocks pour les tests unitaires

L'idée centrale est de remplacer les interactions réelles avec la base de données par des simulations contrôlées:

```python
from unittest.mock import patch, MagicMock

@patch('sqlalchemy.orm.Session')
def test_get_user(mock_session):
    # Configurer le mock
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_filter = MagicMock()
    mock_query.filter.return_value = mock_filter
    
    # Simuler un utilisateur sans se soucier des types enum
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "test_user"
    mock_user.role = "padawan"  # Valeur directe sans risque d'incompatibilité
    mock_filter.first.return_value = mock_user
    
    # Exécuter la fonction à tester
    result = get_user(mock_db, 1)
    
    # Vérifications
    assert result.id == 1
    assert result.username == "test_user"
    assert result.role == "padawan"
```

### Avantages de l'approche par mocks

1. **Indépendance totale du moteur de base de données**:
   - Les tests s'exécutent de manière identique sur tous les environnements
   - Pas de problèmes liés aux différences de type entre SQLite et PostgreSQL

2. **Meilleure isolation des tests**:
   - Chaque test se concentre uniquement sur la logique qu'il doit vérifier
   - Élimination des effets de bord et des dépendances

3. **Performance améliorée**:
   - Exécution beaucoup plus rapide sans accès à une base de données réelle
   - Pas de setup/teardown coûteux

4. **Flexibilité accrue**:
   - Facilité à simuler des erreurs, cas limites et scénarios spécifiques
   - Contrôle total sur les données et comportements simulés

### Exemple complet: Test du service utilisateur

```python
from unittest.mock import patch, MagicMock
import pytest
from app.services.user_service import get_user_stats

@patch('app.services.user_service.get_user')
@patch('sqlalchemy.orm.Session')
def test_get_user_stats_with_specific_exercise_type(mock_session, mock_get_user):
    # Configurer les mocks
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 1
    mock_get_user.return_value = mock_user
    
    # Simuler des tentatives en base de données
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_filter = MagicMock()
    mock_query.filter.return_value = mock_filter
    
    # Simuler le résultat de la requête
    mock_attempts = [
        MagicMock(exercise=MagicMock(exercise_type="addition", difficulty="padawan")),
        MagicMock(exercise=MagicMock(exercise_type="addition", difficulty="padawan")),
        MagicMock(exercise=MagicMock(exercise_type="subtraction", difficulty="initié"))
    ]
    mock_filter.all.return_value = mock_attempts
    
    # Exécuter la fonction à tester avec un filtre par type d'exercice
    stats = get_user_stats(mock_db, 1, exercise_type="addition")
    
    # Vérifications
    assert stats["total_attempts"] == 2
    assert "addition" in stats["by_type"]
    assert "subtraction" not in stats["by_type"]
    
    # Vérifier que les méthodes ont été appelées correctement
    mock_get_user.assert_called_once_with(mock_db, 1)
    mock_db.query.assert_called_once()
```

### Quand utiliser les mocks vs adaptations d'enum

| Approche | Recommandée pour | Limitations |
|----------|------------------|-------------|
| **Mocks** | Tests unitaires, tests de logique pure, tests de fonction individuelles | Ne teste pas l'intégration réelle avec la base de données |
| **Adaptation d'enum** | Tests d'intégration, tests de requêtes SQL réelles, tests de migration | Dépendant de l'environnement, plus complexe à maintenir |

### Bonnes pratiques pour les tests avec mocks

1. **Structure claire**: Suivez le modèle AAA (Arrange-Act-Assert)
2. **Isolation précise**: Ne mockez que ce qui est nécessaire
3. **Assertions complètes**: Vérifiez les valeurs de retour et les appels de méthodes
4. **Documentation**: Expliquez clairement le but et le fonctionnement du test
5. **Maintenabilité**: Créez des fonctions d'aide pour les configurations de mock communes

## Conclusion

La gestion des différences entre SQLite et PostgreSQL, particulièrement pour les types enum, est essentielle pour garantir que les tests fonctionnent correctement dans tous les environnements. 

Pour les tests unitaires, l'approche par mocks offre une solution élégante et efficace qui évite complètement les problèmes de compatibilité. Pour les tests d'intégration où l'interaction avec une base de données réelle est nécessaire, les stratégies d'adaptation d'enum permettent de gérer les différences de type.

En combinant ces deux approches de manière appropriée, vous pouvez créer une suite de tests robuste qui fonctionne de manière fiable dans tous les environnements de développement et de production. 
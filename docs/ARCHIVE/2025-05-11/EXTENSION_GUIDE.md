# Guide d'Extension Mathakine

Ce guide explique comment étendre l'application Mathakine en ajoutant de nouveaux types d'exercices, niveaux de difficulté ou autres fonctionnalités, en utilisant les constantes centralisées.

## 1. Ajouter un nouveau type d'exercice

### Étape 1 : Mettre à jour `app/core/constants.py`

```python
class ExerciseTypes:
    # Types existants
    ADDITION = "addition"
    SUBTRACTION = "soustraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"
    FRACTIONS = "fractions"
    
    # Nouveau type
    EQUATIONS = "equations"
    
    # Mettre à jour la liste ALL_TYPES
    ALL_TYPES = [ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION, FRACTIONS, EQUATIONS]
    
    # Ajouter des alias pour la normalisation
    TYPE_ALIASES = {
        # Alias existants...
        
        # Nouveaux alias
        EQUATIONS: ["equations", "equation", "equa", "eq"]
    }
```

### Étape 2 : Mettre à jour `DISPLAY_NAMES` dans `app/core/constants.py`

```python
DISPLAY_NAMES = {
    # Noms existants...
    
    # Nouveau nom d'affichage
    ExerciseTypes.EQUATIONS: "Équations",
}
```

### Étape 3 : Ajouter les limites dans `DIFFICULTY_LIMITS`

```python
DIFFICULTY_LIMITS = {
    DifficultyLevels.INITIE: {
        # Limites existantes...
        
        # Nouvelles limites
        ExerciseTypes.EQUATIONS: {
            "min_coefficient": 1,
            "max_coefficient": 5,
            "include_negatives": False
        }
    },
    
    DifficultyLevels.PADAWAN: {
        # Limites existantes...
        
        # Nouvelles limites
        ExerciseTypes.EQUATIONS: {
            "min_coefficient": 1,
            "max_coefficient": 10,
            "include_negatives": True
        }
    },
    
    # Répéter pour les autres niveaux...
}
```

### Étape 4 : Ajouter des messages dans `app/core/messages.py`

```python
class ExerciseMessages:
    # Messages existants...
    
    # Nouveaux messages
    TITLE_EQUATIONS = "Résoudre l'équation"
    QUESTION_EQUATIONS = "Quelle est la valeur de x dans l'équation {equation}?"
```

### Étape 5 : Implémenter la génération d'exercices dans `enhanced_server.py`

```python
def generate_simple_exercise(exercise_type, difficulty):
    """Génère un exercice simple de manière algorithmique"""
    # Code existant...
    
    elif normalized_type == ExerciseTypes.EQUATIONS:
        # Récupérer les limites pour ce type et cette difficulté
        limits = type_limits
        min_coef = limits.get("min_coefficient", 1)
        max_coef = limits.get("max_coefficient", 5)
        include_negatives = limits.get("include_negatives", False)
        
        # Générer les coefficients
        a = random.randint(min_coef, max_coef)
        if include_negatives and random.choice([True, False]):
            a = -a
            
        b = random.randint(min_coef, max_coef)
        if include_negatives and random.choice([True, False]):
            b = -b
            
        # Générer la solution
        x = random.randint(1, 10)
        
        # Calculer le résultat
        result = a * x + b
        
        # Créer l'équation
        equation = f"{a}x + {b} = {result}"
        question = ExerciseMessages.QUESTION_EQUATIONS.format(equation=equation)
        correct_answer = str(x)
        
        # Générer des choix
        choices = [str(x), str(x+1), str(x-1), str(x*2)]
        random.shuffle(choices)
        
        return {
            "title": ExerciseMessages.TITLE_EQUATIONS,
            "exercise_type": normalized_type,
            "difficulty": normalized_difficulty,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC
        }
```

## 2. Ajouter un nouveau niveau de difficulté

### Étape 1 : Mettre à jour `app/core/constants.py`

```python
class DifficultyLevels:
    # Niveaux existants
    INITIE = "initie"
    PADAWAN = "padawan"
    CHEVALIER = "chevalier"
    MAITRE = "maitre"
    
    # Nouveau niveau
    GRAND_MAITRE = "grand_maitre"
    
    # Mettre à jour la liste ALL_LEVELS
    ALL_LEVELS = [INITIE, PADAWAN, CHEVALIER, MAITRE, GRAND_MAITRE]
    
    # Ajouter des alias pour la normalisation
    LEVEL_ALIASES = {
        # Alias existants...
        
        # Nouveaux alias
        GRAND_MAITRE: ["grand_maitre", "grand maitre", "grandmaitre", "gm"]
    }
```

### Étape 2 : Mettre à jour `DISPLAY_NAMES` dans `app/core/constants.py`

```python
DISPLAY_NAMES = {
    # Noms existants...
    
    # Nouveau nom d'affichage
    DifficultyLevels.GRAND_MAITRE: "Grand Maître",
}
```

### Étape 3 : Ajouter les limites dans `DIFFICULTY_LIMITS`

```python
DIFFICULTY_LIMITS = {
    # Niveaux existants...
    
    # Nouveau niveau
    DifficultyLevels.GRAND_MAITRE: {
        ExerciseTypes.ADDITION: {
            "min": 500,
            "max": 1000
        },
        ExerciseTypes.SUBTRACTION: {
            "min1": 500,
            "max1": 1000,
            "min2": 200,
            "max2": 500
        },
        # Répéter pour tous les types d'exercices...
    }
}
```

### Étape 4 : Mettre à jour le CSS dans `static/style.css` ou `static/variables.css`

```css
/* Styles pour le nouveau niveau de difficulté */
.difficulty.grand_maitre { 
    background-color: rgba(128, 0, 128, 0.2);
    color: #e0b0ff;
}

.difficulty.grand_maitre::before {
    content: "\f005\f005\f005\f005\f005";
}
```

## 3. Ajouter un nouveau type de statistique

### Étape 1 : Ajouter des constantes dans `app/core/constants.py`

```python
class StatTypes:
    TOTAL_ATTEMPTS = "total_attempts"
    CORRECT_ATTEMPTS = "correct_attempts"
    SUCCESS_RATE = "success_rate"
    AVERAGE_TIME = "average_time"
    
    # Nouveau type de statistique
    STREAK = "streak"
    
    ALL_STAT_TYPES = [TOTAL_ATTEMPTS, CORRECT_ATTEMPTS, SUCCESS_RATE, AVERAGE_TIME, STREAK]
```

### Étape 2 : Ajouter des requêtes SQL dans `app/db/queries.py`

```python
class UserStatsQueries:
    # Requêtes existantes...
    
    # Nouvelle requête
    GET_STREAK = """
    SELECT MAX(streak)
    FROM (
        SELECT 
            SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS streak,
            SUM(CASE WHEN NOT is_correct THEN 1 ELSE 0 END) AS reset_streak
        FROM (
            SELECT
                r.is_correct,
                CASE WHEN LAG(r.is_correct) OVER (ORDER BY r.created_at) = FALSE OR LAG(r.is_correct) OVER (ORDER BY r.created_at) IS NULL THEN 1 ELSE 0 END AS new_series
            FROM results r
            WHERE r.user_id = %s
            ORDER BY r.created_at
        ) AS streak_data
        GROUP BY new_series
    ) AS max_streaks
    """
```

### Étape 3 : Mettre à jour la fonction `get_user_stats` dans `enhanced_server.py`

```python
async def get_user_stats(request):
    # Code existant...
    
    # Ajouter le calcul du streak
    try:
        cursor.execute(UserStatsQueries.GET_STREAK, (user_id,))
        streak = cursor.fetchone()[0] or 0
    except Exception as e:
        print(f"Erreur lors du calcul du streak: {e}")
        streak = 0
    
    # Ajouter à la réponse
    response_data = {
        # Données existantes...
        'streak': streak,
    }
```

## 4. Conseils pour l'extension de l'application

### Maintenir la cohérence

- Suivez toujours le modèle existant pour ajouter des constantes
- Utilisez des noms descriptifs et cohérents
- Documentez les nouvelles constantes avec des commentaires

### Tester vos extensions

Après avoir ajouté de nouvelles constantes, testez :

```python
from app.core.constants import ExerciseTypes, DifficultyLevels
print(f"Types d'exercices: {ExerciseTypes.ALL_TYPES}")
print(f"Niveaux de difficulté: {DifficultyLevels.ALL_LEVELS}")
```

### Intégrer avec les modèles existants

Si vous ajoutez un nouveau type d'exercice, assurez-vous qu'il est compatible avec :

1. Le modèle `Exercise` dans `app/models/exercise.py`
2. Les schémas Pydantic dans `app/schemas/exercise.py`
3. Les fonctions de normalisation dans `enhanced_server.py`

### Mettre à jour les interfaces utilisateur

N'oubliez pas de mettre à jour :

1. Les templates HTML pour afficher les nouvelles options
2. Les styles CSS pour le nouveau contenu
3. Les interfaces API pour prendre en charge les nouveaux types 
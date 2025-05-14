# Historique des refactorings majeurs - Mathakine

Ce document consolidé présente l'historique des refactorings majeurs effectués sur le projet Mathakine (anciennement Math Trainer), avec un focus particulier sur les efforts de centralisation et d'amélioration de la structure du code.

## 1. Refactoring de centralisation des constantes (Mai 2025)

### Objectifs du refactoring

L'objectif principal de ce refactoring était de centraliser toutes les constantes, valeurs et messages dispersés dans le code pour améliorer la maintenabilité et garantir la cohérence.

### Phase 1: Création de fichiers centralisés

1. **Fichiers créés**:
   - `app/core/constants.py`: Types d'exercices, niveaux de difficulté, limites numériques
   - `app/core/messages.py`: Messages et textes de l'interface utilisateur
   - `app/db/queries.py`: Requêtes SQL centralisées
   - `static/variables.css`: Variables CSS (couleurs, espacement, typographie)

2. **Contenu des fichiers**:

   **constants.py**:
   ```python
   class ExerciseTypes:
       ADDITION = "addition"
       SUBTRACTION = "subtraction"
       MULTIPLICATION = "multiplication"
       DIVISION = "division"
   
   class DifficultyLevels:
       INITIATE = "initiate"  # Initié (facile)
       PADAWAN = "padawan"    # Padawan (intermédiaire)
       KNIGHT = "knight"      # Chevalier (difficile)
       MASTER = "master"      # Maître (expert)
   
   # Limites numériques par niveau de difficulté
   DIFFICULTY_LIMITS = {
       DifficultyLevels.INITIATE: (1, 10),     # Nombres entre 1 et 10
       DifficultyLevels.PADAWAN: (10, 50),     # Nombres entre 10 et 50
       DifficultyLevels.KNIGHT: (50, 100),     # Nombres entre 50 et 100
       DifficultyLevels.MASTER: (100, 500),    # Nombres entre 100 et 500
   }
   
   # Mappings de normalisation (pour la rétrocompatibilité)
   EXERCISE_TYPE_MAPPING = {
       "add": ExerciseTypes.ADDITION,
       "addition": ExerciseTypes.ADDITION,
       "sub": ExerciseTypes.SUBTRACTION,
       "subtraction": ExerciseTypes.SUBTRACTION,
       "subtract": ExerciseTypes.SUBTRACTION,
       "soustraction": ExerciseTypes.SUBTRACTION,
       "mul": ExerciseTypes.MULTIPLICATION,
       "mult": ExerciseTypes.MULTIPLICATION,
       "multiplication": ExerciseTypes.MULTIPLICATION,
       "div": ExerciseTypes.DIVISION,
       "division": ExerciseTypes.DIVISION,
   }
   
   DIFFICULTY_MAPPING = {
       "easy": DifficultyLevels.INITIATE,
       "initiate": DifficultyLevels.INITIATE,
       "initié": DifficultyLevels.INITIATE,
       "medium": DifficultyLevels.PADAWAN,
       "padawan": DifficultyLevels.PADAWAN,
       "hard": DifficultyLevels.KNIGHT,
       "knight": DifficultyLevels.KNIGHT,
       "chevalier": DifficultyLevels.KNIGHT,
       "expert": DifficultyLevels.MASTER,
       "master": DifficultyLevels.MASTER,
       "maître": DifficultyLevels.MASTER,
   }
   ```

   **messages.py**:
   ```python
   class SystemMessages:
       ERROR_INVALID_TYPE = "Type d'exercice non valide. Veuillez choisir parmi: addition, subtraction, multiplication, division."
       ERROR_INVALID_DIFFICULTY = "Niveau de difficulté non valide. Veuillez choisir parmi: initiate, padawan, knight, master."
       ERROR_DATABASE = "Erreur lors de l'accès à la base de données. Veuillez réessayer."
       SUCCESS_EXERCISE_CREATED = "Exercice créé avec succès!"
       SUCCESS_EXERCISE_DELETED = "Exercice supprimé avec succès!"
   
   class ExerciseMessages:
       CORRECT_ANSWER = "Bravo! Votre réponse est correcte!"
       INCORRECT_ANSWER = "Dommage! Votre réponse est incorrecte. La réponse correcte est: {correct_answer}"
       EXPLANATION_PREFIX = "Explication: "
       NO_EXPLANATION = "Aucune explication disponible pour cet exercice."
   
   class ExerciseTypeLabels:
       ADDITION = "Addition"
       SUBTRACTION = "Soustraction"
       MULTIPLICATION = "Multiplication"
       DIVISION = "Division"
   
   class DifficultyLabels:
       INITIATE = "Initié"
       PADAWAN = "Padawan"
       KNIGHT = "Chevalier"
       MASTER = "Maître"
   ```

   **queries.py**:
   ```python
   class ExerciseQueries:
       GET_ALL = """
       SELECT id, title, exercise_type, difficulty, question, correct_answer, choices, explanation, created_at
       FROM exercises
       WHERE is_archived = false
       ORDER BY id DESC
       """
       
       GET_BY_ID = """
       SELECT id, title, exercise_type, difficulty, question, correct_answer, choices, explanation, created_at
       FROM exercises
       WHERE id = %s AND is_archived = false
       """
       
       INSERT = """
       INSERT INTO exercises (exercise_type, difficulty, question, correct_answer, choices, explanation, is_archived, ai_generated)
       VALUES (%s, %s, %s, %s, %s, %s, false, %s)
       RETURNING id
       """
       
       DELETE = """
       UPDATE exercises
       SET is_archived = true
       WHERE id = %s
       """
   
   class ResultQueries:
       INSERT = """
       INSERT INTO results (exercise_id, is_correct, attempt_count, time_spent)
       VALUES (%s, %s, %s, %s)
       RETURNING id
       """
       
       GET_RECENT = """
       SELECT r.id, r.exercise_id, r.is_correct, r.time_spent, r.created_at, e.exercise_type, e.difficulty
       FROM results r
       JOIN exercises e ON r.exercise_id = e.id
       ORDER BY r.created_at DESC
       LIMIT %s
       """
   
   class UserStatsQueries:
       GET_ALL = """
       SELECT id, exercise_type, difficulty, total_attempts, correct_attempts, last_updated
       FROM user_stats
       """
       
       UPDATE = """
       INSERT INTO user_stats (exercise_type, difficulty, total_attempts, correct_attempts)
       VALUES (%s, %s, 1, %s)
       ON CONFLICT (exercise_type, difficulty) DO UPDATE
       SET total_attempts = user_stats.total_attempts + 1,
           correct_attempts = user_stats.correct_attempts + EXCLUDED.correct_attempts,
           last_updated = CURRENT_TIMESTAMP
       """
   ```

   **variables.css**:
   ```css
   :root {
     /* Couleurs principales (thème Star Wars) */
     --sw-blue: #0A1E31;
     --sw-light-blue: #2C5D86;
     --sw-accent: #FFD700;
     --sw-gold: #FFD700;
     --sw-dark: #121212;
     --sw-light: #F5F5F5;
     
     /* Espacements */
     --space-xs: 0.25rem;
     --space-sm: 0.5rem;
     --space-md: 1rem;
     --space-lg: 1.5rem;
     --space-xl: 2rem;
     
     /* Typographie */
     --font-family: 'Roboto', sans-serif;
     --font-size-sm: 0.875rem;
     --font-size-md: 1rem;
     --font-size-lg: 1.25rem;
     --font-size-xl: 1.5rem;
     --font-size-xxl: 2rem;
     
     /* Bordures et ombres */
     --border-radius: 4px;
     --box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
     --box-shadow-lg: 0 4px 12px rgba(0, 0, 0, 0.2);
     
     /* Transitions */
     --transition-fast: 150ms ease-in-out;
     --transition-normal: 300ms ease-in-out;
   }
   ```

### Phase 2: Application des constantes centralisées

1. **enhanced_server.py**:
   - Remplacement des types d'exercices et niveaux de difficulté hardcodés par les constantes
   - Utilisation des messages de `SystemMessages` et `ExerciseMessages`
   - Remplacement des requêtes SQL inline par références aux requêtes centralisées
   - Implémentation des fonctions de normalisation utilisant les mappings centralisés

2. **Fichiers CSS**:
   - Modification des fichiers CSS pour utiliser les variables de `variables.css`
   - Remplacement des valeurs en dur (couleurs, espacements, tailles de police) par variables

3. **Templates HTML**:
   - Utilisation des messages centralisés pour les éléments d'interface

### Problème majeur: Affichage des exercices

Suite au refactoring, un problème important a été identifié: les exercices n'apparaissaient plus dans l'interface utilisateur bien qu'ils soient correctement générés et stockés en base de données.

#### Analyse du problème
Les requêtes SQL centralisées dans `app/db/queries.py` incluaient toutes un filtre `WHERE is_archived = false`, mais le champ `is_archived` n'était pas correctement initialisé lors de la création des exercices.

#### Solution implémentée
1. Modification de la fonction `exercises_page` dans `enhanced_server.py` pour utiliser des requêtes SQL personnalisées sans filtre sur `is_archived`
2. Ajout de débogage pour identifier les exercices présents dans la base de données
3. Modification de la requête `ExerciseQueries.INSERT` pour explicitement définir `is_archived = false`

#### Code de correction
```python
async def exercises_page(request):
    """Page listant tous les exercices"""
    try:
        # Utilisation d'une requête personnalisée sans filtre is_archived
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, title, exercise_type, difficulty, question, correct_answer, choices, created_at
        FROM exercises
        ORDER BY id DESC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        exercises = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Debug: compter les exercices
        print(f"Nombre d'exercices trouvés: {len(exercises)}")
        
        for exercise in exercises:
            # Normaliser les types et niveaux pour l'affichage
            exercise["exercise_type"] = normalize_exercise_type(exercise["exercise_type"])
            exercise["difficulty"] = normalize_difficulty(exercise["difficulty"])
        
        return templates.TemplateResponse("exercises.html", {
            "request": request,
            "exercises": exercises
        })
    except Exception as e:
        print(f"Erreur lors du chargement des exercices: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Erreur: {e}"
        })
```

### Bénéfices du refactoring

1. **Maintenance simplifiée**: Modification des valeurs à un seul endroit
2. **Cohérence accrue**: Utilisation cohérente des mêmes valeurs partout
3. **Réduction de la duplication**: Élimination du code dupliqué
4. **Évolutivité améliorée**: Facilite l'ajout de nouveaux types d'exercices ou niveaux
5. **Préparation pour l'internationalisation**: Messages centralisés facilitant la traduction
6. **Documentation implicite**: Les fichiers centralisés servent de documentation

## 2. Refactoring de l'architecture API (Avril 2025)

### Objectifs
- Séparer clairement l'API REST de l'interface utilisateur
- Structurer l'API selon les bonnes pratiques FastAPI
- Faciliter l'ajout de nouvelles fonctionnalités

### Changements principaux

1. **Structure du dossier `app/`**:
   - Création d'une hiérarchie claire avec sous-dossiers spécialisés
   - Séparation du code par responsabilité (api, models, schemas, services)

2. **Système de routing API**:
   - Implémentation de routeurs FastAPI pour chaque groupe de fonctionnalités
   - Configuration des tags et réponses standardisées

3. **Validation des données**:
   - Utilisation de Pydantic 2.0 pour la validation des entrées/sorties
   - Création de schémas clairs avec contraintes de validation

4. **Organisation des endpoints**:
   - Endpoints GET, POST, PUT, DELETE pour chaque entité
   - Options de filtrage et de tri
   - Pagination standardisée

5. **Authentification et autorisation**:
   - Système d'authentification basé sur JWT
   - Middleware de vérification des droits

### Résultats
- API plus maintenable et extensible
- Documentation OpenAPI automatique et complète
- Validation des données robuste
- Expérience développeur améliorée

## 3. Refactoring de la base de données (Mars 2025)

### Objectifs
- Normaliser le schéma de base de données
- Supporter PostgreSQL pour la production
- Conserver SQLite pour le développement

### Changements principaux

1. **Normalisation du schéma**:
   - Suppression des colonnes redondantes
   - Correction des types de données
   - Ajout de contraintes d'intégrité

2. **Migration SQLite vers PostgreSQL**:
   - Création de scripts de migration
   - Gestion des différences de syntaxe SQL
   - Support pour les deux bases de données

3. **Ajout d'index et d'optimisations**:
   - Index sur les colonnes fréquemment consultées
   - Colonnes composites pour les requêtes communes
   - Optimisation des requêtes et jointures

### Résultats
- Performance améliorée des requêtes
- Intégrité des données renforcée
- Support pour déploiement en production

## 4. Intégration du thème Star Wars (Février 2025)

### Objectifs
- Renommer le projet de "Math Trainer" à "Mathakine"
- Intégrer le thème Star Wars dans l'interface et la terminologie
- Créer une expérience immersive

### Changements principaux

1. **Terminologie**:
   - Renommage des niveaux de difficulté: Initié, Padawan, Chevalier, Maître
   - "Force des nombres" pour les compétences mathématiques
   - "Holocrons" pour la documentation API

2. **Interface utilisateur**:
   - Palette de couleurs inspirée de Star Wars
   - Iconographie et éléments visuels thématiques
   - Animations et effets spéciaux subtils

3. **Structure du projet**:
   - Renommage des fichiers et dossiers
   - Mise à jour des noms de variables et fonctions
   - Documentation thématique

### Résultats
- Expérience utilisateur plus engageante
- Cohérence visuelle et conceptuelle
- Préparation pour la gamification à venir

---

*Ce document consolidé remplace les anciens documents CENTRALISATION_ET_REFACTORING.md, REFACTORING_SUMMARY.md et documents archivés associés.*  
*Dernière mise à jour : 11 Mai 2025* 
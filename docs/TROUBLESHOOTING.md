# Guide de résolution des problèmes - Mathakine

Ce document répertorie les problèmes connus et leurs solutions pour l'application Mathakine. Il sert de référence pour les développeurs et les administrateurs du système.

## Table des matières

1. [Problèmes d'interface](#problèmes-dinterface)
   - [Tableau de bord qui ne se met pas à jour](#tableau-de-bord-qui-ne-se-met-pas-à-jour)
2. [Gestion des données](#gestion-des-données)
   - [Doublons dans les statistiques utilisateur](#doublons-dans-les-statistiques-utilisateur)
   - [Incohérence des types d'exercices et niveaux de difficulté](#incohérence-des-types-dexercices-et-niveaux-de-difficulté)
3. [Sécurité des données](#sécurité-des-données)
   - [Protection contre les entrées utilisateur non valides](#protection-contre-les-entrées-utilisateur-non-valides)
4. [Base de données](#base-de-données)
   - [Vérification de l'intégrité des données](#vérification-de-lintégrité-des-données)
   - [Correction manuelle des données](#correction-manuelle-des-données)
5. [Scripts utiles](#scripts-utiles)
6. [Recommandations générales](#recommandations-générales)

---

## Problèmes d'interface

### Tableau de bord qui ne se met pas à jour

**Problème** : Les statistiques dans le tableau de bord ne se mettent pas à jour après avoir complété des exercices.

**Cause** : Incohérence dans le format des types d'exercices et niveaux de difficulté entre les tables de la base de données. Les types d'exercices dans la table `exercises` pouvaient être en majuscules (ex: "ADDITION") tandis que dans la table `user_stats`, ils étaient en minuscules (ex: "addition").

**Solution** :
1. Normalisation des types d'exercices et des niveaux de difficulté dans la fonction `submit_answer` avant mise à jour des statistiques
2. Création d'un script `fix_database.py` pour corriger les données existantes
3. Mise en place d'un mécanisme pour fusionner les statistiques en cas de doublons

**Code de correction** :
```python
# Dans submit_answer de enhanced_server.py
# Normaliser le type d'exercice et la difficulté
exercise_type = exercise['exercise_type'].lower()
if exercise_type not in ['addition', 'subtraction', 'multiplication', 'division']:
    # Mapper aux formats standard
    if exercise_type == 'ADDITION':
        exercise_type = 'addition'
    # [autres mappings...]

# Mise à jour avec les valeurs normalisées
cursor.execute('''
UPDATE user_stats
SET 
    total_attempts = total_attempts + 1,
    correct_attempts = correct_attempts + CASE WHEN ? THEN 1 ELSE 0 END,
    last_updated = CURRENT_TIMESTAMP
WHERE exercise_type = ? AND difficulty = ?
''', (is_correct, exercise_type, difficulty))
```

**Procédure de vérification** : 
1. Lancer le script `python debug_stats.py` pour vérifier l'état des statistiques
2. Effectuer un exercice de chaque type et difficulté
3. Vérifier que le tableau de bord se met à jour correctement
4. Exécuter les tests avec `python -m unittest tests/test_normalization.py`

---

## Gestion des données

### Doublons dans les statistiques utilisateur

**Problème** : Multiples entrées pour la même combinaison type/difficulté dans `user_stats`.

**Symptômes** : 
- Statistiques incorrectes dans le tableau de bord
- Certains exercices semblent ne pas être comptabilisés
- Incohérence dans les taux de réussite affichés

**Solution** : 
- Fonction `fix_duplicates()` dans `fix_database.py` qui identifie et fusionne les entrées dupliquées
- Utilisation de `INSERT OR IGNORE` et mise à jour conditionnelle pour éviter de nouveaux doublons

**Exécution de la correction** :
```bash
# Exécuter le script de correction de la base de données
python fix_database.py

# À l'invite "Voulez-vous corriger la base de données ? (y/n): ", répondre "y"
```

### Incohérence des types d'exercices et niveaux de difficulté

**Problème** : Différents formats et casses utilisés pour les mêmes types d'exercices et niveaux de difficulté.

**Exemples de variations trouvées** :
- Types : "ADDITION", "Addition", "addition", "ADD"
- Difficultés : "EASY", "Easy", "easy", "INITIE", "Initié"

**Solution** :
- Fonctions de normalisation dans `fix_database.py` :
  - `normalize_exercise_type()` : Standardise les types vers : 'addition', 'subtraction', 'multiplication', 'division'
  - `normalize_difficulty()` : Standardise les difficultés vers : 'easy', 'medium', 'hard'

**Tests de validation** :
- Exécuter `python -m unittest tests/test_normalization.py` pour vérifier que les données sont correctement normalisées

---

## Sécurité des données

### Protection contre les entrées utilisateur non valides

**Problème potentiel** : Risque d'injection SQL ou de corruption de données par des valeurs non attendues dans les types d'exercices ou niveaux de difficulté.

**Solution** : 
- Validation stricte des entrées avec mappage vers des valeurs prédéfinies
- Utilisation de requêtes paramétrées pour toutes les interactions avec la base de données

**Vérification de la sécurité** :
```python
# Exemples de validations correctes dans le code
valid_types = ['addition', 'subtraction', 'multiplication', 'division']
if exercise_type not in valid_types:
    exercise_type = normalize_exercise_type(exercise_type)

# Utilisation de requêtes paramétrées
cursor.execute("UPDATE user_stats SET total_attempts = ? WHERE id = ?", (attempts, user_id))
```

---

## Base de données

### Vérification de l'intégrité des données

Pour vérifier l'intégrité des données dans la base de données, utilisez le script `db_check.py` :

```bash
python tests/db_check.py
```

Le script effectue les vérifications suivantes :
1. Vérification de la configuration de la base de données
2. Test de connexion
3. Vérification des modèles de données
4. Vérification de la normalisation des données

### Correction manuelle des données

Si des problèmes persistent après l'exécution de `fix_database.py`, vous pouvez effectuer des corrections manuelles avec les commandes SQL suivantes :

```sql
-- Normaliser les types d'exercices
UPDATE exercises 
SET exercise_type = LOWER(exercise_type) 
WHERE exercise_type IS NOT NULL;

-- Normaliser les difficultés
UPDATE exercises 
SET difficulty = LOWER(difficulty) 
WHERE difficulty IS NOT NULL;

-- Vérifier les doublons dans user_stats
SELECT exercise_type, difficulty, COUNT(*) as count
FROM user_stats
GROUP BY exercise_type, difficulty
HAVING COUNT(*) > 1;
```

---

## Scripts utiles

- `debug_stats.py` : Affiche l'état actuel des statistiques dans la base de données
  ```bash
  python debug_stats.py
  ```

- `fix_database.py` : Corrige les incohérences et fusionne les doublons dans la base de données
  ```bash
  python fix_database.py
  ```

- `test_update_stats.py` : Simule des soumissions de réponses pour tester la mise à jour des statistiques
  ```bash
  python test_update_stats.py
  ```

- `tests/test_normalization.py` : Tests unitaires pour vérifier la normalisation des données
  ```bash
  python -m unittest tests/test_normalization.py
  ```

- `tests/db_check.py` : Vérification complète de l'intégrité de la base de données
  ```bash
  python tests/db_check.py
  ```

---

## Recommandations générales

1. **Cohérence des données** : Utiliser des énumérations ou des constantes pour les types d'exercices et niveaux de difficulté
   ```python
   # Exemple de bonne pratique
   from enum import Enum
   
   class ExerciseType(str, Enum):
       ADDITION = "addition"
       SUBTRACTION = "subtraction"
       MULTIPLICATION = "multiplication"
       DIVISION = "division"
   ```

2. **Migration vers ORM** : Envisager l'utilisation de SQLAlchemy pour une gestion plus robuste des modèles de données
   ```python
   # Exemple avec SQLAlchemy
   from sqlalchemy import Column, String, Integer
   from sqlalchemy.ext.declarative import declarative_base
   
   Base = declarative_base()
   
   class Exercise(Base):
       __tablename__ = "exercises"
       id = Column(Integer, primary_key=True)
       exercise_type = Column(String, nullable=False)
       difficulty = Column(String, nullable=False)
   ```

3. **Tests automatisés** : Ajouter des tests spécifiques pour vérifier la mise à jour correcte des statistiques
   ```python
   # Exemple de test pour la mise à jour des statistiques
   def test_stats_update_after_exercise():
       # Préparer les données de test
       # Soumettre une réponse
       # Vérifier que les statistiques sont correctement mises à jour
   ```

4. **Surveillance régulière** : Mettre en place une vérification périodique de l'intégrité des données pour détecter rapidement les problèmes

---

*Dernière mise à jour : 22/07/2024* 
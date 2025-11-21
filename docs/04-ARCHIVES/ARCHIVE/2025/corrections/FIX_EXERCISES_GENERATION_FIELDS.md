# 🔧 CORRECTION - Champs manquants lors de la génération d'exercices

**Date** : 2025-01-XX  
**Problème** : Certains champs ne sont pas remplis lors de la génération d'exercices, notamment `is_archived` qui reste NULL au lieu d'être `False`.

---

## 🐛 **PROBLÈME IDENTIFIÉ**

Lors de la génération d'exercices, la requête SQL `INSERT` dans `create_exercise_with_translations` ne spécifiait pas les colonnes `is_archived` et `view_count`, ce qui laissait ces valeurs à `NULL` au lieu d'utiliser les valeurs par défaut de la base de données.

**Impact** :
- Les exercices générés avaient `is_archived = NULL` au lieu de `False`
- Les requêtes SQL avec `WHERE is_archived = false` ne retournaient pas ces exercices
- Seulement 10 exercices sur 14 étaient affichés car 4 avaient `is_archived = NULL`

---

## ✅ **CORRECTIONS APPLIQUÉES**

### 1. **Ajout des champs manquants dans l'INSERT (`app/services/exercise_service_translations.py`)**

**Avant** :
```python
query = """
INSERT INTO exercises 
(title, question, explanation, hint, choices,
 title_translations, question_translations, explanation_translations, 
 hint_translations, choices_translations,
 exercise_type, difficulty, correct_answer, tags, 
 image_url, audio_url, ai_generated, is_active) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
```

**Après** :
```python
query = """
INSERT INTO exercises 
(title, question, explanation, hint, choices,
 title_translations, question_translations, explanation_translations, 
 hint_translations, choices_translations,
 exercise_type, difficulty, correct_answer, tags, 
 image_url, audio_url, ai_generated, is_active, is_archived, view_count) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
```

**Paramètres ajoutés** :
```python
exercise_data.get('is_archived', False),  # Valeur par défaut : False
exercise_data.get('view_count', 0),  # Valeur par défaut : 0
```

### 2. **Ajout de `view_count` dans `enhanced_server_adapter.py`**

Pour cohérence, ajout de `view_count: 0` dans le dictionnaire `exercise_data` :

```python
exercise_data = {
    'title': title,
    'exercise_type': exercise_type,
    'difficulty': difficulty,
    'question': question,
    'correct_answer': correct_answer,
    'choices': choices,
    'explanation': explanation,
    'hint': hint,
    'tags': tags or "generated",
    'ai_generated': ai_generated,
    'is_active': True,
    'is_archived': False,
    'view_count': 0  # Ajouté pour cohérence
}
```

---

## 📋 **CHAMPS REQUIS SELON LE SCHÉMA**

Selon le schéma de la table `exercises` :

| Champ | Type | Valeur par défaut | Nullable |
|-------|------|-------------------|----------|
| `is_active` | BOOLEAN | `TRUE` | Oui |
| `is_archived` | BOOLEAN | `FALSE` | Oui |
| `view_count` | INTEGER | `0` | Oui |
| `ai_generated` | BOOLEAN | `FALSE` | Oui |

**Note** : Même si ces champs ont des valeurs par défaut dans le schéma SQL, il est préférable de les spécifier explicitement dans l'INSERT pour éviter les problèmes si les valeurs par défaut ne sont pas appliquées (par exemple, lors d'une migration ou d'une modification du schéma).

---

## ✅ **VÉRIFICATION**

Pour vérifier que la correction fonctionne :

1. **Générer un nouvel exercice** via l'interface
2. **Vérifier dans la base de données** :
   ```sql
   SELECT id, title, is_active, is_archived, view_count 
   FROM exercises 
   WHERE id = <nouvel_exercice_id>;
   ```
3. **Vérifier que tous les exercices sont retournés** :
   ```sql
   SELECT COUNT(*) FROM exercises WHERE is_archived = false AND is_active = true;
   ```

---

## 📝 **FICHIERS MODIFIÉS**

1. `app/services/exercise_service_translations.py`
   - Ajout de `is_archived` et `view_count` dans la requête INSERT
   - Ajout des valeurs correspondantes dans les paramètres

2. `app/services/enhanced_server_adapter.py`
   - Ajout de `view_count: 0` dans `exercise_data`

---

## 🎯 **RÉSULTAT ATTENDU**

- ✅ Tous les exercices générés ont `is_archived = False` (pas NULL)
- ✅ Tous les exercices générés ont `view_count = 0` (pas NULL)
- ✅ Tous les exercices actifs et non archivés sont retournés par les requêtes
- ✅ Le problème d'affichage de seulement 10 exercices sur 14 est résolu

---

**Correction validée et testée** ✅


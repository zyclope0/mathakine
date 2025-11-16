# ✅ CORRECTION - Date created_at incorrecte (01/01/1970)

**Date** : 2025-01-XX  
**Problème** : Les exercices générés affichent la date "01/01/1970" au lieu de la date réelle de création.

---

## 🐛 **PROBLÈME IDENTIFIÉ**

### **Cause Racine**
Les colonnes `created_at` et `updated_at` n'ont **pas de valeur par défaut** dans la base de données réelle, contrairement à ce qui était attendu. Lors de l'INSERT, ces colonnes n'étaient pas spécifiées, donc PostgreSQL les laissait à `NULL`.

### **Symptôme**
- Date affichée : "01/01/1970" (epoch Unix, timestamp 0)
- Valeur en BDD : `NULL`
- Frontend : `new Date(null)` ou `new Date(undefined)` → "01/01/1970"

---

## ✅ **CORRECTIONS APPLIQUÉES**

### **1. INSERT avec timestamps explicites (`app/services/exercise_service_translations.py`)**

**Avant** :
```sql
INSERT INTO exercises 
(title, question, ..., view_count) 
VALUES (%s, %s, ..., %s)
RETURNING id, created_at
```

**Après** :
```sql
INSERT INTO exercises 
(title, question, ..., view_count, created_at, updated_at) 
VALUES (%s, %s, ..., %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
RETURNING id, created_at
```

**Résultat** : `created_at` et `updated_at` sont maintenant explicitement définis avec `CURRENT_TIMESTAMP` lors de la création.

### **2. Formatage des dates (`app/services/exercise_service_translations.py`)**

Ajout du formatage des dates en ISO format strings dans :
- `get_exercise()` : Formate `created_at` et `updated_at` en ISO strings
- `list_exercises()` : Formate `created_at` et `updated_at` pour chaque exercice

**Code ajouté** :
```python
# Formater les dates en ISO format strings pour sérialisation JSON
if exercise.get('created_at'):
    if hasattr(exercise['created_at'], 'isoformat'):
        exercise['created_at'] = exercise['created_at'].isoformat()
```

### **3. Protection frontend (`frontend/components/exercises/ExerciseCard.tsx`)**

Ajout d'une vérification pour éviter l'affichage si `created_at` est absent :
```tsx
{exercise.created_at && (
  <div className="flex items-center gap-1">
    <Calendar className="h-4 w-4" />
    <time dateTime={exercise.created_at}>
      {new Date(exercise.created_at).toLocaleDateString('fr-FR')}
    </time>
  </div>
)}
```

---

## 📋 **VÉRIFICATION DU SCHÉMA**

### **Colonnes sans valeur par défaut en BDD**
- `created_at` : NULL (pas de défaut)
- `updated_at` : NULL (pas de défaut)
- `is_active` : NULL (pas de défaut)
- `is_archived` : NULL (pas de défaut)
- `view_count` : NULL (pas de défaut)

### **Colonnes avec valeur par défaut**
- `ai_generated` : `false`

**Note** : Les valeurs par défaut sont maintenant appliquées explicitement dans l'INSERT plutôt que de dépendre du schéma de la base de données.

---

## ✅ **RÉSULTAT ATTENDU**

Après ces corrections :
- ✅ `created_at` et `updated_at` sont correctement remplis avec `CURRENT_TIMESTAMP`
- ✅ Les dates sont formatées en ISO strings pour la sérialisation JSON
- ✅ Le frontend affiche la date correcte au format français (DD/MM/YYYY)
- ✅ Les exercices existants avec `created_at = NULL` n'afficheront pas de date (protection frontend)

---

## 🔧 **FICHIERS MODIFIÉS**

1. **`app/services/exercise_service_translations.py`**
   - Ajout de `created_at` et `updated_at` dans l'INSERT avec `CURRENT_TIMESTAMP`
   - Ajout du formatage des dates en ISO strings dans `get_exercise()` et `list_exercises()`

2. **`frontend/components/exercises/ExerciseCard.tsx`**
   - Ajout d'une vérification pour éviter l'affichage si `created_at` est absent

---

## 📝 **NOTE IMPORTANTE**

Les exercices existants avec `created_at = NULL` continueront d'afficher "01/01/1970" ou rien (selon la protection frontend). Pour corriger les données existantes, une migration SQL serait nécessaire :

```sql
UPDATE exercises 
SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP 
WHERE created_at IS NULL;
```


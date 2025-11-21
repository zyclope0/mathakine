# 🔍 AUDIT GÉNÉRATION D'EXERCICES

**Date** : Janvier 2025  
**Objectif** : Identifier et corriger les incohérences dans la génération d'exercices (standard et IA)

---

## 📋 **PROBLÈMES IDENTIFIÉS**

### ❌ **1. Normalisation manquante dans `generate_ai_exercise_stream`**

**Fichier** : `server/handlers/exercise_handlers.py`  
**Ligne** : 461  
**Problème** : Le `exercise_type` est utilisé tel quel sans normalisation avant d'être passé à OpenAI et sauvegardé.

```python
# ❌ AVANT (ligne 461)
normalized_exercise = {
    "exercise_type": exercise_type,  # Non normalisé !
    ...
}
```

**Impact** : Si le frontend envoie `"geometrie"` mais que le backend attend `"géométrie"` ou un autre format, l'exercice généré aura le mauvais type.

---

### ❌ **2. Prompt OpenAI sans normalisation**

**Fichier** : `server/handlers/exercise_handlers.py`  
**Ligne** : 428  
**Problème** : Le `exercise_type` est passé directement à OpenAI sans normalisation.

```python
# ❌ AVANT (ligne 428)
user_prompt = f"Crée un exercice de type {exercise_type} niveau {difficulty}."
```

**Impact** : OpenAI peut recevoir un type non normalisé et générer un exercice du mauvais type.

---

### ❌ **3. Correspondance Frontend ↔ Backend**

**Frontend** (`frontend/lib/constants/exercises.ts`) :
- `GEOMETRIE: 'geometrie'` (minuscule)

**Backend** (`app/core/constants.py`) :
- `GEOMETRIE = ExerciseType.GEOMETRIE.value` → `"geometrie"` (minuscule)
- Alias : `GEOMETRIE: [GEOMETRIE, "geometry", "geo"]`

**Vérification** : ✅ La correspondance semble correcte, mais il faut s'assurer que la normalisation fonctionne.

---

### ❌ **4. Types manquants dans `generate_simple_exercise`**

**Fichier** : `server/exercise_generator.py`  
**Types gérés** :
- ✅ ADDITION
- ✅ SUBTRACTION
- ✅ MULTIPLICATION
- ✅ DIVISION
- ✅ TEXTE
- ❌ **FRACTIONS** (manquant)
- ❌ **GEOMETRIE** (manquant)
- ❌ **MIXTE** (manquant)
- ❌ **DIVERS** (manquant)

**Impact** : Si un utilisateur demande un exercice de type FRACTIONS, GEOMETRIE, MIXTE ou DIVERS en mode "standard", aucune génération n'est effectuée (pas de `elif` correspondant).

---

### ❌ **5. Types manquants dans `generate_ai_exercise`**

**Fichier** : `server/exercise_generator.py`  
**Types gérés** :
- ✅ ADDITION
- ✅ SUBTRACTION
- ✅ MULTIPLICATION
- ✅ DIVISION
- ✅ FRACTIONS
- ✅ GEOMETRIE
- ✅ DIVERS
- ✅ MIXTE
- ❌ **TEXTE** (manquant)

**Impact** : Si un utilisateur demande un exercice de type TEXTE en mode IA, aucune génération n'est effectuée.

---

### ⚠️ **6. Fallback par défaut**

**Fichier** : `server/exercise_generator.py`  
**Ligne** : 13-26 (`normalize_exercise_type`)

```python
# Si aucune correspondance trouvée, retourner le type tel quel
return exercise_type
```

**Problème** : Si un type non reconnu est passé, il est retourné tel quel, ce qui peut causer des erreurs dans les fonctions de génération qui ne gèrent pas ce type.

---

## 🔧 **CORRECTIONS À APPLIQUER**

### ✅ **1. Normaliser `exercise_type` dans `generate_ai_exercise_stream`**

```python
# ✅ APRÈS
from server.exercise_generator import normalize_exercise_type, normalize_difficulty

# Normaliser les paramètres
normalized_type = normalize_exercise_type(exercise_type)
normalized_difficulty = normalize_difficulty(difficulty)

# Utiliser les valeurs normalisées
user_prompt = f"Crée un exercice de type {normalized_type} niveau {normalized_difficulty}."
...
normalized_exercise = {
    "exercise_type": normalized_type,  # Normalisé !
    "difficulty": normalized_difficulty,  # Normalisé !
    ...
}
```

---

### ✅ **2. Ajouter les types manquants dans `generate_simple_exercise`**

Ajouter les cas manquants :
- FRACTIONS
- GEOMETRIE
- MIXTE
- DIVERS

---

### ✅ **3. Ajouter le type TEXTE dans `generate_ai_exercise`**

Ajouter le cas manquant :
- TEXTE

---

### ✅ **4. Améliorer le fallback dans `normalize_exercise_type`**

```python
# ✅ APRÈS
def normalize_exercise_type(exercise_type):
    """Normalise le type d'exercice"""
    if not exercise_type:
        return ExerciseTypes.ADDITION

    exercise_type = exercise_type.lower()

    # Parcourir tous les types d'exercices et leurs alias
    for type_key, aliases in ExerciseTypes.TYPE_ALIASES.items():
        if exercise_type in aliases:
            return type_key
    
    # Si aucune correspondance trouvée, logger un avertissement et retourner ADDITION par défaut
    print(f"⚠️ Type d'exercice non reconnu: {exercise_type}, utilisation de ADDITION par défaut")
    return ExerciseTypes.ADDITION
```

---

### ✅ **5. Validation stricte des types**

Ajouter une validation après normalisation pour s'assurer que le type est valide :

```python
# ✅ APRÈS
normalized_type = normalize_exercise_type(exercise_type)

# Valider que le type est dans la liste des types valides
if normalized_type not in ExerciseTypes.ALL_TYPES:
    print(f"⚠️ Type normalisé invalide: {normalized_type}, utilisation de ADDITION par défaut")
    normalized_type = ExerciseTypes.ADDITION
```

---

## 📊 **TABLEAU DE CORRESPONDANCE TYPE ↔ NIVEAU ↔ CONTENU**

| Type | Frontend | Backend | Standard | IA | Niveaux Supportés |
|------|----------|---------|----------|----|-------------------|
| Addition | `addition` | `addition` | ✅ | ✅ | Tous |
| Soustraction | `soustraction` | `soustraction` | ✅ | ✅ | Tous |
| Multiplication | `multiplication` | `multiplication` | ✅ | ✅ | Tous |
| Division | `division` | `division` | ✅ | ✅ | Tous |
| Fractions | `fractions` | `fractions` | ✅ | ✅ | Tous |
| Géométrie | `geometrie` | `geometrie` | ✅ | ✅ | Tous |
| Texte | `texte` | `texte` | ✅ | ✅ | Tous |
| Mixte | `mixte` | `mixte` | ✅ | ✅ | Tous |
| Divers | `divers` | `divers` | ✅ | ✅ | Tous |

**Légende** :
- ✅ : Type géré correctement
- ❌ : Type manquant dans la fonction de génération

---

## 🎯 **PLAN D'ACTION**

1. ✅ **Corriger `generate_ai_exercise_stream`** : Normaliser `exercise_type` et `difficulty` - **FAIT**
2. ✅ **Ajouter types manquants dans `generate_simple_exercise`** : FRACTIONS, GEOMETRIE, MIXTE, DIVERS - **FAIT**
3. ✅ **Ajouter type TEXTE dans `generate_ai_exercise`** : TEXTE - **DÉJÀ PRÉSENT**
4. ✅ **Améliorer `normalize_exercise_type`** : Fallback vers ADDITION au lieu de retourner le type tel quel - **FAIT**
5. ✅ **Ajouter validation stricte** : Vérifier que le type normalisé est valide - **FAIT**
6. ✅ **Améliorer prompt OpenAI** : Instructions strictes sur le type d'exercice - **FAIT**
7. ⏳ **Tests** : Vérifier que chaque type génère bien le bon type d'exercice

---

## 📝 **NOTES**

- Le problème principal semble être la **non-normalisation** dans `generate_ai_exercise_stream`
- Les **types manquants** dans `generate_simple_exercise` peuvent causer des erreurs silencieuses
- Le **fallback par défaut** doit être amélioré pour éviter les types invalides

---

## ✅ **CORRECTIONS APPLIQUÉES**

### **1. Normalisation dans `generate_ai_exercise_stream`**
- ✅ Ajout de la normalisation de `exercise_type` et `difficulty` avant utilisation
- ✅ Validation que le type normalisé est dans `ExerciseTypes.ALL_TYPES`
- ✅ Amélioration du prompt système OpenAI avec instructions strictes sur le type
- ✅ Utilisation des valeurs normalisées dans `normalized_exercise`

### **2. Normalisation dans `generate_exercise_api`**
- ✅ Ajout de la normalisation de `exercise_type` et `difficulty`
- ✅ Validation que le type normalisé est valide
- ✅ Logging amélioré pour tracer la normalisation

### **3. Normalisation dans `generate_exercise` (GET)**
- ✅ Ajout de la normalisation de `exercise_type` et `difficulty`
- ✅ Support de `type` et `exercise_type` dans les query params
- ✅ Validation que le type normalisé est valide

### **4. Types manquants dans `generate_simple_exercise`**
- ✅ Ajout de FRACTIONS avec génération adaptée aux niveaux
- ✅ Ajout de GEOMETRIE avec formes et propriétés selon la difficulté
- ✅ Ajout de MIXTE avec sélection aléatoire d'opération
- ✅ Ajout de DIVERS avec séquences, âge, monnaie

### **5. Amélioration de `normalize_exercise_type`**
- ✅ Fallback vers `ExerciseTypes.ADDITION` au lieu de retourner le type tel quel
- ✅ Logging d'avertissement pour les types non reconnus

### **6. Amélioration du prompt OpenAI**
- ✅ Instructions strictes sur le type d'exercice à générer
- ✅ Liste explicite des types possibles dans le prompt système
- ✅ Répétition du type dans le prompt utilisateur pour renforcer la contrainte

---

## 🧪 **TESTS RECOMMANDÉS**

1. **Test de normalisation** : Vérifier que `"geometrie"`, `"Géométrie"`, `"geometry"` génèrent tous des exercices de géométrie
2. **Test de type** : Vérifier que chaque type génère bien le bon type d'exercice (pas d'addition quand on demande géométrie)
3. **Test de niveau** : Vérifier que chaque niveau génère des exercices adaptés à la difficulté
4. **Test IA vs Standard** : Vérifier que les deux modes génèrent des exercices cohérents pour le même type/niveau
5. **Test de fallback** : Vérifier qu'un type invalide génère un exercice d'addition par défaut avec un avertissement


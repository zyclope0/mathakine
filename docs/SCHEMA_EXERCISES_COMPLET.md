# 📋 SCHÉMA COMPLET - TABLE EXERCISES

**Date** : 2025-01-XX  
**Source** : Modèle SQLAlchemy + Migrations + Liste utilisateur

---

## 🔍 **COLONNES IDENTIFIÉES**

### **Colonnes NOT NULL (Requis)**

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INTEGER (SERIAL) | Clé primaire, auto-incrémentée |
| `title` | VARCHAR(255) | Titre de l'exercice |
| `exercise_type` | VARCHAR(20) / ENUM | Type d'exercice (addition, soustraction, etc.) |
| `difficulty` | VARCHAR(20) / ENUM | Niveau de difficulté (initie, padawan, chevalier, maitre) |
| `question` | TEXT | Énoncé de la question |
| `correct_answer` | VARCHAR(255) | Réponse correcte |

### **Colonnes NULL avec Valeurs par Défaut**

| Colonne | Type | Default | Description |
|---------|------|---------|-------------|
| `is_active` | BOOLEAN | `TRUE` | Exercice actif |
| `is_archived` | BOOLEAN | `FALSE` | Exercice archivé |
| `view_count` | INTEGER | `0` | Nombre de vues |
| `ai_generated` | BOOLEAN | `FALSE` | Généré par IA |
| `created_at` | TIMESTAMP WITH TIME ZONE | `CURRENT_TIMESTAMP` | Date de création |
| `updated_at` | TIMESTAMP WITH TIME ZONE | `CURRENT_TIMESTAMP` | Date de mise à jour |

### **Colonnes NULL sans Défaut (Optionnelles)**

| Colonne | Type | Description |
|---------|------|-------------|
| `creator_id` | INTEGER | ID du créateur (FK vers users.id) |
| `tags` | VARCHAR(255) | Tags séparés par virgules |
| `age_group` | VARCHAR(10) | Groupe d'âge cible (6-8, 8-10, etc.) |
| `context_theme` | VARCHAR(50) | Contexte thématique |
| `complexity` | INTEGER | Niveau de complexité cognitive (1-5) |
| `explanation` | TEXT | Explication de la solution |
| `hint` | TEXT | Indice pour aider l'élève |
| `choices` | JSON/JSONB | Options pour QCM (array) |
| `image_url` | VARCHAR(255) | URL de l'image associée |
| `audio_url` | VARCHAR(255) | URL audio pour accessibilité |

### **Colonnes de Traduction (JSONB)**

| Colonne | Type | Default | Description |
|---------|------|---------|-------------|
| `title_translations` | JSONB | `{"fr": null}` | Traductions du titre |
| `question_translations` | JSONB | `{"fr": null}` | Traductions de la question |
| `explanation_translations` | JSONB | `{"fr": null}` | Traductions de l'explication |
| `hint_translations` | JSONB | `{"fr": null}` | Traductions de l'indice |
| `choices_translations` | JSONB | `{"fr": null}` | Traductions des choix |

### **Colonnes Mentionnées mais Non Trouvées dans le Modèle**

| Colonne | Statut | Action Requise |
|---------|--------|----------------|
| `answer_type` | ⚠️ Non trouvé dans modèle | Vérifier si existe en BDD |
| `text_metadata` | ⚠️ Non trouvé dans modèle | Vérifier si existe en BDD |

---

## ✅ **VALEURS PAR DÉFAUT RECOMMANDÉES**

Pour garantir la cohérence lors de la création :

```python
DEFAULTS = {
    'is_active': True,
    'is_archived': False,
    'view_count': 0,
    'ai_generated': False,
    'tags': 'generated',  # Si non fourni
    # Les timestamps sont gérés automatiquement par PostgreSQL
}
```

---

## 🔧 **CORRECTIONS À APPLIQUER**

### **1. Fonction `create_exercise_with_translations`**

**Champs manquants dans l'INSERT actuel** :
- ❌ `creator_id` (peut être NULL mais devrait être inclus)
- ❌ `age_group` (peut être NULL mais devrait être inclus)
- ❌ `context_theme` (peut être NULL mais devrait être inclus)
- ❌ `complexity` (peut être NULL mais devrait être inclus)
- ⚠️ `answer_type` (si existe en BDD)
- ⚠️ `text_metadata` (si existe en BDD)

**Champs déjà présents** : ✅
- title, question, explanation, hint, choices
- title_translations, question_translations, explanation_translations, hint_translations, choices_translations
- exercise_type, difficulty, correct_answer, tags
- image_url, audio_url
- ai_generated, is_active, is_archived, view_count

---

## 📝 **PROCHAINES ÉTAPES**

1. ✅ Vérifier si `answer_type` et `text_metadata` existent réellement en BDD
2. ✅ Ajouter tous les champs manquants dans l'INSERT
3. ✅ Vérifier toutes les autres fonctions de création (ORM, etc.)
4. ✅ S'assurer que les valeurs par défaut sont appliquées partout


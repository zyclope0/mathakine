# 🌐 PLAN DE TRADUCTION DES DONNÉES

**Date** : Janvier 2025  
**Objectif** : Permettre la traduction des données (exercices, défis, badges) en plus de l'interface utilisateur

---

## 📋 **CHAMPS TRADUISIBLES IDENTIFIÉS**

### **Exercise (Exercices)**
- `title` : Titre de l'exercice
- `question` : Question de l'exercice
- `explanation` : Explication de la solution
- `hint` : Indice pour aider l'élève
- `choices` : Options QCM (JSON array)

### **LogicChallenge (Défis Logiques)**
- `title` : Titre du défi
- `description` : Description du défi
- `question` : Question spécifique
- `solution_explanation` : Explication détaillée
- `hints` : Indices (JSON array)

### **Achievement (Badges)**
- `name` : Nom du badge
- `description` : Description du badge
- `star_wars_title` : Titre Star Wars

---

## 🎯 **SOLUTION PROPOSÉE : JSONB PostgreSQL**

### **Avantages**
- ✅ Flexible : Ajout facile de nouvelles langues
- ✅ Performant : Indexation JSONB native PostgreSQL
- ✅ Cohérent : Même structure pour toutes les entités
- ✅ Rétrocompatible : Fallback vers français si traduction manquante

### **Structure JSONB**

```json
{
  "fr": "Texte en français",
  "en": "Text in English"
}
```

Pour les arrays (choices, hints) :
```json
{
  "fr": ["Choix 1", "Choix 2", "Choix 3"],
  "en": ["Choice 1", "Choice 2", "Choice 3"]
}
```

---

## 📊 **MIGRATION DE BASE DE DONNÉES**

### **Option 1 : Colonnes JSONB dédiées (RECOMMANDÉ)**

Ajouter des colonnes `*_translations` pour chaque champ traduisible :

**Table `exercises` :**
```sql
ALTER TABLE exercises 
  ADD COLUMN title_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN question_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN explanation_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN hint_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN choices_translations JSONB DEFAULT '{"fr": null}'::jsonb;

-- Migrer les données existantes
UPDATE exercises SET
  title_translations = jsonb_build_object('fr', title),
  question_translations = jsonb_build_object('fr', question),
  explanation_translations = jsonb_build_object('fr', COALESCE(explanation, '')),
  hint_translations = jsonb_build_object('fr', COALESCE(hint, '')),
  choices_translations = CASE 
    WHEN choices IS NOT NULL THEN jsonb_build_object('fr', choices)
    ELSE '{"fr": null}'::jsonb
  END;

-- Créer des index GIN pour les recherches
CREATE INDEX idx_exercises_title_translations ON exercises USING GIN (title_translations);
CREATE INDEX idx_exercises_question_translations ON exercises USING GIN (question_translations);
```

**Table `logic_challenges` :**
```sql
ALTER TABLE logic_challenges
  ADD COLUMN title_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN description_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN question_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN solution_explanation_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN hints_translations JSONB DEFAULT '{"fr": null}'::jsonb;

-- Migrer les données existantes
UPDATE logic_challenges SET
  title_translations = jsonb_build_object('fr', title),
  description_translations = jsonb_build_object('fr', description),
  question_translations = jsonb_build_object('fr', COALESCE(question, '')),
  solution_explanation_translations = jsonb_build_object('fr', COALESCE(solution_explanation, '')),
  hints_translations = CASE 
    WHEN hints IS NOT NULL THEN jsonb_build_object('fr', hints)
    ELSE '{"fr": null}'::jsonb
  END;

-- Index GIN
CREATE INDEX idx_challenges_title_translations ON logic_challenges USING GIN (title_translations);
CREATE INDEX idx_challenges_description_translations ON logic_challenges USING GIN (description_translations);
```

**Table `achievements` :**
```sql
ALTER TABLE achievements
  ADD COLUMN name_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN description_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN star_wars_title_translations JSONB DEFAULT '{"fr": null}'::jsonb;

-- Migrer les données existantes
UPDATE achievements SET
  name_translations = jsonb_build_object('fr', name),
  description_translations = jsonb_build_object('fr', COALESCE(description, '')),
  star_wars_title_translations = jsonb_build_object('fr', COALESCE(star_wars_title, ''));

-- Index GIN
CREATE INDEX idx_achievements_name_translations ON achievements USING GIN (name_translations);
```

---

## 🔧 **IMPLÉMENTATION BACKEND**

### **1. Helper de Traduction**

Créer `app/utils/translation.py` :

```python
from typing import Optional, Dict, Any, List
from app.core.config import settings

def get_translated_text(
    translations: Optional[Dict[str, Any]],
    locale: str = "fr",
    fallback_locale: str = "fr"
) -> Optional[str]:
    """
    Récupère le texte traduit depuis un objet JSONB de traductions.
    
    Args:
        translations: Dictionnaire JSONB des traductions {locale: text}
        locale: Locale demandée (fr, en, etc.)
        fallback_locale: Locale de repli si la traduction n'existe pas
    
    Returns:
        Texte traduit ou None
    """
    if not translations:
        return None
    
    # Essayer la locale demandée
    if locale in translations and translations[locale]:
        return translations[locale]
    
    # Fallback vers la locale par défaut
    if fallback_locale in translations and translations[fallback_locale]:
        return translations[fallback_locale]
    
    # Fallback vers la première locale disponible
    if translations:
        first_locale = next(iter(translations))
        return translations[first_locale]
    
    return None


def get_translated_array(
    translations: Optional[Dict[str, List[str]]],
    locale: str = "fr",
    fallback_locale: str = "fr"
) -> Optional[List[str]]:
    """
    Récupère un array traduit depuis un objet JSONB de traductions.
    
    Args:
        translations: Dictionnaire JSONB des traductions {locale: [items]}
        locale: Locale demandée
        fallback_locale: Locale de repli
    
    Returns:
        Liste traduite ou None
    """
    if not translations:
        return None
    
    if locale in translations and translations[locale]:
        return translations[locale]
    
    if fallback_locale in translations and translations[fallback_locale]:
        return translations[fallback_locale]
    
    if translations:
        first_locale = next(iter(translations))
        return translations[first_locale]
    
    return None


def build_translations_dict(
    fr_text: Optional[str],
    en_text: Optional[str] = None,
    **other_locales
) -> Dict[str, Any]:
    """
    Construit un dictionnaire de traductions pour insertion en JSONB.
    
    Args:
        fr_text: Texte français (obligatoire)
        en_text: Texte anglais (optionnel)
        **other_locales: Autres langues (ex: es="Texto en español")
    
    Returns:
        Dictionnaire de traductions
    """
    translations = {"fr": fr_text}
    
    if en_text:
        translations["en"] = en_text
    
    translations.update(other_locales)
    
    return translations
```

### **2. Mise à jour des Requêtes SQL (PostgreSQL pur)**

**`app/db/queries.py` :**

Ajouter des fonctions SQL pour extraire les traductions depuis JSONB :

```python
# Fonction SQL helper pour extraire une traduction
GET_TRANSLATED_TEXT_SQL = """
COALESCE(
    title_translations->%s,
    title_translations->'fr',
    to_jsonb(title)
)::text
"""

# Requêtes mises à jour avec traductions
class ExerciseQueries:
    GET_BY_ID_WITH_TRANSLATION = """
    SELECT 
        id,
        COALESCE(title_translations->%s, title_translations->'fr', to_jsonb(title))::text as title,
        COALESCE(question_translations->%s, question_translations->'fr', to_jsonb(question))::text as question,
        COALESCE(explanation_translations->%s, explanation_translations->'fr', to_jsonb(COALESCE(explanation, '')))::text as explanation,
        COALESCE(hint_translations->%s, hint_translations->'fr', to_jsonb(COALESCE(hint, '')))::text as hint,
        COALESCE(choices_translations->%s, choices_translations->'fr', choices) as choices,
        exercise_type,
        difficulty,
        correct_answer,
        -- autres champs...
    FROM exercises 
    WHERE id = %s AND is_archived = false
    """
```

**Note** : Utiliser des requêtes SQL brutes avec psycopg2, pas SQLAlchemy ORM.

### **3. Mise à jour des Schémas Pydantic**

**`app/schemas/exercise.py` :**
```python
from typing import Optional, Dict, Any, List
import json

class ExerciseBase(BaseModel):
    # ... champs existants ...
    
    # Champs de traduction (optionnels pour création)
    title_translations: Optional[Dict[str, str]] = None
    question_translations: Optional[Dict[str, str]] = None
    explanation_translations: Optional[Dict[str, str]] = None
    hint_translations: Optional[Dict[str, str]] = None
    choices_translations: Optional[Dict[str, List[str]]] = None

class ExerciseResponse(ExerciseInDB):
    """Schéma de réponse avec traductions selon la locale"""
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any], locale: str = "fr"):
        """
        Crée une réponse depuis une ligne de base de données.
        Les traductions sont déjà extraites dans la requête SQL.
        """
        # Les champs traduits sont déjà dans row avec les bonnes valeurs
        return cls(
            id=row['id'],
            title=row.get('title', ''),
            question=row.get('question', ''),
            explanation=row.get('explanation'),
            hint=row.get('hint'),
            choices=row.get('choices'),  # Déjà un array Python depuis JSONB
            exercise_type=row.get('exercise_type'),
            difficulty=row.get('difficulty'),
            # ... autres champs ...
        )
```

### **4. Mise à jour des Services (PostgreSQL pur)**

**`app/services/exercise_service.py` :**
```python
import psycopg2
from psycopg2.extras import RealDictCursor
from server.database import get_db_connection
from app.utils.translation import parse_accept_language

def get_exercise(exercise_id: int, locale: str = "fr") -> Optional[Dict]:
    """
    Récupère un exercice avec traductions depuis PostgreSQL.
    Utilise des requêtes SQL brutes avec psycopg2.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Requête SQL avec extraction des traductions JSONB
        query = """
        SELECT 
            id,
            COALESCE(title_translations->%s, title_translations->'fr', to_jsonb(title))::text as title,
            COALESCE(question_translations->%s, question_translations->'fr', to_jsonb(question))::text as question,
            COALESCE(explanation_translations->%s, explanation_translations->'fr', to_jsonb(COALESCE(explanation, '')))::text as explanation,
            COALESCE(hint_translations->%s, hint_translations->'fr', to_jsonb(COALESCE(hint, '')))::text as hint,
            COALESCE(choices_translations->%s, choices_translations->'fr', choices) as choices,
            exercise_type,
            difficulty,
            correct_answer,
            image_url,
            audio_url,
            is_active,
            view_count,
            created_at,
            updated_at
        FROM exercises 
        WHERE id = %s AND is_archived = false
        """
        
        cursor.execute(query, (locale, locale, locale, locale, locale, exercise_id))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Convertir en dict (RealDictCursor le fait déjà)
        exercise = dict(row)
        
        # Parser les JSON arrays si nécessaire
        if exercise.get('choices') and isinstance(exercise['choices'], str):
            import json
            exercise['choices'] = json.loads(exercise['choices'])
        
        return exercise
    
    finally:
        cursor.close()
        conn.close()
```

### **5. Mise à jour des Endpoints API**

**`app/api/endpoints/exercises.py` :**
```python
from fastapi import Depends, Header, Request
from app.utils.translation import parse_accept_language

@router.get("/exercises/{exercise_id}")
async def get_exercise(
    exercise_id: int,
    request: Request
):
    """Récupère un exercice avec traductions"""
    # Parser Accept-Language header depuis les headers de la requête
    accept_language = request.headers.get("Accept-Language")
    locale = parse_accept_language(accept_language) or "fr"
    
    exercise = exercise_service.get_exercise(exercise_id, locale=locale)
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    return exercise
```

**`server/handlers/exercise_handlers.py` (Starlette) :**
```python
from app.utils.translation import parse_accept_language

async def get_exercise(request):
    """Récupère un exercice avec traductions"""
    exercise_id = int(request.path_params['id'])
    
    # Parser Accept-Language header
    accept_language = request.headers.get("Accept-Language")
    locale = parse_accept_language(accept_language) or "fr"
    
    exercise = exercise_service.get_exercise(exercise_id, locale=locale)
    
    if not exercise:
        return JSONResponse({"error": "Exercise not found"}, status_code=404)
    
    return JSONResponse(exercise)
```

---

## 🎨 **IMPLÉMENTATION FRONTEND**

### **1. Mise à jour des Hooks**

**`frontend/hooks/useExercises.ts` :**
```typescript
import { useLocaleStore } from '@/lib/stores/localeStore';

export function useExercises(filters?: ExerciseFilters) {
  const { locale } = useLocaleStore();
  
  return useQuery({
    queryKey: ['exercises', filters, locale],
    queryFn: async () => {
      const response = await apiClient.get('/api/exercises', {
        params: filters,
        headers: {
          'Accept-Language': locale,
        },
      });
      return response.data;
    },
  });
}
```

### **2. Headers HTTP automatiques**

**`frontend/lib/api/client.ts` :**
```typescript
import { useLocaleStore } from '@/lib/stores/localeStore';

// Ajouter Accept-Language header automatiquement
const localeStore = useLocaleStore.getState();
const headers = {
  'Content-Type': 'application/json',
  'Accept-Language': localeStore.locale,
};
```

---

## 📝 **MIGRATION DES DONNÉES EXISTANTES**

### **Script de Migration (PostgreSQL pur)**

Créer `scripts/migrations/migrate_to_translations.py` :

```python
"""
Script pour migrer les données existantes vers le système de traductions.
Utilise psycopg2 directement.
"""
import psycopg2
import json
from server.database import get_db_connection
from loguru import logger

def migrate_exercises():
    """Migre les exercices vers le système de traductions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Récupérer tous les exercices
        cursor.execute("SELECT id, title, question, explanation, hint, choices FROM exercises")
        exercises = cursor.fetchall()
        
        migrated = 0
        
        for exercise_id, title, question, explanation, hint, choices in exercises:
            updates = []
            params = []
            
            # Vérifier et migrer title_translations
            cursor.execute(
                "SELECT title_translations FROM exercises WHERE id = %s",
                (exercise_id,)
            )
            row = cursor.fetchone()
            if not row[0] or row[0] == '{"fr": null}':
                updates.append("title_translations = %s")
                params.append(json.dumps({"fr": title}))
            
            # Même logique pour les autres champs...
            
            if updates:
                query = f"UPDATE exercises SET {', '.join(updates)} WHERE id = %s"
                params.append(exercise_id)
                cursor.execute(query, tuple(params))
                migrated += 1
        
        conn.commit()
        logger.success(f"✅ Migré {migrated} exercices")
    
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erreur: {e}")
    finally:
        cursor.close()
        conn.close()

# Même logique pour LogicChallenge et Achievement
```

---

## ✅ **CHECKLIST D'IMPLÉMENTATION**

### **Phase 1 : Préparation**
- [x] Créer migration SQL pour ajouter colonnes JSONB (`scripts/migrations/add_translation_columns.sql`)
- [x] Créer helper `app/utils/translation.py`
- [x] Créer requêtes SQL avec traductions (`app/db/queries_translations.py`)
- [x] Créer service avec traductions (`app/services/exercise_service_translations.py`)
- [x] Créer script de migration des données (`scripts/migrations/migrate_to_translations.py`)
- [ ] Tester migration sur données de test

### **Phase 2 : Backend**
- [ ] Exécuter migration SQL (`add_translation_columns.sql`)
- [ ] Exécuter script de migration des données (`migrate_to_translations.py`)
- [ ] Mettre à jour services existants pour utiliser les nouvelles requêtes
- [ ] Mettre à jour endpoints API avec Accept-Language header
- [ ] Mettre à jour handlers Starlette avec Accept-Language

### **Phase 3 : Frontend**
- [ ] Mettre à jour hooks pour envoyer Accept-Language
- [ ] Mettre à jour API client pour headers automatiques
- [ ] Tester changement de langue avec données traduites

### **Phase 4 : Traductions**
- [ ] Traduire exercices existants en anglais
- [ ] Traduire défis existants en anglais
- [ ] Traduire badges existants en anglais
- [ ] Créer interface admin pour gérer traductions (optionnel)

---

## 🚀 **PROCHAINES ÉTAPES**

1. **Créer la migration SQL** pour ajouter les colonnes JSONB
2. **Implémenter le helper de traduction** dans le backend
3. **Mettre à jour les modèles** avec méthodes de traduction
4. **Créer le script de migration** des données existantes
5. **Tester** avec quelques exercices traduits

---

**Prêt à démarrer l'implémentation !** 🎯


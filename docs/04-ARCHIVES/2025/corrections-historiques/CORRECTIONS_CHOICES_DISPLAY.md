# Correction de l'affichage des choix multiples dans les exercices

**Date:** 2025-11-17  
**Statut:** ✅ Résolu

## 🔍 Problème identifié

Les exercices affichaient la réponse correcte mais **aucun champ de saisie ni boutons de choix multiples** n'étaient visibles pour l'utilisateur.

## 🐛 Cause racine

Le problème était dans la **sérialisation des données côté backend** :

1. **Données stockées correctement** : Le champ `choices` dans PostgreSQL contenait bien les choix multiples au format JSON :
   ```json
   ["5", "3", "2", "4"]
   ```

2. **Requête SQL problématique** : La requête SQL dans `app/db/queries_translations.py` essayait de récupérer les choix depuis `choices_translations` :
   ```sql
   CASE 
       WHEN choices_translations->%s IS NOT NULL THEN (choices_translations->%s)::jsonb
       WHEN choices_translations->'fr' IS NOT NULL THEN (choices_translations->'fr')::jsonb
       ELSE COALESCE(choices::jsonb, '[]'::jsonb)
   END::jsonb as choices
   ```

3. **Problème** : `choices_translations` contenait `{'fr': None}`, ce qui faisait que la condition `choices_translations->'fr' IS NOT NULL` était **vraie** (la clé existe), mais la valeur était `null`, donc l'API retournait `"choices": null` au lieu d'utiliser le fallback sur le champ `choices`.

4. **Impact frontend** : Le composant `ExerciseSolver.tsx` vérifiait :
   ```typescript
   const choices = exercise.choices && exercise.choices.length > 0 ? exercise.choices : [];
   ```
   Avec `choices = null`, le tableau était vide, donc aucun bouton ne s'affichait.

## ✅ Solution appliquée

**Script de correction** : `scripts/fix_choices_translations.py`

Mise à jour de tous les exercices pour copier les choix depuis `choices` vers `choices_translations` :

```sql
UPDATE exercises
SET choices_translations = ('{"fr": ' || choices::text || '}')::jsonb
WHERE choices IS NOT NULL
```

**Résultat** : 50 exercices mis à jour

**Vérification** :
```python
# Avant
choices_translations: {'fr': None}
# API retournait : "choices": null

# Après
choices_translations: {'fr': ['5', '3', '2', '4']}
# API retourne : "choices": ["5", "3", "2", "4"]
```

## 🧪 Tests effectués

1. **Vérification du type de colonne** : Confirmé que `choices` est bien de type `json` en PostgreSQL
2. **Test du service de traduction** : Vérifié que `get_exercise_by_id_with_locale()` retourne maintenant un tableau pour `choices`
3. **Simulation de réponse API** : Confirmé que `JSONResponse` sérialise correctement les choices en tant que liste JSON

## 📁 Fichiers impliqués

### Backend
- `app/db/queries_translations.py` : Requête SQL pour récupérer les exercices
- `app/utils/json_utils.py` : Fonction `parse_choices_json()` pour parser les choix
- `app/services/exercise_service_translations.py` : Service utilisant `parse_choices_json()`
- `scripts/fix_choices_translations.py` : Script de correction (à conserver pour référence)

### Frontend
- `frontend/types/api.ts` : Interface `Exercise` définissant `choices?: string[] | null`
- `frontend/components/exercises/ExerciseSolver.tsx` : Composant affichant les boutons de choix
- `frontend/components/exercises/ExerciseModal.tsx` : Modal d'exercice avec choix multiples
- `frontend/hooks/useExercise.ts` : Hook récupérant un exercice depuis l'API

## 🔄 Impact sur les autres fonctionnalités

- ✅ Les exercices existants continuent de fonctionner
- ✅ La génération d'exercices AI/standard n'est pas impactée
- ✅ Les traductions restent compatibles
- ✅ Les challenges ne sont pas affectés (champ séparé `visual_data`)

## 📝 Recommandations

1. **À l'avenir**, lors du seeding, toujours remplir `choices_translations` en même temps que `choices` :
   ```python
   choices_json = json.dumps(["choix1", "choix2", "choix3", "choix4"])
   choices_translations_json = json.dumps({"fr": json.loads(choices_json)})
   
   exercise = Exercise(
       # ...
       choices=choices_json,
       choices_translations=choices_translations_json
   )
   ```

2. **Alternative** : Modifier la requête SQL pour gérer le cas `{'fr': None}` plus proprement :
   ```sql
   CASE 
       WHEN choices_translations->'fr' IS NOT NULL 
            AND jsonb_typeof(choices_translations->'fr') = 'array'
       THEN choices_translations->'fr'
       ELSE COALESCE(choices::jsonb, '[]'::jsonb)
   END::jsonb as choices
   ```

## 🎯 Résultat attendu

Les utilisateurs peuvent maintenant :
- ✅ Voir les 4 boutons de choix multiples pour chaque exercice
- ✅ Sélectionner une réponse en cliquant sur un bouton
- ✅ Soumettre leur réponse
- ✅ Voir le feedback visuel (correct/incorrect)

## 🔗 Lié à

- Seeding initial : `scripts/seed_final_with_visual_data.py`
- Issue précédente : Ajout du champ `choices` aux exercices
- Issue précédente : Ajout du champ `visual_data` aux challenges


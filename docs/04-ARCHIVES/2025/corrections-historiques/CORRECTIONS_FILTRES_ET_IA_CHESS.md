# Corrections : Filtres de Challenges et Génération IA (Type Échecs)

**Date** : 18 novembre 2025  
**Problèmes identifiés** :  
1. Les filtres (type de challenge, groupe d'âge) ne fonctionnaient pas sur la page `/challenges`
2. La génération IA créait une séquence au lieu d'un défi échecs

---

## 🔍 Diagnostic

### Problème des Filtres

**Investigation** : Script de vérification de la base de données
```python
# Valeurs dans PostgreSQL
Challenge Types : SEQUENCE, PATTERN, DEDUCTION, SPATIAL (MAJUSCULES)
Age Groups : GROUP_10_12, GROUP_13_15, ALL_AGES (MAJUSCULES avec préfixe)

# Valeurs envoyées par le frontend
challenge_type: 'sequence', 'pattern', 'chess' (minuscules)
age_group: '10-12', '13-15', 'all' (minuscules sans préfixe)
```

**Cause racine** :  
Les requêtes SQL font une comparaison stricte `WHERE challenge_type = %s` sans normalisation. Les valeurs du frontend (minuscules) ne correspondent jamais aux valeurs PostgreSQL (majuscules) → **filtres silencieusement ignorés**.

### Problème de la Génération IA

**Ligne 474** de `server/handlers/challenge_handlers.py` :
```python
valid_types = ['sequence', 'pattern', ..., 'deduction']  # ❌ 'chess' manquant
if challenge_type not in valid_types:
    challenge_type = 'sequence'  # Remplacé par défaut
```

Si l'utilisateur choisit "Échecs" (`chess`), le type n'est pas dans la liste validée → remplacé par `'sequence'`.

---

## ✅ Solutions Appliquées

### 1. Normalisation des Filtres (Backend)

**Fichier** : `server/handlers/challenge_handlers.py`

**Nouvelle fonction** : `normalize_challenge_type_for_db()`
```python
def normalize_challenge_type_for_db(challenge_type_raw: str) -> str:
    """
    Normalise un type de challenge vers les valeurs PostgreSQL valides (MAJUSCULES).
    
    Args:
        challenge_type_raw: 'sequence', 'chess', etc. (minuscules)
    
    Returns:
        'SEQUENCE', 'CHESS', etc. (majuscules) ou None si invalide
    """
    if not challenge_type_raw:
        return None
    
    normalized = challenge_type_raw.upper().strip()
    valid_types = ['SEQUENCE', 'PATTERN', 'VISUAL', 'SPATIAL', 'PUZZLE', 'GRAPH', 
                   'RIDDLE', 'DEDUCTION', 'CHESS', 'CODING', 'PROBABILITY', 'CUSTOM']
    
    if normalized in valid_types:
        return normalized
    
    logger.warning(f"Type invalide '{challenge_type_raw}', filtre ignoré")
    return None
```

**Fonction modifiée** : `normalize_age_group_for_db()`
```python
# Changement du comportement par défaut
# Avant : return 'GROUP_10_12'  (toujours une valeur)
# Après  : return None          (ignore le filtre si invalide)
```

**Application dans** `get_challenges_list()` :
```python
# Récupérer les valeurs brutes du frontend
challenge_type_raw = request.query_params.get('challenge_type')  # 'sequence'
age_group_raw = request.query_params.get('age_group')            # '10-12'

# Normaliser AVANT de passer aux requêtes SQL
challenge_type = normalize_challenge_type_for_db(challenge_type_raw)  # 'SEQUENCE'
age_group = normalize_age_group_for_db(age_group_raw)                # 'GROUP_10_12'

# Passer les valeurs normalisées
challenges_list = list_challenges_with_locale(
    locale=locale,
    challenge_type=challenge_type,  # ✅ Correspond maintenant à PostgreSQL
    age_group=age_group,            # ✅ Correspond maintenant à PostgreSQL
    search=search,
    limit=limit,
    offset=skip
)
```

### 2. Types de Challenge Manquants pour l'IA

**Fichier** : `server/handlers/challenge_handlers.py`  
**Ligne 474** :

```python
# Avant
valid_types = ['sequence', 'pattern', ..., 'deduction']  # 8 types

# Après
valid_types = ['sequence', 'pattern', 'visual', 'spatial', 'puzzle', 'graph', 
               'riddle', 'deduction', 'chess', 'coding', 'probability', 'custom']  # 12 types
```

**Ajout de logging** :
```python
if challenge_type not in valid_types:
    logger.warning(f"Type invalide: {challenge_type_raw}, utilisation de 'sequence' par défaut")
    challenge_type = 'sequence'
```

---

## 📊 Impact

### Avant

| Action | Frontend envoie | Backend reçoit | SQL compare | Résultat |
|--------|----------------|----------------|-------------|----------|
| Filtrer "Séquence" | `'sequence'` | `'sequence'` | `WHERE challenge_type = 'sequence'` | ❌ 0 résultat |
| Filtrer "10-12 ans" | `'10-12'` | `'10-12'` | `WHERE age_group = '10-12'` | ❌ 0 résultat |
| Générer IA "Échecs" | `'chess'` | `'chess'` | Non reconnu → `'sequence'` | ❌ Séquence créée |

### Après

| Action | Frontend envoie | Backend normalise | SQL compare | Résultat |
|--------|----------------|-------------------|-------------|----------|
| Filtrer "Séquence" | `'sequence'` | `'SEQUENCE'` | `WHERE challenge_type = 'SEQUENCE'` | ✅ Résultats corrects |
| Filtrer "10-12 ans" | `'10-12'` | `'GROUP_10_12'` | `WHERE age_group = 'GROUP_10_12'` | ✅ Résultats corrects |
| Générer IA "Échecs" | `'chess'` | `'chess'` | Reconnu et généré | ✅ Défi échecs créé |

---

## 🧪 Validation

### Tests manuels recommandés

1. **Filtres de challenges** :
   ```
   - Aller sur /challenges
   - Appliquer filtre "Type" : Séquence, Pattern, Échecs, etc.
   - Vérifier que les résultats correspondent au type choisi
   - Appliquer filtre "Groupe d'âge" : 10-12 ans, 13-15 ans, Tous âges
   - Vérifier que les résultats correspondent au groupe d'âge
   - Combiner les deux filtres
   ```

2. **Génération IA** :
   ```
   - Aller sur /challenges
   - Ouvrir le générateur IA
   - Choisir "Type" : Échecs
   - Générer
   - Vérifier que le défi créé est bien de type "Échecs" et pas "Séquence"
   ```

3. **Recherche textuelle** :
   ```
   - Aller sur /challenges
   - Utiliser la barre de recherche
   - Vérifier que la recherche fonctionne (non affectée par ces changements)
   ```

### Logs à vérifier

Après déploiement, vérifier les logs pour :
```
API - Paramètres reçus: challenge_type_raw=sequence, challenge_type_normalized=SEQUENCE, age_group_raw=10-12, age_group_normalized=GROUP_10_12
```

Si un filtre invalide est envoyé :
```
WARNING: Type de challenge invalide pour filtre: 'invalid_type', filtre ignoré
```

---

## 📝 Notes Techniques

### Pourquoi Majuscules dans PostgreSQL ?

Les enum PostgreSQL sont définis en majuscules :
```sql
CREATE TYPE logicchallengetype AS ENUM ('SEQUENCE', 'PATTERN', 'CHESS', ...);
CREATE TYPE agegroup AS ENUM ('GROUP_10_12', 'GROUP_13_15', 'ALL_AGES');
```

### Pourquoi Minuscules dans le Frontend ?

Conventions JavaScript/TypeScript :
```typescript
const CHALLENGE_TYPES = {
  SEQUENCE: 'sequence',  // Valeurs en minuscules (snake_case ou kebab-case)
  CHESS: 'chess',
} as const;
```

### Architecture de Normalisation

```
Frontend (minuscules) 
   ↓
   → Handler (normalisation MAJUSCULES)
   ↓
   → Service (passe les valeurs normalisées)
   ↓
   → Requête SQL (WHERE type = 'SEQUENCE')
   ↓
PostgreSQL (compare avec enum MAJUSCULES) ✅
```

---

## 🚀 Déploiement

**Commandes** :
```bash
git add server/handlers/challenge_handlers.py CORRECTIONS_FILTRES_ET_IA_CHESS.md
git commit -m "fix: normalisation des filtres challenges et ajout types IA manquants

- Ajout fonction normalize_challenge_type_for_db() pour convertir minuscules → MAJUSCULES
- Modification normalize_age_group_for_db() pour retourner None si invalide (filtres)
- Application de la normalisation dans get_challenges_list() avant requêtes SQL
- Ajout types manquants pour génération IA : chess, coding, probability, custom
- Les filtres fonctionnent maintenant correctement (SEQUENCE, GROUP_10_12, etc.)
- La génération IA respecte le type choisi (échecs génère un défi échecs)"

git push origin master
```

**Service à redémarrer** : Backend (Python/FastAPI)  
**Temps d'indisponibilité** : ~30 secondes

---

## ✅ Checklist de Validation Post-Déploiement

- [ ] Les filtres par type de challenge retournent des résultats
- [ ] Les filtres par groupe d'âge retournent des résultats
- [ ] La combinaison des filtres fonctionne
- [ ] La recherche textuelle fonctionne
- [ ] La génération IA d'un défi "Échecs" crée bien un défi échecs
- [ ] La génération IA d'un défi "Probabilité" fonctionne
- [ ] La génération IA d'un défi "Codage" fonctionne
- [ ] Les logs montrent les valeurs normalisées correctement
- [ ] Aucune erreur 500 dans les logs backend

---

**Responsable** : Assistant IA  
**Validé par** : [À compléter après tests]


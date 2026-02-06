# Plan de Migration - Index Manquants sur `exercises`

> **Statut : ✅ APPLIQUÉ** - Migration déployée en production le 06/02/2026

**Date :** 2026-02-06  
**Migration :** `20260206_1600_add_exercises_missing_indexes.py`  
**Impact :** Performance +15-25% sur requêtes de listage exercices

---

## 1. Index à créer

| Index | Type | Colonnes | Justification |
|-------|------|----------|---------------|
| `ix_exercises_age_group` | Simple | `age_group` | Filtrage fréquent par groupe d'âge |
| `ix_exercises_is_archived` | Simple | `is_archived` | Filtrage très fréquent (`== False`) |
| `ix_exercises_archived_age` | Composite | `(is_archived, age_group)` | Requête combinée fréquente |

---

## 2. Analyse d'impact

### Bénéfices
- **Requêtes accélérées** : `GET /api/exercises?age_group=6-8` (+30-50%)
- **Dashboard plus rapide** : Comptages par groupe d'âge
- **Listage optimisé** : Filtrage `is_archived = FALSE` (90%+ des requêtes)

### Risques (faibles)
- **Espace disque** : ~1-5 MB supplémentaire (négligeable)
- **Écritures légèrement plus lentes** : INSERT/UPDATE +2-5ms (négligeable)
- **Temps de création** : ~1-5 secondes sur table de 1000+ lignes

---

## 3. Procédure de déploiement

### Pré-déploiement (dev local)
```bash
# 1. Vérifier l'état actuel
python scripts/verify_indexes.py

# 2. Appliquer la migration
alembic upgrade head

# 3. Vérifier les nouveaux index
python scripts/verify_indexes.py
```

### Déploiement production (Render)
```bash
# La migration s'applique automatiquement via Alembic
# OU manuellement via : alembic upgrade head
```

---

## 4. Plan de Rollback (CRITIQUE)

### Commande de rollback
```bash
# Annuler UNIQUEMENT cette migration
alembic downgrade 20260206_user_achv_idx

# OU via révision spécifique
alembic downgrade -1
```

### Ce que le rollback fait
1. Supprime `ix_exercises_archived_age` (composite)
2. Supprime `ix_exercises_is_archived` (simple)
3. Supprime `ix_exercises_age_group` (simple)

### Quand effectuer un rollback
- Erreurs lors de la migration (ex: index déjà existant)
- Dégradation inattendue des performances d'écriture
- Conflits avec d'autres migrations

### Vérification post-rollback
```bash
python scripts/verify_indexes.py
# Les 3 nouveaux index ne doivent plus apparaître
```

---

## 5. Vérification post-migration

### Script de vérification
```sql
-- Vérifier la présence des nouveaux index
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'exercises' 
  AND indexname IN (
    'ix_exercises_age_group',
    'ix_exercises_is_archived', 
    'ix_exercises_archived_age'
  );
```

### Résultat attendu
```
         indexname          |                           indexdef
----------------------------+--------------------------------------------------------------
 ix_exercises_age_group     | CREATE INDEX ix_exercises_age_group ON exercises (age_group)
 ix_exercises_is_archived   | CREATE INDEX ix_exercises_is_archived ON exercises (is_archived)
 ix_exercises_archived_age  | CREATE INDEX ix_exercises_archived_age ON exercises (is_archived, age_group)
```

---

## 6. Monitoring post-déploiement

### Métriques à surveiller
1. **Temps de réponse** : `GET /api/exercises` (doit diminuer)
2. **Logs slow queries** : Requêtes >100ms sur `exercises`
3. **CPU usage** : Ne doit pas augmenter significativement

### Période de surveillance
- **24h** après déploiement : Monitoring actif
- **7j** : Validation définitive

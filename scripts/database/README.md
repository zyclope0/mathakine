# 🗄️ Scripts Base de Données Mathakine

Ce dossier contient tous les scripts utilitaires pour la gestion et l'évolution de la base de données Mathakine.

## 📁 **Scripts Disponibles**

### **Scripts d'Évolution BDD**

#### **`validate_schema_migrations.py`**
- **Fonction** : Validation complète du schéma après migration
- **Usage** : `python scripts/database/validate_schema_migrations.py`
- **Tests** :
  - Vérification des nouvelles colonnes
  - Validation des nouvelles tables
  - Test de création d'objets
  - Benchmark de performance
  - Vérification des index

#### **`create_user_extensions_migration.py`**
- **Fonction** : Génération automatique des migrations Alembic
- **Usage** : `python scripts/database/create_user_extensions_migration.py`
- **Génère** :
  - Migration extensions table users
  - Migration nouvelles tables
  - Migration extensions table exercises
  - Script de validation

#### **`update_user_model.py`**
- **Fonction** : Génération des modèles SQLAlchemy étendus
- **Usage** : `python scripts/database/update_user_model.py`
- **Crée** :
  - `app/models/user_extended.py`
  - `app/models/user_session.py`
  - `app/models/achievement.py`
  - `app/models/notification.py`

## 🚀 **Workflow d'Évolution BDD**

### **Étape 1 : Préparation**
```bash
# 1. Backup de la base de données
pg_dump mathakine_prod > backup_$(date +%Y%m%d).sql

# 2. Créer environnement de test
createdb mathakine_test
psql mathakine_test < backup_$(date +%Y%m%d).sql
```

### **Étape 2 : Génération**
```bash
# 1. Générer les modèles étendus
python scripts/database/update_user_model.py

# 2. Générer les migrations
python scripts/database/create_user_extensions_migration.py
```

### **Étape 3 : Application**
```bash
# 1. Appliquer les migrations (TEST SEULEMENT)
export DATABASE_URL="postgresql://user:pass@localhost/mathakine_test"
alembic upgrade head

# 2. Valider le schéma
python scripts/database/validate_schema_migrations.py
```

### **Étape 4 : Production**
```bash
# Seulement après validation complète en test
export DATABASE_URL="postgresql://user:pass@localhost/mathakine_prod"
alembic upgrade head
```

## 📋 **Prérequis**

### **Dépendances Python**
- SQLAlchemy 2.0+
- Alembic
- psycopg2-binary (PostgreSQL)
- Pydantic 2.0+

### **Variables d'Environnement**
```bash
DATABASE_URL="postgresql://user:password@host:port/database"
```

### **Permissions Base de Données**
- CREATE TABLE
- ALTER TABLE
- CREATE INDEX
- INSERT/UPDATE/DELETE

## ⚠️ **Sécurité et Bonnes Pratiques**

### **Avant Toute Migration**
1. ✅ **Backup complet** de la base de données
2. ✅ **Test sur environnement** de développement
3. ✅ **Validation des scripts** de migration
4. ✅ **Plan de rollback** préparé

### **Pendant la Migration**
1. ✅ **Mode maintenance** activé
2. ✅ **Monitoring** des performances
3. ✅ **Logs détaillés** activés
4. ✅ **Validation** étape par étape

### **Après la Migration**
1. ✅ **Tests fonctionnels** complets
2. ✅ **Vérification des performances**
3. ✅ **Validation des données**
4. ✅ **Documentation** mise à jour

## 🔍 **Dépannage**

### **Erreurs Communes**

#### **Erreur : "Table already exists"**
```bash
# Vérifier l'état des migrations
alembic current
alembic history

# Marquer comme appliquée si nécessaire
alembic stamp head
```

#### **Erreur : "Permission denied"**
```bash
# Vérifier les permissions utilisateur
GRANT CREATE ON DATABASE mathakine TO username;
GRANT USAGE ON SCHEMA public TO username;
```

#### **Erreur : "Column already exists"**
```bash
# Vérifier le schéma actuel
\d+ users  # Dans psql
```

### **Validation Manuelle**

#### **Vérifier les Nouvelles Colonnes**
```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('avatar_url', 'jedi_rank', 'total_points');
```

#### **Vérifier les Nouvelles Tables**
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('user_sessions', 'achievements', 'notifications');
```

#### **Vérifier les Index**
```sql
SELECT indexname, tablename 
FROM pg_indexes 
WHERE tablename IN ('users', 'user_sessions', 'achievements')
AND indexname LIKE 'idx_%';
```

## 📊 **Métriques de Validation**

### **Performance Attendue**
- **Temps de migration** : < 5 minutes pour Phase 1
- **Temps de validation** : < 30 secondes
- **Performance post-migration** : < 200ms (95e percentile)

### **Critères de Succès**
- ✅ Toutes les nouvelles colonnes créées
- ✅ Toutes les nouvelles tables créées
- ✅ Tous les index de performance créés
- ✅ Contraintes de clés étrangères fonctionnelles
- ✅ Tests de création d'objets réussis

## 📞 **Support**

### **En Cas de Problème**
1. **Consulter les logs** : `logs/database_migration.log`
2. **Vérifier la documentation** : `docs/architecture/database-evolution.md`
3. **Rollback si nécessaire** : Restaurer depuis backup
4. **Contacter l'équipe** : Issues GitHub ou support direct

---

**Scripts de base de données pour l'évolution Mathakine** 🗄️⚡ 
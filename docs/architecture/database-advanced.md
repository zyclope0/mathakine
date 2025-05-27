# 🗄️ Guide Avancé Base de Données - Mathakine

**Documentation complète du système de base de données** incluant migrations, optimisations et procédures avancées.

## 🎯 Vue d'Ensemble

Mathakine supporte deux systèmes de gestion de base de données avec une architecture flexible permettant de basculer facilement entre les environnements.

### Systèmes Supportés
- **SQLite** : Développement local et tests
- **PostgreSQL** : Production et environnements avancés

## 🏗️ Architecture de Base de Données

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │     │                   │
│  Modèles SQLAlchemy  ◄──┼──►  Base de données  ◄──┼──►  Migrations Alembic │
│                   │     │                   │     │                   │
└───────────────────┘     └───────────────────┘     └───────────────────┘
```

### Tables Principales
- **users** : Utilisateurs de l'application
- **exercises** : Exercices mathématiques
- **attempts** : Tentatives de résolution
- **progress** : Progression des utilisateurs
- **logic_challenges** : Défis logiques

### Tables Héritées (Protégées)
- **results** : Résultats d'exercices (héritage)
- **statistics** : Statistiques par session (héritage)
- **user_stats** : Statistiques utilisateur (héritage)
- **schema_version** : Version du schéma (héritage)

## 🚀 Migration vers PostgreSQL

### Pourquoi Migrer vers PostgreSQL ?

#### Avantages par rapport à SQLite

**1. Performances Accrues**
- Meilleure gestion des requêtes complexes
- Optimisation pour les grands volumes de données
- Index plus sophistiqués et parallélisation

**2. Concurrence**
- Support des accès simultanés multiples
- Verrouillage au niveau des lignes (non de la base entière)
- Idéal pour applications multi-utilisateurs

**3. Scalabilité**
- Capacité à gérer de grands volumes de données
- Support de la réplication et du clustering
- Performances maintenues avec la croissance

**4. Fonctionnalités Avancées**
- Transactions ACID complètes
- Contraintes d'intégrité avancées
- Types de données riches (JSON, Arrays, etc.)
- Procédures stockées et triggers

### Prérequis Techniques

#### Logiciels Requis
- **PostgreSQL 12+** (version 17 recommandée)
- **Python 3.8+** avec bibliothèques :
  - `psycopg2` ou `psycopg2-binary`
  - `python-dotenv`
  - `sqlalchemy[postgresql]`

#### Configuration Système
- **Accès administrateur** à PostgreSQL
- **Mémoire** : 4GB+ recommandés
- **Espace disque** : 2GB+ libres

### Processus de Migration Détaillé

#### 1. Configuration de l'Environnement

**Fichier `.env`** :
```env
# Configuration PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_mot_de_passe_securise
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mathakine_production

# URL de connexion complète
DATABASE_URL=postgresql://postgres:password@localhost:5432/mathakine_production
```

#### 2. Exécution de la Migration

**Windows** :
```bash
scripts/migrate_to_postgres.bat
```

**Linux/MacOS** :
```bash
python scripts/migrate_to_postgres.py
```

#### 3. Opérations Effectuées

Le script de migration effectue automatiquement :

1. **Connexion SQLite** : Lecture de la base existante
2. **Création PostgreSQL** : Base de données si inexistante
3. **Conversion schéma** : Adaptation des types de données
4. **Migration données** : Transfert avec conversion des types
5. **Vérification intégrité** : Validation des données migrées
6. **Index et contraintes** : Recréation optimisée

#### 4. Basculement entre Bases

**Utilitaire de basculement** :
```bash
# Basculer vers PostgreSQL
python scripts/toggle_database.py postgres

# Basculer vers SQLite
python scripts/toggle_database.py sqlite

# Vérifier la configuration actuelle
python scripts/toggle_database.py status
```

## ☁️ Déploiement sur Render

### Configuration Base PostgreSQL

#### 1. Création sur Render
1. **Dashboard Render** → Nouvelle base PostgreSQL
2. **Configuration** :
   - Nom : `mathakine-production`
   - Région : Europe (Frankfurt) recommandée
   - Plan : Starter (gratuit) ou Professional

#### 2. Récupération des Informations
Render fournit automatiquement :
- **URL interne** : Pour connexions depuis services Render
- **URL externe** : Pour connexions externes
- **Paramètres individuels** : Host, port, database, user, password

#### 3. Migration vers Render

**Script de migration** :
```bash
python scripts/migrate_to_render.py
```

**Configuration service web** :
```env
# Variable d'environnement Render
DATABASE_URL=postgresql://user:password@host:port/database
```

### Optimisations Render

#### Configuration Recommandée
```python
# app/core/config.py - Configuration optimisée Render
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "echo": False  # Désactiver en production
}
```

## 🔧 Différences de Types de Données

### Mapping SQLite → PostgreSQL

| SQLite | PostgreSQL | Notes |
|--------|------------|-------|
| `INTEGER` | `INTEGER` | Compatible direct |
| `REAL` | `DOUBLE PRECISION` | Précision améliorée |
| `TEXT` | `TEXT` ou `VARCHAR` | Longueur illimitée |
| `BLOB` | `BYTEA` | Données binaires |
| `INTEGER (0/1)` | `BOOLEAN` | Pour colonnes `is_*`, `has_*` |
| `JSON (text)` | `JSON` ou `JSONB` | Type natif PostgreSQL |

### Gestion des Énumérations

#### Problème SQLite vs PostgreSQL
```python
# SQLite : Stockage en string
exercise_type = "addition"

# PostgreSQL : Peut nécessiter adaptation
exercise_type = "ADDITION"  # Selon configuration
```

#### Solution avec Adaptateur
```python
from app.utils.db_helpers import adapt_enum_for_db

# Adaptation automatique selon la base
adapted_value = adapt_enum_for_db("ExerciseType", "addition", db)
# SQLite : "addition"
# PostgreSQL : "ADDITION" (selon mapping)
```

## ⚡ Optimisations PostgreSQL

### Script d'Optimisation Automatique

```bash
python scripts/optimize_postgres.py
```

#### Opérations Effectuées

**1. Création d'Index**
```sql
-- Index sur colonnes fréquemment utilisées
CREATE INDEX IF NOT EXISTS idx_exercises_type ON exercises(exercise_type);
CREATE INDEX IF NOT EXISTS idx_exercises_difficulty ON exercises(difficulty);
CREATE INDEX IF NOT EXISTS idx_attempts_user_id ON attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_attempts_exercise_id ON attempts(exercise_id);
CREATE INDEX IF NOT EXISTS idx_attempts_created_at ON attempts(created_at);
```

**2. Maintenance de Base**
```sql
-- Analyse et optimisation
VACUUM ANALYZE exercises;
VACUUM ANALYZE attempts;
VACUUM ANALYZE users;
VACUUM ANALYZE progress;
```

**3. Statistiques de Performance**
```sql
-- Rapport d'état des tables
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables;
```

### Configuration Avancée PostgreSQL

#### Paramètres de Performance
```sql
-- Configuration recommandée pour Mathakine
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

#### Monitoring des Requêtes
```sql
-- Activer le logging des requêtes lentes
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1 seconde
ALTER SYSTEM SET log_statement = 'mod';  -- INSERT, UPDATE, DELETE
```

## 🔄 Gestion des Migrations avec Alembic

### Configuration Avancée

#### Structure des Migrations
```
migrations/
├── env.py              # Configuration personnalisée
├── script.py.mako      # Template des migrations
├── alembic.ini         # Configuration Alembic
└── versions/           # Versions des migrations
    ├── initial_snapshot.py
    └── 20250513_baseline_migration.py
```

#### Protection des Tables Héritées

**Fichier `migrations/env.py`** :
```python
def include_object(object, name, type_, reflected, compare_to):
    """
    Protège les tables héritées contre la suppression accidentelle
    """
    # Tables héritées à préserver
    PROTECTED_TABLES = ["results", "statistics", "user_stats", "schema_version"]
    
    if type_ == "table" and name in PROTECTED_TABLES:
        # Ne pas inclure dans les migrations auto-générées
        return False
    
    return True
```

### Commandes Alembic Avancées

#### Gestion des Versions
```bash
# Afficher l'historique complet
alembic history --verbose

# Afficher les différences avec la base
alembic show <revision_id>

# Créer une migration vide (pour modifications manuelles)
alembic revision -m "Custom migration"

# Merger plusieurs branches de migration
alembic merge -m "Merge branches" <rev1> <rev2>
```

#### Migrations Conditionnelles
```python
# Dans une migration - Exemple de migration conditionnelle
def upgrade():
    # Vérifier si la colonne existe déjà
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns('exercises')]
    
    if 'new_column' not in columns:
        op.add_column('exercises', sa.Column('new_column', sa.String(255)))
```

### Scripts Utilitaires Avancés

#### Génération Sécurisée de Migrations
```bash
python scripts/generate_migration.py --message "Add new feature"
```

**Fonctionnalités** :
- Vérification des conflits potentiels
- Sauvegarde automatique avant génération
- Validation de la migration générée
- Suggestions d'amélioration

#### Migration avec Sauvegarde
```bash
python scripts/safe_migrate.py
```

**Processus** :
1. Sauvegarde complète de la base
2. Application des migrations
3. Vérification de l'intégrité
4. Restauration automatique si échec

## 🔍 Monitoring et Maintenance

### Métriques de Performance

#### Requêtes de Monitoring
```sql
-- Top 10 des requêtes les plus lentes
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;

-- Utilisation des index
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

#### Surveillance de l'Espace Disque
```sql
-- Taille des tables
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
```

### Maintenance Automatisée

#### Script de Maintenance Quotidienne
```bash
#!/bin/bash
# scripts/daily_maintenance.sh

# Nettoyage des logs anciens
python scripts/cleanup_logs.py --days 30

# Optimisation base de données
python scripts/optimize_postgres.py

# Sauvegarde
python scripts/backup_database.py

# Rapport de santé
python scripts/health_check.py
```

#### Sauvegarde Automatique
```python
# scripts/backup_database.py
import subprocess
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_mathakine_{timestamp}.sql"
    
    cmd = [
        "pg_dump",
        "--host", os.getenv("POSTGRES_HOST"),
        "--port", os.getenv("POSTGRES_PORT"),
        "--username", os.getenv("POSTGRES_USER"),
        "--dbname", os.getenv("POSTGRES_DB"),
        "--file", backup_file,
        "--verbose"
    ]
    
    subprocess.run(cmd, check=True)
    logger.info(f"Sauvegarde créée : {backup_file}")
```

## 🚨 Résolution de Problèmes

### Problèmes Courants

#### 1. Erreur de Connexion PostgreSQL
```
FATAL: password authentication failed for user "postgres"
```

**Solutions** :
- Vérifier les variables d'environnement
- Tester la connexion : `psql -h localhost -U postgres -d mathakine`
- Réinitialiser le mot de passe PostgreSQL

#### 2. Erreur de Migration Alembic
```
Target database is not up to date
```

**Solutions** :
```bash
# Marquer comme à jour
alembic stamp head

# Ou forcer la migration
alembic upgrade head --sql > migration.sql
# Réviser le SQL avant application
```

#### 3. Performance Dégradée
**Diagnostic** :
```sql
-- Identifier les requêtes problématiques
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
WHERE mean_time > 1000  -- Plus de 1 seconde
ORDER BY mean_time DESC;
```

**Solutions** :
- Ajouter des index appropriés
- Optimiser les requêtes ORM
- Augmenter les paramètres de cache

### Outils de Diagnostic

#### Script de Santé Globale
```bash
python scripts/health_check.py --full
```

**Vérifications** :
- Connexion base de données
- État des migrations
- Performance des requêtes
- Utilisation de l'espace disque
- Intégrité des données

---

**Base de données optimisée pour la performance et la fiabilité** 🗄️⚡ 
# Schéma de Base de Données - Mathakine

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture de Base de Données](#architecture-de-base-de-données)
3. [Modèles et Relations](#modèles-et-relations)
4. [Schéma Détaillé des Tables](#schéma-détaillé-des-tables)
5. [Énumérations](#énumérations)
6. [Migrations](#migrations)
7. [Optimisations](#optimisations)
8. [Sécurité](#sécurité)

## Vue d'ensemble

Mathakine utilise une architecture de base de données relationnelle avec PostgreSQL en production et SQLite pour le développement. Le schéma est conçu pour supporter une plateforme éducative scalable avec gestion des utilisateurs, exercices, progression et défis logiques.

### Caractéristiques Principales

- **ORM** : SQLAlchemy 2.0 avec support des fonctionnalités modernes
- **Migrations** : Alembic pour la gestion versionnée du schéma
- **Cascade** : Suppression en cascade pour maintenir l'intégrité référentielle
- **JSON** : Support natif pour les données semi-structurées
- **Énumérations** : Types énumérés pour la cohérence des données

## Architecture de Base de Données

### Diagramme ER Simplifié

```mermaid
erDiagram
    USERS ||--o{ EXERCISES : creates
    USERS ||--o{ ATTEMPTS : makes
    USERS ||--o{ PROGRESS : has
    USERS ||--o{ LOGIC_CHALLENGES : creates
    USERS ||--o{ LOGIC_CHALLENGE_ATTEMPTS : attempts
    USERS ||--o{ RECOMMENDATIONS : receives
    
    EXERCISES ||--o{ ATTEMPTS : has
    LOGIC_CHALLENGES ||--o{ LOGIC_CHALLENGE_ATTEMPTS : has
    
    USERS {
        int id PK
        string username UK
        string email UK
        string hashed_password
        enum role
        boolean is_active
        json accessibility_settings
    }
    
    EXERCISES {
        int id PK
        string title
        int creator_id FK
        enum exercise_type
        enum difficulty
        text question
        string correct_answer
        json choices
        boolean is_archived
    }
    
    ATTEMPTS {
        int id PK
        int user_id FK
        int exercise_id FK
        string user_answer
        boolean is_correct
        float time_spent
    }
```

## Modèles et Relations

### 1. User (Utilisateur)

**Rôle** : Stocke les informations des utilisateurs avec leurs préférences et paramètres d'accessibilité.

**Relations** :
- `1:N` avec Exercise (créateur)
- `1:N` avec Attempt
- `1:N` avec Progress
- `1:N` avec LogicChallenge (créateur)
- `1:N` avec LogicChallengeAttempt
- `1:N` avec Recommendation

### 2. Exercise (Exercice)

**Rôle** : Contient les exercices mathématiques avec métadonnées enrichies.

**Relations** :
- `N:1` avec User (créateur)
- `1:N` avec Attempt

### 3. Attempt (Tentative)

**Rôle** : Enregistre chaque tentative de résolution d'exercice.

**Relations** :
- `N:1` avec User
- `N:1` avec Exercise

### 4. Progress (Progression)

**Rôle** : Agrège les statistiques de progression par type et difficulté.

**Relations** :
- `N:1` avec User

### 5. LogicChallenge (Défi Logique)

**Rôle** : Défis avancés pour les groupes d'âge plus élevés.

**Relations** :
- `N:1` avec User (créateur)
- `1:N` avec LogicChallengeAttempt

## Schéma Détaillé des Tables

### Table: users

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'padawan' CHECK (role IN ('padawan', 'maitre', 'gardien', 'archiviste', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Informations pédagogiques
    grade_level INTEGER CHECK (grade_level BETWEEN 1 AND 12),
    learning_style VARCHAR(50),
    preferred_difficulty VARCHAR(50),
    
    -- Préférences interface
    preferred_theme VARCHAR(50),
    accessibility_settings JSON,
    
    -- Index
    INDEX idx_users_email (email),
    INDEX idx_users_username (username),
    INDEX idx_users_active (is_active)
);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE
    ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Table: exercises

```sql
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    creator_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- Type et difficulté
    exercise_type VARCHAR(20) NOT NULL CHECK (exercise_type IN (
        'addition', 'soustraction', 'multiplication', 'division',
        'fractions', 'geometrie', 'texte', 'mixte', 'divers'
    )),
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN (
        'initie', 'padawan', 'chevalier', 'maitre'
    )),
    
    -- Métadonnées
    tags VARCHAR(255),
    age_group VARCHAR(10) CHECK (age_group IN ('6-8', '8-10', '10-12', '12-14', '14-16')),
    context_theme VARCHAR(50),
    complexity INTEGER CHECK (complexity BETWEEN 1 AND 5),
    ai_generated BOOLEAN DEFAULT FALSE,
    
    -- Contenu
    question TEXT NOT NULL,
    correct_answer VARCHAR(255) NOT NULL,
    choices JSON, -- Format: ["option1", "option2", "option3", "option4"]
    explanation TEXT,
    hint TEXT,
    
    -- Médias
    image_url VARCHAR(255),
    audio_url VARCHAR(255),
    
    -- États
    is_active BOOLEAN DEFAULT TRUE,
    is_archived BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_exercises_type (exercise_type),
    INDEX idx_exercises_difficulty (difficulty),
    INDEX idx_exercises_active_archived (is_active, is_archived),
    INDEX idx_exercises_creator (creator_id)
);
```

### Table: attempts

```sql
CREATE TABLE attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    
    -- Données de tentative
    user_answer VARCHAR(255) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_spent REAL, -- En secondes
    attempt_number INTEGER DEFAULT 1,
    hints_used INTEGER DEFAULT 0,
    
    -- Contexte
    device_info VARCHAR(255),
    session_id VARCHAR(255),
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_attempts_user (user_id),
    INDEX idx_attempts_exercise (exercise_id),
    INDEX idx_attempts_user_exercise (user_id, exercise_id),
    INDEX idx_attempts_created (created_at),
    
    -- Contrainte unique pour numéro de tentative
    UNIQUE (user_id, exercise_id, attempt_number)
);
```

### Table: progress

```sql
CREATE TABLE progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_type VARCHAR(255) NOT NULL,
    difficulty VARCHAR(255) NOT NULL,
    
    -- Statistiques
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,
    average_time REAL, -- Temps moyen en secondes
    completion_rate REAL, -- Pourcentage (0-100)
    
    -- Gamification
    streak INTEGER DEFAULT 0,
    highest_streak INTEGER DEFAULT 0,
    mastery_level INTEGER DEFAULT 0, -- 0-5
    awards JSON, -- Badges et récompenses
    
    -- Analyses
    strengths VARCHAR(255),
    areas_to_improve VARCHAR(255),
    recommendations VARCHAR(255),
    
    -- Timestamp
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_progress_user (user_id),
    INDEX idx_progress_type_difficulty (exercise_type, difficulty),
    
    -- Contrainte unique
    UNIQUE (user_id, exercise_type, difficulty)
);
```

### Table: logic_challenges

```sql
CREATE TABLE logic_challenges (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    creator_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    
    -- Type et groupe
    challenge_type VARCHAR(20) NOT NULL CHECK (challenge_type IN (
        'visual', 'abstract', 'pattern', 'word'
    )),
    age_group VARCHAR(10) NOT NULL CHECK (age_group IN (
        '10-11', '12-13', '14-15'
    )),
    
    -- Contenu
    description TEXT NOT NULL,
    visual_data JSON, -- Données pour représentation visuelle
    correct_answer VARCHAR(255) NOT NULL,
    solution_explanation TEXT NOT NULL,
    hints JSON, -- Format: ["hint1", "hint2", "hint3"]
    
    -- Métadonnées
    difficulty_rating REAL CHECK (difficulty_rating BETWEEN 1 AND 5),
    estimated_time_minutes INTEGER,
    success_rate REAL, -- Pourcentage (0-100)
    
    -- Référence
    image_url VARCHAR(255),
    source_reference VARCHAR(255),
    tags VARCHAR(255),
    
    -- Configuration
    is_template BOOLEAN DEFAULT FALSE,
    generation_parameters JSON,
    
    -- États
    is_active BOOLEAN DEFAULT TRUE,
    is_archived BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_logic_challenges_type (challenge_type),
    INDEX idx_logic_challenges_age_group (age_group),
    INDEX idx_logic_challenges_active (is_active)
);
```

### Table: logic_challenge_attempts

```sql
CREATE TABLE logic_challenge_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    challenge_id INTEGER NOT NULL REFERENCES logic_challenges(id) ON DELETE CASCADE,
    
    -- Données de tentative
    user_solution VARCHAR(255) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_spent REAL, -- En secondes
    hints_used JSON, -- Indices utilisés [0, 1, 2]
    
    -- Métadonnées
    difficulty_felt INTEGER CHECK (difficulty_felt BETWEEN 1 AND 5),
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_lc_attempts_user (user_id),
    INDEX idx_lc_attempts_challenge (challenge_id),
    INDEX idx_lc_attempts_user_challenge (user_id, challenge_id)
);
```

### Table: recommendations

```sql
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Type de recommandation
    recommendation_type VARCHAR(50) NOT NULL,
    exercise_type VARCHAR(50),
    difficulty_level VARCHAR(50),
    
    -- Contenu
    title VARCHAR(255) NOT NULL,
    description TEXT,
    reason TEXT,
    
    -- Métadonnées
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    is_viewed BOOLEAN DEFAULT FALSE,
    is_applied BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    viewed_at TIMESTAMP WITH TIME ZONE,
    applied_at TIMESTAMP WITH TIME ZONE,
    
    -- Index
    INDEX idx_recommendations_user (user_id),
    INDEX idx_recommendations_active (is_active),
    INDEX idx_recommendations_priority (priority DESC)
);
```

### Table: settings

```sql
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    category VARCHAR(50),
    is_system BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_settings_key (key),
    INDEX idx_settings_category (category)
);
```

## Énumérations

### UserRole
```python
class UserRole(str, Enum):
    PADAWAN = "padawan"       # Utilisateur standard
    MAITRE = "maitre"         # Enseignant
    GARDIEN = "gardien"       # Modérateur
    ARCHIVISTE = "archiviste" # Administrateur système avec tous les privilèges
```

### ExerciseType
```python
class ExerciseType(str, Enum):
    ADDITION = "addition"
    SOUSTRACTION = "soustraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"
    FRACTIONS = "fractions"
    GEOMETRIE = "geometrie"
    TEXTE = "texte"
    MIXTE = "mixte"
    DIVERS = "divers"
```

### DifficultyLevel
```python
class DifficultyLevel(str, Enum):
    INITIE = "initie"         # 1-10
    PADAWAN = "padawan"       # 10-50
    CHEVALIER = "chevalier"   # 50-100
    MAITRE = "maitre"         # 100-500
```

### LogicChallengeType
```python
class LogicChallengeType(str, Enum):
    VISUAL = "visual"         # Défis visuels
    ABSTRACT = "abstract"     # Raisonnement abstrait
    PATTERN = "pattern"       # Reconnaissance de motifs
    WORD = "word"            # Problèmes verbaux
```

### AgeGroup
```python
class AgeGroup(str, Enum):
    GROUP_10_11 = "10-11"
    GROUP_12_13 = "12-13"
    GROUP_14_15 = "14-15"
```

## Migrations

### Configuration Alembic

```ini
# alembic.ini
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://user:pass@localhost/mathakine

[loggers]
keys = root,sqlalchemy,alembic
```

### Workflow de Migration

1. **Création d'une migration**
   ```bash
   python scripts/generate_migration.py "Add new feature"
   ```

2. **Vérification de la migration**
   ```bash
   alembic show "head"
   ```

3. **Application de la migration**
   ```bash
   alembic upgrade head
   ```

4. **Rollback si nécessaire**
   ```bash
   alembic downgrade -1
   ```

## Optimisations

### Index

Les index sont créés sur :
- Clés étrangères pour les jointures
- Colonnes fréquemment filtrées (type, difficulté, statut)
- Colonnes utilisées dans les clauses WHERE
- Combinaisons de colonnes pour les requêtes complexes

### Partitionnement

Pour les tables volumineuses :
- `attempts` : Partitionnement par date (mensuel)
- `progress` : Partitionnement par user_id (hash)

### Vues Matérialisées

```sql
CREATE MATERIALIZED VIEW user_statistics AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(DISTINCT a.exercise_id) as exercises_attempted,
    COUNT(a.id) as total_attempts,
    AVG(CASE WHEN a.is_correct THEN 1 ELSE 0 END) * 100 as success_rate,
    AVG(a.time_spent) as avg_time_spent
FROM users u
LEFT JOIN attempts a ON u.id = a.user_id
GROUP BY u.id, u.username;

-- Refresh périodique
CREATE INDEX idx_user_statistics_user_id ON user_statistics(user_id);
```

## Sécurité

### Protection des Données

1. **Chiffrement**
   - Mots de passe : Bcrypt avec salt
   - Données sensibles : Chiffrement AES-256
   - Connexions : SSL/TLS obligatoire

2. **Accès**
   - Row Level Security (RLS) pour PostgreSQL
   - Vues restreintes par rôle
   - Audit trail des modifications

3. **Validation**
   - Contraintes CHECK sur les colonnes
   - Triggers de validation
   - Types énumérés pour limiter les valeurs

### Exemple de RLS

```sql
-- Activer RLS sur la table exercises
ALTER TABLE exercises ENABLE ROW LEVEL SECURITY;

-- Politique pour les utilisateurs standards
CREATE POLICY exercises_user_policy ON exercises
    FOR ALL
    TO application_user
    USING (is_active = TRUE AND is_archived = FALSE);

-- Politique pour les créateurs
CREATE POLICY exercises_creator_policy ON exercises
    FOR ALL
    TO application_user
    USING (creator_id = current_user_id() OR is_active = TRUE);
```

## Maintenance

### Sauvegardes

```bash
# Sauvegarde complète
pg_dump -h localhost -U user -d mathakine -f backup_$(date +%Y%m%d).sql

# Sauvegarde incrémentale avec pg_basebackup
pg_basebackup -D /backup/mathakine -Ft -z -P
```

### Monitoring

Métriques surveillées :
- Taille des tables et index
- Performance des requêtes (pg_stat_statements)
- Taux de cache hit
- Connexions actives
- Deadlocks et locks longs

### Optimisation des Requêtes

```sql
-- Analyser les requêtes lentes
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    stddev_time
FROM pg_stat_statements
WHERE mean_time > 100
ORDER BY mean_time DESC
LIMIT 20;
```

---

*Dernière mise à jour : 26 mai 2025* 
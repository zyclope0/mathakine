# 🗄️ ÉVOLUTION TECHNIQUE BASE DE DONNÉES MATHAKINE

## 📊 **ANALYSE TECHNIQUE DÉTAILLÉE**

Ce document technique consolide l'analyse complète du schéma de base de données Mathakine et les spécifications techniques pour son évolution.

### **État Actuel du Schéma : EXCELLENT**
- **8 tables existantes** couvrant 85% des besoins actuels
- **Architecture solide** et bien conçue pour extension
- **Performance optimisée** avec index appropriés
- **Sécurité** : Bonnes pratiques respectées

### **Évaluation Détaillée par Table**
| Table | État | Couverture | Prêt Futur | Extensions Requises |
|-------|------|------------|-------------|-------------------|
| `users` | ✅ MATURE | 85% | ⚠️ EXTENSIONS | **20+ nouveaux champs** |
| `exercises` | ✅ MATURE | 90% | ✅ PRÊT | Métadonnées IA |
| `attempts` | ✅ STABLE | 80% | ⚠️ MINEURES | Analytics comportementales |
| `progress` | ✅ AVANCÉ | 95% | ✅ EXCELLENT | Aucune |
| `logic_challenges` | ✅ COMPLET | 100% | ✅ FUTUR-READY | Aucune |
| `logic_challenge_attempts` | ✅ STABLE | 85% | ✅ PRÊT | Aucune |
| `recommendations` | ✅ FONCTIONNEL | 75% | ⚠️ EXTENSIONS | IA avancée |
| `settings` | ✅ BASIQUE | 60% | ⚠️ DÉVELOPPEMENT | Préférences étendues |

## 🛠️ **SPÉCIFICATIONS TECHNIQUES DES EXTENSIONS**

### **Extensions Table Users (Détail Technique)**

#### **Nouveaux Champs - Spécifications SQL**
```sql
-- Profil enrichi
ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255);
ALTER TABLE users ADD COLUMN bio TEXT;
ALTER TABLE users ADD COLUMN birth_date DATE;
ALTER TABLE users ADD COLUMN timezone VARCHAR(50) NOT NULL DEFAULT 'UTC';
ALTER TABLE users ADD COLUMN language_preference VARCHAR(10) NOT NULL DEFAULT 'fr';

-- Sécurité avancée
ALTER TABLE users ADD COLUMN last_password_change TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN two_factor_secret VARCHAR(255);
ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN locked_until TIMESTAMP WITH TIME ZONE;

-- Préférences d'apprentissage étendues
ALTER TABLE users ADD COLUMN cognitive_profile JSON;
ALTER TABLE users ADD COLUMN special_needs JSON;

-- Gamification
ALTER TABLE users ADD COLUMN total_points INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN current_level INTEGER NOT NULL DEFAULT 1;
ALTER TABLE users ADD COLUMN experience_points INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN jedi_rank VARCHAR(50) NOT NULL DEFAULT 'youngling';

-- Métadonnées sociales
ALTER TABLE users ADD COLUMN is_public_profile BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN allow_friend_requests BOOLEAN NOT NULL DEFAULT true;
ALTER TABLE users ADD COLUMN show_in_leaderboards BOOLEAN NOT NULL DEFAULT true;

-- Conformité et données
ALTER TABLE users ADD COLUMN data_retention_consent BOOLEAN NOT NULL DEFAULT true;
ALTER TABLE users ADD COLUMN marketing_consent BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN deletion_requested_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT false;
```

#### **Index de Performance**
```sql
-- Index pour les performances
CREATE INDEX idx_users_avatar_url ON users(avatar_url);
CREATE INDEX idx_users_jedi_rank ON users(jedi_rank);
CREATE INDEX idx_users_is_public_profile ON users(is_public_profile);
CREATE INDEX idx_users_is_deleted ON users(is_deleted);
CREATE INDEX idx_users_total_points ON users(total_points);
CREATE INDEX idx_users_two_factor_enabled ON users(two_factor_enabled);
CREATE INDEX idx_users_locked_until ON users(locked_until) WHERE locked_until IS NOT NULL;
```

### **Nouvelles Tables - Spécifications Complètes**

#### **Table user_sessions - Gestion Avancée des Sessions**
```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    device_info JSON,
    ip_address INET,
    user_agent TEXT,
    location_data JSON,
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Index pour performances
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active, expires_at);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);
```

#### **Table achievements - Système de Badges**
```sql
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    category VARCHAR(50),
    difficulty VARCHAR(50),
    points_reward INTEGER NOT NULL DEFAULT 0,
    is_secret BOOLEAN NOT NULL DEFAULT false,
    requirements JSON,
    star_wars_title VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Index pour performances
CREATE INDEX idx_achievements_category ON achievements(category);
CREATE INDEX idx_achievements_difficulty ON achievements(difficulty);
CREATE INDEX idx_achievements_active ON achievements(is_active);
CREATE INDEX idx_achievements_code ON achievements(code);
```

#### **Table user_achievements - Badges Obtenus**
```sql
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    progress_data JSON,
    is_displayed BOOLEAN NOT NULL DEFAULT true,
    UNIQUE(user_id, achievement_id)
);

-- Index pour performances
CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_achievement ON user_achievements(achievement_id);
CREATE INDEX idx_user_achievements_earned ON user_achievements(earned_at);
```

#### **Table notifications - Système de Notifications**
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    data JSON,
    action_url VARCHAR(255),
    is_read BOOLEAN NOT NULL DEFAULT false,
    is_email_sent BOOLEAN NOT NULL DEFAULT false,
    priority INTEGER NOT NULL DEFAULT 5,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Index pour performances
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_priority ON notifications(priority);
CREATE INDEX idx_notifications_expires ON notifications(expires_at) WHERE expires_at IS NOT NULL;
```

#### **Table learning_analytics - Analytics Comportementales**
```sql
CREATE TABLE learning_analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,
    event_data JSON NOT NULL,
    exercise_id INTEGER REFERENCES exercises(id) ON DELETE SET NULL,
    challenge_id INTEGER REFERENCES logic_challenges(id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Index pour performances
CREATE INDEX idx_learning_analytics_user ON learning_analytics(user_id);
CREATE INDEX idx_learning_analytics_session ON learning_analytics(session_id);
CREATE INDEX idx_learning_analytics_type ON learning_analytics(event_type);
CREATE INDEX idx_learning_analytics_time ON learning_analytics(timestamp);
CREATE INDEX idx_learning_analytics_exercise ON learning_analytics(exercise_id) WHERE exercise_id IS NOT NULL;
CREATE INDEX idx_learning_analytics_challenge ON learning_analytics(challenge_id) WHERE challenge_id IS NOT NULL;
```

### **Extensions Table Exercises**

#### **Nouveaux Champs - Spécifications SQL**
```sql
-- Métadonnées IA et génération
ALTER TABLE exercises ADD COLUMN generation_seed VARCHAR(255);
ALTER TABLE exercises ADD COLUMN ai_confidence_score NUMERIC(3,2);
ALTER TABLE exercises ADD COLUMN human_reviewed BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE exercises ADD COLUMN review_notes TEXT;

-- Métadonnées pédagogiques
ALTER TABLE exercises ADD COLUMN cognitive_load INTEGER;
ALTER TABLE exercises ADD COLUMN prerequisite_concepts JSON;
ALTER TABLE exercises ADD COLUMN learning_objectives JSON;

-- Métadonnées sociales
ALTER TABLE exercises ADD COLUMN likes_count INTEGER NOT NULL DEFAULT 0;
ALTER TABLE exercises ADD COLUMN difficulty_votes JSON;
ALTER TABLE exercises ADD COLUMN quality_rating NUMERIC(3,2);

-- Accessibilité
ALTER TABLE exercises ADD COLUMN accessibility_features JSON;
ALTER TABLE exercises ADD COLUMN alternative_formats JSON;
```

#### **Index de Performance pour Exercises**
```sql
-- Index pour les nouvelles colonnes
CREATE INDEX idx_exercises_ai_confidence ON exercises(ai_confidence_score);
CREATE INDEX idx_exercises_human_reviewed ON exercises(human_reviewed);
CREATE INDEX idx_exercises_likes_count ON exercises(likes_count);
CREATE INDEX idx_exercises_quality_rating ON exercises(quality_rating);
CREATE INDEX idx_exercises_cognitive_load ON exercises(cognitive_load);
```

## 🔧 **MODÈLES SQLALCHEMY ÉTENDUS**

### **Modèle User Étendu**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, JSON, Numeric
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    
    # Champs existants
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), nullable=False, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Nouveaux champs - Profil enrichi
    avatar_url = Column(String(255), index=True)
    bio = Column(Text)
    birth_date = Column(Date)
    timezone = Column(String(50), nullable=False, default='UTC')
    language_preference = Column(String(10), nullable=False, default='fr')
    
    # Nouveaux champs - Sécurité avancée
    last_password_change = Column(DateTime(timezone=True))
    two_factor_enabled = Column(Boolean, nullable=False, default=False, index=True)
    two_factor_secret = Column(String(255))
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True), index=True)
    
    # Nouveaux champs - Préférences d'apprentissage
    cognitive_profile = Column(JSON)
    special_needs = Column(JSON)
    
    # Nouveaux champs - Gamification
    total_points = Column(Integer, nullable=False, default=0, index=True)
    current_level = Column(Integer, nullable=False, default=1)
    experience_points = Column(Integer, nullable=False, default=0)
    jedi_rank = Column(String(50), nullable=False, default='youngling', index=True)
    
    # Nouveaux champs - Métadonnées sociales
    is_public_profile = Column(Boolean, nullable=False, default=False, index=True)
    allow_friend_requests = Column(Boolean, nullable=False, default=True)
    show_in_leaderboards = Column(Boolean, nullable=False, default=True)
    
    # Nouveaux champs - Conformité et données
    data_retention_consent = Column(Boolean, nullable=False, default=True)
    marketing_consent = Column(Boolean, nullable=False, default=False)
    deletion_requested_at = Column(DateTime(timezone=True))
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
```

### **Modèle UserSession**
```python
class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    device_info = Column(JSON)
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    location_data = Column(JSON)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    last_activity = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Relations
    user = relationship("User", back_populates="sessions")
```

### **Modèle Achievement**
```python
class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))
    category = Column(String(50), index=True)
    difficulty = Column(String(50), index=True)
    points_reward = Column(Integer, nullable=False, default=0)
    is_secret = Column(Boolean, nullable=False, default=False)
    requirements = Column(JSON)
    star_wars_title = Column(String(255))
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
```

## 📊 **STRATÉGIE DE MIGRATION**

### **Phase 1 : Extensions Critiques**
1. **Backup complet** de la base de données
2. **Application des migrations** en mode maintenance
3. **Validation des données** après migration
4. **Tests de performance** sur nouvelles requêtes

### **Phase 2 : Optimisation**
1. **Analyse des requêtes** les plus fréquentes
2. **Ajout d'index** supplémentaires si nécessaire
3. **Optimisation des jointures** complexes
4. **Mise en place du monitoring** des performances

### **Phase 3 : Validation**
1. **Tests de charge** avec données réelles
2. **Validation de l'intégrité** des données
3. **Tests de sécurité** sur nouvelles fonctionnalités
4. **Documentation** des nouvelles API

## 🔍 **SCRIPTS DE VALIDATION TECHNIQUE**

### **Script de Validation du Schéma**
```python
def validate_database_schema():
    """Valider que le schéma de base de données est correct"""
    
    # Test 1: Vérifier les nouvelles colonnes users
    expected_columns = [
        'avatar_url', 'jedi_rank', 'total_points', 'two_factor_enabled',
        'cognitive_profile', 'is_public_profile', 'data_retention_consent'
    ]
    
    # Test 2: Vérifier les nouvelles tables
    expected_tables = [
        'user_sessions', 'achievements', 'user_achievements', 
        'notifications', 'learning_analytics'
    ]
    
    # Test 3: Vérifier les index de performance
    expected_indexes = [
        'idx_users_avatar_url', 'idx_users_jedi_rank', 'idx_users_total_points',
        'idx_user_sessions_user_id', 'idx_achievements_category'
    ]
    
    # Test 4: Vérifier les contraintes de clés étrangères
    # Test 5: Valider les types de données JSON
```

### **Script de Test de Performance**
```python
def validate_performance():
    """Valider les performances après migration"""
    
    # Test requête complexe avec nouvelles tables
    query = """
        SELECT u.username, u.total_points, u.jedi_rank,
               COUNT(ua.id) as achievements_count,
               COUNT(n.id) as unread_notifications
        FROM users u
        LEFT JOIN user_achievements ua ON u.id = ua.user_id
        LEFT JOIN notifications n ON u.id = n.user_id AND n.is_read = false
        WHERE u.is_active = true AND u.is_deleted = false
        GROUP BY u.id, u.username, u.total_points, u.jedi_rank
        ORDER BY u.total_points DESC
        LIMIT 10
    """
    
    # Mesurer le temps d'exécution
    # Objectif : < 100ms pour 95e percentile
```

## 📈 **MÉTRIQUES DE PERFORMANCE ATTENDUES**

### **Objectifs de Performance**
- **Temps de réponse** : < 200ms (95e percentile)
- **Débit** : 1000+ requêtes/seconde
- **Concurrence** : 50k+ utilisateurs simultanés
- **Disponibilité** : 99.9% uptime

### **Optimisations Prévues**
- **Index composites** pour requêtes complexes
- **Partitioning** des tables analytics par date
- **Cache Redis** pour données fréquemment accédées
- **Connection pooling** optimisé

## 🔒 **CONSIDÉRATIONS DE SÉCURITÉ**

### **Chiffrement des Données Sensibles**
- **two_factor_secret** : Chiffré avec AES-256
- **session_token** : Hash sécurisé avec salt
- **device_info** : Anonymisation des données sensibles

### **Audit et Traçabilité**
- **learning_analytics** : Traçage complet des actions
- **user_sessions** : Historique des connexions
- **notifications** : Logs des communications

### **Protection RGPD**
- **Suppression logique** avec `is_deleted`
- **Consentement granulaire** par type de données
- **Export automatisé** des données utilisateur
- **Anonymisation** après suppression

---

## 📁 **FICHIERS TECHNIQUES DISPONIBLES**

### **Migrations Alembic**
- `migrations/versions/20250527_190218_user_extensions.py`
- `migrations/versions/20250527_190218_new_tables.py`
- `migrations/versions/20250527_190218_exercise_extensions.py`

### **Modèles SQLAlchemy**
- `app/models/user_extended.py`
- `app/models/user_session.py`
- `app/models/achievement.py`
- `app/models/notification.py`

### **Scripts de Validation**
- `validate_schema_migrations.py`
- `update_user_model.py`
- `create_user_extensions_migration.py`

**🔧 Documentation technique complète pour l'évolution BDD Mathakine 🔧** 
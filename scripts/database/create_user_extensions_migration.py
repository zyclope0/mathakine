#!/usr/bin/env python3
"""
Script pour créer les migrations Alembic pour les extensions du schéma BDD Mathakine.
Ce script génère les migrations nécessaires pour supporter les futures fonctionnalités.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_user_extensions_migration():
    """Créer la migration pour les extensions de la table users"""
    
    migration_content = f'''"""Extensions critiques table users pour futures fonctionnalités

Revision ID: user_extensions_{datetime.now().strftime('%Y%m%d_%H%M%S')}
Revises: 
Create Date: {datetime.now().isoformat()}

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'user_extensions_{datetime.now().strftime('%Y%m%d_%H%M%S')}'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Ajouter les extensions à la table users"""
    
    # Profil enrichi
    op.add_column('users', sa.Column('avatar_url', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('birth_date', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'))
    op.add_column('users', sa.Column('language_preference', sa.String(10), nullable=False, server_default='fr'))
    
    # Sécurité et sessions
    op.add_column('users', sa.Column('last_password_change', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('two_factor_secret', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))
    
    # Préférences d'apprentissage étendues
    op.add_column('users', sa.Column('cognitive_profile', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('users', sa.Column('special_needs', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Gamification
    op.add_column('users', sa.Column('total_points', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('current_level', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('users', sa.Column('experience_points', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('jedi_rank', sa.String(50), nullable=False, server_default='youngling'))
    
    # Métadonnées sociales
    op.add_column('users', sa.Column('is_public_profile', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('allow_friend_requests', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('show_in_leaderboards', sa.Boolean(), nullable=False, server_default='true'))
    
    # Conformité et données
    op.add_column('users', sa.Column('data_retention_consent', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('marketing_consent', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('deletion_requested_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))
    
    # Créer les index pour les performances
    op.create_index('idx_users_avatar_url', 'users', ['avatar_url'])
    op.create_index('idx_users_jedi_rank', 'users', ['jedi_rank'])
    op.create_index('idx_users_is_public_profile', 'users', ['is_public_profile'])
    op.create_index('idx_users_is_deleted', 'users', ['is_deleted'])
    op.create_index('idx_users_total_points', 'users', ['total_points'])


def downgrade():
    """Supprimer les extensions de la table users"""
    
    # Supprimer les index
    op.drop_index('idx_users_total_points', table_name='users')
    op.drop_index('idx_users_is_deleted', table_name='users')
    op.drop_index('idx_users_is_public_profile', table_name='users')
    op.drop_index('idx_users_jedi_rank', table_name='users')
    op.drop_index('idx_users_avatar_url', table_name='users')
    
    # Supprimer les colonnes (ordre inverse)
    op.drop_column('users', 'is_deleted')
    op.drop_column('users', 'deletion_requested_at')
    op.drop_column('users', 'marketing_consent')
    op.drop_column('users', 'data_retention_consent')
    op.drop_column('users', 'show_in_leaderboards')
    op.drop_column('users', 'allow_friend_requests')
    op.drop_column('users', 'is_public_profile')
    op.drop_column('users', 'jedi_rank')
    op.drop_column('users', 'experience_points')
    op.drop_column('users', 'current_level')
    op.drop_column('users', 'total_points')
    op.drop_column('users', 'special_needs')
    op.drop_column('users', 'cognitive_profile')
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'two_factor_secret')
    op.drop_column('users', 'two_factor_enabled')
    op.drop_column('users', 'last_password_change')
    op.drop_column('users', 'language_preference')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'birth_date')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'avatar_url')
'''

    return migration_content

def create_new_tables_migration():
    """Créer la migration pour les nouvelles tables"""
    
    migration_content = f'''"""Création nouvelles tables pour fonctionnalités avancées

Revision ID: new_tables_{datetime.now().strftime('%Y%m%d_%H%M%S')}
Revises: user_extensions_{datetime.now().strftime('%Y%m%d_%H%M%S')}
Create Date: {datetime.now().isoformat()}

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'new_tables_{datetime.now().strftime('%Y%m%d_%H%M%S')}'
down_revision = 'user_extensions_{datetime.now().strftime('%Y%m%d_%H%M%S')}'
branch_labels = None
depends_on = None


def upgrade():
    """Créer les nouvelles tables"""
    
    # Table user_sessions
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(255), nullable=False),
        sa.Column('device_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('location_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token')
    )
    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('idx_user_sessions_token', 'user_sessions', ['session_token'])
    op.create_index('idx_user_sessions_active', 'user_sessions', ['is_active', 'expires_at'])
    
    # Table achievements
    op.create_table('achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_url', sa.String(255), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('difficulty', sa.String(50), nullable=True),
        sa.Column('points_reward', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_secret', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('requirements', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('star_wars_title', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('idx_achievements_category', 'achievements', ['category'])
    op.create_index('idx_achievements_active', 'achievements', ['is_active'])
    
    # Table user_achievements
    op.create_table('user_achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('achievement_id', sa.Integer(), nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('progress_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_displayed', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'achievement_id')
    )
    op.create_index('idx_user_achievements_user', 'user_achievements', ['user_id'])
    op.create_index('idx_user_achievements_earned', 'user_achievements', ['earned_at'])
    
    # Table notifications
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('action_url', sa.String(255), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_email_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notifications_user', 'notifications', ['user_id'])
    op.create_index('idx_notifications_unread', 'notifications', ['user_id', 'is_read'])
    op.create_index('idx_notifications_type', 'notifications', ['type'])
    
    # Table learning_analytics
    op.create_table('learning_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(255), nullable=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('event_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=True),
        sa.Column('challenge_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['challenge_id'], ['logic_challenges.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_learning_analytics_user', 'learning_analytics', ['user_id'])
    op.create_index('idx_learning_analytics_session', 'learning_analytics', ['session_id'])
    op.create_index('idx_learning_analytics_type', 'learning_analytics', ['event_type'])
    op.create_index('idx_learning_analytics_time', 'learning_analytics', ['timestamp'])


def downgrade():
    """Supprimer les nouvelles tables"""
    
    # Supprimer dans l'ordre inverse des dépendances
    op.drop_table('learning_analytics')
    op.drop_table('notifications')
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('user_sessions')
'''

    return migration_content

def create_exercise_extensions_migration():
    """Créer la migration pour les extensions de la table exercises"""
    
    migration_content = f'''"""Extensions table exercises pour métadonnées avancées

Revision ID: exercise_extensions_{datetime.now().strftime('%Y%m%d_%H%M%S')}
Revises: new_tables_{datetime.now().strftime('%Y%m%d_%H%M%S')}
Create Date: {datetime.now().isoformat()}

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'exercise_extensions_{datetime.now().strftime('%Y%m%d_%H%M%S')}'
down_revision = 'new_tables_{datetime.now().strftime('%Y%m%d_%H%M%S')}'
branch_labels = None
depends_on = None


def upgrade():
    """Ajouter les extensions à la table exercises"""
    
    # Métadonnées IA et génération
    op.add_column('exercises', sa.Column('generation_seed', sa.String(255), nullable=True))
    op.add_column('exercises', sa.Column('ai_confidence_score', sa.Numeric(precision=3, scale=2), nullable=True))
    op.add_column('exercises', sa.Column('human_reviewed', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('exercises', sa.Column('review_notes', sa.Text(), nullable=True))
    
    # Métadonnées pédagogiques
    op.add_column('exercises', sa.Column('cognitive_load', sa.Integer(), nullable=True))
    op.add_column('exercises', sa.Column('prerequisite_concepts', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('exercises', sa.Column('learning_objectives', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Métadonnées sociales
    op.add_column('exercises', sa.Column('likes_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('exercises', sa.Column('difficulty_votes', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('exercises', sa.Column('quality_rating', sa.Numeric(precision=3, scale=2), nullable=True))
    
    # Accessibilité
    op.add_column('exercises', sa.Column('accessibility_features', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('exercises', sa.Column('alternative_formats', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Index pour les performances
    op.create_index('idx_exercises_ai_confidence', 'exercises', ['ai_confidence_score'])
    op.create_index('idx_exercises_human_reviewed', 'exercises', ['human_reviewed'])
    op.create_index('idx_exercises_likes_count', 'exercises', ['likes_count'])
    op.create_index('idx_exercises_quality_rating', 'exercises', ['quality_rating'])


def downgrade():
    """Supprimer les extensions de la table exercises"""
    
    # Supprimer les index
    op.drop_index('idx_exercises_quality_rating', table_name='exercises')
    op.drop_index('idx_exercises_likes_count', table_name='exercises')
    op.drop_index('idx_exercises_human_reviewed', table_name='exercises')
    op.drop_index('idx_exercises_ai_confidence', table_name='exercises')
    
    # Supprimer les colonnes
    op.drop_column('exercises', 'alternative_formats')
    op.drop_column('exercises', 'accessibility_features')
    op.drop_column('exercises', 'quality_rating')
    op.drop_column('exercises', 'difficulty_votes')
    op.drop_column('exercises', 'likes_count')
    op.drop_column('exercises', 'learning_objectives')
    op.drop_column('exercises', 'prerequisite_concepts')
    op.drop_column('exercises', 'cognitive_load')
    op.drop_column('exercises', 'review_notes')
    op.drop_column('exercises', 'human_reviewed')
    op.drop_column('exercises', 'ai_confidence_score')
    op.drop_column('exercises', 'generation_seed')
'''

    return migration_content

def create_migration_files():
    """Créer tous les fichiers de migration"""
    
    migrations_dir = project_root / "migrations" / "versions"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    
    # Créer les migrations dans l'ordre
    migrations = [
        ("user_extensions", create_user_extensions_migration()),
        ("new_tables", create_new_tables_migration()),
        ("exercise_extensions", create_exercise_extensions_migration())
    ]
    
    created_files = []
    
    for name, content in migrations:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{name}.py"
        file_path = migrations_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        created_files.append(file_path)
        print(f"✅ Migration créée : {file_path}")
    
    return created_files

def create_validation_script():
    """Créer un script de validation des migrations"""
    
    validation_script = '''#!/usr/bin/env python3
"""
Script de validation des migrations de schéma BDD Mathakine
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import get_settings
from app.models.user_extended import User
from app.models.achievement import Achievement, UserAchievement
from app.models.user_session import UserSession
from app.models.notification import Notification

def validate_database_schema():
    """Valider que le schéma de base de données est correct"""
    
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        print("🔍 Validation du schéma de base de données...")
        
        # Test 1: Vérifier les nouvelles colonnes users
        print("📋 Test 1: Colonnes table users")
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('avatar_url', 'jedi_rank', 'total_points', 'two_factor_enabled')
        """))
        columns = [row[0] for row in result]
        
        expected_columns = ['avatar_url', 'jedi_rank', 'total_points', 'two_factor_enabled']
        missing_columns = set(expected_columns) - set(columns)
        
        if missing_columns:
            print(f"❌ Colonnes manquantes dans users: {missing_columns}")
            return False
        else:
            print("✅ Toutes les nouvelles colonnes users présentes")
        
        # Test 2: Vérifier les nouvelles tables
        print("📋 Test 2: Nouvelles tables")
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('user_sessions', 'achievements', 'user_achievements', 'notifications')
        """))
        tables = [row[0] for row in result]
        
        expected_tables = ['user_sessions', 'achievements', 'user_achievements', 'notifications']
        missing_tables = set(expected_tables) - set(tables)
        
        if missing_tables:
            print(f"❌ Tables manquantes: {missing_tables}")
            return False
        else:
            print("✅ Toutes les nouvelles tables présentes")
        
        # Test 3: Tester la création d'objets
        print("📋 Test 3: Création d'objets de test")
        
        # Test User étendu
        test_user = User(
            username="test_validation",
            email="test@validation.com",
            hashed_password="test_hash",
            avatar_url="https://example.com/avatar.jpg",
            jedi_rank="padawan",
            total_points=100,
            two_factor_enabled=False
        )
        db.add(test_user)
        db.flush()  # Pour obtenir l'ID sans commit
        
        # Test Achievement
        test_achievement = Achievement(
            code="test_achievement",
            name="Test Achievement",
            description="Achievement de test",
            category="test",
            difficulty="bronze",
            points_reward=10
        )
        db.add(test_achievement)
        db.flush()
        
        # Test UserAchievement
        test_user_achievement = UserAchievement(
            user_id=test_user.id,
            achievement_id=test_achievement.id
        )
        db.add(test_user_achievement)
        db.flush()
        
        # Test Notification
        test_notification = Notification(
            user_id=test_user.id,
            type="test",
            title="Test Notification",
            message="Notification de test"
        )
        db.add(test_notification)
        db.flush()
        
        print("✅ Tous les objets de test créés avec succès")
        
        # Test 4: Vérifier les index
        print("📋 Test 4: Index de performance")
        result = db.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename IN ('users', 'user_sessions', 'achievements', 'notifications')
            AND indexname LIKE 'idx_%'
        """))
        indexes = [row[0] for row in result]
        
        expected_indexes = [
            'idx_users_avatar_url', 'idx_users_jedi_rank', 'idx_users_total_points',
            'idx_user_sessions_user_id', 'idx_achievements_category', 'idx_notifications_user'
        ]
        
        missing_indexes = set(expected_indexes) - set(indexes)
        if missing_indexes:
            print(f"⚠️ Index manquants (non critique): {missing_indexes}")
        else:
            print("✅ Tous les index de performance présents")
        
        # Rollback pour ne pas polluer la base
        db.rollback()
        
        print("🎉 Validation du schéma réussie !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la validation: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

def validate_performance():
    """Valider les performances après migration"""
    
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        print("⚡ Test de performance...")
        
        import time
        start_time = time.time()
        
        # Test requête complexe
        result = db.execute(text("""
            SELECT u.username, u.total_points, u.jedi_rank,
                   COUNT(ua.id) as achievements_count
            FROM users u
            LEFT JOIN user_achievements ua ON u.id = ua.user_id
            WHERE u.is_active = true AND u.is_deleted = false
            GROUP BY u.id, u.username, u.total_points, u.jedi_rank
            ORDER BY u.total_points DESC
            LIMIT 10
        """))
        
        results = result.fetchall()
        end_time = time.time()
        
        query_time = (end_time - start_time) * 1000  # en ms
        
        if query_time < 100:  # moins de 100ms
            print(f"✅ Performance excellente: {query_time:.2f}ms")
        elif query_time < 500:  # moins de 500ms
            print(f"✅ Performance acceptable: {query_time:.2f}ms")
        else:
            print(f"⚠️ Performance à optimiser: {query_time:.2f}ms")
        
        return query_time < 1000  # Acceptable si moins de 1 seconde
        
    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
        return False
        
    finally:
        db.close()

def main():
    """Exécuter toutes les validations"""
    
    print("🚀 Validation des migrations Mathakine...")
    print("=" * 50)
    
    # Validation du schéma
    schema_valid = validate_database_schema()
    
    print("=" * 50)
    
    # Validation des performances
    performance_ok = validate_performance()
    
    print("=" * 50)
    
    if schema_valid and performance_ok:
        print("🎉 Toutes les validations réussies !")
        print("✅ Le schéma de base de données est prêt pour les nouvelles fonctionnalités")
        return 0
    else:
        print("❌ Certaines validations ont échoué")
        print("🔧 Vérifiez les migrations et réessayez")
        return 1

if __name__ == "__main__":
    exit(main())
'''

    validation_file = project_root / "validate_schema_migrations.py"
    with open(validation_file, 'w', encoding='utf-8') as f:
        f.write(validation_script)
    
    print(f"✅ Script de validation créé : {validation_file}")
    return validation_file

def main():
    """Créer tous les fichiers de migration et de validation"""
    
    print("🚀 Génération des migrations pour l'évolution du schéma BDD Mathakine...")
    print("=" * 70)
    
    try:
        # Créer les fichiers de migration
        migration_files = create_migration_files()
        print()
        
        # Créer le script de validation
        validation_file = create_validation_script()
        print()
        
        print("🎉 Tous les fichiers de migration ont été créés !")
        print("=" * 70)
        print()
        print("📋 Prochaines étapes :")
        print("   1. Vérifier les fichiers de migration générés")
        print("   2. Faire un backup de la base de données")
        print("   3. Tester sur environnement de développement :")
        print("      alembic upgrade head")
        print("   4. Valider avec le script :")
        print("      python validate_schema_migrations.py")
        print("   5. Si tout est OK, appliquer en production")
        print()
        print("📁 Fichiers créés :")
        for file_path in migration_files:
            print(f"   - {file_path}")
        print(f"   - {validation_file}")
        print()
        print("⚠️  IMPORTANT : Toujours tester sur un environnement de développement d'abord !")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération : {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
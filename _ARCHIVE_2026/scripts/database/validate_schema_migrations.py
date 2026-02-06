#!/usr/bin/env python3
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

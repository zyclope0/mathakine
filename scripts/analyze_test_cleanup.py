#!/usr/bin/env python3
"""
Analyse complète des problèmes de nettoyage des données de test.
"""

from app.db.base import engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

def analyze_test_cleanup():
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("=== ANALYSE COMPLÈTE DU NETTOYAGE DES TESTS ===\n")
        
        # 1. Tous les utilisateurs créés récemment (dernières 24h)
        yesterday = datetime.now() - timedelta(days=1)
        result = db.execute(text("""
            SELECT username, email, created_at, id 
            FROM users 
            WHERE created_at > NOW() - INTERVAL '24 hours' 
            OR username LIKE '%test%' 
            OR email LIKE '%test%'
            OR username LIKE '%new_%'
            OR username LIKE '%duplicate_%'
            ORDER BY created_at DESC
        """))
        recent_users = result.fetchall()
        
        print(f"🔍 UTILISATEURS SUSPECTS (récents ou test): {len(recent_users)}")
        for user in recent_users:
            print(f"  - ID {user[3]}: {user[0]} ({user[1]}) - {user[2]}")
        
        # 2. Utilisateurs avec des patterns de test
        test_patterns = [
            'test_%', 'new_test_%', 'duplicate_%', '%_test_%', 
            'user_stats_%', 'rec_cascade_%', 'attempt_error_%',
            'nonexistent_%', 'record_%', 'starlette_%'
        ]
        
        all_test_users = []
        for pattern in test_patterns:
            result = db.execute(text(f"SELECT username, email, id FROM users WHERE username LIKE '{pattern}' OR email LIKE '{pattern}'"))
            users = result.fetchall()
            all_test_users.extend(users)
        
        # Dédupliquer
        unique_test_users = list(set(all_test_users))
        print(f"\n🔍 TOUS LES UTILISATEURS DE TEST: {len(unique_test_users)}")
        
        # 3. Exercices suspects
        result = db.execute(text("""
            SELECT title, creator_id, created_at, id
            FROM exercises 
            WHERE title LIKE '%test%' 
            OR title LIKE '%Test%'
            OR title LIKE '%TEST%'
            OR created_at > NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC
        """))
        test_exercises = result.fetchall()
        
        print(f"\n🔍 EXERCICES SUSPECTS: {len(test_exercises)}")
        for ex in test_exercises:
            print(f"  - ID {ex[3]}: {ex[0]} (créateur: {ex[1]}) - {ex[2]}")
        
        # 4. Défis logiques suspects
        result = db.execute(text("""
            SELECT title, creator_id, created_at, id
            FROM logic_challenges 
            WHERE title LIKE '%test%' 
            OR title LIKE '%Test%'
            OR title LIKE '%TEST%'
            OR created_at > NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC
        """))
        test_challenges = result.fetchall()
        
        print(f"\n🔍 DÉFIS LOGIQUES SUSPECTS: {len(test_challenges)}")
        for ch in test_challenges:
            print(f"  - ID {ch[3]}: {ch[0]} (créateur: {ch[1]}) - {ch[2]}")
        
        # 5. Tentatives orphelines (sans utilisateur valide)
        result = db.execute(text("""
            SELECT a.id, a.user_id, a.exercise_id, a.created_at, u.username
            FROM attempts a
            LEFT JOIN users u ON a.user_id = u.id
            WHERE u.username LIKE '%test%' OR u.username IS NULL
            ORDER BY a.created_at DESC
            LIMIT 20
        """))
        orphan_attempts = result.fetchall()
        
        print(f"\n🔍 TENTATIVES SUSPECTES: {len(orphan_attempts)}")
        for att in orphan_attempts:
            print(f"  - ID {att[0]}: user_id={att[1]}, exercise_id={att[2]}, user={att[4]} - {att[3]}")
        
        # 6. Recommandations suspectes
        result = db.execute(text("""
            SELECT r.id, r.user_id, r.created_at, u.username
            FROM recommendations r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE u.username LIKE '%test%' OR u.username IS NULL
            ORDER BY r.created_at DESC
            LIMIT 20
        """))
        test_recommendations = result.fetchall()
        
        print(f"\n🔍 RECOMMANDATIONS SUSPECTES: {len(test_recommendations)}")
        for rec in test_recommendations:
            print(f"  - ID {rec[0]}: user_id={rec[1]}, user={rec[3]} - {rec[2]}")
        
        # 7. Analyse des fixtures pytest
        print(f"\n📊 ANALYSE DES FIXTURES:")
        
        # Vérifier si des fixtures utilisent des transactions
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE username LIKE 'fixture_%'"))
        fixture_users = result.scalar()
        print(f"  - Utilisateurs de fixture: {fixture_users}")
        
        # 8. Recommandations de nettoyage
        print(f"\n🧹 RECOMMANDATIONS DE NETTOYAGE:")
        
        if len(unique_test_users) > 0:
            print(f"  ❌ {len(unique_test_users)} utilisateurs de test à supprimer")
            
        if len(test_exercises) > 0:
            print(f"  ❌ {len(test_exercises)} exercices de test à supprimer")
            
        if len(test_challenges) > 0:
            print(f"  ❌ {len(test_challenges)} défis logiques de test à supprimer")
            
        if len(orphan_attempts) > 0:
            print(f"  ❌ {len(orphan_attempts)} tentatives suspectes à vérifier")
            
        if len(test_recommendations) > 0:
            print(f"  ❌ {len(test_recommendations)} recommandations suspectes à supprimer")
        
        # 9. Problèmes identifiés dans les tests
        print(f"\n🚨 PROBLÈMES IDENTIFIÉS:")
        print("  1. Les tests créent des données mais ne les suppriment pas")
        print("  2. Pas de fixtures avec rollback automatique")
        print("  3. Pas de nettoyage dans tearDown/teardown_method")
        print("  4. Utilisation de la vraie base de données au lieu de mocks")
        print("  5. Pas d'isolation entre les tests")
        
        # 10. Solutions recommandées
        print(f"\n💡 SOLUTIONS RECOMMANDÉES:")
        print("  1. Utiliser des fixtures pytest avec scope='function' et rollback")
        print("  2. Implémenter des teardown methods dans chaque test")
        print("  3. Utiliser des transactions avec rollback automatique")
        print("  4. Créer une base de données de test séparée")
        print("  5. Utiliser des mocks pour éviter les vraies insertions")
        
    finally:
        db.close()

if __name__ == "__main__":
    analyze_test_cleanup() 
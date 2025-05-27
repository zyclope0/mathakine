#!/usr/bin/env python3
"""
Script pour vérifier les données de test restantes dans la base de données.
"""

from app.db.base import engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

def check_test_data():
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("=== ANALYSE DES DONNÉES DE TEST RESTANTES ===\n")
        
        # Vérifier les utilisateurs de test
        result = db.execute(text("SELECT username, email, created_at FROM users WHERE username LIKE 'test_%' ORDER BY created_at DESC LIMIT 20"))
        users = result.fetchall()
        print(f"🔍 Utilisateurs de test trouvés: {len(users)}")
        for user in users:
            print(f"  - {user[0]} ({user[1]}) - {user[2]}")
        
        # Vérifier les exercices de test
        result = db.execute(text("SELECT title, creator_id, created_at FROM exercises WHERE title LIKE '%test%' OR title LIKE '%Test%' ORDER BY created_at DESC LIMIT 10"))
        exercises = result.fetchall()
        print(f"\n🔍 Exercices de test trouvés: {len(exercises)}")
        for exercise in exercises:
            print(f"  - {exercise[0]} (créateur: {exercise[1]}) - {exercise[2]}")
        
        # Vérifier les défis logiques de test
        result = db.execute(text("SELECT title, creator_id, created_at FROM logic_challenges WHERE title LIKE '%test%' OR title LIKE '%Test%' ORDER BY created_at DESC LIMIT 10"))
        challenges = result.fetchall()
        print(f"\n🔍 Défis logiques de test trouvés: {len(challenges)}")
        for challenge in challenges:
            print(f"  - {challenge[0]} (créateur: {challenge[1]}) - {challenge[2]}")
        
        # Vérifier les tentatives de test
        result = db.execute(text("""
            SELECT COUNT(*) as count, u.username 
            FROM attempts a 
            JOIN users u ON a.user_id = u.id 
            WHERE u.username LIKE 'test_%' 
            GROUP BY u.username 
            ORDER BY count DESC
        """))
        attempts = result.fetchall()
        print(f"\n🔍 Tentatives par utilisateur de test:")
        for attempt in attempts:
            print(f"  - {attempt[1]}: {attempt[0]} tentatives")
        
        # Vérifier les recommandations de test
        result = db.execute(text("""
            SELECT COUNT(*) as count, u.username 
            FROM recommendations r 
            JOIN users u ON r.user_id = u.id 
            WHERE u.username LIKE 'test_%' 
            GROUP BY u.username 
            ORDER BY count DESC
        """))
        recommendations = result.fetchall()
        print(f"\n🔍 Recommandations par utilisateur de test:")
        for rec in recommendations:
            print(f"  - {rec[1]}: {rec[0]} recommandations")
        
        # Statistiques globales
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        total_users = result.scalar()
        
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE username LIKE 'test_%'"))
        test_users = result.scalar()
        
        result = db.execute(text("SELECT COUNT(*) FROM exercises"))
        total_exercises = result.scalar()
        
        result = db.execute(text("SELECT COUNT(*) FROM attempts"))
        total_attempts = result.scalar()
        
        print(f"\n📊 STATISTIQUES GLOBALES:")
        print(f"  - Total utilisateurs: {total_users} (dont {test_users} de test = {test_users/total_users*100:.1f}%)")
        print(f"  - Total exercices: {total_exercises}")
        print(f"  - Total tentatives: {total_attempts}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_test_data() 
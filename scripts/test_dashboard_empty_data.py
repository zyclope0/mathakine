#!/usr/bin/env python3
"""Test du dashboard avec données vides"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("=== TEST DASHBOARD AVEC DONNEES VIDES ===\n")
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import NullPool
    from app.models.user import User
    from app.models.attempt import Attempt
    from app.models.logic_challenge import LogicChallengeAttempt
    import os
    
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url, poolclass=NullPool, connect_args={"connect_timeout": 10})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("[1/3] Verification des utilisateurs...")
        users = db.query(User).all()
        print(f"  Total utilisateurs: {len(users)}")
        
        if len(users) > 0:
            user = users[0]
            print(f"  Test avec utilisateur: {user.username}\n")
            
            print("[2/3] Verification des attempts...")
            user_attempts = db.query(Attempt).filter(Attempt.user_id == user.id).count()
            user_challenge_attempts = db.query(LogicChallengeAttempt).filter(LogicChallengeAttempt.user_id == user.id).count()
            print(f"  Attempts exercices: {user_attempts}")
            print(f"  Attempts challenges: {user_challenge_attempts}")
            
            if user_attempts == 0 and user_challenge_attempts == 0:
                print("  ⚠ ATTENTION: Utilisateur sans aucun attempt")
                print("  → Le dashboard doit afficher un message approprié\n")
            
            print("[3/3] Simulation des stats vides...")
            stats_simulation = {
                "total_exercises": 0,
                "total_challenges": 0,
                "correct_answers": 0,
                "incorrect_answers": 0,
                "average_score": 0,
                "level": user.level if hasattr(user, 'level') else 1,
                "xp": user.xp if hasattr(user, 'xp') else 0,
                "next_level_xp": 100,
                "exercises_by_type": {},
                "exercises_by_difficulty": {},
                "recent_activity": []
            }
            
            print("  Stats simulées pour utilisateur sans données:")
            print(f"    - total_exercises: {stats_simulation['total_exercises']}")
            print(f"    - total_challenges: {stats_simulation['total_challenges']}")
            print(f"    - level: {stats_simulation['level']}")
            print(f"    - xp: {stats_simulation['xp']}")
            print("\n  ✓ Le dashboard devrait afficher:")
            print("    1. Message d'accueil avec le nom d'utilisateur")
            print("    2. Cards avec 0 exercices/challenges")
            print("    3. Message encourageant à commencer")
            print("    4. Pas d'erreur si recent_activity est vide")
        else:
            print("  ⚠ Aucun utilisateur dans la base")
            print("  → Créer un utilisateur de test pour vérifier le dashboard\n")
        
        print("\n[RECOMMANDATIONS]")
        print("1. Le dashboard doit gérer gracieusement les cas suivants:")
        print("   - Nouvel utilisateur sans attempts")
        print("   - Utilisateur après reset de la base")
        print("   - Tableaux vides (exercises_by_type, recent_activity)")
        print("2. Afficher un EmptyState avec un CTA 'Commencer les exercices'")
        print("3. Les graphiques doivent gérer les données vides")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()
        engine.dispose()

if __name__ == "__main__":
    sys.exit(main())


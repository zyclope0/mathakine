"""
Test des statistiques du dashboard après corrections.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.services.user_service import UserService

def test_stats():
    """Test les statistiques après corrections."""
    # Récupérer le premier utilisateur
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("SELECT id, username FROM users ORDER BY id LIMIT 1")
        user = cursor.fetchone()
        if not user:
            print("Aucun utilisateur trouve")
            return
        
        user_id = user['id']
        username = user['username']
        print(f"Test avec utilisateur: {username} (ID: {user_id})")
        
        # Tester avec UserService
        db = SessionLocal()
        try:
            stats = UserService.get_user_stats(db, user_id)
            
            print("\n=== STATISTIQUES RETOURNEES ===")
            print(f"Total attempts: {stats.get('total_attempts', 0)}")
            print(f"Correct attempts: {stats.get('correct_attempts', 0)}")
            print(f"Success rate: {stats.get('success_rate', 0)}%")
            
            print("\n=== STATISTIQUES PAR TYPE ===")
            by_type = stats.get('by_exercise_type', {})
            if by_type:
                for ex_type, type_stats in by_type.items():
                    print(f"  {ex_type}: {type_stats.get('total', 0)} tentatives, "
                          f"{type_stats.get('correct', 0)} correctes, "
                          f"{type_stats.get('success_rate', 0)}%")
            else:
                print("  AUCUNE STATISTIQUE PAR TYPE!")
            
            # Tester le format attendu par le frontend
            print("\n=== FORMAT POUR FRONTEND ===")
            performance_by_type = {}
            for exercise_type, type_stats in stats.get("by_exercise_type", {}).items():
                type_key = str(exercise_type).lower() if exercise_type else 'unknown'
                performance_by_type[type_key] = {
                    "completed": type_stats.get("total", 0),
                    "correct": type_stats.get("correct", 0),
                    "success_rate": type_stats.get("success_rate", 0)
                }
            
            print(f"Performance by type keys: {list(performance_by_type.keys())}")
            for key, value in performance_by_type.items():
                print(f"  {key}: {value}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_stats()


"""
Script de diagnostic pour vérifier pourquoi les statistiques du dashboard sont à 0.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings
from loguru import logger

def diagnose_stats():
    """Diagnostique les statistiques du dashboard."""
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("=" * 80)
        print("DIAGNOSTIC DES STATISTIQUES DU DASHBOARD")
        print("=" * 80)
        
        # 1. Vérifier les utilisateurs
        print("\n1. UTILISATEURS:")
        cursor.execute("SELECT id, username, email FROM users ORDER BY id LIMIT 5")
        users = cursor.fetchall()
        print(f"   Nombre d'utilisateurs: {len(users)}")
        for user in users:
            print(f"   - ID: {user['id']}, Username: {user['username']}, Email: {user.get('email', 'N/A')}")
        
        if not users:
            print("   ⚠️ AUCUN UTILISATEUR TROUVÉ!")
            return
        
        first_user_id = users[0]['id']
        print(f"\n   -> Utilisation de l'utilisateur ID {first_user_id} pour les tests")
        
        # 2. Vérifier les tentatives
        print("\n2. TENTATIVES (table attempts):")
        cursor.execute("SELECT COUNT(*) as total FROM attempts")
        total_attempts = cursor.fetchone()['total']
        print(f"   Total de tentatives dans la base: {total_attempts}")
        
        cursor.execute("SELECT COUNT(*) as total FROM attempts WHERE user_id = %s", (first_user_id,))
        user_attempts = cursor.fetchone()['total']
        print(f"   Tentatives pour l'utilisateur {first_user_id}: {user_attempts}")
        
        if user_attempts > 0:
            cursor.execute("""
                SELECT id, exercise_id, user_answer, is_correct, created_at 
                FROM attempts 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 5
            """, (first_user_id,))
            recent_attempts = cursor.fetchall()
            print(f"\n   Dernières tentatives:")
            for attempt in recent_attempts:
                print(f"   - ID: {attempt['id']}, Exercise: {attempt['exercise_id']}, "
                      f"Correct: {attempt['is_correct']}, Date: {attempt['created_at']}")
        
        # 3. Vérifier les exercices
        print("\n3. EXERCICES:")
        cursor.execute("SELECT COUNT(*) as total FROM exercises")
        total_exercises = cursor.fetchone()['total']
        print(f"   Total d'exercices: {total_exercises}")
        
        cursor.execute("SELECT DISTINCT exercise_type FROM exercises")
        exercise_types = [row['exercise_type'] for row in cursor.fetchall()]
        print(f"   Types d'exercices disponibles: {exercise_types}")
        
        # 4. Vérifier la jointure attempts + exercises
        print("\n4. JOINTURE ATTEMPTS + EXERCISES:")
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM attempts a
            JOIN exercises e ON e.id = a.exercise_id
            WHERE a.user_id = %s
        """, (first_user_id,))
        joined_count = cursor.fetchone()['total']
        print(f"   Tentatives avec exercice valide: {joined_count}")
        
        # 5. Statistiques par type
        print("\n5. STATISTIQUES PAR TYPE:")
        cursor.execute("""
            SELECT 
                e.exercise_type,
                COUNT(*) as total,
                SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) as correct
            FROM attempts a
            JOIN exercises e ON e.id = a.exercise_id
            WHERE a.user_id = %s
            GROUP BY e.exercise_type
            ORDER BY total DESC
        """, (first_user_id,))
        stats_by_type = cursor.fetchall()
        
        if stats_by_type:
            for stat in stats_by_type:
                success_rate = (stat['correct'] / stat['total'] * 100) if stat['total'] > 0 else 0
                print(f"   - {stat['exercise_type']}: {stat['total']} tentatives, "
                      f"{stat['correct']} correctes ({success_rate:.1f}%)")
        else:
            print("   ⚠️ AUCUNE STATISTIQUE PAR TYPE!")
        
        # 6. Vérifier les tentatives récentes (2-3 derniers jours)
        print("\n6. TENTATIVES RÉCENTES (2-3 derniers jours):")
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM attempts
            WHERE user_id = %s
            AND created_at >= CURRENT_DATE - INTERVAL '3 days'
        """, (first_user_id,))
        recent_count = cursor.fetchone()['total']
        print(f"   Tentatives des 3 derniers jours: {recent_count}")
        
        if recent_count > 0:
            cursor.execute("""
                SELECT 
                    a.id,
                    a.exercise_id,
                    e.exercise_type,
                    a.is_correct,
                    a.created_at
                FROM attempts a
                JOIN exercises e ON e.id = a.exercise_id
                WHERE a.user_id = %s
                AND a.created_at >= CURRENT_DATE - INTERVAL '3 days'
                ORDER BY a.created_at DESC
                LIMIT 10
            """, (first_user_id,))
            recent_details = cursor.fetchall()
            print(f"\n   Détails des tentatives récentes:")
            for detail in recent_details:
                print(f"   - {detail['created_at']}: Exercise {detail['exercise_id']} "
                      f"({detail['exercise_type']}), Correct: {detail['is_correct']}")
        
        # 7. Vérifier si SQLAlchemy peut lire les tentatives
        print("\n7. TEST AVEC SQLALCHEMY:")
        try:
            from sqlalchemy.orm import Session
            from app.db.base import SessionLocal
            from app.models.attempt import Attempt
            from app.models.exercise import Exercise
            
            db = SessionLocal()
            try:
                attempts_query = db.query(Attempt).filter(Attempt.user_id == first_user_id)
                total_sqlalchemy = attempts_query.count()
                print(f"   Tentatives trouvées par SQLAlchemy: {total_sqlalchemy}")
                
                if total_sqlalchemy > 0:
                    # Test de la jointure
                    type_attempts = (
                        db.query(Attempt)
                        .join(Exercise, Exercise.id == Attempt.exercise_id)
                        .filter(Attempt.user_id == first_user_id)
                        .all()
                    )
                    print(f"   Tentatives avec jointure SQLAlchemy: {len(type_attempts)}")
                    
                    # Test par type
                    for ex_type in exercise_types[:3]:  # Test sur les 3 premiers types
                        type_count = (
                            db.query(Attempt)
                            .join(Exercise, Exercise.id == Attempt.exercise_id)
                            .filter(Attempt.user_id == first_user_id)
                            .filter(Exercise.exercise_type == ex_type)
                            .count()
                        )
                        print(f"   - Type {ex_type}: {type_count} tentatives")
                else:
                    print("   ⚠️ SQLAlchemy ne trouve AUCUNE tentative!")
            finally:
                db.close()
        except Exception as e:
            print(f"   ❌ ERREUR avec SQLAlchemy: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 80)
        print("FIN DU DIAGNOSTIC")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Erreur lors du diagnostic: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    diagnose_stats()


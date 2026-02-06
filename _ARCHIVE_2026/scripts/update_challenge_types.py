"""
Script pour mettre à jour les types de challenges de test.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_db_connection

def update_challenge_types():
    """Met à jour les types de challenges de test"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        updates = [
            ('Test Sequence - Suite de nombres', 'SEQUENCE'),
            ('Test Pattern - Grille 3x3', 'PATTERN'),
            ('Test Visuel - Formes geometriques', 'VISUAL'),
            ('Test Puzzle - Reorganiser les etapes', 'PUZZLE'),
            ('Test Graphe - Reseau de connexions', 'GRAPH'),
        ]
        
        for title, challenge_type in updates:
            cursor.execute(
                "UPDATE logic_challenges SET challenge_type = %s WHERE title = %s RETURNING id, title, challenge_type",
                (challenge_type, title)
            )
            result = cursor.fetchone()
            if result:
                print(f"[OK] Mis a jour: '{result['title']}' -> {result['challenge_type']}")
            else:
                print(f"[INFO] Challenge '{title}' non trouve")
        
        conn.commit()
        print("\n=== Mise a jour terminee ===\n")
        
    except Exception as e:
        conn.rollback()
        print(f"[ERREUR] {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_challenge_types()


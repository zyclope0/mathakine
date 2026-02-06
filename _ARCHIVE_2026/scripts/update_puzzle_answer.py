"""Script pour mettre à jour la réponse correcte du challenge puzzle"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_db_connection

def update_puzzle_answer():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE logic_challenges SET correct_answer = %s WHERE title = %s",
            ('Préparer,Mélanger,Cuire,Servir', 'Test Puzzle - Reorganiser les etapes')
        )
        conn.commit()
        print(f"[OK] Challenge 'Test Puzzle - Reorganiser les etapes' mis à jour")
        print(f"     Nouvelle réponse correcte: 'Préparer,Mélanger,Cuire,Servir'")
    except Exception as e:
        conn.rollback()
        print(f"[ERREUR] {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_puzzle_answer()


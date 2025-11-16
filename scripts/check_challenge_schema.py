"""Script pour vérifier le schéma de la table logic_challenges"""
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_db_connection

def check_schema():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Vérifier les colonnes de traduction
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'logic_challenges' 
            AND column_name LIKE '%translation%'
            ORDER BY column_name
        """)
        translation_cols = cursor.fetchall()
        print("Colonnes de traduction:", [c['column_name'] for c in translation_cols] if translation_cols else "Aucune")
        
        # Vérifier les colonnes title et description
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'logic_challenges' 
            AND column_name IN ('title', 'description')
            ORDER BY column_name
        """)
        basic_cols = cursor.fetchall()
        print("\nColonnes de base:")
        for col in basic_cols:
            print(f"  - {col['column_name']}: {col['data_type']}, nullable: {col['is_nullable']}")
        
        # Tester la requête sur un challenge de test
        cursor.execute("""
            SELECT 
                id,
                title,
                description,
                title_translations,
                description_translations
            FROM logic_challenges 
            WHERE id = 2356
        """)
        test_challenge = cursor.fetchone()
        if test_challenge:
            print(f"\nChallenge de test (ID 2356):")
            print(f"  title: {test_challenge['title']}")
            print(f"  description: {test_challenge['description']}")
            print(f"  title_translations: {test_challenge.get('title_translations')}")
            print(f"  description_translations: {test_challenge.get('description_translations')}")
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_schema()


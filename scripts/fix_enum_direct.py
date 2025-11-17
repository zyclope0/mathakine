#!/usr/bin/env python3
"""Script direct pour corriger les enums PostgreSQL"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.base import engine

def main():
    print("="*60)
    print("CORRECTION ENUMS POSTGRESQL - VERSION DIRECTE")
    print("="*60)
    
    with engine.connect() as conn:
        trans = conn.begin()
        
        try:
            print("\n[1/6] Conversion en TEXT...")
            conn.execute(text("ALTER TABLE exercises ALTER COLUMN exercise_type TYPE text USING exercise_type::text"))
            conn.execute(text("ALTER TABLE exercises ALTER COLUMN difficulty TYPE text USING difficulty::text"))
            print("OK")
            
            print("\n[2/6] Suppression anciens ENUM...")
            conn.execute(text("DROP TYPE IF EXISTS exercisetype CASCADE"))
            conn.execute(text("DROP TYPE IF EXISTS difficultylevel CASCADE"))
            print("OK")
            
            print("\n[3/6] Creation nouveaux ENUM (MAJUSCULES)...")
            conn.execute(text("""
                CREATE TYPE exercisetype AS ENUM (
                    'ADDITION', 'SOUSTRACTION', 'MULTIPLICATION', 'DIVISION',
                    'FRACTIONS', 'GEOMETRIE', 'TEXTE', 'MIXTE', 'DIVERS'
                )
            """))
            print("exercisetype OK")
            
            conn.execute(text("""
                CREATE TYPE difficultylevel AS ENUM (
                    'INITIE', 'PADAWAN', 'CHEVALIER', 'MAITRE'
                )
            """))
            print("difficultylevel OK")
            
            print("\n[4/6] Reapplication des types...")
            conn.execute(text("ALTER TABLE exercises ALTER COLUMN exercise_type TYPE exercisetype USING UPPER(exercise_type)::exercisetype"))
            conn.execute(text("ALTER TABLE exercises ALTER COLUMN difficulty TYPE difficultylevel USING UPPER(difficulty)::difficultylevel"))
            print("OK")
            
            print("\n[5/6] Commit...")
            trans.commit()
            print("OK")
            
            print("\n[6/6] Verification...")
            result = conn.execute(text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'exercisetype'::regtype ORDER BY enumsortorder"))
            values = [row[0] for row in result]
            print(f"Valeurs: {values}")
            
            print("\n" + "="*60)
            print("SUCCES ! Migration terminee.")
            print("="*60)
            return True
            
        except Exception as e:
            trans.rollback()
            print(f"\nERREUR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



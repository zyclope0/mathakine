#!/usr/bin/env python3
"""Fix choices_translations pour copier les choices"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("=== FIX CHOICES_TRANSLATIONS ===\n")
    
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import NullPool
    import os
    
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url, poolclass=NullPool, connect_args={"connect_timeout": 10})
    
    try:
        with engine.connect() as conn:
            print("[1/2] Mise a jour choices_translations...\n")
            
            # Mettre à jour choices_translations avec les choix de choices
            # Forcer la mise à jour pour tous les exercices avec choices
            # Construire un JSON array correct : {"fr": ["choix1", "choix2", ...]}
            result = conn.execute(text("""
                UPDATE exercises
                SET choices_translations = ('{"fr": ' || choices::text || '}')::jsonb
                WHERE choices IS NOT NULL
            """))
            
            # Commit explicite
            conn.commit()
            
            print(f"  {result.rowcount} exercices mis a jour\n")
            
            print("[2/2] Verification...")
            result = conn.execute(text("""
                SELECT id, choices, choices_translations
                FROM exercises
                WHERE choices IS NOT NULL
                LIMIT 5
            """))
            
            for row in result:
                print(f"  ID {row[0]}:")
                print(f"    choices: {str(row[1])[:50]}")
                print(f"    choices_translations: {str(row[2])[:80]}")
            
            print("\n[SUCCES] Correction terminee!")
            
            conn.close()
    finally:
        engine.dispose()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


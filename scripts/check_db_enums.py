#!/usr/bin/env python3
"""
Script pour vérifier les valeurs enum dans la base de données PostgreSQL
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import SessionLocal
from sqlalchemy import text

def check_enums():
    """Vérifie les valeurs enum disponibles dans PostgreSQL"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("VERIFICATION DES ENUMS POSTGRESQL")
        print("=" * 60)
        
        # Vérifier les types enum existants
        query_enum_types = text("""
            SELECT 
                t.typname as enum_name,
                e.enumlabel as enum_value
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            WHERE n.nspname = 'public'
            ORDER BY t.typname, e.enumsortorder;
        """)
        
        result = db.execute(query_enum_types)
        rows = result.fetchall()
        
        if rows:
            current_enum = None
            for row in rows:
                if current_enum != row[0]:
                    if current_enum:
                        print()
                    current_enum = row[0]
                    print(f"\n[{current_enum}]")
                print(f"  - {row[1]}")
        else:
            print("Aucun enum trouvé")
        
        # Vérifier la structure de la table exercises
        print("\n" + "=" * 60)
        print("STRUCTURE TABLE EXERCISES")
        print("=" * 60)
        
        query_columns = text("""
            SELECT 
                column_name,
                data_type,
                udt_name,
                is_nullable
            FROM information_schema.columns
            WHERE table_name = 'exercises'
            ORDER BY ordinal_position;
        """)
        
        result = db.execute(query_columns)
        rows = result.fetchall()
        
        for row in rows:
            nullable = "NULL" if row[3] == 'YES' else "NOT NULL"
            print(f"{row[0]:20} {row[1]:15} ({row[2]:20}) {nullable}")
        
        # Vérifier la structure de la table logic_challenges
        print("\n" + "=" * 60)
        print("STRUCTURE TABLE LOGIC_CHALLENGES")
        print("=" * 60)
        
        query_columns = text("""
            SELECT 
                column_name,
                data_type,
                udt_name,
                is_nullable
            FROM information_schema.columns
            WHERE table_name = 'logic_challenges'
            ORDER BY ordinal_position;
        """)
        
        result = db.execute(query_columns)
        rows = result.fetchall()
        
        for row in rows:
            nullable = "NULL" if row[3] == 'YES' else "NOT NULL"
            print(f"{row[0]:30} {row[1]:15} ({row[2]:25}) {nullable}")
        
    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_enums()


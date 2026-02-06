#!/usr/bin/env python3
"""Analyse complete du schema de la base de donnees"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.db.base import engine

def main():
    print("="*80)
    print("ANALYSE DU SCHEMA DE LA BASE DE DONNEES")
    print("="*80)
    
    with engine.connect() as conn:
        # 1. Lister toutes les tables
        print("\n[1] TABLES EXISTANTES:")
        print("-"*80)
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")
        
        # 2. Lister tous les ENUM types
        print("\n[2] TYPES ENUM EXISTANTS:")
        print("-"*80)
        result = conn.execute(text("""
            SELECT t.typname, string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) as values
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            WHERE t.typtype = 'e'
            GROUP BY t.typname
            ORDER BY t.typname
        """))
        enums = list(result)
        for enum_name, enum_values in enums:
            print(f"\n  {enum_name}:")
            print(f"    Valeurs: {enum_values}")
        
        # 3. Schema de la table exercises
        if 'exercises' in tables:
            print("\n[3] SCHEMA DE LA TABLE 'exercises':")
            print("-"*80)
            result = conn.execute(text("""
                SELECT 
                    column_name,
                    data_type,
                    udt_name,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = 'exercises'
                ORDER BY ordinal_position
            """))
            for row in result:
                col_name, data_type, udt_name, nullable, default = row
                print(f"  {col_name}")
                print(f"    Type: {data_type} ({udt_name})")
                print(f"    Nullable: {nullable}")
                if default:
                    print(f"    Default: {default}")
                print()
        
        # 4. Schema de la table logic_challenges
        if 'logic_challenges' in tables:
            print("\n[4] SCHEMA DE LA TABLE 'logic_challenges':")
            print("-"*80)
            result = conn.execute(text("""
                SELECT 
                    column_name,
                    data_type,
                    udt_name,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = 'logic_challenges'
                ORDER BY ordinal_position
            """))
            for row in result:
                col_name, data_type, udt_name, nullable, default = row
                print(f"  {col_name}")
                print(f"    Type: {data_type} ({udt_name})")
                print(f"    Nullable: {nullable}")
                if default:
                    print(f"    Default: {default}")
                print()
        
        # 5. Compter les donnees existantes
        print("\n[5] DONNEES EXISTANTES:")
        print("-"*80)
        if 'exercises' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM exercises"))
            count = result.scalar()
            print(f"  Exercises: {count}")
            
            if count > 0:
                result = conn.execute(text("""
                    SELECT exercise_type, COUNT(*) 
                    FROM exercises 
                    GROUP BY exercise_type
                """))
                print("  Repartition par type:")
                for ex_type, count in result:
                    print(f"    - {ex_type}: {count}")
        
        if 'logic_challenges' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM logic_challenges"))
            count = result.scalar()
            print(f"  Challenges: {count}")
            
            if count > 0:
                result = conn.execute(text("""
                    SELECT challenge_type, COUNT(*) 
                    FROM logic_challenges 
                    GROUP BY challenge_type
                """))
                print("  Repartition par type:")
                for ch_type, count in result:
                    print(f"    - {ch_type}: {count}")
        
        # 6. Verifier les contraintes de cles etrangeres
        print("\n[6] CONTRAINTES DE CLES ETRANGERES:")
        print("-"*80)
        result = conn.execute(text("""
            SELECT
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND (tc.table_name = 'exercises' OR tc.table_name = 'logic_challenges'
                     OR ccu.table_name = 'exercises' OR ccu.table_name = 'logic_challenges')
            ORDER BY tc.table_name
        """))
        for table, column, foreign_table, foreign_column in result:
            print(f"  {table}.{column} -> {foreign_table}.{foreign_column}")
    
    print("\n" + "="*80)
    print("ANALYSE TERMINEE")
    print("="*80)

if __name__ == "__main__":
    main()



#!/usr/bin/env python3
"""
Script pour exporter le schéma complet de la base de données depuis Render.

Ce script génère un fichier SQL contenant :
- Toutes les tables avec leurs colonnes
- Tous les types ENUM
- Toutes les contraintes (PK, FK, UNIQUE, CHECK)
- Tous les index
- Toutes les séquences
- Les commentaires sur les tables et colonnes
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

def export_schema():
    """Exporte le schéma complet de la base de données"""
    
    # Utiliser DATABASE_URL depuis les settings
    database_url = settings.DATABASE_URL
    
    if not database_url:
        print("❌ ERREUR: DATABASE_URL n'est pas défini dans les variables d'environnement")
        sys.exit(1)
    
    print(f"[*] Connexion a la base de donnees...")
    print(f"   Host: {urlparse(database_url).hostname}")
    print(f"   Database: {urlparse(database_url).path[1:]}")
    
    try:
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as conn:
            # Créer le fichier de sortie
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"schema_export_{timestamp}.sql"
            
            print(f"\n[*] Export du schema vers: {output_file}\n")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # En-tête
                f.write("-- ============================================================================\n")
                f.write(f"-- SCHÉMA COMPLET DE LA BASE DE DONNÉES MATHAKINE\n")
                f.write(f"-- Exporté le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- Source: {urlparse(database_url).hostname}\n")
                f.write("-- ============================================================================\n\n")
                
                # 1. Types ENUM
                print("[*] Export des types ENUM...")
                f.write("-- ============================================================================\n")
                f.write("-- TYPES ENUM\n")
                f.write("-- ============================================================================\n\n")
                
                result = conn.execute(text("""
                    SELECT 
                        t.typname as enum_name,
                        string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) as enum_values
                    FROM pg_type t 
                    JOIN pg_enum e ON t.oid = e.enumtypid  
                    WHERE t.typtype = 'e'
                    AND t.typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                    GROUP BY t.typname
                    ORDER BY t.typname
                """))
                
                enums = list(result)
                if enums:
                    for enum_name, enum_values in enums:
                        values_list = enum_values.split(', ')
                        f.write(f"CREATE TYPE {enum_name} AS ENUM (\n")
                        f.write(",\n".join(f"    '{val}'" for val in values_list))
                        f.write("\n);\n\n")
                else:
                    f.write("-- Aucun type ENUM trouvé\n\n")
                
                # 2. Tables et leurs colonnes
                print("[*] Export des tables...")
                f.write("-- ============================================================================\n")
                f.write("-- TABLES\n")
                f.write("-- ============================================================================\n\n")
                
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """))
                
                tables = [row[0] for row in result]
                
                for table_name in tables:
                    # Détails de la table
                    f.write(f"-- Table: {table_name}\n")
                    f.write(f"CREATE TABLE {table_name} (\n")
                    
                    # Colonnes
                    result = conn.execute(text("""
                        SELECT 
                            column_name,
                            data_type,
                            character_maximum_length,
                            is_nullable,
                            column_default,
                            udt_name
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                        AND table_name = :table_name
                        ORDER BY ordinal_position
                    """), {"table_name": table_name})
                    
                    columns = list(result)
                    column_defs = []
                    
                    for col in columns:
                        col_name, data_type, max_length, is_nullable, default, udt_name = col
                        
                        # Construire le type de colonne
                        if udt_name.startswith('_'):
                            # Type array
                            base_type = udt_name[1:]
                            col_type = f"{base_type}[]"
                        elif data_type == 'USER-DEFINED':
                            col_type = udt_name
                        elif data_type == 'character varying':
                            col_type = f"VARCHAR({max_length})" if max_length else "VARCHAR"
                        elif data_type == 'character':
                            col_type = f"CHAR({max_length})" if max_length else "CHAR"
                        elif data_type == 'numeric':
                            col_type = "NUMERIC"
                        elif data_type == 'timestamp without time zone':
                            col_type = "TIMESTAMP"
                        elif data_type == 'timestamp with time zone':
                            col_type = "TIMESTAMPTZ"
                        else:
                            col_type = data_type.upper()
                        
                        col_def = f"    {col_name} {col_type}"
                        
                        # NULL/NOT NULL
                        if is_nullable == 'NO':
                            col_def += " NOT NULL"
                        
                        # DEFAULT
                        if default:
                            # Nettoyer la valeur par défaut
                            default_clean = default
                            if default.startswith("nextval("):
                                default_clean = default
                            elif default.startswith("'") and default.endswith("'"):
                                default_clean = default
                            else:
                                default_clean = f"'{default}'"
                            col_def += f" DEFAULT {default_clean}"
                        
                        column_defs.append(col_def)
                    
                    f.write(",\n".join(column_defs))
                    f.write("\n);\n\n")
                    
                    # Commentaires sur la table
                    result = conn.execute(text("""
                        SELECT obj_description(c.oid, 'pg_class') as comment
                        FROM pg_class c
                        JOIN pg_namespace n ON n.oid = c.relnamespace
                        WHERE c.relname = :table_name
                        AND n.nspname = 'public'
                    """), {"table_name": table_name})
                    
                    comment_row = result.fetchone()
                    if comment_row and comment_row[0]:
                        f.write(f"COMMENT ON TABLE {table_name} IS '{comment_row[0]}';\n\n")
                    
                    # Commentaires sur les colonnes
                    result = conn.execute(text("""
                        SELECT 
                            a.attname as column_name,
                            col_description(a.attrelid, a.attnum) as comment
                        FROM pg_attribute a
                        JOIN pg_class c ON c.oid = a.attrelid
                        JOIN pg_namespace n ON n.oid = c.relnamespace
                        WHERE c.relname = :table_name
                        AND n.nspname = 'public'
                        AND a.attnum > 0
                        AND NOT a.attisdropped
                        AND col_description(a.attrelid, a.attnum) IS NOT NULL
                    """), {"table_name": table_name})
                    
                    col_comments = list(result)
                    for col_name, comment in col_comments:
                        f.write(f"COMMENT ON COLUMN {table_name}.{col_name} IS '{comment}';\n")
                    
                    if col_comments:
                        f.write("\n")
                
                # 3. Contraintes de clé primaire
                print("[*] Export des cles primaires...")
                f.write("-- ============================================================================\n")
                f.write("-- CONTRAINTES DE CLÉ PRIMAIRE\n")
                f.write("-- ============================================================================\n\n")
                
                result = conn.execute(text("""
                    SELECT
                        tc.table_name,
                        tc.constraint_name,
                        string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as columns
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_schema = 'public'
                    GROUP BY tc.table_name, tc.constraint_name
                    ORDER BY tc.table_name
                """))
                
                pks = list(result)
                for table_name, constraint_name, columns in pks:
                    f.write(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} PRIMARY KEY ({columns});\n")
                
                if pks:
                    f.write("\n")
                
                # 4. Contraintes de clé étrangère
                print("[*] Export des cles etrangeres...")
                f.write("-- ============================================================================\n")
                f.write("-- CONTRAINTES DE CLÉ ÉTRANGÈRE\n")
                f.write("-- ============================================================================\n\n")
                
                result = conn.execute(text("""
                    SELECT
                        tc.table_name,
                        tc.constraint_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name,
                        rc.update_rule,
                        rc.delete_rule
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    JOIN information_schema.referential_constraints AS rc
                        ON rc.constraint_name = tc.constraint_name
                        AND rc.constraint_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public'
                    ORDER BY tc.table_name, tc.constraint_name, kcu.ordinal_position
                """))
                
                fks = {}
                for row in result:
                    table_name, constraint_name, column_name, foreign_table, foreign_column, update_rule, delete_rule = row
                    if constraint_name not in fks:
                        fks[constraint_name] = {
                            'table': table_name,
                            'columns': [],
                            'foreign_table': foreign_table,
                            'foreign_columns': [],
                            'update_rule': update_rule,
                            'delete_rule': delete_rule
                        }
                    fks[constraint_name]['columns'].append(column_name)
                    fks[constraint_name]['foreign_columns'].append(foreign_column)
                
                for constraint_name, fk_info in fks.items():
                    columns = ', '.join(fk_info['columns'])
                    foreign_columns = ', '.join(fk_info['foreign_columns'])
                    f.write(f"ALTER TABLE {fk_info['table']} ADD CONSTRAINT {constraint_name} ")
                    f.write(f"FOREIGN KEY ({columns}) ")
                    f.write(f"REFERENCES {fk_info['foreign_table']} ({foreign_columns}) ")
                    f.write(f"ON UPDATE {fk_info['update_rule']} ON DELETE {fk_info['delete_rule']};\n")
                
                if fks:
                    f.write("\n")
                
                # 5. Contraintes UNIQUE
                print("[*] Export des contraintes UNIQUE...")
                f.write("-- ============================================================================\n")
                f.write("-- CONTRAINTES UNIQUE\n")
                f.write("-- ============================================================================\n\n")
                
                result = conn.execute(text("""
                    SELECT
                        tc.table_name,
                        tc.constraint_name,
                        string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as columns
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    WHERE tc.constraint_type = 'UNIQUE'
                    AND tc.table_schema = 'public'
                    AND tc.constraint_name NOT LIKE '%_pkey'
                    GROUP BY tc.table_name, tc.constraint_name
                    ORDER BY tc.table_name
                """))
                
                uniques = list(result)
                for table_name, constraint_name, columns in uniques:
                    f.write(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} UNIQUE ({columns});\n")
                
                if uniques:
                    f.write("\n")
                
                # 6. Index
                print("[*] Export des index...")
                f.write("-- ============================================================================\n")
                f.write("-- INDEX\n")
                f.write("-- ============================================================================\n\n")
                
                result = conn.execute(text("""
                    SELECT
                        schemaname,
                        tablename,
                        indexname,
                        indexdef
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                    AND indexname NOT LIKE '%_pkey'
                    ORDER BY tablename, indexname
                """))
                
                indexes = list(result)
                for schema, table, index_name, index_def in indexes:
                    f.write(f"{index_def};\n")
                
                if indexes:
                    f.write("\n")
                
                # 7. Séquences
                print("[*] Export des sequences...")
                f.write("-- ============================================================================\n")
                f.write("-- SÉQUENCES\n")
                f.write("-- ============================================================================\n\n")
                
                result = conn.execute(text("""
                    SELECT 
                        sequence_name,
                        data_type,
                        start_value,
                        minimum_value,
                        maximum_value,
                        increment,
                        cycle_option
                    FROM information_schema.sequences
                    WHERE sequence_schema = 'public'
                    ORDER BY sequence_name
                """))
                
                sequences = list(result)
                for seq_name, data_type, start_val, min_val, max_val, increment, cycle in sequences:
                    f.write(f"CREATE SEQUENCE {seq_name} ")
                    f.write(f"AS {data_type} ")
                    f.write(f"START WITH {start_val} ")
                    f.write(f"INCREMENT BY {increment} ")
                    f.write(f"MINVALUE {min_val} ")
                    f.write(f"MAXVALUE {max_val} ")
                    f.write(f"{'CYCLE' if cycle == 'YES' else 'NO CYCLE'};\n")
                
                if sequences:
                    f.write("\n")
                
                # 8. Résumé
                f.write("-- ============================================================================\n")
                f.write("-- RÉSUMÉ\n")
                f.write("-- ============================================================================\n\n")
                f.write(f"-- Tables: {len(tables)}\n")
                f.write(f"-- Types ENUM: {len(enums)}\n")
                f.write(f"-- Clés primaires: {len(pks)}\n")
                f.write(f"-- Clés étrangères: {len(fks)}\n")
                f.write(f"-- Contraintes UNIQUE: {len(uniques)}\n")
                f.write(f"-- Index: {len(indexes)}\n")
                f.write(f"-- Séquences: {len(sequences)}\n")
            
            print(f"\n[OK] Schema exporte avec succes dans: {output_file}")
            print(f"\n[*] Resume:")
            print(f"   - Tables: {len(tables)}")
            print(f"   - Types ENUM: {len(enums)}")
            print(f"   - Clés primaires: {len(pks)}")
            print(f"   - Clés étrangères: {len(fks)}")
            print(f"   - Contraintes UNIQUE: {len(uniques)}")
            print(f"   - Index: {len(indexes)}")
            print(f"   - Séquences: {len(sequences)}")
            
    except Exception as e:
        print(f"\n[ERREUR] ERREUR lors de l'export: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    export_schema()

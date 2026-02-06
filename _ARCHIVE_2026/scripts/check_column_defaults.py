#!/usr/bin/env python3
"""Script pour vérifier les valeurs par défaut des colonnes"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.database import get_db_connection

def check_defaults():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT column_name, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'exercises' 
            AND column_name IN ('created_at', 'updated_at', 'is_active', 'is_archived', 'view_count', 'ai_generated')
            ORDER BY column_name
        """)
        
        cols = cursor.fetchall()
        
        print("=" * 80)
        print("VALEURS PAR DÉFAUT DES COLONNES")
        print("=" * 80)
        print(f"{'Colonne':<20} {'DEFAULT':<50}")
        print("-" * 80)
        
        for col in cols:
            col_name, col_default = col
            default_str = str(col_default) if col_default else "NULL (pas de défaut)"
            print(f"{col_name:<20} {default_str:<50}")
        
        print("=" * 80)
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_defaults()


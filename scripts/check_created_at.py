#!/usr/bin/env python3
"""Script pour vérifier la valeur de created_at dans les exercices"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.database import get_db_connection
from psycopg2.extras import RealDictCursor

def check_created_at():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("SELECT id, created_at, updated_at FROM exercises ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        
        print("=" * 80)
        print("VÉRIFICATION CREATED_AT DANS LES EXERCICES")
        print("=" * 80)
        print(f"{'ID':<10} {'created_at':<30} {'Type':<20} {'updated_at':<30}")
        print("-" * 80)
        
        for row in rows:
            created_at = row['created_at']
            updated_at = row['updated_at']
            created_at_type = type(created_at).__name__
            created_at_str = str(created_at) if created_at else "NULL"
            updated_at_str = str(updated_at) if updated_at else "NULL"
            
            print(f"{row['id']:<10} {created_at_str:<30} {created_at_type:<20} {updated_at_str:<30}")
        
        print("=" * 80)
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_created_at()


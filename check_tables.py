#!/usr/bin/env python3
"""Script pour vérifier les tables existantes dans la base de données"""

from server.database import get_db_connection

def check_existing_tables():
    """Vérifier les tables existantes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Lister toutes les tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print("=== TABLES EXISTANTES ===")
        for table in tables:
            print(f"- {table[0]}")
        
        # Vérifier spécifiquement les tables du système de badges
        badge_tables = ['achievements', 'user_achievements']
        print("\n=== VÉRIFICATION SYSTÈME DE BADGES ===")
        for table in badge_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (table,))
            exists = cursor.fetchone()[0]
            status = "✅ EXISTE" if exists else "❌ MANQUANTE"
            print(f"{table}: {status}")
        
        # Vérifier les colonnes de gamification dans users
        print("\n=== VÉRIFICATION COLONNES GAMIFICATION USERS ===")
        gamification_columns = [
            'total_points', 'current_level', 'experience_points', 
            'jedi_rank', 'avatar_url'
        ]
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND table_schema = 'public'
        """)
        
        existing_columns = [col[0] for col in cursor.fetchall()]
        
        for col in gamification_columns:
            status = "✅ EXISTE" if col in existing_columns else "❌ MANQUANTE"
            print(f"{col}: {status}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    check_existing_tables() 
#!/usr/bin/env python3
"""Script pour vérifier le schéma de la table exercises"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.database import get_db_connection

def check_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'exercises' 
            ORDER BY ordinal_position
        """)
        
        cols = cursor.fetchall()
        
        print("=" * 80)
        print("SCHÉMA TABLE EXERCISES")
        print("=" * 80)
        print(f"{'Colonne':<30} {'Type':<20} {'NULL':<8} {'DEFAULT':<30}")
        print("-" * 80)
        
        for col in cols:
            col_name, data_type, is_nullable, col_default = col
            default_str = str(col_default) if col_default else "None"
            print(f"{col_name:<30} {data_type:<20} {is_nullable:<8} {default_str:<30}")
        
        print("=" * 80)
        print(f"Total: {len(cols)} colonnes")
        
        # Vérifier les colonnes mentionnées par l'utilisateur
        user_columns = [
            'id', 'title', 'creator_id', 'exercise_type', 'difficulty', 'tags',
            'question', 'correct_answer', 'choices', 'explanation', 'hint',
            'image_url', 'audio_url', 'is_active', 'is_archived', 'view_count',
            'created_at', 'updated_at', 'ai_generated', 'age_group', 'context_theme',
            'complexity', 'answer_type', 'text_metadata',
            'title_translations', 'question_translations', 'explanation_translations',
            'hint_translations', 'choices_translations'
        ]
        
        existing_cols = [col[0] for col in cols]
        missing_cols = [col for col in user_columns if col not in existing_cols]
        
        if missing_cols:
            print("\n⚠️  Colonnes mentionnées mais absentes de la BDD:")
            for col in missing_cols:
                print(f"  - {col}")
        else:
            print("\n✅ Toutes les colonnes mentionnées existent en BDD")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_schema()


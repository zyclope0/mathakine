#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification des index PostgreSQL
=================================
Verifie que les index crees par les migrations existent reellement en DB.
"""

import sys
import os
from pathlib import Path

# Fix encodage Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Ajouter le repertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.base import SessionLocal


def verify_indexes():
    """Verifie la presence des index en base de donnees"""
    
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("VERIFICATION DES INDEX POSTGRESQL")
        print("=" * 70)
        print()
        
        # Index attendus (crees par les migrations)
        expected_indexes = {
            'exercises': [
                'ix_exercises_creator_id',
                'ix_exercises_exercise_type',
                'ix_exercises_difficulty',
                'ix_exercises_is_active',
                'ix_exercises_created_at',
                'ix_exercises_type_difficulty',
                'ix_exercises_active_type',
                'ix_exercises_creator_active',
            ],
            'users': [
                'ix_users_created_at',
                'ix_users_is_active',
            ],
            'user_achievements': [
                'ix_user_achievements_user_achievement',
            ],
        }
        
        total_expected = 0
        total_found = 0
        missing_indexes = []
        
        for table, indexes in expected_indexes.items():
            print(f"TABLE: {table}")
            print("-" * 50)
            
            # Requete pour lister les index de la table
            query = text("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = :table_name 
                ORDER BY indexname
            """)
            
            result = db.execute(query, {'table_name': table}).fetchall()
            existing_indexes = {row[0]: row[1] for row in result}
            
            for idx_name in indexes:
                total_expected += 1
                if idx_name in existing_indexes:
                    total_found += 1
                    print(f"  [OK] {idx_name}")
                    # Afficher definition (tronquee)
                    definition = existing_indexes[idx_name]
                    if len(definition) > 80:
                        definition = definition[:77] + "..."
                    print(f"       -> {definition}")
                else:
                    print(f"  [MANQUANT] {idx_name}")
                    missing_indexes.append(f"{table}.{idx_name}")
            
            # Afficher autres index existants (non dans la liste)
            other_indexes = [k for k in existing_indexes if k not in indexes]
            if other_indexes:
                print(f"\n  Index supplementaires existants:")
                for idx in other_indexes[:5]:  # Limiter affichage
                    print(f"    - {idx}")
                if len(other_indexes) > 5:
                    print(f"    ... et {len(other_indexes) - 5} autres")
            
            print()
        
        # Resume
        print("=" * 70)
        print("RESUME")
        print("=" * 70)
        print(f"Index attendus:  {total_expected}")
        print(f"Index trouves:   {total_found}")
        print(f"Index manquants: {len(missing_indexes)}")
        
        if missing_indexes:
            print(f"\n[!] Index manquants:")
            for idx in missing_indexes:
                print(f"    - {idx}")
            print("\nAction: Executer 'alembic upgrade head' pour creer les index manquants")
            return False
        else:
            print("\n[OK] Tous les index attendus sont presents en DB!")
            return True
            
    finally:
        db.close()


if __name__ == "__main__":
    success = verify_indexes()
    sys.exit(0 if success else 1)

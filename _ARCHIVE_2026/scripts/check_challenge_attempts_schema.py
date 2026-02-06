"""
Script pour vérifier le schéma de la table logic_challenge_attempts
et tester l'insertion d'une tentative.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_db_connection
from loguru import logger

def check_schema():
    """Vérifie le schéma de la table logic_challenge_attempts"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Récupérer les informations sur les colonnes de la table
        query = """
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = 'logic_challenge_attempts'
            ORDER BY ordinal_position;
        """
        cursor.execute(query)
        columns = cursor.fetchall()
        
        print("\n=== SCHÉMA DE LA TABLE logic_challenge_attempts ===\n")
        for col in columns:
            print(f"Colonne: {col['column_name']}")
            print(f"  Type: {col['data_type']}")
            print(f"  Nullable: {col['is_nullable']}")
            print(f"  Default: {col['column_default']}")
            print()
        
        # Vérifier les contraintes
        query_constraints = """
            SELECT 
                constraint_name,
                constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = 'logic_challenge_attempts';
        """
        cursor.execute(query_constraints)
        constraints = cursor.fetchall()
        
        print("\n=== CONTRAINTES ===\n")
        for constraint in constraints:
            print(f"{constraint['constraint_type']}: {constraint['constraint_name']}")
        
        # Vérifier les données existantes
        query_data = """
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN is_correct = true THEN 1 END) as correct
            FROM logic_challenge_attempts;
        """
        cursor.execute(query_data)
        stats = cursor.fetchone()
        
        print(f"\n=== STATISTIQUES ===\n")
        print(f"Total tentatives: {stats['total']}")
        print(f"Tentatives correctes: {stats['correct']}")
        
        # Afficher quelques exemples de tentatives
        query_examples = """
            SELECT id, user_id, challenge_id, user_solution, is_correct, 
                   time_spent, hints_used, created_at
            FROM logic_challenge_attempts
            ORDER BY created_at DESC
            LIMIT 5;
        """
        cursor.execute(query_examples)
        examples = cursor.fetchall()
        
        print(f"\n=== DERNIÈRES TENTATIVES (max 5) ===\n")
        for ex in examples:
            print(f"ID: {ex['id']}")
            print(f"  user_id: {ex['user_id']}")
            print(f"  challenge_id: {ex['challenge_id']}")
            print(f"  user_solution: {ex['user_solution']}")
            print(f"  is_correct: {ex['is_correct']}")
            print(f"  time_spent: {ex['time_spent']}")
            print(f"  hints_used: {ex['hints_used']} (type: {type(ex['hints_used']).__name__})")
            print(f"  created_at: {ex['created_at']}")
            print()
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du schéma: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_schema()


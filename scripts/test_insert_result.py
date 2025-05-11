import psycopg2
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

def main():
    """
    Script de test pour insérer manuellement une entrée dans la table results
    et vérifier que l'insertion fonctionne correctement.
    """
    # Charger les variables d'environnement
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("Erreur: La variable DATABASE_URL n'est pas définie dans le fichier .env")
        sys.exit(1)
    
    print(f"Connexion à la base de données PostgreSQL...")
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        conn.autocommit = True  # Important pour voir les changements immédiatement
        
        # 1. Vérifier l'état actuel de la table results
        cursor.execute("SELECT COUNT(*) FROM results")
        count_before = cursor.fetchone()[0]
        print(f"Nombre d'enregistrements dans la table results avant insertion: {count_before}")
        
        # 2. Récupérer un exercice existant pour l'utiliser dans le test
        cursor.execute("SELECT id FROM exercises LIMIT 1")
        exercise_row = cursor.fetchone()
        if not exercise_row:
            print("Erreur: Aucun exercice trouvé dans la base de données.")
            conn.close()
            sys.exit(1)
        
        exercise_id = exercise_row[0]
        print(f"Utilisation de l'exercice avec ID {exercise_id} pour le test")
        
        # 3. Insérer un nouveau résultat
        print("Tentative d'insertion d'un nouveau résultat...")
        
        # Directement avec la requête SQL complète
        cursor.execute("""
        INSERT INTO results (exercise_id, is_correct, attempt_count, time_spent)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """, (exercise_id, True, 1, 10.5))
        
        result_id = cursor.fetchone()[0]
        print(f"Résultat inséré avec succès, ID: {result_id}")
        
        # 4. Vérifier que l'insertion a bien fonctionné
        cursor.execute("SELECT COUNT(*) FROM results")
        count_after = cursor.fetchone()[0]
        print(f"Nombre d'enregistrements dans la table results après insertion: {count_after}")
        
        if count_after > count_before:
            print("✅ TEST RÉUSSI: L'insertion dans la table results fonctionne correctement.")
        else:
            print("❌ TEST ÉCHOUÉ: Aucune augmentation du nombre d'enregistrements dans la table results.")
        
        # 5. Afficher le dernier enregistrement inséré
        cursor.execute("""
        SELECT id, exercise_id, is_correct, attempt_count, time_spent, created_at
        FROM results
        WHERE id = %s
        """, (result_id,))
        
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        result = dict(zip(columns, row))
        
        print("\nDétails du résultat inséré:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Erreur lors de l'exécution du test: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Connexion à la base de données fermée.")

if __name__ == "__main__":
    main() 
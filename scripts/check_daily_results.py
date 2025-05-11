import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

def main():
    """
    Script pour vérifier les résultats par jour dans la table results
    """
    # Charger les variables d'environnement
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    print(f"Connexion à la base de données PostgreSQL...")
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Obtenir les résultats par jour
        cursor.execute("""
        SELECT DATE(created_at) as day, COUNT(*) 
        FROM results 
        GROUP BY day 
        ORDER BY day DESC 
        LIMIT 10
        """)
        
        rows = cursor.fetchall()
        print(f"Résultats par jour (10 derniers jours):")
        for row in rows:
            print(f"- {row[0]}: {row[1]} résultats")
            
        # Vérifier si les résultats d'aujourd'hui sont bien comptés
        today = datetime.now().date()
        cursor.execute("""
        SELECT COUNT(*) 
        FROM results 
        WHERE DATE(created_at) = %s
        """, (today,))
        
        today_count = cursor.fetchone()[0]
        print(f"\nRésultats pour aujourd'hui ({today}): {today_count}")
        
        # Vérifier que les données sont bien prises en compte dans la requête GET_EXERCISES_BY_DAY
        # Utiliser directement la requête SQL au lieu d'importer le module
        get_exercises_by_day_sql = """
        SELECT 
            DATE(created_at) as exercise_date,
            COUNT(*) as count
        FROM results
        GROUP BY DATE(created_at)
        ORDER BY exercise_date DESC
        LIMIT 30
        """
        
        cursor.execute(get_exercises_by_day_sql)
        daily_data = cursor.fetchall()
        
        print(f"\nDonnées quotidiennes retournées par GET_EXERCISES_BY_DAY:")
        for row in daily_data:
            print(f"- {row[0]}: {row[1]} exercices")
        
    except Exception as e:
        print(f"Erreur lors de la vérification des résultats: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("Connexion à la base de données fermée.")

if __name__ == "__main__":
    main() 
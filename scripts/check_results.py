import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

def main():
    """
    Ce script vérifie les enregistrements récents dans la table results
    pour confirmer que l'insertion fonctionne correctement.
    """
    # Charger les variables d'environnement
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    print("Connexion à la base de données PostgreSQL...")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Afficher le nombre total d'enregistrements
    cursor.execute("SELECT COUNT(*) FROM results")
    total_count = cursor.fetchone()[0]
    print(f"Nombre total d'enregistrements dans la table results: {total_count}")
    
    # Récupérer les 10 derniers enregistrements
    cursor.execute("""
    SELECT id, exercise_id, is_correct, time_spent, DATE(created_at) as date, created_at 
    FROM results 
    ORDER BY id DESC 
    LIMIT 10
    """)
    
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()
    
    print("\nDerniers enregistrements dans la table results:")
    print("-" * 80)
    print(f"{columns[0]:<5} | {columns[1]:<10} | {columns[2]:<10} | {columns[3]:<10} | {columns[4]:<12} | {columns[5]}")
    print("-" * 80)
    
    for row in results:
        time_value = f"{row[3]:.2f}" if row[3] is not None else "None"
        print(f"{row[0]:<5} | {row[1]:<10} | {str(row[2]):<10} | {time_value:<10} | {row[4]} | {row[5]}")
    
    # Récupérer le nombre d'enregistrements par jour
    cursor.execute("""
    SELECT DATE(created_at) as day, COUNT(*) as count
    FROM results
    GROUP BY DATE(created_at)
    ORDER BY day DESC
    LIMIT 7
    """)
    
    days = cursor.fetchall()
    
    print("\nNombre d'enregistrements par jour:")
    print("-" * 40)
    print(f"{'Date':<12} | {'Nombre d''enregistrements'}")
    print("-" * 40)
    
    for day in days:
        print(f"{day[0]} | {day[1]}")
    
    conn.close()

if __name__ == "__main__":
    main() 
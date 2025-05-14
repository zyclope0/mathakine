import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("Erreur: DATABASE_URL non définie")
    exit(1)

try:
    # Se connecter à PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Vérifier les colonnes de la table exercises
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'exercises'
        ORDER BY ordinal_position
    """)
    
    print("Colonnes de la table exercises:")
    for row in cursor.fetchall():
        print(f"- {row[0]}: {row[1]}")
    
    conn.close()

except Exception as e:
    print(f"Erreur: {e}")
    exit(1) 
import psycopg2
import os
from dotenv import load_dotenv

def main():
    """
    Ce script vérifie la structure actuelle de la table results
    """
    # Charger les variables d'environnement
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    print("Connexion à la base de données PostgreSQL...")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Vérifier la structure de la table
    cursor.execute("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'results' 
    ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    
    print("\nStructure de la table results:")
    print("-" * 60)
    print(f"{'Colonne':<20} | {'Type':<20} | {'Nullable'}")
    print("-" * 60)
    
    for col in columns:
        nullable = "OUI" if col[2] == 'YES' else "NON"
        print(f"{col[0]:<20} | {col[1]:<20} | {nullable}")
    
    # Vérifier si la table a des enregistrements
    cursor.execute("SELECT COUNT(*) FROM results")
    count = cursor.fetchone()[0]
    print(f"\nNombre total d'enregistrements: {count}")
    
    if count > 0:
        # Récupérer un exemple d'enregistrement
        cursor.execute("SELECT * FROM results ORDER BY id DESC LIMIT 1")
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        
        print("\nExemple d'enregistrement:")
        print("-" * 60)
        for i, col in enumerate(columns):
            print(f"{col:<20}: {row[i]}")
    
    conn.close()

if __name__ == "__main__":
    main() 
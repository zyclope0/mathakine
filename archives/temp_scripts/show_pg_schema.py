import os
import sys
import psycopg2
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer l'URL de la base de données PostgreSQL
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("Erreur: Variable DATABASE_URL non définie dans le fichier .env")
    sys.exit(1)

try:
    # Connexion à PostgreSQL
    print(f"Connexion à PostgreSQL...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    # Récupérer la liste des tables
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)

    tables = cursor.fetchall()
    print(f"\nTables dans la base de données ({len(tables)}):")

    for i, table in enumerate(tables, 1):
        table_name = table[0]
        print(f"\n{i}. Table: {table_name}")

        # Récupérer les colonnes de la table
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)

        columns = cursor.fetchall()
        print(f"   Colonnes ({len(columns)}):")

        for col in columns:
            col_name = col[0]
            col_type = col[1]
            is_nullable = col[2]
            print(f"   - {col_name} ({col_type}) {'NULL' if is_nullable == 'YES' else 'NOT NULL'}")

        # Récupérer le nombre d'enregistrements
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   Nombre d'enregistrements: {count}")

    # Fermer la connexion
    conn.close()
    print("\nConnexion fermée.")

except Exception as e:
    print(f"Erreur lors de la connexion à PostgreSQL: {e}")
    sys.exit(1)

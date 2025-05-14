"""
Teste la connexion à PostgreSQL.
"""

import psycopg2
import os
import sys

# Charger les variables d'environnement depuis .env
from dotenv import load_dotenv
load_dotenv()

password = os.getenv('POSTGRES_PASSWORD', 'postgres')

# Afficher les paramètres de connexion
print("Tentative de connexion à PostgreSQL avec les paramètres suivants:")
print(f"  Hôte: localhost")
print(f"  Port: 5432")
print(f"  Base: postgres")
print(f"  Utilisateur: postgres")
print(f"  Mot de passe: ********")

try:
    # Établir la connexion
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password=password,  # Utiliser le mot de passe du fichier .env
        host='localhost',
        port='5432'
    )
    
    print("Connexion réussie!")
    
    # Tester une requête simple
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"Version de PostgreSQL: {version}")
    
    # Fermer la connexion
    conn.close()
    print("Connexion fermée.")
    
except Exception as e:
    print(f"Erreur de connexion: {e}")
    import traceback
    print(traceback.format_exc())
    sys.exit(1) 
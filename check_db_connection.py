"""
Vérifie la connexion à la base de données configurée dans .env
"""

import os
import re
import urllib.parse
from sqlalchemy import create_engine, text, inspect

# Lire le fichier .env directement
env_path = os.path.join(os.getcwd(), ".env")
db_url = None

with open(env_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('DATABASE_URL='):
            db_url = line.strip().split('=', 1)[1].strip("'\"")
            break

if not db_url:
    print("URL de base de données non trouvée dans le fichier .env")
    exit(1)

print(f"URL de la base de données: {db_url}")

# Déterminer le type de base de données
if db_url.startswith('sqlite'):
    print("Type de base de données: SQLite")
elif db_url.startswith('postgresql'):
    print("Type de base de données: PostgreSQL")
else:
    print(f"Type de base de données inconnu: {db_url.split('://')[0] if '://' in db_url else 'Inconnu'}")

try:
    # Créer un moteur SQLAlchemy
    engine = create_engine(db_url)
    
    # Tester la connexion
    with engine.connect() as conn:
        # Exécuter une requête pour obtenir la version
        if db_url.startswith('sqlite'):
            result = conn.execute(text("SELECT sqlite_version();"))
        else:
            result = conn.execute(text("SELECT version();"))
        
        version = result.fetchone()[0]
        print(f"Connexion réussie à la base de données!")
        print(f"Version: {version}")
        
        # Vérifier les tables en utilisant l'inspecteur SQLAlchemy
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("\nTables disponibles:")
        for table_name in tables:
            # Compter le nombre d'entrées
            count_query = f"SELECT COUNT(*) FROM \"{table_name}\""
            try:
                count = conn.execute(text(count_query)).fetchone()[0]
                print(f"  - {table_name}: {count} enregistrements")
            except Exception as e:
                print(f"  - {table_name}: Erreur de comptage - {str(e)}")
    
    print("\nTest de connexion à la base de données réussi!")
except Exception as e:
    print(f"Erreur de connexion à la base de données: {str(e)}")
    import traceback
    print(traceback.format_exc()) 
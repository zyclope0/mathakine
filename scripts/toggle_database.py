"""
Script permettant de basculer entre SQLite et PostgreSQL.
"""

import os
import argparse
from dotenv import load_dotenv, set_key

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Basculer entre SQLite et PostgreSQL")
    parser.add_argument("db_type", choices=["sqlite", "postgres"], help="Type de base de données à utiliser")
    args = parser.parse_args()
    
    # Charger les variables d'environnement
    env_path = os.path.join(os.getcwd(), ".env")
    load_dotenv(env_path)
    
    # Configurations de base de données
    postgres_url = f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'postgres')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'mathakine_test')}"
    sqlite_url = "sqlite:///./math_trainer.db"
    
    if args.db_type == "postgres":
        print(f"Configuration de l'application pour utiliser PostgreSQL...")
        set_key(env_path, "DATABASE_URL", postgres_url)
        print(f"Base de données configurée pour PostgreSQL: {postgres_url}")
    else:
        print(f"Configuration de l'application pour utiliser SQLite...")
        set_key(env_path, "DATABASE_URL", sqlite_url)
        print(f"Base de données configurée pour SQLite: {sqlite_url}")
    
    print("\nRedémarrez l'application pour appliquer les changements.")

if __name__ == "__main__":
    main() 
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
    postgres_url = f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD'
        , 'postgres')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'mathakine_test')}"
    sqlite_url = "sqlite:///./math_trainer.db"

    # Lire le fichier .env actuel
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Modifier la ligne DATABASE_URL
    with open(env_path, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.startswith('DATABASE_URL='):
                if args.db_type == "postgres":
                    f.write(f'DATABASE_URL={postgres_url}\n')
                    print(f"Configuration de l'application pour utiliser PostgreSQL...")
                    print(f"Base de données configurée pour PostgreSQL: {postgres_url}")
                else:
                    f.write(f'DATABASE_URL={sqlite_url}\n')
                    print(f"Configuration de l'application pour utiliser SQLite...")
                    print(f"Base de données configurée pour SQLite: {sqlite_url}")
            else:
                f.write(line)

    print("\nRedémarrez l'application pour appliquer les changements.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Prépare la base de test locale : vérifie PostgreSQL, crée la base, applique les migrations et les données de test.
Usage: python scripts/check_local_db.py
"""
import os
import sys

# Répertoire projet pour imports
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

TEST_URL = "postgresql://postgres:postgres@localhost:5432/test_mathakine"


def main():
    print("\n=== Diagnostic base de données locale ===\n")

    # 1. Docker (optionnel - juste info)
    print("1. Vérification connexion localhost:5432...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            "postgresql://postgres:postgres@localhost:5432/postgres",
            connect_timeout=3
        )
        conn.close()
        print("   OK: PostgreSQL répond sur localhost:5432")
    except Exception as e:
        print(f"   ECHEC: {e}")
        print("\n   Cause probable: PostgreSQL n'est pas démarré.")
        print("   Solutions:")
        print("   - Docker: docker run -d --name pg-test -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15")
        print("   - Ou installer PostgreSQL: https://www.postgresql.org/download/windows/")
        return 1

    # 2. Base test_mathakine
    print("\n2. Base test_mathakine...")
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/postgres", connect_timeout=3)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname='test_mathakine'")
        if cur.fetchone():
            print("   OK: La base existe")
        else:
            cur.execute("CREATE DATABASE test_mathakine")
            print("   OK: Base créée")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"   Erreur: {e}")
        return 1

    # 3. Connexion directe à test_mathakine
    print("\n3. Connexion à test_mathakine...")
    try:
        import psycopg2
        conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/test_mathakine", connect_timeout=3)
        conn.close()
        print("   OK: Connexion OK")
    except Exception as e:
        print(f"   Erreur: {e}")
        return 1

    # 4. Schéma et données de test (migrations Alembic + Yoda, ObiWan, etc.)
    print("\n4. Schéma et données de test...")
    try:
        os.environ["TESTING"] = "true"
        os.environ["TEST_DATABASE_URL"] = TEST_URL
        os.environ["DATABASE_URL"] = TEST_URL

        from app.db.init_db import create_tables_with_test_data
        create_tables_with_test_data()
        print("   OK: Schéma à jour, données de test prêtes")
    except Exception as e:
        print(f"   Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n=== Prêt. Tu peux lancer: python -m pytest tests/ ===\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())

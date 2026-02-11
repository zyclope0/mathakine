#!/usr/bin/env python3
"""
Diagnostic : base PostgreSQL locale pour les tests.
Usage: python scripts/check_local_db.py
"""
import sys

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
        print("   OK: Prêt pour les tests")
    except Exception as e:
        print(f"   Erreur: {e}")
        return 1

    print("\n=== Tout est OK. Tu peux lancer: python -m pytest tests/ ===\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())

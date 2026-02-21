#!/usr/bin/env python3
"""
Commande unique pour lancer les tests backend en local.
Démarre PostgreSQL (Docker si besoin), initialise la DB, lance pytest.

Usage: python scripts/test_backend_local.py
       ou: make test-backend-local
"""
import os
import subprocess
import sys
import time

# Répertoire projet = parent de scripts/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# URL de test (aligné CI)
TEST_URL = "postgresql://postgres:postgres@localhost:5432/test_mathakine"
CONTAINER_NAME = "pg-mathakine"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Exécute une commande."""
    return subprocess.run(cmd, check=check, capture_output=False)


def pg_ready(timeout: int = 30) -> bool:
    """Vérifie si PostgreSQL répond sur localhost:5432."""
    import psycopg2
    end = time.time() + timeout
    while time.time() < end:
        try:
            conn = psycopg2.connect(
                "postgresql://postgres:postgres@localhost:5432/postgres",
                connect_timeout=2,
            )
            conn.close()
            return True
        except Exception:
            time.sleep(1)
    return False


def ensure_pg_running() -> bool:
    """Démarre PostgreSQL (Docker) si absent. Retourne True si prêt."""
    if pg_ready(timeout=3):
        print("   OK: PostgreSQL déjà démarré")
        return True

    print("   PostgreSQL absent. Tentative de démarrage via Docker...")
    try:
        # Vérifier si le conteneur existe déjà (arrêté)
        r = subprocess.run(
            ["docker", "ps", "-a", "-q", "-f", f"name={CONTAINER_NAME}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            subprocess.run(["docker", "start", CONTAINER_NAME], check=True, capture_output=True, timeout=10)
            print(f"   Conteneur {CONTAINER_NAME} redémarré")
        else:
            subprocess.run(
                [
                    "docker", "run", "-d",
                    "--name", CONTAINER_NAME,
                    "-e", "POSTGRES_PASSWORD=postgres",
                    "-p", "5432:5432",
                    "postgres:15",
                ],
                check=True,
                capture_output=True,
                timeout=30,
            )
            print(f"   Conteneur {CONTAINER_NAME} créé et démarré")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("\n   ECHEC: Docker non disponible ou erreur.")
        print("   Démarrer PostgreSQL manuellement :")
        print(f"   docker run -d --name {CONTAINER_NAME} -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15")
        return False

    if not pg_ready(timeout=20):
        print("   ECHEC: PostgreSQL ne répond pas après démarrage")
        return False
    print("   OK: PostgreSQL prêt")
    return True


def create_test_db():
    """Crée la base test_mathakine si elle n'existe pas."""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/postgres", connect_timeout=5)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", ("test_mathakine",))
    if cur.fetchone():
        print("   OK: Base test_mathakine existe")
    else:
        cur.execute("CREATE DATABASE test_mathakine")
        print("   OK: Base test_mathakine créée")
    cur.close()
    conn.close()


def init_schema():
    """Initialise le schéma et les données de test."""
    os.environ["TESTING"] = "true"
    os.environ["TEST_DATABASE_URL"] = TEST_URL
    os.environ["DATABASE_URL"] = TEST_URL

    from app.db.init_db import create_tables_with_test_data
    create_tables_with_test_data()
    print("   OK: Schéma et données de test initialisés")


def run_pytest():
    """Lance pytest avec les mêmes options que la CI."""
    os.environ["TESTING"] = "true"
    os.environ["TEST_DATABASE_URL"] = TEST_URL
    os.environ["DATABASE_URL"] = TEST_URL
    os.environ["SECRET_KEY"] = "test-secret-key-for-ci-cd-pipeline"

    import pytest
    args = [
        "tests/",
        "-v",
        "--ignore=tests/archives/",
        "--cov=app",
        "--cov=server",
        "--cov-report=term-missing",
        "--tb=short",
        '-m', "not slow",
    ]
    return pytest.main(args)


def main():
    print("\n=== Tests backend (local) ===\n")

    print("1. PostgreSQL...")
    if not ensure_pg_running():
        return 1

    print("\n2. Base de test...")
    create_test_db()

    print("\n3. Initialisation schéma...")
    init_schema()

    print("\n4. pytest...")
    code = run_pytest()

    print("\n=== Fin ===\n")
    return code


if __name__ == "__main__":
    sys.exit(main())

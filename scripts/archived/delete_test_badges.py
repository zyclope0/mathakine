#!/usr/bin/env python3
"""
Suppression hard des badges test (test, test2).

Usage:
    python scripts/delete_test_badges.py              # Dry-run
    python scripts/delete_test_badges.py --execute    # Supprime effectivement
"""
import argparse
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

from sqlalchemy import create_engine, text

CODES_TO_DELETE = ("test", "test2")


def get_db_url():
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        print("Erreur: DATABASE_URL non défini dans .env")
        sys.exit(1)
    return url


def main():
    ap = argparse.ArgumentParser(description="Suppression hard des badges test")
    ap.add_argument("--execute", action="store_true", help="Exécuter la suppression")
    args = ap.parse_args()

    db_url = get_db_url()
    if not db_url:
        print("Erreur: DATABASE_URL non défini.")
        sys.exit(1)

    engine = create_engine(db_url)
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT id, code, name FROM achievements WHERE code IN ('test', 'test2')"
            )
        ).fetchall()

        if not rows:
            print("Aucun badge 'test' ou 'test2' trouve.")
            return

        print("Badges a supprimer :")
        for r in rows:
            print(f"  - id={r[0]}, code={r[1]}, name={r[2]}")

        ids = [r[0] for r in rows]
        ids_ph = ",".join(str(i) for i in ids)
        ua_count = conn.execute(
            text(
                f"SELECT COUNT(*) FROM user_achievements "
                f"WHERE achievement_id IN ({ids_ph})"
            )
        ).scalar()

        print(f"\n  -> {ua_count} user_achievements seront supprimes (cascade)")

        if not args.execute:
            print("\n>> Dry-run. Relancer avec --execute pour supprimer.")
            return

        conn.execute(
            text("DELETE FROM achievements WHERE code IN ('test', 'test2')")
        )
        conn.commit()
        print(f"\n[OK] {len(rows)} badge(s) supprime(s).")


if __name__ == "__main__":
    main()

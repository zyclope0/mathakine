#!/usr/bin/env python3
"""
Vide la table edtech_events (tous les événements EdTech).

Usage:
  python scripts/truncate_edtech_events.py --confirm
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

if "TESTING" not in os.environ:
    os.environ["TESTING"] = "false"


def main():
    if "--confirm" not in sys.argv:
        print("Usage: python scripts/truncate_edtech_events.py --confirm")
        print("Vide la table edtech_events. Ajoutez --confirm pour exécuter.")
        return 1

    from sqlalchemy import create_engine, text
    from app.core.config import settings
    from urllib.parse import urlparse

    url = settings.SQLALCHEMY_DATABASE_URL
    parsed = urlparse(url)
    target = f"{parsed.hostname or 'localhost'}:{parsed.port or 5432}/{parsed.path.lstrip('/') or '?'}"
    print(f"Base ciblée : {target}\n")

    engine = create_engine(url)
    with engine.connect() as conn:
        r = conn.execute(text("SELECT COUNT(*) FROM edtech_events"))
        count = r.scalar() or 0
        print(f"Lignes à supprimer : {count}")

        conn.execute(text("TRUNCATE TABLE edtech_events RESTART IDENTITY"))
        conn.commit()
        print("Table edtech_events vidée.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

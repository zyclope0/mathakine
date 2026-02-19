#!/usr/bin/env python3
"""
Script pour ajouter la colonne pinned_badge_ids à la table users.
À exécuter sur la base de test si les migrations Alembic ne peuvent pas
s'exécuter complètement (ex: état désynchronisé de la base de test).

Usage:
    TESTING=true python scripts/add_pinned_badges_to_test_db.py

Ou avec DATABASE_URL pointant vers la base de test :
    DATABASE_URL="postgresql://.../test_mathakine" python scripts/add_pinned_badges_to_test_db.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(override=True)

if os.environ.get("TESTING", "").lower() != "true":
    os.environ.setdefault("TEST_DATABASE_URL", os.environ.get("DATABASE_URL", ""))

from sqlalchemy import create_engine, text
from app.core.config import settings


def main():
    url = settings.SQLALCHEMY_DATABASE_URL
    if "test" not in url.lower() and "localhost" not in url:
        print("⚠️  ATTENTION: Ce script modifie la base de données.")
        print("   Pour la base de test, utilisez: TESTING=true python scripts/add_pinned_badges_to_test_db.py")
        if input("   Continuer quand même ? (y/N): ").lower() != "y":
            sys.exit(1)

    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'pinned_badge_ids'
        """))
        if result.fetchone():
            print("OK Colonne pinned_badge_ids existe déjà.")
            conn.commit()
            return

        print("Ajout de la colonne pinned_badge_ids...")
        conn.execute(text("""
            ALTER TABLE users
            ADD COLUMN pinned_badge_ids JSONB NULL
        """))
        conn.commit()

    print("OK Colonne pinned_badge_ids ajoutée.")


if __name__ == "__main__":
    main()

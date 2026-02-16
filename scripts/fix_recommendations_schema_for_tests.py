#!/usr/bin/env python3
"""
Script pour ajouter les colonnes manquantes (challenge_id, recommendation_type) à la table
recommendations. À exécuter sur la base de test si les migrations Alembic ne peuvent pas
s'exécuter complètement (ex: base créée par create_all ou init script).

Usage:
    TESTING=true python scripts/fix_recommendations_schema_for_tests.py

Ou avec DATABASE_URL pointant vers la base de test :
    DATABASE_URL="postgresql://.../test_mathakine" python scripts/fix_recommendations_schema_for_tests.py
"""
import os
import sys
from pathlib import Path

# Ajouter la racine du projet au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Charger .env avant les imports
from dotenv import load_dotenv
load_dotenv(override=True)

# TESTING=true pour utiliser TEST_DATABASE_URL
if os.environ.get("TESTING", "").lower() != "true":
    os.environ.setdefault("TEST_DATABASE_URL", os.environ.get("DATABASE_URL", ""))

from sqlalchemy import create_engine, text
from app.core.config import settings

def main():
    url = settings.SQLALCHEMY_DATABASE_URL
    if "test" not in url.lower() and "localhost" not in url:
        print("⚠️  ATTENTION: Ce script modifie la base de données.")
        print("   Pour la base de test, utilisez: TESTING=true python scripts/fix_recommendations_schema_for_tests.py")
        if input("   Continuer quand même ? (y/N): ").lower() != "y":
            sys.exit(1)

    engine = create_engine(url)
    with engine.connect() as conn:
        # Vérifier si challenge_id existe
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'recommendations' AND column_name = 'challenge_id'
        """))
        if result.fetchone():
            print("OK Colonne challenge_id existe deja.")
            return

        print("Ajout de la colonne challenge_id...")
        conn.execute(text("""
            ALTER TABLE recommendations
            ADD COLUMN challenge_id INTEGER
            REFERENCES logic_challenges(id) ON DELETE SET NULL
        """))
        conn.execute(text("CREATE INDEX ix_recommendations_challenge_id ON recommendations (challenge_id)"))
        conn.commit()

        # recommendation_type
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'recommendations' AND column_name = 'recommendation_type'
        """))
        if result.fetchone():
            print("OK Colonne recommendation_type existe deja.")
        else:
            print("Ajout de la colonne recommendation_type...")
            conn.execute(text("""
                ALTER TABLE recommendations
                ADD COLUMN recommendation_type VARCHAR(20) NOT NULL DEFAULT 'exercise'
            """))
            conn.commit()

    print("OK Schema recommendations mis a jour.")

if __name__ == "__main__":
    main()

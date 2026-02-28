#!/usr/bin/env python3
"""
Reset de tous les badges et du classement pour tous les utilisateurs.

Usage:
    python scripts/reset_all_badges.py              # Mode dry-run
    python scripts/reset_all_badges.py --execute     # Execution

Effets:
  - Supprime user_achievements
  - Vide pinned_badge_ids
  - Reset classement : total_points=0, current_level=1, experience_points=0, jedi_rank='youngling'
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


def get_db_url():
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("Erreur: DATABASE_URL non défini. Définir dans .env ou l'environnement.")
        sys.exit(1)
    return db_url


def run_reset(dry_run: bool = True):
    engine = create_engine(get_db_url())
    with engine.connect() as conn:
        # Compter les lignes avant
        r = conn.execute(text("SELECT COUNT(*) FROM user_achievements")).scalar()
        badge_count = r
        users_with_pins = conn.execute(
            text("SELECT COUNT(*) FROM users WHERE pinned_badge_ids IS NOT NULL")
        ).scalar()
        users_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()

        print(
            "=== Reset badges + classement — mode",
            "DRY-RUN (simulation)" if dry_run else "EXECUTION",
            "===\n",
        )
        print(f"  user_achievements a supprimer : {badge_count}")
        print(
            f"  utilisateurs avec badges epingles a reinitialiser : {users_with_pins}"
        )
        print(f"  utilisateurs a remettre a zero (classement) : {users_count}")

        if dry_run:
            print("\n>> Aucune modification. Relancer avec --execute pour appliquer.")
            return

        ok = input(
            "\nConfirmer le reset badges + classement pour TOUS les utilisateurs ? (oui/non) : "
        )
        if ok.strip().lower() != "oui":
            print("Annule.")
            return

        conn.execute(text("DELETE FROM user_achievements"))
        conn.execute(text("UPDATE users SET pinned_badge_ids = NULL"))
        conn.execute(
            text(
                "UPDATE users SET total_points = 0, current_level = 1, experience_points = 0, jedi_rank = 'youngling'"
            )
        )
        conn.commit()
        print("\n[OK] Reset termine (badges + classement).")


def main():
    ap = argparse.ArgumentParser(
        description="Reset tous les badges pour tous les utilisateurs"
    )
    ap.add_argument(
        "--execute", action="store_true", help="Exécuter le reset (sinon dry-run)"
    )
    args = ap.parse_args()
    run_reset(dry_run=not args.execute)


if __name__ == "__main__":
    main()

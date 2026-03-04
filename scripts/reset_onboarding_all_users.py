#!/usr/bin/env python3
"""
Réinitialise onboarding_completed_at à NULL pour tous les utilisateurs.

Effet : au prochain login, chaque utilisateur sera redirigé vers /onboarding,
puis vers /diagnostic (F03) après soumission.

Usage:
    python scripts/reset_onboarding_all_users.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(override=False)

from app.db.base import SessionLocal
from app.models.user import User


def main():
    db = SessionLocal()
    try:
        count = db.query(User).update({User.onboarding_completed_at: None})
        db.commit()
        print(f"onboarding_completed_at mis à NULL pour {count} utilisateur(s).")
    except Exception as e:
        db.rollback()
        print(f"Erreur: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

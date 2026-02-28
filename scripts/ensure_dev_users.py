#!/usr/bin/env python3
"""
Ajoute ObiWan et les utilisateurs de dev s'ils n'existent pas.
Fixe aussi is_email_verified=True pour ces utilisateurs s'ils existent déjà (ex: créés avant la mise à jour).

Utile quand la base contient déjà des utilisateurs (ex: fixtures pytest) mais pas ObiWan,
ou quand ObiWan existe mais n'est pas vérifié.

Usage:
    $env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_mathakine"
    python scripts/ensure_dev_users.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(override=False)

from datetime import datetime

from app.db.base import SessionLocal
from app.models.user import User, UserRole

DEV_USERS = [
    (
        "ObiWan",
        "obiwan.kenobi@jedi-temple.sw",
        "$2b$12$YwQHz5jRyMGFUgvDelz/7.lWPY.sEePXKYhWEHcYJLZ2j3mLRl7uy",
        "Obi-Wan Kenobi",
        UserRole.MAITRE,
        12,
    ),
    (
        "maitre_yoda",
        "yoda@jedi-temple.sw",
        "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "Maître Yoda",
        UserRole.MAITRE,
        12,
    ),
    (
        "padawan1",
        "padawan1@jedi-temple.sw",
        "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "Anakin Skywalker",
        UserRole.PADAWAN,
        5,
    ),
    (
        "gardien1",
        "gardien1@jedi-temple.sw",
        "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "Mace Windu",
        UserRole.GARDIEN,
        10,
    ),
]


def main():
    url = os.environ.get("DATABASE_URL", "")
    if not url or ("localhost" not in url and "127.0.0.1" not in url):
        print(
            "Usage: DATABASE_URL vers base locale (ex: postgresql://...@localhost:5432/test_mathakine)"
        )
        sys.exit(1)

    db = SessionLocal()
    try:
        added = []
        fixed = []
        for username, email, hp, full_name, role, grade in DEV_USERS:
            u = db.query(User).filter(User.username == username).first()
            if u:
                if not u.is_email_verified:
                    u.is_email_verified = True
                    fixed.append(username)
                continue
            u = User(
                username=username,
                email=email,
                hashed_password=hp,
                full_name=full_name,
                role=role,
                grade_level=grade,
                created_at=datetime.now(),
                is_email_verified=True,
            )
            db.add(u)
            added.append(username)
        db.commit()
        if added:
            print(f"OK: {len(added)} utilisateur(s) ajouté(s): {', '.join(added)}")
        if fixed:
            print(
                f"OK: {len(fixed)} utilisateur(s) mis à jour (is_email_verified): {', '.join(fixed)}"
            )
        if added or fixed:
            print(
                "  ObiWan / HelloThere123!  |  padawan1, maitre_yoda, gardien1 / password"
            )
        elif not added and not fixed:
            print(
                "ObiWan et les autres utilisateurs de dev existent déjà et sont vérifiés."
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()

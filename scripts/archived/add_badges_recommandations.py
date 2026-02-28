#!/usr/bin/env python3
"""
Ajoute les 4 badges de recommandation (évaluation pertinence 17/02).

1. guardian_150 : palier 150 exercices (goal-gradient)
2. marathon : 300 exercices légendaire visible (scarcity)
3. comeback : retour après 7j sans activité (loss aversion)
4. Doc : vigilance 35-40 badges -> dans PLAN_REFONTE_BADGES

Usage:
    python scripts/add_badges_recommandations.py              # Dry-run
    python scripts/add_badges_recommandations.py --execute    # Insert
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

load_dotenv(ROOT_DIR / ".env")

NEW_BADGES = [
    {
        "code": "guardian_150",
        "name": "Gardien des 150",
        "description": "Résous 150 exercices. Le palier entre Maître et Grand Maître.",
        "star_wars_title": "Gardien du Seuil Intermédiaire",
        "category": "progression",
        "difficulty": "gold",
        "points_reward": 65,
        "icon_url": "🛡️",
        "is_secret": False,
        "requirements": {"attempts_count": 150},
    },
    {
        "code": "marathon",
        "name": "Marathon",
        "description": "Résous 300 exercices. L'endurance des plus déterminés.",
        "star_wars_title": "Coureur des Trois Cents",
        "category": "progression",
        "difficulty": "legendary",
        "points_reward": 150,
        "icon_url": "🏃",
        "is_secret": False,
        "requirements": {"attempts_count": 300},
    },
    {
        "code": "comeback",
        "name": "Retour aux affaires",
        "description": "Reviens après 7 jours sans activité. La persévérance compte.",
        "star_wars_title": "Gardien du Retour",
        "category": "regularity",
        "difficulty": "silver",
        "points_reward": 40,
        "icon_url": "🔄",
        "is_secret": False,
        "requirements": {"comeback_days": 7},
    },
]


def get_db_url():
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("Erreur: DATABASE_URL non defini.")
        sys.exit(1)
    return db_url


def run_add(dry_run: bool = True):
    from sqlalchemy import create_engine, text

    engine = create_engine(get_db_url())
    with engine.connect() as conn:
        print(
            "=== Ajout badges recommandations - mode",
            "DRY-RUN" if dry_run else "EXECUTION",
            "===\n",
        )

        for b in NEW_BADGES:
            code = b["code"]
            existing = conn.execute(
                text("SELECT id FROM achievements WHERE code = :code"),
                {"code": code},
            ).fetchone()
            if existing:
                print(f"  [SKIP] {code} existe deja")
                continue

            req_json = json.dumps(b["requirements"])
            secret = b.get("is_secret", False)
            icon = b.get("icon_url") or ""
            star_wars = b.get("star_wars_title") or ""

            if dry_run:
                print(f"  [ADD] {code} - {b['name']}")
                continue

            conn.execute(
                text("""
                    INSERT INTO achievements (code, name, description, icon_url, category, difficulty,
                        points_reward, is_secret, requirements, star_wars_title, is_active)
                    VALUES (:code, :name, :desc, :icon, :cat, :diff, :pts, :secret, CAST(:req AS jsonb), :sw, true)
                """),
                {
                    "code": code,
                    "name": b["name"],
                    "desc": b.get("description") or "",
                    "icon": icon,
                    "cat": b.get("category") or "special",
                    "diff": b.get("difficulty") or "bronze",
                    "pts": b.get("points_reward") or 0,
                    "secret": secret,
                    "req": req_json,
                    "sw": star_wars,
                },
            )
            print(f"  [OK] {code} ajoute")

        if not dry_run:
            conn.commit()
            print("\n[OK] Ajout termine.")


def main():
    ap = argparse.ArgumentParser(description="Ajoute badges recommandations")
    ap.add_argument("--execute", action="store_true", help="Executer (sinon dry-run)")
    args = ap.parse_args()
    run_add(dry_run=not args.execute)


if __name__ == "__main__":
    main()

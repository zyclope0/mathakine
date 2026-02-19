#!/usr/bin/env python3
"""
Ajoute des badges supplémentaires selon critères psychologiques et rétention.
Contexte : Mathakine (exercices maths + défis logiques).

Usage:
    python scripts/add_badges_psycho.py              # Dry-run
    python scripts/add_badges_psycho.py --execute    # Insert en base

Principes : Goal-gradient, Endowment, Scarcity, Social proof, Loss aversion
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

# Nouveaux badges : exercices, défis, mixte, secrets
NEW_BADGES = [
    # --- Progression (goal-gradient : paliers intermédiaires)
    {
        "code": "meteore",
        "name": "Météore",
        "description": "Résous 25 exercices. Tu accélères sur la voie de la maîtrise.",
        "star_wars_title": "Étoile Filante des Vingt-Cinq",
        "category": "progression",
        "difficulty": "bronze",
        "points_reward": 15,
        "icon_url": "🌠",
        "is_secret": False,
        "requirements": {"attempts_count": 25},
    },
    {
        "code": "centurion",
        "name": "Centurion",
        "description": "Résous 75 exercices. La moitié du chemin vers les 150.",
        "star_wars_title": "Garde des Soixante-Quinze",
        "category": "progression",
        "difficulty": "silver",
        "points_reward": 35,
        "icon_url": "🛡️",
        "is_secret": False,
        "requirements": {"attempts_count": 75},
    },
    # --- Performance (scarcity : plus difficile que speed_demon)
    {
        "code": "flash",
        "name": "Éclair Flash",
        "description": "Résous un exercice correctement en moins de 3 secondes. Réflexes d'exception.",
        "star_wars_title": "Foudre du Temple",
        "category": "performance",
        "difficulty": "gold",
        "points_reward": 50,
        "icon_url": "⚡",
        "is_secret": False,
        "requirements": {"max_time": 3},
    },
    # --- Regularity (loss aversion : streak 2 semaines)
    {
        "code": "fortnight",
        "name": "Deux Semaines d'Or",
        "description": "Pratique au moins une fois par jour pendant 14 jours consécutifs. Ne lâche rien !",
        "star_wars_title": "Gardien de la Quinzenaire",
        "category": "regularity",
        "difficulty": "gold",
        "points_reward": 70,
        "icon_url": "🔥",
        "is_secret": False,
        "requirements": {"consecutive_days": 14},
    },
    # --- Défis logiques (discovery)
    {
        "code": "logic_explorer",
        "name": "Explorateur des Défis",
        "description": "Résous 5 défis logiques correctement. Découvre les énigmes et suites.",
        "star_wars_title": "Initiation aux Enigmes",
        "category": "discovery",
        "difficulty": "bronze",
        "points_reward": 20,
        "icon_url": "🧩",
        "is_secret": False,
        "requirements": {"logic_attempts_count": 5},
    },
    {
        "code": "logic_master",
        "name": "Maître des Enigmes",
        "description": "Résous 15 défis logiques correctement. Le raisonnement devient une force.",
        "star_wars_title": "Gardien des Suites",
        "category": "discovery",
        "difficulty": "silver",
        "points_reward": 45,
        "icon_url": "🎯",
        "is_secret": False,
        "requirements": {"logic_attempts_count": 15},
    },
    # --- Mixte exercices + défis (special)
    {
        "code": "hybrid_warrior",
        "name": "Guerrier Polyvalent",
        "description": "Résous 20 exercices et 5 défis logiques. Exercices et raisonnement réunis.",
        "star_wars_title": "Combattant des Deux Arts",
        "category": "special",
        "difficulty": "silver",
        "points_reward": 55,
        "icon_url": "⚔️",
        "is_secret": False,
        "requirements": {"attempts_count": 20, "logic_attempts_count": 5},
    },
    {
        "code": "polyvalent_total",
        "name": "Polyvalent Total",
        "description": "Résous 50 exercices et 10 défis logiques. La maîtrise complète.",
        "star_wars_title": "Maître des Deux Voies",
        "category": "special",
        "difficulty": "gold",
        "points_reward": 80,
        "icon_url": "🌟",
        "is_secret": False,
        "requirements": {"attempts_count": 50, "logic_attempts_count": 10},
    },
    # ========== BADGES SECRETS (scarcity, rareté) ==========
    {
        "code": "logic_legend",
        "name": "Légende Cachée",
        "description": "Résous 50 défis logiques correctement. Un chemin peu emprunté.",
        "star_wars_title": "Sagesse des Cinquante Enigmes",
        "category": "special",
        "difficulty": "legendary",
        "points_reward": 120,
        "icon_url": "💎",
        "is_secret": True,
        "requirements": {"logic_attempts_count": 50},
    },
    {
        "code": "perfection_100",
        "name": "Parfait Absolu",
        "description": "Atteins 100% de réussite sur 100 exercices. L'excellence ultime.",
        "star_wars_title": "Sans Ombre",
        "category": "mastery",
        "difficulty": "legendary",
        "points_reward": 150,
        "icon_url": "✨",
        "is_secret": True,
        "requirements": {"min_attempts": 100, "success_rate": 100},
    },
    {
        "code": "eclipse",
        "name": "Éclipse",
        "description": "Pratique au moins une fois par jour pendant 21 jours. Trois semaines de constance pure.",
        "star_wars_title": "Gardien des Trois Semaines",
        "category": "regularity",
        "difficulty": "legendary",
        "points_reward": 120,
        "icon_url": "🌑",
        "is_secret": True,
        "requirements": {"consecutive_days": 21},
    },
    {
        "code": "grand_hybrid",
        "name": "Grand Hybride",
        "description": "100 exercices et 25 défis logiques. L'union parfaite des deux arts.",
        "star_wars_title": "Souverain des Deux Mondes",
        "category": "special",
        "difficulty": "legendary",
        "points_reward": 180,
        "icon_url": "👑",
        "is_secret": True,
        "requirements": {"attempts_count": 100, "logic_attempts_count": 25},
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
        print("=== Ajout badges psycho/retention - mode", "DRY-RUN" if dry_run else "EXECUTION", "===\n")

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
                print(f"  [ADD] {code} - {b['name']} ({'secret' if secret else 'visible'})")
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
    ap = argparse.ArgumentParser(description="Ajoute badges psycho/retention")
    ap.add_argument("--execute", action="store_true", help="Executer (sinon dry-run)")
    args = ap.parse_args()
    run_add(dry_run=not args.execute)


if __name__ == "__main__":
    main()

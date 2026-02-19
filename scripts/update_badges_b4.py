#!/usr/bin/env python3
"""
Applique les reformulations B4 aux badges existants.

Basé sur docs/02-FEATURES/B4_REFORMULATION_BADGES.md
Met à jour name, description, star_wars_title, category, difficulty, points_reward
pour chaque badge identifié par son code. Les requirements ne sont pas modifiés.

Usage:
    python scripts/update_badges_b4.py              # Dry-run (affiche sans modifier)
    python scripts/update_badges_b4.py --execute    # Applique les mises à jour
"""
import argparse
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

# Reformulations B4 — aligné sur B4_REFORMULATION_BADGES.md
BADGE_UPDATES = {
    "first_steps": {
        "name": "Premiers pas au Temple",
        "description": "Résous ton premier exercice et fais ton entrée dans l'Ordre. Chaque Maître a débuté ainsi.",
        "star_wars_title": "Youngling du Premier Matin",
        "category": "progression",
        "difficulty": "bronze",
        "points_reward": 5,
    },
    "padawan_path": {
        "name": "Voie du Padawan",
        "description": "Résous 10 exercices. Tu découvres les bases de l'entraînement Jedi.",
        "star_wars_title": "Padawan de la Dizaine",
        "category": "progression",
        "difficulty": "bronze",
        "points_reward": 10,
    },
    "knight_trial": {
        "name": "Épreuve du Chevalier",
        "description": "Résous 50 exercices et prouve ta constance. L'Ordre te reconnaît comme aspirant chevalier.",
        "star_wars_title": "Aspirant des Cinquante Épreuves",
        "category": "progression",
        "difficulty": "silver",
        "points_reward": 25,
    },
    "jedi_master": {
        "name": "Maître Jedi",
        "description": "Résous 100 exercices. Tu as atteint la maîtrise de l'entraînement régulier.",
        "star_wars_title": "Maître des Cent Épreuves",
        "category": "progression",
        "difficulty": "gold",
        "points_reward": 50,
    },
    "grand_master": {
        "name": "Grand Maître",
        "description": "Résous 200 exercices. Tu rejoins le cercle restreint des Maîtres les plus assidus de l'Ordre.",
        "star_wars_title": "Grand Maître des Deux Cents",
        "category": "progression",
        "difficulty": "legendary",
        "points_reward": 100,
    },
    "addition_master": {
        "name": "Maître des Additions",
        "description": "Réussis 20 additions consécutives sans erreur. La Force des nombres t'obéit.",
        "star_wars_title": "Gardien des Sommes",
        "category": "mastery",
        "difficulty": "silver",
        "points_reward": 30,
    },
    "subtraction_master": {
        "name": "Maître des Soustractions",
        "description": "Réussis 15 soustractions consécutives sans erreur. Le retranchement n'a plus de secret.",
        "star_wars_title": "Maître du Retranchement",
        "category": "mastery",
        "difficulty": "silver",
        "points_reward": 30,
    },
    "multiplication_master": {
        "name": "Maître des Multiplications",
        "description": "Réussis 15 multiplications consécutives sans erreur. Les tables sont ton allié.",
        "star_wars_title": "Gardien des Produits",
        "category": "mastery",
        "difficulty": "silver",
        "points_reward": 30,
    },
    "division_master": {
        "name": "Maître des Divisions",
        "description": "Réussis 15 divisions consécutives sans erreur. La partition des nombres est maîtrisée.",
        "star_wars_title": "Maître de la Partition",
        "category": "mastery",
        "difficulty": "silver",
        "points_reward": 30,
    },
    "speed_demon": {
        "name": "Éclair de Vitesse",
        "description": "Résous un exercice correctement en moins de 5 secondes. La Force accélère tes réflexes.",
        "star_wars_title": "Éclair du Temple",
        "category": "performance",
        "difficulty": "silver",
        "points_reward": 25,
    },
    "perfect_day": {
        "name": "Journée Parfaite",
        "description": "Réussis tous tes exercices du jour. Une journée sans faille, une étape vers la maîtrise.",
        "star_wars_title": "Jour sans Ombre",
        "category": "regularity",
        "difficulty": "gold",
        "points_reward": 40,
    },
    "perfect_week": {
        "name": "Semaine Parfaite",
        "description": "Pratique au moins une fois par jour pendant 7 jours consécutifs. La constance forge les Jedi.",
        "star_wars_title": "Gardien de la Semaine Sacrée",
        "category": "regularity",
        "difficulty": "gold",
        "points_reward": 50,
    },
    "perfect_month": {
        "name": "Mois Parfait",
        "description": "Pratique au moins une fois par jour pendant 30 jours consécutifs. Réservé aux plus déterminés.",
        "star_wars_title": "Gardien du Mois des Étoiles",
        "category": "regularity",
        "difficulty": "legendary",
        "points_reward": 150,
    },
    "expert": {
        "name": "Expert",
        "description": "Atteins au moins 80% de réussite sur 50 exercices. La précision est la marque des Jedi confirmés.",
        "star_wars_title": "Jedi de la Précision",
        "category": "mastery",
        "difficulty": "silver",
        "points_reward": 35,
    },
    "perfectionist": {
        "name": "Perfectionniste",
        "description": "Atteins au moins 95% de réussite sur 30 exercices. L'excellence est rare.",
        "star_wars_title": "Maître de l'Excellence",
        "category": "mastery",
        "difficulty": "gold",
        "points_reward": 60,
    },
    "explorer": {
        "name": "Explorateur",
        "description": "Essaie au moins un exercice de chaque type (addition, soustraction, multiplication, division).",
        "star_wars_title": "Explorateur des Quatre Voies",
        "category": "discovery",
        "difficulty": "bronze",
        "points_reward": 15,
    },
    "versatile": {
        "name": "Polyvalent",
        "description": "Réussis au moins 5 exercices de chaque type. La polyvalence est une force.",
        "star_wars_title": "Padawan des Quatre Arts",
        "category": "discovery",
        "difficulty": "silver",
        "points_reward": 35,
    },
}


def get_db_url():
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("Erreur: DATABASE_URL non défini. Définir dans .env ou l'environnement.")
        sys.exit(1)
    return db_url


def run_update(dry_run=True):
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(get_db_url())
    Session = sessionmaker(bind=engine, autocommit=False)

    with Session() as session:
        for code, updates in BADGE_UPDATES.items():
            row = session.execute(
                text("SELECT id, name, description, star_wars_title, category, difficulty, points_reward FROM achievements WHERE code = :code"),
                {"code": code},
            ).fetchone()

            if not row:
                print(f"  [WARN] Badge '{code}' non trouve - ignore")
                continue

            bid, old_name, old_desc, old_sw, old_cat, old_diff, old_pts = row

            if dry_run:
                print(f"\n{code}:")
                print(f"  name: {old_name!r} -> {updates['name']!r}")
                print(f"  description: ... -> {updates['description'][:60]}...")
                print(f"  star_wars_title: {old_sw!r} -> {updates['star_wars_title']!r}")
                print(f"  category: {old_cat!r} -> {updates['category']!r}")
                print(f"  difficulty: {old_diff!r} -> {updates['difficulty']!r}")
                print(f"  points_reward: {old_pts} -> {updates['points_reward']}")
            else:
                session.execute(
                    text("""
                        UPDATE achievements
                        SET name = :name, description = :desc, star_wars_title = :sw,
                            category = :cat, difficulty = :diff, points_reward = :pts
                        WHERE id = :id
                    """),
                    {
                        "id": bid,
                        "name": updates["name"],
                        "desc": updates["description"],
                        "sw": updates["star_wars_title"],
                        "cat": updates["category"],
                        "diff": updates["difficulty"],
                        "pts": updates["points_reward"],
                    },
                )
                print(f"  [OK] {code} mis a jour")

        if not dry_run:
            session.commit()
            print("\n[OK] Mise a jour terminee.")


def main():
    parser = argparse.ArgumentParser(description="Applique les reformulations B4 aux badges")
    parser.add_argument("--execute", action="store_true", help="Exécuter les mises à jour (sinon dry-run)")
    args = parser.parse_args()

    if args.execute:
        print("Exécution des mises à jour B4…")
        run_update(dry_run=False)
    else:
        print("Mode dry-run (prévisualisation). Utiliser --execute pour appliquer.")
        run_update(dry_run=True)


if __name__ == "__main__":
    main()

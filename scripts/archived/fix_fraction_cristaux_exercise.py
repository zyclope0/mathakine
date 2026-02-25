#!/usr/bin/env python3
"""
Corrige l'exercice de fractions "cristaux 120" (moitié rouges, tiers bleus).

Problème : La bonne réponse est 20, pas 30.
- Rouges : 120 × 1/2 = 60
- Bleus : 120 × 1/3 = 40
- Ni rouge ni bleu : 120 - 100 = 20

Usage:
    python scripts/fix_fraction_cristaux_exercise.py              # Dry-run (affiche sans modifier)
    python scripts/fix_fraction_cristaux_exercise.py --execute    # Applique les corrections
"""
import argparse
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

# Correction à appliquer
CORRECT_ANSWER = "20"
CORRECT_EXPLANATION = """Pour résoudre ce problème, nous devons d'abord déterminer combien de cristaux sont rouges et bleus.

- La moitié des 120 cristaux sont rouges : 120 × 1/2 = 60 cristaux rouges.
- Un tiers des 120 cristaux sont bleus : 120 × 1/3 = 40 cristaux bleus.
- Total des cristaux rouges et bleus : 60 + 40 = 100.
- Cristaux ni rouges ni bleus : 120 - 100 = 20.

La réponse correcte est donc 20 cristaux."""


def get_db_url():
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("Erreur: DATABASE_URL non défini. Définir dans .env ou l'environnement.")
        sys.exit(1)
    return db_url


def find_and_fix(dry_run=True):
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(get_db_url())
    Session = sessionmaker(bind=engine, autocommit=False)
    session = Session()

    # Rechercher l'exercice : 120 cristaux, moitié rouges, tiers bleus (critères élargis)
    result = session.execute(
        text("""
            SELECT id, title, question, correct_answer, choices, explanation
            FROM exercises
            WHERE question ILIKE '%120%'
              AND (question ILIKE '%cristal%' OR question ILIKE '%cristaux%')
              AND (question ILIKE '%rouge%' OR question ILIKE '%bleu%')
              AND (question ILIKE '%moitié%' OR question ILIKE '%moitie%'
                   OR question ILIKE '%tiers%' OR question ILIKE '%tier %'
                   OR question ILIKE '%demi%' OR question ILIKE '%tier %')
            ORDER BY id DESC
        """)
    )
    rows = result.fetchall()

    if not rows:
        print("Aucun exercice correspondant trouvé.")
        session.close()
        return 0

    fixed = 0
    for row in rows:
        ex_id, title, question, correct_answer, choices, explanation = row
        # Ne corriger que si la question mentionne bien 120 comme total
        if "120" not in question:
            continue
        if correct_answer == CORRECT_ANSWER:
            print(f"Exercice {ex_id} déjà correct (réponse = 20).")
            continue

        print(f"\n--- Exercice {ex_id}: {title[:50]}...")
        print(f"  Question: {question[:80]}...")
        print(f"  Réponse actuelle: {correct_answer} -> à corriger en {CORRECT_ANSWER}")

        if not dry_run:
            # Mettre à jour correct_answer et explanation
            session.execute(
                text("UPDATE exercises SET correct_answer = :ans, explanation = :exp WHERE id = :id"),
                {"ans": CORRECT_ANSWER, "exp": CORRECT_EXPLANATION, "id": ex_id}
            )
            fixed += 1
            print(f"  -> Corrigé.")

    if not dry_run and fixed > 0:
        session.commit()
        print(f"\n{fixed} exercice(s) corrigé(s).")
    elif dry_run and rows:
        print("\n[MODE DRY-RUN] Aucune modification. Lancez avec --execute pour appliquer.")

    session.close()
    return 0


def main():
    parser = argparse.ArgumentParser(description="Corrige l'exercice fractions cristaux 120")
    parser.add_argument("--execute", action="store_true", help="Appliquer les corrections")
    args = parser.parse_args()
    return find_and_fix(dry_run=not args.execute)


if __name__ == "__main__":
    sys.exit(main())

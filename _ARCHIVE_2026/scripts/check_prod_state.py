#!/usr/bin/env python3
"""Script pour vérifier l'état de la base de données de production"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import SessionLocal
from app.models.exercise import Exercise
from app.models.logic_challenge import LogicChallenge

def main():
    db = SessionLocal()
    
    try:
        # Compter les exercices
        ex_count = db.query(Exercise).count()
        ch_count = db.query(LogicChallenge).count()
        
        print("=" * 60)
        print("ÉTAT DE LA BASE DE DONNÉES DE PRODUCTION")
        print("=" * 60)
        print(f"Exercices : {ex_count}")
        print(f"Challenges : {ch_count}")
        
        if ex_count > 0:
            print("\n--- Exemple d'exercice ---")
            sample = db.query(Exercise).first()
            print(f"Titre : {sample.title}")
            print(f"Type : {sample.exercise_type} (type Python : {type(sample.exercise_type)})")
            print(f"Difficulté : {sample.difficulty} (type Python : {type(sample.difficulty)})")
            
            # Vérifier tous les types uniques
            all_exercises = db.query(Exercise).all()
            types_used = set(ex.exercise_type for ex in all_exercises)
            difficulties_used = set(ex.difficulty for ex in all_exercises)
            
            print(f"\nTypes d'exercices utilisés : {types_used}")
            print(f"Difficultés utilisées : {difficulties_used}")
        
        if ch_count > 0:
            print("\n--- Exemple de challenge ---")
            sample_ch = db.query(LogicChallenge).first()
            print(f"Titre : {sample_ch.title}")
            print(f"Type : {sample_ch.challenge_type}")
            print(f"Difficulté : {sample_ch.difficulty}")
        
        print("\n" + "=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    main()



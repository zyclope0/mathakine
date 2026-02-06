#!/usr/bin/env python3
"""Test seed 5+5 - Verification des valeurs enum"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("=== TEST SEED 5+5 ===\n")
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import NullPool
    from app.models.exercise import Exercise
    from app.models.logic_challenge import LogicChallenge
    import os
    
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url, poolclass=NullPool, connect_args={"connect_timeout": 10})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # IMPORTANT: Importer les enums Python
        from app.models.exercise import ExerciseType, DifficultyLevel
        from app.models.logic_challenge import LogicChallengeType, AgeGroup
        
        print("[1/2] Creation 5 exercices...\n")
        
        # Utiliser les enums Python directement
        exercises = [
            Exercise(title="Addition Simple", question="3+2=?", correct_answer="5", explanation="Addition",
                    hint="Compte", exercise_type=ExerciseType.ADDITION, difficulty=DifficultyLevel.INITIE, age_group="6-8", is_active=True),
            Exercise(title="Soustraction", question="10-3=?", correct_answer="7", explanation="Soustraction",
                    hint="Enleve", exercise_type=ExerciseType.SOUSTRACTION, difficulty=DifficultyLevel.INITIE, age_group="6-8", is_active=True),
            Exercise(title="Multiplication", question="5x3=?", correct_answer="15", explanation="Multiplication",
                    hint="5+5+5", exercise_type=ExerciseType.MULTIPLICATION, difficulty=DifficultyLevel.PADAWAN, age_group="8-10", is_active=True),
            Exercise(title="Division", question="20/4=?", correct_answer="5", explanation="Division",
                    hint="Combien de fois", exercise_type=ExerciseType.DIVISION, difficulty=DifficultyLevel.PADAWAN, age_group="8-10", is_active=True),
            Exercise(title="Fraction", question="1/2+1/4=?", correct_answer="3/4", explanation="Fractions",
                    hint="Denominateur commun", exercise_type=ExerciseType.FRACTIONS, difficulty=DifficultyLevel.CHEVALIER, age_group="10-12", is_active=True),
        ]
        
        for ex in exercises:
            db.add(ex)
        db.commit()
        print(f"  OK: {len(exercises)} exercices\n")
        
        print("[2/2] Creation 5 challenges...\n")
        
        # Utiliser les enums Python directement (PostgreSQL a les valeurs EN MAJUSCULES)
        challenges = [
            LogicChallenge(title="Suite Paires", description="Nombres pairs", question="2,4,6,8,?",
                          correct_answer="10", solution_explanation="Suite +2",
                          challenge_type=LogicChallengeType.SEQUENCE, age_group=AgeGroup.GROUP_10_12, difficulty=DifficultyLevel.INITIE, is_active=True),
            LogicChallenge(title="Pattern AB", description="Motif", question="A,B,A,B,?",
                          correct_answer="A", solution_explanation="Alternance",
                          challenge_type=LogicChallengeType.PATTERN, age_group=AgeGroup.ALL_AGES, difficulty=DifficultyLevel.INITIE, is_active=True),
            LogicChallenge(title="Enigme", description="Devinette", question="Je suis leger. Qui suis-je?",
                          correct_answer="le souffle", solution_explanation="Le souffle",
                          challenge_type=LogicChallengeType.RIDDLE, age_group=AgeGroup.GROUP_13_15, difficulty=DifficultyLevel.PADAWAN, is_active=True),
            LogicChallenge(title="Logique", description="Syllogisme", question="Tous les chats sont animaux. Felix?",
                          correct_answer="animal", solution_explanation="Syllogisme",
                          challenge_type=LogicChallengeType.DEDUCTION, age_group=AgeGroup.GROUP_13_15, difficulty=DifficultyLevel.PADAWAN, is_active=True),
            LogicChallenge(title="Cube", description="Geometrie", question="Faces d'un cube?",
                          correct_answer="6", solution_explanation="6 faces",
                          challenge_type=LogicChallengeType.SPATIAL, age_group=AgeGroup.ALL_AGES, difficulty=DifficultyLevel.INITIE, is_active=True),
        ]
        
        for ch in challenges:
            db.add(ch)
        db.commit()
        print(f"  OK: {len(challenges)} challenges\n")
        
        print("[VERIFICATION]")
        ex_count = db.query(Exercise).count()
        ch_count = db.query(LogicChallenge).count()
        print(f"  Exercises: {ex_count}")
        print(f"  Challenges: {ch_count}")
        
        print("\n[SUCCES] Test termine!")
        return 0
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
    finally:
        db.close()
        engine.dispose()

if __name__ == "__main__":
    sys.exit(main())


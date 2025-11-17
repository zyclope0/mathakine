#!/usr/bin/env python3
"""Nettoyage et seed simple - Version qui ne bloque pas"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    print("Debut du nettoyage et seed...")
    
    from app.db.base import SessionLocal
    from app.models.exercise import Exercise
    from app.models.logic_challenge import LogicChallenge
    from app.models.attempt import Attempt
    from app.models.logic_challenge import LogicChallengeAttempt
    
    db = SessionLocal()
    
    try:
        # 1. NETTOYAGE
        print("\n[1/3] Nettoyage de la base...")
        attempts = db.query(Attempt).delete()
        challenge_attempts = db.query(LogicChallengeAttempt).delete()
        exercises = db.query(Exercise).delete()
        challenges = db.query(LogicChallenge).delete()
        db.commit()
        print(f"  Supprime: {attempts} attempts, {challenge_attempts} challenge attempts, {exercises} exercises, {challenges} challenges")
        
        # 2. SEED EXERCICES (5 exemples pour tester)
        print("\n[2/3] Creation de 5 exercices de test...")
        test_exercises = [
            Exercise(
                title="Addition Simple",
                question="3 + 2 = ?",
                correct_answer="5",
                explanation="3 + 2 = 5",
                hint="Compte sur tes doigts",
                exercise_type="addition",
                difficulty="initie",
                age_group="6-8",
                is_active=True
            ),
            Exercise(
                title="Soustraction Simple",
                question="10 - 3 = ?",
                correct_answer="7",
                explanation="10 - 3 = 7",
                hint="Enleve 3 de 10",
                exercise_type="soustraction",
                difficulty="initie",
                age_group="6-8",
                is_active=True
            ),
            Exercise(
                title="Multiplication",
                question="5 x 3 = ?",
                correct_answer="15",
                explanation="5 x 3 = 15",
                hint="5 + 5 + 5",
                exercise_type="multiplication",
                difficulty="padawan",
                age_group="8-10",
                is_active=True
            ),
            Exercise(
                title="Division",
                question="20 / 4 = ?",
                correct_answer="5",
                explanation="20 / 4 = 5",
                hint="Combien de fois 4 dans 20?",
                exercise_type="division",
                difficulty="padawan",
                age_group="8-10",
                is_active=True
            ),
            Exercise(
                title="Fractions",
                question="1/2 + 1/4 = ?",
                correct_answer="3/4",
                explanation="2/4 + 1/4 = 3/4",
                hint="Mets au meme denominateur",
                exercise_type="fractions",
                difficulty="chevalier",
                age_group="10-12",
                is_active=True
            ),
        ]
        
        for ex in test_exercises:
            db.add(ex)
        db.commit()
        print(f"  Cree: {len(test_exercises)} exercices")
        
        # 3. SEED CHALLENGES (5 exemples pour tester)
        print("\n[3/3] Creation de 5 challenges de test...")
        test_challenges = [
            LogicChallenge(
                title="Suite Simple",
                description="Trouve le nombre suivant",
                question="2, 4, 6, 8, ?",
                correct_answer="10",
                solution_explanation="Suite des nombres pairs",
                challenge_type="sequence",
                age_group="enfant",
                difficulty="initie",
                is_active=True
            ),
            LogicChallenge(
                title="Pattern",
                description="Quel est le motif?",
                question="A, B, A, B, ?",
                correct_answer="A",
                solution_explanation="Alternance A-B",
                challenge_type="pattern",
                age_group="enfant",
                difficulty="initie",
                is_active=True
            ),
            LogicChallenge(
                title="Devinette",
                description="Resous l'enigme",
                question="Je suis leger comme une plume mais personne ne peut me tenir longtemps. Qui suis-je?",
                correct_answer="le souffle",
                solution_explanation="C'est le souffle/la respiration",
                challenge_type="riddle",
                age_group="adolescent",
                difficulty="padawan",
                is_active=True
            ),
            LogicChallenge(
                title="Logique",
                description="Raisonnement deductif",
                question="Si tous les chats sont des animaux et que Felix est un chat, que peut-on conclure?",
                correct_answer="Felix est un animal",
                solution_explanation="Syllogisme simple",
                challenge_type="deduction",
                age_group="adolescent",
                difficulty="padawan",
                is_active=True
            ),
            LogicChallenge(
                title="Spatial",
                description="Vision dans l'espace",
                question="Combien de faces a un cube?",
                correct_answer="6",
                solution_explanation="Un cube a 6 faces carrees",
                challenge_type="spatial",
                age_group="all",
                difficulty="chevalier",
                is_active=True
            ),
        ]
        
        for ch in test_challenges:
            db.add(ch)
        db.commit()
        print(f"  Cree: {len(test_challenges)} challenges")
        
        # Verification
        print("\n[VERIFICATION]")
        ex_count = db.query(Exercise).count()
        ch_count = db.query(LogicChallenge).count()
        print(f"  Total exercises: {ex_count}")
        print(f"  Total challenges: {ch_count}")
        
        print("\n[SUCCES] Nettoyage et seed termines!")
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
    sys.exit(0)


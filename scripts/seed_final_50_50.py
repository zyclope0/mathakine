#!/usr/bin/env python3
"""Seed final 50 exercices + 50 challenges"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("=== SEED FINAL 50 EXERCICES + 50 CHALLENGES ===\n")
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import NullPool
    from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
    from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
    import os
    
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url, poolclass=NullPool, connect_args={"connect_timeout": 10})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("[1/2] Creation de 50 exercices...\n")
        exercises = []
        
        # Template pour générer des exercices variés
        # 10 additions, 10 soustractions, 10 multiplications, 10 divisions, 5 fractions, 5 géométrie
        types_config = [
            (ExerciseType.ADDITION, 10, [
                ("Addition Simple {}", "Luke trouve {} cristaux, Leia lui en donne {}. Total?", lambda a,b: str(a+b)),
                ("Droïdes Rebelles {}", "La base a {} droïdes astromech et {} protocolaires. Total?", lambda a,b: str(a+b)),
            ]),
            (ExerciseType.SOUSTRACTION, 10, [
                ("Soustraction Cristaux {}", "Obi-Wan a {} cristaux, en perd {}. Reste?", lambda a,b: str(a-b)),
                ("TIE Fighters {}", "{} TIE Fighters, {} detruits. Reste?", lambda a,b: str(a-b)),
            ]),
            (ExerciseType.MULTIPLICATION, 10, [
                ("Multiplication Escadrons {}", "{} escadrons de {} vaisseaux. Total?", lambda a,b: str(a*b)),
                ("Rations Clones {}", "{} clones, {} rations chacun. Total?", lambda a,b: str(a*b)),
            ]),
            (ExerciseType.DIVISION, 10, [
                ("Division Cristaux {}", "{} cristaux pour {} Jedi. Par Jedi?", lambda a,b: str(a//b)),
                ("Escadrons {}", "{} vaisseaux en {} escadrons. Par escadron?", lambda a,b: str(a//b)),
            ]),
            (ExerciseType.FRACTIONS, 5, [
                ("Fraction {}", "1/{} + 1/{}. Resultat en fraction simplifiee?", lambda a,b: f"{a+b}/{a*b}"),
            ]),
            (ExerciseType.GEOMETRIE, 5, [
                ("Perimetre Carre {}", "Carre de cote {}m. Perimetre?", lambda a,b: str(4*a)),
                ("Aire Rectangle {}", "Rectangle {}m x {}m. Aire?", lambda a,b: str(a*b)),
            ]),
        ]
        
        # Générer les exercices
        for ex_type, count, templates in types_config:
            for i in range(count):
                template = templates[i % len(templates)]
                # Générer des nombres adaptés à la difficulté
                if i < 3:  # Initié
                    a, b = (i+2, i+1)
                    diff = DifficultyLevel.INITIE
                elif i < 6:  # Padawan
                    a, b = (10+i*3, 5+i*2)
                    diff = DifficultyLevel.PADAWAN
                elif i < 8:  # Chevalier
                    a, b = (20+i*10, 5+i*3)
                    diff = DifficultyLevel.CHEVALIER
                else:  # Maître
                    a, b = (50+i*20, 10+i*5)
                    diff = DifficultyLevel.MAITRE
                
                title = template[0].format(i+1)
                question = template[1].format(a, b)
                answer = template[2](a, b)
                
                exercises.append(Exercise(
                    title=title,
                    question=question,
                    correct_answer=answer,
                    explanation=f"Calcul: {answer}",
                    hint="Pose l'operation",
                    exercise_type=ex_type,
                    difficulty=diff,
                    age_group="6-8" if diff == DifficultyLevel.INITIE else ("8-10" if diff == DifficultyLevel.PADAWAN else "10-12"),
                    context_theme="Star Wars",
                    is_active=True
                ))
        
        for ex in exercises:
            db.add(ex)
        db.commit()
        print(f"  OK: {len(exercises)} exercices\n")
        
        print("[2/2] Creation de 50 challenges...\n")
        challenges = []
        
        # Template pour générer des challenges variés
        # 10 sequences, 10 patterns, 10 riddles, 10 deduction, 10 spatial
        challenge_templates = [
            # SEQUENCES (10)
            (LogicChallengeType.SEQUENCE, "Suite Nombres {}", "Trouve le suivant: {}", AgeGroup.GROUP_10_12, DifficultyLevel.INITIE),
            (LogicChallengeType.SEQUENCE, "Suite Geometrique {}", "Quelle est la suite: {}", AgeGroup.GROUP_10_12, DifficultyLevel.PADAWAN),
            (LogicChallengeType.SEQUENCE, "Suite Complexe {}", "Complète: {}", AgeGroup.GROUP_13_15, DifficultyLevel.CHEVALIER),
            (LogicChallengeType.SEQUENCE, "Suite Avancee {}", "Sequence logique: {}", AgeGroup.GROUP_13_15, DifficultyLevel.MAITRE),
            # PATTERNS (10)
            (LogicChallengeType.PATTERN, "Motif {}", "Quel motif: {}", AgeGroup.GROUP_10_12, DifficultyLevel.INITIE),
            (LogicChallengeType.PATTERN, "Pattern {}", "Reconnais le pattern: {}", AgeGroup.ALL_AGES, DifficultyLevel.PADAWAN),
            (LogicChallengeType.PATTERN, "Structure {}", "Quelle structure: {}", AgeGroup.GROUP_13_15, DifficultyLevel.CHEVALIER),
            (LogicChallengeType.PATTERN, "Forme Avancee {}", "Pattern complexe: {}", AgeGroup.GROUP_13_15, DifficultyLevel.MAITRE),
            # RIDDLES (10)
            (LogicChallengeType.RIDDLE, "Enigme {}", "Qui suis-je? {}", AgeGroup.GROUP_10_12, DifficultyLevel.INITIE),
            (LogicChallengeType.RIDDLE, "Devinette {}", "Devine: {}", AgeGroup.GROUP_10_12, DifficultyLevel.PADAWAN),
            (LogicChallengeType.RIDDLE, "Mystere {}", "Resous: {}", AgeGroup.GROUP_13_15, DifficultyLevel.CHEVALIER),
            (LogicChallengeType.RIDDLE, "Paradoxe {}", "Enigme difficile: {}", AgeGroup.ALL_AGES, DifficultyLevel.MAITRE),
            # DEDUCTION (10)
            (LogicChallengeType.DEDUCTION, "Logique {}", "Deduis: {}", AgeGroup.GROUP_10_12, DifficultyLevel.INITIE),
            (LogicChallengeType.DEDUCTION, "Raisonnement {}", "Qu'en conclus-tu: {}", AgeGroup.GROUP_13_15, DifficultyLevel.PADAWAN),
            (LogicChallengeType.DEDUCTION, "Syllogisme {}", "Logique avancee: {}", AgeGroup.GROUP_13_15, DifficultyLevel.CHEVALIER),
            (LogicChallengeType.DEDUCTION, "Inference {}", "Deduis la conclusion: {}", AgeGroup.ALL_AGES, DifficultyLevel.MAITRE),
            # SPATIAL (10)
            (LogicChallengeType.SPATIAL, "Geometrie {}", "Vision spatiale: {}", AgeGroup.GROUP_10_12, DifficultyLevel.INITIE),
            (LogicChallengeType.SPATIAL, "Rotation {}", "Apres rotation: {}", AgeGroup.GROUP_10_12, DifficultyLevel.PADAWAN),
            (LogicChallengeType.SPATIAL, "3D {}", "En 3 dimensions: {}", AgeGroup.GROUP_13_15, DifficultyLevel.CHEVALIER),
            (LogicChallengeType.SPATIAL, "Projection {}", "Projection complexe: {}", AgeGroup.ALL_AGES, DifficultyLevel.MAITRE),
        ]
        
        # Générer 50 challenges (2.5 fois chaque template)
        for i in range(50):
            template = challenge_templates[i % len(challenge_templates)]
            ch_type, title_tpl, q_tpl, age, diff = template
            
            title = title_tpl.format(i+1)
            question = q_tpl.format(f"exemple_{i+1}")
            answer = f"reponse_{i+1}"
            explanation = f"Explication pour challenge {i+1}"
            
            challenges.append(LogicChallenge(
                title=title,
                description=f"Challenge de type {ch_type.value}",
                question=question,
                correct_answer=answer,
                solution_explanation=explanation,
                challenge_type=ch_type,
                age_group=age,
                difficulty=diff,
                is_active=True
            ))
        
        for ch in challenges:
            db.add(ch)
        db.commit()
        print(f"  OK: {len(challenges)} challenges\n")
        
        print("[VERIFICATION]")
        ex_count = db.query(Exercise).count()
        ch_count = db.query(LogicChallenge).count()
        print(f"  Exercises: {ex_count}")
        print(f"  Challenges: {ch_count}")
        
        print("\n[SUCCES] Seed 50+50 termine!")
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


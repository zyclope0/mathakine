#!/usr/bin/env python3
"""Seed final 50 exercices + 50 challenges AVEC choix multiples"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("=== SEED FINAL 50 EXERCICES + 50 CHALLENGES (avec choix) ===\n")
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import NullPool
    from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
    from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
    import os
    import json
    
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url, poolclass=NullPool, connect_args={"connect_timeout": 10})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Nettoyer d'abord
        print("[0/2] Nettoyage de la base...\n")
        from app.models.attempt import Attempt
        from app.models.logic_challenge import LogicChallengeAttempt
        db.query(Attempt).delete()
        db.query(LogicChallengeAttempt).delete()
        db.query(Exercise).delete()
        db.query(LogicChallenge).delete()
        db.commit()
        print("  Base nettoyee\n")
        
        print("[1/2] Creation de 50 exercices AVEC choix multiples...\n")
        exercises = []
        
        # Helper pour generer des choix multiples
        def generate_choices(correct, operation_type):
            """Genere 4 choix dont un correct"""
            correct_num = int(correct) if correct.isdigit() else 0
            choices = [correct]
            
            # Generer 3 mauvaises reponses plausibles
            if operation_type in ["addition", "multiplication"]:
                choices.append(str(correct_num + 1))
                choices.append(str(correct_num - 1))
                choices.append(str(correct_num + 2))
            elif operation_type == "soustraction":
                choices.append(str(correct_num + 1))
                choices.append(str(correct_num - 1))
                choices.append(str(abs(correct_num - 2)))
            elif operation_type == "division":
                choices.append(str(correct_num + 1))
                choices.append(str(correct_num * 2))
                choices.append(str(max(1, correct_num - 1)))
            else:  # fractions, geometrie
                choices.append(str(correct_num + 1))
                choices.append(str(correct_num - 1))
                choices.append(str(correct_num + 5))
            
            # Melanger et retourner
            import random
            random.shuffle(choices)
            return choices
        
        # Template pour générer des exercices variés
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
                ("Division Cristaux {}", "{} cristaux pour {} Jedi. Par Jedi?", lambda a,b: str(a//b) if b != 0 else "0"),
                ("Escadrons {}", "{} vaisseaux en {} escadrons. Par escadron?", lambda a,b: str(a//b) if b != 0 else "0"),
            ]),
            (ExerciseType.FRACTIONS, 5, [
                ("Fraction {}", "1/2 + 1/4 = ?", lambda a,b: "3/4"),
                ("Moitie {}", "La moitie de {} = ?", lambda a,b: str(a//2)),
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
                    a, b = (20+i*5, 3+i)
                    diff = DifficultyLevel.CHEVALIER
                else:  # Maître
                    a, b = (30+i*5, 5+i)
                    diff = DifficultyLevel.MAITRE
                
                title = template[0].format(i+1)
                question = template[1].format(a, b)
                answer = template[2](a, b)
                
                # Generer choix multiples
                choices = generate_choices(answer, ex_type.value)
                
                exercises.append(Exercise(
                    title=title,
                    question=question,
                    correct_answer=answer,
                    choices=json.dumps(choices),  # JSON array de choix
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
        print(f"  OK: {len(exercises)} exercices avec choix multiples\n")
        
        print("[2/2] Creation de 50 challenges...\n")
        challenges = []
        
        # Template pour générer des challenges variés
        challenge_templates = [
            # SEQUENCES (10)
            (LogicChallengeType.SEQUENCE, "Suite Nombres {}", "2, 4, 6, 8, ?", "10", ["10", "9", "12", "7"], AgeGroup.GROUP_10_12, DifficultyLevel.INITIE),
            (LogicChallengeType.SEQUENCE, "Suite Impairs {}", "1, 3, 5, 7, ?", "9", ["9", "8", "10", "11"], AgeGroup.GROUP_10_12, DifficultyLevel.INITIE),
            (LogicChallengeType.SEQUENCE, "Multiples 5 {}", "5, 10, 15, 20, ?", "25", ["25", "24", "30", "20"], AgeGroup.GROUP_10_12, DifficultyLevel.PADAWAN),
            (LogicChallengeType.SEQUENCE, "Carres {}", "1, 4, 9, 16, ?", "25", ["25", "20", "24", "30"], AgeGroup.GROUP_13_15, DifficultyLevel.CHEVALIER),
            # PATTERNS (10)
            (LogicChallengeType.PATTERN, "Motif AB {}", "A, B, A, B, ?", "A", ["A", "B", "C", "AB"], AgeGroup.GROUP_10_12, DifficultyLevel.INITIE),
            (LogicChallengeType.PATTERN, "Pattern ABC {}", "A, B, C, A, B, C, A, ?", "B", ["B", "A", "C", "D"], AgeGroup.ALL_AGES, DifficultyLevel.PADAWAN),
            (LogicChallengeType.PATTERN, "Lettres {}", "A, C, E, G, ?", "I", ["I", "H", "J", "F"], AgeGroup.GROUP_13_15, DifficultyLevel.CHEVALIER),
            (LogicChallengeType.PATTERN, "Double Saut {}", "A, D, G, J, ?", "M", ["M", "K", "L", "N"], AgeGroup.GROUP_13_15, DifficultyLevel.MAITRE),
            # RIDDLES (10)
            (LogicChallengeType.RIDDLE, "Enigme Souffle {}", "Je suis leger mais personne ne me tient longtemps. Qui suis-je?", "le souffle", ["le souffle", "l'air", "le vent", "la plume"], AgeGroup.GROUP_10_12, DifficultyLevel.INITIE),
            (LogicChallengeType.RIDDLE, "Silence {}", "Plus tu me parles, moins je suis la. Qui suis-je?", "le silence", ["le silence", "l'echo", "le son", "la voix"], AgeGroup.GROUP_10_12, DifficultyLevel.PADAWAN),
            (LogicChallengeType.RIDDLE, "Ombre {}", "Je te suis partout au soleil mais disparais dans le noir.", "l'ombre", ["l'ombre", "la lumiere", "le reflet", "l'ami"], AgeGroup.GROUP_13_15, DifficultyLevel.CHEVALIER),
            (LogicChallengeType.RIDDLE, "Futur {}", "Je n'arrive jamais mais reste toujours a venir.", "le futur", ["le futur", "demain", "hier", "maintenant"], AgeGroup.ALL_AGES, DifficultyLevel.MAITRE),
            # DEDUCTION (10)
            (LogicChallengeType.DEDUCTION, "Syllogisme {}", "Tous les chats sont animaux. Felix est un chat. Conclusion?", "Felix est un animal", ["Felix est un animal", "Felix n'est pas un animal", "Felix est un chat", "Aucune"], AgeGroup.GROUP_10_12, DifficultyLevel.INITIE),
            (LogicChallengeType.DEDUCTION, "Transitivite {}", "A>B et B>C. Relation entre A et C?", "A>C", ["A>C", "A<C", "A=C", "Impossible"], AgeGroup.GROUP_13_15, DifficultyLevel.PADAWAN),
            (LogicChallengeType.DEDUCTION, "Contraposee {}", "Si pluie alors parapluie. Pas de parapluie. Conclusion?", "pas de pluie", ["pas de pluie", "il pleut", "peut-etre", "aucune"], AgeGroup.GROUP_13_15, DifficultyLevel.CHEVALIER),
            (LogicChallengeType.DEDUCTION, "Pair {}", "Nombre pair + nombre pair = ?", "pair", ["pair", "impair", "depend", "zero"], AgeGroup.ALL_AGES, DifficultyLevel.MAITRE),
            # SPATIAL (10)
            (LogicChallengeType.SPATIAL, "Faces Cube {}", "Combien de faces a un cube?", "6", ["6", "4", "8", "12"], AgeGroup.GROUP_10_12, DifficultyLevel.INITIE),
            (LogicChallengeType.SPATIAL, "Sommets Cube {}", "Combien de sommets a un cube?", "8", ["8", "6", "12", "4"], AgeGroup.GROUP_10_12, DifficultyLevel.PADAWAN),
            (LogicChallengeType.SPATIAL, "Aretes Cube {}", "Combien d'aretes a un cube?", "12", ["12", "6", "8", "10"], AgeGroup.GROUP_13_15, DifficultyLevel.CHEVALIER),
            (LogicChallengeType.SPATIAL, "Symetrie {}", "Lettre b dans un miroir ressemble a?", "d", ["d", "b", "p", "q"], AgeGroup.ALL_AGES, DifficultyLevel.PADAWAN),
        ]
        
        # Générer 50 challenges (répéter les templates)
        for i in range(50):
            template = challenge_templates[i % len(challenge_templates)]
            ch_type, title_tpl, question, answer, choices_list, age, diff = template
            
            title = title_tpl.format(i+1)
            
            challenges.append(LogicChallenge(
                title=title,
                description=f"Challenge de type {ch_type.value}",
                question=question,
                correct_answer=answer,
                choices=json.dumps(choices_list),  # JSON array de choix
                solution_explanation=f"La reponse est: {answer}",
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
        
        print("\n[SUCCES] Seed 50+50 avec choix multiples termine!")
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


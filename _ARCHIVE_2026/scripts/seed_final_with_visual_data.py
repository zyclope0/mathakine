#!/usr/bin/env python3
"""Seed final 50 exercices + 50 challenges AVEC visual_data complets"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("=== SEED FINAL AVEC VISUAL_DATA COMPLETS ===\n")
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import NullPool
    from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
    from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
    from app.models.attempt import Attempt
    from app.models.logic_challenge import LogicChallengeAttempt
    import os
    import json
    
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url, poolclass=NullPool, connect_args={"connect_timeout": 10})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Nettoyer d'abord
        print("[0/2] Nettoyage de la base...\n")
        db.query(Attempt).delete()
        db.query(LogicChallengeAttempt).delete()
        db.query(Exercise).delete()
        db.query(LogicChallenge).delete()
        db.commit()
        print("  Base nettoyee\n")
        
        print("[1/2] Creation de 50 exercices avec choix multiples...\n")
        exercises = []
        
        # Helper pour generer des choix multiples
        def generate_choices(correct, operation_type):
            """Genere 4 choix dont un correct"""
            correct_num = int(correct) if correct.replace("-", "").isdigit() else 0
            choices = [correct]
            
            if operation_type in ["addition", "multiplication"]:
                choices.extend([str(correct_num + 1), str(correct_num - 1), str(correct_num + 2)])
            elif operation_type == "soustraction":
                choices.extend([str(correct_num + 1), str(correct_num - 1), str(abs(correct_num - 2))])
            elif operation_type == "division":
                choices.extend([str(correct_num + 1), str(correct_num * 2), str(max(1, correct_num - 1))])
            else:
                choices.extend([str(correct_num + 1), str(correct_num - 1), str(correct_num + 5)])
            
            import random
            random.shuffle(choices)
            return choices[:4]  # Garder seulement 4 choix
        
        # Générer 50 exercices (10 de chaque type)
        types_config = [
            (ExerciseType.ADDITION, 10),
            (ExerciseType.SOUSTRACTION, 10),
            (ExerciseType.MULTIPLICATION, 10),
            (ExerciseType.DIVISION, 10),
            (ExerciseType.FRACTIONS, 5),
            (ExerciseType.GEOMETRIE, 5),
        ]
        
        for ex_type, count in types_config:
            for i in range(count):
                if i < 3:
                    a, b, diff = i+2, i+1, DifficultyLevel.INITIE
                elif i < 6:
                    a, b, diff = 10+i*3, 5+i*2, DifficultyLevel.PADAWAN
                elif i < 8:
                    a, b, diff = 20+i*5, 3+i, DifficultyLevel.CHEVALIER
                else:
                    a, b, diff = 30+i*5, 5+i, DifficultyLevel.MAITRE
                
                if ex_type == ExerciseType.ADDITION:
                    title = f"Addition Stellaire {i+1}"
                    question = f"Luke trouve {a} cristaux, Leia lui en donne {b}. Total?"
                    answer = str(a + b)
                elif ex_type == ExerciseType.SOUSTRACTION:
                    title = f"Soustraction Cristaux {i+1}"
                    question = f"Obi-Wan a {a} cristaux, en perd {b}. Reste?"
                    answer = str(a - b)
                elif ex_type == ExerciseType.MULTIPLICATION:
                    title = f"Multiplication Escadrons {i+1}"
                    question = f"{a} escadrons de {b} vaisseaux. Total?"
                    answer = str(a * b)
                elif ex_type == ExerciseType.DIVISION:
                    a = a if a > b else a + b
                    title = f"Division Flotte {i+1}"
                    question = f"{a} vaisseaux en {b} escadrons. Par escadron?"
                    answer = str(a // b)
                elif ex_type == ExerciseType.FRACTIONS:
                    title = f"Fraction {i+1}"
                    question = "1/2 + 1/4 = ?" if i % 2 == 0 else f"La moitie de {a*2} = ?"
                    answer = "3/4" if i % 2 == 0 else str(a)
                else:  # GEOMETRIE
                    if i % 2 == 0:
                        title = f"Perimetre Carre {i+1}"
                        question = f"Carre de cote {a}m. Perimetre?"
                        answer = str(4 * a)
                    else:
                        title = f"Aire Rectangle {i+1}"
                        question = f"Rectangle {a}m x {b}m. Aire?"
                        answer = str(a * b)
                
                choices = generate_choices(answer, ex_type.value)
                
                exercises.append(Exercise(
                    title=title,
                    question=question,
                    correct_answer=answer,
                    choices=json.dumps(choices),
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
        
        print("[2/2] Creation de 50 challenges avec visual_data...\n")
        challenges = []
        
        # Définitions des challenges avec visual_data complets
        challenge_defs = [
            # SEQUENCES (12)
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Suite Paires",
                "description": "Trouve le prochain nombre pair",
                "question": "2, 4, 6, 8, ?",
                "answer": "10",
                "choices": ["10", "9", "12", "7"],
                "visual_data": {"sequence": ["2", "4", "6", "8", "?"], "type": "numeric"},
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.INITIE
            },
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Suite Impairs",
                "description": "Suite des nombres impairs",
                "question": "1, 3, 5, 7, ?",
                "answer": "9",
                "choices": ["9", "8", "10", "11"],
                "visual_data": {"sequence": ["1", "3", "5", "7", "?"], "type": "numeric"},
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.INITIE
            },
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Multiples de 5",
                "description": "Table de multiplication par 5",
                "question": "5, 10, 15, 20, ?",
                "answer": "25",
                "choices": ["25", "24", "30", "20"],
                "visual_data": {"sequence": ["5", "10", "15", "20", "?"], "type": "numeric"},
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.PADAWAN
            },
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Carres Parfaits",
                "description": "Suite des carres",
                "question": "1, 4, 9, 16, ?",
                "answer": "25",
                "choices": ["25", "20", "24", "30"],
                "visual_data": {"sequence": ["1", "4", "9", "16", "?"], "type": "numeric"},
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.CHEVALIER
            },
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Suite Geometrique x2",
                "description": "Chaque nombre est multiplié par 2",
                "question": "2, 4, 8, 16, ?",
                "answer": "32",
                "choices": ["32", "24", "30", "20"],
                "visual_data": {"sequence": ["2", "4", "8", "16", "?"], "type": "numeric"},
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.CHEVALIER
            },
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Suite +3",
                "description": "Ajoute 3 à chaque fois",
                "question": "3, 6, 9, 12, ?",
                "answer": "15",
                "choices": ["15", "14", "16", "18"],
                "visual_data": {"sequence": ["3", "6", "9", "12", "?"], "type": "numeric"},
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.PADAWAN
            },
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Cubes",
                "description": "Nombres au cube",
                "question": "1, 8, 27, 64, ?",
                "answer": "125",
                "choices": ["125", "100", "120", "81"],
                "visual_data": {"sequence": ["1³=1", "2³=8", "3³=27", "4³=64", "5³=?"], "type": "numeric"},
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.MAITRE
            },
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Fibonacci Debut",
                "description": "Somme des deux précédents",
                "question": "1, 1, 2, 3, 5, ?",
                "answer": "8",
                "choices": ["8", "6", "7", "9"],
                "visual_data": {"sequence": ["1", "1", "2", "3", "5", "?"], "type": "fibonacci"},
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.MAITRE
            },
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Suite -2",
                "description": "Soustrais 2 à chaque fois",
                "question": "20, 18, 16, 14, ?",
                "answer": "12",
                "choices": ["12", "10", "13", "11"],
                "visual_data": {"sequence": ["20", "18", "16", "14", "?"], "type": "numeric"},
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.PADAWAN
            },
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Multiples de 10",
                "description": "Compte par dizaines",
                "question": "10, 20, 30, 40, ?",
                "answer": "50",
                "choices": ["50", "45", "60", "40"],
                "visual_data": {"sequence": ["10", "20", "30", "40", "?"], "type": "numeric"},
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.INITIE
            },
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Suite Geometrique x3",
                "description": "Multiplie par 3",
                "question": "2, 6, 18, 54, ?",
                "answer": "162",
                "choices": ["162", "160", "150", "180"],
                "visual_data": {"sequence": ["2", "6", "18", "54", "?"], "type": "numeric"},
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.MAITRE
            },
            {
                "type": LogicChallengeType.SEQUENCE,
                "title": "Nombres Premiers",
                "description": "Suite des premiers",
                "question": "2, 3, 5, 7, 11, ?",
                "answer": "13",
                "choices": ["13", "12", "14", "15"],
                "visual_data": {"sequence": ["2", "3", "5", "7", "11", "?"], "type": "prime"},
                "age": AgeGroup.ALL_AGES,
                "diff": DifficultyLevel.MAITRE
            },
            
            # PATTERNS (13)
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Motif AB",
                "description": "Alternance simple",
                "question": "A, B, A, B, ?",
                "answer": "A",
                "choices": ["A", "B", "C", "AB"],
                "visual_data": {"pattern": ["A", "B", "A", "B", "?"], "grid": ["A", "B", "A", "B", "?"]},
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.INITIE
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Motif ABC",
                "description": "Repetition de 3 elements",
                "question": "A, B, C, A, B, C, A, ?",
                "answer": "B",
                "choices": ["B", "A", "C", "D"],
                "visual_data": {"pattern": ["A", "B", "C", "A", "B", "C", "A", "?"], "grid": ["A", "B", "C", "A", "B", "C", "A", "?"]},
                "age": AgeGroup.ALL_AGES,
                "diff": DifficultyLevel.INITIE
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Lettres Saut 1",
                "description": "Saute une lettre",
                "question": "A, C, E, G, ?",
                "answer": "I",
                "choices": ["I", "H", "J", "F"],
                "visual_data": {"pattern": ["A", "C", "E", "G", "?"], "grid": ["A", "C", "E", "G", "?"]},
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.CHEVALIER
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Double Saut",
                "description": "Saute 2 lettres",
                "question": "A, D, G, J, ?",
                "answer": "M",
                "choices": ["M", "K", "L", "N"],
                "visual_data": {"pattern": ["A", "D", "G", "J", "?"], "grid": ["A", "D", "G", "J", "?"]},
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.MAITRE
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Couleurs",
                "description": "Alternance de couleurs",
                "question": "Rouge, Bleu, Rouge, Bleu, ?",
                "answer": "Rouge",
                "choices": ["Rouge", "Bleu", "Vert", "Jaune"],
                "visual_data": {"pattern": ["🔴", "🔵", "🔴", "🔵", "?"], "grid": ["🔴", "🔵", "🔴", "🔵", "?"]},
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.PADAWAN
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Formes",
                "description": "Reconnaissance de formes",
                "question": "Cercle, Carre, Cercle, Carre, ?",
                "answer": "Cercle",
                "choices": ["Cercle", "Carre", "Triangle", "Etoile"],
                "visual_data": {"pattern": ["○", "□", "○", "□", "?"], "grid": ["○", "□", "○", "□", "?"]},
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.PADAWAN
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Croissant",
                "description": "Repete N fois",
                "question": "1, 2, 2, 3, 3, 3, ?",
                "answer": "4",
                "choices": ["4", "3", "5", "1"],
                "visual_data": {"pattern": ["1", "2", "2", "3", "3", "3", "?"], "grid": ["1", "2", "2", "3", "3", "3", "?"]},
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.CHEVALIER
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Palindrome",
                "description": "Motif symetrique",
                "question": "1, 2, 3, 2, 1, 2, 3, ?",
                "answer": "2",
                "choices": ["2", "1", "3", "4"],
                "visual_data": {"pattern": ["1", "2", "3", "2", "1", "2", "3", "?"], "grid": ["1", "2", "3", "2", "1", "2", "3", "?"]},
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.MAITRE
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Taille Croissante",
                "description": "Les elements grandissent",
                "question": "Petit, Moyen, Grand, ?",
                "answer": "Tres Grand",
                "choices": ["Tres Grand", "Petit", "Moyen", "Enorme"],
                "visual_data": {"pattern": ["▪", "▫", "◻", "?"], "grid": ["▪", "▫", "◻", "?"]},
                "age": AgeGroup.ALL_AGES,
                "diff": DifficultyLevel.PADAWAN
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Rotation",
                "description": "Rotation horaire",
                "question": "←, ↑, →, ↓, ←, ↑, ?",
                "answer": "→",
                "choices": ["→", "↓", "←", "↑"],
                "visual_data": {"pattern": ["←", "↑", "→", "↓", "←", "↑", "?"], "grid": ["←", "↑", "→", "↓", "←", "↑", "?"]},
                "age": AgeGroup.ALL_AGES,
                "diff": DifficultyLevel.MAITRE
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Nombres Lettres",
                "description": "Combine nombres et lettres",
                "question": "1A, 2B, 3C, 4D, ?",
                "answer": "5E",
                "choices": ["5E", "4E", "5D", "6E"],
                "visual_data": {"pattern": ["1A", "2B", "3C", "4D", "?"], "grid": ["1A", "2B", "3C", "4D", "?"]},
                "age": AgeGroup.ALL_AGES,
                "diff": DifficultyLevel.MAITRE
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Motif 1-2-3",
                "description": "Compte jusqu'a 3",
                "question": "1, 2, 3, 1, 2, 3, 1, ?",
                "answer": "2",
                "choices": ["2", "1", "3", "4"],
                "visual_data": {"pattern": ["1", "2", "3", "1", "2", "3", "1", "?"], "grid": ["1", "2", "3", "1", "2", "3", "1", "?"]},
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.INITIE
            },
            {
                "type": LogicChallengeType.PATTERN,
                "title": "Voyelles",
                "description": "Suite de voyelles",
                "question": "A, E, I, O, ?",
                "answer": "U",
                "choices": ["U", "Y", "A", "I"],
                "visual_data": {"pattern": ["A", "E", "I", "O", "?"], "grid": ["A", "E", "I", "O", "?"]},
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.PADAWAN
            },
            
            # SPATIAL (10)
            {
                "type": LogicChallengeType.SPATIAL,
                "title": "Faces Cube",
                "description": "Geometrie 3D",
                "question": "Combien de faces a un cube?",
                "answer": "6",
                "choices": ["6", "4", "8", "12"],
                "visual_data": {
                    "shapes": ["cube"],
                    "type": "3d",
                    "ascii": "   +-----+\n  /     /|\n +-----+ |\n |     | +\n |     |/\n +-----+"
                },
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.INITIE
            },
            {
                "type": LogicChallengeType.SPATIAL,
                "title": "Sommets Cube",
                "description": "Points du cube",
                "question": "Combien de sommets a un cube?",
                "answer": "8",
                "choices": ["8", "6", "12", "4"],
                "visual_data": {
                    "shapes": ["cube"],
                    "type": "3d",
                    "ascii": "   ●-----●\n  /     /|\n ●-----● |\n |     | ●\n |     |/\n ●-----●"
                },
                "age": AgeGroup.GROUP_10_12,
                "diff": DifficultyLevel.PADAWAN
            },
            {
                "type": LogicChallengeType.SPATIAL,
                "title": "Aretes Cube",
                "description": "Lignes du cube",
                "question": "Combien d'aretes a un cube?",
                "answer": "12",
                "choices": ["12", "6", "8", "10"],
                "visual_data": {
                    "shapes": ["cube"],
                    "type": "3d",
                    "ascii": "   +━━━━━+\n  ┃     ┃|\n +━━━━━+ |\n |     | +\n |     |┃\n +━━━━━+"
                },
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.CHEVALIER
            },
            {
                "type": LogicChallengeType.SPATIAL,
                "title": "Symetrie Miroir",
                "description": "Reflexion",
                "question": "Lettre b dans un miroir ressemble a?",
                "answer": "d",
                "choices": ["d", "b", "p", "q"],
                "visual_data": {
                    "type": "symmetry",
                    "symmetry_line": "vertical",
                    "content": "b ↔ d"
                },
                "age": AgeGroup.ALL_AGES,
                "diff": DifficultyLevel.PADAWAN
            },
            {
                "type": LogicChallengeType.SPATIAL,
                "title": "Rotation 90°",
                "description": "Tourne a droite",
                "question": "Carre tourne 90° droite. Face avant devient?",
                "answer": "face gauche",
                "choices": ["face gauche", "face droite", "face arriere", "face avant"],
                "visual_data": {
                    "shapes": ["square"],
                    "type": "rotation",
                    "rotation": 90
                },
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.CHEVALIER
            },
            {
                "type": LogicChallengeType.SPATIAL,
                "title": "Ombre Sphere",
                "description": "Projection",
                "question": "Sphere sous lumiere verticale. Forme ombre?",
                "answer": "cercle",
                "choices": ["cercle", "carre", "triangle", "sphere"],
                "visual_data": {
                    "shapes": ["sphere"],
                    "type": "projection",
                    "ascii": "   ●\n   |\n  ◯◯◯"
                },
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.CHEVALIER
            },
            {
                "type": LogicChallengeType.SPATIAL,
                "title": "Pliage Papier",
                "description": "Transformation",
                "question": "Papier plie 2 fois, 1 trou. Nombre trous en depliant?",
                "answer": "4",
                "choices": ["4", "2", "8", "1"],
                "visual_data": {
                    "type": "folding",
                    "shapes": ["paper"],
                    "ascii": "▭ → ▭ → ● → ●●\n        ↓     ●●"
                },
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.MAITRE
            },
            {
                "type": LogicChallengeType.SPATIAL,
                "title": "De Oppose",
                "description": "Faces cachees",
                "question": "Sur un de, le 1 face au 6. Le 2 face au...?",
                "answer": "5",
                "choices": ["5", "4", "3", "6"],
                "visual_data": {
                    "shapes": ["dice"],
                    "type": "3d",
                    "ascii": " ●  ─  ⚅"
                },
                "age": AgeGroup.GROUP_13_15,
                "diff": DifficultyLevel.CHEVALIER
            },
            {
                "type": LogicChallengeType.SPATIAL,
                "title": "Vision Dessus",
                "description": "Perspective aerienne",
                "question": "Pyramide vue du dessus. Quelle forme?",
                "answer": "carre",
                "choices": ["carre", "triangle", "cercle", "pyramide"],
                "visual_data": {
                    "shapes": ["pyramid"],
                    "type": "top_view",
                    "ascii": "   △\n   |\n   ↓\n   □"
                },
                "age": AgeGroup.ALL_AGES,
                "diff": DifficultyLevel.PADAWAN
            },
            {
                "type": LogicChallengeType.SPATIAL,
                "title": "Chemins Grille",
                "description": "Comptage de chemins",
                "question": "3x3 grille, haut-gauche a bas-droite (droite/bas). Chemins?",
                "answer": "6",
                "choices": ["6", "4", "8", "9"],
                "visual_data": {
                    "type": "grid",
                    "grid": [["●", "→", "→"], ["↓", "◇", "→"], ["↓", "↓", "◆"]],
                    "size": 3
                },
                "age": AgeGroup.ALL_AGES,
                "diff": DifficultyLevel.MAITRE
            },
        ]
        
        # Compléter jusqu'à 50 en répétant
        while len(challenge_defs) < 50:
            for ch_def in challenge_defs[:15]:  # Répéter les 15 premiers
                if len(challenge_defs) >= 50:
                    break
                new_def = ch_def.copy()
                new_def["title"] = f"{ch_def['title']} Bis"
                challenge_defs.append(new_def)
        
        # Créer les challenges
        for ch_def in challenge_defs[:50]:
            challenge = LogicChallenge(
                title=ch_def["title"],
                description=ch_def["description"],
                question=ch_def["question"],
                correct_answer=ch_def["answer"],
                choices=json.dumps(ch_def["choices"]),
                visual_data=ch_def["visual_data"],
                solution_explanation=f"La reponse est: {ch_def['answer']}",
                challenge_type=ch_def["type"],
                age_group=ch_def["age"],
                difficulty=ch_def["diff"],
                is_active=True
            )
            challenges.append(challenge)
        
        for ch in challenges:
            db.add(ch)
        db.commit()
        print(f"  OK: {len(challenges)} challenges avec visual_data\n")
        
        print("[VERIFICATION]")
        ex_count = db.query(Exercise).count()
        ch_count = db.query(LogicChallenge).count()
        with_visual = db.query(LogicChallenge).filter(LogicChallenge.visual_data.isnot(None)).count()
        print(f"  Exercises: {ex_count}")
        print(f"  Challenges: {ch_count}")
        print(f"  Challenges avec visual_data: {with_visual}")
        
        print("\n[SUCCES] Seed complet termine!")
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


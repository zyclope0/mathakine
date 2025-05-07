"""
Script pour initialiser la base de données avec les modèles Mathakine
"""

import sys
import os

# Ajout du répertoire principal au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.init_db import create_tables
from app.db.base import SessionLocal
from app.models.all_models import User, UserRole, Exercise, ExerciseType, DifficultyLevel, Setting
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
from loguru import logger

def create_initial_data():
    """Crée les données initiales dans la base de données"""
    logger.info("Création des données initiales dans la base de données")
    
    db = SessionLocal()
    try:
        # Vérifier si des données existent déjà
        existing_users = db.query(User).first()
        if existing_users:
            logger.info("Des données existent déjà dans la base, abandon de l'initialisation")
            return
            
        logger.info("Création des paramètres système initiaux")
        db_settings = [
            Setting(
                key="app_name",
                value="Mathakine",
                description="Nom de l'application",
                category="system",
                is_system=True
            ),
            Setting(
                key="app_version",
                value="1.0.0",
                description="Version de l'application",
                category="system",
                is_system=True
            ),
            Setting(
                key="theme",
                value="jedi",
                description="Thème de l'interface",
                category="interface",
                is_system=False
            ),
            Setting(
                key="difficulty_default",
                value=DifficultyLevel.INITIE.value,
                description="Niveau de difficulté par défaut",
                category="exercices",
                is_system=False
            )
        ]
        db.add_all(db_settings)
        
        logger.info("Création de l'utilisateur administrateur")
        admin_user = User(
            username="maitre_yoda",
            email="yoda@jedi-temple.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            full_name="Maître Yoda",
            role=UserRole.ARCHIVISTE,
            grade_level=10,
            preferred_theme="dark"
        )
        db.add(admin_user)
        db.flush()  # Pour obtenir l'ID de l'utilisateur
        
        logger.info("Création d'un exemple d'exercice")
        example_exercise = Exercise(
            title="Addition de Padawan",
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.INITIE,
            question="Quelle est la somme de 5 + 3?",
            correct_answer="8",
            choices=["6", "7", "8", "9"],
            explanation="Pour additionner 5 et 3, il faut compter 3 nombres après 5, ce qui donne 8.",
            hint="Imagine que tu as 5 étoiles et que tu en reçois 3 de plus."
        )
        db.add(example_exercise)
        
        logger.info("Création d'un exemple de défi logique")
        example_logic_challenge = LogicChallenge(
            title="La séquence des cristaux Kyber",
            creator_id=admin_user.id,
            challenge_type=LogicChallengeType.SEQUENCE,
            age_group=AgeGroup.GROUP_10_12,
            description="Maître Yoda a disposé des cristaux Kyber dans un ordre précis. Quelle est la valeur du prochain cristal dans cette séquence: 2, 4, 8, 16, 32, ?",
            correct_answer="64",
            solution_explanation="Chaque nombre est multiplié par 2 pour obtenir le suivant.",
            hint_level1="Observe comment chaque nombre est lié au précédent.",
            hint_level2="Quelle opération mathématique simple permet de passer d'un nombre au suivant?",
            hint_level3="Essaie de multiplier chaque nombre par 2.",
            difficulty_rating=2.5,
            estimated_time_minutes=10,
            tags="séquence,multiplication,cristaux"
        )
        db.add(example_logic_challenge)
        
        logger.info("Création d'un exemple de défi de déduction")
        deduction_challenge = LogicChallenge(
            title="L'ordre des apprentis Jedi",
            creator_id=admin_user.id,
            challenge_type=LogicChallengeType.DEDUCTION,
            age_group=AgeGroup.GROUP_13_15,
            description="""Cinq apprentis Jedi (Anakin, Ben, Cere, Depa et Ezra) ont chacun un sabre laser de couleur différente (bleu, vert, violet, jaune, rouge). D'après les indices suivants, détermine qui possède quel sabre:
1. Anakin n'a pas le sabre bleu ni le rouge.
2. Ben se trouve juste à droite du propriétaire du sabre vert.
3. Cere est entre le propriétaire du sabre violet et celui du sabre jaune.
4. Depa a le sabre rouge.
5. Ezra n'est pas à côté du propriétaire du sabre bleu.""",
            correct_answer="Anakin: jaune, Ben: violet, Cere: bleu, Depa: rouge, Ezra: vert",
            solution_explanation="""Solution pas à pas:
1. Depa a le sabre rouge (indice 4).
2. Anakin n'a ni le bleu ni le rouge (indice 1), donc il a soit le jaune, soit le vert, soit le violet.
3. Ezra n'est pas à côté du propriétaire du sabre bleu (indice 5).
4. Ben est à droite du propriétaire du sabre vert (indice 2), donc Ezra est le propriétaire du sabre vert.
5. Ben est à droite d'Ezra et a donc le sabre violet.
6. Cere est entre le violet et le jaune (indice 3), donc Cere a le sabre bleu et Anakin a le sabre jaune.""",
            hint_level1="Commence par placer Depa avec le sabre rouge.",
            hint_level2="Ensuite, détermine la position de Ben par rapport au sabre vert.",
            hint_level3="Cere est entre le violet et le jaune, ce qui aide à finaliser le placement.",
            difficulty_rating=4.0,
            estimated_time_minutes=25,
            tags="déduction,logique,jedi,sabre laser"
        )
        db.add(deduction_challenge)
        
        db.commit()
        logger.success("Données initiales créées avec succès")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la création des données initiales: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Initialisation de la base de données Mathakine")
    create_tables()
    create_initial_data()
    logger.success("Base de données initialisée avec succès!") 
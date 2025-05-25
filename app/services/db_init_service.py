"""
Service d'initialisation de la base de données
"""
from loguru import logger
from sqlalchemy.orm import Session
from app.db.base import get_db, engine, Base
import random
from datetime import datetime, timedelta

from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
from app.utils.db_helpers import get_enum_value




def create_tables():
    """
    Crée toutes les tables dans la base de données.
    """
    logger.info("Création des tables dans la base de données")
    Base.metadata.create_all(bind=engine)
    logger.success("Tables créées avec succès")




def populate_test_data():
    """
    Remplit la base de données avec des données de test.
    """
    logger.info("Remplissage de la base de données avec des données de test")

    # Obtenir une session de base de données
    db_generator = get_db()
    db = next(db_generator)

    try:
        # Créer des utilisateurs de test
        create_test_users(db)

        # Créer des exercices de test
        create_test_exercises(db)

        # Créer des tentatives de test
        create_test_attempts(db)

        # Créer des défis logiques de test
        create_test_logic_challenges(db)

        db.commit()
        logger.success("Données de test créées avec succès")
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la création des données de test: {str(e)}")
        raise
    finally:
        db.close()




def create_test_users(db: Session):
    """
    Crée des utilisateurs de test dans la base de données.
    """
    logger.info("Création des utilisateurs de test")

    # Vérifier si des utilisateurs existent déjà
    if db.query(User).count() > 0:
        logger.info("Des utilisateurs existent déjà, création ignorée")
        return

    # Maintenant que le modèle utilise des énumérations natives, on peut les utiliser directement
    users = [
        User(
            username="maitre_yoda",
            email="yoda@jedi-temple.sw",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            full_name="Maître Yoda",
            role=UserRole.MAITRE,
            grade_level=12,
            created_at=datetime.now(),
        ),
        User(
            username="padawan1",
            email="padawan1@jedi-temple.sw",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            full_name="Anakin Skywalker",
            role=UserRole.PADAWAN,
            grade_level=5,
            created_at=datetime.now(),
        ),
        User(
            username="gardien1",
            email="gardien1@jedi-temple.sw",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            full_name="Mace Windu",
            role=UserRole.GARDIEN,
            grade_level=10,
            created_at=datetime.now(),
        ),
    ]

    db.add_all(users)
    db.flush()
    logger.info(f"{len(users)} utilisateurs créés")




def create_test_exercises(db: Session):
    """
    Crée des exercices de test dans la base de données.
    """
    logger.info("Création des exercices de test")

    # Vérifier si des exercices existent déjà
    if db.query(Exercise).count() > 0:
        logger.info("Des exercices existent déjà, création ignorée")
        return

    # Récupérer l'utilisateur Maître Yoda
    yoda = db.query(User).filter(User.username == "maitre_yoda").first()

    # Maintenant que le modèle utilise des énumérations natives, on peut les utiliser directement
    exercises = [
        Exercise(
            title="Addition simple",
            creator_id=yoda.id if yoda else None,
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.INITIE,
            question="Combien font 2 + 2 ?",
            correct_answer="4",
            choices=["2", "3", "4", "5"],
            explanation="2 + 2 = 4",
            created_at=datetime.now(),
        ),
        Exercise(
            title="Multiplication simple",
            creator_id=yoda.id if yoda else None,
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Combien font 5 × 6 ?",
            correct_answer="30",
            choices=["24", "30", "36", "60"],
            explanation="5 × 6 = 30",
            created_at=datetime.now(),
        ),
        Exercise(
            title="Division simple",
            creator_id=yoda.id if yoda else None,
            exercise_type=ExerciseType.DIVISION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="Combien font 20 ÷ 4 ?",
            correct_answer="5",
            choices=["4", "5", "6", "8"],
            explanation="20 ÷ 4 = 5",
            created_at=datetime.now(),
        ),
    ]

    db.add_all(exercises)
    db.flush()
    logger.info(f"{len(exercises)} exercices créés")




def create_test_attempts(db: Session):
    """
    Crée des tentatives de test dans la base de données.
    """
    logger.info("Création des tentatives de test")

    # Vérifier si des tentatives existent déjà
    if db.query(Attempt).count() > 0:
        logger.info("Des tentatives existent déjà, création ignorée")
        return

    # Récupérer un utilisateur Padawan avec l'énumération native
    padawan = db.query(User).filter(User.role == UserRole.PADAWAN).first()

    if not padawan:
        logger.warning("Aucun utilisateur Padawan trouvé, création des tentatives ignorée")
        return

    # Récupérer tous les exercices
    exercises = db.query(Exercise).all()

    if not exercises:
        logger.warning("Aucun exercice trouvé, création des tentatives ignorée")
        return

    # Traiter les exercices un par un et valider chaque insertion
    for exercise in exercises:
        # Créer une tentative réussie
        successful_attempt = Attempt(
            user_id=padawan.id,
            exercise_id=exercise.id,
            user_answer=exercise.correct_answer,
            is_correct=True,
            time_spent=random.randint(5, 30),
            attempt_number=1,
            hints_used=0,
            created_at=datetime.now() - timedelta(days=random.randint(0, 10)),
        )
        db.add(successful_attempt)
        db.flush()
        logger.info(f"Tentative réussie créée pour l'exercice {exercise.id}")

        # Créer une tentative échouée
        failed_answer = ""
        
        if exercise.choices and len(exercise.choices) > 0:
            incorrect_choices = [c for c in exercise.choices if c != exercise.correct_answer]
            if incorrect_choices:
                failed_answer = random.choice(incorrect_choices)
        
        # Si on n'a pas trouvé de mauvaise réponse, on utilise juste un espace
        if not failed_answer:
            failed_answer = " "
            
        failed_attempt = Attempt(
            user_id=padawan.id,
            exercise_id=exercise.id,
            user_answer=failed_answer,
            is_correct=False,
            time_spent=random.randint(2, 15),
            attempt_number=2,
            hints_used=1,
            created_at=datetime.now() - timedelta(days=random.randint(10, 20)),
        )
        db.add(failed_attempt)
        db.flush()
        logger.info(f"Tentative échouée créée pour l'exercice {exercise.id}")

    logger.info(f"Tentatives créées pour {len(exercises)} exercices")




def create_test_logic_challenges(db: Session):
    """
    Crée des défis logiques de test dans la base de données.
    """
    logger.info("Création des défis logiques de test")

    # Vérifier si des défis logiques existent déjà
    if db.query(LogicChallenge).count() > 0:
        logger.info("Des défis logiques existent déjà, création ignorée")
        return

    # Récupérer l'utilisateur Maître Yoda
    yoda = db.query(User).filter(User.username == "maitre_yoda").first()

    # Maintenant que le modèle utilise des énumérations natives, on peut les utiliser directement
    logic_challenges = [
        LogicChallenge(
            title="Séquence de nombres",
            creator_id=yoda.id if yoda else None,
            challenge_type=LogicChallengeType.SEQUENCE,
            age_group=AgeGroup.GROUP_10_12,
            description="Trouvez le prochain nombre dans la séquence",
            question="Complète la séquence: 2, 4, 6, 8, ...",
            correct_answer="10",
            choices=["9", "10", "12", "16"],
            solution="C'est une séquence de nombres pairs, donc le prochain nombre est 10.",
            solution_explanation="C'est une séquence de nombres pairs, donc le prochain nombre est 10.",
            content="Trouvez le prochain nombre dans la séquence: 2, 4, 6, 8, ...",
            hints=[],
            created_at=datetime.now(),
        ),
        LogicChallenge(
            title="Énigme du Sphinx",
            creator_id=yoda.id if yoda else None,
            challenge_type=LogicChallengeType.PUZZLE,
            age_group=AgeGroup.ALL_AGES,
            description="Résoudre l'énigme du Sphinx",
            question="Je suis grand quand je suis jeune et petit quand je suis vieux. Qui suis-je?",
            correct_answer="Une bougie",
            choices=["Un arbre", "Une bougie", "Un homme", "Une montagne"],
            solution="Une bougie est grande quand elle est neuve et se réduit à mesure qu'elle brûle.",
            solution_explanation="Une bougie est grande quand elle est neuve et se réduit à mesure qu'elle brûle.",
            content="Je suis grand quand je suis jeune et petit quand je suis vieux. Qui suis-je?",
            hints=[],
            created_at=datetime.now(),
        ),
    ]

    db.add_all(logic_challenges)
    db.flush()
    logger.info(f"{len(logic_challenges)} défis logiques créés")




def initialize_database():
    """
    Initialise la base de données avec les tables et les données nécessaires.
    """
    try:
        create_tables()
        populate_test_data()
        logger.success("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        raise 
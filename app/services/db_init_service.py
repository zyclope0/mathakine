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

    users = [
        User(
            username="maitre_yoda",
            email="yoda@jedi-temple.sw",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"\
                ,  # "password"
            full_name="Maître Yoda",
            role=UserRole.MAITRE,
            grade_level=12,
            created_at=datetime.now(),
        ),
        User(
            username="padawan1",
            email="padawan1@jedi-temple.sw",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"\
                ,  # "password"
            full_name="Anakin Skywalker",
            role=UserRole.PADAWAN,
            grade_level=5,
            created_at=datetime.now(),
        ),
        User(
            username="gardien1",
            email="gardien1@jedi-temple.sw",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"\
                ,  # "password"
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

    # Récupérer un utilisateur Padawan
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
            time_spent=random.randint(5, 30),  # Entre 5 et 30 secondes
            attempt_number=1,  # Définir explicitement
            hints_used=0,      # Définir explicitement
            created_at=datetime.now() - timedelta(days=random.randint(1, 10)),
        )
        db.add(successful_attempt)

        # Valider chaque insertion individuellement
        try:
            db.flush()
            logger.info(f"Tentative réussie créée pour l'exercice {exercise.id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur lors de la création de la tentative réussie: {e}")
            continue  # Passer à l'exercice suivant

        # Créer une tentative échouée
        incorrect_answers = [c for c in exercise.choices if c != exercise.correct_answer]
        if incorrect_answers:
            failed_attempt = Attempt(
                user_id=padawan.id,
                exercise_id=exercise.id,
                user_answer=random.choice(incorrect_answers),
                is_correct=False,
                time_spent=random.randint(3, 20),  # Entre 3 et 20 secondes
                attempt_number=2,  # Définir explicitement un numéro différent
                hints_used=1,      # Définir explicitement
                created_at=datetime.now() - timedelta(days=random.randint(11, 20)),
            )
            db.add(failed_attempt)

            # Valider chaque insertion individuellement
            try:
                db.flush()
                logger.info(f"Tentative échouée créée pour l'exercice {exercise.id}")
            except Exception as e:
                db.rollback()
                logger.error(f"Erreur lors de la création de la tentative échouée: {e}")

    logger.info("Tentatives créées avec succès")




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

    logic_challenges = [
        LogicChallenge(
            title="Le chemin du Jedi",
            creator_id=yoda.id if yoda else None,
            challenge_type=LogicChallengeType.SEQUENCE,
            age_group=AgeGroup.GROUP_10_12,
            description="Qui reste dans cette séquence : 1, 4, 9, 16, 25, 36, ?",
            correct_answer="49",
            solution_explanation="Ce sont les carrés des nombres entiers : 1², 2²\
                , 3², 4², 5², 6², 7²",
            hint_level1="Observe le rapport entre la position et la valeur",
            hint_level2="Pense aux opérations mathématiques de base",
            created_at=datetime.now(),
        ),
        LogicChallenge(
            title="Les cristaux Kyber",
            creator_id=yoda.id if yoda else None,
            challenge_type=LogicChallengeType.PUZZLE,
            age_group=AgeGroup.GROUP_10_12,
            description="Un maître Jedi a trouvé 3 cristaux Kyber rouges, 4 bleus et 5 verts. "
                        "Combien de sabres différents peut-il construire s'il doit utiliser exactement un cristal par sabre ?",
            correct_answer="12",
            solution_explanation="Le maître peut construire 3 + 4 + 5 = 12 sabres différents\
                , un pour chaque cristal disponible.",
            hint_level1="Chaque cristal ne peut être utilisé qu'une seule fois",
            hint_level2="Compte le nombre total de cristaux",
            created_at=datetime.now(),
        ),
        LogicChallenge(
            title="Le code d'accès",
            creator_id=yoda.id if yoda else None,
            challenge_type=LogicChallengeType.DEDUCTION,
            age_group=AgeGroup.GROUP_13_15,
            description="Pour accéder à l'archive Jedi, un code est nécessaire. Tu sais que :\n"
                        "- C'est un nombre à 3 chiffres\n"
                        "- Le premier chiffre est le double du dernier\n"
                        "- La somme des trois chiffres est 13\n"
                        "Quel est ce code ?",
            correct_answer="841",
            solution_explanation="Si on note le code abc, on a a = 2c et a + b + c\
                = 13. En remplaçant a par 2c, on obtient "
                        "2c + b + c = 13, donc 3c + b = 13. En testant les valeurs possibles\
                            , on trouve c = 1, b = 4 et a = 8.",
            hint_level1="Utilise les équations pour représenter les conditions",
            hint_level2="Essaie différentes valeurs pour le dernier chiffre",
            created_at=datetime.now(),
        ),
    ]

    db.add_all(logic_challenges)
    db.flush()
    logger.info(f"{len(logic_challenges)} défis logiques créés")




def initialize_database():
    """
    Initialise la base de données et ajoute des données de test.
    """
    create_tables()
    populate_test_data()

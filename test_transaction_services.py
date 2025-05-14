#!/usr/bin/env python
"""
Script de test pour vérifier le fonctionnement du gestionnaire de transactions et des services.
"""
import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path pour importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.services import ExerciseService, UserService, LogicChallengeService
from app.models.user import UserRole
from app.models.exercise import ExerciseType, DifficultyLevel
from app.db.transaction import TransactionManager
from app.db.adapter import DatabaseAdapter

from loguru import logger


def test_services():
    """Test les services avec le gestionnaire de transactions"""
    logger.info("Début des tests de service et transactions")
    db = SessionLocal()

    try:
        # Test 1: Création d'un utilisateur
        logger.info("Test 1: Création d'un utilisateur")
        test_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user_data = {
            "username": f"test_user_{test_timestamp}",
            "email": f"test_{test_timestamp}@example.com",
            "hashed_password": "test_password_hashed",
            "role": UserRole.PADAWAN
        }
        user = UserService.create_user(db, user_data)
        
        if user:
            logger.success(f"✅ Utilisateur créé avec succès: {user.username} (ID: {user.id})")
        else:
            logger.error("❌ Échec de la création de l'utilisateur")
            return False

        # Test 2: Création d'un exercice
        logger.info("Test 2: Création d'un exercice")
        exercise_data = {
            "title": f"Test Exercise {test_timestamp}",
            "creator_id": user.id,
            "exercise_type": ExerciseType.ADDITION,
            "difficulty": DifficultyLevel.PADAWAN,
            "question": "2 + 2 = ?",
            "correct_answer": "4",
            "explanation": "Addition simple",
            "is_archived": False
        }
        exercise = ExerciseService.create_exercise(db, exercise_data)
        
        if exercise:
            logger.success(f"✅ Exercice créé avec succès: {exercise.title} (ID: {exercise.id})")
        else:
            logger.error("❌ Échec de la création de l'exercice")
            return False

        # Test 3: Archivage d'un exercice
        logger.info("Test 3: Archivage d'un exercice")
        archive_result = ExerciseService.archive_exercise(db, exercise.id)
        
        if archive_result:
            # Récupérer l'exercice mis à jour pour vérifier que is_archived est True
            archived_exercise = ExerciseService.get_exercise(db, exercise.id)
            if archived_exercise and archived_exercise.is_archived:
                logger.success(f"✅ Exercice archivé avec succès: {archived_exercise.title}")
            else:
                logger.error("❌ L'exercice n'a pas été correctement archivé")
                return False
        else:
            logger.error("❌ Échec de l'archivage de l'exercice")
            return False

        # Test 4: Enregistrement d'une tentative
        logger.info("Test 4: Enregistrement d'une tentative")
        attempt_data = {
            "user_id": user.id,
            "exercise_id": exercise.id,
            "user_answer": "4",
            "is_correct": True,
            "time_spent": 5.2
        }
        attempt = ExerciseService.record_attempt(db, attempt_data)
        
        if attempt:
            logger.success(f"✅ Tentative enregistrée avec succès (ID: {attempt.id})")
        else:
            logger.error("❌ Échec de l'enregistrement de la tentative")
            return False

        # Test 5: Suppression de l'utilisateur (avec cascade)
        logger.info("Test 5: Suppression de l'utilisateur (avec cascade)")
        delete_result = UserService.delete_user(db, user.id)
        
        if delete_result:
            # Vérifier que l'utilisateur et ses dépendances ont été supprimés
            deleted_user = UserService.get_user(db, user.id)
            deleted_exercise = ExerciseService.get_exercise(db, exercise.id)
            
            if not deleted_user and not deleted_exercise:
                logger.success("✅ Utilisateur et ses dépendances supprimés avec succès")
            else:
                if deleted_user:
                    logger.error("❌ L'utilisateur n'a pas été supprimé")
                if deleted_exercise:
                    logger.error("❌ L'exercice n'a pas été supprimé en cascade")
                return False
        else:
            logger.error("❌ Échec de la suppression de l'utilisateur")
            return False

        logger.success("✅ Tous les tests ont réussi!")
        return True

    except Exception as e:
        logger.error(f"❌ Erreur pendant les tests: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_services()
    if success:
        logger.info("Tests réussis. Le système de transaction et les services fonctionnent correctement.")
        sys.exit(0)
    else:
        logger.error("Échec des tests. Veuillez vérifier les erreurs ci-dessus.")
        sys.exit(1) 
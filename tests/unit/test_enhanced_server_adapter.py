#!/usr/bin/env python
"""
Test pour l'adaptateur EnhancedServerAdapter.
Vérifie que l'adaptateur fonctionne correctement avec le système de transaction.
"""
import sys
import os
import json
from datetime import datetime

# Ajouter le répertoire parent au path pour importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.models.exercise import Exercise
from app.models.attempt import Attempt
from app.models.user import User, UserRole
from app.db.transaction import TransactionManager
from app.core.constants import ExerciseTypes, DifficultyLevels

from loguru import logger


def test_enhanced_server_adapter():
    """Test l'adaptateur EnhancedServerAdapter avec le système de transaction"""
    logger.info("Test de l'adaptateur EnhancedServerAdapter")

    # Obtenir une session de base de données
    db = EnhancedServerAdapter.get_db_session()

    try:
        # Préparation: Créer un utilisateur test si nécessaire
        logger.info("Préparation: Création d'un utilisateur test")
        from sqlalchemy.orm import Session
        from app.db.transaction import TransactionManager
        
        # Vérifier si l'utilisateur test existe déjà
        with TransactionManager.transaction(db) as session:
            test_user = session.query(User).filter(User.username == "test_user").first()
            if not test_user:
                # Créer un utilisateur test
                test_user = User(
                    username="test_user",
                    email="test@example.com",
                    hashed_password="test_password_hashed",
                    role=UserRole.PADAWAN  # Utiliser une valeur valide de l'enum UserRole
                )
                session.add(test_user)
        
        # S'assurer que l'utilisateur est créé
        user_id = test_user.id
        logger.info(f"Utilisateur test créé/trouvé avec ID {user_id}")
        
        # Test 1: Créer un exercice
        logger.info("Test 1: Création d'un exercice")
        exercise_data = {
            "title": "Test via adaptateur",
            "exercise_type": ExerciseTypes.ADDITION,
            "difficulty": DifficultyLevels.INITIE,
            "question": "1 + 2 = ?",
            "correct_answer": "3",
            "choices": json.dumps(["2", "3", "4", "5"]),
            "is_active": True,
            "is_archived": False
        }
        
        exercise = EnhancedServerAdapter.create_exercise(db, exercise_data)
        assert exercise is not None, "L'exercice n'a pas été créé"
        logger.info(f"Exercice créé avec ID {exercise['id']}")
        
        # Test 2: Récupérer l'exercice
        logger.info("Test 2: Récupération de l'exercice")
        retrieved_exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise['id'])
        assert retrieved_exercise is not None, "L'exercice n'a pas été récupéré"
        assert retrieved_exercise['title'] == "Test via adaptateur", "Le titre de l'exercice est incorrect"
        logger.info("Exercice récupéré avec succès")
        
        # Test 3: Lister les exercices
        logger.info("Test 3: Liste des exercices")
        exercises = EnhancedServerAdapter.list_exercises(db, 
                                                      exercise_type=ExerciseTypes.ADDITION,
                                                      difficulty=DifficultyLevels.INITIE)
        assert len(exercises) > 0, "Aucun exercice n'a été trouvé"
        logger.info(f"{len(exercises)} exercices trouvés")
        
        # Test 4: Enregistrer une tentative
        logger.info("Test 4: Enregistrement d'une tentative")
        attempt_data = {
            "user_id": user_id,  # Utiliser l'ID de l'utilisateur créé
            "exercise_id": exercise['id'],
            "user_answer": "3",
            "is_correct": True,
            "time_spent": 5.2
        }
        
        attempt = EnhancedServerAdapter.record_attempt(db, attempt_data)
        assert attempt is not None, "La tentative n'a pas été enregistrée"
        logger.info(f"Tentative enregistrée avec ID {attempt['id']}")
        
        # Test 5: Archiver l'exercice
        logger.info("Test 5: Archivage de l'exercice")
        success = EnhancedServerAdapter.archive_exercise(db, exercise['id'])
        assert success, "L'exercice n'a pas été archivé"
        
        # Vérifier que l'exercice est bien archivé
        archived_exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise['id'])
        assert archived_exercise['is_archived'], "L'exercice n'est pas marqué comme archivé"
        logger.info("Exercice archivé avec succès")
        
        logger.info("Tous les tests ont réussi !")
        
    finally:
        # Fermer la session dans tous les cas
        EnhancedServerAdapter.close_db_session(db)


if __name__ == "__main__":
    logger.info("Début des tests de l'adaptateur EnhancedServerAdapter")
    test_enhanced_server_adapter()
    logger.info("Fin des tests") 
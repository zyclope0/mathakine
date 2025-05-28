#!/usr/bin/env python3
"""
Script de test pour vérifier le workflow complet des statistiques.

Ce script :
1. Crée un utilisateur de test
2. Crée quelques exercices
3. Simule des tentatives de réponse
4. Vérifie que les statistiques sont mises à jour
"""

import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.models.legacy_tables import UserStats
from app.services.exercise_service import ExerciseService
from app.utils.db_helpers import get_enum_value
from loguru import logger


def test_statistics_workflow():
    """Teste le workflow complet des statistiques."""
    logger.info("🧪 Début du test du workflow des statistiques")
    
    db = SessionLocal()
    
    try:
        # 1. Créer un utilisateur de test
        test_user = User(
            username=f"test_stats_user_{int(datetime.now().timestamp())}",
            email=f"test_stats_{int(datetime.now().timestamp())}@example.com",
            hashed_password="test_password",
            role=get_enum_value(UserRole, UserRole.PADAWAN.value, db)
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        logger.info(f"✅ Utilisateur de test créé: {test_user.username} (ID: {test_user.id})")
        
        # 2. Créer un exercice de test
        test_exercise = Exercise(
            title="Test Addition",
            exercise_type=get_enum_value(ExerciseType, ExerciseType.ADDITION.value, db),
            difficulty=get_enum_value(DifficultyLevel, DifficultyLevel.INITIE.value, db),
            question="2 + 3 = ?",
            correct_answer="5",
            choices=["3", "4", "5", "6"],
            explanation="2 + 3 = 5",
            is_active=True,
            is_archived=False
        )
        db.add(test_exercise)
        db.commit()
        db.refresh(test_exercise)
        
        logger.info(f"✅ Exercice de test créé: {test_exercise.title} (ID: {test_exercise.id})")
        
        # 3. Vérifier l'état initial des statistiques
        initial_progress_count = db.query(Progress).filter(Progress.user_id == test_user.id).count()
        initial_user_stats_count = db.query(UserStats).count()
        
        logger.info(f"📊 État initial - Progress: {initial_progress_count}, UserStats: {initial_user_stats_count}")
        
        # 4. Simuler une tentative correcte via ExerciseService
        attempt_data = {
            "user_id": test_user.id,
            "exercise_id": test_exercise.id,
            "user_answer": "5",
            "is_correct": True,
            "time_spent": 15.5,
            "attempt_number": 1
        }
        
        logger.info("🎯 Simulation d'une tentative correcte...")
        attempt = ExerciseService.record_attempt(db, attempt_data)
        
        if attempt:
            logger.success(f"✅ Tentative enregistrée avec ID: {attempt.id}")
        else:
            logger.error("❌ Échec de l'enregistrement de la tentative")
            return False
        
        # 5. Vérifier que les statistiques ont été mises à jour
        db.commit()  # S'assurer que tout est persisté
        
        # Vérifier Progress
        progress_records = db.query(Progress).filter(Progress.user_id == test_user.id).all()
        logger.info(f"📈 Progress trouvés: {len(progress_records)}")
        
        for progress in progress_records:
            logger.info(f"   - Type: {progress.exercise_type}, Tentatives: {progress.total_attempts}, Correctes: {progress.correct_attempts}")
        
        # Vérifier UserStats
        user_stats_records = db.query(UserStats).all()
        logger.info(f"📊 UserStats trouvés: {len(user_stats_records)}")
        
        for stat in user_stats_records:
            logger.info(f"   - Type: {stat.exercise_type}, Difficulté: {stat.difficulty}, Tentatives: {stat.total_attempts}")
        
        # 6. Simuler une tentative incorrecte
        attempt_data_2 = {
            "user_id": test_user.id,
            "exercise_id": test_exercise.id,
            "user_answer": "4",
            "is_correct": False,
            "time_spent": 25.0,
            "attempt_number": 2
        }
        
        logger.info("🎯 Simulation d'une tentative incorrecte...")
        attempt_2 = ExerciseService.record_attempt(db, attempt_data_2)
        
        if attempt_2:
            logger.success(f"✅ Deuxième tentative enregistrée avec ID: {attempt_2.id}")
        else:
            logger.error("❌ Échec de l'enregistrement de la deuxième tentative")
            return False
        
        # 7. Vérifier les statistiques finales
        db.commit()
        
        final_progress_records = db.query(Progress).filter(Progress.user_id == test_user.id).all()
        final_user_stats_records = db.query(UserStats).all()
        
        logger.info(f"📈 État final - Progress: {len(final_progress_records)}, UserStats: {len(final_user_stats_records)}")
        
        # Vérifier les valeurs attendues
        success = True
        
        if len(final_progress_records) > 0:
            progress = final_progress_records[0]
            if progress.total_attempts == 2 and progress.correct_attempts == 1:
                logger.success("✅ Progress correctement mis à jour")
            else:
                logger.error(f"❌ Progress incorrect: {progress.total_attempts} tentatives, {progress.correct_attempts} correctes (attendu: 2, 1)")
                success = False
        else:
            logger.error("❌ Aucun Progress créé")
            success = False
        
        if len(final_user_stats_records) > 0:
            # Chercher le UserStats correspondant à notre exercice
            matching_stats = [s for s in final_user_stats_records 
                            if s.exercise_type == test_exercise.exercise_type.value 
                            and s.difficulty == test_exercise.difficulty.value]
            
            if matching_stats:
                stat = matching_stats[0]
                if stat.total_attempts == 2 and stat.correct_attempts == 1:
                    logger.success("✅ UserStats correctement mis à jour")
                else:
                    logger.error(f"❌ UserStats incorrect: {stat.total_attempts} tentatives, {stat.correct_attempts} correctes (attendu: 2, 1)")
                    success = False
            else:
                logger.error("❌ Aucun UserStats correspondant trouvé")
                success = False
        else:
            logger.error("❌ Aucun UserStats créé")
            success = False
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


def main():
    """Point d'entrée principal."""
    logger.info("🚀 Démarrage du test du workflow des statistiques")
    
    success = test_statistics_workflow()
    
    if success:
        logger.success("🎉 Test du workflow des statistiques réussi!")
        print("\n✅ RÉSULTAT: Le système de statistiques fonctionne correctement")
    else:
        logger.error("❌ Test du workflow des statistiques échoué!")
        print("\n❌ RÉSULTAT: Le système de statistiques a des problèmes")
        sys.exit(1)


if __name__ == "__main__":
    main() 
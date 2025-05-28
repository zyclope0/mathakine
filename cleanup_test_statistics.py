#!/usr/bin/env python3
"""
Script de nettoyage des données de test pour les statistiques.
Supprime uniquement les données créées lors des tests.
"""

import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.user import User
from app.models.exercise import Exercise
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.models.legacy_tables import UserStats
from loguru import logger


def cleanup_test_data():
    """Nettoie les données de test créées lors des tests de statistiques."""
    logger.info("🧹 Début du nettoyage des données de test...")
    
    db = SessionLocal()
    
    try:
        # 1. Supprimer les utilisateurs de test
        test_users = db.query(User).filter(
            User.username.like('test_stats_user_%')
        ).all()
        
        user_ids = [user.id for user in test_users]
        logger.info(f"📋 Trouvé {len(test_users)} utilisateurs de test à supprimer")
        
        if user_ids:
            # Supprimer les tentatives liées
            attempts_deleted = db.query(Attempt).filter(
                Attempt.user_id.in_(user_ids)
            ).delete(synchronize_session=False)
            logger.info(f"🗑️ {attempts_deleted} tentatives supprimées")
            
            # Supprimer les progress liés
            progress_deleted = db.query(Progress).filter(
                Progress.user_id.in_(user_ids)
            ).delete(synchronize_session=False)
            logger.info(f"📊 {progress_deleted} enregistrements Progress supprimés")
            
            # Supprimer les utilisateurs
            users_deleted = db.query(User).filter(
                User.username.like('test_stats_user_%')
            ).delete(synchronize_session=False)
            logger.info(f"👤 {users_deleted} utilisateurs de test supprimés")
        
        # 2. Supprimer les exercices de test
        test_exercises = db.query(Exercise).filter(
            Exercise.title.like('Test %')
        ).all()
        
        exercise_ids = [ex.id for ex in test_exercises]
        logger.info(f"📝 Trouvé {len(test_exercises)} exercices de test à supprimer")
        
        if exercise_ids:
            # Supprimer les tentatives liées aux exercices de test
            exercise_attempts_deleted = db.query(Attempt).filter(
                Attempt.exercise_id.in_(exercise_ids)
            ).delete(synchronize_session=False)
            logger.info(f"🎯 {exercise_attempts_deleted} tentatives d'exercices de test supprimées")
            
            # Supprimer les exercices de test
            exercises_deleted = db.query(Exercise).filter(
                Exercise.title.like('Test %')
            ).delete(synchronize_session=False)
            logger.info(f"📚 {exercises_deleted} exercices de test supprimés")
        
        # 3. Réinitialiser les UserStats (optionnel - garder les vraies données)
        # Nous ne supprimons que les UserStats si elles sont vides ou incohérentes
        
        db.commit()
        logger.success("✅ Nettoyage des données de test terminé avec succès!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du nettoyage: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()


def verify_cleanup():
    """Vérifie que le nettoyage a bien fonctionné."""
    logger.info("🔍 Vérification du nettoyage...")
    
    db = SessionLocal()
    
    try:
        # Compter ce qui reste
        test_users_count = db.query(User).filter(
            User.username.like('test_stats_user_%')
        ).count()
        
        test_exercises_count = db.query(Exercise).filter(
            Exercise.title.like('Test %')
        ).count()
        
        total_attempts = db.query(Attempt).count()
        total_progress = db.query(Progress).count()
        total_user_stats = db.query(UserStats).count()
        
        logger.info(f"📊 État après nettoyage:")
        logger.info(f"   - Utilisateurs de test restants: {test_users_count}")
        logger.info(f"   - Exercices de test restants: {test_exercises_count}")
        logger.info(f"   - Total tentatives: {total_attempts}")
        logger.info(f"   - Total progress: {total_progress}")
        logger.info(f"   - Total user_stats: {total_user_stats}")
        
        if test_users_count == 0 and test_exercises_count == 0:
            logger.success("✅ Nettoyage vérifié - Aucune donnée de test restante")
            return True
        else:
            logger.warning("⚠️ Des données de test persistent encore")
            return False
    
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("🚀 Démarrage du script de nettoyage des données de test")
    
    success = cleanup_test_data()
    
    if success:
        verify_cleanup()
        logger.success("🎉 Script de nettoyage terminé avec succès!")
    else:
        logger.error("❌ Échec du nettoyage")
        sys.exit(1) 
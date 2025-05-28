#!/usr/bin/env python3
"""
Script pour vérifier les données de l'utilisateur Obiwan dans le tableau de bord.
"""

import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import text

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.user import User
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.models.legacy_tables import UserStats
from loguru import logger

def check_obiwan_data():
    """Vérifie les données de l'utilisateur Obiwan."""
    logger.info("🔍 Vérification des données de l'utilisateur Obiwan...")
    
    db = SessionLocal()
    try:
        # Chercher l'utilisateur ObiWan (avec W majuscule)
        obiwan = db.query(User).filter(User.username == "ObiWan").first()
        
        if not obiwan:
            logger.error("❌ Utilisateur 'Obiwan' non trouvé dans la base de données")
            
            # Lister tous les utilisateurs disponibles
            all_users = db.query(User).all()
            logger.info(f"👥 Utilisateurs disponibles ({len(all_users)}):")
            for user in all_users:
                logger.info(f"   - ID: {user.id}, Username: {user.username}, Email: {user.email}")
            return False
        
        logger.success(f"✅ Utilisateur Obiwan trouvé - ID: {obiwan.id}, Email: {obiwan.email}")
        
        # Vérifier les tentatives
        attempts = db.query(Attempt).filter(Attempt.user_id == obiwan.id).all()
        logger.info(f"📝 Tentatives pour Obiwan: {len(attempts)}")
        
        if attempts:
            for attempt in attempts[:5]:  # Afficher les 5 premières
                logger.info(f"   - Tentative ID: {attempt.id}, Exercice: {attempt.exercise_id}, Correct: {attempt.is_correct}")
        
        # Vérifier les Progress
        progress_records = db.query(Progress).filter(Progress.user_id == obiwan.id).all()
        logger.info(f"📊 Progress pour Obiwan: {len(progress_records)}")
        
        if progress_records:
            for progress in progress_records:
                logger.info(f"   - Type: {progress.exercise_type}, Difficulté: {progress.difficulty}")
                logger.info(f"     Tentatives: {progress.total_attempts}, Réussites: {progress.correct_attempts}")
        
        # Vérifier les UserStats globales
        user_stats = db.query(UserStats).all()
        logger.info(f"🌍 UserStats globales: {len(user_stats)}")
        
        # Test de l'API de statistiques
        logger.info("🔍 Test de récupération des statistiques via service...")
        
        # Simuler l'appel API
        from app.services.user_service import UserService
        try:
            stats = UserService.get_user_stats(db, obiwan.id)
            logger.info(f"📈 Statistiques récupérées: {stats}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des stats: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification: {e}")
        return False
    finally:
        db.close()

def create_test_data_for_obiwan():
    """Crée des données de test pour Obiwan si nécessaire."""
    logger.info("🔧 Création de données de test pour Obiwan...")
    
    db = SessionLocal()
    try:
        # Chercher ObiWan (avec W majuscule)
        obiwan = db.query(User).filter(User.username == "ObiWan").first()
        if not obiwan:
            logger.error("❌ Utilisateur ObiWan non trouvé")
            return False
        
        # Vérifier s'il a déjà des données
        existing_attempts = db.query(Attempt).filter(Attempt.user_id == obiwan.id).count()
        if existing_attempts > 0:
            logger.info(f"ℹ️ Obiwan a déjà {existing_attempts} tentatives")
            return True
        
        # Créer un exercice de test si nécessaire
        from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
        
        test_exercise = db.query(Exercise).first()
        if not test_exercise:
            logger.info("📝 Création d'un exercice de test...")
            test_exercise = Exercise(
                title="Test Addition",
                question="Combien font 2 + 2 ?",
                correct_answer="4",
                exercise_type=ExerciseType.ADDITION,
                difficulty=DifficultyLevel.INITIE,
                creator_id=obiwan.id
            )
            db.add(test_exercise)
            db.commit()
            db.refresh(test_exercise)
        
        # Créer quelques tentatives de test
        logger.info("📝 Création de tentatives de test...")
        
        from app.services.exercise_service import ExerciseService
        
        # Tentative 1 - Correcte
        attempt_data_1 = {
            "user_id": obiwan.id,
            "exercise_id": test_exercise.id,
            "user_answer": "4",
            "is_correct": True,
            "time_spent": 15.5
        }
        
        # Tentative 2 - Incorrecte
        attempt_data_2 = {
            "user_id": obiwan.id,
            "exercise_id": test_exercise.id,
            "user_answer": "5",
            "is_correct": False,
            "time_spent": 12.3
        }
        
        # Enregistrer les tentatives via le service (qui devrait mettre à jour les stats)
        attempt1 = ExerciseService.record_attempt(db, attempt_data_1)
        attempt2 = ExerciseService.record_attempt(db, attempt_data_2)
        
        if attempt1 and attempt2:
            logger.success("✅ Données de test créées avec succès pour Obiwan")
            return True
        else:
            logger.error("❌ Erreur lors de la création des données de test")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des données: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Fonction principale."""
    logger.info("🚀 Démarrage de la vérification des données Obiwan...")
    
    # Vérifier les données existantes
    if not check_obiwan_data():
        return
    
    # Demander si on veut créer des données de test
    print("\n" + "="*60)
    print("🤔 Voulez-vous créer des données de test pour Obiwan ?")
    print("   Cela ajoutera quelques tentatives d'exercices pour tester le tableau de bord.")
    response = input("   Tapez 'oui' pour continuer: ").lower().strip()
    
    if response in ['oui', 'o', 'yes', 'y']:
        create_test_data_for_obiwan()
        
        # Revérifier après création
        logger.info("🔍 Nouvelle vérification après création des données...")
        check_obiwan_data()
    
    logger.success("🎉 Vérification terminée!")

if __name__ == "__main__":
    main() 
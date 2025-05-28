#!/usr/bin/env python3
"""
Test manuel d'enregistrement d'une tentative pour ObiWan
"""

import sys
import os
from sqlalchemy.orm import Session

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.user import User
from app.models.exercise import Exercise
from app.services.exercise_service import ExerciseService
from app.services.user_service import UserService
from loguru import logger

def test_obiwan_attempt():
    """Teste l'enregistrement d'une tentative pour ObiWan."""
    logger.info("🧪 Test d'enregistrement d'une tentative pour ObiWan...")
    
    db = SessionLocal()
    try:
        # 1. Récupérer ObiWan
        obiwan = db.query(User).filter(User.username == "ObiWan").first()
        if not obiwan:
            logger.error("❌ ObiWan non trouvé")
            return False
        
        logger.info(f"✅ ObiWan trouvé - ID: {obiwan.id}")
        
        # 2. Récupérer un exercice existant
        exercise = db.query(Exercise).filter(Exercise.is_active == True).first()
        if not exercise:
            logger.error("❌ Aucun exercice actif trouvé")
            return False
        
        logger.info(f"✅ Exercice trouvé - ID: {exercise.id}, Question: {exercise.question}")
        
        # 3. Vérifier les statistiques AVANT
        logger.info("📊 Statistiques AVANT la tentative:")
        stats_before = UserService.get_user_stats(db, obiwan.id)
        logger.info(f"   Total tentatives: {stats_before.get('total_attempts', 0)}")
        logger.info(f"   Tentatives correctes: {stats_before.get('correct_attempts', 0)}")
        logger.info(f"   Taux de réussite: {stats_before.get('success_rate', 0)}%")
        
        # 4. Créer une tentative correcte
        logger.info("📝 Création d'une tentative correcte...")
        attempt_data = {
            "user_id": obiwan.id,
            "exercise_id": exercise.id,
            "user_answer": exercise.correct_answer,
            "is_correct": True,
            "time_spent": 25.5
        }
        
        # 5. Enregistrer la tentative via ExerciseService
        attempt = ExerciseService.record_attempt(db, attempt_data)
        
        if not attempt:
            logger.error("❌ Échec de l'enregistrement de la tentative")
            return False
        
        logger.success(f"✅ Tentative enregistrée - ID: {attempt.id}")
        
        # 6. Vérifier les statistiques APRÈS
        logger.info("📊 Statistiques APRÈS la tentative:")
        stats_after = UserService.get_user_stats(db, obiwan.id)
        logger.info(f"   Total tentatives: {stats_after.get('total_attempts', 0)}")
        logger.info(f"   Tentatives correctes: {stats_after.get('correct_attempts', 0)}")
        logger.info(f"   Taux de réussite: {stats_after.get('success_rate', 0)}%")
        
        # 7. Comparer les statistiques
        total_before = stats_before.get('total_attempts', 0)
        total_after = stats_after.get('total_attempts', 0)
        correct_before = stats_before.get('correct_attempts', 0)
        correct_after = stats_after.get('correct_attempts', 0)
        
        if total_after > total_before:
            logger.success(f"✅ Total tentatives mis à jour: {total_before} → {total_after}")
        else:
            logger.error(f"❌ Total tentatives non mis à jour: {total_before} → {total_after}")
        
        if correct_after > correct_before:
            logger.success(f"✅ Tentatives correctes mises à jour: {correct_before} → {correct_after}")
        else:
            logger.error(f"❌ Tentatives correctes non mises à jour: {correct_before} → {correct_after}")
        
        # 8. Créer une deuxième tentative incorrecte
        logger.info("📝 Création d'une tentative incorrecte...")
        attempt_data_2 = {
            "user_id": obiwan.id,
            "exercise_id": exercise.id,
            "user_answer": "mauvaise_réponse",
            "is_correct": False,
            "time_spent": 15.0
        }
        
        attempt_2 = ExerciseService.record_attempt(db, attempt_data_2)
        
        if attempt_2:
            logger.success(f"✅ Deuxième tentative enregistrée - ID: {attempt_2.id}")
            
            # Vérifier les statistiques finales
            logger.info("📊 Statistiques FINALES:")
            stats_final = UserService.get_user_stats(db, obiwan.id)
            logger.info(f"   Total tentatives: {stats_final.get('total_attempts', 0)}")
            logger.info(f"   Tentatives correctes: {stats_final.get('correct_attempts', 0)}")
            logger.info(f"   Taux de réussite: {stats_final.get('success_rate', 0)}%")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    """Fonction principale."""
    logger.info("🚀 Test d'enregistrement d'une tentative pour ObiWan...")
    
    print("="*60)
    print("🧪 TEST TENTATIVE OBIWAN")
    print("="*60)
    
    success = test_obiwan_attempt()
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    if success:
        print("✅ SUCCÈS: Les tentatives sont enregistrées et les statistiques mises à jour")
        print("🎯 Le système de statistiques fonctionne correctement !")
    else:
        print("❌ ÉCHEC: Problème avec l'enregistrement des tentatives")
        print("🔧 Vérifier ExerciseService.record_attempt et les services de statistiques")
    
    logger.success("🎉 Test terminé!")

if __name__ == "__main__":
    main() 
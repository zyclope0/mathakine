#!/usr/bin/env python3
"""
Debug en temps réel des tentatives d'ObiWan
"""

import sys
import os
import time
from datetime import datetime

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.user import User
from app.models.attempt import Attempt
from loguru import logger

def monitor_obiwan_attempts():
    """Surveille les tentatives d'ObiWan en temps réel."""
    logger.info("🔍 Surveillance des tentatives d'ObiWan en temps réel...")
    
    # Récupérer l'ID d'ObiWan
    db = SessionLocal()
    try:
        obiwan = db.query(User).filter(User.username == "ObiWan").first()
        if not obiwan:
            logger.error("❌ ObiWan non trouvé")
            return
        
        obiwan_id = obiwan.id
        logger.info(f"✅ ObiWan trouvé - ID: {obiwan_id}")
        
        # Compter les tentatives initiales
        initial_count = db.query(Attempt).filter(Attempt.user_id == obiwan_id).count()
        logger.info(f"📊 Tentatives initiales: {initial_count}")
        
    finally:
        db.close()
    
    print("\n" + "="*60)
    print("🔍 SURVEILLANCE EN TEMPS RÉEL")
    print("="*60)
    print(f"Utilisateur: ObiWan (ID: {obiwan_id})")
    print(f"Tentatives initiales: {initial_count}")
    print("Appuyez sur Ctrl+C pour arrêter...")
    print("="*60)
    
    last_count = initial_count
    
    try:
        while True:
            time.sleep(2)  # Vérifier toutes les 2 secondes
            
            db = SessionLocal()
            try:
                current_count = db.query(Attempt).filter(Attempt.user_id == obiwan_id).count()
                
                if current_count != last_count:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    new_attempts = current_count - last_count
                    
                    print(f"\n🎯 [{timestamp}] NOUVELLE TENTATIVE DÉTECTÉE!")
                    print(f"   Tentatives: {last_count} → {current_count} (+{new_attempts})")
                    
                    # Récupérer les dernières tentatives
                    latest_attempts = db.query(Attempt).filter(
                        Attempt.user_id == obiwan_id
                    ).order_by(Attempt.created_at.desc()).limit(new_attempts).all()
                    
                    for attempt in latest_attempts:
                        status = "✅ CORRECTE" if attempt.is_correct else "❌ INCORRECTE"
                        print(f"   - Exercice {attempt.exercise_id}: {attempt.user_answer} {status}")
                    
                    last_count = current_count
                else:
                    # Afficher un point pour montrer que le script fonctionne
                    print(".", end="", flush=True)
                    
            finally:
                db.close()
                
    except KeyboardInterrupt:
        print(f"\n\n📊 RÉSUMÉ FINAL")
        print(f"Tentatives finales: {last_count}")
        print(f"Nouvelles tentatives: {last_count - initial_count}")
        logger.success("🎉 Surveillance terminée!")

def main():
    """Fonction principale."""
    monitor_obiwan_attempts()

if __name__ == "__main__":
    main() 
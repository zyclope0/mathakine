#!/usr/bin/env python3
"""
Définir un mot de passe pour ObiWan
"""

import sys
import os
from passlib.context import CryptContext

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.user import User
from loguru import logger

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fix_obiwan_password():
    """Définit un mot de passe pour ObiWan."""
    logger.info("🔧 Définition d'un mot de passe pour ObiWan...")
    
    db = SessionLocal()
    try:
        # Récupérer ObiWan
        obiwan = db.query(User).filter(User.username == "ObiWan").first()
        if not obiwan:
            logger.error("❌ Utilisateur ObiWan non trouvé")
            return False
        
        logger.info(f"✅ ObiWan trouvé - ID: {obiwan.id}")
        logger.info(f"   Mot de passe actuel: {'Défini' if obiwan.hashed_password else 'Non défini'}")
        
        # Définir le nouveau mot de passe
        new_password = "jedi123"
        hashed_password = pwd_context.hash(new_password)
        
        # Mettre à jour le mot de passe
        obiwan.hashed_password = hashed_password
        db.commit()
        
        logger.success(f"✅ Mot de passe défini pour ObiWan: {new_password}")
        logger.info(f"   Hash: {hashed_password[:50]}...")
        
        # Vérifier que le mot de passe fonctionne
        if pwd_context.verify(new_password, hashed_password):
            logger.success("✅ Vérification du mot de passe réussie")
            return True
        else:
            logger.error("❌ Erreur lors de la vérification du mot de passe")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Fonction principale."""
    print("="*60)
    print("🔧 DÉFINITION MOT DE PASSE OBIWAN")
    print("="*60)
    
    success = fix_obiwan_password()
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    if success:
        print("✅ SUCCÈS: Mot de passe défini pour ObiWan")
        print("🔑 Mot de passe: jedi123")
        print("🎯 Vous pouvez maintenant tester la soumission d'exercices")
    else:
        print("❌ ÉCHEC: Impossible de définir le mot de passe")
    
    logger.success("🎉 Terminé!")

if __name__ == "__main__":
    main() 
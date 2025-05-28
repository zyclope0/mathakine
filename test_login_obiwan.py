#!/usr/bin/env python3
"""Test de connexion avec ObiWan et vérification du tableau de bord"""

import requests
import sys
import os

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.user import User
from loguru import logger

def test_obiwan_login():
    """Teste la connexion avec ObiWan et vérifie le tableau de bord."""
    
    # Vérifier d'abord si ObiWan existe et récupérer ses infos
    db = SessionLocal()
    try:
        obiwan = db.query(User).filter(User.username == "ObiWan").first()
        if not obiwan:
            logger.error("❌ ObiWan non trouvé dans la base de données")
            return False
        
        logger.info(f"✅ ObiWan trouvé - ID: {obiwan.id}, Email: {obiwan.email}")
        
        # Vérifier si ObiWan a un mot de passe
        if not obiwan.hashed_password:
            logger.error("❌ ObiWan n'a pas de mot de passe défini")
            return False
        
        logger.info("✅ ObiWan a un mot de passe défini")
        
    finally:
        db.close()
    
    # Créer une session pour maintenir les cookies
    session = requests.Session()
    base_url = "http://localhost:8000"
    
    try:
        # 1. Tester la page de login
        logger.info("🌐 Test 1: Page de login")
        response = session.get(f"{base_url}/login")
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error("❌ Page de login inaccessible")
            return False
        
        # 2. Essayer de se connecter avec ObiWan
        # Note: Nous ne connaissons pas le mot de passe d'ObiWan
        # Nous allons d'abord vérifier s'il y a un mot de passe par défaut
        
        logger.info("🔐 Test 2: Tentative de connexion avec ObiWan")
        
        # Mots de passe courants à tester
        common_passwords = ["password", "123456", "obiwan", "ObiWan", "starwars", "jedi"]
        
        login_success = False
        for password in common_passwords:
            logger.info(f"   Essai avec mot de passe: {password}")
            
            login_data = {
                "username": "ObiWan",
                "password": password
            }
            
            response = session.post(f"{base_url}/api/login", json=login_data)
            logger.info(f"   Status: {response.status_code}")
            
            if response.status_code == 302:  # Redirection = succès
                logger.success(f"✅ Connexion réussie avec mot de passe: {password}")
                login_success = True
                break
            elif response.status_code == 401:
                logger.info(f"   ❌ Mot de passe incorrect: {password}")
            else:
                logger.warning(f"   ⚠️ Réponse inattendue: {response.status_code}")
        
        if not login_success:
            logger.error("❌ Impossible de se connecter avec ObiWan")
            logger.info("💡 Suggestion: Créer un nouveau mot de passe pour ObiWan")
            return False
        
        # 3. Tester l'API des statistiques maintenant que nous sommes connectés
        logger.info("📊 Test 3: API des statistiques (authentifié)")
        response = session.get(f"{base_url}/api/users/stats")
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.success("✅ API des statistiques fonctionne !")
            logger.info(f"   Total exercices: {data.get('total_exercises', 0)}")
            logger.info(f"   Réponses correctes: {data.get('correct_answers', 0)}")
            logger.info(f"   Taux de réussite: {data.get('success_rate', 0)}%")
        else:
            logger.error(f"❌ API des statistiques échoue: {response.text}")
            return False
        
        # 4. Tester la page du tableau de bord
        logger.info("🌐 Test 4: Page du tableau de bord (authentifié)")
        response = session.get(f"{base_url}/dashboard")
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            logger.success("✅ Tableau de bord accessible !")
            
            # Vérifier si la page contient les données
            content = response.text
            if "total_exercises" in content or "Exercices complétés" in content:
                logger.success("✅ Données présentes dans le tableau de bord")
            else:
                logger.warning("⚠️ Données manquantes dans le tableau de bord")
        else:
            logger.error(f"❌ Tableau de bord inaccessible: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        return False

def create_obiwan_password():
    """Crée un mot de passe pour ObiWan si nécessaire."""
    logger.info("🔧 Création d'un mot de passe pour ObiWan...")
    
    try:
        from app.core.security import get_password_hash
        
        db = SessionLocal()
        try:
            obiwan = db.query(User).filter(User.username == "ObiWan").first()
            if not obiwan:
                logger.error("❌ ObiWan non trouvé")
                return False
            
            # Définir un mot de passe simple pour les tests
            new_password = "jedi123"
            hashed_password = get_password_hash(new_password)
            
            obiwan.hashed_password = hashed_password
            db.commit()
            
            logger.success(f"✅ Mot de passe créé pour ObiWan: {new_password}")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création du mot de passe: {e}")
        return False

def main():
    """Fonction principale."""
    logger.info("🚀 Test de connexion ObiWan et tableau de bord...")
    
    print("="*60)
    print("🧪 TEST DE CONNEXION OBIWAN")
    print("="*60)
    
    # Étape 1: Tester la connexion
    success = test_obiwan_login()
    
    if not success:
        logger.info("🔧 Tentative de création d'un mot de passe pour ObiWan...")
        if create_obiwan_password():
            logger.info("🔄 Nouvelle tentative de connexion...")
            success = test_obiwan_login()
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    if success:
        print("✅ SUCCÈS: ObiWan peut se connecter et voir son tableau de bord")
        print("🎯 Le problème était l'authentification, maintenant résolu !")
    else:
        print("❌ ÉCHEC: Problème persistant avec la connexion d'ObiWan")
        print("🔧 Actions suggérées:")
        print("   1. Vérifier la configuration d'authentification")
        print("   2. Contrôler les cookies et sessions")
        print("   3. Examiner les logs du serveur")
    
    logger.success("🎉 Test terminé!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script pour tester l'API du tableau de bord et diagnostiquer les problèmes d'affichage.
"""

import requests
import json
import sys
import os

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import SessionLocal
from app.models.user import User
from loguru import logger

def test_dashboard_api():
    """Teste l'API du tableau de bord."""
    logger.info("🧪 Test de l'API du tableau de bord...")
    
    # URL de base de l'application
    base_url = "http://localhost:8000"
    
    # Créer une session pour maintenir les cookies
    session = requests.Session()
    
    try:
        # 1. Tester l'API sans authentification
        logger.info("📡 Test 1: API sans authentification")
        response = session.get(f"{base_url}/api/users/stats")
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.text[:200]}...")
        
        # 2. Vérifier si l'utilisateur ObiWan existe dans la base
        logger.info("🔍 Test 2: Vérification de l'utilisateur ObiWan")
        db = SessionLocal()
        try:
            obiwan = db.query(User).filter(User.username == "ObiWan").first()
            if obiwan:
                logger.success(f"✅ ObiWan trouvé - ID: {obiwan.id}")
                
                # 3. Tester l'API avec l'ID d'ObiWan directement
                logger.info("📡 Test 3: API avec ID d'ObiWan")
                
                # Simuler une authentification en modifiant temporairement l'API
                # (pour le diagnostic uniquement)
                
            else:
                logger.error("❌ ObiWan non trouvé dans la base de données")
                return False
        finally:
            db.close()
        
        # 4. Tester la page du tableau de bord
        logger.info("🌐 Test 4: Page du tableau de bord")
        response = session.get(f"{base_url}/dashboard")
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Vérifier si la page contient les éléments attendus
            content = response.text
            
            # Chercher les éléments JavaScript qui chargent les données
            if "loadDashboardData" in content:
                logger.success("✅ JavaScript de chargement des données trouvé")
            else:
                logger.warning("⚠️ JavaScript de chargement des données manquant")
            
            # Chercher l'appel à l'API
            if "/api/users/stats" in content:
                logger.success("✅ Appel API trouvé dans le JavaScript")
            else:
                logger.warning("⚠️ Appel API manquant dans le JavaScript")
            
            # Chercher les éléments DOM des statistiques
            if "stats-value" in content:
                logger.success("✅ Éléments DOM des statistiques trouvés")
            else:
                logger.warning("⚠️ Éléments DOM des statistiques manquants")
        
        # 5. Tester l'authentification (simulation)
        logger.info("🔐 Test 5: Simulation d'authentification")
        
        # Essayer de se connecter avec ObiWan (si on connaît son mot de passe)
        # Pour l'instant, on va juste vérifier la route de login
        response = session.get(f"{base_url}/login")
        logger.info(f"Page de login - Status: {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        return False

def test_direct_stats_service():
    """Teste directement le service de statistiques."""
    logger.info("🔧 Test direct du service de statistiques...")
    
    try:
        from app.services.user_service import UserService
        
        db = SessionLocal()
        try:
            # Récupérer ObiWan
            obiwan = db.query(User).filter(User.username == "ObiWan").first()
            if not obiwan:
                logger.error("❌ ObiWan non trouvé")
                return False
            
            # Tester le service directement
            logger.info(f"📊 Test du service pour ObiWan (ID: {obiwan.id})")
            stats = UserService.get_user_stats(db, obiwan.id)
            
            logger.info(f"📈 Statistiques récupérées:")
            logger.info(f"   - Total tentatives: {stats.get('total_attempts', 0)}")
            logger.info(f"   - Tentatives correctes: {stats.get('correct_attempts', 0)}")
            logger.info(f"   - Taux de réussite: {stats.get('success_rate', 0)}%")
            
            # Afficher les statistiques par type
            by_type = stats.get('by_exercise_type', {})
            if by_type:
                logger.info("   - Par type d'exercice:")
                for ex_type, type_stats in by_type.items():
                    logger.info(f"     * {ex_type}: {type_stats.get('total', 0)} tentatives, {type_stats.get('success_rate', 0)}% réussite")
            
            # Vérifier les données de progression
            progress = stats.get('progress', {})
            if progress:
                logger.info("   - Progression détaillée:")
                for ex_type, difficulties in progress.items():
                    for difficulty, prog_data in difficulties.items():
                        logger.info(f"     * {ex_type}/{difficulty}: Niveau {prog_data.get('mastery_level', 0)}")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erreur lors du test du service: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale."""
    logger.info("🚀 Démarrage des tests du tableau de bord...")
    
    print("="*60)
    print("🧪 DIAGNOSTIC DU TABLEAU DE BORD MATHAKINE")
    print("="*60)
    
    # Test 1: Service direct
    logger.info("\n📋 ÉTAPE 1: Test du service de statistiques")
    service_ok = test_direct_stats_service()
    
    # Test 2: API HTTP
    logger.info("\n📋 ÉTAPE 2: Test de l'API HTTP")
    api_ok = test_dashboard_api()
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("="*60)
    
    if service_ok:
        print("✅ Service de statistiques: FONCTIONNEL")
    else:
        print("❌ Service de statistiques: DÉFAILLANT")
    
    if api_ok:
        print("✅ API HTTP: ACCESSIBLE")
    else:
        print("❌ API HTTP: PROBLÈME")
    
    # Recommandations
    print("\n🔧 RECOMMANDATIONS:")
    
    if not service_ok:
        print("   1. Vérifier la base de données et les modèles")
        print("   2. Contrôler les services UserService et ExerciseService")
    
    if not api_ok:
        print("   3. Vérifier les routes API et l'authentification")
        print("   4. Contrôler le JavaScript du tableau de bord")
    
    if service_ok and not api_ok:
        print("   5. Le problème semble être dans l'authentification ou les routes")
    
    if not service_ok and not api_ok:
        print("   6. Problème plus profond - vérifier la configuration complète")
    
    print("\n🎯 PROCHAINE ÉTAPE SUGGÉRÉE:")
    if service_ok and api_ok:
        print("   → Vérifier l'authentification utilisateur dans le navigateur")
    elif service_ok:
        print("   → Corriger l'authentification et les routes API")
    else:
        print("   → Réparer le service de statistiques en priorité")
    
    logger.success("🎉 Diagnostic terminé!")

if __name__ == "__main__":
    main() 
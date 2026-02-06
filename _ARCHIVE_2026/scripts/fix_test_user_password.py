#!/usr/bin/env python3
"""
Script pour corriger le mot de passe de l'utilisateur test en production
"""

import bcrypt
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

def fix_test_user_password():
    """Corrige le mot de passe de l'utilisateur test"""
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Configuration base de données
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ Erreur: Variable DATABASE_URL non trouvée dans .env")
        return False
    
    # Masquer les informations sensibles pour l'affichage
    display_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'locale'
    print(f"Connexion à la base: {display_url}")
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    
    # Générer nouveau hash pour 'test_password'
    password = 'test_password'
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    hashed_str = hashed.decode('utf-8')
    
    print(f"Nouveau hash généré: {hashed_str[:20]}...")
    
    try:
        with Session() as session:
            # Trouver l'utilisateur de test
            query = "SELECT id, username FROM users WHERE username = 'test_user'"
            result = session.execute(text(query)).fetchone()
            
            if not result:
                print("❌ Utilisateur test_user non trouvé")
                return False
                
            user_id = result[0]
            print(f"✅ Utilisateur test_user trouvé (ID: {user_id})")
            
            # Mettre à jour le mot de passe
            update_query = text("UPDATE users SET hashed_password = :password WHERE id = :user_id")
            session.execute(update_query, {"password": hashed_str, "user_id": user_id})
            session.commit()
            
            print(f"✅ Mot de passe mis à jour pour test_user (ID: {user_id})")
            
            # Vérifier la mise à jour
            verify_query = text("SELECT hashed_password FROM users WHERE id = :user_id")
            updated = session.execute(verify_query, {"user_id": user_id}).fetchone()
            
            if updated and updated[0] == hashed_str:
                print("✅ Vérification réussie - Mot de passe correctement mis à jour")
                return True
            else:
                print("❌ Échec de la vérification")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔄 Réinitialisation du mot de passe pour l'utilisateur test_user...")
    success = fix_test_user_password()
    if success:
        print("✅ OPÉRATION RÉUSSIE - Mot de passe 'test_password' réinitialisé")
    else:
        print("❌ ÉCHEC - Impossible de réinitialiser le mot de passe") 
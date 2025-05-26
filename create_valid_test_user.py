#!/usr/bin/env python3
"""
Script pour créer un utilisateur de test valide
"""
import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.core.security import get_password_hash
from app.models.user import User, UserRole

def create_test_user():
    """Créer un utilisateur de test valide"""
    print("🔧 Création d'un utilisateur de test valide...")
    
    # Obtenir une session de base de données
    db = EnhancedServerAdapter.get_db_session()
    
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(User).filter(User.username == "test_user").first()
        
        if existing_user:
            print("   ℹ️  L'utilisateur test_user existe déjà")
            print(f"   📧 Email: {existing_user.email}")
            print(f"   👤 Rôle: {existing_user.role}")
            
            # Mettre à jour le mot de passe avec un hash valide
            new_password = "test_password"
            hashed_password = get_password_hash(new_password)
            existing_user.hashed_password = hashed_password
            
            db.commit()
            print(f"   ✅ Mot de passe mis à jour pour test_user")
            print(f"   🔑 Nouveau mot de passe: {new_password}")
            
        else:
            # Créer un nouvel utilisateur
            password = "test_password"
            hashed_password = get_password_hash(password)
            
            new_user = User(
                username="test_user",
                email="test@mathakine.com",
                hashed_password=hashed_password,
                full_name="Utilisateur Test",
                role=UserRole.STUDENT,
                is_active=True,
                grade_level="CM1"
            )
            
            db.add(new_user)
            db.commit()
            
            print("   ✅ Utilisateur test_user créé avec succès")
            print(f"   📧 Email: test@mathakine.com")
            print(f"   🔑 Mot de passe: {password}")
            print(f"   👤 Rôle: {UserRole.STUDENT}")
        
        # Vérifier que l'utilisateur peut être récupéré
        user = db.query(User).filter(User.username == "test_user").first()
        if user:
            print(f"   ✅ Vérification: utilisateur trouvé avec ID {user.id}")
        else:
            print("   ❌ Erreur: utilisateur non trouvé après création")
            
    except Exception as e:
        print(f"   ❌ Erreur lors de la création: {e}")
        db.rollback()
        raise
    finally:
        EnhancedServerAdapter.close_db_session(db)

if __name__ == "__main__":
    create_test_user() 
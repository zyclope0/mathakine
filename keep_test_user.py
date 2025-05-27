#!/usr/bin/env python3
"""
Script pour préserver le mot de passe de l'utilisateur test en production
malgré les procédures CI/CD qui réinitialisent la base de données
"""

import os
import bcrypt
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

def get_test_user_password_hash():
    """Récupère le hash actuel du mot de passe de l'utilisateur test"""
    # Charger les variables d'environnement
    load_dotenv()
    
    # Configuration base de données
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ Erreur: Variable DATABASE_URL non trouvée dans .env")
        return None
    
    # Masquer les informations sensibles pour l'affichage
    display_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'locale'
    print(f"Connexion à la base: {display_url}")
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Récupérer l'utilisateur test
            query = "SELECT id, username, hashed_password FROM users WHERE username = 'test_user'"
            result = session.execute(text(query)).fetchone()
            
            if not result:
                print("❌ Utilisateur test_user non trouvé")
                return None
                
            user_id = result[0]
            password_hash = result[2]
            
            print(f"✅ Hash mot de passe récupéré pour test_user (ID: {user_id})")
            return {
                'user_id': user_id,
                'password_hash': password_hash
            }
    except Exception as e:
        print(f"❌ Erreur lors de la récupération: {str(e)}")
        return None

def restore_test_user_password(user_info):
    """Restaure le mot de passe de l'utilisateur test avec le hash sauvegardé"""
    if not user_info or 'user_id' not in user_info or 'password_hash' not in user_info:
        print("❌ Informations utilisateur invalides")
        return False
    
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
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Vérifier si l'utilisateur existe toujours
            check_query = text("SELECT id FROM users WHERE username = 'test_user'")
            user = session.execute(check_query).fetchone()
            
            if not user:
                print("❌ Utilisateur test_user n'existe plus, impossible de restaurer")
                return False
            
            # Si l'ID est différent, utiliser celui trouvé
            user_id = user[0]
            if user_id != user_info['user_id']:
                print(f"⚠️ ID utilisateur différent: {user_id} (nouveau) vs {user_info['user_id']} (ancien)")
                print("⚠️ Utilisation du nouvel ID pour la restauration")
            
            # Mettre à jour le mot de passe
            update_query = text("UPDATE users SET hashed_password = :password WHERE id = :user_id")
            session.execute(update_query, {"password": user_info['password_hash'], "user_id": user_id})
            session.commit()
            
            print(f"✅ Mot de passe restauré pour test_user (ID: {user_id})")
            
            # Vérifier la mise à jour
            verify_query = text("SELECT hashed_password FROM users WHERE id = :user_id")
            updated = session.execute(verify_query, {"user_id": user_id}).fetchone()
            
            if updated and updated[0] == user_info['password_hash']:
                print("✅ Vérification réussie - Mot de passe correctement restauré")
                return True
            else:
                print("❌ Échec de la vérification")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors de la restauration: {str(e)}")
        return False

def save_password_hash_to_file(user_info, filename=".test_user_hash"):
    """Sauvegarde le hash du mot de passe dans un fichier"""
    if not user_info or 'password_hash' not in user_info:
        print("❌ Aucune information à sauvegarder")
        return False
    
    try:
        with open(filename, 'w') as f:
            f.write(f"{user_info['user_id']}:{user_info['password_hash']}")
        print(f"✅ Hash mot de passe sauvegardé dans {filename}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde dans le fichier: {str(e)}")
        return False

def load_password_hash_from_file(filename=".test_user_hash"):
    """Charge le hash du mot de passe depuis un fichier"""
    try:
        if not os.path.exists(filename):
            print(f"❌ Fichier {filename} non trouvé")
            return None
        
        with open(filename, 'r') as f:
            content = f.read().strip()
            
        if ':' not in content:
            print("❌ Format de fichier invalide")
            return None
            
        user_id, password_hash = content.split(':', 1)
        print(f"✅ Hash mot de passe chargé depuis {filename}")
        return {
            'user_id': int(user_id),
            'password_hash': password_hash
        }
    except Exception as e:
        print(f"❌ Erreur lors du chargement depuis le fichier: {str(e)}")
        return None

def reset_test_user_password():
    """Réinitialise le mot de passe de l'utilisateur test à test_password"""
    # Charger les variables d'environnement
    load_dotenv()
    
    # Configuration base de données
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ Erreur: Variable DATABASE_URL non trouvée dans .env")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Trouver l'utilisateur test
            query = text("SELECT id FROM users WHERE username = 'test_user'")
            result = session.execute(query).fetchone()
            
            if not result:
                print("❌ Utilisateur test_user non trouvé")
                return False
                
            user_id = result[0]
            
            # Générer hash pour 'test_password'
            password = 'test_password'
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            hashed_str = hashed.decode('utf-8')
            
            # Mettre à jour le mot de passe
            update_query = text("UPDATE users SET hashed_password = :password WHERE id = :user_id")
            session.execute(update_query, {"password": hashed_str, "user_id": user_id})
            session.commit()
            
            print(f"✅ Mot de passe 'test_password' défini pour test_user (ID: {user_id})")
            return True
                
    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Gestion du mot de passe de l'utilisateur test")
    parser.add_argument('action', choices=['save', 'restore', 'reset'], 
                        help="Action à effectuer: save (sauvegarder le hash actuel), restore (restaurer un hash sauvegardé), reset (réinitialiser à 'test_password')")
    parser.add_argument('--file', default=".test_user_hash", help="Fichier pour sauvegarder/charger le hash (défaut: .test_user_hash)")
    
    args = parser.parse_args()
    
    if args.action == 'save':
        user_info = get_test_user_password_hash()
        if user_info:
            save_password_hash_to_file(user_info, args.file)
    
    elif args.action == 'restore':
        user_info = load_password_hash_from_file(args.file)
        if user_info:
            restore_test_user_password(user_info)
    
    elif args.action == 'reset':
        reset_test_user_password()

if __name__ == "__main__":
    main() 
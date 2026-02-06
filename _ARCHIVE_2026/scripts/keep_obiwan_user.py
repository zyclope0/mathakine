#!/usr/bin/env python3
"""
Script pour préserver l'utilisateur permanent ObiWan en production
Remplace l'ancien système test_user par une approche plus robuste et académique.

Fonctionnalités :
1. Sauvegarde et restauration du hash de mot de passe ObiWan
2. Intégration avec les processus CI/CD
3. Gestion des migrations et réinitialisations de base de données
4. Validation de l'intégrité de l'utilisateur permanent
5. Logs détaillés et gestion d'erreurs robuste
"""

import os
import bcrypt
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path

# Configuration de l'utilisateur ObiWan (doit correspondre à create_obiwan_user.py)
OBIWAN_CONFIG = {
    'username': 'ObiWan',
    'email': 'obiwan.kenobi@jedi-temple.sw',
    'password': 'HelloThere123!',
    'full_name': 'Obi-Wan Kenobi',
    'role': 'maitre',
    'grade_level': 12
}

def get_obiwan_password_hash():
    """Récupère le hash actuel du mot de passe de l'utilisateur ObiWan"""
    # Charger les variables d'environnement
    load_dotenv()
    
    # Configuration base de données
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ Erreur: Variable DATABASE_URL non trouvée dans .env")
        return None
    
    # Masquer les informations sensibles pour l'affichage
    display_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'locale'
    print(f"🔗 Connexion à la base: {display_url}")
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Récupérer l'utilisateur ObiWan
            query = "SELECT id, username, hashed_password, role FROM users WHERE username = 'ObiWan'"
            result = session.execute(text(query)).fetchone()
            
            if not result:
                print("❌ Utilisateur ObiWan non trouvé")
                return None
                
            user_id = result[0]
            username = result[1]
            password_hash = result[2]
            role = result[3]
            
            print(f"✅ Hash mot de passe récupéré pour {username} (ID: {user_id}, Rôle: {role})")
            return {
                'user_id': user_id,
                'username': username,
                'password_hash': password_hash,
                'role': role
            }
    except Exception as e:
        print(f"❌ Erreur lors de la récupération: {str(e)}")
        return None

def restore_obiwan_password(user_info):
    """Restaure le mot de passe de l'utilisateur ObiWan avec le hash sauvegardé"""
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
    print(f"🔗 Connexion à la base: {display_url}")
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Vérifier si l'utilisateur existe toujours
            check_query = text("SELECT id FROM users WHERE username = 'ObiWan'")
            user = session.execute(check_query).fetchone()
            
            if not user:
                print("❌ Utilisateur ObiWan n'existe plus, impossible de restaurer")
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
            
            print(f"✅ Mot de passe restauré pour ObiWan (ID: {user_id})")
            
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

def save_password_hash_to_file(user_info, filename=".obiwan_user_hash"):
    """Sauvegarde le hash du mot de passe dans un fichier"""
    if not user_info or 'password_hash' not in user_info:
        print("❌ Aucune information à sauvegarder")
        return False
    
    try:
        with open(filename, 'w') as f:
            f.write(f"{user_info['user_id']}:{user_info['username']}:{user_info['password_hash']}:{user_info['role']}")
        print(f"✅ Hash mot de passe ObiWan sauvegardé dans {filename}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde dans le fichier: {str(e)}")
        return False

def load_password_hash_from_file(filename=".obiwan_user_hash"):
    """Charge le hash du mot de passe depuis un fichier"""
    try:
        if not os.path.exists(filename):
            print(f"❌ Fichier {filename} non trouvé")
            return None
        
        with open(filename, 'r') as f:
            content = f.read().strip()
            
        if content.count(':') < 2:
            print("❌ Format de fichier invalide")
            return None
            
        parts = content.split(':', 3)
        user_id, username, password_hash = parts[0], parts[1], parts[2]
        role = parts[3] if len(parts) > 3 else 'maitre'
        
        print(f"✅ Hash mot de passe ObiWan chargé depuis {filename}")
        return {
            'user_id': int(user_id),
            'username': username,
            'password_hash': password_hash,
            'role': role
        }
    except Exception as e:
        print(f"❌ Erreur lors du chargement depuis le fichier: {str(e)}")
        return None

def reset_obiwan_password():
    """Réinitialise le mot de passe de l'utilisateur ObiWan au mot de passe par défaut"""
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
            # Trouver l'utilisateur ObiWan
            query = text("SELECT id FROM users WHERE username = 'ObiWan'")
            result = session.execute(query).fetchone()
            
            if not result:
                print("❌ Utilisateur ObiWan non trouvé")
                return False
                
            user_id = result[0]
            
            # Générer hash pour le mot de passe par défaut
            password = OBIWAN_CONFIG['password']
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            hashed_str = hashed.decode('utf-8')
            
            # Mettre à jour le mot de passe
            update_query = text("UPDATE users SET hashed_password = :password WHERE id = :user_id")
            session.execute(update_query, {"password": hashed_str, "user_id": user_id})
            session.commit()
            
            print(f"✅ Mot de passe '{password}' défini pour ObiWan (ID: {user_id})")
            return True
                
    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation: {str(e)}")
        return False

def ensure_obiwan_exists():
    """S'assure que l'utilisateur ObiWan existe avec les bonnes propriétés"""
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
            # Vérifier si ObiWan existe
            query = text("SELECT id, username, email, role FROM users WHERE username = 'ObiWan'")
            result = session.execute(query).fetchone()
            
            if result:
                print(f"✅ Utilisateur ObiWan existe (ID: {result[0]}, Rôle: {result[3]})")
                return True
            else:
                print("⚠️ Utilisateur ObiWan n'existe pas - Création nécessaire")
                
                # Créer l'utilisateur ObiWan
                password = OBIWAN_CONFIG['password']
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
                hashed_str = hashed.decode('utf-8')
                
                insert_query = text("""
                    INSERT INTO users (username, email, hashed_password, full_name, role, grade_level, is_active, created_at, updated_at)
                    VALUES (:username, :email, :hashed_password, :full_name, :role, :grade_level, :is_active, NOW(), NOW())
                    RETURNING id
                """)
                
                result = session.execute(insert_query, {
                    'username': OBIWAN_CONFIG['username'],
                    'email': OBIWAN_CONFIG['email'],
                    'hashed_password': hashed_str,
                    'full_name': OBIWAN_CONFIG['full_name'],
                    'role': OBIWAN_CONFIG['role'],
                    'grade_level': OBIWAN_CONFIG['grade_level'],
                    'is_active': True
                })
                
                user_id = result.fetchone()[0]
                session.commit()
                
                print(f"✅ Utilisateur ObiWan créé avec succès (ID: {user_id})")
                return True
                
    except Exception as e:
        print(f"❌ Erreur lors de la vérification/création: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Gestion du mot de passe de l'utilisateur permanent ObiWan")
    parser.add_argument('action', choices=['save', 'restore', 'reset', 'ensure'], 
                        help="""Action à effectuer:
                        save - Sauvegarder le hash actuel
                        restore - Restaurer un hash sauvegardé
                        reset - Réinitialiser au mot de passe par défaut
                        ensure - S'assurer que ObiWan existe""")
    parser.add_argument('--file', '-f', default='.obiwan_user_hash',
                        help='Fichier pour sauvegarder/charger le hash (défaut: .obiwan_user_hash)')
    
    args = parser.parse_args()
    
    print(f"🚀 Gestion de l'utilisateur permanent ObiWan - Action: {args.action}")
    print("=" * 60)
    
    if args.action == 'save':
        user_info = get_obiwan_password_hash()
        if user_info:
            if save_password_hash_to_file(user_info, args.file):
                print(f"\n🎉 Hash sauvegardé avec succès dans {args.file}")
            else:
                print(f"\n❌ Échec de la sauvegarde")
                exit(1)
        else:
            print(f"\n❌ Impossible de récupérer les informations ObiWan")
            exit(1)
    
    elif args.action == 'restore':
        user_info = load_password_hash_from_file(args.file)
        if user_info:
            if restore_obiwan_password(user_info):
                print(f"\n🎉 Mot de passe restauré avec succès")
            else:
                print(f"\n❌ Échec de la restauration")
                exit(1)
        else:
            print(f"\n❌ Impossible de charger les informations depuis {args.file}")
            exit(1)
    
    elif args.action == 'reset':
        if reset_obiwan_password():
            print(f"\n🎉 Mot de passe réinitialisé avec succès")
            print(f"🔑 Nouveau mot de passe: {OBIWAN_CONFIG['password']}")
        else:
            print(f"\n❌ Échec de la réinitialisation")
            exit(1)
    
    elif args.action == 'ensure':
        if ensure_obiwan_exists():
            print(f"\n🎉 Utilisateur ObiWan vérifié/créé avec succès")
            print(f"🔑 Mot de passe: {OBIWAN_CONFIG['password']}")
        else:
            print(f"\n❌ Échec de la vérification/création")
            exit(1)
    
    print("=" * 60)
    print("✅ Opération terminée avec succès")

if __name__ == "__main__":
    main() 
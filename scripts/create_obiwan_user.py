#!/usr/bin/env python3
"""
Script de création de l'utilisateur permanent ObiWan
Approche académique pour remplacer l'ancien utilisateur test_user par un utilisateur permanent et distinct.

Fonctionnalités :
1. Création sécurisée de l'utilisateur ObiWan avec mot de passe défini
2. Vérification de l'unicité et gestion des conflits
3. Configuration pour les tests et l'interface de connexion
4. Intégration avec le système de nettoyage automatique (préservation)
5. Logs détaillés et gestion d'erreurs robuste
"""

import sys
import os
import bcrypt
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.models.user import User, UserRole
from app.utils.db_helpers import get_enum_value, adapt_enum_for_db
from app.db.base import get_db
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class ObiWanUserManager:
    """
    Gestionnaire pour la création et maintenance de l'utilisateur permanent ObiWan.
    Implémente une approche académique avec validation complète.
    """
    
    # Configuration de l'utilisateur ObiWan
    OBIWAN_CONFIG = {
        'username': 'ObiWan',
        'email': 'obiwan.kenobi@jedi-temple.sw',
        'password': 'HelloThere123!',  # Mot de passe distinct et mémorable
        'full_name': 'Obi-Wan Kenobi',
        'role': UserRole.MAITRE,
        'grade_level': 12,
        'is_permanent': True  # Marqueur pour le système de nettoyage
    }
    
    def __init__(self):
        """Initialise le gestionnaire avec la configuration de base de données."""
        load_dotenv()
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("❌ Variable DATABASE_URL non trouvée dans .env")
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Masquer les informations sensibles pour l'affichage
        display_url = self.database_url.split('@')[1] if '@' in self.database_url else 'locale'
        logger.info(f"🔗 Connexion à la base : {display_url}")
    
    def generate_password_hash(self, password: str) -> str:
        """
        Génère un hash bcrypt sécurisé pour le mot de passe.
        
        Args:
            password: Mot de passe en clair
            
        Returns:
            Hash bcrypt du mot de passe
        """
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds pour un bon équilibre sécurité/performance
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Vérifie qu'un mot de passe correspond au hash.
        
        Args:
            password: Mot de passe en clair
            hashed: Hash bcrypt
            
        Returns:
            True si le mot de passe correspond
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def check_existing_user(self) -> dict:
        """
        Vérifie si l'utilisateur ObiWan existe déjà.
        
        Returns:
            Dict avec les informations de l'utilisateur existant ou None
        """
        with self.SessionLocal() as session:
            try:
                query = text("SELECT id, username, email, hashed_password, role FROM users WHERE username = :username")
                result = session.execute(query, {"username": self.OBIWAN_CONFIG['username']}).fetchone()
                
                if result:
                    return {
                        'id': result[0],
                        'username': result[1],
                        'email': result[2],
                        'hashed_password': result[3],
                        'role': result[4],
                        'exists': True
                    }
                return {'exists': False}
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la vérification : {str(e)}")
                return {'exists': False, 'error': str(e)}
    
    def create_obiwan_user(self, force_recreate: bool = False) -> dict:
        """
        Crée l'utilisateur ObiWan avec toutes les validations nécessaires.
        
        Args:
            force_recreate: Si True, supprime et recrée l'utilisateur s'il existe
            
        Returns:
            Dict avec le résultat de l'opération
        """
        logger.info("🚀 Début de la création de l'utilisateur ObiWan...")
        
        # Vérifier si l'utilisateur existe déjà
        existing = self.check_existing_user()
        
        if existing.get('exists', False) and not force_recreate:
            logger.info(f"✅ L'utilisateur ObiWan existe déjà (ID: {existing['id']})")
            
            # Vérifier si le mot de passe est correct
            if self.verify_password(self.OBIWAN_CONFIG['password'], existing['hashed_password']):
                logger.info("✅ Mot de passe vérifié - Utilisateur prêt à l'emploi")
                return {
                    'success': True,
                    'action': 'verified',
                    'user_id': existing['id'],
                    'message': 'Utilisateur ObiWan vérifié et opérationnel'
                }
            else:
                logger.warning("⚠️ Mot de passe incorrect - Mise à jour nécessaire")
                return self._update_password(existing['id'])
        
        elif existing.get('exists', False) and force_recreate:
            logger.info("🔄 Suppression de l'utilisateur existant pour recréation...")
            self._delete_existing_user(existing['id'])
        
        # Créer le nouvel utilisateur
        return self._create_new_user()
    
    def _update_password(self, user_id: int) -> dict:
        """Met à jour le mot de passe de l'utilisateur existant."""
        with self.SessionLocal() as session:
            try:
                new_hash = self.generate_password_hash(self.OBIWAN_CONFIG['password'])
                
                update_query = text("""
                    UPDATE users 
                    SET hashed_password = :password, updated_at = :updated_at 
                    WHERE id = :user_id
                """)
                
                session.execute(update_query, {
                    "password": new_hash,
                    "updated_at": datetime.now(timezone.utc),
                    "user_id": user_id
                })
                session.commit()
                
                logger.info(f"✅ Mot de passe mis à jour pour ObiWan (ID: {user_id})")
                return {
                    'success': True,
                    'action': 'password_updated',
                    'user_id': user_id,
                    'message': 'Mot de passe ObiWan mis à jour avec succès'
                }
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Erreur lors de la mise à jour du mot de passe : {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'message': 'Échec de la mise à jour du mot de passe'
                }
    
    def _delete_existing_user(self, user_id: int):
        """Supprime l'utilisateur existant et ses données associées."""
        with self.SessionLocal() as session:
            try:
                # Supprimer en respectant les contraintes FK
                delete_queries = [
                    "DELETE FROM logic_challenge_attempts WHERE user_id = :user_id",
                    "DELETE FROM attempts WHERE user_id = :user_id",
                    "DELETE FROM recommendations WHERE user_id = :user_id",
                    "DELETE FROM progress WHERE user_id = :user_id",
                    "DELETE FROM exercises WHERE creator_id = :user_id",
                    "DELETE FROM logic_challenges WHERE creator_id = :user_id",
                    "DELETE FROM users WHERE id = :user_id"
                ]
                
                for query in delete_queries:
                    result = session.execute(text(query), {"user_id": user_id})
                    if result.rowcount > 0:
                        logger.info(f"  🗑️ Supprimé {result.rowcount} éléments : {query.split()[2]}")
                
                session.commit()
                logger.info(f"✅ Utilisateur existant supprimé (ID: {user_id})")
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Erreur lors de la suppression : {str(e)}")
                raise
    
    def _create_new_user(self) -> dict:
        """Crée un nouvel utilisateur ObiWan."""
        with self.SessionLocal() as session:
            try:
                # Générer le hash du mot de passe
                password_hash = self.generate_password_hash(self.OBIWAN_CONFIG['password'])
                
                # Adapter le rôle pour PostgreSQL
                adapted_role = adapt_enum_for_db("UserRole", self.OBIWAN_CONFIG['role'].value, session)
                
                # Préparer les données utilisateur
                user_data = {
                    'username': self.OBIWAN_CONFIG['username'],
                    'email': self.OBIWAN_CONFIG['email'],
                    'hashed_password': password_hash,
                    'full_name': self.OBIWAN_CONFIG['full_name'],
                    'role': adapted_role,  # Utiliser la valeur adaptée
                    'grade_level': self.OBIWAN_CONFIG['grade_level'],
                    'is_active': True,
                    'created_at': datetime.now(timezone.utc),
                    'updated_at': datetime.now(timezone.utc)
                }
                
                # Insérer l'utilisateur
                insert_query = text("""
                    INSERT INTO users (username, email, hashed_password, full_name, role, grade_level, is_active, created_at, updated_at)
                    VALUES (:username, :email, :hashed_password, :full_name, :role, :grade_level, :is_active, :created_at, :updated_at)
                    RETURNING id
                """)
                
                result = session.execute(insert_query, user_data)
                user_id = result.fetchone()[0]
                session.commit()
                
                logger.info(f"🎉 Utilisateur ObiWan créé avec succès (ID: {user_id})")
                logger.info(f"📧 Email : {self.OBIWAN_CONFIG['email']}")
                logger.info(f"🔑 Mot de passe : {self.OBIWAN_CONFIG['password']}")
                logger.info(f"👑 Rôle : {self.OBIWAN_CONFIG['role'].value}")
                
                # Vérifier la création
                verification = self.verify_user_creation(user_id)
                
                return {
                    'success': True,
                    'action': 'created',
                    'user_id': user_id,
                    'verification': verification,
                    'credentials': {
                        'username': self.OBIWAN_CONFIG['username'],
                        'password': self.OBIWAN_CONFIG['password']
                    },
                    'message': 'Utilisateur ObiWan créé et vérifié avec succès'
                }
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Erreur lors de la création : {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'message': 'Échec de la création de l\'utilisateur ObiWan'
                }
    
    def verify_user_creation(self, user_id: int) -> dict:
        """
        Vérifie que l'utilisateur a été créé correctement.
        
        Args:
            user_id: ID de l'utilisateur à vérifier
            
        Returns:
            Dict avec les résultats de la vérification
        """
        with self.SessionLocal() as session:
            try:
                query = text("""
                    SELECT username, email, role, is_active, created_at 
                    FROM users WHERE id = :user_id
                """)
                result = session.execute(query, {"user_id": user_id}).fetchone()
                
                if not result:
                    return {'success': False, 'error': 'Utilisateur non trouvé après création'}
                
                # Vérifier le mot de passe
                password_query = text("SELECT hashed_password FROM users WHERE id = :user_id")
                password_result = session.execute(password_query, {"user_id": user_id}).fetchone()
                
                password_valid = self.verify_password(
                    self.OBIWAN_CONFIG['password'], 
                    password_result[0]
                )
                
                return {
                    'success': True,
                    'username': result[0],
                    'email': result[1],
                    'role': result[2],
                    'is_active': result[3],
                    'created_at': result[4],
                    'password_valid': password_valid
                }
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la vérification : {str(e)}")
                return {'success': False, 'error': str(e)}
    
    def generate_login_info(self) -> dict:
        """
        Génère les informations de connexion pour l'interface.
        
        Returns:
            Dict avec les informations de connexion
        """
        return {
            'username': self.OBIWAN_CONFIG['username'],
            'password': self.OBIWAN_CONFIG['password'],
            'email': self.OBIWAN_CONFIG['email'],
            'display_name': self.OBIWAN_CONFIG['full_name'],
            'role': self.OBIWAN_CONFIG['role'].value,
            'login_url': '/login',
            'dashboard_url': '/dashboard'
        }


def main():
    """Fonction principale avec gestion des arguments."""
    parser = argparse.ArgumentParser(
        description="Création de l'utilisateur permanent ObiWan",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python scripts/create_obiwan_user.py                    # Création normale
  python scripts/create_obiwan_user.py --force           # Recréation forcée
  python scripts/create_obiwan_user.py --verify-only     # Vérification seulement
  python scripts/create_obiwan_user.py --show-credentials # Afficher les identifiants
        """
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force la recréation même si l\'utilisateur existe'
    )
    
    parser.add_argument(
        '--verify-only', '-v',
        action='store_true',
        help='Vérifie seulement l\'existence et la validité de l\'utilisateur'
    )
    
    parser.add_argument(
        '--show-credentials', '-c',
        action='store_true',
        help='Affiche les identifiants de connexion'
    )
    
    args = parser.parse_args()
    
    try:
        manager = ObiWanUserManager()
        
        if args.show_credentials:
            # Afficher les identifiants
            info = manager.generate_login_info()
            print("\n🔑 IDENTIFIANTS DE CONNEXION OBIWAN")
            print("=" * 40)
            print(f"👤 Nom d'utilisateur : {info['username']}")
            print(f"🔐 Mot de passe      : {info['password']}")
            print(f"📧 Email            : {info['email']}")
            print(f"👑 Rôle             : {info['role']}")
            print(f"🌐 URL de connexion : {info['login_url']}")
            print("=" * 40)
            return
        
        if args.verify_only:
            # Vérification seulement
            existing = manager.check_existing_user()
            if existing.get('exists', False):
                print(f"✅ L'utilisateur ObiWan existe (ID: {existing['id']})")
                
                # Vérifier le mot de passe
                if manager.verify_password(manager.OBIWAN_CONFIG['password'], existing['hashed_password']):
                    print("✅ Mot de passe valide")
                else:
                    print("❌ Mot de passe invalide - Mise à jour recommandée")
                    print("💡 Utilisez --force pour corriger")
            else:
                print("❌ L'utilisateur ObiWan n'existe pas")
                print("💡 Lancez sans --verify-only pour le créer")
            return
        
        # Création/mise à jour de l'utilisateur
        print("🚀 Création de l'utilisateur permanent ObiWan...")
        print(f"🔄 Mode force : {'Activé' if args.force else 'Désactivé'}")
        print()
        
        result = manager.create_obiwan_user(force_recreate=args.force)
        
        if result['success']:
            print(f"\n🎉 SUCCÈS : {result['message']}")
            print(f"🆔 Action effectuée : {result['action']}")
            print(f"🔢 ID utilisateur : {result['user_id']}")
            
            if 'credentials' in result:
                creds = result['credentials']
                print(f"\n🔑 IDENTIFIANTS DE CONNEXION :")
                print(f"   👤 Utilisateur : {creds['username']}")
                print(f"   🔐 Mot de passe : {creds['password']}")
            
            if 'verification' in result and result['verification']['success']:
                verif = result['verification']
                print(f"\n✅ VÉRIFICATION RÉUSSIE :")
                print(f"   📧 Email : {verif['email']}")
                print(f"   👑 Rôle : {verif['role']}")
                print(f"   🔑 Mot de passe : {'Valide' if verif['password_valid'] else 'Invalide'}")
                print(f"   📅 Créé le : {verif['created_at']}")
            
            print(f"\n🌐 L'utilisateur ObiWan est prêt pour :")
            print(f"   • Tests automatisés")
            print(f"   • Interface de connexion")
            print(f"   • Développement local")
            print(f"   • Démonstrations")
            
        else:
            print(f"\n❌ ÉCHEC : {result['message']}")
            if 'error' in result:
                print(f"💥 Erreur : {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erreur critique : {str(e)}")
        print(f"\n💥 Erreur critique : {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
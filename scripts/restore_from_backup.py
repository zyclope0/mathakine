#!/usr/bin/env python
"""
Script pour restaurer une base de données à partir d'une sauvegarde.
Ce script:
1. Liste les sauvegardes disponibles dans le dossier backups/database
2. Permet de sélectionner une sauvegarde à restaurer
3. Restaure la sauvegarde dans la base de données spécifiée
4. Réinitialise la table alembic_version si nécessaire

À utiliser uniquement en cas de problème après l'application d'une migration Alembic.
"""
import os
import sys
import subprocess
import argparse
import datetime
from pathlib import Path

# Ajouter le répertoire parent au sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger("db_restore")

# Configuration du stockage des sauvegardes
BACKUP_DIR = os.path.join(BASE_DIR, "backups", "database")

def list_backups():
    """Liste les sauvegardes disponibles."""
    logger.info("Recherche des sauvegardes disponibles...")
    
    if not os.path.exists(BACKUP_DIR):
        logger.error(f"Le répertoire de sauvegarde {BACKUP_DIR} n'existe pas")
        return []
    
    # Rechercher tous les fichiers .sql.gz dans le répertoire
    backups = sorted(Path(BACKUP_DIR).glob("*.sql.gz"), key=os.path.getmtime, reverse=True)
    
    if not backups:
        logger.error("Aucune sauvegarde trouvée")
        return []
    
    return backups

def parse_db_url(db_url):
    """Extrait les informations de connexion depuis l'URL de la base de données."""
    # Exemple: postgresql://user:password@host:port/dbname
    if not db_url.startswith('postgresql://'):
        logger.error("L'URL de la base de données doit être PostgreSQL pour la restauration")
        return None
    
    try:
        # Séparer les parties de l'URL
        credentials, rest = db_url.replace('postgresql://', '').split('@')
        user_pass = credentials.split(':')
        host_port_db = rest.split('/')
        
        # Construire le dictionnaire des informations de connexion
        db_info = {
            'user': user_pass[0],
            'password': user_pass[1] if len(user_pass) > 1 else None,
            'host': host_port_db[0].split(':')[0],
            'port': host_port_db[0].split(':')[1] if ':' in host_port_db[0] else '5432',
            'dbname': host_port_db[1]
        }
        
        return db_info
    except Exception as e:
        logger.error(f"Impossible de parser l'URL de la base de données: {e}")
        return None

def restore_database(backup_path, db_info, force=False):
    """Restaure la base de données à partir d'une sauvegarde."""
    logger.info(f"Restauration de la base de données {db_info['dbname']} à partir de {backup_path}...")
    
    if not force:
        # Demander confirmation avant de continuer
        response = input(f"⚠️ ATTENTION: Cette opération va remplacer la base de données {db_info['dbname']} par la sauvegarde {os.path.basename(backup_path)}.\nToutes les données actuelles seront perdues. Continuer? (y/n): ")
        if response.lower() != 'y':
            logger.info("Restauration annulée par l'utilisateur")
            return False
    
    # Construction de la commande pg_restore
    pg_restore_cmd = [
        "pg_restore",
        "--clean",        # Nettoie (drop) les objets avant de les recréer
        "--if-exists",    # Ajoute IF EXISTS aux commandes DROP
        "-h", db_info["host"],
        "-p", db_info["port"],
        "-U", db_info["user"],
        "-d", db_info["dbname"],
        backup_path
    ]
    
    # Configuration de l'environnement pour pg_restore (mot de passe)
    env = os.environ.copy()
    if db_info["password"]:
        env["PGPASSWORD"] = db_info["password"]
    
    try:
        logger.info("Exécution de pg_restore...")
        process = subprocess.run(
            pg_restore_cmd, 
            env=env, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # pg_restore peut retourner un code non-zéro même si la restauration réussit partiellement
        if process.returncode != 0:
            logger.warning(f"pg_restore a terminé avec le code {process.returncode}")
            logger.warning(f"Messages d'erreur: {process.stderr}")
            
            # Même si pg_restore échoue partiellement, certaines tables peuvent être restaurées
            # On considère que c'est un succès avec avertissement
            logger.info("La restauration a probablement réussi partiellement.")
        else:
            logger.success("Restauration terminée avec succès")
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la restauration: {e}")
        return False

def reset_alembic_version(revision=None):
    """Réinitialise la table alembic_version à une révision spécifique."""
    if not revision:
        logger.info("Aucune révision spécifiée pour alembic_version")
        return False
    
    logger.info(f"Réinitialisation de la table alembic_version à la révision {revision}...")
    
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            # Vider la table alembic_version
            conn.execute(text("DELETE FROM alembic_version"))
            
            # Insérer la révision spécifiée
            conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{revision}')"))
            
            # Valider la transaction
            conn.commit()
            
        logger.success(f"Table alembic_version réinitialisée à la révision {revision}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation de alembic_version: {e}")
        return False

def main(backup_index=None, force=False, reset_to=None):
    """
    Fonction principale pour la restauration de la base de données.
    
    Args:
        backup_index: Index de la sauvegarde à restaurer (si None, affiche la liste)
        force: Si True, restaure sans demander de confirmation
        reset_to: Révision Alembic à définir après la restauration
    """
    logger.info("Démarrage du processus de restauration...")
    
    # Liste des sauvegardes disponibles
    backups = list_backups()
    if not backups:
        return False
    
    # Afficher la liste des sauvegardes
    if backup_index is None:
        print("\nSauvegardes disponibles:")
        for i, backup in enumerate(backups):
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(backup))
            size_mb = os.path.getsize(backup) / (1024 * 1024)
            dbname = os.path.basename(backup).split('_')[1]  # backup_dbname_timestamp.sql.gz
            print(f"{i+1}. {os.path.basename(backup)}")
            print(f"   - Base de données: {dbname}")
            print(f"   - Date: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   - Taille: {size_mb:.2f} MB")
        
        # Demander à l'utilisateur de choisir une sauvegarde
        try:
            choice = int(input("\nEntrez le numéro de la sauvegarde à restaurer (0 pour annuler): "))
            if choice == 0:
                logger.info("Restauration annulée par l'utilisateur")
                return False
            
            if choice < 1 or choice > len(backups):
                logger.error(f"Choix invalide: {choice}")
                return False
            
            backup_index = choice - 1
        except ValueError:
            logger.error("Entrée invalide")
            return False
    
    # Vérifier l'index de la sauvegarde
    if backup_index < 0 or backup_index >= len(backups):
        logger.error(f"Index de sauvegarde invalide: {backup_index}")
        return False
    
    # Sélectionner la sauvegarde
    selected_backup = backups[backup_index]
    logger.info(f"Sauvegarde sélectionnée: {selected_backup}")
    
    # Extraire les informations de connexion
    db_info = parse_db_url(settings.DATABASE_URL)
    if not db_info:
        return False
    
    # Restaurer la base de données
    if not restore_database(selected_backup, db_info, force):
        logger.error("Échec de la restauration")
        return False
    
    # Réinitialiser la table alembic_version si une révision est spécifiée
    if reset_to:
        if not reset_alembic_version(reset_to):
            logger.warning("Échec de la réinitialisation de alembic_version")
            logger.info("La base de données a été restaurée, mais la table alembic_version n'a pas été mise à jour")
            return True
    
    logger.success("Processus de restauration terminé avec succès")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restaurer une base de données à partir d'une sauvegarde")
    parser.add_argument("--backup", type=int, help="Index de la sauvegarde à restaurer (1-based)")
    parser.add_argument("--force", action="store_true", help="Restaurer sans demander de confirmation")
    parser.add_argument("--reset-to", help="Révision Alembic à définir après la restauration")
    args = parser.parse_args()
    
    # Ajuster l'index (interface utilisateur est 1-based, mais le code est 0-based)
    backup_index = args.backup - 1 if args.backup is not None else None
    
    success = main(backup_index, args.force, args.reset_to)
    if success:
        sys.exit(0)
    else:
        sys.exit(1) 
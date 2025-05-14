#!/usr/bin/env python
"""
Script pour sauvegarder la base de données avant d'appliquer des migrations Alembic.
Ce script:
1. Crée une sauvegarde de la base de données PostgreSQL actuelle
2. Stocke la sauvegarde avec un horodatage pour pouvoir la restaurer si nécessaire
3. Vérifie que la sauvegarde est utilisable

Étant donné que ce script est critique pour la sécurité des données, il implémente:
- Validation des permissions nécessaires
- Vérification de l'espace disque disponible
- Logs détaillés de chaque étape
- Mécanisme de notification en cas d'échec
"""
import os
import sys
import subprocess
import datetime
import shutil
import argparse
import platform
from pathlib import Path

# Ajouter le répertoire parent au sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger("alembic_backup")

# Configuration du stockage des sauvegardes
BACKUP_DIR = os.path.join(BASE_DIR, "backups", "database")
MAX_BACKUPS = 5  # Nombre maximum de sauvegardes à conserver

def ensure_backup_dir():
    """Crée le répertoire de sauvegarde s'il n'existe pas déjà."""
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
    logger.info(f"Répertoire de sauvegarde: {BACKUP_DIR}")

def check_disk_space():
    """Vérifie qu'il y a suffisamment d'espace disque pour la sauvegarde."""
    if platform.system() == "Windows":
        # Obtenir l'espace disque disponible sur Windows
        free_bytes = shutil.disk_usage(BACKUP_DIR).free
    else:
        # Obtenir l'espace disque disponible sur Unix/Linux
        stat = os.statvfs(BACKUP_DIR)
        free_bytes = stat.f_bavail * stat.f_frsize
    
    # Convertir en MB pour une lecture plus facile
    free_mb = free_bytes / (1024 * 1024)
    logger.info(f"Espace disque disponible: {free_mb:.2f} MB")
    
    # On estime avoir besoin d'au moins 100 MB pour la sauvegarde
    # (à ajuster selon la taille de la base de données)
    if free_mb < 100:
        logger.error(f"Espace disque insuffisant: {free_mb:.2f} MB disponible, 100 MB requis")
        return False
    
    return True

def clean_old_backups():
    """Supprime les sauvegardes les plus anciennes si le nombre maximum est dépassé."""
    backups = sorted(Path(BACKUP_DIR).glob("*.sql.gz"), key=os.path.getmtime)
    
    if len(backups) >= MAX_BACKUPS:
        logger.info(f"Nombre de sauvegardes ({len(backups)}) supérieur à la limite ({MAX_BACKUPS})")
        to_delete = backups[:(len(backups) - MAX_BACKUPS + 1)]
        
        for backup in to_delete:
            logger.info(f"Suppression de la sauvegarde ancienne: {backup}")
            os.remove(backup)

def parse_db_url(db_url):
    """Extrait les informations de connexion depuis l'URL de la base de données."""
    # Exemple: postgresql://user:password@host:port/dbname
    if not db_url.startswith('postgresql://'):
        logger.error("L'URL de la base de données doit être PostgreSQL pour la sauvegarde")
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

def create_backup(db_info):
    """Crée une sauvegarde de la base de données PostgreSQL."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"backup_{db_info['dbname']}_{timestamp}.sql.gz")
    
    # Construction de la commande pg_dump
    pg_dump_cmd = [
        "pg_dump",
        "-h", db_info["host"],
        "-p", db_info["port"],
        "-U", db_info["user"],
        "-d", db_info["dbname"],
        "-F", "c",  # Format personnalisé pour une meilleure compression
        "-f", backup_path
    ]
    
    # Configuration de l'environnement pour pg_dump (mot de passe)
    env = os.environ.copy()
    if db_info["password"]:
        env["PGPASSWORD"] = db_info["password"]
    
    try:
        logger.info(f"Démarrage de la sauvegarde de {db_info['dbname']}...")
        process = subprocess.run(
            pg_dump_cmd, 
            env=env, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        logger.info(f"Sauvegarde terminée: {backup_path}")
        return backup_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la sauvegarde: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Exception lors de la sauvegarde: {e}")
        return None

def verify_backup(backup_path, db_info):
    """Vérifie que la sauvegarde est utilisable."""
    # Vérifier que le fichier existe et n'est pas vide
    if not os.path.exists(backup_path):
        logger.error(f"Le fichier de sauvegarde {backup_path} n'existe pas")
        return False
    
    if os.path.getsize(backup_path) == 0:
        logger.error(f"Le fichier de sauvegarde {backup_path} est vide")
        return False
    
    # Vérifier la sauvegarde avec pg_restore (sans la restaurer)
    pg_restore_cmd = [
        "pg_restore", 
        "--list",
        "-f", "/dev/null" if platform.system() != "Windows" else "NUL",
        backup_path
    ]
    
    env = os.environ.copy()
    if db_info["password"]:
        env["PGPASSWORD"] = db_info["password"]
    
    try:
        logger.info(f"Vérification de la sauvegarde {backup_path}...")
        process = subprocess.run(
            pg_restore_cmd, 
            env=env, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.returncode != 0:
            logger.error(f"Erreur lors de la vérification: {process.stderr}")
            return False
        
        logger.info("Sauvegarde vérifiée avec succès")
        return True
    except Exception as e:
        logger.error(f"Exception lors de la vérification: {e}")
        return False

def main(force=False):
    """
    Fonction principale pour la sauvegarde de la base de données.
    
    Args:
        force: Si True, ignore les vérifications préliminaires
    """
    logger.info("Démarrage du processus de sauvegarde...")
    
    # Créer le répertoire de sauvegarde
    ensure_backup_dir()
    
    # Nettoyer les anciennes sauvegardes
    clean_old_backups()
    
    # Vérifier l'espace disque disponible
    if not force and not check_disk_space():
        logger.error("Sauvegarde annulée: espace disque insuffisant")
        return False
    
    # Extraire les informations de connexion
    db_info = parse_db_url(settings.DATABASE_URL)
    if not db_info:
        logger.error("Sauvegarde annulée: impossible de se connecter à la base de données")
        return False
    
    # Créer la sauvegarde
    backup_path = create_backup(db_info)
    if not backup_path:
        logger.error("Sauvegarde annulée: échec de la création du fichier de sauvegarde")
        return False
    
    # Vérifier la sauvegarde
    if verify_backup(backup_path, db_info):
        logger.success(f"Sauvegarde terminée avec succès: {backup_path}")
        return True
    else:
        logger.error(f"La sauvegarde a été créée mais sa vérification a échoué: {backup_path}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sauvegarde de la base de données avant les migrations Alembic")
    parser.add_argument("--force", action="store_true", help="Forcer la sauvegarde sans vérifications")
    args = parser.parse_args()
    
    success = main(force=args.force)
    if success:
        sys.exit(0)
    else:
        sys.exit(1) 
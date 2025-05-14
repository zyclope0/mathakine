#!/usr/bin/env python
"""
Script de restauration de base de données Mathakine

Ce script permet de restaurer facilement une base de données à partir d'une sauvegarde,
soit en spécifiant le fichier manuellement, soit en choisissant parmi les sauvegardes disponibles.

Usage: python scripts/restore_from_backup.py [--list] [--file BACKUP_FILE]
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import datetime
import logging

# Configure le logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/restore.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("restore_db")

def get_db_url():
    """Récupère l'URL de la base de données depuis l'environnement."""
    # Essayer d'abord avec la variable d'environnement standard
    db_url = os.environ.get('DATABASE_URL')
    
    # Si non défini, essayer de charger depuis la configuration
    if not db_url:
        try:
            sys.path.append('.')
            from app.core.config import settings
            db_url = settings.DATABASE_URL
        except ImportError:
            logger.error("Impossible de charger la configuration. DATABASE_URL doit être défini.")
            sys.exit(1)
    
    return db_url

def list_backups():
    """Liste les sauvegardes disponibles dans le répertoire de sauvegarde."""
    backup_dir = Path("backups/database")
    if not backup_dir.exists():
        logger.error(f"Le répertoire de sauvegarde {backup_dir} n'existe pas.")
        return []
    
    # Récupérer tous les fichiers de sauvegarde
    backups = []
    for file in backup_dir.glob("backup_*"):
        if file.is_file() and (file.name.endswith('.sql.gz') or file.name.endswith('.sqlite')):
            # Extraire la date et l'heure de la création
            try:
                # Format: backup_dbname_YYYYMMDD_HHMMSS.sql.gz
                date_str = file.name.split('_')[2]
                time_str = file.name.split('_')[3].split('.')[0]
                timestamp = datetime.datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                size = file.stat().st_size
                backups.append({
                    'file': file,
                    'timestamp': timestamp,
                    'size': size
                })
            except (IndexError, ValueError):
                # Si le format ne correspond pas, utiliser la date de modification
                timestamp = datetime.datetime.fromtimestamp(file.stat().st_mtime)
                size = file.stat().st_size
                backups.append({
                    'file': file,
                    'timestamp': timestamp,
                    'size': size
                })
    
    # Trier par date décroissante (plus récent d'abord)
    backups.sort(key=lambda x: x['timestamp'], reverse=True)
    return backups

def print_backups(backups):
    """Affiche la liste des sauvegardes disponibles."""
    if not backups:
        print("Aucune sauvegarde trouvée.")
        return
    
    print(f"\n{'#':<4} {'Date':<20} {'Taille':<12} {'Fichier':<50}")
    print("-" * 90)
    
    for i, backup in enumerate(backups, 1):
        size_str = f"{backup['size'] / (1024*1024):.2f} MB" if backup['size'] > 1024*1024 else f"{backup['size'] / 1024:.2f} KB"
        print(f"{i:<4} {backup['timestamp'].strftime('%Y-%m-%d %H:%M:%S'):<20} {size_str:<12} {backup['file'].name:<50}")
    
    print("")

def restore_backup(backup_file, db_url):
    """Restaure la base de données à partir d'une sauvegarde."""
    logger.info(f"Restauration de la base de données depuis: {backup_file}")
    
    try:
        # Vérifier si c'est PostgreSQL ou SQLite
        if db_url.startswith('postgresql'):
            # Extraire les informations de connexion
            parts = db_url.replace('postgresql://', '').split('@')
            user_pass = parts[0].split(':')
            host_db = parts[1].split('/')
            
            user = user_pass[0]
            password = user_pass[1]
            host = host_db[0]
            dbname = host_db[1]
            
            # Configuration des variables d'environnement pour pg_restore
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # Commande pg_restore
            if str(backup_file).endswith('.sql.gz'):
                # Décompresser d'abord le fichier SQL
                logger.info("Décompression du fichier de sauvegarde...")
                temp_sql = "/tmp/temp_restore.sql"
                subprocess.run(
                    f"gunzip -c {backup_file} > {temp_sql}",
                    shell=True, check=True
                )
                
                # Restaurer avec psql
                logger.info("Restauration avec psql...")
                cmd = [
                    'psql',
                    '-h', host,
                    '-U', user,
                    '-d', dbname,
                    '-f', temp_sql
                ]
                subprocess.run(cmd, env=env, check=True)
                
                # Nettoyer
                os.remove(temp_sql)
            else:
                # Fichier binaire pg_dump
                cmd = [
                    'pg_restore',
                    '-h', host,
                    '-U', user,
                    '-d', dbname,
                    '-c',  # Clean (drop) objects before recreating
                    str(backup_file)
                ]
                subprocess.run(cmd, env=env, check=True)
            
        elif db_url.startswith('sqlite'):
            # Pour SQLite, remplacer le fichier
            db_path = db_url.replace('sqlite:///', '')
            
            # Stopper temporairement toute activité sur la base (si possible)
            logger.info("Arrêt temporaire des services utilisant la base de données...")
            
            # Décompresser et restaurer
            if str(backup_file).endswith('.sql.gz'):
                subprocess.run(
                    f"gunzip -c {backup_file} | sqlite3 {db_path}",
                    shell=True, check=True
                )
            elif str(backup_file).endswith('.sqlite'):
                # Faire une copie de sauvegarde du fichier existant
                if os.path.exists(db_path):
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = f"{db_path}.bak_{timestamp}"
                    subprocess.run(
                        f"cp {db_path} {backup_path}",
                        shell=True, check=True
                    )
                    logger.info(f"Base de données existante sauvegardée sous: {backup_path}")
                
                # Copie directe
                subprocess.run(
                    f"cp {backup_file} {db_path}",
                    shell=True, check=True
                )
        
        logger.info("Restauration terminée avec succès ✓")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la restauration: {e}")
        return False

def interactive_restore():
    """Mode interactif pour choisir une sauvegarde à restaurer."""
    backups = list_backups()
    
    if not backups:
        logger.error("Aucune sauvegarde trouvée.")
        return False
    
    print_backups(backups)
    
    while True:
        try:
            choice = input("Choisissez une sauvegarde à restaurer (numéro ou 'q' pour quitter): ")
            
            if choice.lower() == 'q':
                return False
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(backups):
                selected_backup = backups[choice_num - 1]['file']
                break
            else:
                print(f"Veuillez choisir un numéro entre 1 et {len(backups)}.")
        except ValueError:
            print("Veuillez entrer un numéro valide.")
    
    confirm = input(f"ATTENTION: Cela va écraser votre base de données actuelle avec {selected_backup.name}. Continuer? (oui/non) ")
    if confirm.lower() in ['oui', 'o', 'yes', 'y']:
        return restore_backup(selected_backup, get_db_url())
    else:
        print("Restauration annulée.")
        return False

def main():
    parser = argparse.ArgumentParser(description='Restauration de base de données Mathakine')
    parser.add_argument('--list', action='store_true', help='Lister les sauvegardes disponibles')
    parser.add_argument('--file', help='Fichier de sauvegarde spécifique à restaurer')
    
    args = parser.parse_args()
    
    if args.list:
        backups = list_backups()
        print_backups(backups)
        return
    
    if args.file:
        backup_file = Path(args.file)
        if not backup_file.exists():
            logger.error(f"Le fichier de sauvegarde {args.file} n'existe pas.")
            sys.exit(1)
        
        success = restore_backup(backup_file, get_db_url())
        if success:
            logger.info("Restauration terminée avec succès.")
        else:
            logger.error("Échec de la restauration.")
        sys.exit(0 if success else 1)
    
    # Mode interactif
    success = interactive_restore()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
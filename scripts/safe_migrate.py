#!/usr/bin/env python
"""
Script de migration Alembic sécurisé pour Mathakine

Ce script effectue une migration Alembic en production avec les sécurités suivantes :
1. Sauvegarde automatique de la base de données avant migration
2. Vérification post-migration de l'intégrité des tables protégées
3. Journal détaillé de l'opération
4. Restauration automatique en cas d'échec

Usage: python scripts/safe_migrate.py [--check-only] [--force] [--restore-backup file]
"""

import argparse
import datetime
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure le logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/migration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("safe_migrate")

# Tables protégées qui ne doivent jamais être supprimées
PROTECTED_TABLES = [
    'exercises',
    'results',
    'statistics',
    'user_stats',
    'schema_version'
]

def create_backup(db_url):
    """Crée une sauvegarde de la base de données avant la migration."""
    logger.info("Création d'une sauvegarde de la base de données...")
    
    # Répertoire de sauvegarde
    backup_dir = Path("backups/database")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Nom de fichier basé sur la date et l'heure
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = db_url.split('/')[-1]
    backup_file = backup_dir / f"backup_{db_name}_{timestamp}.sql.gz"
    
    try:
        # Vérifier si c'est PostgreSQL ou SQLite
        if db_url.startswith('postgresql'):
            # Extraire les informations de connexion
            # Format: postgresql://user:password@host/dbname
            parts = db_url.replace('postgresql://', '').split('@')
            user_pass = parts[0].split(':')
            host_db = parts[1].split('/')
            
            user = user_pass[0]
            password = user_pass[1]
            host = host_db[0]
            dbname = host_db[1]
            
            # Configuration des variables d'environnement pour pg_dump
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # Commande pg_dump avec compression gzip
            cmd = [
                'pg_dump',
                '-h', host,
                '-U', user,
                '-d', dbname,
                '-F', 'c',  # Format personnalisé
                '-f', str(backup_file)
            ]
            
            # Exécuter la commande
            subprocess.run(cmd, env=env, check=True, capture_output=True)
            
        elif db_url.startswith('sqlite'):
            # Pour SQLite, faire une copie simple du fichier
            db_path = db_url.replace('sqlite:///', '')
            sqlite_backup_file = str(backup_file).replace('.sql.gz', '.sqlite')
            
            # Utiliser sqlite3 pour exporter sous forme SQL, puis compresser
            subprocess.run(
                f"sqlite3 {db_path} .dump | gzip > {backup_file}",
                shell=True, check=True
            )
            
        logger.info(f"Sauvegarde créée avec succès: {backup_file}")
        return str(backup_file)
    
    except Exception as e:
        logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
        raise

def check_protected_tables(db_url):
    """Vérifie que toutes les tables protégées existent toujours après la migration."""
    logger.info("Vérification de l'intégrité des tables protégées...")
    
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
            
            # Configuration des variables d'environnement pour psql
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # Vérifier chaque table protégée
            for table in PROTECTED_TABLES:
                cmd = [
                    'psql',
                    '-h', host,
                    '-U', user,
                    '-d', dbname,
                    '-t',  # Format tableau (moins de bruit)
                    '-c', f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}');"
                ]
                
                result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
                exists = 't' in result.stdout.strip().lower()
                
                if exists:
                    logger.info(f"Table protégée '{table}' vérifiée ✓")
                else:
                    logger.error(f"Table protégée '{table}' MANQUANTE ✗")
                    return False
            
        elif db_url.startswith('sqlite'):
            # Pour SQLite
            db_path = db_url.replace('sqlite:///', '')
            
            for table in PROTECTED_TABLES:
                cmd = [
                    'sqlite3',
                    db_path,
                    f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table}';"
                ]
                
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                exists = '1' in result.stdout.strip()
                
                if exists:
                    logger.info(f"Table protégée '{table}' vérifiée ✓")
                else:
                    logger.error(f"Table protégée '{table}' MANQUANTE ✗")
                    return False
        
        logger.info("Toutes les tables protégées sont présentes ✓")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des tables protégées: {e}")
        return False

def run_migration():
    """Exécute la migration Alembic."""
    logger.info("Démarrage de la migration...")
    
    try:
        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Migration réussie: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Migration échouée: {e.stderr}")
        return False

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
            cmd = [
                'pg_restore',
                '-h', host,
                '-U', user,
                '-d', dbname,
                '-c',  # Clean (drop) objects before recreating
                str(backup_file)
            ]
            
            # Exécuter la commande
            subprocess.run(cmd, env=env, check=True)
            
        elif db_url.startswith('sqlite'):
            # Pour SQLite, remplacer le fichier
            db_path = db_url.replace('sqlite:///', '')
            
            # Décompresser et restaurer
            if backup_file.endswith('.sql.gz'):
                subprocess.run(
                    f"gunzip -c {backup_file} | sqlite3 {db_path}",
                    shell=True, check=True
                )
            elif backup_file.endswith('.sqlite'):
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

def main():
    """Fonction principale du script."""
    parser = argparse.ArgumentParser(description='Migration Alembic sécurisée pour Mathakine')
    parser.add_argument('--check-only', action='store_true', help='Vérifier uniquement sans migrer')
    parser.add_argument('--force', action='store_true', help='Forcer la migration même si des tables protégées sont menacées')
    parser.add_argument('--restore-backup', help='Restaurer une sauvegarde spécifique')
    
    args = parser.parse_args()
    db_url = get_db_url()
    
    # Mode restauration
    if args.restore_backup:
        success = restore_backup(args.restore_backup, db_url)
        sys.exit(0 if success else 1)
    
    # Mode vérification uniquement
    if args.check_only:
        success = check_protected_tables(db_url)
        logger.info(f"Vérification des tables protégées: {'✓ OK' if success else '✗ ÉCHEC'}")
        sys.exit(0 if success else 1)
    
    # Mode migration normal
    logger.info("=== DÉMARRAGE DE LA MIGRATION SÉCURISÉE ===")
    
    # Créer une sauvegarde
    backup_file = create_backup(db_url)
    
    # Exécuter la migration
    migration_success = run_migration()
    
    # Vérifier l'intégrité
    integrity_ok = check_protected_tables(db_url) if migration_success else False
    
    # Si migration réussie et intégrité OK
    if migration_success and integrity_ok:
        logger.info("=== MIGRATION TERMINÉE AVEC SUCCÈS ===")
        sys.exit(0)
    
    # Si échec et pas de forçage
    if not args.force:
        logger.error("Migration échouée ou intégrité compromise. Restauration de la sauvegarde...")
        restore_success = restore_backup(backup_file, db_url)
        if restore_success:
            logger.info("Restauration réussie. La base de données a été rétablie à son état initial.")
        else:
            logger.critical("ÉCHEC DE LA RESTAURATION. INTERVENTION MANUELLE REQUISE!")
        
    logger.error("=== MIGRATION TERMINÉE AVEC ERREURS ===")
    sys.exit(1)

if __name__ == "__main__":
    main() 
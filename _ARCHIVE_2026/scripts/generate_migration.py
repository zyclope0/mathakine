#!/usr/bin/env python
"""
Script pour générer une nouvelle migration Alembic en toute sécurité.
Ce script:
1. Génère une nouvelle migration
2. Vérifie que la migration ne supprime pas les tables héritées
3. Affiche un résumé des opérations de la migration
"""
import os
import sys
import re
import argparse
from pathlib import Path

# Ajouter le répertoire parent au sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.core.config import settings
from alembic.config import Config
from alembic import command
from loguru import logger

# Tables héritées à protéger
PROTECTED_TABLES = {'results', 'statistics', 'user_stats', 'schema_version'}

def check_migration_file(filepath):
    """
    Vérifie qu'un fichier de migration ne tente pas de supprimer des tables protégées
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher les opérations de suppression de table
    drop_table_pattern = r'op\.drop_table\([\'"]([^\'"]+)[\'"]\)'
    drop_tables = re.findall(drop_table_pattern, content)
    
    # Vérifier si des tables protégées sont supprimées
    protected_drops = [table for table in drop_tables if table in PROTECTED_TABLES]
    
    if protected_drops:
        logger.error(f"🚨 ATTENTION: La migration tente de supprimer des tables protégées: {', '.join(protected_drops)}")
        return False
    
    return True

def find_latest_migration():
    """
    Trouve le dernier fichier de migration généré
    """
    versions_dir = os.path.join(BASE_DIR, "migrations", "versions")
    migration_files = sorted(Path(versions_dir).glob("*.py"), key=os.path.getmtime)
    
    if not migration_files:
        return None
    
    return str(migration_files[-1])

def generate_migration(message):
    """
    Génère une nouvelle migration Alembic
    """
    logger.info(f"Génération d'une nouvelle migration: {message}")
    
    # Configurer Alembic
    alembic_cfg = Config(os.path.join(BASE_DIR, "alembic.ini"))
    
    try:
        # Générer une nouvelle migration
        command.revision(alembic_cfg, message=message, autogenerate=True)
        logger.success("Migration générée avec succès")
        
        # Trouver le fichier de migration généré
        latest_migration = find_latest_migration()
        
        if latest_migration:
            logger.info(f"Vérification de la migration: {os.path.basename(latest_migration)}")
            
            # Vérifier que la migration ne supprime pas de tables protégées
            if not check_migration_file(latest_migration):
                logger.warning("La migration nécessite une attention particulière.")
                logger.info("Veuillez vérifier et modifier manuellement le fichier de migration si nécessaire.")
            else:
                logger.success("La migration semble sûre, aucune table protégée n'est supprimée.")
                
            # Afficher un résumé du fichier de migration
            with open(latest_migration, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extraire les opérations principales
            upgrade_section = re.search(r'def upgrade.*?def downgrade', content, re.DOTALL)
            if upgrade_section:
                operations = upgrade_section.group(0)
                # Rechercher et afficher les principales opérations
                add_column = re.findall(r'op\.add_column\([\'"]([^\'"]+)[\'"]', operations)
                create_table = re.findall(r'op\.create_table\([\'"]([^\'"]+)[\'"]', operations)
                alter_column = re.findall(r'op\.alter_column\([\'"]([^\'"]+)[\'"]', operations)
                
                logger.info("Résumé des opérations de la migration:")
                if create_table:
                    logger.info(f"- Création de tables: {', '.join(create_table)}")
                if add_column:
                    logger.info(f"- Ajout de colonnes dans: {', '.join(add_column)}")
                if alter_column:
                    logger.info(f"- Modification de colonnes dans: {', '.join(alter_column)}")
        else:
            logger.error("Impossible de trouver le fichier de migration généré")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la migration: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Générer une nouvelle migration Alembic")
    parser.add_argument("message", help="Message décrivant la migration")
    args = parser.parse_args()
    
    success = generate_migration(args.message)
    
    if success:
        logger.info("Migration générée avec succès.")
        logger.info("Pour appliquer la migration, exécutez: alembic upgrade head")
        sys.exit(0)
    else:
        logger.error("Échec de la génération de la migration")
        sys.exit(1) 
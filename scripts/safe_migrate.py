#!/usr/bin/env python
"""
Script pour appliquer les migrations Alembic de manière sécurisée en production.
Ce script:
1. Analyse les migrations à appliquer pour détecter des opérations risquées
2. Effectue une sauvegarde de la base de données avant la migration
3. Applique les migrations avec journalisation détaillée
4. Gère les erreurs et propose des actions de récupération

Ce script doit être utilisé en production pour toute migration de schéma.
"""
import os
import sys
import re
import subprocess
import argparse
import time
from pathlib import Path

# Ajouter le répertoire parent au sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.core.config import settings
from app.core.logging_config import get_logger
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text

# Configuration du logging
logger = get_logger("safe_migrate")

# Chemin vers le script de sauvegarde
BACKUP_SCRIPT = os.path.join(BASE_DIR, "scripts", "alembic_backup.py")

# Liste des opérations considérées comme risquées
RISKY_OPERATIONS = [
    r'op\.drop_table\([\'"]([^\'"]+)[\'"]\)',              # Suppression de table
    r'op\.drop_column\([\'"]([^\'"]+)[\'"],\s*[\'"]([^\'"]+)[\'"]\)',  # Suppression de colonne
    r'op\.alter_column\([\'"]([^\'"]+)[\'"],\s*[\'"]([^\'"]+)[\'"]\s*.*not_nullable=True',  # Ajout de NOT NULL
    r'op\.rename_table\([\'"]([^\'"]+)[\'"],\s*[\'"]([^\'"]+)[\'"]\)',  # Renommage de table
    r'op\.execute\([\'"]DROP',                              # Exécution directe de DROP
    r'op\.execute\([\'"]TRUNCATE',                          # Exécution directe de TRUNCATE
    r'op\.execute\([\'"]ALTER\s+TABLE.*DROP\s+CONSTRAINT',  # Suppression de contrainte
]

# Tables protégées que nous ne voulons jamais supprimer ou modifier sans confirmation
PROTECTED_TABLES = {'results', 'statistics', 'user_stats', 'schema_version', 'exercises', 'users', 'attempts'}

def get_current_revision():
    """Récupère la révision actuelle de la base de données."""
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la révision actuelle: {e}")
        return None

def get_pending_migrations():
    """Récupère la liste des migrations à appliquer."""
    alembic_cfg = Config(os.path.join(BASE_DIR, "alembic.ini"))
    script = ScriptDirectory.from_config(alembic_cfg)
    
    current_rev = get_current_revision()
    if not current_rev:
        logger.error("Impossible de déterminer la révision actuelle")
        return []
    
    # Récupérer les migrations à appliquer
    revisions = []
    for rev in script.walk_revisions(base=current_rev, head="head"):
        if rev.revision != current_rev:
            revisions.append(rev)
    
    return list(reversed(revisions))

def check_migration_safety(revision):
    """Analyse une migration pour y détecter des opérations risquées."""
    # Trouver le fichier de migration
    migrations_dir = os.path.join(BASE_DIR, "migrations", "versions")
    migration_file = os.path.join(migrations_dir, f"{revision.revision}.py")
    
    if not os.path.exists(migration_file):
        # Tenter de trouver le fichier avec le nom de fichier différent du revision_id
        for file in os.listdir(migrations_dir):
            if file.endswith(".py"):
                with open(os.path.join(migrations_dir, file), 'r') as f:
                    content = f.read()
                    if f'revision: str = \'{revision.revision}\'' in content:
                        migration_file = os.path.join(migrations_dir, file)
                        break
    
    if not os.path.exists(migration_file):
        logger.error(f"Fichier de migration introuvable pour {revision.revision}")
        return False, []
    
    risky_operations = []
    with open(migration_file, 'r') as f:
        content = f.read()
        
        # Rechercher les opérations risquées
        for pattern in RISKY_OPERATIONS:
            matches = re.findall(pattern, content)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):  # Pour les patterns avec plusieurs groupes
                        table_name = match[0]
                        column_name = match[1] if len(match) > 1 else ""
                        operation = f"{pattern.split('op\\.')[1].split('\\(')[0]} sur {table_name}.{column_name}" if column_name else f"{pattern.split('op\\.')[1].split('\\(')[0]} sur {table_name}"
                    else:  # Pour les patterns avec un seul groupe
                        table_name = match
                        operation = f"{pattern.split('op\\.')[1].split('\\(')[0]} sur {table_name}"
                    
                    # Vérifier si c'est une table protégée
                    if table_name in PROTECTED_TABLES:
                        risky_operations.append(f"🚨 CRITIQUE: {operation} (Table protégée)")
                    else:
                        risky_operations.append(f"⚠️ RISQUE: {operation}")
    
    return len(risky_operations) == 0, risky_operations

def backup_database():
    """Exécute le script de sauvegarde de la base de données."""
    logger.info("Lancement de la sauvegarde de la base de données...")
    
    try:
        subprocess.run(
            [sys.executable, BACKUP_SCRIPT],
            check=True
        )
        logger.success("Sauvegarde de la base de données terminée")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la sauvegarde: {e}")
        return False
    except Exception as e:
        logger.error(f"Exception lors de la sauvegarde: {e}")
        return False

def apply_migrations(target="head", sql=False):
    """Applique les migrations jusqu'à la révision cible."""
    logger.info(f"Application des migrations jusqu'à {target}...")
    
    alembic_cfg = Config(os.path.join(BASE_DIR, "alembic.ini"))
    
    try:
        if sql:
            # Générer le SQL sans l'exécuter
            with open("migration_sql.sql", "w") as f:
                command.upgrade(alembic_cfg, target, sql=True, stdout=f)
            logger.info(f"SQL de migration généré dans migration_sql.sql")
            return True
        else:
            # Exécuter la migration
            command.upgrade(alembic_cfg, target)
            logger.success(f"Migrations appliquées avec succès jusqu'à {target}")
            return True
    except Exception as e:
        logger.error(f"Erreur lors de l'application des migrations: {e}")
        return False

def safe_migrate(target="head", force=False, dry_run=False, sql=False):
    """
    Applique les migrations de manière sécurisée.
    
    Args:
        target: La révision cible (défaut: "head")
        force: Forcer l'application même si des opérations risquées sont détectées
        dry_run: Ne pas appliquer les migrations, juste afficher ce qui serait fait
        sql: Générer le SQL sans l'exécuter
    """
    logger.info(f"Démarrage de la migration sécurisée vers {target}...")
    
    # 1. Récupérer les migrations à appliquer
    pending_migrations = get_pending_migrations()
    if not pending_migrations:
        logger.info("Aucune migration à appliquer.")
        return True
    
    logger.info(f"{len(pending_migrations)} migration(s) à appliquer:")
    for i, rev in enumerate(pending_migrations, 1):
        logger.info(f"{i}. {rev.revision}: {rev.doc}")
    
    # 2. Analyser chaque migration pour les opérations risquées
    all_safe = True
    risky_operations = []
    
    for rev in pending_migrations:
        logger.info(f"Analyse de la migration {rev.revision}...")
        is_safe, operations = check_migration_safety(rev)
        
        if not is_safe:
            all_safe = False
            risky_operations.extend(operations)
    
    if not all_safe:
        logger.warning("Des opérations risquées ont été détectées dans les migrations:")
        for op in risky_operations:
            logger.warning(f"  - {op}")
        
        if not force and not dry_run:
            logger.error("Migration annulée. Utilisez --force pour appliquer malgré les risques.")
            return False
    
    # 3. Si c'est un dry run, s'arrêter ici
    if dry_run:
        logger.info("Dry run terminé. Aucune modification n'a été appliquée.")
        return True
    
    # 4. Faire une sauvegarde avant d'appliquer les migrations
    if not backup_database():
        logger.error("Migration annulée à cause de l'échec de la sauvegarde.")
        logger.info("Utilisez --force pour ignorer l'échec de la sauvegarde.")
        if not force:
            return False
    
    # 5. Appliquer les migrations
    start_time = time.time()
    success = apply_migrations(target, sql)
    end_time = time.time()
    
    if success:
        logger.success(f"Migration terminée en {end_time - start_time:.2f} secondes")
    else:
        logger.error("La migration a échoué.")
        logger.info("Consultez les logs pour plus de détails et envisagez de restaurer la sauvegarde.")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Appliquer les migrations Alembic de manière sécurisée")
    parser.add_argument("--target", default="head", help="Révision cible (défaut: head)")
    parser.add_argument("--force", action="store_true", help="Forcer l'application même si des risques sont détectés")
    parser.add_argument("--dry-run", action="store_true", help="Ne pas appliquer les migrations, juste afficher ce qui serait fait")
    parser.add_argument("--sql", action="store_true", help="Générer le SQL sans l'exécuter")
    args = parser.parse_args()
    
    success = safe_migrate(args.target, args.force, args.dry_run, args.sql)
    if success:
        sys.exit(0)
    else:
        sys.exit(1) 
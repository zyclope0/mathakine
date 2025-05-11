#!/usr/bin/env python
"""
Script pour migrer tous les fichiers logs vers le dossier centralisé.
Ce script :
1. Recherche tous les fichiers .log dans le projet
2. Les copie dans le dossier logs/ avec un préfixe indiquant leur emplacement d'origine
3. Maintient les logs originaux en place jusqu'à ce qu'ils soient nettoyés manuellement
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au path pour pouvoir importer les modules du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.core.logging_config import LOGS_DIR, get_logger
    logger = get_logger("migrate_logs")
except ImportError:
    # Si le module n'est pas encore disponible, définir les valeurs par défaut
    LOGS_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "logs"

    # Importer directement loguru
    from loguru import logger
    logger.add(str(LOGS_DIR / "migration.log"), level="DEBUG", rotation="5 MB")

# Répertoires à exclure
EXCLUDED_DIRS = {
    ".git",
    "venv",
    "__pycache__",
    "node_modules",
    str(LOGS_DIR.name)  # Exclure le dossier logs/ lui-même
}



def find_log_files(start_dir=None):
    """
    Recherche tous les fichiers .log dans le projet, à l'exception des répertoires exclus.

    Args:
        start_dir: Répertoire de départ pour la recherche. Si None, utilise le répertoire racine du projet.

    Returns:
        list: Liste de chemins de fichiers logs trouvés
    """
    if start_dir is None:
        start_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    log_files = []

    for root, dirs, files in os.walk(start_dir):
        # Filtrer les répertoires exclus
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        # Trouver les fichiers .log
        for file in files:
            if file.endswith(".log"):
                log_files.append(Path(root) / file)

    return log_files



def migrate_logs(log_files, timestamp=True):
    """
    Copie les fichiers logs vers le dossier centralisé.

    Args:
        log_files: Liste des chemins de fichiers logs à migrer
        timestamp: Si True, ajoute un timestamp au nom du fichier

    Returns:
        int: Nombre de fichiers migrés
    """
    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Dossier de logs créé: {LOGS_DIR}")

    migrated_count = 0

    # Créer un sous-dossier spécifique pour la migration
    migration_dir = LOGS_DIR / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    migration_dir.mkdir(exist_ok=True)

    for log_file in log_files:
        try:
            # Créer un nom unique pour le fichier
            relative_path = log_file.relative_to(Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            new_name = str(relative_path).replace(os.sep, "_")

            if timestamp:
                # Ajouter un timestamp au nom du fichier
                file_name, file_ext = os.path.splitext(new_name)
                new_name = f"{file_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"

            # Copier le fichier
            target_file = migration_dir / new_name
            shutil.copy2(log_file, target_file)
            logger.info(f"Fichier migré: {log_file} -> {target_file}")
            migrated_count += 1

        except Exception as e:
            logger.error(f"Erreur lors de la migration du fichier {log_file}: {e}")

    return migrated_count



def main():
    logger.info("Début de la migration des fichiers logs")

    # Trouver tous les fichiers logs
    log_files = find_log_files()
    logger.info(f"{len(log_files)} fichiers logs trouvés")

    # Migrer les logs
    count = migrate_logs(log_files)
    logger.success(f"{count} fichiers logs migrés avec succès vers {LOGS_DIR}")

    print(f"Migration terminée: {count}/{len(log_files)} fichiers migrés.")
    print(f"Les logs ont été copiés dans: {LOGS_DIR}")
    print("Les fichiers d'origine restent en place.")
    print("Pour un nettoyage sécurisé, utilisez scripts/cleanup_logs.py après avoir vérifié la migration.")

if __name__ == "__main__":
    main()

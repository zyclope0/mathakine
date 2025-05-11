#!/usr/bin/env python
"""
Script pour nettoyer les anciens fichiers logs après la migration.
ATTENTION: Ce script supprime les fichiers. À utiliser avec précaution.

Ce script :
1. Trouve tous les fichiers .log dans le projet (hors du dossier logs/ centralisé)
2. Propose à l'utilisateur de les supprimer ou de les conserver
3. Crée une sauvegarde supplémentaire avant la suppression (optionnel)
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
    from scripts.migrate_logs import find_log_files
    logger = get_logger("cleanup_logs")
except ImportError:
    # Définitions alternatives si les modules ne sont pas disponibles
    LOGS_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "logs"

    # Importer directement loguru
    from loguru import logger
    logger.add(str(LOGS_DIR / "cleanup.log"), level="DEBUG", rotation="5 MB")

    # Définir find_log_files localement si le module n'est pas disponible
    from scripts.migrate_logs import find_log_files



def confirm_action(message="Voulez-vous continuer ?", default=False):
    """
    Demande une confirmation à l'utilisateur.

    Args:
        message: Le message à afficher
        default: Valeur par défaut (True/False) si l'utilisateur appuie sur Entrée

    Returns:
        bool: True si l'utilisateur confirme, False sinon
    """
    if default:
        options = "[O/n]"
        valid_responses = {"": True, "o": True, "oui": True, "y": True, "yes": True,
                        "n": False, "non": False, "no": False}
    else:
        options = "[o/N]"
        valid_responses = {"": False, "o": True, "oui": True, "y": True, "yes": True,
                        "n": False, "non": False, "no": False}

    while True:
        response = input(f"{message} {options} ").lower()
        if response in valid_responses:
            return valid_responses[response]
        print("Réponse invalide, veuillez répondre par o/oui ou n/non.")



def create_backup(log_files, backup_dir=None):
    """
    Crée une sauvegarde des fichiers logs avant de les supprimer.

    Args:
        log_files: Liste des chemins de fichiers logs à sauvegarder
        backup_dir: Répertoire de sauvegarde. Si None, crée un sous-répertoire dans logs/

    Returns:
        Path: Chemin du répertoire de sauvegarde
    """
    if backup_dir is None:
        backup_dir = LOGS_DIR / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    for log_file in log_files:
        try:
            # Créer un nom unique pour le fichier de sauvegarde
            relative_path = log_file.relative_to(Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            backup_path = backup_dir / str(relative_path).replace(os.sep, "_")

            # Créer les sous-répertoires si nécessaire
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Copier le fichier
            shutil.copy2(log_file, backup_path)
            logger.debug(f"Fichier sauvegardé: {log_file} -> {backup_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier {log_file}: {e}")

    return backup_dir



def delete_log_files(log_files, skip_confirmation=False):
    """
    Supprime les fichiers logs.

    Args:
        log_files: Liste des chemins de fichiers logs à supprimer
        skip_confirmation: Si True, supprime sans demander de confirmation individuelle

    Returns:
        int: Nombre de fichiers supprimés
    """
    deleted_count = 0

    for log_file in log_files:
        try:
            # Demander confirmation pour chaque fichier si skip_confirmation est False
            if skip_confirmation or confirm_action(f"Supprimer {log_file} ?", default=False):
                os.remove(log_file)
                logger.info(f"Fichier supprimé: {log_file}")
                deleted_count += 1
            else:
                logger.info(f"Conservation du fichier: {log_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier {log_file}: {e}")

    return deleted_count



def main():
    logger.info("Début du nettoyage des fichiers logs")

    # Trouver tous les fichiers logs
    log_files = find_log_files()
    logger.info(f"{len(log_files)} fichiers logs trouvés")

    if not log_files:
        print("Aucun fichier log à nettoyer.")
        return

    # Afficher les fichiers trouvés
    print(f"Fichiers logs trouvés ({len(log_files)}):")
    for i, file in enumerate(log_files, 1):
        print(f"{i}. {file}")

    # Demander confirmation
    if not confirm_action("\nVoulez-vous nettoyer ces fichiers logs ?", default=False):
        print("Opération annulée.")
        return

    # Proposer de faire une sauvegarde
    if confirm_action("Voulez-vous créer une sauvegarde avant la suppression ?", default=True):
        backup_dir = create_backup(log_files)
        print(f"Sauvegarde créée dans: {backup_dir}")

    # Demander le mode de suppression
    batch_mode = confirm_action("Voulez-vous supprimer tous les fichiers sans confirmation individuelle ?"
        , default=False)

    # Supprimer les fichiers
    deleted = delete_log_files(log_files, skip_confirmation=batch_mode)

    # Afficher le résultat
    logger.success(f"{deleted} fichiers logs nettoyés sur {len(log_files)}")
    print(f"\nNettoyage terminé: {deleted}/{len(log_files)} fichiers supprimés.")

    if deleted < len(log_files):
        print(f"{len(log_files) - deleted} fichiers ont été conservés.")

if __name__ == "__main__":
    main()

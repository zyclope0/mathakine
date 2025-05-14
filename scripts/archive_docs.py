#!/usr/bin/env python3
import os
import shutil
from datetime import datetime
import logging
import filecmp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOCS_DIR = "docs"
ARCHIVE_DIR = os.path.join(DOCS_DIR, "ARCHIVE")

# Structure attendue des dossiers principaux
EXPECTED_STRUCTURE = {
    "Core": [
        "ARCHITECTURE.md",
        "DEVELOPER_GUIDE.md",
        "PROJECT_STATUS.md",
        "UI_GUIDE.md"
    ],
    "Tech": [
        "DATABASE_GUIDE.md",
        "TRANSACTION_SYSTEM.md",
        "TESTING_GUIDE.md",
        "OPERATIONS_GUIDE.md"
    ],
    "Features": [
        "LOGIC_CHALLENGES.md"
    ]
}

# Fichiers à supprimer immédiatement
FILES_TO_DELETE = [
    "*.redirect",
    "NEW_TABLE_DES_MATIERES.md",
    "NEW_DOCUMENTATION_STRUCTURE.md",
    "TRANSACTION_SYSTEM_EXAMPLE.md"
]

# Fichiers à archiver par année
ARCHIVE_2024 = [
    "PYDANTIC_V2_MIGRATION.md",
    "LOGGING.md",
    "POSTGRESQL_MIGRATION.md",
    "CLEANUP_REPORT.md",
    "HISTORIQUE_REFACTORING.md",
    "Reference/CHANGELOG.md",
    "Reference/GLOSSARY.md",
    "validation/COMPATIBILITY.md",
    "validation/QUICKSTART.md",
    "validation/README.md"
]

ARCHIVE_2025 = [
    "IMPLEMENTATION_PLAN_DOCUMENTATION.md",
    "DOCUMENT_CONVERSION_STATUS.md",
    "ADAPTATEUR.md",
    "TRANSACTION_MANAGEMENT.md",
    "CASCADE_DELETION.md",
    "NOUVEAUX_TYPES_EXERCICES.md",
    "TESTS.md",
    "API_REFERENCE.md",
    "ALEMBIC_SÉCURITÉ.md",
    "ALEMBIC.md",
    "SCHEMA.md",
    "AUTH_GUIDE.md",
    "GUIDE_DEVELOPPEUR.md",
    "MAINTENANCE_ET_NETTOYAGE.md",
    "CORRECTIONS_ET_MAINTENANCE.md",
    "ADMIN_COMMANDS.md",
    "DEPLOYMENT_GUIDE.md",
    "IMPLEMENTATION_PLAN.md",
    "UI_GUIDE.md",
    "PROJECT_STATUS.md",
    "ARCHITECTURE.md",
    "LOGIC_CHALLENGES_REQUIREMENTS.md"
]

# Dossiers à supprimer après archivage
DIRS_TO_REMOVE = [
    "Reference",
    "validation"
]

def ensure_dir(directory):
    """Crée un répertoire s'il n'existe pas."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Créé le répertoire: {directory}")

def check_and_fix_duplicates():
    """Vérifie et corrige les fichiers dupliqués."""
    for category, files in EXPECTED_STRUCTURE.items():
        category_dir = os.path.join(DOCS_DIR, category)
        ensure_dir(category_dir)
        
        for file in files:
            root_file = os.path.join(DOCS_DIR, file)
            category_file = os.path.join(category_dir, file)
            
            # Si le fichier existe à la racine
            if os.path.exists(root_file):
                # Si le fichier existe aussi dans le dossier catégorie
                if os.path.exists(category_file):
                    # Comparer les fichiers
                    if filecmp.cmp(root_file, category_file, shallow=False):
                        # Si identiques, supprimer celui de la racine
                        os.remove(root_file)
                        logger.info(f"Supprimé le duplicata: {root_file}")
                    else:
                        # Si différents, archiver celui de la racine
                        archive_dir = os.path.join(ARCHIVE_DIR, "2025", "duplicates")
                        ensure_dir(archive_dir)
                        shutil.move(root_file, os.path.join(archive_dir, file))
                        logger.info(f"Archivé la version différente: {root_file}")
                else:
                    # Déplacer le fichier dans son dossier de catégorie
                    shutil.move(root_file, category_file)
                    logger.info(f"Déplacé {file} vers {category_dir}/")

def archive_files(files, year):
    """Archive les fichiers dans le dossier approprié."""
    archive_dir = os.path.join(ARCHIVE_DIR, str(year))
    ensure_dir(archive_dir)
    
    for file in files:
        src = os.path.join(DOCS_DIR, file)
        if os.path.exists(src):
            # Créer le sous-dossier dans l'archive si nécessaire
            if '/' in file:
                subdir = os.path.dirname(file)
                ensure_dir(os.path.join(archive_dir, subdir))
            
            dst = os.path.join(archive_dir, file)
            shutil.move(src, dst)
            logger.info(f"Déplacé {file} vers {dst}")
        else:
            logger.warning(f"Fichier non trouvé: {file}")

def delete_files(patterns):
    """Supprime les fichiers correspondant aux motifs donnés."""
    import glob
    
    for pattern in patterns:
        for file in glob.glob(os.path.join(DOCS_DIR, pattern)):
            try:
                os.remove(file)
                logger.info(f"Supprimé: {file}")
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de {file}: {e}")

def remove_empty_dirs():
    """Supprime les dossiers vides et spécifiés."""
    for dir_name in DIRS_TO_REMOVE:
        dir_path = os.path.join(DOCS_DIR, dir_name)
        try:
            shutil.rmtree(dir_path)
            logger.info(f"Supprimé le dossier: {dir_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du dossier {dir_path}: {e}")

def main():
    """Fonction principale d'archivage."""
    logger.info("Début de l'archivage des documents...")
    
    # Créer les répertoires d'archive
    ensure_dir(ARCHIVE_DIR)
    ensure_dir(os.path.join(ARCHIVE_DIR, "2024"))
    ensure_dir(os.path.join(ARCHIVE_DIR, "2025"))
    
    # Vérifier et corriger les duplications
    check_and_fix_duplicates()
    
    # Supprimer les fichiers non nécessaires
    delete_files(FILES_TO_DELETE)
    
    # Archiver les fichiers par année
    archive_files(ARCHIVE_2024, 2024)
    archive_files(ARCHIVE_2025, 2025)
    
    # Supprimer les dossiers vides et obsolètes
    remove_empty_dirs()
    
    logger.info("Archivage terminé avec succès!")

if __name__ == "__main__":
    main() 
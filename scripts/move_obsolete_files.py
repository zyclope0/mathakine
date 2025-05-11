#!/usr/bin/env python
"""
Script pour déplacer les fichiers de sauvegarde (.bak)
et autres fichiers obsolètes vers le dossier d'archives.
"""

import os
import shutil
from pathlib import Path
import datetime

# Définition des chemins
ROOT_DIR = Path(__file__).parent.parent
DOCS_DIR = ROOT_DIR / "docs"
ARCHIVE_DIR = DOCS_DIR / "ARCHIVE"



def ensure_archive_dir():
    """S'assurer que le dossier d'archives existe"""
    ARCHIVE_DIR.mkdir(exist_ok=True)

    # Créer un sous-dossier daté pour cette opération d'archivage
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    archive_date_dir = ARCHIVE_DIR / today
    archive_date_dir.mkdir(exist_ok=True)

    return archive_date_dir



def move_backup_files(archive_dir):
    """Déplacer tous les fichiers .bak vers le dossier d'archives"""
    moved_files = []

    # Rechercher tous les fichiers .bak dans le répertoire docs
    for file in DOCS_DIR.glob("*.bak"):
        # Ignorer les fichiers qui sont déjà dans le dossier ARCHIVE
        if "ARCHIVE" in str(file):
            continue

        # Définir le chemin de destination
        dest_path = archive_dir / file.name

        # S'assurer que le nom de fichier est unique dans le dossier d'archives
        if dest_path.exists():
            base_name = file.stem
            extension = file.suffix
            counter = 1
            while dest_path.exists():
                new_name = f"{base_name}_{counter}{extension}"
                dest_path = archive_dir / new_name
                counter += 1

        # Déplacer le fichier
        shutil.move(str(file), str(dest_path))
        moved_files.append((str(file), str(dest_path)))

    return moved_files



def main():
    """Fonction principale"""
    print("Déplacement des fichiers obsolètes vers le dossier d'archives...")

    # S'assurer que le dossier d'archives existe
    archive_dir = ensure_archive_dir()
    print(f"Dossier d'archives: {archive_dir}")

    # Déplacer les fichiers .bak
    moved_files = move_backup_files(archive_dir)

    # Afficher le résultat
    if moved_files:
        print(f"\n{len(moved_files)} fichiers déplacés vers {archive_dir}:")
        for src, dest in moved_files:
            print(f"  {src} -> {dest}")
    else:
        print("\nAucun fichier .bak trouvé à déplacer.")

    print("\nOpération terminée.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Script pour nettoyer la documentation redondante.
Usage : python scripts/cleanup_doc.py [check|move|delete]
  - check : Liste les fichiers redondants sans les modifier
  - move : Déplace les fichiers redondants vers docs/ARCHIVE
  - delete : Supprime les fichiers redondants
"""

import os
import sys
import shutil
from datetime import datetime

# Répertoires concernés
DOCS_DIR = 'docs'
ARCHIVE_DIR = os.path.join(DOCS_DIR, 'ARCHIVE')

# Liste des fichiers qui ont été consolidés et qui sont désormais redondants
REDUNDANT_FILES = [
    os.path.join(DOCS_DIR, 'REFACTORING_SUMMARY.md'),
    os.path.join(DOCS_DIR, 'CENTRALISATION_DOCUMENTATION.md'),
]

def ensure_archive_dir():
    """S'assure que le répertoire d'archives existe."""
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

def check_redundant_files():
    """Vérifie si les fichiers redondants existent."""
    existing_files = []
    for file_path in REDUNDANT_FILES:
        if os.path.exists(file_path):
            existing_files.append(file_path)
    
    return existing_files

def move_redundant_files():
    """Déplace les fichiers redondants vers le répertoire d'archives."""
    ensure_archive_dir()
    moved_files = []
    
    for file_path in check_redundant_files():
        file_name = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_path = os.path.join(ARCHIVE_DIR, f"{timestamp}_{file_name}")
        
        shutil.move(file_path, archived_path)
        moved_files.append((file_path, archived_path))
    
    return moved_files

def delete_redundant_files():
    """Supprime les fichiers redondants."""
    deleted_files = []
    
    for file_path in check_redundant_files():
        os.remove(file_path)
        deleted_files.append(file_path)
    
    return deleted_files

def main():
    """Fonction principale."""
    if len(sys.argv) != 2 or sys.argv[1] not in ['check', 'move', 'delete']:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'check':
        redundant_files = check_redundant_files()
        if redundant_files:
            print("Fichiers redondants détectés :")
            for file_path in redundant_files:
                print(f"  - {file_path}")
        else:
            print("Aucun fichier redondant détecté.")
    
    elif command == 'move':
        moved_files = move_redundant_files()
        if moved_files:
            print("Fichiers déplacés vers le répertoire d'archives :")
            for source, dest in moved_files:
                print(f"  - {source} -> {dest}")
        else:
            print("Aucun fichier n'a été déplacé.")
    
    elif command == 'delete':
        deleted_files = delete_redundant_files()
        if deleted_files:
            print("Fichiers supprimés :")
            for file_path in deleted_files:
                print(f"  - {file_path}")
        else:
            print("Aucun fichier n'a été supprimé.")

if __name__ == "__main__":
    main() 
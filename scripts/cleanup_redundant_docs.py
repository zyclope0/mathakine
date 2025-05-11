#!/usr/bin/env python
"""
Script pour supprimer les fichiers redondants après vérification
des fichiers fusionnés par le script consolidate_docs.py.
"""

import os
import sys
import shutil
from pathlib import Path

# Définition des chemins
ROOT_DIR = Path(__file__).parent.parent
DOCS_DIR = ROOT_DIR / "docs"

# Liste des fichiers à supprimer après consolidation
FILES_TO_REMOVE = [
    DOCS_DIR / "RECENT_UPDATES.md",        # Fusionné dans CHANGELOG.md
    DOCS_DIR / "CLEANUP_REPORT_AUTO.md",   # Fusionné dans CLEANUP_REPORT.md
    DOCS_DIR / "migration_section.md",     # Intégré dans POSTGRESQL_MIGRATION.md
]



def check_backups_exist():
    """Vérifie que les fichiers de sauvegarde existent"""
    all_exist = True
    for file_path in FILES_TO_REMOVE:
        backup_path = Path(str(file_path) + ".bak")
        if not backup_path.exists():
            print(f"⚠️  Sauvegarde non trouvée pour {file_path}")
            all_exist = False
    return all_exist



def remove_files(force=False):
    """Supprime les fichiers redondants"""
    backups_exist = check_backups_exist()

    if not backups_exist and not force:
        print("❌ Certaines sauvegardes sont manquantes. Utiliser --force pour supprimer quand même.")
        return False

    success = True
    for file_path in FILES_TO_REMOVE:
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"✅ Supprimé: {file_path}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file_path}: {e}")
                success = False
        else:
            print(f"ℹ️  Déjà supprimé: {file_path}")

    return success



def restore_from_backups():
    """Restaure les fichiers à partir des sauvegardes"""
    success = True
    for file_path in FILES_TO_REMOVE:
        backup_path = Path(str(file_path) + ".bak")
        if backup_path.exists():
            try:
                shutil.copy2(backup_path, file_path)
                print(f"✅ Restauré: {file_path}")
            except Exception as e:
                print(f"❌ Erreur lors de la restauration de {file_path}: {e}")
                success = False
        else:
            print(f"⚠️  Sauvegarde non trouvée pour {file_path}")
            success = False

    return success



def main():
    """Fonction principale"""
    print("Script de nettoyage des documents redondants")
    print("============================================\n")

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python cleanup_redundant_docs.py [remove|check|restore] [--force]")
        print("\nArguments:")
        print("  remove   - Supprimer les fichiers redondants")
        print("  check    - Vérifier quels fichiers seraient supprimés")
        print("  restore  - Restaurer les fichiers à partir des sauvegardes")
        print("  --force  - Forcer la suppression même si les sauvegardes n'existent pas")
        return

    action = sys.argv[1].lower()
    force = "--force" in sys.argv

    if action == "check":
        print("Fichiers qui seraient supprimés:")
        for file_path in FILES_TO_REMOVE:
            if file_path.exists():
                print(f"- {file_path}")
            else:
                print(f"- {file_path} (n'existe pas)")

        print("\nFichiers de sauvegarde:")
        for file_path in FILES_TO_REMOVE:
            backup_path = Path(str(file_path) + ".bak")
            if backup_path.exists():
                print(f"- {backup_path} ✅")
            else:
                print(f"- {backup_path} ❌")

    elif action == "remove":
        print("Suppression des fichiers redondants...")
        if remove_files(force):
            print("\n✅ Tous les fichiers redondants ont été supprimés avec succès.")
            print("Pour restaurer les fichiers à partir des sauvegardes, utilisez:")
            print("  python cleanup_redundant_docs.py restore")
        else:
            print("\n⚠️  Des erreurs se sont produites lors de la suppression.")

    elif action == "restore":
        print("Restauration des fichiers à partir des sauvegardes...")
        if restore_from_backups():
            print("\n✅ Tous les fichiers ont été restaurés avec succès.")
        else:
            print("\n⚠️  Des erreurs se sont produites lors de la restauration.")

    else:
        print(f"❌ Action inconnue: {action}")
        print("Actions valides: remove, check, restore")

if __name__ == "__main__":
    main()

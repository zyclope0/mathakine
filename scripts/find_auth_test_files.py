#!/usr/bin/env python
"""
[TEST_AUTH_JWT] Script pour trouver tous les fichiers liés aux tests d'authentification JWT.
Ce script recherche tous les fichiers contenant le tag '[TEST_AUTH_JWT]'.
"""
import os
import sys
from pathlib import Path


def find_auth_test_files():
    """
    Trouve tous les fichiers contenant le tag '[TEST_AUTH_JWT]'.
    """
    print("[TEST_AUTH_JWT] Recherche des fichiers liés aux tests d'authentification...")
    
    # Obtenir le chemin racine du projet
    root_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Liste pour stocker les fichiers trouvés
    auth_test_files = []
    
    # Extensions de fichiers à rechercher
    extensions = ['.py', '.md', '.sql', '.json', '.yml', '.yaml', '.sh', '.bat']
    
    # Répertoires à exclure
    exclude_dirs = ['.git', '.venv', 'venv', '__pycache__', 'node_modules', '.pytest_cache']
    
    # Parcourir tous les fichiers du projet
    for path in root_dir.glob('**/*'):
        # Vérifier si c'est un fichier avec une extension pertinente
        if path.is_file() and path.suffix in extensions:
            # Vérifier si le fichier n'est pas dans un répertoire exclu
            if not any(exclude_dir in str(path) for exclude_dir in exclude_dirs):
                try:
                    # Lire le contenu du fichier
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # Vérifier si le tag est présent
                        if '[TEST_AUTH_JWT]' in content:
                            auth_test_files.append(path)
                except UnicodeDecodeError:
                    # Ignorer les fichiers binaires
                    pass
    
    # Afficher les fichiers trouvés
    if auth_test_files:
        print(f"[TEST_AUTH_JWT] {len(auth_test_files)} fichiers trouvés :")
        for file_path in auth_test_files:
            # Afficher le chemin relatif à la racine du projet
            rel_path = file_path.relative_to(root_dir)
            print(f"  - {rel_path}")
    else:
        print("[TEST_AUTH_JWT] Aucun fichier lié aux tests d'authentification trouvé.")
    
    return auth_test_files


if __name__ == "__main__":
    find_auth_test_files() 
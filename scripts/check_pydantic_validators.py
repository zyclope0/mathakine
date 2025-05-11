#!/usr/bin/env python
"""
Script pour vérifier si tous les modèles Pydantic utilisent le nouveau style de validation (v2).
Ce script recherche les anciennes utilisations comme @validator ou class Config: orm_mode = True.

Usage:
    python scripts/check_pydantic_validators.py
"""

import os
import re
import sys
from colorama import init, Fore, Style

# Initialiser colorama pour les messages colorés
init()



def print_success(message):
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")



def print_warning(message):
    print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")



def print_error(message):
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")



def check_file(file_path):
    """Vérifie un fichier pour les anciens styles Pydantic."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = []
    line_number = 1

    # Rechercher les importations de validator (sans field_validator)
    if re.search(r'from\s+pydantic\s+import\s+.*validator.*(?<!field_validator)', content):
        issues.append((line_number, "Importation de 'validator' au lieu de 'field_validator'"))

    # Rechercher les utilisations de @validator
    for match in re.finditer(r'@validator\(', content):
        line_number = content[:match.start()].count('\n') + 1
        issues.append((line_number, "Utilisation de '@validator' au lieu de '@field_validator'"))

    # Rechercher les class Config: orm_mode = True
    for match in re.finditer(r'class\s+Config.*?orm_mode\s*=\s*True', content, re.DOTALL):
        line_number = content[:match.start()].count('\n') + 1
        issues.append((line_number, "Utilisation de 'class Config: orm_mode = True' au lieu de 'model_config = ConfigDict(from_attributes=True)'"))

    return issues



def find_python_files(directory, exclude_dirs=None):
    """Recherche tous les fichiers Python dans le répertoire, en excluant certains dossiers."""
    if exclude_dirs is None:
        exclude_dirs = ['venv', '.git', '__pycache__', 'node_modules']

    for root, dirs, files in os.walk(directory):
        # Exclure certains dossiers
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith('.py'):
                yield os.path.join(root, file)



def main():
    print("Vérification des modèles Pydantic pour le style v2...")

    # Déterminer le répertoire racine du projet
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # Rechercher tous les fichiers Python
    issues_found = False
    files_checked = 0
    files_with_issues = 0

    for file_path in find_python_files(project_root):
        files_checked += 1

        # Vérifier seulement les fichiers qui pourraient contenir des modèles Pydantic
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'from pydantic import' not in content and 'import pydantic' not in content:
                continue

        # Vérifier le fichier
        issues = check_file(file_path)

        if issues:
            issues_found = True
            files_with_issues += 1
            print_warning(f"\nProblèmes dans {os.path.relpath(file_path, project_root)}:")
            for line, issue in issues:
                print_error(f"  • Ligne {line}: {issue}")

    print(f"\n{files_checked} fichiers Python vérifiés.")

    if issues_found:
        print_warning(f"{files_with_issues} fichiers contiennent encore des éléments de style Pydantic v1.")
        print("Veuillez consulter docs/PYDANTIC_V2_MIGRATION.md pour savoir comment les mettre à jour.")
        sys.exit(1)
    else:
        print_success("Tous les modèles Pydantic utilisent le style v2. 🎉")
        sys.exit(0)

if __name__ == "__main__":
    main()

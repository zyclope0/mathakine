#!/usr/bin/env python
"""
Script pour corriger les problèmes de style plus avancés dans les fichiers Python.
Ce script corrige:
- L'espacement entre les définitions de fonctions et classes (2 lignes vides)
- Les lignes trop longues en les découpant lorsque possible

Usage: python scripts/fix_advanced_style.py [chemin_fichier_ou_dossier]
"""

import os
import sys
import re
from pathlib import Path

# Couleurs pour la console
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_status(message, status):
    """Affiche un message de statut avec une couleur appropriée."""
    if status == "OK":
        color = GREEN
        status_text = f"{BOLD}{GREEN}[OK]{RESET}"
    elif status == "WARNING":
        color = YELLOW
        status_text = f"{BOLD}{YELLOW}[ATTENTION]{RESET}"
    elif status == "ERROR":
        color = RED
        status_text = f"{BOLD}{RED}[ERREUR]{RESET}"
    else:
        color = BLUE
        status_text = f"{BOLD}{BLUE}[INFO]{RESET}"

    print(f"{status_text} {message}")


def fix_line_breaks(content):
    """Ajoute des sauts de ligne pour certains motifs courants."""
    # Détecter les longues chaînes de caractères avec + et les formater
    long_string_pattern = r'(\".*?\"\s*\+\s*\".*?\".*?)$'
    content = re.sub(long_string_pattern, r'\1\n', content, flags=re.MULTILINE)
    return content


def fix_function_spacing(content):
    """Corrige l'espacement entre les définitions de fonction (2 lignes vides)."""
    # Détecter les définitions de fonction/classe, s'assurer qu'il y a 2 lignes vides avant
    # Note: Ceci est une approximation simple et peut nécessiter des améliorations
    func_pattern = r'(\n)[ \t]*(?:def|class)\s+'
    # Remplacer par deux lignes vides (mais pas au début du fichier)
    content = re.sub(r'(?<!\A)' + func_pattern, r'\n\n\1', content)
    return content


def fix_python_file(file_path):
    """Corrige les problèmes de style avancés dans un fichier Python."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Tracking des changements
        original_content = content

        # Appliquer les corrections avancées
        content = fix_function_spacing(content)
        content = fix_line_breaks(content)

        # Vérifier si des modifications ont été apportées
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print_status(f"Problèmes de style avancés corrigés: {file_path}", "OK")
            return True
        else:
            print_status(f"Aucun problème de style avancé trouvé: {file_path}", "INFO")
            return False
    except Exception as e:
        print_status(f"Erreur lors de la correction du fichier {file_path}: {str(e)}", "ERROR")
        return False


def process_path(path):
    """Traite un chemin (fichier ou dossier) pour corriger les problèmes de style avancés."""
    path = Path(path)

    if path.is_file() and path.suffix == '.py':
        return fix_python_file(path)

    if path.is_dir():
        # Exclure certains dossiers
        excluded_dirs = {'venv', 'env', '.git', '__pycache__', 'archive', 'archives'}

        fixed_count = 0
        for root, dirs, files in os.walk(path):
            # Filtrer les dossiers exclus
            dirs[:] = [d for d in dirs if d not in excluded_dirs]

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    if fix_python_file(file_path):
                        fixed_count += 1

        return fixed_count > 0

    print_status(f"Le chemin spécifié n'est pas un fichier Python ou un dossier: {path}", "WARNING")
    return False


def main():
    """Fonction principale."""
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        # Par défaut, traiter le répertoire courant
        path = os.getcwd()

    print(f"{BOLD}{BLUE}=== Correction automatique des problèmes de style avancés ==={RESET}")
    success = process_path(path)

    if success:
        print(f"\n{BOLD}{GREEN}=== Les problèmes de style avancés ont été corrigés avec succès ! ==={RESET}")
        return 0
    else:
        print(f"\n{BOLD}{YELLOW}=== Aucune correction n'a été nécessaire ou des erreurs sont survenues. ==={RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
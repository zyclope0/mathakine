#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour vérifier la cohérence des variables d'environnement utilisées dans le projet.
Ce script analyse les fichiers du projet à la recherche de variables d'environnement
et vérifie qu'elles respectent les conventions de nommage.
"""

import os
import re
import sys
from pathlib import Path
from colorama import init, Fore, Style

# Initialiser colorama pour les couleurs dans la console
try:
    init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

# Obtenir le chemin du projet
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Définir les conventions de nommage
PREFIX = "MATH_TRAINER_"
# Exception pour les variables standard comme OPENAI_API_KEY
EXCEPTIONS = ["OPENAI_API_KEY", "DATABASE_URL"]
ENV_PATTERN = re.compile(r'os\.environ\.get\(["\']([A-Za-z0-9_]+)["\']')

# Extensions de fichiers à analyser
FILE_EXTENSIONS = ['.py', '.bat', '.ps1', '.md']




def color_text(text, color):
    """Ajoute de la couleur au texte si colorama est disponible"""
    if HAS_COLOR:
        return f"{color}{text}{Style.RESET_ALL}"
    return text




def find_env_vars_in_file(file_path):
    """Trouve toutes les variables d'environnement utilisées dans un fichier"""
    env_vars = set()

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        try:
            content = f.read()
            # Rechercher les patterns comme os.environ.get('VAR_NAME')
            matches = ENV_PATTERN.findall(content)
            env_vars.update(matches)

            # Rechercher les patterns comme %VAR_NAME% (pour les fichiers batch)
            if file_path.suffix == '.bat':
                batch_vars = re.findall(r'%([A-Za-z0-9_]+)%', content)
                env_vars.update(batch_vars)

            # Rechercher les patterns comme $env:VAR_NAME (pour les fichiers PowerShell)
            if file_path.suffix == '.ps1':
                ps_vars = re.findall(r'\$env:([A-Za-z0-9_]+)', content)
                env_vars.update(ps_vars)

        except UnicodeDecodeError:
            print(f"Erreur de décodage pour {file_path}")

    return env_vars




def check_file(file_path):
    """Vérifie les variables d'environnement dans un fichier"""
    env_vars = find_env_vars_in_file(file_path)
    if not env_vars:
        return [], []

    # Filtrer les variables qui ne respectent pas les conventions
    non_compliant = [var for var in env_vars if not var.startswith(PREFIX) and var not in EXCEPTIONS]

    # Filtrer les variables qui respectent les conventions
    compliant = [var for var in env_vars if var.startswith(PREFIX) or var in EXCEPTIONS]

    return compliant, non_compliant




def scan_directory(directory):
    """Parcourt récursivement un répertoire et vérifie les variables d'environnement"""
    all_compliant = set()
    all_non_compliant = set()

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in FILE_EXTENSIONS:
                compliant, non_compliant = check_file(file_path)
                if compliant:
                    all_compliant.update(compliant)
                if non_compliant:
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    print(f"\nFichier: {color_text(rel_path, Fore.CYAN)}")
                    for var in non_compliant:
                        print(f"  ❌ Variable non conforme: {color_text(var, Fore.RED)}")
                        print(f"     → Suggestion: {color_text(PREFIX + var, Fore.GREEN)}")
                    all_non_compliant.update(non_compliant)

    return all_compliant, all_non_compliant




def check_env_example():
    """Vérifie que toutes les variables utilisées sont documentées dans env.example"""
    env_example_path = SCRIPT_DIR / "env.example"
    if not env_example_path.exists():
        print(f"\n⚠️ {color_text('Le fichier env.example est introuvable!', Fore.YELLOW)}")
        return set()

    documented_vars = set()
    with open(env_example_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                var_name = line.split('=')[0]
                documented_vars.add(var_name)

    return documented_vars




def main():
    print(f"\n{color_text('Vérification des variables d\'environnement...', Fore.CYAN)}")

    # Scanner le répertoire du projet
    print(f"\nAnalyse du répertoire: {PROJECT_ROOT}")
    all_compliant, all_non_compliant = scan_directory(PROJECT_ROOT)

    # Vérifier les variables documentées
    documented_vars = check_env_example()

    # Trouver les variables utilisées mais non documentées
    undocumented = all_compliant - documented_vars

    # Trouver les variables documentées mais non utilisées
    unused = documented_vars - all_compliant

    # Afficher le résumé
    print(f"\n{color_text('Résumé:', Fore.CYAN)}")
    print(f"  Variables conformes trouvées: {color_text(len(all_compliant), Fore.GREEN)}")
    print(f"  Variables non conformes trouvées: {color_text(len(all_non_compliant), Fore.RED)}")
    print(f"  Variables documentées dans env.example: {color_text(len(documented_vars)
        , Fore.GREEN)}")

    if undocumented:
        print(f"\n{color_text('Variables utilisées mais non documentées:', Fore.YELLOW)}")
        for var in sorted(undocumented):
            print(f"  ⚠️ {var}")

    if unused:
        print(f"\n{color_text('Variables documentées mais non utilisées:', Fore.YELLOW)}")
        for var in sorted(unused):
            print(f"  ℹ️ {var}")

    if all_non_compliant:
        print(f"\n{color_text('Actions recommandées:', Fore.CYAN)}")
        print("  1. Renommer les variables non conformes pour suivre la convention de nommage")
        print("  2. Documenter toutes les variables utilisées dans le fichier env.example")
        return 1
    elif undocumented:
        print(f"\n{color_text('Actions recommandées:', Fore.CYAN)}")
        print("  1. Documenter toutes les variables utilisées dans le fichier env.example")
        return 0
    else:
        print(f"\n{color_text('Toutes les variables d\'environnement sont conformes et documentées. 👍'
            , Fore.GREEN)}")
        return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""
Script utilitaire pour vérifier la santé du projet.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

# Ajouter le répertoire parent au path pour pouvoir importer les modules du projet
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Couleurs pour la console
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"




def check_tool_installed(tool_name):
    """Vérifie si un outil est installé dans l'environnement Python actuel."""
    try:
        importlib.util.find_spec(tool_name)
        return True
    except ImportError:
        return False




def print_status(message, status, details=None):
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

    if details:
        lines = details.strip().split("\n")
        for line in lines:
            print(f"     {color}│{RESET} {line}")
        print(f"     {color}└{'─' * 50}{RESET}")




def check_code_style():
    """Vérifie le style de code avec pycodestyle."""
    print(f"\n{BOLD}=== Vérification du style de code ==={RESET}")

    if not check_tool_installed("pycodestyle"):
        print_status("L'outil pycodestyle n'est pas installé", "ERROR")
        return False

    pyfiles = list(BASE_DIR.glob("**/*.py"))
    pyfiles = [f for f in pyfiles if "venv" not in str(f) and "archive" not in str(f)]

    all_good = True
    for pyfile in pyfiles[:10]:  # Limiter aux 10 premiers fichiers pour cet exemple
        rel_path = pyfile.relative_to(BASE_DIR)
        result = subprocess.run(
            ["pycodestyle", str(pyfile)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print_status(f"Style vérifié: {rel_path}", "OK")
        else:
            all_good = False
            print_status(f"Problèmes de style: {rel_path}", "WARNING", result.stdout)

    return all_good




def check_syntax():
    """Vérifie la syntaxe des fichiers Python."""
    print(f"\n{BOLD}=== Vérification de la syntaxe Python ==={RESET}")

    pyfiles = list(BASE_DIR.glob("**/*.py"))
    pyfiles = [f for f in pyfiles if "venv" not in str(f) and "archive" not in str(f)]

    all_good = True
    for pyfile in pyfiles[:10]:  # Limiter aux 10 premiers fichiers pour cet exemple
        rel_path = pyfile.relative_to(BASE_DIR)
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(pyfile)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print_status(f"Syntaxe correcte: {rel_path}", "OK")
        else:
            all_good = False
            print_status(f"Erreur de syntaxe: {rel_path}", "ERROR", result.stderr)

    return all_good




def check_imports():
    """Vérifie que les imports sont fonctionnels."""
    print(f"\n{BOLD}=== Vérification des imports ==={RESET}")

    main_modules = ["enhanced_server", "mathakine_cli"]
    all_good = True

    for module in main_modules:
        try:
            if os.path.exists(f"{module}.py"):
                # Import dynamique du module avec exec()
                cmd = f"import {module}"
                try:
                    exec(cmd)
                    print_status(f"Import OK: {module}", "OK")
                except Exception as e:
                    all_good = False
                    print_status(f"Erreur lors de l'import de {module}", "ERROR", str(e))
        except Exception as e:
            all_good = False
            print_status(f"Erreur lors de la vérification de {module}", "ERROR", str(e))

    return all_good




def check_dependencies():
    """Vérifie les dépendances du projet."""
    print(f"\n{BOLD}=== Vérification des dépendances ==={RESET}")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        capture_output=True,
        text=True
    )

    if "No broken requirements found" in result.stdout:
        print_status("Toutes les dépendances sont compatibles", "OK")
        return True
    else:
        print_status("Problèmes de dépendances détectés", "WARNING", result.stdout)
        return False




def main():
    """Fonction principale."""
    print(f"{BOLD}{BLUE}=== Vérification de la santé du projet Mathakine ==={RESET}")

    results = []
    results.append(("Style de code", check_code_style()))
    results.append(("Syntaxe Python", check_syntax()))
    results.append(("Imports", check_imports()))
    results.append(("Dépendances", check_dependencies()))

    print(f"\n{BOLD}{BLUE}=== Résumé des vérifications ==={RESET}")

    all_good = True
    for name, result in results:
        if result:
            print_status(name, "OK")
        else:
            all_good = False
            print_status(name, "WARNING")

    if all_good:
        print(f"\n{BOLD}{GREEN}=== Tous les contrôles sont passés avec succès ! ==={RESET}")
        return 0
    else:
        print(f"\n{BOLD}{YELLOW}=== Certaines vérifications ont échoué. Voir les détails ci-dessus. ==={RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

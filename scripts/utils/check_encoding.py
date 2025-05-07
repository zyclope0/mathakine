#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour vérifier l'encodage des fichiers du projet.
Ce script analyse les fichiers du projet pour identifier ceux qui ont des problèmes
d'encodage des caractères accentués.
"""

import os
import re
import sys
import chardet
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

# Extensions de fichiers à analyser
TEXT_EXTENSIONS = ['.py', '.bat', '.ps1', '.md', '.txt', '.html', '.css', '.js', '.json', '.env']

# Caractères accentués courants en français
ACCENTED_CHARS = "éèêëàâäùûüçôöîïÉÈÊËÀÂÄÙÛÜÇÔÖÎÏ"

# Modèle pour trouver des caractères accentués mal encodés
ENCODING_ISSUE_PATTERN = re.compile(r'[���������������������]')


def color_text(text, color):
    """Ajoute de la couleur au texte si colorama est disponible"""
    if HAS_COLOR:
        return f"{color}{text}{Style.RESET_ALL}"
    return text


def detect_encoding(file_path):
    """Détecte l'encodage d'un fichier"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
    return result['encoding'], result['confidence']


def has_encoding_issues(file_path, encoding):
    """Vérifie si un fichier a des problèmes d'encodage des caractères accentués"""
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()
            
            # Vérifier s'il y a des caractères accentués
            has_accents = any(c in content for c in ACCENTED_CHARS)
            
            # Vérifier s'il y a des caractères mal encodés
            has_issues = bool(ENCODING_ISSUE_PATTERN.search(content))
            
            return has_accents, has_issues, content
            
    except UnicodeDecodeError:
        return False, True, ""


def check_file_encoding(file_path):
    """Vérifie l'encodage d'un fichier et identifie les problèmes potentiels"""
    encoding, confidence = detect_encoding(file_path)
    
    # Si l'encodage n'est pas UTF-8 ou a une faible confiance, signaler le fichier
    needs_attention = encoding != 'utf-8' or confidence < 0.9
    
    # Vérifier s'il y a des problèmes d'encodage des caractères accentués
    has_accents, has_issues, content = has_encoding_issues(file_path, encoding)
    
    # Si le fichier a des caractères accentués et des problèmes d'encodage, il nécessite une correction
    needs_fix = has_accents and has_issues
    
    return {
        'encoding': encoding,
        'confidence': confidence,
        'has_accents': has_accents,
        'has_issues': has_issues,
        'needs_attention': needs_attention or needs_fix,
        'needs_fix': needs_fix,
        'content': content if needs_fix else None
    }


def scan_directory(directory):
    """Parcourt récursivement un répertoire et vérifie l'encodage des fichiers"""
    needs_attention = []
    needs_fix = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in TEXT_EXTENSIONS:
                try:
                    result = check_file_encoding(file_path)
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    
                    if result['needs_fix']:
                        needs_fix.append((rel_path, result))
                    elif result['needs_attention']:
                        needs_attention.append((rel_path, result))
                        
                except Exception as e:
                    print(f"Erreur lors de l'analyse de {file_path}: {e}")
    
    return needs_attention, needs_fix


def print_results(needs_attention, needs_fix):
    """Affiche les résultats de l'analyse"""
    print(f"\n{color_text('Résumé de l\'analyse d\'encodage:', Fore.CYAN)}")
    print(f"  Fichiers nécessitant une attention: {color_text(len(needs_attention), Fore.YELLOW)}")
    print(f"  Fichiers nécessitant une correction d'encodage: {color_text(len(needs_fix), Fore.RED)}")
    
    if needs_attention:
        print(f"\n{color_text('Fichiers nécessitant une attention (encodage non-UTF-8 ou faible confiance):', Fore.YELLOW)}")
        for rel_path, result in needs_attention:
            print(f"  • {rel_path}")
            print(f"    → Encodage détecté: {result['encoding']} (confiance: {result['confidence']:.2f})")
    
    if needs_fix:
        print(f"\n{color_text('Fichiers nécessitant une correction d\'encodage (caractères accentués mal encodés):', Fore.RED)}")
        for rel_path, result in needs_fix:
            print(f"  • {rel_path}")
            print(f"    → Encodage détecté: {result['encoding']} (confiance: {result['confidence']:.2f})")


def fix_encoding(file_path, original_encoding):
    """Tente de corriger l'encodage d'un fichier en le convertissant en UTF-8"""
    try:
        # Lire le contenu avec l'encodage détecté
        with open(file_path, 'r', encoding=original_encoding, errors='replace') as f:
            content = f.read()
        
        # Réécrire le contenu en UTF-8
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return True
    except Exception as e:
        print(f"Erreur lors de la correction de l'encodage de {file_path}: {e}")
        return False


def main():
    # Vérifier si chardet est installé
    try:
        import chardet
    except ImportError:
        print(f"{color_text('Le module chardet est requis.', Fore.RED)} Installation en cours...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "chardet"])
        import chardet
    
    print(f"\n{color_text('Analyse de l\'encodage des fichiers...', Fore.CYAN)}")
    print(f"Répertoire: {PROJECT_ROOT}")
    
    needs_attention, needs_fix = scan_directory(PROJECT_ROOT)
    print_results(needs_attention, needs_fix)
    
    # Proposer de corriger les fichiers
    if needs_fix:
        print(f"\n{color_text('Actions recommandées:', Fore.CYAN)}")
        print("  1. Corriger l'encodage des fichiers signalés en les convertissant en UTF-8")
        print("  2. Utiliser le script fix_direct.py pour les fichiers avec des caractères accentués")
        
        answer = input("\nVoulez-vous tenter de corriger automatiquement les fichiers ? (o/n): ")
        if answer.lower() == 'o':
            success_count = 0
            for rel_path, result in needs_fix:
                file_path = PROJECT_ROOT / rel_path
                print(f"Correction de {rel_path}... ", end="")
                if fix_encoding(file_path, result['encoding']):
                    success_count += 1
                    print(color_text("OK", Fore.GREEN))
                else:
                    print(color_text("ÉCHEC", Fore.RED))
            
            print(f"\n{success_count}/{len(needs_fix)} fichiers corrigés avec succès.")
            
            # Recommandations pour les fichiers non corrigés
            if success_count < len(needs_fix):
                print(f"\nPour les fichiers restants, utilisez le script fix_direct.py :")
                print("  python scripts/utils/fix_direct.py")
        
        return 1 if len(needs_fix) > 0 else 0
    else:
        print(f"\n{color_text('Tous les fichiers ont un encodage UTF-8 correct. 👍', Fore.GREEN)}")
        return 0


if __name__ == "__main__":
    sys.exit(main()) 
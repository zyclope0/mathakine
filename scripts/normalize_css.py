#!/usr/bin/env python
"""
Script pour normaliser les styles CSS dans les fichiers HTML du projet Mathakine.
Ce script remplace les styles en ligne (inline) par des classes CSS appropriées.
"""

import os
import re
from pathlib import Path
import sys

# Répertoire des templates à traiter
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Mappings des styles en ligne vers des classes CSS
STYLE_MAPPING = {
    "display: none;": "d-none",
    "display: block;": "d-block",
    "display: flex;": "d-flex",
    "display: flex; align-items: center; justify-content: space-between;": "flex-between",
    "text-align: center;": "text-center",
    "text-align: left;": "text-left",
    "text-align: right;": "text-right",
    "margin-bottom: 20px;": "mb-3",
    "margin-top: 20px;": "mt-3",
    "padding: 20px;": "p-3",
    "width: 0%;": "progress-bar-value",
    "font-size: 3rem; color: var(--sw-red); margin-bottom: 15px;": "error-icon",
}

# Fonction pour remplacer les styles en ligne par des classes CSS
def replace_inline_styles(content):
    """Remplace les styles en ligne par des classes CSS appropriées."""
    for style, css_class in STYLE_MAPPING.items():
        # Recherche de style="STYLE" et remplace par class="CSS_CLASS"
        pattern = f'style="{re.escape(style)}"'
        
        # Si un élément a déjà une classe, on ajoute notre classe
        content = re.sub(
            r'class="([^"]+)"([^>]*?)' + pattern,
            fr'class="\1 {css_class}"\2',
            content
        )
        
        # Si un élément n'a pas de classe, on en crée une
        content = re.sub(
            r'(<[^>]*?)' + pattern + r'([^>]*?>)',
            fr'\1class="{css_class}"\2',
            content
        )
    
    return content

# Fonction pour nettoyer les styles combinés déjà traités
def clean_combined_styles(content):
    """Nettoie les styles en ligne qui peuvent rester après le traitement initial."""
    # Recherche les attributs style qui ne contiennent qu'une partie des styles mappés
    for style, css_class in STYLE_MAPPING.items():
        partial_styles = style.split(';')
        for partial in partial_styles:
            if partial and not partial.isspace():
                partial = partial.strip() + ";"
                pattern = f'style="[^"]*{re.escape(partial)}[^"]*"'
                
                # Vérifie si l'élément a déjà la classe
                content = re.sub(
                    r'class="([^"]*?)(?!\b' + re.escape(css_class) + r'\b)([^"]*)"([^>]*?)' + pattern,
                    fr'class="\1\2 {css_class}"\3',
                    content
                )
    
    return content

# Fonction principale pour traiter les fichiers
def process_files():
    """Traite tous les fichiers HTML dans le répertoire des templates."""
    count = 0
    for file in TEMPLATES_DIR.glob("*.html"):
        print(f"Traitement du fichier: {file}")
        
        # Lecture du contenu
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remplacement des styles en ligne
        new_content = replace_inline_styles(content)
        
        # Nettoyer les styles combinés
        new_content = clean_combined_styles(new_content)
        
        # Si le contenu a été modifié, écrire les changements
        if content != new_content:
            with open(file, "w", encoding="utf-8") as f:
                f.write(new_content)
            count += 1
            print(f"  ✓ Styles normalisés dans {file}")
        else:
            print(f"  ✓ Aucune modification nécessaire dans {file}")
    
    print(f"\nTerminé! {count} fichiers ont été mis à jour.")

if __name__ == "__main__":
    print("=== Normalisation des styles CSS dans les fichiers HTML ===")
    process_files()
    sys.exit(0) 
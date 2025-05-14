#!/usr/bin/env python
"""
Script pour vérifier que les fichiers statiques et templates sont correctement configurés.
"""

import os
import sys
from pathlib import Path

def check_directory(path, name, required_files=None):
    """Vérifie qu'un répertoire existe et contient les fichiers requis."""
    print(f"Vérification du répertoire {name}...")
    
    if not os.path.exists(path):
        print(f"❌ Le répertoire {name} n'existe pas: {path}")
        return False
    
    print(f"✅ Le répertoire {name} existe")
    
    if required_files:
        missing_files = []
        for file in required_files:
            file_path = os.path.join(path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Fichiers manquants dans {name}: {', '.join(missing_files)}")
            return False
        else:
            print(f"✅ Tous les fichiers requis sont présents dans {name}")
    
    return True

def check_static_files():
    """Vérifie que les fichiers statiques sont correctement configurés."""
    base_dir = Path(__file__).parent.absolute()
    static_dir = os.path.join(base_dir, "static")
    
    static_files = [
        "style.css",
        "space-theme.css",
        "home-styles.css"
    ]
    
    return check_directory(static_dir, "static", static_files)

def check_templates():
    """Vérifie que les templates sont correctement configurés."""
    base_dir = Path(__file__).parent.absolute()
    templates_dir = os.path.join(base_dir, "templates")
    
    template_files = [
        "base.html",
        "home.html",
        "exercises.html",
        "dashboard.html"
    ]
    
    return check_directory(templates_dir, "templates", template_files)

def check_static_img():
    """Vérifie que les images statiques sont correctement configurées."""
    base_dir = Path(__file__).parent.absolute()
    img_dir = os.path.join(base_dir, "static", "img")
    
    img_files = [
        "mathakine-logo.svg",
        "favicon.svg"
    ]
    
    return check_directory(img_dir, "static/img", img_files)

def check_fastapi_import():
    """Vérifie que les imports FastAPI nécessaires sont disponibles."""
    print("Vérification des imports FastAPI...")
    
    try:
        from fastapi.staticfiles import StaticFiles
        from fastapi.templating import Jinja2Templates
        print("✅ Les imports FastAPI pour les fichiers statiques et les templates sont disponibles")
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import FastAPI: {e}")
        return False

def main():
    """Fonction principale."""
    print("Vérification de la configuration des fichiers statiques et templates...")
    
    # Vérifier les répertoires et fichiers
    static_ok = check_static_files()
    templates_ok = check_templates()
    img_ok = check_static_img()
    imports_ok = check_fastapi_import()
    
    # Résumé
    print("\nRésumé de la vérification:")
    print(f"- Fichiers statiques: {'✅' if static_ok else '❌'}")
    print(f"- Templates: {'✅' if templates_ok else '❌'}")
    print(f"- Images: {'✅' if img_ok else '❌'}")
    print(f"- Imports FastAPI: {'✅' if imports_ok else '❌'}")
    
    if static_ok and templates_ok and img_ok and imports_ok:
        print("\n✅ Tout est correctement configuré!")
        return 0
    else:
        print("\n❌ Des problèmes ont été détectés. Veuillez corriger les erreurs avant de continuer.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
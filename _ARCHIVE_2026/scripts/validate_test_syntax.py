#!/usr/bin/env python3
"""
Script de validation de la syntaxe des tests créés pour la Phase 4.
Vérifie que les fichiers de tests sont syntaxiquement corrects et que les imports sont valides.
"""
import ast
import sys
from pathlib import Path

def validate_python_file(file_path: Path) -> tuple[bool, list[str]]:
    """Valide la syntaxe d'un fichier Python et vérifie les imports."""
    errors = []
    
    try:
        # Lire le fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier la syntaxe
        try:
            ast.parse(content, filename=str(file_path))
        except SyntaxError as syntax_error:
            errors.append(f"Erreur de syntaxe ligne {syntax_error.lineno}: {syntax_error.msg}")
            return False, errors
        
        # Vérifier les imports critiques
        if 'from app.main import app' in content:
            # Vérifier que app.main existe
            try:
                import app.main
            except ImportError as import_error:
                errors.append(f"Import app.main échoué: {import_error}")
        
        if 'from fastapi.testclient import TestClient' in content:
            try:
                from fastapi.testclient import TestClient
            except ImportError as import_error:
                errors.append(f"Import TestClient échoué: {import_error}")
        
        if 'import pytest' in content:
            try:
                import pytest
            except ImportError as import_error:
                errors.append(f"Import pytest échoué: {import_error}")
        
        return True, errors
        
    except Exception as file_error:
        errors.append(f"Erreur lors de la lecture du fichier: {file_error}")
        return False, errors

def main():
    """Valide tous les fichiers de tests de la Phase 4."""
    test_files = [
        Path("tests/integration/test_auth_no_fallback.py"),
        Path("tests/integration/test_auth_cookies_only.py"),
        Path("tests/integration/test_sse_auth.py"),
    ]
    
    print("=" * 60)
    print("VALIDATION DES TESTS - PHASE 4")
    print("=" * 60)
    print()
    
    all_valid = True
    
    for test_file in test_files:
        print(f"Vérification de {test_file.name}...")
        
        if not test_file.exists():
            print(f"  ❌ Fichier introuvable: {test_file}")
            all_valid = False
            continue
        
        is_valid, errors = validate_python_file(test_file)
        
        if is_valid and not errors:
            print(f"  ✅ Syntaxe valide")
        else:
            print(f"  ❌ Erreurs détectées:")
            for error in errors:
                print(f"     - {error}")
            all_valid = False
        
        print()
    
    print("=" * 60)
    if all_valid:
        print("✅ TOUS LES TESTS SONT VALIDES")
        return 0
    else:
        print("❌ CERTAINS TESTS ONT DES ERREURS")
        return 1

if __name__ == "__main__":
    sys.exit(main())


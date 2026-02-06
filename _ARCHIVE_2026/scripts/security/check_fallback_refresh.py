#!/usr/bin/env python3
"""
Script pour vérifier que le fallback refresh token a été supprimé.
Utilisé pour valider la correction SEC-1.2.
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_fallback_refresh():
    """Vérifie que le fallback refresh token n'existe plus"""
    issues = []
    
    file_to_check = "server/handlers/auth_handlers.py"
    full_path = project_root / file_to_check
    
    if not full_path.exists():
        print(f"❌ Fichier {file_to_check} non trouvé")
        return issues
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns à détecter (fallback)
    fallback_patterns = [
        (r'verify_exp.*False', 'verify_exp=False détecté (fallback)'),
        (r'FALLBACK.*refresh', 'Commentaire FALLBACK détecté'),
        (r'fallback.*refresh.*token', 'Code fallback refresh token détecté'),
        (r'access_token_fallback', 'Variable access_token_fallback détectée'),
    ]
    
    for pattern, description in fallback_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            # Trouver le numéro de ligne
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                'file': file_to_check,
                'line': line_num,
                'description': description,
                'content': match.group(0)
            })
    
    return issues

def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("🔍 VÉRIFICATION DU FALLBACK REFRESH TOKEN")
    print("=" * 80)
    print()
    
    issues = check_fallback_refresh()
    
    if issues:
        print(f"❌ {len(issues)} problème(s) détecté(s):\n")
        for issue in issues:
            print(f"  📄 {issue['file']}:{issue['line']}")
            print(f"     {issue['description']}")
            print(f"     Code: {issue['content']}")
            print()
        print("⚠️  Le fallback refresh token doit être supprimé (SEC-1.2)")
        return 1
    else:
        print("✅ Aucun fallback refresh token détecté")
        print("   Le code est sécurisé")
        return 0

if __name__ == "__main__":
    sys.exit(main())


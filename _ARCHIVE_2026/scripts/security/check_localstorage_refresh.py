#!/usr/bin/env python3
"""
Script pour vérifier qu'aucun refresh_token n'est stocké dans localStorage.
Utilisé pour valider la correction SEC-1.3.
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

def check_localstorage_refresh():
    """Vérifie les fichiers frontend pour localStorage refresh_token"""
    issues = []
    
    files_to_check = [
        "frontend/lib/api/client.ts",
        "frontend/hooks/useAuth.ts"
    ]
    
    for file_path in files_to_check:
        full_path = project_root / file_path
        if not full_path.exists():
            continue
        
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            # Détecter localStorage avec refresh_token
            if re.search(r'localStorage.*refresh_token|refresh_token.*localStorage', line, re.IGNORECASE):
                # Vérifier si c'est un commentaire
                if not line.strip().startswith('//'):
                    issues.append({
                        'file': file_path,
                        'line': line_num,
                        'description': 'localStorage utilisé pour refresh_token',
                        'content': line.strip()
                    })
    
    return issues

def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("🔍 VÉRIFICATION LOCALSTORAGE REFRESH_TOKEN")
    print("=" * 80)
    print()
    
    issues = check_localstorage_refresh()
    
    if issues:
        print(f"❌ {len(issues)} problème(s) détecté(s):\n")
        for issue in issues:
            print(f"  📄 {issue['file']}:{issue['line']}")
            print(f"     {issue['description']}")
            print(f"     Code: {issue['content'][:80]}...")
            print()
        print("⚠️  Le refresh_token ne doit pas être stocké dans localStorage (SEC-1.3)")
        print("   Utiliser uniquement les cookies HTTP-only")
        return 1
    else:
        print("✅ Aucun refresh_token dans localStorage détecté")
        print("   Le code utilise uniquement les cookies HTTP-only")
        return 0

if __name__ == "__main__":
    sys.exit(main())


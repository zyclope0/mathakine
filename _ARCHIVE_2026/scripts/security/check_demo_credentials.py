#!/usr/bin/env python3
"""
Script pour vérifier que les credentials démo sont masqués en production.
Utilisé pour valider la correction SEC-1.4.
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

def check_demo_credentials():
    """Vérifie que les credentials démo sont conditionnés par DEMO_MODE"""
    issues = []
    
    file_to_check = "frontend/app/login/page.tsx"
    full_path = project_root / file_to_check
    
    if not full_path.exists():
        print(f"❌ Fichier {file_to_check} non trouvé")
        return issues
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si les credentials sont affichés sans condition
    if re.search(r'ObiWan.*HelloThere123', content, re.IGNORECASE):
        # Vérifier si c'est conditionné par DEMO_MODE
        if 'NEXT_PUBLIC_DEMO_MODE' not in content and 'DEMO_MODE' not in content:
            issues.append({
                'file': file_to_check,
                'description': 'Credentials démo affichés sans condition DEMO_MODE',
                'recommendation': 'Ajouter NEXT_PUBLIC_DEMO_MODE pour masquer en production'
            })
    
    return issues

def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("🔍 VÉRIFICATION DES CREDENTIALS DÉMO")
    print("=" * 80)
    print()
    
    issues = check_demo_credentials()
    
    if issues:
        print(f"❌ {len(issues)} problème(s) détecté(s):\n")
        for issue in issues:
            print(f"  📄 {issue['file']}")
            print(f"     {issue['description']}")
            print(f"     💡 {issue['recommendation']}")
            print()
        return 1
    else:
        print("✅ Les credentials démo sont conditionnés par DEMO_MODE")
        print("   Ils seront masqués en production")
        return 0

if __name__ == "__main__":
    sys.exit(main())


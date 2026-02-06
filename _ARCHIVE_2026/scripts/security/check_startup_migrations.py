#!/usr/bin/env python3
"""
Script pour vérifier que les migrations au boot sont conditionnées.
Utilisé pour valider la correction SEC-2.2.
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_startup_migrations():
    """Vérifie que les migrations au boot sont conditionnées"""
    issues = []
    
    file_to_check = "server/app.py"
    full_path = project_root / file_to_check
    
    if not full_path.exists():
        print(f"❌ Fichier {file_to_check} non trouvé")
        return issues
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si init_database() est appelé sans condition
    if 'init_database()' in content:
        # Vérifier si c'est conditionné par RUN_STARTUP_MIGRATIONS
        if 'RUN_STARTUP_MIGRATIONS' not in content:
            issues.append({
                'file': file_to_check,
                'description': 'init_database() appelé sans condition RUN_STARTUP_MIGRATIONS',
                'recommendation': 'Conditionner init_database() avec RUN_STARTUP_MIGRATIONS'
            })
    
    # Vérifier si apply_migration() est appelé sans condition
    if 'apply_migration()' in content:
        if 'RUN_STARTUP_MIGRATIONS' not in content:
            issues.append({
                'file': file_to_check,
                'description': 'apply_migration() appelé sans condition RUN_STARTUP_MIGRATIONS',
                'recommendation': 'Conditionner apply_migration() avec RUN_STARTUP_MIGRATIONS'
            })
    
    return issues

def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("🔍 VÉRIFICATION DES MIGRATIONS AU BOOT")
    print("=" * 80)
    print()
    
    issues = check_startup_migrations()
    
    if issues:
        print(f"❌ {len(issues)} problème(s) détecté(s):\n")
        for issue in issues:
            print(f"  📄 {issue['file']}")
            print(f"     {issue['description']}")
            print(f"     💡 {issue['recommendation']}")
            print()
        return 1
    else:
        print("✅ Les migrations au boot sont conditionnées par RUN_STARTUP_MIGRATIONS")
        print("   Elles seront désactivées en production")
        return 0

if __name__ == "__main__":
    sys.exit(main())


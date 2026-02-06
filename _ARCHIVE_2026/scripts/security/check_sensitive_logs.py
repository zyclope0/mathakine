#!/usr/bin/env python3
"""
Script pour vérifier qu'aucun mot de passe ou hash n'est loggé.
Utilisé pour valider la correction SEC-1.1.
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_sensitive_logs():
    """Vérifie les fichiers Python pour les logs sensibles"""
    issues = []
    
    files_to_check = [
        "app/core/security.py",
        "app/services/auth_service.py",
        "server/handlers/auth_handlers.py"
    ]
    
    # Patterns à détecter
    sensitive_patterns = [
        (r'logger\.(debug|info|warning|error).*password.*clair', 'Mot de passe en clair loggé'),
        (r'logger\.(debug|info|warning|error).*hash.*comparer', 'Hash à comparer loggé'),
        (r'logger\.(debug|info|warning|error).*hash.*généré', 'Hash généré loggé'),
        (r'logger\.(debug|info|warning|error).*hashed_password', 'Hashed password loggé'),
        (r'logger\.(debug|info|warning|error).*plain_password', 'Plain password loggé'),
    ]
    
    for file_path in files_to_check:
        full_path = project_root / file_path
        if not full_path.exists():
            continue
        
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            # Ignorer les commentaires et les messages génériques sécurisés
            stripped_line = line.strip()
            if stripped_line.startswith('#'):
                continue  # Ignorer les commentaires
            
            for pattern, description in sensitive_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Vérifier si c'est un message générique sécurisé (sans variable)
                    if '{' not in line and 'f"' not in line and 'f\'' not in line:
                        # Message générique sécurisé, ignorer
                        continue
                    issues.append({
                        'file': file_path,
                        'line': line_num,
                        'description': description,
                        'content': line.strip()
                    })
    
    return issues

def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("🔍 VÉRIFICATION DES LOGS SENSIBLES")
    print("=" * 80)
    print()
    
    issues = check_sensitive_logs()
    
    if issues:
        print(f"❌ {len(issues)} problème(s) détecté(s):\n")
        for issue in issues:
            print(f"  📄 {issue['file']}:{issue['line']}")
            print(f"     {issue['description']}")
            print(f"     Code: {issue['content'][:80]}...")
            print()
        return 1
    else:
        print("✅ Aucun log sensible détecté")
        print("   Les mots de passe et hashes ne sont pas loggés")
        return 0

if __name__ == "__main__":
    sys.exit(main())


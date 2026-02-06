#!/usr/bin/env python3
"""
Script pour tester automatiquement les modifications de sécurité.
Exécute tous les scripts de vérification et affiche un résumé.
"""

import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent

def run_check(script_name, description):
    """Exécute un script de vérification"""
    print(f"\n{'='*80}")
    print(f"🔍 {description}")
    print(f"{'='*80}")
    script_path = project_root / "scripts" / "security" / script_name
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    """Point d'entrée principal"""
    print("="*80)
    print("🧪 TESTS AUTOMATISÉS - MODIFICATIONS DE SÉCURITÉ")
    print("="*80)
    
    checks = [
        ("check_sensitive_logs.py", "Vérification des logs sensibles"),
        ("check_fallback_refresh.py", "Vérification du fallback refresh token"),
        ("check_localstorage_refresh.py", "Vérification localStorage refresh_token"),
        ("check_demo_credentials.py", "Vérification des credentials démo"),
        ("check_startup_migrations.py", "Vérification des migrations au boot"),
    ]
    
    results = []
    for script, description in checks:
        success = run_check(script, description)
        results.append((description, success))
    
    print("\n" + "="*80)
    print("📊 RÉSULTATS")
    print("="*80)
    
    for description, success in results:
        status = "✅ PASSE" if success else "❌ ÉCHEC"
        print(f"{status} : {description}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n✅ Tous les tests de sécurité passent !")
        print("   Les modifications de sécurité sont correctement implémentées.")
        return 0
    else:
        print("\n❌ Certains tests ont échoué. Vérifiez les détails ci-dessus.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


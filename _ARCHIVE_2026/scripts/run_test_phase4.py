#!/usr/bin/env python3
"""Script pour exécuter les tests de la Phase 4 et afficher les résultats."""
import subprocess
import sys
from pathlib import Path

def run_tests():
    """Exécute les tests de la Phase 4."""
    test_files = [
        "tests/integration/test_auth_no_fallback.py",
        "tests/integration/test_auth_cookies_only.py",
        "tests/integration/test_sse_auth.py",
    ]
    
    print("=" * 70)
    print("EXÉCUTION DES TESTS - PHASE 4")
    print("=" * 70)
    print()
    
    all_passed = True
    
    for test_file in test_files:
        test_path = Path(test_file)
        if not test_path.exists():
            print(f"❌ Fichier introuvable: {test_file}")
            all_passed = False
            continue
        
        print(f"Exécution de {test_path.name}...")
        print("-" * 70)
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short", "--override-ini=addopts="],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            # Afficher la sortie
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            if result.returncode == 0:
                print(f"✅ {test_path.name}: TOUS LES TESTS PASSENT")
            else:
                print(f"❌ {test_path.name}: CERTAINS TESTS ONT ÉCHOUÉ")
                all_passed = False
            
        except Exception as test_error:
            print(f"❌ Erreur lors de l'exécution: {test_error}")
            all_passed = False
        
        print()
    
    print("=" * 70)
    if all_passed:
        print("✅ TOUS LES TESTS DE LA PHASE 4 PASSENT")
        return 0
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())


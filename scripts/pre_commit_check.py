#!/usr/bin/env python3
"""
🔍 Script de vérification pre-commit pour Mathakine
Exécute les tests critiques avant chaque commit pour éviter les régressions.
"""

import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class TestLevel(Enum):
    """Niveaux de criticité des tests"""
    CRITICAL = "🔴 CRITIQUE"      # Bloque le commit
    IMPORTANT = "🟡 IMPORTANT"    # Avertissement
    SUPPLEMENTARY = "🟢 INFORMATIF"  # Information seulement

@dataclass
class TestSuite:
    """Configuration d'une suite de tests"""
    name: str
    level: TestLevel
    paths: List[str]
    blocking: bool
    timeout: int = 300  # 5 minutes par défaut

class PreCommitChecker:
    """Gestionnaire des vérifications pre-commit"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        self.start_time = time.time()
        
        # Configuration des suites de tests
        self.test_suites = [
            TestSuite(
                name="Tests Critiques",
                level=TestLevel.CRITICAL,
                paths=[
                    "tests/functional/",
                    "tests/unit/test_user_service.py",
                    "tests/unit/test_exercise_service.py", 
                    "tests/unit/test_logic_challenge_service.py",
                    "tests/unit/test_auth_service.py"
                ],
                blocking=True,
                timeout=300  # Augmenté de 180s à 300s (5 min)
            ),
            TestSuite(
                name="Tests Importants",
                level=TestLevel.IMPORTANT,
                paths=[
                    "tests/integration/",
                    "tests/unit/test_models.py",
                    "tests/unit/test_enhanced_server_adapter.py"
                ],
                blocking=False,
                timeout=180  # Augmenté de 120s à 180s (3 min)
            ),
            TestSuite(
                name="Tests Complémentaires",
                level=TestLevel.SUPPLEMENTARY,
                paths=[
                    "tests/unit/test_cli.py",
                    "tests/unit/test_db_init_service.py"
                ],
                blocking=False,
                timeout=120  # Augmenté de 60s à 120s (2 min)
            )
        ]

    def print_header(self):
        """Affiche l'en-tête du script"""
        print("=" * 60)
        print("🔍 VÉRIFICATION PRE-COMMIT MATHAKINE")
        print("=" * 60)
        print()

    def print_section(self, title: str, level: TestLevel):
        """Affiche une section de tests"""
        print(f"\n{level.value} {title}")
        print("-" * 50)

    def run_command(self, cmd: List[str], timeout: int = 300) -> Tuple[bool, str, str]:
        """Exécute une commande avec timeout"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Timeout après {timeout}s"
        except Exception as e:
            return False, "", str(e)

    def run_test_suite(self, suite: TestSuite) -> bool:
        """Exécute une suite de tests"""
        self.print_section(suite.name, suite.level)
        
        # Vérifier que les chemins existent
        existing_paths = []
        for path in suite.paths:
            full_path = self.project_root / path
            if full_path.exists():
                existing_paths.append(path)
            else:
                print(f"⚠️  Chemin ignoré (inexistant): {path}")
        
        if not existing_paths:
            print(f"❌ Aucun test trouvé pour {suite.name}")
            return not suite.blocking
        
        # Construire la commande pytest
        cmd = [
            sys.executable, "-m", "pytest",
            *existing_paths,
            "--tb=short",
            "-v",
            "--maxfail=3" if suite.blocking else "--maxfail=10"
        ]
        
        print(f"🚀 Exécution: {' '.join(cmd)}")
        print()
        
        success, stdout, stderr = self.run_command(cmd, suite.timeout)
        
        # Analyser les résultats
        if success:
            print(f"✅ {suite.name} - SUCCÈS")
            # Extraire le nombre de tests passés
            lines = stdout.split('\n')
            for line in lines:
                if 'passed' in line and ('failed' in line or 'error' in line):
                    print(f"📊 {line.strip()}")
                    break
        else:
            print(f"❌ {suite.name} - ÉCHEC")
            if stderr:
                print(f"🔍 Erreur: {stderr[:500]}...")
            
            # Afficher les échecs importants
            if "FAILED" in stdout:
                print("\n🔍 Tests échoués:")
                lines = stdout.split('\n')
                for line in lines:
                    if "FAILED" in line:
                        print(f"  ❌ {line.strip()}")
        
        self.results[suite.name] = {
            'success': success,
            'level': suite.level,
            'blocking': suite.blocking,
            'stdout': stdout,
            'stderr': stderr
        }
        
        return success

    def check_code_quality(self) -> bool:
        """Vérifications de qualité du code"""
        self.print_section("Qualité du Code", TestLevel.IMPORTANT)
        
        checks = [
            {
                'name': 'Formatage (Black)',
                'cmd': [sys.executable, '-m', 'black', '--check', '--diff', '.'],
                'blocking': False
            },
            {
                'name': 'Imports (isort)', 
                'cmd': [sys.executable, '-m', 'isort', '--check-only', '--diff', '.'],
                'blocking': False
            },
            {
                'name': 'Linting (Flake8)',
                'cmd': [sys.executable, '-m', 'flake8', '.', '--count', '--statistics'],
                'blocking': False
            }
        ]
        
        all_passed = True
        
        for check in checks:
            print(f"🔍 {check['name']}...")
            success, stdout, stderr = self.run_command(check['cmd'], 30)
            
            if success:
                print(f"  ✅ {check['name']} - OK")
            else:
                print(f"  ⚠️  {check['name']} - Problèmes détectés")
                if not check['blocking']:
                    print(f"     (Non-bloquant)")
                else:
                    all_passed = False
        
        return all_passed

    def generate_summary(self) -> bool:
        """Génère un résumé des résultats"""
        print("\n" + "=" * 60)
        print("📋 RÉSUMÉ DES VÉRIFICATIONS")
        print("=" * 60)
        
        critical_failed = False
        important_failed = False
        
        for suite_name, result in self.results.items():
            level = result['level']
            success = result['success']
            blocking = result['blocking']
            
            status = "✅ PASSÉ" if success else "❌ ÉCHEC"
            blocking_text = " (BLOQUANT)" if blocking else " (non-bloquant)"
            
            print(f"{level.value} {suite_name}: {status}{blocking_text}")
            
            if not success and blocking:
                critical_failed = True
            elif not success and level == TestLevel.IMPORTANT:
                important_failed = True
        
        # Temps d'exécution
        duration = time.time() - self.start_time
        print(f"\n⏱️  Durée totale: {duration:.1f}s")
        
        # Décision finale
        print("\n" + "=" * 60)
        if critical_failed:
            print("🚨 COMMIT BLOQUÉ")
            print("❌ Des tests critiques ont échoué")
            print("🔧 Corrigez les erreurs avant de commiter")
            return False
        elif important_failed:
            print("⚠️  COMMIT AUTORISÉ AVEC AVERTISSEMENTS")
            print("🟡 Des tests importants ont échoué")
            print("📝 Considérez corriger ces problèmes")
            return True
        else:
            print("🎉 COMMIT AUTORISÉ")
            print("✅ Toutes les vérifications critiques passent")
            return True

    def run(self) -> bool:
        """Exécute toutes les vérifications"""
        self.print_header()
        
        # Vérifier que nous sommes dans le bon répertoire
        if not (self.project_root / "mathakine_cli.py").exists():
            print("❌ Erreur: Script doit être exécuté depuis la racine du projet Mathakine")
            return False
        
        # Exécuter les suites de tests
        for suite in self.test_suites:
            self.run_test_suite(suite)
        
        # Vérifications de qualité du code
        self.check_code_quality()
        
        # Générer le résumé
        return self.generate_summary()

def main():
    """Point d'entrée principal"""
    checker = PreCommitChecker()
    success = checker.run()
    
    if not success:
        print("\n💡 CONSEILS:")
        print("  • Exécutez les tests individuellement: python -m pytest tests/functional/ -v")
        print("  • Vérifiez les logs détaillés ci-dessus")
        print("  • Utilisez --tb=long pour plus de détails")
        print("  • Consultez la documentation des tests")
        
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
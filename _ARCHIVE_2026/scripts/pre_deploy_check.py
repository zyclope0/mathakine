#!/usr/bin/env python3
"""
🚀 Script de vérification pré-déploiement pour Mathakine
Exécute toutes les validations nécessaires avant un déploiement en production
"""

import sys
import subprocess
import os
from pathlib import Path
from typing import List, Tuple

class PreDeployChecker:
    """Gestionnaire des vérifications pré-déploiement"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors = []
        self.warnings = []
        
    def print_header(self):
        """Affiche l'en-tête"""
        print("=" * 70)
        print("🚀 VÉRIFICATION PRÉ-DÉPLOIEMENT MATHAKINE")
        print("=" * 70)
        print()
    
    def run_command(self, cmd: List[str], description: str, cwd: Path = None) -> Tuple[bool, str]:
        """Exécute une commande et retourne le résultat"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd or self.project_root,
                timeout=300
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)
    
    def check_typescript(self) -> bool:
        """Vérifie que le build TypeScript passe"""
        print("🔨 Vérification TypeScript...")
        
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            self.warnings.append("Répertoire frontend non trouvé")
            return True
        
        # Vérifier npm install
        success, output = self.run_command(
            ["npm", "install", "--silent"],
            "npm install",
            cwd=frontend_dir
        )
        if not success:
            self.errors.append("npm install a échoué")
            return False
        
        # Vérifier build
        success, output = self.run_command(
            ["npm", "run", "build"],
            "TypeScript build",
            cwd=frontend_dir
        )
        
        if success:
            print("  ✅ Build TypeScript réussi")
            return True
        else:
            print("  ❌ Build TypeScript échoué")
            print(f"     Erreurs: {output[:500]}")
            self.errors.append("Build TypeScript échoué")
            return False
    
    def check_python_tests(self) -> bool:
        """Vérifie que les tests Python critiques passent"""
        print("🧪 Vérification tests Python critiques...")
        
        # Exécuter les tests critiques via pre_commit_check
        success, output = self.run_command(
            [sys.executable, "scripts/pre_commit_check.py"],
            "Tests critiques"
        )
        
        if success:
            print("  ✅ Tests critiques passés")
            return True
        else:
            print("  ❌ Tests critiques échoués")
            self.errors.append("Tests critiques échoués")
            return False
    
    def check_security_scripts(self) -> bool:
        """Vérifie les scripts de sécurité"""
        print("🔒 Vérification scripts de sécurité...")
        
        security_scripts = [
            "scripts/security/check_sensitive_logs.py",
            "scripts/security/check_fallback_refresh.py",
            "scripts/security/check_localstorage_refresh.py",
            "scripts/security/check_demo_credentials.py",
            "scripts/security/check_startup_migrations.py",
        ]
        
        all_passed = True
        for script in security_scripts:
            script_path = self.project_root / script
            if not script_path.exists():
                continue
            
            success, output = self.run_command(
                [sys.executable, str(script_path)],
                f"Security check: {script}"
            )
            
            if not success:
                print(f"  ⚠️  {script}: Échec")
                self.warnings.append(f"Security check failed: {script}")
                # Ne bloque pas le déploiement mais avertit
        
        print("  ✅ Vérifications de sécurité terminées")
        return True
    
    def check_load_tests(self, skip_load_tests: bool = False) -> bool:
        """Vérifie les tests de charge (optionnel)"""
        if skip_load_tests:
            print("⏭️  Tests de charge ignorés (--skip-load-tests)")
            return True
        
        print("📈 Vérification tests de charge...")
        
        # Vérifier si k6 est installé
        success, _ = self.run_command(["k6", "version"], "k6 version")
        if not success:
            print("  ⚠️  k6 non installé - tests de charge ignorés")
            self.warnings.append("k6 non installé - tests de charge ignorés")
            return True
        
        # Vérifier si le backend est accessible
        backend_url = os.getenv("BACKEND_URL", "http://localhost:10000")
        print(f"  Backend URL: {backend_url}")
        
        # Exécuter les tests de charge rapides
        success, output = self.run_command(
            [sys.executable, "scripts/load/run_load_tests.py", "--level", "quick"],
            "Load tests (quick)"
        )
        
        if success:
            print("  ✅ Tests de charge rapides passés")
            return True
        else:
            print("  ⚠️  Tests de charge rapides échoués (non bloquant)")
            self.warnings.append("Tests de charge rapides échoués")
            return True  # Non bloquant
    
    def check_env_vars(self) -> bool:
        """Vérifie les variables d'environnement critiques"""
        print("🔐 Vérification variables d'environnement...")
        
        required_vars = {
            "production": ["DATABASE_URL", "SECRET_KEY"],
            "development": []
        }
        
        env = os.getenv("ENVIRONMENT", "development")
        required = required_vars.get(env, [])
        
        missing = []
        for var in required:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print(f"  ⚠️  Variables manquantes: {', '.join(missing)}")
            self.warnings.append(f"Variables d'environnement manquantes: {', '.join(missing)}")
        else:
            print("  ✅ Variables d'environnement OK")
        
        return True  # Non bloquant
    
    def run_all(self, skip_load_tests: bool = False) -> bool:
        """Exécute toutes les vérifications"""
        self.print_header()
        
        checks = [
            ("TypeScript", self.check_typescript),
            ("Tests Python", self.check_python_tests),
            ("Sécurité", self.check_security_scripts),
            ("Variables d'environnement", self.check_env_vars),
            ("Tests de charge", lambda: self.check_load_tests(skip_load_tests)),
        ]
        
        all_passed = True
        
        for name, check_func in checks:
            print()
            try:
                if not check_func():
                    all_passed = False
            except Exception as e:
                print(f"  ❌ Erreur lors de {name}: {str(e)}")
                self.errors.append(f"Erreur {name}: {str(e)}")
                all_passed = False
        
        # Résumé
        print()
        print("=" * 70)
        print("📊 RÉSUMÉ")
        print("=" * 70)
        
        if self.errors:
            print(f"❌ Erreurs: {len(self.errors)}")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print(f"⚠️  Avertissements: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ Toutes les vérifications sont passées")
        elif not self.errors:
            print("✅ Déploiement autorisé (avertissements non bloquants)")
        else:
            print("❌ Déploiement bloqué (erreurs critiques)")
        
        return all_passed

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Vérifications pré-déploiement pour Mathakine"
    )
    parser.add_argument(
        "--skip-load-tests",
        action="store_true",
        help="Ignorer les tests de charge"
    )
    
    args = parser.parse_args()
    
    checker = PreDeployChecker()
    success = checker.run_all(skip_load_tests=args.skip_load_tests)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()


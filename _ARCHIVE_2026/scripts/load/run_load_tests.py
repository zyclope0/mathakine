#!/usr/bin/env python3
"""
📈 Script d'exécution des tests de charge k6 pour Mathakine
Intégré dans le processus de validation pré-déploiement
"""

import sys
import subprocess
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class LoadTestLevel(Enum):
    """Niveaux de tests de charge"""
    QUICK = "quick"      # Tests rapides (30s)
    STANDARD = "standard"  # Tests standards (60s)
    FULL = "full"        # Tests complets (120s+)

@dataclass
class LoadTestScenario:
    """Configuration d'un scénario de test de charge"""
    name: str
    file: str
    description: str
    vus: int
    duration: str
    level: LoadTestLevel
    required: bool = True  # Si True, échec bloque le déploiement

class LoadTestRunner:
    """Gestionnaire des tests de charge k6"""
    
    def __init__(self, backend_url: Optional[str] = None, test_level: LoadTestLevel = LoadTestLevel.STANDARD):
        self.project_root = Path(__file__).parent.parent.parent
        self.k6_dir = self.project_root / "scripts" / "load" / "k6"
        self.backend_url = backend_url or os.getenv("BACKEND_URL", "http://localhost:10000")
        self.test_level = test_level
        self.test_username = os.getenv("TEST_USERNAME", "ObiWan")
        self.test_password = os.getenv("TEST_PASSWORD", "HelloThere123!")
        
        # Configuration des scénarios selon le niveau
        self.scenarios = self._get_scenarios_for_level()
        
    def _get_scenarios_for_level(self) -> List[LoadTestScenario]:
        """Retourne les scénarios selon le niveau de test"""
        base_scenarios = [
            LoadTestScenario(
                name="Auth Burst",
                file="auth_burst.js",
                description="300 req/min sur POST /api/auth/login",
                vus=5,
                duration="60s",
                level=LoadTestLevel.STANDARD,
                required=True
            ),
            LoadTestScenario(
                name="Refresh Storm",
                file="refresh_storm.js",
                description="150 req/min sur POST /api/auth/refresh",
                vus=3,
                duration="60s",
                level=LoadTestLevel.STANDARD,
                required=True
            ),
            LoadTestScenario(
                name="SSE IA Challenges",
                file="sse_ia_challenges.js",
                description="200 connexions SSE simultanées",
                vus=200,
                duration="60s",
                level=LoadTestLevel.FULL,
                required=False  # Optionnel car intensif
            ),
            LoadTestScenario(
                name="Mix Auth+SSE",
                file="mix_auth_sse.js",
                description="100 utilisateurs auth + SSE",
                vus=100,
                duration="120s",
                level=LoadTestLevel.FULL,
                required=False  # Optionnel car long
            ),
        ]
        
        # Filtrer selon le niveau
        if self.test_level == LoadTestLevel.QUICK:
            return [s for s in base_scenarios if s.level == LoadTestLevel.QUICK or s.name == "Auth Burst"]
        elif self.test_level == LoadTestLevel.STANDARD:
            return [s for s in base_scenarios if s.level != LoadTestLevel.FULL]
        else:  # FULL
            return base_scenarios
    
    def check_k6_installed(self) -> bool:
        """Vérifie si k6 est installé"""
        try:
            result = subprocess.run(
                ["k6", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def check_backend_available(self) -> bool:
        """Vérifie si le backend est accessible"""
        try:
            import urllib.request
            import urllib.error
            
            req = urllib.request.Request(f"{self.backend_url}/health")
            req.add_header("User-Agent", "Mathakine-LoadTest/1.0")
            
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False
    
    def run_scenario(self, scenario: LoadTestScenario) -> Tuple[bool, Dict]:
        """Exécute un scénario de test de charge"""
        script_path = self.k6_dir / scenario.file
        
        if not script_path.exists():
            print(f"❌ Fichier non trouvé: {script_path}")
            return False, {"error": f"File not found: {scenario.file}"}
        
        # Construire la commande k6
        cmd = [
            "k6", "run",
            "--vus", str(scenario.vus),
            "--duration", scenario.duration,
            "--env", f"BACKEND_URL={self.backend_url}",
            "--env", f"TEST_USERNAME={self.test_username}",
            "--env", f"TEST_PASSWORD={self.test_password}",
            str(script_path)
        ]
        
        print(f"  📊 Exécution: {scenario.name}")
        print(f"     VUs: {scenario.vus}, Durée: {scenario.duration}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=int(scenario.duration.replace("s", "")) + 30,  # Timeout = durée + 30s
                cwd=self.k6_dir
            )
            
            # Analyser la sortie pour détecter les échecs
            success = result.returncode == 0
            
            # Extraire les métriques de la sortie
            metrics = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
            
            if success:
                print(f"  ✅ {scenario.name}: Succès")
            else:
                print(f"  ❌ {scenario.name}: Échec (code {result.returncode})")
                if result.stderr:
                    print(f"     Erreur: {result.stderr[:200]}")
            
            return success, metrics
            
        except subprocess.TimeoutExpired:
            print(f"  ⏱️ {scenario.name}: Timeout")
            return False, {"error": "Timeout"}
        except Exception as e:
            print(f"  ❌ {scenario.name}: Erreur - {str(e)}")
            return False, {"error": str(e)}
    
    def run_all(self) -> bool:
        """Exécute tous les scénarios configurés"""
        print("=" * 70)
        print("📈 TESTS DE CHARGE MATHAKINE")
        print("=" * 70)
        print()
        
        # Vérifications préalables
        print("🔍 Vérifications préalables...")
        
        if not self.check_k6_installed():
            print("❌ k6 n'est pas installé")
            print("   Installation: winget install k6 (Windows) ou brew install k6 (macOS)")
            return False
        print("  ✅ k6 installé")
        
        if not self.check_backend_available():
            print(f"⚠️  Backend non accessible à {self.backend_url}")
            print("   Assurez-vous que le backend est démarré")
            response = input("   Continuer quand même ? (o/N): ")
            if response.lower() != "o":
                return False
        else:
            print(f"  ✅ Backend accessible: {self.backend_url}")
        
        print()
        print(f"📋 Niveau de test: {self.test_level.value}")
        print(f"📊 Scénarios à exécuter: {len(self.scenarios)}")
        print()
        
        # Exécuter les scénarios
        results = []
        all_passed = True
        
        for i, scenario in enumerate(self.scenarios, 1):
            print(f"[{i}/{len(self.scenarios)}] {scenario.name}")
            print(f"  Description: {scenario.description}")
            
            success, metrics = self.run_scenario(scenario)
            results.append({
                "scenario": scenario.name,
                "success": success,
                "required": scenario.required,
                "metrics": metrics
            })
            
            if not success and scenario.required:
                all_passed = False
            
            print()
        
        # Résumé
        print("=" * 70)
        print("📊 RÉSUMÉ DES TESTS DE CHARGE")
        print("=" * 70)
        
        passed = sum(1 for r in results if r["success"])
        failed = len(results) - passed
        required_failed = sum(1 for r in results if not r["success"] and r["required"])
        
        print(f"✅ Succès: {passed}/{len(results)}")
        print(f"❌ Échecs: {failed}/{len(results)}")
        
        if required_failed > 0:
            print(f"🚨 Échecs critiques: {required_failed}")
            print()
            print("Les scénarios suivants ont échoué (bloquants):")
            for r in results:
                if not r["success"] and r["required"]:
                    print(f"  - {r['scenario']}")
        
        print()
        
        if all_passed:
            print("✅ Tous les tests de charge critiques sont passés")
            return True
        else:
            print("❌ Certains tests de charge critiques ont échoué")
            return False

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Exécute les tests de charge k6 pour Mathakine"
    )
    parser.add_argument(
        "--backend-url",
        type=str,
        default=None,
        help="URL du backend (défaut: BACKEND_URL ou http://localhost:10000)"
    )
    parser.add_argument(
        "--level",
        type=str,
        choices=["quick", "standard", "full"],
        default="standard",
        help="Niveau de test (quick/standard/full)"
    )
    parser.add_argument(
        "--username",
        type=str,
        default=None,
        help="Username pour les tests (défaut: TEST_USERNAME ou ObiWan)"
    )
    parser.add_argument(
        "--password",
        type=str,
        default=None,
        help="Password pour les tests (défaut: TEST_PASSWORD)"
    )
    
    args = parser.parse_args()
    
    # Mapper le niveau
    level_map = {
        "quick": LoadTestLevel.QUICK,
        "standard": LoadTestLevel.STANDARD,
        "full": LoadTestLevel.FULL
    }
    
    runner = LoadTestRunner(
        backend_url=args.backend_url,
        test_level=level_map[args.level]
    )
    
    if args.username:
        runner.test_username = args.username
    if args.password:
        runner.test_password = args.password
    
    success = runner.run_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()


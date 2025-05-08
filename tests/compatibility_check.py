"""Script de vérification de compatibilité et de préparation de l'environnement"""
import os
import sys
import platform
import subprocess
import pkg_resources
from pathlib import Path
from datetime import datetime

def main():
    """Fonction principale qui exécute la vérification de compatibilité"""
    print("=== VÉRIFICATION DE COMPATIBILITÉ MATHAKINE ===")
    print(f"Date: {datetime.now()}")
    print(f"Répertoire: {os.getcwd()}\n")
    
    # 1. Vérifier l'environnement Python
    check_python_environment()
    
    # 2. Vérifier les dépendances et leur compatibilité
    check_dependencies_compatibility()
    
    # 3. Vérifier la configuration
    check_configuration()
    
    # 4. Proposer des correctifs
    propose_fixes()
    
    print("\n=== VÉRIFICATION TERMINÉE ===")

def check_python_environment():
    """Vérifie l'environnement Python"""
    print("1. Vérification de l'environnement Python:")
    
    # Version de Python
    python_version = platform.python_version()
    print(f"  • Version de Python: {python_version}")
    
    # Architecture
    architecture = platform.architecture()[0]
    print(f"  • Architecture: {architecture}")
    
    # Environnement virtuel
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"  • Environnement virtuel: {venv_path}")
        venv_version = subprocess.run([sys.executable, "-c", "import sys; print(sys.prefix)"], 
                                    capture_output=True, text=True).stdout.strip()
        print(f"  • Version dans l'environnement virtuel: {venv_version}")
    else:
        print("  • Pas d'environnement virtuel détecté")
    
    # Vérifier les problèmes connus
    if python_version.startswith("3.13"):
        print("  ⚠️ Python 3.13 détecté - Des problèmes de compatibilité sont connus avec certaines dépendances")
        print("     (notamment SQLAlchemy < 2.0.27)")

def check_dependencies_compatibility():
    """Vérifie la compatibilité des dépendances"""
    print("\n2. Vérification des dépendances et leur compatibilité:")
    
    # Liste des dépendances critiques et leurs versions minimales pour Python 3.13
    critical_deps = {
        "sqlalchemy": "2.0.27",  # Version minimale pour Python 3.13
        "starlette": "0.31.1",
        "fastapi": "0.100.0",
        "uvicorn": "0.23.2",
        "pydantic": "2.0.0"
    }
    
    # Lire les dépendances installées
    installed_deps = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    
    # Afficher les dépendances critiques et vérifier leur compatibilité
    incompatible_deps = []
    for dep, min_version in critical_deps.items():
        if dep in installed_deps:
            installed_version = installed_deps[dep]
            print(f"  • {dep}: installé ({installed_version}), minimum recommandé ({min_version})")
            
            # Vérifier si la version est compatible
            if pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(min_version):
                print(f"    ⚠️ Version installée de {dep} ({installed_version}) plus ancienne que recommandée ({min_version})")
                incompatible_deps.append((dep, installed_version, min_version))
        else:
            print(f"  • {dep}: Non installé")
    
    # Enregistrer les dépendances incompatibles pour plus tard
    return incompatible_deps

def check_configuration():
    """Vérifie la configuration du projet"""
    print("\n3. Vérification de la configuration:")
    
    # Vérifier le fichier .env
    if Path(".env").exists():
        print("  ✅ Fichier .env trouvé")
        
        # Lire les variables d'environnement
        with open(".env", "r") as f:
            env_vars = {}
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                try:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                except ValueError:
                    continue
        
        # Vérifier la configuration de la base de données
        if "DATABASE_URL" in env_vars:
            db_url = env_vars["DATABASE_URL"]
            print(f"  ✅ DATABASE_URL: {db_url[:15]}***[masqué]")
            
            # Vérifier le type de base de données
            if "sqlite" in db_url.lower():
                print("  ℹ️ Type de base de données: SQLite (local)")
                # Vérifier si le fichier existe
                db_path = db_url.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    print(f"  ✅ Fichier de base de données trouvé: {db_path}")
                else:
                    print(f"  ⚠️ Fichier de base de données non trouvé: {db_path}")
            elif "postgresql" in db_url.lower():
                print("  ℹ️ Type de base de données: PostgreSQL")
            else:
                print(f"  ℹ️ Type de base de données: {db_url.split(':')[0]}")
        else:
            print("  ⚠️ DATABASE_URL non trouvé dans .env")
    else:
        print("  ❌ Fichier .env non trouvé")
        # Vérifier si le fichier .env.example existe
        if Path(".env.example").exists():
            print("  ℹ️ Fichier .env.example trouvé, vous pouvez le copier en .env")

def propose_fixes():
    """Propose des correctifs pour les problèmes détectés"""
    print("\n4. Actions recommandées:")
    
    python_version = platform.python_version()
    
    if python_version.startswith("3.13"):
        print("  • Pour Python 3.13:")
        print("    - Mettre à jour SQLAlchemy: pip install sqlalchemy>=2.0.27")
        print("    - Utiliser un environnement virtuel avec Python 3.11 ou 3.12 pour une meilleure compatibilité")
        print("    - Vérifier les nouvelles versions des dépendances qui supportent Python 3.13")
    
    print("\n  • Actions générales:")
    print("    - Exécuter: pip install -r requirements.txt --upgrade")
    print("    - Vérifier la documentation des dépendances pour les problèmes connus")
    print("    - Tester avec différentes versions de Python (3.11 ou 3.12 recommandés)")
    
    # Commandes spécifiques pour résoudre les problèmes
    print("\n  • Commandes à exécuter pour résoudre les problèmes:")
    print("    ```")
    print("    # Mettre à jour SQLAlchemy à la dernière version")
    print("    pip install sqlalchemy>=2.0.27")
    print("")
    print("    # Créer un environnement virtuel avec Python 3.12 (si disponible)")
    print("    python3.12 -m venv venv_py312")
    print("    source venv_py312/bin/activate  # Linux/Mac")
    print("    venv_py312\\Scripts\\activate   # Windows")
    print("    pip install -r requirements.txt")
    print("    ```")

def generate_compatibility_report():
    """Génère un rapport de compatibilité"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_results/compatibility_report_{timestamp}.txt"
    
    # Créer le dossier test_results si nécessaire
    Path("test_results").mkdir(exist_ok=True)
    
    with open(report_file, "w") as f:
        f.write("=== RAPPORT DE COMPATIBILITÉ MATHAKINE ===\n")
        f.write(f"Date: {datetime.now()}\n\n")
        
        f.write("1. Environnement Python:\n")
        f.write(f"   - Version: {platform.python_version()}\n")
        f.write(f"   - Architecture: {platform.architecture()[0]}\n")
        f.write(f"   - Système: {platform.system()} {platform.release()}\n\n")
        
        f.write("2. Dépendances installées:\n")
        for pkg in sorted(pkg_resources.working_set, key=lambda x: x.key):
            f.write(f"   - {pkg.key}: {pkg.version}\n")
        
        f.write("\n3. Recommandations:\n")
        if platform.python_version().startswith("3.13"):
            f.write("   - Utiliser Python 3.11 ou 3.12 pour une meilleure compatibilité\n")
            f.write("   - Mettre à jour SQLAlchemy à la version 2.0.27 ou supérieure\n")
        
        f.write("\n=== FIN DU RAPPORT ===\n")
    
    print(f"\nRapport de compatibilité généré: {report_file}")
    return report_file

if __name__ == "__main__":
    try:
        main()
        report_file = generate_compatibility_report()
        print(f"\nVérification terminée. Consultez {report_file} pour plus de détails.")
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
        print("\nTraceback complet:")
        import traceback
        traceback.print_exc()
        # Afficher des informations supplémentaires
        print("\nInformations de débogage:")
        print(f"Python: {sys.version}")
        print(f"Chemin Python: {sys.executable}")
        print(f"Répertoire courant: {os.getcwd()}")
        try:
            import pip
            print(f"PIP version: {pip.__version__}")
        except:
            print("PIP non disponible")
        sys.exit(1) 
"""Script de génération de rapport complet pour le projet Mathakine"""
import os
import sys
import platform
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    """Fonction principale pour générer le rapport"""
    print("=== GÉNÉRATION DU RAPPORT MATHAKINE ===")
    print(f"Date: {datetime.now()}")
    print(f"Répertoire: {os.getcwd()}")
    
    # Créer le dossier de rapports s'il n'existe pas
    Path("test_results").mkdir(exist_ok=True)
    
    # Générer le nom du fichier de rapport
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_results/rapport_complet_{timestamp}.md"
    
    # Collecter les informations
    python_info = collect_python_info()
    files_info = collect_files_info()
    env_info = collect_env_info()
    dependencies_info = collect_dependencies_info()
    recommendations = generate_recommendations(python_info, files_info, env_info, dependencies_info)
    
    # Générer le rapport
    with open(report_file, "w", encoding="utf-8") as f:
        write_report(f, python_info, files_info, env_info, dependencies_info, recommendations)
    
    print(f"\nRapport généré avec succès: {report_file}")
    print("=== GÉNÉRATION TERMINÉE ===")
    
    # Afficher le contenu du rapport
    print("\nContenu du rapport:")
    with open(report_file, "r", encoding="utf-8") as f:
        print(f.read())
    
    return report_file

def collect_python_info():
    """Collecte des informations sur l'environnement Python"""
    info = {
        "version": platform.python_version(),
        "executable": sys.executable,
        "architecture": platform.architecture()[0],
        "system": f"{platform.system()} {platform.release()}",
        "virtual_env": os.environ.get("VIRTUAL_ENV", "Aucun"),
        "is_compatible": not platform.python_version().startswith("3.13")
    }
    return info

def collect_files_info():
    """Collecte des informations sur les fichiers du projet"""
    essential_files = [
        "app/main.py",
        "app/core/config.py",
        "requirements.txt",
        "app/db/base.py",
        "app/models/user.py",
        ".env",
        ".env.example",
        "tests/conftest.py"
    ]
    
    files_info = {}
    for file_path in essential_files:
        path = Path(file_path)
        if path.exists():
            files_info[file_path] = {
                "exists": True,
                "size": path.stat().st_size,
                "modified": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            files_info[file_path] = {
                "exists": False
            }
    
    return files_info

def collect_env_info():
    """Collecte des informations sur le fichier .env"""
    env_info = {
        "exists": Path(".env").exists(),
        "variables": {}
    }
    
    if env_info["exists"]:
        try:
            with open(".env", "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    try:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Masquer les valeurs sensibles
                        if key in ["DATABASE_URL", "SECRET_KEY", "PASSWORD"]:
                            if len(value) > 10:
                                value = value[:5] + "..." + value[-2:]
                            else:
                                value = "***"
                        
                        env_info["variables"][key] = value
                    except ValueError:
                        continue
            
            # Déterminer le type de base de données
            db_url = env_info["variables"].get("DATABASE_URL", "")
            if "sqlite" in db_url.lower():
                env_info["db_type"] = "SQLite"
            elif "postgresql" in db_url.lower():
                env_info["db_type"] = "PostgreSQL"
            else:
                env_info["db_type"] = "Autre"
        except Exception as e:
            env_info["error"] = str(e)
    
    return env_info

def collect_dependencies_info():
    """Collecte des informations sur les dépendances"""
    dependencies_info = {"packages": {}}
    
    # Collecter les dépendances du fichier requirements.txt
    if Path("requirements.txt").exists():
        with open("requirements.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                parts = line.split('==', 1)
                if len(parts) == 2:
                    package_name = parts[0].strip()
                    version = parts[1].strip()
                    dependencies_info["packages"][package_name] = {
                        "required_version": version,
                        "is_critical": package_name.lower() in ["sqlalchemy", "fastapi", "starlette", "uvicorn"]
                    }
    
    # Collecter les dépendances installées
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], 
                               capture_output=True, text=True, check=True)
        installed_packages = result.stdout.strip().split('\n')
        
        for package in installed_packages:
            if "==" in package:
                name, version = package.split('==', 1)
                name = name.strip()
                version = version.strip()
                
                if name in dependencies_info["packages"]:
                    dependencies_info["packages"][name]["installed_version"] = version
                    
                    # Vérifier la compatibilité des versions
                    req_version = dependencies_info["packages"][name].get("required_version")
                    if req_version and req_version != version:
                        dependencies_info["packages"][name]["version_mismatch"] = True
    except Exception as e:
        dependencies_info["error"] = str(e)
    
    return dependencies_info

def generate_recommendations(python_info, files_info, env_info, dependencies_info):
    """Génère des recommandations basées sur les informations collectées"""
    recommendations = []
    
    # Recommandations pour Python
    if not python_info["is_compatible"]:
        recommendations.append({
            "category": "Python",
            "severity": "Haute",
            "issue": "Python 3.13 est incompatible avec certaines dépendances (notamment SQLAlchemy)",
            "solution": "Utiliser Python 3.11 ou 3.12 avec un environnement virtuel",
            "commands": [
                "python3.11 -m venv venv_py311",
                "venv_py311\\Scripts\\activate   # Windows",
                "source venv_py311/bin/activate  # Linux/Mac",
                "pip install -r requirements.txt"
            ]
        })
    
    # Recommandations pour SQLAlchemy
    sqlalchemy_info = dependencies_info["packages"].get("sqlalchemy", {})
    if sqlalchemy_info and "required_version" in sqlalchemy_info:
        required_version = sqlalchemy_info["required_version"]
        is_compatible = not required_version.startswith("2.0.26")
        
        if not is_compatible:
            recommendations.append({
                "category": "Dépendances",
                "severity": "Haute",
                "issue": f"SQLAlchemy {required_version} est incompatible avec Python 3.13",
                "solution": "Mettre à jour SQLAlchemy à la version 2.0.27 ou supérieure",
                "commands": [
                    "pip install sqlalchemy>=2.0.27",
                    "pip install -r requirements.txt"
                ]
            })
    
    # Recommandations pour les variables d'environnement
    if env_info["exists"]:
        if "SECRET_KEY" not in env_info["variables"]:
            recommendations.append({
                "category": "Configuration",
                "severity": "Moyenne",
                "issue": "La variable SECRET_KEY n'est pas définie dans le fichier .env",
                "solution": "Ajouter une clé secrète au fichier .env pour renforcer la sécurité",
                "commands": [
                    "Ajouter au fichier .env : SECRET_KEY=votre_cle_secrete_complexe"
                ]
            })
    
    # Recommandations générales
    recommendations.append({
        "category": "Général",
        "severity": "Basse",
        "issue": "Mettre à jour régulièrement les dépendances",
        "solution": "Exécuter pip install --upgrade pour maintenir les dépendances à jour",
        "commands": [
            "pip install -r requirements.txt --upgrade"
        ]
    })
    
    return recommendations

def write_report(file, python_info, files_info, env_info, dependencies_info, recommendations):
    """Écrit le rapport complet"""
    file.write("# Rapport de Validation Mathakine\n\n")
    file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Environnement Python
    file.write("## 1. Environnement Python\n\n")
    file.write(f"- **Version**: {python_info['version']}\n")
    file.write(f"- **Exécutable**: {python_info['executable']}\n")
    file.write(f"- **Architecture**: {python_info['architecture']}\n")
    file.write(f"- **Système**: {python_info['system']}\n")
    file.write(f"- **Environnement virtuel**: {python_info['virtual_env']}\n")
    file.write(f"- **Compatible**: {'Oui' if python_info['is_compatible'] else 'Non'}\n\n")
    
    # Fichiers
    file.write("## 2. Fichiers Essentiels\n\n")
    file.write("| Fichier | Statut | Taille | Dernière modification |\n")
    file.write("|---------|--------|--------|----------------------|\n")
    for file_path, info in files_info.items():
        if info["exists"]:
            file.write(f"| {file_path} | ✅ | {info['size']} octets | {info['modified']} |\n")
        else:
            file.write(f"| {file_path} | ❌ | - | - |\n")
    file.write("\n")
    
    # Configuration
    file.write("## 3. Configuration\n\n")
    if env_info["exists"]:
        file.write("Fichier .env trouvé ✅\n\n")
        file.write("### Variables d'environnement\n\n")
        file.write("| Variable | Valeur |\n")
        file.write("|----------|--------|\n")
        for key, value in env_info["variables"].items():
            file.write(f"| {key} | {value} |\n")
        
        if "db_type" in env_info:
            file.write(f"\nType de base de données: **{env_info['db_type']}**\n")
    else:
        file.write("Fichier .env non trouvé ❌\n\n")
    file.write("\n")
    
    # Dépendances
    file.write("## 4. Dépendances\n\n")
    file.write("| Package | Version requise | Version installée | Statut |\n")
    file.write("|---------|----------------|-------------------|--------|\n")
    for package, info in dependencies_info["packages"].items():
        required = info.get("required_version", "-")
        installed = info.get("installed_version", "-")
        status = "✅"
        
        if info.get("is_critical") and info.get("version_mismatch"):
            status = "⚠️"
        
        file.write(f"| {package} | {required} | {installed} | {status} |\n")
    file.write("\n")
    
    # Recommandations
    file.write("## 5. Recommandations\n\n")
    for i, rec in enumerate(recommendations, 1):
        severity_marker = "🔴" if rec["severity"] == "Haute" else "🟠" if rec["severity"] == "Moyenne" else "🟢"
        file.write(f"### {i}. {rec['category']} ({severity_marker} {rec['severity']})\n\n")
        file.write(f"**Problème**: {rec['issue']}\n\n")
        file.write(f"**Solution**: {rec['solution']}\n\n")
        file.write("**Commandes**:\n")
        for cmd in rec["commands"]:
            file.write(f"```\n{cmd}\n```\n")
        file.write("\n")

if __name__ == "__main__":
    try:
        report_file = main()
        print(f"\nRapport sauvegardé dans: {report_file}")
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 
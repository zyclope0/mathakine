"""
Script de validation simple pour vérifier les fonctionnalités de base
de l'application Mathakine sans dépendre des tests complexes.
"""
import sys
import os
import importlib.util
from pathlib import Path
import datetime
import json

def print_header(message):
    """Affiche un en-tête formaté"""
    line = "=" * 80
    print(f"\n{line}\n{message}\n{line}")

def check_file_exists(file_path):
    """Vérifie qu'un fichier existe et affiche son état"""
    path = Path(file_path)
    if path.exists():
        size = path.stat().st_size
        modified = datetime.datetime.fromtimestamp(path.stat().st_mtime)
        print(f"✅ {file_path} - Taille: {size} octets, Modifié: {modified}")
        return True
    else:
        print(f"❌ {file_path} - Fichier non trouvé")
        return False

def check_directory_structure():
    """Vérifie la structure des répertoires"""
    print_header("Vérification de la structure des répertoires")
    
    # Répertoires essentiels
    essential_dirs = [
        "app",
        "app/models",
        "app/core",
        "app/schemas",
        "app/db",
        "tests",
        "tests/unit",
        "tests/api",
        "tests/integration",
        "tests/functional"
    ]
    
    # Vérifier chaque répertoire
    all_found = True
    for directory in essential_dirs:
        path = Path(directory)
        if path.exists() and path.is_dir():
            files = list(path.glob("*.py"))
            print(f"✅ {directory} - {len(files)} fichiers Python")
        else:
            print(f"❌ {directory} - Répertoire non trouvé")
            all_found = False
    
    return all_found

def check_essential_files():
    """Vérifie la présence des fichiers essentiels"""
    print_header("Vérification des fichiers essentiels")
    
    # Fichiers essentiels
    essential_files = [
        "app/main.py",
        "app/models/user.py",
        "app/models/exercise.py",
        "app/models/attempt.py",
        "app/core/config.py",
        "requirements.txt",
        ".env"
    ]
    
    # Vérifier chaque fichier
    all_found = True
    for file in essential_files:
        if not check_file_exists(file):
            all_found = False
    
    return all_found

def validate_python_syntax(file_path):
    """Valide la syntaxe Python d'un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        compile(source, file_path, 'exec')
        return True
    except Exception as e:
        print(f"❌ Erreur de syntaxe dans {file_path}: {str(e)}")
        return False

def check_python_syntax():
    """Vérifie la syntaxe Python des fichiers importants"""
    print_header("Vérification de la syntaxe Python")
    
    # Fichiers à vérifier
    files_to_check = []
    
    # Ajouter tous les fichiers Python de l'application
    for py_file in Path("app").rglob("*.py"):
        files_to_check.append(str(py_file))
    
    # Vérifier chaque fichier
    all_valid = True
    for file in files_to_check:
        if validate_python_syntax(file):
            print(f"✅ {file} - Syntaxe valide")
        else:
            all_valid = False
    
    return all_valid

def validate_requirements():
    """Valide les dépendances dans requirements.txt"""
    print_header("Vérification des dépendances")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.readlines()
        
        required_packages = [
            "fastapi|starlette",  # fastapi OU starlette
            "sqlalchemy",
            "pytest",
            "uvicorn",
            "loguru"
        ]
        
        # Vérifier chaque package
        found_packages = []
        for req in requirements:
            req = req.strip()
            if not req or req.startswith('#'):
                continue
            
            package_name = req.split('==')[0].strip() if '==' in req else req.strip()
            found_packages.append(package_name)
        
        # Afficher les résultats
        all_found = True
        for package in required_packages:
            # Gérer les alternatives (séparées par |)
            if '|' in package:
                package_alternatives = package.split('|')
                found_any = any(alt in found_packages for alt in package_alternatives)
                if found_any:
                    print(f"✅ {package} - Au moins une alternative trouvée dans requirements.txt")
                else:
                    print(f"❌ {package} - Aucune alternative trouvée dans requirements.txt")
                    all_found = False
            else:
                # Traitement standard
                if package in found_packages:
                    print(f"✅ {package} - Trouvé dans requirements.txt")
                else:
                    print(f"❌ {package} - Non trouvé dans requirements.txt")
                    all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des dépendances: {str(e)}")
        return False

def check_database_config():
    """Vérifie la configuration de la base de données"""
    print_header("Vérification de la configuration de la base de données")
    
    try:
        # Vérifier la configuration dans .env
        if not Path('.env').exists():
            print("❌ Fichier .env non trouvé")
            return False
        
        env_vars = {}
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
        
        # Vérifier les variables essentielles
        db_vars = ['DATABASE_URL', 'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        found_vars = []
        
        for var in db_vars:
            if var in env_vars:
                print(f"✅ {var} - Configuré dans .env")
                found_vars.append(var)
            else:
                print(f"⚠️ {var} - Non trouvé dans .env")
        
        # Si au moins DATABASE_URL est défini, c'est bon
        if 'DATABASE_URL' in found_vars:
            return True
        elif len(found_vars) >= 4:  # Si au moins 4 variables sont définies
            return True
        else:
            print("❌ Configuration de base de données insuffisante")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la configuration: {str(e)}")
        return False

def validate_app():
    """Exécute toutes les validations"""
    print_header("VALIDATION DU PROJET MATHAKINE")
    print(f"Date: {datetime.datetime.now()}")
    print(f"Répertoire: {os.getcwd()}")
    
    # Exécuter les vérifications
    structure_ok = check_directory_structure()
    files_ok = check_essential_files()
    syntax_ok = check_python_syntax()
    requirements_ok = validate_requirements()
    db_config_ok = check_database_config()
    
    # Afficher le résumé
    print_header("RÉSUMÉ DE LA VALIDATION")
    print(f"Structure des répertoires: {'✅ OK' if structure_ok else '❌ ÉCHEC'}")
    print(f"Fichiers essentiels: {'✅ OK' if files_ok else '❌ ÉCHEC'}")
    print(f"Syntaxe Python: {'✅ OK' if syntax_ok else '❌ ÉCHEC'}")
    print(f"Dépendances: {'✅ OK' if requirements_ok else '❌ ÉCHEC'}")
    print(f"Configuration DB: {'✅ OK' if db_config_ok else '❌ ÉCHEC'}")
    
    # Calculer le résultat global
    all_ok = structure_ok and files_ok and syntax_ok and requirements_ok and db_config_ok
    
    print_header("RÉSULTAT FINAL")
    if all_ok:
        print("✅ VALIDATION RÉUSSIE - Le projet est bien configuré")
    else:
        print("⚠️ VALIDATION AVEC AVERTISSEMENTS - Certains éléments nécessitent votre attention")
    
    # Sauvegarder les résultats
    save_results({
        "date": datetime.datetime.now().isoformat(),
        "structure_ok": structure_ok,
        "files_ok": files_ok,
        "syntax_ok": syntax_ok,
        "requirements_ok": requirements_ok,
        "db_config_ok": db_config_ok,
        "overall_ok": all_ok
    })
    
    return all_ok

def save_results(results):
    """Sauvegarde les résultats de la validation dans un fichier JSON"""
    Path("test_results").mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results/validation_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Résultats sauvegardés dans {filename}")

if __name__ == "__main__":
    try:
        success = validate_app()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n\n❌ ERREUR CRITIQUE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 
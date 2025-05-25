#!/usr/bin/env python3
"""
Script de nettoyage complet du projet Mathakine
Analyse et archive tous les fichiers obsolètes
"""
import os
import shutil
from datetime import datetime
from pathlib import Path

# Définir les fichiers à archiver par catégorie
ADDITIONAL_FILES_TO_ARCHIVE = {
    "obsolete_tests": [
        "tests/conftest_new.py",  # Ancien conftest
        "tests/simple_test.py",   # Test simple temporaire
        "tests/indentation_fixer.py",  # Script de fix
        "tests/maintain_tests.py",  # Ancien script de maintenance
        "tests/DOCUMENTATION_TESTS_CONSOLIDEE.md",  # Documentation obsolète
        "tests/NETTOYAGE_DOCUMENTATION.md"  # Documentation temporaire
    ],
    "obsolete_scripts": [
        "scripts/fix_all_issues.py",
        "scripts/fix_enum_names_project_wide.py",
        "scripts/fix_enum_reference_chain.py",
        "scripts/fix_enum_values.py",
        "scripts/clean_test_db.py",  # Déjà archivé ailleurs
        "scripts/move_obsolete_files.py",
        "scripts/detect_obsolete_files.py",
        "scripts/add_test_data_v2.py"  # Ancien script de données test
    ],
    "old_documentation": [
        "ARCHITECTURE_AMÉLIORÉE.md",  # Ancienne version de l'architecture
        "init_db.py"  # Ancien script d'init (remplacé par alembic)
    ],
    "build_scripts": [
        "scripts/build.sh",
        "scripts/setup_persistent_db.sh",
        "scripts/start_render.sh"
    ]
}

def analyze_project_structure():
    """Analyser la structure du projet et identifier les fichiers obsolètes"""
    print("🔍 Analyse du projet Mathakine...")
    
    # Fichiers essentiels à conserver
    ESSENTIAL_FILES = {
        "root": [
            ".env", ".env.example", "sample.env",
            ".gitignore", ".dockerignore", ".flake8",
            "alembic.ini", "setup.cfg",
            "Dockerfile", "Procfile",
            "LICENSE", "README.md", "STRUCTURE.md",
            "requirements.txt",
            "mathakine_cli.py", "enhanced_server.py",
            "ai_context_summary.md"
        ],
        "app": "Tous les fichiers (code principal)",
        "migrations": "Tous les fichiers (migrations Alembic)",
        "templates": "Tous les fichiers (templates HTML)",
        "static": "Tous les fichiers (CSS/JS)",
        "docs": "Tous les fichiers (documentation)",
        "server": "Tous les fichiers (serveur)",
        "logs": "Conserver mais vider périodiquement",
        "backups": "Conserver pour sauvegardes"
    }
    
    # Scripts essentiels à conserver
    ESSENTIAL_SCRIPTS = [
        "scripts/check_compatibility.py",
        "scripts/generate_context.py",
        "scripts/generate_migration.py",
        "scripts/init_alembic.py",
        "scripts/normalize_css.py",
        "scripts/pre_commit_migration_check.py",
        "scripts/toggle_database.py",
        "scripts/restore_deleted_tables.sql",
        "scripts/README.md"
    ]
    
    # Tests essentiels à conserver
    ESSENTIAL_TESTS = [
        "tests/conftest.py",
        "tests/CORRECTION_PLAN.md",
        "tests/DOCUMENTATION_TESTS.md",
        "tests/README.md",
        "tests/test_enum_adaptation.py",
        "tests/unified_test_runner.bat",
        "tests/unified_test_runner.py"
    ]
    
    print("\n✅ Fichiers essentiels identifiés")
    print("❌ Fichiers obsolètes identifiés pour archivage")
    
    return ESSENTIAL_FILES, ESSENTIAL_SCRIPTS, ESSENTIAL_TESTS

def archive_additional_files():
    """Archiver les fichiers supplémentaires identifiés"""
    base_archive = Path("archives")
    archived_count = 0
    
    print("\n🗄️ Archivage des fichiers obsolètes supplémentaires...")
    
    for category, files in ADDITIONAL_FILES_TO_ARCHIVE.items():
        print(f"\n📁 Catégorie: {category}")
        
        # Créer le dossier si nécessaire
        category_path = base_archive / category
        category_path.mkdir(exist_ok=True)
        
        for file in files:
            if os.path.exists(file):
                try:
                    # Extraire le nom du fichier
                    filename = Path(file).name
                    dest = category_path / filename
                    
                    # Si le fichier existe déjà, ajouter un timestamp
                    if dest.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        stem = dest.stem
                        suffix = dest.suffix
                        dest = category_path / f"{stem}_{timestamp}{suffix}"
                    
                    shutil.move(file, dest)
                    print(f"  ✅ {file} → archives/{category}/")
                    archived_count += 1
                except Exception as e:
                    print(f"  ❌ Erreur avec {file}: {e}")
            else:
                print(f"  ⏭️ {file} n'existe pas (déjà archivé?)")
    
    return archived_count

def clean_cache_directories():
    """Nettoyer les dossiers de cache"""
    cache_dirs = [
        "__pycache__",
        ".pytest_cache",
        "test_results"
    ]
    
    cleaned_count = 0
    print("\n🧹 Nettoyage des dossiers de cache...")
    
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name in cache_dirs:
                dir_path = Path(root) / dir_name
                try:
                    shutil.rmtree(dir_path)
                    print(f"  ✅ Supprimé: {dir_path}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"  ❌ Erreur avec {dir_path}: {e}")
    
    return cleaned_count

def generate_cleanup_report():
    """Générer un rapport de nettoyage"""
    report_content = f"""# Rapport de nettoyage du projet Mathakine
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Structure du projet après nettoyage

### Dossiers principaux conservés:
- **app/** : Code principal de l'application
- **migrations/** : Migrations Alembic de la base de données
- **templates/** : Templates HTML
- **static/** : Fichiers CSS, JS et images
- **docs/** : Documentation complète
- **server/** : Code du serveur
- **tests/** : Tests unitaires, API, intégration et fonctionnels
- **scripts/** : Scripts utilitaires essentiels
- **archives/** : Fichiers obsolètes archivés

### Fichiers racine essentiels:
- Configuration: .env, .gitignore, alembic.ini, setup.cfg
- Déploiement: Dockerfile, Procfile, requirements.txt
- Documentation: README.md, STRUCTURE.md, ai_context_summary.md
- Points d'entrée: mathakine_cli.py, enhanced_server.py

### Scripts essentiels conservés:
- check_compatibility.py : Vérification de compatibilité
- generate_context.py : Génération de contexte
- generate_migration.py : Génération de migrations
- toggle_database.py : Basculement SQLite/PostgreSQL
- normalize_css.py : Normalisation CSS

### Tests essentiels conservés:
- unified_test_runner.py : Runner de tests unifié
- conftest.py : Configuration pytest
- CORRECTION_PLAN.md : Plan de correction des tests
- DOCUMENTATION_TESTS.md : Documentation des tests

## Fichiers archivés
Voir le dossier archives/ pour tous les fichiers obsolètes conservés pour référence historique.

## Recommandations
1. Exécuter régulièrement ce script de nettoyage
2. Vider périodiquement le dossier logs/
3. Nettoyer les caches après chaque session de développement
4. Réviser périodiquement le dossier archives/
"""
    
    with open("CLEANUP_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("\n📝 Rapport de nettoyage créé: CLEANUP_REPORT.md")

def main():
    """Fonction principale de nettoyage"""
    print("🚀 Nettoyage complet du projet Mathakine")
    print("=" * 50)
    
    # Analyser la structure
    analyze_project_structure()
    
    # Archiver les fichiers obsolètes
    archived = archive_additional_files()
    
    # Nettoyer les caches
    cleaned = clean_cache_directories()
    
    # Générer le rapport
    generate_cleanup_report()
    
    print("\n" + "=" * 50)
    print(f"✅ Nettoyage terminé!")
    print(f"📊 Résultats:")
    print(f"  - {archived} fichiers archivés")
    print(f"  - {cleaned} dossiers de cache nettoyés")
    print(f"  - 1 rapport de nettoyage généré")
    
    # Archiver ce script lui-même après exécution
    print("\n🗑️ Archivage du script de nettoyage lui-même...")
    if os.path.exists("archive_obsolete_files.py"):
        try:
            shutil.move("archive_obsolete_files.py", "archives/obsolete_scripts/")
            print("  ✅ archive_obsolete_files.py archivé")
        except:
            pass
    
    try:
        shutil.move("complete_project_cleanup.py", "archives/obsolete_scripts/")
        print("  ✅ complete_project_cleanup.py archivé")
    except:
        pass

if __name__ == "__main__":
    main() 
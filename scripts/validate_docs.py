#!/usr/bin/env python
"""
Script pour valider l'intégrité de la documentation du projet Mathakine.
Vérifie la présence des fichiers essentiels, les références entre fichiers
et les liens internes.
"""

import os
import re
import sys
from pathlib import Path
from collections import namedtuple

# Définition des chemins
ROOT_DIR = Path(__file__).parent.parent
DOCS_DIR = ROOT_DIR / "docs"

# Liste des fichiers essentiels
ESSENTIAL_FILES = [
    "CONTEXT.md",
    "CHANGELOG.md",
    "POSTGRESQL_MIGRATION.md",
    "CLEANUP_REPORT.md",
    "TROUBLESHOOTING.md",
]

# Liste des fichiers qui ont été consolidés et ne devraient plus exister
OBSOLETE_FILES = [
    "RECENT_UPDATES.md",
    "CLEANUP_REPORT_AUTO.md",
    "migration_section.md",
]

# Structure pour les problèmes trouvés
Issue = namedtuple('Issue', ['file', 'line', 'description', 'severity'])
# Niveaux de sévérité : ERROR, WARNING, INFO



def check_essential_files():
    """Vérifier que tous les fichiers essentiels existent"""
    issues = []
    for file in ESSENTIAL_FILES:
        file_path = DOCS_DIR / file
        if not file_path.exists():
            issues.append(Issue(
                file="",
                line=0,
                description=f"Fichier essentiel manquant: {file}",
                severity="ERROR"
            ))
    return issues



def check_obsolete_files():
    """Vérifier qu'aucun fichier obsolète n'existe (sauf les .bak)"""
    issues = []
    for file in OBSOLETE_FILES:
        file_path = DOCS_DIR / file
        if file_path.exists():
            issues.append(Issue(
                file=file,
                line=0,
                description=f"Fichier obsolète détecté. Il devrait être consolidé et supprimé.",
                severity="WARNING"
            ))
    return issues



def check_readme_references():
    """Vérifier que le README.md référence correctement les fichiers de documentation"""
    issues = []
    readme_path = ROOT_DIR / "README.md"

    if not readme_path.exists():
        issues.append(Issue(
            file="",
            line=0,
            description="README.md est manquant",
            severity="ERROR"
        ))
        return issues

    content = readme_path.read_text(encoding="utf-8")

    # Vérifier les références aux fichiers obsolètes
    for file in OBSOLETE_FILES:
        if re.search(r'\[.*?\]\(.*?' + re.escape(file) + r'\)', content) or \
           re.search(r'\[docs/' + re.escape(file) + r'\]', content):
            issues.append(Issue(
                file="README.md",
                line=0,
                description=f"Référence à un fichier obsolète: {file}",
                severity="WARNING"
            ))

    # Vérifier que les fichiers essentiels sont référencés
    for file in ESSENTIAL_FILES:
        if not (re.search(r'\[.*?\]\(.*?' + re.escape(file) + r'\)', content) or \
                re.search(r'\[docs/' + re.escape(file) + r'\]', content)):
            issues.append(Issue(
                file="README.md",
                line=0,
                description=f"Fichier essentiel non référencé dans README.md: {file}",
                severity="INFO"
            ))

    return issues



def check_internal_links():
    """Vérifier les liens internes entre les fichiers de documentation"""
    issues = []
    md_files = list(DOCS_DIR.glob("*.md"))
    md_files_root = list(ROOT_DIR.glob("*.md"))

    # Créer un dictionnaire des fichiers existants pour vérifier les références
    existing_files = {f.name.lower(): f.name for f in md_files}
    existing_files_root = {f.name.lower(): f.name for f in md_files_root}
    validation_files = list((DOCS_DIR / "validation").glob("*.md"))
    existing_files_validation = {f.name.lower(): f.name for f in validation_files}

    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8")

            # Trouver tous les liens internes
            internal_links = re.findall(r'\[.*?\]\((.*?\.md)(?:#.*?)?\)', content)

            # Vérifier chaque lien
            for link in internal_links:
                # Gérer les chemins relatifs
                if "../" in link:
                    # Lien vers un fichier à la racine
                    link_name = os.path.basename(link)
                    if link_name.lower() not in existing_files_root:
                        issues.append(Issue(
                            file=file_path.name,
                            line=0,
                            description=f"Lien cassé vers {link_name}",
                            severity="ERROR"
                        ))
                elif "validation/" in link:
                    # Lien vers un fichier dans le dossier validation
                    link_name = os.path.basename(link)
                    if link_name.lower() not in existing_files_validation:
                        issues.append(Issue(
                            file=file_path.name,
                            line=0,
                            description=f"Lien cassé vers {link_name}",
                            severity="ERROR"
                        ))
                else:
                    # Lien vers un fichier dans le même dossier
                    link_name = os.path.basename(link)
                    if link_name.lower() not in existing_files:
                        issues.append(Issue(
                            file=file_path.name,
                            line=0,
                            description=f"Lien cassé vers {link_name}",
                            severity="ERROR"
                        ))
        except Exception as e:
            issues.append(Issue(
                file=file_path.name,
                line=0,
                description=f"Erreur lors de l'analyse du fichier: {str(e)}",
                severity="ERROR"
            ))

    return issues



def run_validation():
    """Exécuter toutes les vérifications et retourner les problèmes trouvés"""
    issues = []

    # Vérifier les fichiers essentiels
    issues.extend(check_essential_files())

    # Vérifier les fichiers obsolètes
    issues.extend(check_obsolete_files())

    # Vérifier les références dans le README
    issues.extend(check_readme_references())

    # Vérifier les liens internes
    issues.extend(check_internal_links())

    return issues



def print_issues(issues):
    """Afficher les problèmes trouvés de manière formatée"""
    if not issues:
        print("✓ Aucun problème trouvé. La documentation est valide!")
        return True

    # Compter les problèmes par niveau de sévérité
    error_count = sum(1 for issue in issues if issue.severity == "ERROR")
    warning_count = sum(1 for issue in issues if issue.severity == "WARNING")
    info_count = sum(1 for issue in issues if issue.severity == "INFO")

    print(f"Problèmes trouvés: {len(issues)} ({error_count} erreurs, {warning_count} avertissements
        , {info_count} infos)")
    print("\n" + "="*80)

    # Trier par sévérité, puis par fichier
    issues.sort(key=lambda i: (
        0 if i.severity == "ERROR" else 1 if i.severity == "WARNING" else 2,
        i.file
    ))

    for issue in issues:
        # Utiliser des marqueurs ASCII au lieu d'emoji pour éviter les problèmes d'encodage
        severity_mark = "[X]" if issue.severity == "ERROR" else "[!]" if issue.severity == "WARNING" else "[i]"
        file_info = f"{issue.file}:{issue.line}" if issue.line > 0 else issue.file
        print(f"{severity_mark} [{issue.severity}] {file_info}: {issue.description}")

    print("="*80)

    return error_count == 0  # Succès si aucune erreur



def main():
    """Fonction principale"""
    print("="*80)
    print("Validation de la documentation du projet Mathakine")
    print("="*80)
    print(f"Répertoire de documentation: {DOCS_DIR}")
    print("\nRecherche des problèmes...\n")

    issues = run_validation()
    success = print_issues(issues)

    # Retourner un code d'erreur si des erreurs sont trouvées
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

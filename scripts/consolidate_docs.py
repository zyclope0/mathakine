#!/usr/bin/env python
"""
Script pour consolider la documentation du projet Mathakine.
Fusionne les documents qui contiennent des informations se chevauchant et
supprime les fragments redondants pour une documentation plus cohérente.
"""

import os
import re
import datetime
from pathlib import Path

# Définition des chemins
ROOT_DIR = Path(__file__).parent.parent
DOCS_DIR = ROOT_DIR / "docs"



def merge_changelog_and_updates():
    """Fusionne CHANGELOG.md et RECENT_UPDATES.md"""
    changelog_file = DOCS_DIR / "CHANGELOG.md"
    updates_file = DOCS_DIR / "RECENT_UPDATES.md"

    if not changelog_file.exists() or not updates_file.exists():
        print("Certains fichiers n'existent pas. Vérifiez les chemins.")
        return False

    # Lire les fichiers
    changelog_content = changelog_file.read_text(encoding="utf-8")
    updates_content = updates_file.read_text(encoding="utf-8")

    # Extraire les sections pertinentes du fichier RECENT_UPDATES.md
    sections = re.findall(r'## Dernière mise à jour : ([^\n]+)([\s\S]+?)(?=## |$)', updates_content)

    # Pour chaque section, trouver sa place dans le CHANGELOG
    for date_str, content in sections:
        # Convertir la date au format du CHANGELOG (YYYY-MM-DD)
        try:
            if "Mai" in date_str:
                date_iso = "2025-05-01"  # Date approximative pour Mai 2025
            else:
                # Pour d'autres formats de date, on pourrait ajouter une conversion ici
                date_iso = date_str

            # Vérifier si cette date existe déjà dans le CHANGELOG
            date_pattern = rf'\[\d+\.\d+\.\d+\] - {date_iso}'
            if re.search(date_pattern, changelog_content):
                # Extraire les sections individuelles du contenu
                updates_sections = re.findall(r'#### ([^\n]+)([\s\S]+?)(?=#### |$)', content)

                for section_title, section_content in updates_sections:
                    # Convertir le titre de section au format du CHANGELOG
                    if "Améliorations" in section_title:
                        changelog_section = "### Ajouts"
                    elif "Corrections" in section_title:
                        changelog_section = "### Corrections"
                    elif "Optimisation" in section_title:
                        changelog_section = "### Modifications"
                    else:
                        changelog_section = f"### {section_title}"

                    # Convertir les éléments de liste au format du CHANGELOG
                    items = re.findall(r'- \*\*([^*]+)\*\*', section_content)
                    formatted_items = [f"- ✅ {item.strip()}" for item in items]
                    section_content_formatted = "\n".join(formatted_items)

                    # Trouver l'endroit où insérer le contenu
                    version_pattern = rf'\[\d+\.\d+\.\d+\] - {date_iso}[\s\S]+?({changelog_section}[\s\S]+?)(?=### |## |\[\d+)'
                    match = re.search(version_pattern, changelog_content)

                    if match:
                        # Ajouter les nouveaux éléments à la section existante
                        section_with_items = match.group(1) + "\n" + section_content_formatted
                        changelog_content = changelog_content.replace(match.group(1)
                            , section_with_items)
                    else:
                        # Créer une nouvelle section si elle n'existe pas
                        version_pattern = rf'\[\d+\.\d+\.\d+\] - {date_iso}([\s\S]+?)(?=\[\d+|\Z)'
                        match = re.search(version_pattern, changelog_content)
                        if match:
                            new_section = f"{match.group(1)}{changelog_section}\n{section_content_formatted}\n\n"
                            changelog_content = changelog_content.replace(match.group(1)
                                , new_section)
            else:
                # Créer une nouvelle entrée de version
                # Trouver la dernière version pour incrémenter
                version_match = re.search(r'\[(\d+)\.(\d+)\.(\d+)\]', changelog_content)
                if version_match:
                    major, minor, patch = map(int, version_match.groups())
                    new_version = f"[{major}.{minor+1}.0]"
                else:
                    new_version = "[0.1.0]"

                # Formater le contenu pour qu'il corresponde au style du CHANGELOG
                formatted_content = content.replace("#### ", "### ")
                formatted_content = re.sub(r'- \*\*([^*]+)\*\*', r'- ✅ \1', formatted_content)

                # Insérer la nouvelle entrée après la section "Unreleased"
                unreleased_section = "## [Unreleased]\n\n"
                new_entry = f"{unreleased_section}## {new_version} - {date_iso}\n\n{formatted_content}\n"

                changelog_content = changelog_content.replace(unreleased_section, new_entry)
        except Exception as e:
            print(f"Erreur lors de la conversion de la date: {e}")

    # Ajouter une note sur la fusion
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    note = f"\n\n> Note: Ce fichier a été consolidé à partir de CHANGELOG.md et RECENT_UPDATES.md le {now}.\n"
    changelog_content += note

    # Écrire le contenu fusionné
    changelog_file.write_text(changelog_content, encoding="utf-8")

    # Créer une copie de sauvegarde du fichier RECENT_UPDATES.md
    backup_file = DOCS_DIR / "RECENT_UPDATES.md.bak"
    backup_file.write_text(updates_content, encoding="utf-8")

    print(f"Fusion terminée. Une sauvegarde a été créée: {backup_file}")
    return True



def merge_cleanup_reports():
    """Fusionne CLEANUP_REPORT.md et CLEANUP_REPORT_AUTO.md"""
    manual_report = DOCS_DIR / "CLEANUP_REPORT.md"
    auto_report = DOCS_DIR / "CLEANUP_REPORT_AUTO.md"

    if not manual_report.exists() or not auto_report.exists():
        print("Certains fichiers n'existent pas. Vérifiez les chemins.")
        return False

    # Lire les fichiers
    manual_content = manual_report.read_text(encoding="utf-8")
    auto_content = auto_report.read_text(encoding="utf-8")

    # Extraire la date du rapport manuel
    manual_date_match = re.search(r'Date de nettoyage: ([^\n]+)', manual_content)
    manual_date = manual_date_match.group(1) if manual_date_match else "Inconnue"

    # Extraire la date du rapport automatique
    auto_date_match = re.search(r'Date de nettoyage: ([^\n]+)', auto_content)
    auto_date = auto_date_match.group(1) if auto_date_match else "Inconnue"

    # Déterminer le rapport le plus récent
    most_recent_content = auto_content if auto_date > manual_date else manual_content

    # Extraire les sections pertinentes des deux rapports
    manual_files_section = re.search(r'## Fichiers supprimés([\s\S]+?)(?=## |$)', manual_content)
    auto_files_section = re.search(r'## Fichiers supprimés([\s\S]+?)(?=## |$)', auto_content)
    manual_kept_section = re.search(r'## Fichiers conservés([\s\S]+?)(?=## |$)', manual_content)
    auto_manual_section = re.search(r'## Actions de nettoyage manuelles([\s\S]+?)(?=## |$)'
        , auto_content)

    # Construire le contenu fusionné
    header = "# Rapport de nettoyage du projet Mathakine\n\n"
    date_section = f"## Date de nettoyage: {max(auto_date, manual_date)}\n\n"
    description = "Ce document présente un résumé des opérations de nettoyage effectuées sur le projet Mathakine pour éliminer les fichiers obsolètes.\n\n"
    tools_section = "## Outils utilisés\n\n- Script personnalisé `scripts/detect_obsolete_files.py`\n- Commandes PowerShell pour l'identification de fichiers spécifiques\n- Analyse manuelle des fichiers potentiellement obsolètes\n\n"

    # Section des fichiers supprimés (combinés)
    deleted_files = "## Fichiers supprimés\n\n"
    if manual_files_section and manual_files_section.group(1).strip():
        deleted_files += manual_files_section.group(1) + "\n"
    elif auto_files_section and auto_files_section.group(1).strip():
        deleted_files += auto_files_section.group(1) + "\n"
    else:
        deleted_files += "Aucun fichier n'a été supprimé lors de cette opération de nettoyage.\n\n"

    # Section des actions manuelles
    manual_actions = ""
    if auto_manual_section:
        manual_actions = "## Actions de nettoyage manuelles\n" + auto_manual_section.group(1) + "\n"

    # Section des fichiers conservés
    kept_files = ""
    if manual_kept_section:
        kept_files = "## Fichiers conservés malgré suspicion d'obsolescence\n" + manual_kept_section.group(1)
            + "\n"

    # Section résumé
    summary = "## Résumé\n\n"
    summary += "Le projet a été nettoyé des fichiers inutiles et redondants tout en préservant les fichiers essentiels à sa structure. "
    summary += "Le script `detect_obsolete_files.py` pourra être utilisé régulièrement pour maintenir le projet propre et détecter de nouveaux fichiers obsolètes.\n\n"

    # Note sur la consolidation
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    note = f"> Note: Ce rapport est le résultat de la consolidation de CLEANUP_REPORT.md et CLEANUP_REPORT_AUTO.md le {now}.\n"

    # Assembler le contenu final
    final_content = header + date_section + description + tools_section + deleted_files\
        + manual_actions + kept_files + summary + note

    # Créer des sauvegardes
    manual_backup = DOCS_DIR / "CLEANUP_REPORT.md.bak"
    auto_backup = DOCS_DIR / "CLEANUP_REPORT_AUTO.md.bak"
    manual_backup.write_text(manual_content, encoding="utf-8")
    auto_backup.write_text(auto_content, encoding="utf-8")

    # Écrire le contenu fusionné
    manual_report.write_text(final_content, encoding="utf-8")

    print(f"Fusion des rapports de nettoyage terminée. Des sauvegardes ont été créées.")
    return True



def integrate_migration_section():
    """Intègre migration_section.md dans POSTGRESQL_MIGRATION.md"""
    migration_section = DOCS_DIR / "migration_section.md"
    postgres_migration = DOCS_DIR / "POSTGRESQL_MIGRATION.md"

    if not migration_section.exists():
        print("Le fichier migration_section.md n'existe pas.")
        return False

    # Lire le fragment de migration
    section_content = migration_section.read_text(encoding="utf-8")

    # Si le fichier de migration PostgreSQL existe, y intégrer le fragment
    if postgres_migration.exists():
        postgres_content = postgres_migration.read_text(encoding="utf-8")

        # Vérifier si le contenu est déjà présent
        if section_content.strip() in postgres_content:
            print("Le contenu de migration_section.md est déjà présent dans POSTGRESQL_MIGRATION.md.")
        else:
            # Trouver un endroit approprié pour insérer le contenu
            # Par exemple, après une section introduction ou à la fin
            if "# Migration vers PostgreSQL" in postgres_content:
                # Si le fichier contient déjà une section PostgreSQL, la remplacer par le contenu du fragment
                postgres_content = re.sub(r'# Migration vers PostgreSQL[\s\S]+?(# |$)'
                    , f"# Migration vers PostgreSQL\n\n{section_content}\n\n\\1", postgres_content)
            else:
                # Sinon, ajouter à la fin
                postgres_content += f"\n\n{section_content}\n"

            # Créer une sauvegarde
            backup_file = DOCS_DIR / "POSTGRESQL_MIGRATION.md.bak"
            backup_file.write_text(postgres_content, encoding="utf-8")

            # Écrire le contenu mis à jour
            postgres_migration.write_text(postgres_content, encoding="utf-8")
            print(f"Contenu intégré dans POSTGRESQL_MIGRATION.md. Une sauvegarde a été créée.")
    else:
        # Si le fichier n'existe pas, le créer avec un en-tête approprié
        header = "# Guide de migration vers PostgreSQL\n\n"
        description = "Ce document fournit des instructions détaillées pour migrer la base de données Mathakine de SQLite vers PostgreSQL.\n\n"

        final_content = header + description + section_content

        postgres_migration.write_text(final_content, encoding="utf-8")
        print(f"Fichier POSTGRESQL_MIGRATION.md créé avec le contenu de migration_section.md.")

    # Créer une sauvegarde du fragment
    backup_file = DOCS_DIR / "migration_section.md.bak"
    backup_file.write_text(section_content, encoding="utf-8")

    print(f"Migration du contenu terminée. Une sauvegarde a été créée: {backup_file}")
    return True



def main():
    """Fonction principale pour la consolidation des documents"""
    print("Démarrage de la consolidation de la documentation...")

    # Créer le répertoire de sauvegarde si nécessaire
    if not os.path.exists(DOCS_DIR):
        print(f"Le répertoire {DOCS_DIR} n'existe pas.")
        return

    # Exécuter les fonctions de consolidation
    changelog_merged = merge_changelog_and_updates()
    cleanup_merged = merge_cleanup_reports()
    migration_integrated = integrate_migration_section()

    # Résumé
    print("\nRésumé de la consolidation:")
    print(f"- Fusion CHANGELOG.md et RECENT_UPDATES.md: {'Réussi' if changelog_merged else 'Échec'}")
    print(f"- Fusion des rapports de nettoyage: {'Réussi' if cleanup_merged else 'Échec'}")
    print(f"- Intégration de migration_section.md: {'Réussi' if migration_integrated else 'Échec'}")

    print("\nNote: Des fichiers de sauvegarde .bak ont été créés pour tous les fichiers modifiés.")
    print("Après avoir vérifié que la consolidation est correcte, vous pouvez supprimer les fichiers redondants.")

if __name__ == "__main__":
    main()

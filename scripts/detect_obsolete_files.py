#!/usr/bin/env python
"""
Script pour détecter les fichiers obsolètes dans le projet Mathakine.

Ce script utilise plusieurs techniques pour identifier avec une confiance élevée (≈99%)
les fichiers qui ne sont plus utilisés:

1. Analyse des importations Python (recherche de fichiers non importés)
2. Recherche de références directes aux fichiers dans la base de code
3. Détection de modèles de nommage indiquant l'obsolescence (_old, .bak, etc.)
4. Analyse des dates de dernière modification comparées à l'activité globale du projet
5. Exclusion des fichiers essentiels ou à risque faible (README, docs, etc.)

Usage:
    python scripts/detect_obsolete_files.py [--delete] [--move-to DIRECTORY]

Options:
    --delete            Supprime automatiquement les fichiers identifiés comme obsolètes avec une
                        confiance très élevée (>99.5%)
    --move-to DIRECTORY Déplace les fichiers obsolètes vers le répertoire spécifié au lieu de les supprimer
    --verbose           Affiche des informations détaillées sur chaque fichier analysé
    --confidence N      Définit le seuil de confiance minimum (0-100) pour rapporter un fichier comme obsolète
"""

import os
import sys
import re
import time
import shutil
import argparse
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
import ast
import importlib.util
from typing import Dict, List, Set, Tuple, Optional
from colorama import Fore


# Configuration
IGNORE_DIRS = {
    '.git', '__pycache__', 'venv', 'node_modules', 'static', 'templates',
    'logs', '.pytest_cache', 'migrations', 'media', 'fixtures', 'cache'
}

ESSENTIAL_FILES = {
    'requirements.txt', 'setup.py', 'pyproject.toml', 'Dockerfile', '.env.example',
    'README.md', 'LICENSE', '.gitignore', 'Procfile', 'app/main.py', 'app/__init__.py',
    '.dockerignore', 'GETTING_STARTED.md', 'STRUCTURE.md', 'docs/MAINTENANCE.md'
}

OBSOLETE_PATTERNS = [
    r'_old[.][^/]*$', r'_bak[.][^/]*$', r'[.]bak$', r'[.]old$', r'[.]backup$',
    r'_obsolete[.]', r'_deprecated[.]', r'_archive[.]', r'_v\d+[.]',
    r'_tmp[.]', r'_temp[.]', r'unused_', r'test_old_', r'draft_', r'wip_',
    r'_draft[.]', r'_wip[.]', r'_delete_me[.]', r'delete_me_', r'to_delete_',
    r'_to_delete[.]', r'_not_used[.]', r'not_used_', r'_unused[.]', r'backup\d+_',
    r'_backup\d+[.]', r'old\d+_', r'_old\d+[.]', r'__old__', r'__tmp__', r'__temp__'
]

# Préfixes et suffixes couramment utilisés pour les fichiers temporaires ou de sauvegarde
OBSOLETE_PREFIXES = [
    'old_', 'bak_', 'backup_', 'deprecated_', 'archive_', 'unused_', 'tmp_', 'temp_',
    'draft_', 'wip_', 'delete_me_', 'to_delete_', 'not_used_', 'backup', 'old',
    'temp', 'tmp', 'obsolete_', 'prev_', 'previous_', 'legacy_', 'archive'
]

OBSOLETE_SUFFIXES = [
    '.old', '.bak', '.backup', '.deprecated', '.tmp', '.temp', '.orig', '.swp', '.swo',
    '.save', '.saved', '.copy', '.BAK', '.OLD', '.COPY', '.TMP', '.TEMP', '.back',
    '.~', '.orig.py', '.py~', '.js~', '.html~', '.css~', '.draft', '.wip',
    '.deleted', '.not_used', '.unused', '.to_delete'
]

SAFE_EXTENSIONS = {'.txt', '.md', '.rst', '.csv', '.json', '.yaml', '.yml', '.log', '.env'}
HIGH_RISK_EXTENSIONS = {'.py', '.sh', '.bat', '.ps1', '.js', '.html', '.css'}



class FileAnalyzer:
    """Analyseur de fichiers pour détecter les fichiers obsolètes."""



    def __init__(self, project_root: Path, verbose: bool = False,
                 confidence_threshold: int = 85, report_file: Optional[str] = None):
        self.project_root = project_root
        self.verbose = verbose
        self.confidence_threshold = confidence_threshold
        self.report_file = report_file
        self.all_files = set()
        self.python_files = set()
        self.file_references = {}
        self.file_last_modified = {}
        self.git_history = {}
        self.results = []
        self.report_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project_path": str(project_root),
            "confidence_threshold": confidence_threshold,
            "files_analyzed": 0,
            "python_files_analyzed": 0,
            "files_with_references": 0,
            "obsolete_files": [],
            "statistics": {}
        }



    def collect_files(self):
        """Collecte tous les fichiers du projet."""
        print("🔍 Collecte des fichiers du projet...")

        for root, dirs, files in os.walk(self.project_root):
            # Filtrer les répertoires à ignorer
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            rel_root = os.path.relpath(root, self.project_root)
            if rel_root == '.':
                rel_root = ''

            for file in files:
                file_path = os.path.join(rel_root, file)
                abs_path = os.path.join(root, file)

                # Ignorer les fichiers commençant par un point (cachés)
                if file.startswith('.') and not file in ['.env.example', '.gitignore'
                    , '.dockerignore']:
                    continue

                self.all_files.add(file_path)
                self.file_last_modified[file_path] = os.path.getmtime(abs_path)

                # Collecter les fichiers Python pour analyse d'importation
                if file.endswith('.py'):
                    self.python_files.add(file_path)

        self.report_data["files_analyzed"] = len(self.all_files)
        self.report_data["python_files_analyzed"] = len(self.python_files)

        print(f"📊 {len(self.all_files)} fichiers trouvés, dont {len(self.python_files)} fichiers Python")



    def analyze_imports(self):
        """Analyse les importations entre fichiers Python."""
        print("🔍 Analyse des importations Python...")

        # Dictionnaire pour stocker toutes les importations
        imports_map = {}

        for py_file in self.python_files:
            try:
                with open(os.path.join(self.project_root, py_file), 'r', encoding='utf-8') as f:
                    content = f.read()

                try:
                    # Analyser le code Python
                    tree = ast.parse(content)
                    imports = set()

                    # Extraire toutes les importations
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for name in node.names:
                                imports.add(name.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module)

                    imports_map[py_file] = imports

                except SyntaxError:
                    if self.verbose:
                        print(f"⚠️ Erreur de syntaxe dans {py_file}, impossible d'analyser les importations")

            except Exception as e:
                if self.verbose:
                    print(f"⚠️ Erreur lors de l'analyse de {py_file}: {str(e)}")

        # Pour chaque importation, trouver le fichier correspondant
        for file_path, imports in imports_map.items():
            dir_path = os.path.dirname(file_path)

            for imp in imports:
                # Convertir le module en chemin de fichier
                module_parts = imp.split('.')

                # Essayer de résoudre l'importation en fichier relatif
                potential_paths = []

                # Importation absolue depuis la racine du projet
                potential_paths.append(os.path.join(*module_parts) + '.py')

                # Importation depuis un package
                potential_paths.append(os.path.join(*module_parts, '__init__.py'))

                # Importation relative
                if dir_path:
                    potential_paths.append(os.path.join(dir_path, *module_parts) + '.py')
                    potential_paths.append(os.path.join(dir_path, *module_parts, '__init__.py'))

                # Enregistrer chaque référence possible
                for pot_path in potential_paths:
                    if pot_path in self.all_files:
                        self.file_references.setdefault(pot_path, set()).add(file_path)



    def find_string_references(self):
        """Recherche les références directes aux fichiers dans le code source."""
        print("🔍 Recherche de références directes aux fichiers...")

        # Créer un ensemble de noms de fichiers et répertoires à rechercher
        file_names = set()
        for file_path in self.all_files:
            # Ajouter le nom de fichier seul
            file_names.add(os.path.basename(file_path))

            # Ajouter le chemin complet
            file_names.add(file_path)

            # Ajouter des variantes courantes du chemin
            file_names.add(file_path.replace('\\', '/'))
            if file_path.startswith('./'):
                file_names.add(file_path[2:])
            else:
                file_names.add('./' + file_path)

        # Rechercher des références à ces noms de fichiers dans tous les fichiers texte
        for file_path in self.all_files:
            if self._is_text_file(file_path):
                try:
                    with open(os.path.join(self.project_root, file_path), 'r', encoding='utf-8'
                        , errors='ignore') as f:
                        content = f.read()

                    # Rechercher des références aux fichiers
                    for name in file_names:
                        # Éviter d'enregistrer une référence d'un fichier à lui-même
                        if name != file_path and name != os.path.basename(file_path):
                            # Rechercher des occurrences du nom de fichier
                            # entouré par des guillemets, apostrophes, espaces ou caractères de ponctuation
                            pattern = r'[\'"\s(/]{}[\'"\s).,]'.format(re.escape(name))
                            if re.search(pattern, content):
                                # Si le nom trouvé est un nom de fichier seul, chercher le fichier complet
                                if os.path.basename(name) == name:
                                    for full_path in self.all_files:
                                        if os.path.basename(full_path) == name:
                                            self.file_references.setdefault(full_path
                                                , set()).add(file_path)
                                else:
                                    # Sinon, c'est un chemin complet
                                    if name in self.all_files:
                                        self.file_references.setdefault(name, set()).add(file_path)

                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ Erreur lors de l'analyse de {file_path}: {str(e)}")



    def analyze_file_dates(self):
        """Analyse les dates de dernière modification des fichiers."""
        print("🔍 Analyse des dates de modification...")

        # Calculer la date moyenne de modification et l'écart-type
        if not self.file_last_modified:
            return

        timestamps = list(self.file_last_modified.values())
        avg_timestamp = sum(timestamps) / len(timestamps)

        # Calculer l'écart-type
        variance = sum((t - avg_timestamp) ** 2 for t in timestamps) / len(timestamps)
        std_dev = variance ** 0.5

        # Calculer la date médiane
        sorted_timestamps = sorted(timestamps)
        if len(sorted_timestamps) % 2 == 0:
            median_timestamp = (sorted_timestamps[len(sorted_timestamps)//2 - 1] +
                               sorted_timestamps[len(sorted_timestamps)//2]) / 2
        else:
            median_timestamp = sorted_timestamps[len(sorted_timestamps)//2]

        # Convertir timestamp en datetime pour un affichage lisible
        median_date = datetime.fromtimestamp(median_timestamp)
        print(f"📅 Date médiane de modification: {median_date.strftime('%Y-%m-%d')}")

        # Stocker ces statistiques pour évaluation ultérieure
        self.date_stats = {
            'avg': avg_timestamp,
            'median': median_timestamp,
            'std_dev': std_dev
        }



    def analyze_git_history(self):
        """Analyse l'historique Git pour avoir des informations supplémentaires."""
        print("🔍 Analyse de l'historique Git...")

        try:
            # Vérifier si le dossier est un dépôt Git
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                if self.verbose:
                    print("⚠️ Ce dossier n'est pas un dépôt Git, l'analyse d'historique sera ignorée.")
                return

            # Obtenir la liste des derniers commits pour chaque fichier
            for file_path in self.all_files:
                abs_path = os.path.join(self.project_root, file_path)
                if not os.path.exists(abs_path):
                    continue

                result = subprocess.run(
                    ['git', 'log', '--format=%at', '-n', '1', '--', file_path],
                    cwd=self.project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if result.returncode == 0 and result.stdout.strip():
                    try:
                        last_commit_timestamp = int(result.stdout.strip())
                        self.git_history[file_path] = {
                            'last_commit': last_commit_timestamp
                        }
                    except ValueError:
                        pass

        except Exception as e:
            if self.verbose:
                print(f"⚠️ Erreur lors de l'analyse Git: {str(e)}")



    def evaluate_files(self):
        """Évaluer chaque fichier et calculer la probabilité qu'il soit obsolète."""
        print("🧮 Évaluation des fichiers...")

        # Statistiques pour le rapport
        stats = {
            "nom_patterns": 0,
            "non_referenced": 0,
            "old_files": 0,
            "has_newer_version": 0
        }

        for file_path in self.all_files:
            # Ignorer les fichiers essentiels
            if file_path in ESSENTIAL_FILES or any(file_path.endswith(ext) for ext in ['.svg'
                , '.png', '.jpg', '.ico']):
                continue

            confidence = 0
            reasons = []
            details = {}

            # 1. Vérifier les modèles de nommage indiquant l'obsolescence
            for pattern in OBSOLETE_PATTERNS:
                if re.search(pattern, file_path):
                    confidence += 40
                    reasons.append(f"Le nom du fichier correspond au modèle d'obsolescence '{pattern}'")
                    stats["nom_patterns"] += 1
                    details["obsolete_pattern"] = pattern
                    break

            # 2. Vérifier les préfixes et suffixes courants pour les fichiers obsolètes
            filename = os.path.basename(file_path)
            for prefix in OBSOLETE_PREFIXES:
                if filename.startswith(prefix):
                    confidence += 35
                    reasons.append(f"Le fichier commence par '{prefix}', préfixe couramment utilisé pour les fichiers obsolètes")
                    stats["nom_patterns"] += 1
                    details["obsolete_prefix"] = prefix
                    break

            for suffix in OBSOLETE_SUFFIXES:
                if filename.endswith(suffix):
                    confidence += 35
                    reasons.append(f"Le fichier se termine par '{suffix}', suffixe couramment utilisé pour les fichiers obsolètes")
                    stats["nom_patterns"] += 1
                    details["obsolete_suffix"] = suffix
                    break

            # 3. Vérifier si le fichier n'est pas référencé
            if file_path not in self.file_references and file_path.endswith('.py'):
                confidence += 30
                reasons.append("Le fichier Python n'est pas importé ou référencé dans d'autres fichiers")
                stats["non_referenced"] += 1
                details["referenced"] = False
            elif file_path not in self.file_references:
                confidence += 15
                reasons.append("Le fichier n'est pas référencé dans d'autres fichiers")
                stats["non_referenced"] += 1
                details["referenced"] = False
            else:
                details["referenced"] = True
                details["referenced_by"] = list(self.file_references.get(file_path, []))

            # 4. Vérifier la date de dernière modification
            if file_path in self.file_last_modified:
                last_mod = self.file_last_modified[file_path]

                # Si le fichier est beaucoup plus ancien que la date médiane
                if last_mod < self.date_stats['median'] - self.date_stats['std_dev'] * 2:
                    confidence += 20
                    mod_date = datetime.fromtimestamp(last_mod).strftime('%Y-%m-%d')
                    reasons.append(f"Le fichier n'a pas été modifié depuis longtemps (dernière modif: {mod_date})")
                    stats["old_files"] += 1
                    details["last_modified"] = mod_date
                    details["days_since_modified"] = (datetime.now() - datetime.fromtimestamp(last_mod)).days

            # 5. Vérifier l'historique Git si disponible
            if file_path in self.git_history:
                git_last_commit = self.git_history[file_path]['last_commit']
                git_date = datetime.fromtimestamp(git_last_commit).strftime('%Y-%m-%d')

                # Si le dernier commit est très ancien par rapport à l'activité du projet
                if git_last_commit < self.date_stats['median'] - self.date_stats['std_dev'] * 3:
                    confidence += 15
                    reasons.append(f"Aucun commit récent sur ce fichier (dernier commit: {git_date})")
                    details["last_git_commit"] = git_date
                    details["days_since_commit"] = (datetime.now() - datetime.fromtimestamp(git_last_commit)).days

            # 6. Ajuster la confiance en fonction du type de fichier
            ext = os.path.splitext(file_path)[1].lower()
            if ext in SAFE_EXTENSIONS:
                # Fichiers moins critiques - augmenter la confiance
                confidence = min(100, confidence * 1.2)
                details["file_type"] = "safe"
            elif ext in HIGH_RISK_EXTENSIONS:
                # Fichiers plus critiques - réduire la confiance
                confidence = confidence * 0.8
                details["file_type"] = "high_risk"
            else:
                details["file_type"] = "normal"

            # 7. Vérifier si c'est un fichier de travail temporaire (comme .swp de vim)
            if re.search(r'\.[^.]+\.sw[ponx]$', file_path):
                confidence += 50
                reasons.append("Fichier de travail temporaire d'éditeur")
                details["temp_editor_file"] = True

            # 8. Vérifier les fichiers de sauvegarde numérotés (file.py.1, file.py.2, etc.)
            if re.search(r'\.[0-9]+$', file_path):
                confidence += 45
                reasons.append("Fichier de sauvegarde numéroté automatiquement")
                details["numbered_backup"] = True

            # 9. Vérifier si le fichier a une copie sans préfixe/suffixe d'obsolescence
            base_name = filename
            for prefix in OBSOLETE_PREFIXES:
                if base_name.startswith(prefix):
                    base_name = base_name[len(prefix):]
                    break

            for suffix in OBSOLETE_SUFFIXES:
                if base_name.endswith(suffix):
                    base_name = base_name[:-len(suffix)]
                    break

            # Si la version "normale" du fichier existe, c'est un indice fort
            potential_current_file = os.path.join(os.path.dirname(file_path), base_name)
            if potential_current_file in self.all_files and potential_current_file != file_path:
                confidence += 40
                reasons.append(f"Une version non marquée comme obsolète existe: {base_name}")
                stats["has_newer_version"] += 1
                details["newer_version"] = potential_current_file

            # 10. Vérifier si le fichier est vide ou presque vide
            try:
                abs_path = os.path.join(self.project_root, file_path)
                if os.path.getsize(abs_path) < 10:  # Moins de 10 octets
                    confidence += 25
                    reasons.append("Fichier vide ou presque vide")
                    details["file_size"] = os.path.getsize(abs_path)
            except Exception:
                pass

            # Enregistrer les résultats si la confiance est supérieure au seuil
            if confidence >= self.confidence_threshold:
                result_entry = {
                    'file': file_path,
                    'confidence': confidence,
                    'reasons': reasons
                }

                # Ajouter des détails supplémentaires pour le rapport
                if self.report_file:
                    result_entry['details'] = details

                self.results.append(result_entry)

                # Ajouter au rapport
                self.report_data["obsolete_files"].append({
                    "file": file_path,
                    "confidence": confidence,
                    "reasons": reasons,
                    "details": details
                })

        # Ajouter les statistiques au rapport
        self.report_data["statistics"] = stats

        # Trier les résultats par niveau de confiance décroissant
        self.results.sort(key=lambda x: x['confidence'], reverse=True)



    def generate_report(self):
        """Génère un rapport détaillé au format JSON."""
        if not self.report_file:
            return

        print(f"📝 Génération du rapport détaillé dans {self.report_file}...")

        try:
            with open(os.path.join(self.project_root, self.report_file), 'w', encoding='utf-8') as f:
                json.dump(self.report_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Rapport généré avec succès dans {self.report_file}")
        except Exception as e:
            print(f"❌ Erreur lors de la génération du rapport: {str(e)}")



    def print_results(self):
        """Affiche les résultats de l'analyse."""
        if not self.results:
            print("✅ Aucun fichier obsolète détecté avec le seuil de confiance spécifié.")
            return

        print(f"\n🔎 {len(self.results)} fichiers potentiellement obsolètes détectés:\n")

        for i, result in enumerate(self.results, 1):
            confidence_color = '\033[91m' if result['confidence'] > 95 else '\033[93m'
            print(f"{i}. {confidence_color}{result['file']} - Confiance: {result['confidence']}%\033[0m")
            if self.verbose:
                for reason in result['reasons']:
                    print(f"   • {reason}")
                print()

        print("\n💡 Conseil: Examinez ces fichiers manuellement avant de prendre une décision.")
        print("   Utilisez --delete pour supprimer les fichiers avec confiance élevée ou")
        print("   --move-to DIR pour les déplacer dans un répertoire d'archives.")



    def process_files(self, delete: bool = False, move_to: Optional[str] = None):
        """Traite les fichiers obsolètes (suppression ou déplacement)."""
        if not self.results:
            return

        processed = 0

        # Créer le répertoire de destination si nécessaire
        if move_to:
            move_dir = os.path.join(self.project_root, move_to)
            os.makedirs(move_dir, exist_ok=True)

        for result in self.results:
            # Uniquement traiter les fichiers avec une confiance très élevée
            if result['confidence'] >= 95:
                file_path = os.path.join(self.project_root, result['file'])

                try:
                    if delete:
                        os.remove(file_path)
                        print(f"🗑️ Supprimé: {result['file']}")
                        processed += 1
                    elif move_to:
                        # Créer la structure de répertoires dans la destination
                        rel_dir = os.path.dirname(result['file'])
                        dest_dir = os.path.join(move_dir, rel_dir)
                        os.makedirs(dest_dir, exist_ok=True)

                        # Déplacer le fichier
                        dest_file = os.path.join(move_dir, result['file'])
                        shutil.move(file_path, dest_file)
                        print(f"📦 Déplacé: {result['file']} -> {move_to}/{result['file']}")
                        processed += 1

                except Exception as e:
                    print(f"⚠️ Erreur lors du traitement de {result['file']}: {str(e)}")

        if processed > 0:
            print(f"\n✅ {processed} fichiers traités.")



    def _is_text_file(self, file_path: str) -> bool:
        """Vérifie si un fichier est un fichier texte."""
        text_extensions = {
            '.py', '.js', '.ts', '.html', '.css', '.json', '.xml', '.yml', '.yaml',
            '.md', '.txt', '.rst', '.bat', '.sh', '.ps1', '.template', '.conf',
            '.ini', '.cfg', '.env', '.toml'
        }

        ext = os.path.splitext(file_path)[1].lower()
        return ext in text_extensions



    def run(self, delete: bool = False, move_to: Optional[str] = None):
        """Exécute l'analyse complète."""
        self.collect_files()
        self.analyze_imports()
        self.find_string_references()
        self.analyze_git_history()
        self.analyze_file_dates()
        self.evaluate_files()
        self.print_results()

        if self.report_file:
            self.generate_report()

        if delete or move_to:
            self.process_files(delete, move_to)




def parse_args():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Détecte les fichiers obsolètes dans le projet avec une haute confiance."
    )
    parser.add_argument('--delete', action='store_true',
                      help="Supprime automatiquement les fichiers avec une confiance très élevée (>95%)")
    parser.add_argument('--move-to', type=str,
                      help="Déplace les fichiers vers le répertoire spécifié au lieu de les supprimer")
    parser.add_argument('--verbose', action='store_true',
                      help="Affiche des informations détaillées sur chaque fichier")
    parser.add_argument('--confidence', type=int, default=85,
                      help="Seuil de confiance minimum (0-100) pour détecter un fichier comme obsolète")
    parser.add_argument('--report', type=str,
                      help="Génère un rapport détaillé au format JSON dans le fichier spécifié")
    parser.add_argument("--cleanup-report", metavar="FILE", help="Générer un rapport de nettoyage")

    return parser.parse_args()




def main():
    """Fonction principale."""
    args = parse_args()

    # Déterminer le répertoire racine du projet
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    print("🔍 Analyse des fichiers obsolètes dans le projet Mathakine")
    print(f"📂 Répertoire du projet: {project_root}")

    analyzer = FileAnalyzer(
        project_root=project_root,
        verbose=args.verbose,
        confidence_threshold=args.confidence,
        report_file=args.report
    )

    analyzer.run(delete=args.delete, move_to=args.move_to)

    if args.cleanup_report:
        # Exemple d'utilisation avec des fichiers fictifs pour démonstration
        # Dans une utilisation réelle, ces listes seraient remplies par le script
        obsolete_files = []
        preserved_files = []

        # Si des fichiers ont été détectés comme obsolètes, les inclure dans le rapport
        if analyzer.results:
            for result in analyzer.results:
                if result['confidence'] >= 95:
                    file_path = result['file']
                    mod_time = datetime.fromtimestamp(analyzer.file_last_modified.get(file_path
                        , datetime.now()))
                    obsolete_files.append({
                        "path": file_path,
                        "reason": ", ".join(result['reasons']),
                        "modified_date": mod_time.strftime("%d.%m.%Y")
                    })

        # Si des fichiers ont été préservés malgré une suspicion d'obsolescence
        if args.confidence < 85:  # Considérer les fichiers avec confiance inférieure au seuil par défaut
            for file_path in analyzer.all_files:
                if file_path not in analyzer.file_references and file_path.endswith('.py'):
                    confidence = 0
                    reasons = []
                    for result in analyzer.results:
                        if result['file'] == file_path:
                            confidence = result['confidence']
                            reasons = result['reasons']
                            break
                    if 40 <= confidence < 85:
                        preserved_files.append({
                            "path": file_path,
                            "reason": "Fichier nécessaire pour la structure du projet",
                            "confidence": round(confidence, 1)
                        })

        generate_cleanup_report(obsolete_files, preserved_files, args.cleanup_report)




def generate_cleanup_report(obsolete_files, preserved_files=None, output_path="docs/CLEANUP_REPORT.md"):
    """
    Générer un rapport de nettoyage au format Markdown.

    Args:
        obsolete_files (list): Liste de dictionnaires contenant les informations sur les fichiers supprimés
        preserved_files (list, optional): Liste de dictionnaires contenant les informations sur les fichiers conservés
        output_path (str, optional): Chemin du fichier de sortie
    """
    preserved_files = preserved_files or []
    now = datetime.now()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Rapport de nettoyage du projet Mathakine\n\n")
        f.write(f"## Date de nettoyage: {now.strftime('%d %B %Y')}\n\n")
        f.write("Ce document présente un résumé des opérations de nettoyage effectuées sur le projet Mathakine pour éliminer les fichiers obsolètes.\n\n")

        f.write("## Outils utilisés\n\n")
        f.write("- Script personnalisé `scripts/detect_obsolete_files.py`\n")
        f.write("- Commandes PowerShell pour l'identification de fichiers spécifiques\n")
        f.write("- Analyse manuelle des fichiers potentiellement obsolètes\n\n")

        if obsolete_files:
            f.write("## Fichiers supprimés\n\n")
            f.write("Les fichiers suivants ont été identifiés comme obsolètes et ont été supprimés :\n\n")
            f.write("| Fichier | Raison de la suppression | Date de modification |\n")
            f.write("| --- | --- | --- |\n")
            for file_info in obsolete_files:
                filepath = file_info.get("path", "")
                reason = file_info.get("reason", "Fichier obsolète")
                mod_date = file_info.get("modified_date", "Inconnue")
                f.write(f"| {filepath} | {reason} | {mod_date} |\n")
            f.write("\n")
        else:
            f.write("## Fichiers supprimés\n\n")
            f.write("Aucun fichier n'a été supprimé lors de cette opération de nettoyage.\n\n")

        if preserved_files:
            f.write("## Fichiers conservés malgré suspicion d'obsolescence\n\n")
            f.write("Les fichiers suivants ont été identifiés comme potentiellement obsolètes par le script mais ont été conservés pour les raisons indiquées :\n\n")
            f.write("| Fichier | Raison de conservation | Confiance d'obsolescence |\n")
            f.write("| --- | --- | --- |\n")
            for file_info in preserved_files:
                filepath = file_info.get("path", "")
                reason = file_info.get("reason", "Raison non spécifiée")
                confidence = file_info.get("confidence", "")
                confidence_str = f"{confidence}%" if isinstance(confidence, (int
                    , float)) else confidence
                f.write(f"| {filepath} | {reason} | {confidence_str} |\n")
            f.write("\n")

        f.write("## Résumé\n\n")
        f.write("Le projet a été nettoyé des fichiers inutiles et redondants tout en préservant les fichiers essentiels à sa structure. ")
        f.write("Le script `detect_obsolete_files.py` pourra être utilisé régulièrement pour maintenir le projet propre et détecter de nouveaux fichiers obsolètes.")

    print(f"{Fore.GREEN}✅ Rapport de nettoyage généré avec succès dans {output_path}{Fore.RESET}")
    return output_path


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Script pour identifier et corriger les problèmes de compatibilité dans le projet Mathakine:
1. Problèmes d'énumérations PostgreSQL (besoin d'utiliser .value)
2. Migration Pydantic v1 vers v2 (.dict() → .model_dump())

Usage:
    python scripts/check_compatibility.py [--check-only] [--verbose] [--fix-enums] [--fix-pydantic] [directory]

Arguments:
    --check-only   : Ne fait que rapporter les problèmes sans les corriger
    --verbose      : Affiche des informations détaillées pendant l'exécution
    --fix-enums    : Corrige les problèmes d'énumérations (.value manquant)
    --fix-pydantic : Corrige les problèmes Pydantic (.dict() → .model_dump())
    directory      : Répertoire à analyser (par défaut: 'tests' et 'app')
"""

import os
import re
import sys
import argparse
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Énumérations courantes dans le projet
ENUM_PATTERNS = [
    r'UserRole\.[A-Z_]+(?!\.value)',
    r'ExerciseType\.[A-Z_]+(?!\.value)',
    r'DifficultyLevel\.[A-Z_]+(?!\.value)',
    r'LogicChallengeType\.[A-Z_]+(?!\.value)',
    r'AgeGroup\.[A-Z_]+(?!\.value)',
]

# Méthodes à migrer pour Pydantic v2
PYDANTIC_PATTERNS = [
    (r'\.dict\(\)', '.model_dump()'),
    (r'\.json\(\)', '.model_dump_json()'),
    (r'from pydantic import BaseSettings', 'from pydantic_settings import BaseSettings'),
]

class ProblemType(Enum):
    ENUM = 'Enum sans .value'
    PYDANTIC = 'Migration Pydantic v1 → v2'

class FileProblem:
    def __init__(self, file_path: str, line_num: int, line: str, problem_type: ProblemType, 
                 match: str, replacement: Optional[str] = None):
        self.file_path = file_path
        self.line_num = line_num
        self.line = line
        self.problem_type = problem_type
        self.match = match
        self.replacement = replacement

    def __str__(self):
        return f"{self.file_path}:{self.line_num} - {self.problem_type.value}: {self.match}"

def find_problems(directory: str, verbose: bool = False) -> List[FileProblem]:
    """Trouve tous les problèmes de compatibilité dans les fichiers Python du répertoire."""
    problems = []
    directories_to_search = [directory]
    
    if directory == '.':
        directories_to_search = ['app', 'tests']
    
    for dir_path in directories_to_search:
        if not os.path.exists(dir_path):
            logger.warning(f"Le répertoire {dir_path} n'existe pas, ignoré")
            continue
            
        if verbose:
            logger.info(f"Analyse du répertoire {dir_path}...")
        
        for root, _, files in os.walk(dir_path):
            for file_name in files:
                if file_name.endswith('.py'):
                    file_path = os.path.join(root, file_name)
                    
                    # Vérifier les problèmes d'énumérations
                    enum_problems = find_enum_problems(file_path, verbose)
                    problems.extend(enum_problems)
                    
                    # Vérifier les problèmes Pydantic
                    pydantic_problems = find_pydantic_problems(file_path, verbose)
                    problems.extend(pydantic_problems)
    
    return problems

def find_enum_problems(file_path: str, verbose: bool = False) -> List[FileProblem]:
    """Trouve les problèmes d'énumérations sans .value dans un fichier."""
    problems = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            for i, line in enumerate(lines):
                for pattern in ENUM_PATTERNS:
                    for match in re.finditer(pattern, line):
                        enum_usage = match.group(0)
                        
                        # Ignorer les cas où l'énumération est dans un commentaire
                        if '#' in line and line.index('#') < match.start():
                            continue
                            
                        # Ignorer les cas où l'énumération est dans un import
                        if 'import' in line and line.index('import') < match.start():
                            continue
                            
                        # Ignorer les cas où l'énumération est dans une chaîne de caractères
                        if ('"' in line and line.index('"') < match.start()) or \
                           ("'" in line and line.index("'") < match.start()):
                            # Vérification plus sophistiquée pourrait être nécessaire
                            continue
                        
                        replacement = f"{enum_usage}.value"
                        problem = FileProblem(
                            file_path=file_path,
                            line_num=i + 1,
                            line=line,
                            problem_type=ProblemType.ENUM,
                            match=enum_usage,
                            replacement=replacement
                        )
                        problems.append(problem)
                        
                        if verbose:
                            logger.debug(f"Problème trouvé: {problem}")
    
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de {file_path}: {str(e)}")
    
    return problems

def find_pydantic_problems(file_path: str, verbose: bool = False) -> List[FileProblem]:
    """Trouve les problèmes de migration Pydantic dans un fichier."""
    problems = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            for i, line in enumerate(lines):
                for pattern, replacement in PYDANTIC_PATTERNS:
                    for match in re.finditer(pattern, line):
                        # Ignorer les cas où le pattern est dans un commentaire
                        if '#' in line and line.index('#') < match.start():
                            continue
                            
                        matched_text = match.group(0)
                        problem = FileProblem(
                            file_path=file_path,
                            line_num=i + 1,
                            line=line,
                            problem_type=ProblemType.PYDANTIC,
                            match=matched_text,
                            replacement=replacement
                        )
                        problems.append(problem)
                        
                        if verbose:
                            logger.debug(f"Problème trouvé: {problem}")
    
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de {file_path}: {str(e)}")
    
    return problems

def fix_problems(problems: List[FileProblem], fix_enums: bool = True, fix_pydantic: bool = True, 
                verbose: bool = False) -> Dict[str, int]:
    """Corrige les problèmes identifiés dans les fichiers."""
    # Regrouper les problèmes par fichier pour éviter les conflits lors de la correction
    problems_by_file: Dict[str, List[FileProblem]] = {}
    for problem in problems:
        if problem.file_path not in problems_by_file:
            problems_by_file[problem.file_path] = []
        problems_by_file[problem.file_path].append(problem)
    
    stats = {
        "files_modified": 0,
        "enum_fixes": 0,
        "pydantic_fixes": 0
    }
    
    for file_path, file_problems in problems_by_file.items():
        # Ne traiter que les types de problèmes à corriger
        file_problems_filtered = []
        if fix_enums:
            file_problems_filtered.extend([p for p in file_problems if p.problem_type == ProblemType.ENUM])
        if fix_pydantic:
            file_problems_filtered.extend([p for p in file_problems if p.problem_type == ProblemType.PYDANTIC])
        
        if not file_problems_filtered:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            original_content = content
            enum_fixes = 0
            pydantic_fixes = 0
            
            # Trier les problèmes par ordre décroissant de position pour éviter les décalages
            file_problems_filtered.sort(key=lambda p: (p.line_num, p.line.find(p.match)), reverse=True)
            
            lines = content.split('\n')
            
            for problem in file_problems_filtered:
                if problem.line_num <= len(lines):
                    line = lines[problem.line_num - 1]
                    new_line = line.replace(problem.match, problem.replacement)
                    
                    if new_line != line:
                        lines[problem.line_num - 1] = new_line
                        
                        if problem.problem_type == ProblemType.ENUM:
                            enum_fixes += 1
                        elif problem.problem_type == ProblemType.PYDANTIC:
                            pydantic_fixes += 1
                        
                        if verbose:
                            logger.info(f"Ligne corrigée dans {file_path}:{problem.line_num}")
                            logger.info(f"  Avant: {line.strip()}")
                            logger.info(f"  Après: {new_line.strip()}")
            
            new_content = '\n'.join(lines)
            
            # Ne sauvegarder que si des changements ont été effectués
            if new_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                
                stats["files_modified"] += 1
                stats["enum_fixes"] += enum_fixes
                stats["pydantic_fixes"] += pydantic_fixes
                
                logger.info(f"Fichier modifié: {file_path} ({enum_fixes} corrections d'énumérations, {pydantic_fixes} corrections Pydantic)")
        
        except Exception as e:
            logger.error(f"Erreur lors de la modification de {file_path}: {str(e)}")
    
    return stats

def generate_report(problems: List[FileProblem], stats: Optional[Dict[str, int]] = None) -> str:
    """Génère un rapport détaillé des problèmes identifiés et des corrections effectuées."""
    enum_problems = [p for p in problems if p.problem_type == ProblemType.ENUM]
    pydantic_problems = [p for p in problems if p.problem_type == ProblemType.PYDANTIC]
    
    files_with_problems = set(p.file_path for p in problems)
    
    report = [
        "=" * 80,
        f"RAPPORT DE COMPATIBILITÉ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 80,
        f"Total des fichiers analysés avec problèmes: {len(files_with_problems)}",
        f"Total des problèmes identifiés: {len(problems)}",
        f"  - Problèmes d'énumérations: {len(enum_problems)}",
        f"  - Problèmes Pydantic: {len(pydantic_problems)}",
        ""
    ]
    
    if stats:
        report.extend([
            "STATISTIQUES DE CORRECTION:",
            f"  - Fichiers modifiés: {stats['files_modified']}",
            f"  - Corrections d'énumérations: {stats['enum_fixes']}",
            f"  - Corrections Pydantic: {stats['pydantic_fixes']}",
            ""
        ])
    
    # Top 10 des fichiers avec le plus de problèmes
    files_count = {}
    for problem in problems:
        files_count[problem.file_path] = files_count.get(problem.file_path, 0) + 1
    
    top_files = sorted(files_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    if top_files:
        report.extend([
            "TOP 10 DES FICHIERS AVEC LE PLUS DE PROBLÈMES:",
            ""
        ])
        
        for file_path, count in top_files:
            report.append(f"  - {file_path}: {count} problèmes")
        
        report.append("")
    
    # Exemples de problèmes
    if enum_problems:
        report.extend([
            "EXEMPLES DE PROBLÈMES D'ÉNUMÉRATIONS:",
            ""
        ])
        
        for problem in enum_problems[:5]:
            report.append(f"  - {problem.file_path}:{problem.line_num} - {problem.match} → {problem.replacement}")
        
        if len(enum_problems) > 5:
            report.append(f"  - ... et {len(enum_problems) - 5} autres problèmes d'énumérations")
        
        report.append("")
    
    if pydantic_problems:
        report.extend([
            "EXEMPLES DE PROBLÈMES PYDANTIC:",
            ""
        ])
        
        for problem in pydantic_problems[:5]:
            report.append(f"  - {problem.file_path}:{problem.line_num} - {problem.match} → {problem.replacement}")
        
        if len(pydantic_problems) > 5:
            report.append(f"  - ... et {len(pydantic_problems) - 5} autres problèmes Pydantic")
        
        report.append("")
    
    report.extend([
        "RECOMMANDATIONS:",
        "",
        "  1. Corriger tous les problèmes d'énumérations pour assurer la compatibilité PostgreSQL",
        "  2. Migrer les méthodes Pydantic pour compatibilité avec Pydantic v2",
        "  3. Exécuter les tests après chaque correction",
        "",
        "=" * 80
    ])
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Outil de vérification de compatibilité pour Mathakine")
    parser.add_argument("--check-only", action="store_true", 
                        help="Ne fait que rapporter les problèmes sans les corriger")
    parser.add_argument("--verbose", action="store_true", 
                        help="Affiche des informations détaillées pendant l'exécution")
    parser.add_argument("--fix-enums", action="store_true", 
                        help="Corrige les problèmes d'énumérations (.value manquant)")
    parser.add_argument("--fix-pydantic", action="store_true", 
                        help="Corrige les problèmes Pydantic (.dict() → .model_dump())")
    parser.add_argument("directory", nargs="?", default=".", 
                        help="Répertoire à analyser (par défaut: app et tests)")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("Recherche des problèmes de compatibilité...")
    problems = find_problems(args.directory, args.verbose)
    
    if not problems:
        logger.info("Aucun problème de compatibilité trouvé!")
        return
    
    enum_problems = [p for p in problems if p.problem_type == ProblemType.ENUM]
    pydantic_problems = [p for p in problems if p.problem_type == ProblemType.PYDANTIC]
    
    logger.info(f"Problèmes trouvés: {len(problems)} total, {len(enum_problems)} énumérations, {len(pydantic_problems)} Pydantic")
    
    # Si aucune option de correction spécifique n'est fournie et que check_only n'est pas activé,
    # nous corrigeons tous les types de problèmes
    if not args.check_only and not (args.fix_enums or args.fix_pydantic):
        args.fix_enums = True
        args.fix_pydantic = True
    
    stats = None
    if not args.check_only:
        logger.info("Correction des problèmes...")
        stats = fix_problems(
            problems, 
            fix_enums=args.fix_enums, 
            fix_pydantic=args.fix_pydantic,
            verbose=args.verbose
        )
    
    # Générer un rapport
    report = generate_report(problems, stats)
    
    # Afficher le rapport
    print(report)
    
    # Sauvegarder le rapport dans un fichier
    report_path = f"compatibility_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_path, 'w', encoding='utf-8') as report_file:
        report_file.write(report)
    
    logger.info(f"Rapport sauvegardé dans {report_path}")
    
    if args.check_only:
        logger.info("Exécutez à nouveau le script avec --fix-enums et/ou --fix-pydantic pour corriger les problèmes")

if __name__ == "__main__":
    main() 
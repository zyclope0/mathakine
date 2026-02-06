#!/usr/bin/env python3
"""
Script d'analyse exhaustive des variables Phase 6.
Détecte toutes les variables cryptiques à renommer.
"""
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Patterns de détection
PATTERNS = {
    "exception_e": re.compile(r"except\s+(\w+)\s+as\s+e:"),
    "db_variable": re.compile(r"\bdb\s*="),
    "idx_variable": re.compile(r"\bidx\b"),
    "conn_variable": re.compile(r"\bconn\s*="),
    "row_variable": re.compile(r"\brow\s*="),
    "tmp_variable": re.compile(r"\b(tmp|temp)\s*="),
    "single_char": re.compile(r"\b[a-z]\s*="),
}

def analyze_file(filepath: Path) -> Dict:
    """Analyse un fichier Python pour les variables cryptiques."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return {"error": str(e)}
    
    results = defaultdict(list)
    
    for line_num, line in enumerate(lines, 1):
        # Skip commentaires et docstrings
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        
        # Vérifier chaque pattern
        for pattern_name, pattern in PATTERNS.items():
            if pattern.search(line):
                results[pattern_name].append({
                    "line_num": line_num,
                    "line": line.strip()
                })
    
    return {
        "filepath": str(filepath),
        "results": dict(results),
        "total": sum(len(v) for v in results.values())
    }

def main():
    """Lance l'analyse sur app/ et server/."""
    print("=" * 80)
    print("PHASE 6 - ANALYSE EXHAUSTIVE DES VARIABLES")
    print("=" * 80)
    print()
    
    directories = ["app", "server"]
    all_results = []
    
    # Analyser tous les fichiers
    for directory in directories:
        if not Path(directory).exists():
            print(f"[!] Dossier {directory}/ non trouve, skip")
            continue
        
        for py_file in Path(directory).rglob("*.py"):
            result = analyze_file(py_file)
            if result.get("results"):
                all_results.append(result)
    
    if not all_results:
        print("[OK] Aucune variable cryptique trouvee !")
        return
    
    # Statistiques globales
    print("[STATS] STATISTIQUES GLOBALES")
    print("-" * 80)
    print(f"Fichiers avec variables cryptiques : {len(all_results)}")
    
    total_by_type = defaultdict(int)
    for result in all_results:
        for pattern_name, occurrences in result["results"].items():
            total_by_type[pattern_name] += len(occurrences)
    
    print(f"\nTotal par type :")
    for pattern_name, count in sorted(total_by_type.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {pattern_name:20s} : {count:3d} occurrences")
    
    total = sum(total_by_type.values())
    print(f"\n[TOTAL] VARIABLES A RENOMMER : {total}")
    
    # Top 10 fichiers
    print(f"\n[TOP 10] FICHIERS AVEC LE PLUS DE VARIABLES CRYPTIQUES")
    print("-" * 80)
    sorted_results = sorted(all_results, key=lambda x: x["total"], reverse=True)[:10]
    for i, result in enumerate(sorted_results, 1):
        filepath = result["filepath"]
        total = result["total"]
        print(f"{i:2d}. {filepath:60s} : {total:3d} variables")
    
    # Détail par pattern
    print(f"\n[DETAIL] PAR PATTERN")
    print("-" * 80)
    
    for pattern_name in sorted(total_by_type.keys()):
        count = total_by_type[pattern_name]
        print(f"\n[{pattern_name.upper()}] ({count} occurrences)")
        print("-" * 80)
        
        # Afficher 5 premiers exemples
        examples = []
        for result in all_results:
            if pattern_name in result["results"]:
                for occ in result["results"][pattern_name][:2]:  # 2 par fichier max
                    examples.append({
                        "file": result["filepath"],
                        "line_num": occ["line_num"],
                        "line": occ["line"]
                    })
                    if len(examples) >= 5:
                        break
            if len(examples) >= 5:
                break
        
        for ex in examples:
            print(f"  {ex['file']}:{ex['line_num']}")
            print(f"    {ex['line']}")
    
    # Sauvegarder rapport
    print(f"\n[SAVE] Sauvegarde du rapport...")
    with open("phase6_variables_report.txt", "w", encoding="utf-8") as f:
        f.write("PHASE 6 - ANALYSE VARIABLES\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total variables à renommer : {total}\n")
        f.write(f"Fichiers concernés : {len(all_results)}\n\n")
        
        f.write("PAR TYPE :\n")
        for pattern_name, count in sorted(total_by_type.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  - {pattern_name:20s} : {count:3d}\n")
        
        f.write("\n\nDÉTAIL PAR FICHIER :\n")
        f.write("=" * 80 + "\n")
        
        for result in sorted(all_results, key=lambda x: x["total"], reverse=True):
            f.write(f"\n{result['filepath']} ({result['total']} variables)\n")
            f.write("-" * 80 + "\n")
            for pattern_name, occurrences in result["results"].items():
                f.write(f"\n  {pattern_name} :\n")
                for occ in occurrences:
                    f.write(f"    Ligne {occ['line_num']:4d} : {occ['line']}\n")
    
    print(f"[OK] Rapport sauvegarde dans phase6_variables_report.txt")
    print()
    print("[GO] Pret pour le renommage !")

if __name__ == "__main__":
    main()


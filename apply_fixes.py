"""
Ce script applique les correctifs au fichier enhanced_server.py
"""

import re
import os
import sys

def main():
    print("Application des correctifs à enhanced_server.py...")
    
    # Vérifier si les fichiers de correctifs existent
    required_files = [
        "temp_fix.py",
        "temp_fix_get_exercises_list.py", 
        "temp_fix_get_user_stats.py"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"Erreur: Le fichier {file} est manquant!")
            return 1
    
    # Lire le fichier original
    with open("enhanced_server.py", "r", encoding="utf-8") as f:
        original_content = f.read()
    
    # Créer une sauvegarde
    with open("enhanced_server.py.bak", "w", encoding="utf-8") as f:
        f.write(original_content)
    print("Sauvegarde créée: enhanced_server.py.bak")
    
    # Lire les correctifs
    with open("temp_fix.py", "r", encoding="utf-8") as f:
        submit_answer_fix = f.read()
    
    with open("temp_fix_get_exercises_list.py", "r", encoding="utf-8") as f:
        get_exercises_list_fix = f.read()
    
    with open("temp_fix_get_user_stats.py", "r", encoding="utf-8") as f:
        get_user_stats_fix = f.read()
    
    # Extraire les fonctions corrigées (sans le commentaire de documentation)
    submit_answer_function = re.search(r'async def submit_answer\(request\):(.*?)(?=\n\n)', submit_answer_fix, re.DOTALL).group(0)
    get_exercises_list_function = re.search(r'async def get_exercises_list\(request\):(.*?)(?=\n\n)', get_exercises_list_fix, re.DOTALL).group(0)
    get_user_stats_function = re.search(r'async def get_user_stats\(request\):(.*?)(?=\n\n)', get_user_stats_fix, re.DOTALL).group(0)
    
    # Appliquer les correctifs
    # 1. Remplacer submit_answer
    pattern_submit = r'async def submit_answer\(request\):.*?(?=async def|def|$)'
    content = re.sub(pattern_submit, submit_answer_function, original_content, flags=re.DOTALL)
    
    # 2. Remplacer get_exercises_list
    pattern_exercises = r'async def get_exercises_list\(request\):.*?(?=async def|def|$)'
    content = re.sub(pattern_exercises, get_exercises_list_function, content, flags=re.DOTALL)
    
    # 3. Remplacer get_user_stats
    pattern_stats = r'async def get_user_stats\(request\):.*?(?=async def|def|$)'
    content = re.sub(pattern_stats, get_user_stats_function, content, flags=re.DOTALL)
    
    # Écrire le fichier corrigé
    with open("enhanced_server.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("Correctifs appliqués avec succès!")
    print("Vous pouvez maintenant démarrer le serveur avec: python mathakine_cli.py run")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
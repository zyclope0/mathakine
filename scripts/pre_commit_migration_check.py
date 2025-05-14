#!/usr/bin/env python
"""
Script de vérification des migrations Alembic avant commit.
Ce script:
1. Analyse les migrations qui ne sont pas encore commitées
2. Vérifie qu'elles ne contiennent pas d'opérations dangereuses
3. Sort avec un code d'erreur si des problèmes sont détectés

Conçu pour être utilisé comme hook pre-commit Git.
Installation: 
1. Copiez ce fichier dans .git/hooks/pre-commit ou 
2. Créez un lien symbolique: ln -s ../../scripts/pre_commit_migration_check.py .git/hooks/pre-commit
3. Rendez-le exécutable: chmod +x .git/hooks/pre-commit
"""
import os
import sys
import re
import subprocess
from pathlib import Path

# Ajouter le répertoire parent au sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Constantes
MIGRATIONS_DIR = os.path.join(BASE_DIR, "migrations", "versions")

# Liste des opérations considérées comme risquées
RISKY_OPERATIONS = [
    (r'op\.drop_table\([\'"]([^\'"]+)[\'"]\)', "Suppression de table"),
    (r'op\.drop_column\([\'"]([^\'"]+)[\'"],\s*[\'"]([^\'"]+)[\'"]\)', "Suppression de colonne"),
    (r'op\.alter_column\([\'"]([^\'"]+)[\'"],\s*[\'"]([^\'"]+)[\'"]\s*.*not_nullable=True', "Ajout de NOT NULL"),
    (r'op\.rename_table\([\'"]([^\'"]+)[\'"],\s*[\'"]([^\'"]+)[\'"]\)', "Renommage de table"),
    (r'op\.execute\([\'"]DROP', "Exécution directe de DROP"),
    (r'op\.execute\([\'"]TRUNCATE', "Exécution directe de TRUNCATE"),
    (r'op\.execute\([\'"]ALTER\s+TABLE.*DROP\s+CONSTRAINT', "Suppression de contrainte"),
]

# Tables protégées que nous ne voulons jamais modifier sans confirmation explicite
PROTECTED_TABLES = {'results', 'statistics', 'user_stats', 'schema_version', 'exercises', 'users', 'attempts'}

def get_modified_migrations():
    """
    Récupère la liste des fichiers de migration modifiés mais non commitées.
    """
    try:
        # Récupérer les fichiers modifiés
        git_cmd = ['git', 'diff', '--name-only', '--cached']
        result = subprocess.run(git_cmd, capture_output=True, text=True, check=True)
        modified_files = result.stdout.splitlines()
        
        # Filtrer pour ne garder que les fichiers de migration
        migrations = []
        for file in modified_files:
            if file.startswith('migrations/versions/') and file.endswith('.py'):
                migrations.append(file)
        
        return migrations
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la récupération des fichiers modifiés: {e}")
        return []

def check_migration_file(filepath):
    """
    Vérifie qu'un fichier de migration ne contient pas d'opérations risquées.
    
    Returns:
        tuple: (is_safe, warnings) où is_safe est un booléen et warnings est une liste de chaînes
    """
    # S'assurer que le chemin est absolu
    if not os.path.isabs(filepath):
        filepath = os.path.join(BASE_DIR, filepath)
    
    if not os.path.exists(filepath):
        print(f"Le fichier {filepath} n'existe pas")
        return False, [f"Le fichier {filepath} est introuvable"]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    warnings = []
    
    # Vérifier chaque type d'opération risquée
    for pattern, description in RISKY_OPERATIONS:
        matches = re.findall(pattern, content)
        if matches:
            for match in matches:
                if isinstance(match, tuple):  # Pour les patterns avec plusieurs groupes
                    table_name = match[0]
                    column_name = match[1] if len(match) > 1 else ""
                    operation = f"{description} sur {table_name}.{column_name}" if column_name else f"{description} sur {table_name}"
                else:  # Pour les patterns avec un seul groupe
                    table_name = match
                    operation = f"{description} sur {table_name}"
                
                # Vérifier si c'est une table protégée
                if table_name in PROTECTED_TABLES:
                    warnings.append(f"🚨 CRITIQUE: {operation} (Table protégée)")
                else:
                    warnings.append(f"⚠️ RISQUE: {operation}")
    
    # Rechercher des suppressions d'index, de contraintes, etc.
    additional_patterns = [
        (r'op\.drop_constraint\([\'"]([^\'"]+)[\'"]\)', "Suppression de contrainte"),
        (r'op\.drop_index\([\'"]([^\'"]+)[\'"]\)', "Suppression d'index"),
    ]
    
    for pattern, description in additional_patterns:
        matches = re.findall(pattern, content)
        if matches:
            for match in matches:
                warnings.append(f"⚠️ ATTENTION: {description} {match}")
    
    return len(warnings) == 0, warnings

def main():
    """
    Fonction principale qui vérifie toutes les migrations modifiées.
    """
    print("Vérification des migrations Alembic avant commit...")
    
    # Récupérer les migrations modifiées
    migrations = get_modified_migrations()
    if not migrations:
        print("Aucune migration modifiée détectée.")
        return 0
    
    print(f"{len(migrations)} migration(s) à vérifier:")
    
    all_safe = True
    for migration in migrations:
        print(f"\nVérification de {migration}...")
        is_safe, warnings = check_migration_file(migration)
        
        if not is_safe:
            all_safe = False
            print("⚠️ Avertissements:")
            for warning in warnings:
                print(f"  - {warning}")
        else:
            print("✅ Aucune opération risquée détectée.")
    
    if not all_safe:
        print("\n🚨 Des opérations risquées ont été détectées dans les migrations!")
        print("Pour ignorer ces avertissements et forcer le commit, utilisez l'option --no-verify:")
        print("    git commit --no-verify -m \"Votre message de commit\"")
        print("\nATTENTION: Assurez-vous de comprendre les risques avant de forcer un commit.")
        return 1
    
    print("\n✅ Toutes les migrations sont sécurisées.")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
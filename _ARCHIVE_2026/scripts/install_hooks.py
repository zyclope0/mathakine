#!/usr/bin/env python3
"""
Script d'installation des hooks Git pour Mathakine
"""

import os
import shutil
import stat
from pathlib import Path

def main():
    """Installe les hooks Git pre-commit et post-commit"""
    
    # Trouver le répertoire racine du projet (contenant .git)
    project_root = Path.cwd()
    while not (project_root / '.git').exists():
        project_root = project_root.parent
        if project_root == project_root.parent:  # Atteint la racine du système de fichiers
            print("❌ Erreur: Répertoire .git non trouvé. Êtes-vous dans un projet Git?")
            return 1
    
    # Vérifier que les fichiers de hooks existent
    pre_commit_file = Path.cwd() / 'pre-commit'
    post_commit_file = Path.cwd() / 'post-commit'
    
    if not pre_commit_file.exists() or not post_commit_file.exists():
        print("❌ Erreur: Fichiers de hooks non trouvés. Assurez-vous d'exécuter ce script dans le même répertoire que pre-commit et post-commit.")
        return 1
    
    # Chemin des hooks Git
    git_hooks_dir = project_root / '.git' / 'hooks'
    if not git_hooks_dir.exists():
        print(f"❌ Erreur: Répertoire {git_hooks_dir} non trouvé.")
        return 1
    
    # Créer une sauvegarde des hooks existants
    pre_commit_target = git_hooks_dir / 'pre-commit'
    post_commit_target = git_hooks_dir / 'post-commit'
    
    if pre_commit_target.exists():
        backup_file = pre_commit_target.with_suffix('.bak')
        print(f"📦 Sauvegarde de l'ancien pre-commit hook vers {backup_file}")
        shutil.copy2(pre_commit_target, backup_file)
    
    if post_commit_target.exists():
        backup_file = post_commit_target.with_suffix('.bak')
        print(f"📦 Sauvegarde de l'ancien post-commit hook vers {backup_file}")
        shutil.copy2(post_commit_target, backup_file)
    
    # Installer les nouveaux hooks
    print("🔧 Installation du hook pre-commit...")
    shutil.copy2(pre_commit_file, pre_commit_target)
    pre_commit_target.chmod(pre_commit_target.stat().st_mode | stat.S_IEXEC)
    
    print("🔧 Installation du hook post-commit...")
    shutil.copy2(post_commit_file, post_commit_target)
    post_commit_target.chmod(post_commit_target.stat().st_mode | stat.S_IEXEC)
    
    # Installer le script keep_test_user.py dans le répertoire racine
    keep_user_script = Path.cwd() / 'keep_test_user.py'
    if keep_user_script.exists():
        keep_user_target = project_root / 'keep_test_user.py'
        print(f"🔧 Installation du script keep_test_user.py dans {project_root}...")
        shutil.copy2(keep_user_script, keep_user_target)
        keep_user_target.chmod(keep_user_target.stat().st_mode | stat.S_IEXEC)
    else:
        print("⚠️ Script keep_test_user.py non trouvé. Les hooks ne fonctionneront pas correctement sans ce fichier.")
    
    print("""
✅ Hooks Git installés avec succès!

Les hooks vont maintenant:
1. Sauvegarder le mot de passe de l'utilisateur test avant chaque commit
2. Restaurer le mot de passe après chaque commit

Remarque: Pour désinstaller les hooks, supprimez les fichiers:
- {pre_commit_target}
- {post_commit_target}
    """.format(pre_commit_target=pre_commit_target, post_commit_target=post_commit_target))
    
    return 0

if __name__ == "__main__":
    exit(main()) 
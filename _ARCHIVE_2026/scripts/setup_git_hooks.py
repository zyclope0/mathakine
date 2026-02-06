#!/usr/bin/env python3
"""
🔧 Script d'installation des hooks Git pour Mathakine
Configure automatiquement les hooks pre-commit et post-merge.
"""

import os
import shutil
import stat
from pathlib import Path

class GitHooksInstaller:
    """Installateur des hooks Git"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.git_hooks_dir = self.project_root / ".git" / "hooks"
        self.custom_hooks_dir = self.project_root / ".githooks"
        
    def check_git_repository(self) -> bool:
        """Vérifie que nous sommes dans un dépôt Git"""
        git_dir = self.project_root / ".git"
        if not git_dir.exists():
            print("❌ Erreur: Ce n'est pas un dépôt Git")
            print("💡 Initialisez d'abord un dépôt: git init")
            return False
        return True
    
    def create_hooks_directory(self):
        """Crée le répertoire des hooks s'il n'existe pas"""
        self.git_hooks_dir.mkdir(exist_ok=True)
        print(f"📁 Répertoire hooks: {self.git_hooks_dir}")
    
    def install_hook(self, hook_name: str) -> bool:
        """Installe un hook spécifique"""
        source_hook = self.custom_hooks_dir / hook_name
        target_hook = self.git_hooks_dir / hook_name
        
        if not source_hook.exists():
            print(f"⚠️  Hook source non trouvé: {source_hook}")
            return False
        
        try:
            # Copier le hook
            shutil.copy2(source_hook, target_hook)
            
            # Rendre exécutable
            current_permissions = target_hook.stat().st_mode
            target_hook.chmod(current_permissions | stat.S_IEXEC)
            
            print(f"✅ Hook installé: {hook_name}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'installation de {hook_name}: {e}")
            return False
    
    def create_pre_commit_hook(self):
        """Crée le hook pre-commit s'il n'existe pas"""
        hook_content = '''#!/bin/bash
# 🔍 Hook pre-commit pour Mathakine
# Exécute les vérifications automatiques avant chaque commit

set -e

echo "🔍 Exécution des vérifications pre-commit..."

# Vérifier que Python est disponible
if ! command -v python &> /dev/null; then
    echo "❌ Python n'est pas installé ou accessible"
    exit 1
fi

# Exécuter le script de vérification Python
python scripts/pre_commit_check.py

# Récupérer le code de sortie
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ Toutes les vérifications sont passées"
    echo "🚀 Commit autorisé"
else
    echo ""
    echo "❌ Des vérifications ont échoué"
    echo "🚫 Commit bloqué"
    echo ""
    echo "💡 Pour forcer le commit (non recommandé):"
    echo "   git commit --no-verify"
fi

exit $exit_code
'''
        
        hook_file = self.custom_hooks_dir / "pre-commit"
        hook_file.parent.mkdir(exist_ok=True)
        
        with open(hook_file, 'w', encoding='utf-8') as f:
            f.write(hook_content)
        
        # Rendre exécutable
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
        print(f"📝 Hook pre-commit créé: {hook_file}")
    
    def create_post_merge_hook(self):
        """Crée le hook post-merge pour mettre à jour les dépendances"""
        hook_content = '''#!/bin/bash
# 🔄 Hook post-merge pour Mathakine
# Met à jour les dépendances après un merge

echo "🔄 Post-merge: Vérification des mises à jour..."

# Vérifier si requirements.txt a changé
if git diff-tree -r --name-only --no-commit-id HEAD@{1} HEAD | grep -q "requirements.txt"; then
    echo "📦 requirements.txt a changé, mise à jour des dépendances..."
    pip install -r requirements.txt
fi

# Vérifier si des migrations sont nécessaires
if git diff-tree -r --name-only --no-commit-id HEAD@{1} HEAD | grep -q "migrations/"; then
    echo "🗃️  Nouvelles migrations détectées"
    echo "💡 Pensez à exécuter: python mathakine_cli.py migrate"
fi

echo "✅ Post-merge terminé"
'''
        
        hook_file = self.custom_hooks_dir / "post-merge"
        hook_file.parent.mkdir(exist_ok=True)
        
        with open(hook_file, 'w', encoding='utf-8') as f:
            f.write(hook_content)
        
        # Rendre exécutable
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
        print(f"📝 Hook post-merge créé: {hook_file}")
    
    def backup_existing_hooks(self):
        """Sauvegarde les hooks existants"""
        hooks_to_backup = ["pre-commit", "post-merge"]
        
        for hook_name in hooks_to_backup:
            existing_hook = self.git_hooks_dir / hook_name
            if existing_hook.exists():
                backup_name = f"{hook_name}.backup"
                backup_path = self.git_hooks_dir / backup_name
                shutil.copy2(existing_hook, backup_path)
                print(f"💾 Sauvegarde: {hook_name} → {backup_name}")
    
    def install_all_hooks(self) -> bool:
        """Installe tous les hooks"""
        print("🔧 Installation des hooks Git pour Mathakine")
        print("=" * 50)
        
        if not self.check_git_repository():
            return False
        
        # Créer les hooks personnalisés s'ils n'existent pas
        if not (self.custom_hooks_dir / "pre-commit").exists():
            self.create_pre_commit_hook()
        
        if not (self.custom_hooks_dir / "post-merge").exists():
            self.create_post_merge_hook()
        
        # Créer le répertoire des hooks Git
        self.create_hooks_directory()
        
        # Sauvegarder les hooks existants
        self.backup_existing_hooks()
        
        # Installer les hooks
        hooks_installed = 0
        hooks_to_install = ["pre-commit", "post-merge"]
        
        for hook_name in hooks_to_install:
            if self.install_hook(hook_name):
                hooks_installed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Résultat: {hooks_installed}/{len(hooks_to_install)} hooks installés")
        
        if hooks_installed == len(hooks_to_install):
            print("🎉 Installation réussie !")
            print("\n💡 Utilisation:")
            print("  • Les tests critiques s'exécuteront automatiquement avant chaque commit")
            print("  • Pour ignorer les vérifications: git commit --no-verify")
            print("  • Pour tester manuellement: python scripts/pre_commit_check.py")
            return True
        else:
            print("⚠️  Installation partielle")
            return False
    
    def uninstall_hooks(self):
        """Désinstalle les hooks"""
        print("🗑️  Désinstallation des hooks Git")
        
        hooks_to_remove = ["pre-commit", "post-merge"]
        
        for hook_name in hooks_to_remove:
            hook_file = self.git_hooks_dir / hook_name
            backup_file = self.git_hooks_dir / f"{hook_name}.backup"
            
            if hook_file.exists():
                hook_file.unlink()
                print(f"🗑️  Hook supprimé: {hook_name}")
                
                # Restaurer la sauvegarde si elle existe
                if backup_file.exists():
                    shutil.move(backup_file, hook_file)
                    print(f"🔄 Sauvegarde restaurée: {hook_name}")
        
        print("✅ Désinstallation terminée")

def main():
    """Point d'entrée principal"""
    import sys
    
    installer = GitHooksInstaller()
    
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        installer.uninstall_hooks()
    else:
        success = installer.install_all_hooks()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
🔄 Script de mise à jour automatique des tests après modifications
Détecte les changements dans le code et suggère/crée les tests correspondants.
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileChange:
    """Représente un changement de fichier"""
    path: str
    change_type: str  # 'added', 'modified', 'deleted'
    lines_added: int
    lines_removed: int

@dataclass
class TestSuggestion:
    """Suggestion de test à créer ou mettre à jour"""
    test_file: str
    test_function: str
    reason: str
    priority: str  # 'critical', 'important', 'supplementary'
    template: str

class TestUpdater:
    """Gestionnaire de mise à jour des tests"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.changes = []
        self.suggestions = []
        
        # Mapping des fichiers vers leurs tests
        self.file_to_test_mapping = {
            'app/services/user_service.py': 'tests/unit/test_user_service.py',
            'app/services/exercise_service.py': 'tests/unit/test_exercise_service.py',
            'app/services/logic_challenge_service.py': 'tests/unit/test_logic_challenge_service.py',
            'app/services/auth_service.py': 'tests/unit/test_auth_service.py',
            'app/models/user.py': 'tests/unit/test_models.py',
            'app/models/exercise.py': 'tests/unit/test_models.py',
            'app/models/logic_challenge.py': 'tests/unit/test_models.py',
            'app/api/endpoints/users.py': 'tests/api/test_users.py',
            'app/api/endpoints/exercises.py': 'tests/api/test_exercises.py',
            'app/api/endpoints/challenges.py': 'tests/api/test_challenges.py',
            'app/api/endpoints/auth.py': 'tests/api/test_auth.py',
        }
        
        # Patterns pour détecter les nouvelles fonctions/classes
        self.function_pattern = re.compile(r'^\s*def\s+(\w+)\s*\(', re.MULTILINE)
        self.class_pattern = re.compile(r'^\s*class\s+(\w+)\s*\(', re.MULTILINE)
        self.endpoint_pattern = re.compile(r'@\w+\.(?:get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']', re.MULTILINE)

    def get_git_changes(self, since: str = "HEAD~1") -> List[FileChange]:
        """Récupère les changements Git depuis un commit"""
        try:
            # Obtenir la liste des fichiers modifiés
            cmd = ["git", "diff", "--name-status", since]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                print(f"⚠️  Erreur Git: {result.stderr}")
                return []
            
            changes = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 2:
                    status = parts[0]
                    file_path = parts[1]
                    
                    # Ignorer les fichiers non-Python et les tests
                    if not file_path.endswith('.py') or file_path.startswith('tests/'):
                        continue
                    
                    # Obtenir les statistiques de changement
                    stats_cmd = ["git", "diff", "--numstat", since, file_path]
                    stats_result = subprocess.run(stats_cmd, capture_output=True, text=True, cwd=self.project_root)
                    
                    lines_added, lines_removed = 0, 0
                    if stats_result.returncode == 0 and stats_result.stdout.strip():
                        stats = stats_result.stdout.strip().split('\t')
                        if len(stats) >= 2:
                            try:
                                lines_added = int(stats[0]) if stats[0] != '-' else 0
                                lines_removed = int(stats[1]) if stats[1] != '-' else 0
                            except ValueError:
                                pass
                    
                    change_type = {
                        'A': 'added',
                        'M': 'modified', 
                        'D': 'deleted'
                    }.get(status[0], 'modified')
                    
                    changes.append(FileChange(
                        path=file_path,
                        change_type=change_type,
                        lines_added=lines_added,
                        lines_removed=lines_removed
                    ))
            
            return changes
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des changements Git: {e}")
            return []

    def analyze_file_changes(self, file_path: str) -> List[str]:
        """Analyse les changements dans un fichier pour détecter les nouvelles fonctions"""
        try:
            # Obtenir le contenu actuel
            full_path = self.project_root / file_path
            if not full_path.exists():
                return []
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Détecter les fonctions et classes
            functions = self.function_pattern.findall(content)
            classes = self.class_pattern.findall(content)
            endpoints = self.endpoint_pattern.findall(content)
            
            detected = []
            detected.extend([f"function:{func}" for func in functions])
            detected.extend([f"class:{cls}" for cls in classes])
            detected.extend([f"endpoint:{ep}" for ep in endpoints])
            
            return detected
            
        except Exception as e:
            print(f"⚠️  Erreur lors de l'analyse de {file_path}: {e}")
            return []

    def generate_test_suggestions(self, change: FileChange) -> List[TestSuggestion]:
        """Génère des suggestions de tests pour un changement"""
        suggestions = []
        
        # Trouver le fichier de test correspondant
        test_file = self.file_to_test_mapping.get(change.path)
        if not test_file:
            # Générer un nom de fichier de test par défaut
            if change.path.startswith('app/services/'):
                test_file = change.path.replace('app/services/', 'tests/unit/test_')
            elif change.path.startswith('app/api/endpoints/'):
                test_file = change.path.replace('app/api/endpoints/', 'tests/api/test_')
            elif change.path.startswith('app/models/'):
                test_file = 'tests/unit/test_models.py'
            else:
                test_file = f"tests/unit/test_{Path(change.path).stem}.py"
        
        # Analyser les changements dans le fichier
        detected_items = self.analyze_file_changes(change.path)
        
        for item in detected_items:
            item_type, item_name = item.split(':', 1)
            
            # Déterminer la priorité
            priority = 'supplementary'
            if 'service' in change.path.lower() or 'auth' in change.path.lower():
                priority = 'critical'
            elif 'api' in change.path.lower() or 'model' in change.path.lower():
                priority = 'important'
            
            # Générer le nom de la fonction de test
            if item_type == 'function':
                test_function = f"test_{item_name}"
            elif item_type == 'class':
                test_function = f"test_{item_name.lower()}_creation"
            elif item_type == 'endpoint':
                endpoint_name = item_name.replace('/', '_').replace('{', '').replace('}', '').strip('_')
                test_function = f"test_{endpoint_name}_endpoint"
            else:
                test_function = f"test_{item_name}"
            
            # Générer le template de test
            template = self.generate_test_template(item_type, item_name, change.path)
            
            suggestions.append(TestSuggestion(
                test_file=test_file,
                test_function=test_function,
                reason=f"Nouvelle {item_type} '{item_name}' détectée dans {change.path}",
                priority=priority,
                template=template
            ))
        
        # Suggestion générale si beaucoup de changements
        if change.lines_added > 50:
            suggestions.append(TestSuggestion(
                test_file=test_file,
                test_function=f"test_{Path(change.path).stem}_integration",
                reason=f"Changements importants ({change.lines_added} lignes) dans {change.path}",
                priority='important',
                template=self.generate_integration_test_template(change.path)
            ))
        
        return suggestions

    def generate_test_template(self, item_type: str, item_name: str, file_path: str) -> str:
        """Génère un template de test pour un élément spécifique"""
        
        if item_type == 'function':
            return f'''def test_{item_name}():
    """Teste la fonction {item_name}."""
    # TODO: Implémenter le test pour {item_name}
    # Arrange
    # Act
    # Assert
    pass'''
        
        elif item_type == 'class':
            return f'''def test_{item_name.lower()}_creation():
    """Teste la création d'une instance de {item_name}."""
    # TODO: Implémenter le test de création pour {item_name}
    # Arrange
    # Act
    # Assert
    pass'''
        
        elif item_type == 'endpoint':
            return f'''def test_{item_name.replace("/", "_").strip("_")}_endpoint(client):
    """Teste l'endpoint {item_name}."""
    # TODO: Implémenter le test pour l'endpoint {item_name}
    # Arrange
    # Act
    response = client.get("{item_name}")  # ou post, put, delete selon le cas
    # Assert
    # assert response.status_code == 200
    pass'''
        
        return f'''def test_{item_name}():
    """Teste {item_name}."""
    # TODO: Implémenter le test
    pass'''

    def generate_integration_test_template(self, file_path: str) -> str:
        """Génère un template de test d'intégration"""
        module_name = Path(file_path).stem
        return f'''def test_{module_name}_integration():
    """Test d'intégration pour {module_name}."""
    # TODO: Implémenter le test d'intégration
    # Ce test devrait vérifier l'interaction avec d'autres composants
    pass'''

    def check_existing_tests(self, suggestion: TestSuggestion) -> bool:
        """Vérifie si un test existe déjà"""
        test_path = self.project_root / suggestion.test_file
        if not test_path.exists():
            return False
        
        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return suggestion.test_function in content
        except Exception:
            return False

    def create_or_update_test_file(self, suggestion: TestSuggestion) -> bool:
        """Crée ou met à jour un fichier de test"""
        test_path = self.project_root / suggestion.test_file
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if test_path.exists():
                # Ajouter le test au fichier existant
                with open(test_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ajouter le nouveau test à la fin
                new_content = content.rstrip() + '\n\n' + suggestion.template + '\n'
                
                with open(test_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Test ajouté à {suggestion.test_file}: {suggestion.test_function}")
            else:
                # Créer un nouveau fichier de test
                template = f'''"""
Tests pour {suggestion.test_file.replace('tests/', '').replace('.py', '')}
Généré automatiquement le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pytest
from unittest.mock import Mock, patch


{suggestion.template}
'''
                with open(test_path, 'w', encoding='utf-8') as f:
                    f.write(template)
                
                print(f"📝 Nouveau fichier de test créé: {suggestion.test_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création/mise à jour de {suggestion.test_file}: {e}")
            return False

    def run_analysis(self, since: str = "HEAD~1", auto_create: bool = False) -> Dict:
        """Exécute l'analyse complète"""
        print("🔄 Analyse des changements et mise à jour des tests")
        print("=" * 60)
        
        # Récupérer les changements
        self.changes = self.get_git_changes(since)
        
        if not self.changes:
            print("ℹ️  Aucun changement détecté dans les fichiers Python")
            return {'changes': 0, 'suggestions': 0, 'created': 0}
        
        print(f"📊 {len(self.changes)} fichier(s) modifié(s) détecté(s)")
        
        # Générer les suggestions
        all_suggestions = []
        for change in self.changes:
            print(f"\n🔍 Analyse de {change.path} ({change.change_type})")
            suggestions = self.generate_test_suggestions(change)
            all_suggestions.extend(suggestions)
        
        # Filtrer les tests existants
        new_suggestions = []
        for suggestion in all_suggestions:
            if not self.check_existing_tests(suggestion):
                new_suggestions.append(suggestion)
            else:
                print(f"⚠️  Test existant ignoré: {suggestion.test_function}")
        
        self.suggestions = new_suggestions
        
        # Afficher les suggestions
        print(f"\n📋 {len(self.suggestions)} suggestion(s) de test(s)")
        
        critical_count = sum(1 for s in self.suggestions if s.priority == 'critical')
        important_count = sum(1 for s in self.suggestions if s.priority == 'important')
        supplementary_count = sum(1 for s in self.suggestions if s.priority == 'supplementary')
        
        print(f"  🔴 Critiques: {critical_count}")
        print(f"  🟡 Importants: {important_count}")
        print(f"  🟢 Complémentaires: {supplementary_count}")
        
        # Créer les tests si demandé
        created_count = 0
        if auto_create:
            print(f"\n🚀 Création automatique des tests...")
            for suggestion in self.suggestions:
                if self.create_or_update_test_file(suggestion):
                    created_count += 1
        else:
            print(f"\n💡 Pour créer automatiquement les tests:")
            print(f"   python scripts/update_tests_after_changes.py --auto-create")
            
            print(f"\n📝 Suggestions détaillées:")
            for suggestion in self.suggestions:
                priority_icon = {'critical': '🔴', 'important': '🟡', 'supplementary': '🟢'}[suggestion.priority]
                print(f"  {priority_icon} {suggestion.test_file}::{suggestion.test_function}")
                print(f"     Raison: {suggestion.reason}")
        
        return {
            'changes': len(self.changes),
            'suggestions': len(self.suggestions),
            'created': created_count
        }

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Met à jour les tests après modifications")
    parser.add_argument('--since', default='HEAD~1', help='Commit de référence (défaut: HEAD~1)')
    parser.add_argument('--auto-create', action='store_true', help='Créer automatiquement les tests')
    parser.add_argument('--dry-run', action='store_true', help='Afficher seulement les suggestions')
    
    args = parser.parse_args()
    
    updater = TestUpdater()
    
    if args.dry_run:
        args.auto_create = False
    
    results = updater.run_analysis(args.since, args.auto_create)
    
    print(f"\n📊 Résumé:")
    print(f"  • Fichiers analysés: {results['changes']}")
    print(f"  • Tests suggérés: {results['suggestions']}")
    print(f"  • Tests créés: {results['created']}")
    
    if results['suggestions'] > 0 and not args.auto_create:
        print(f"\n💡 Prochaines étapes:")
        print(f"  1. Examiner les suggestions ci-dessus")
        print(f"  2. Créer les tests: --auto-create")
        print(f"  3. Implémenter la logique des tests")
        print(f"  4. Exécuter: python scripts/pre_commit_check.py")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script pour vérifier tous les challenges créés dans la base de données.
Vérifie la structure technique, l'exactitude mathématique et la compatibilité avec le frontend.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def verify_challenge(challenge: LogicChallenge, index: int) -> dict:
    """Vérifie un challenge individuellement"""
    issues = []
    warnings = []
    
    # 1. Vérification des champs requis
    if not challenge.title:
        issues.append("❌ Title manquant")
    if not challenge.description:
        issues.append("❌ Description manquante")
    if not challenge.correct_answer:
        issues.append("❌ correct_answer manquant")
    if not challenge.solution_explanation:
        issues.append("❌ solution_explanation manquant")
    
    # 2. Vérification du challenge_type
    if challenge.challenge_type not in [ct.value for ct in LogicChallengeType]:
        issues.append(f"❌ challenge_type invalide: {challenge.challenge_type}")
    
    # 3. Vérification de l'age_group
    if challenge.age_group not in [ag.value for ag in AgeGroup]:
        issues.append(f"❌ age_group invalide: {challenge.age_group}")
    
    # 4. Vérification des hints (doit être une liste JSON)
    if challenge.hints:
        if isinstance(challenge.hints, str):
            try:
                hints_parsed = json.loads(challenge.hints)
                if not isinstance(hints_parsed, list):
                    issues.append(f"❌ hints n'est pas une liste: {type(hints_parsed)}")
            except json.JSONDecodeError:
                issues.append("❌ hints n'est pas un JSON valide")
        elif not isinstance(challenge.hints, list):
            issues.append(f"❌ hints n'est pas une liste: {type(challenge.hints)}")
    
    # 5. Vérification des choices (doit être une liste JSON)
    if challenge.choices:
        if isinstance(challenge.choices, str):
            try:
                choices_parsed = json.loads(challenge.choices)
                if not isinstance(choices_parsed, list):
                    issues.append(f"❌ choices n'est pas une liste: {type(choices_parsed)}")
                elif challenge.correct_answer and challenge.correct_answer not in choices_parsed:
                    warnings.append(f"⚠️  correct_answer '{challenge.correct_answer}' n'est pas dans les choices")
            except json.JSONDecodeError:
                issues.append("❌ choices n'est pas un JSON valide")
        elif not isinstance(challenge.choices, list):
            issues.append(f"❌ choices n'est pas une liste: {type(challenge.choices)}")
        elif challenge.correct_answer and challenge.correct_answer not in challenge.choices:
            warnings.append(f"⚠️  correct_answer '{challenge.correct_answer}' n'est pas dans les choices")
    
    # 6. Vérification de visual_data
    visual_data_ok = False
    if challenge.visual_data:
        if isinstance(challenge.visual_data, str):
            try:
                visual_data_parsed = json.loads(challenge.visual_data)
                if isinstance(visual_data_parsed, dict):
                    visual_data_ok = True
                    # Vérifier la structure selon le type
                    if challenge.challenge_type == LogicChallengeType.SPATIAL.value:
                        if "type" not in visual_data_parsed:
                            warnings.append("⚠️  visual_data pour SPATIAL devrait avoir un champ 'type'")
                    elif challenge.challenge_type == LogicChallengeType.VISUAL.value:
                        if "type" not in visual_data_parsed:
                            warnings.append("⚠️  visual_data pour VISUAL devrait avoir un champ 'type'")
            except json.JSONDecodeError:
                issues.append("❌ visual_data n'est pas un JSON valide")
        elif isinstance(challenge.visual_data, dict):
            visual_data_ok = True
        else:
            issues.append(f"❌ visual_data n'est pas un dict: {type(challenge.visual_data)}")
    else:
        # Certains types nécessitent visual_data
        if challenge.challenge_type in [LogicChallengeType.VISUAL.value, LogicChallengeType.SPATIAL.value]:
            warnings.append(f"⚠️  {challenge.challenge_type} devrait avoir visual_data pour un meilleur rendu")
    
    # 7. Vérification mathématique/logique selon le type
    if challenge.challenge_type == LogicChallengeType.SEQUENCE.value:
        # Vérifier que la réponse est cohérente avec la séquence
        if challenge.question and challenge.correct_answer:
            # Extraire les nombres de la séquence
            import re
            numbers = re.findall(r'\d+', challenge.question)
            if len(numbers) >= 2:
                try:
                    nums = [int(n) for n in numbers]
                    # Vérifier si c'est arithmétique
                    if len(nums) >= 3:
                        diff = nums[1] - nums[0]
                        if all(nums[i+1] - nums[i] == diff for i in range(len(nums)-1)):
                            expected = nums[-1] + diff
                            if str(expected) != challenge.correct_answer:
                                warnings.append(f"⚠️  Séquence arithmétique: attendu {expected}, trouvé {challenge.correct_answer}")
                except ValueError:
                    pass
    
    # 8. Vérification de la cohérence question/description
    if challenge.question and challenge.description:
        if challenge.question == challenge.description:
            warnings.append("⚠️  question et description sont identiques")
    
    # 9. Vérification de is_active
    if not challenge.is_active:
        warnings.append("⚠️  Challenge inactif (ne sera pas visible)")
    
    return {
        "id": challenge.id,
        "title": challenge.title,
        "type": challenge.challenge_type,
        "age_group": challenge.age_group,
        "issues": issues,
        "warnings": warnings,
        "has_visual_data": visual_data_ok,
        "has_hints": bool(challenge.hints),
        "has_choices": bool(challenge.choices),
    }


def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("🔍 VÉRIFICATION DES CHALLENGES DANS LA BASE DE DONNÉES")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    
    try:
        # Récupérer tous les challenges
        challenges = db.query(LogicChallenge).order_by(LogicChallenge.id).all()
        
        if not challenges:
            print("❌ Aucun challenge trouvé dans la base de données")
            return 1
        
        print(f"📊 {len(challenges)} challenges trouvés\n")
        
        total_issues = 0
        total_warnings = 0
        
        # Vérifier chaque challenge
        for i, challenge in enumerate(challenges, 1):
            result = verify_challenge(challenge, i)
            
            print(f"\n{'='*80}")
            print(f"Challenge #{i} - ID: {result['id']}")
            print(f"{'='*80}")
            print(f"📝 Titre: {result['title']}")
            print(f"🏷️  Type: {result['type']}")
            print(f"👥 Groupe d'âge: {result['age_group']}")
            print(f"🎨 Visual data: {'✅' if result['has_visual_data'] else '❌'}")
            print(f"💡 Hints: {'✅' if result['has_hints'] else '❌'}")
            print(f"📋 Choices: {'✅' if result['has_choices'] else '❌'}")
            
            if result['issues']:
                print(f"\n❌ PROBLÈMES ({len(result['issues'])}):")
                for issue in result['issues']:
                    print(f"   {issue}")
                total_issues += len(result['issues'])
            
            if result['warnings']:
                print(f"\n⚠️  AVERTISSEMENTS ({len(result['warnings'])}):")
                for warning in result['warnings']:
                    print(f"   {warning}")
                total_warnings += len(result['warnings'])
            
            if not result['issues'] and not result['warnings']:
                print("\n✅ Challenge OK")
            
            # Afficher les détails pour debug
            print(f"\n📄 Détails:")
            print(f"   Description: {challenge.description[:100]}..." if len(challenge.description) > 100 else f"   Description: {challenge.description}")
            if challenge.question:
                print(f"   Question: {challenge.question[:100]}..." if len(challenge.question) > 100 else f"   Question: {challenge.question}")
            print(f"   Réponse correcte: {challenge.correct_answer}")
            if challenge.choices:
                choices_str = challenge.choices if isinstance(challenge.choices, list) else json.loads(challenge.choices) if isinstance(challenge.choices, str) else []
                print(f"   Choices: {choices_str}")
            if challenge.hints:
                hints_str = challenge.hints if isinstance(challenge.hints, list) else json.loads(challenge.hints) if isinstance(challenge.hints, str) else []
                print(f"   Hints: {hints_str}")
            if challenge.visual_data:
                visual_str = str(challenge.visual_data)[:200] + "..." if len(str(challenge.visual_data)) > 200 else str(challenge.visual_data)
                print(f"   Visual data: {visual_str}")
        
        # Résumé
        print(f"\n{'='*80}")
        print("📊 RÉSUMÉ")
        print(f"{'='*80}")
        print(f"Total challenges: {len(challenges)}")
        print(f"Total problèmes: {total_issues}")
        print(f"Total avertissements: {total_warnings}")
        print(f"Challenges OK: {len(challenges) - total_issues}")
        
        if total_issues == 0:
            print("\n✅ Tous les challenges sont techniquement corrects!")
        else:
            print(f"\n❌ {total_issues} problème(s) à corriger")
        
        return 0 if total_issues == 0 else 1
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())


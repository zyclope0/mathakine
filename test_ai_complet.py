#!/usr/bin/env python3
"""
Test complet de la génération IA pour tous les types d'exercices
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TYPES = ["addition", "soustraction", "multiplication", "division", "mixte", "fractions", "geometrie", "divers", "texte"]
DIFFICULTIES = ["initie", "padawan", "chevalier", "maitre"]

def test_ai_generation():
    """Test de génération IA pour tous les types et difficultés"""
    print("🤖 TEST GÉNÉRATION IA - TOUS LES TYPES")
    print("=" * 50)
    
    total_tests = 0
    success_tests = 0
    
    for exercise_type in TYPES:
        print(f"\n📝 Type: {exercise_type.upper()}")
        print("-" * 30)
        
        for difficulty in DIFFICULTIES:
            total_tests += 1
            
            # Données pour la génération IA
            data = {
                "exercise_type": exercise_type,
                "difficulty": difficulty,
                "ai_generated": True  # ✅ GÉNÉRATION IA
            }
            
            try:
                response = requests.post(f"{BASE_URL}/api/exercises/generate", json=data)
                
                if response.status_code == 200:
                    exercise = response.json()
                    
                    # Vérifications
                    assert exercise["exercise_type"] == exercise_type.upper()
                    assert exercise["difficulty"] == difficulty
                    assert exercise["ai_generated"] == True  # ✅ Doit être True pour IA
                    assert "question" in exercise
                    assert "correct_answer" in exercise
                    assert "choices" in exercise
                    assert "explanation" in exercise
                    
                    # Vérifier le préfixe IA dans le titre ou l'explication
                    has_ai_prefix = ("[IA]" in exercise.get("title", "") or 
                                   "[IA]" in exercise.get("explanation", ""))
                    
                    print(f"  ✅ {difficulty}: {exercise['question'][:60]}...")
                    if has_ai_prefix:
                        print(f"     🤖 Contexte IA détecté")
                    
                    success_tests += 1
                    
                else:
                    print(f"  ❌ {difficulty}: Erreur HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {difficulty}: Erreur - {str(e)}")
    
    print(f"\n📊 RÉSULTATS FINAUX")
    print("=" * 50)
    print(f"✅ Tests réussis: {success_tests}/{total_tests}")
    print(f"📈 Taux de réussite: {(success_tests/total_tests)*100:.1f}%")
    
    if success_tests == total_tests:
        print("🎉 TOUS LES TESTS RÉUSSIS ! Génération IA complète opérationnelle.")
    else:
        print(f"⚠️  {total_tests - success_tests} tests ont échoué.")
    
    return success_tests == total_tests

if __name__ == "__main__":
    test_ai_generation() 
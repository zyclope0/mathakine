#!/usr/bin/env python3
"""
Test spécifique des types MIXTE et TEXTE avec génération IA
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
DIFFICULTIES = ["initie", "padawan", "chevalier", "maitre"]

def test_mixte_ai():
    """Test du type MIXTE avec IA"""
    print("🎲 TEST TYPE MIXTE AVEC IA")
    print("=" * 40)
    
    for difficulty in DIFFICULTIES:
        data = {
            "exercise_type": "mixte",
            "difficulty": difficulty,
            "ai": True  # ✅ PARAMÈTRE CORRECT POUR L'IA
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/exercises/generate", json=data)
            
            if response.status_code == 200:
                exercise = response.json()
                
                print(f"✅ {difficulty.upper()}:")
                print(f"   Question: {exercise['question']}")
                print(f"   Réponse: {exercise['correct_answer']}")
                print(f"   IA: {exercise['ai_generated']}")
                print(f"   Titre: {exercise.get('title', 'N/A')}")
                
                # Vérifier le contexte Star Wars
                has_starwars = any(word in exercise['question'].lower() for word in 
                                 ['x-wing', 'tie', 'empire', 'rebelle', 'luke', 'leia', 'cantina', 'parsec', 'cristaux'])
                if has_starwars:
                    print(f"   🌟 Contexte Star Wars détecté")
                print()
                
            else:
                print(f"❌ {difficulty}: Erreur HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {difficulty}: Erreur - {str(e)}")

def test_texte_ai():
    """Test du type TEXTE avec IA"""
    print("📝 TEST TYPE TEXTE AVEC IA")
    print("=" * 40)
    
    for difficulty in DIFFICULTIES:
        data = {
            "exercise_type": "texte",
            "difficulty": difficulty,
            "ai": True  # ✅ PARAMÈTRE CORRECT POUR L'IA
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/exercises/generate", json=data)
            
            if response.status_code == 200:
                exercise = response.json()
                
                print(f"✅ {difficulty.upper()}:")
                print(f"   Question: {exercise['question']}")
                print(f"   Réponse: {exercise['correct_answer']}")
                print(f"   IA: {exercise['ai_generated']}")
                print(f"   Titre: {exercise.get('title', 'N/A')}")
                
                # Vérifier le contexte Star Wars
                has_starwars = any(word in exercise['question'].lower() for word in 
                                 ['r2-d2', 'c-3po', 'luke', 'yoda', 'jedi', 'padawan', 'obi-wan', 'leia'])
                if has_starwars:
                    print(f"   🌟 Contexte Star Wars détecté")
                print()
                
            else:
                print(f"❌ {difficulty}: Erreur HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {difficulty}: Erreur - {str(e)}")

if __name__ == "__main__":
    test_mixte_ai()
    print("\n" + "="*50 + "\n")
    test_texte_ai() 
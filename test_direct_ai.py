#!/usr/bin/env python3
"""
Test direct de generate_ai_exercise
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.exercise_generator import generate_ai_exercise

def test_direct_ai():
    """Test direct de generate_ai_exercise"""
    print("🤖 TEST DIRECT GENERATE_AI_EXERCISE")
    print("=" * 50)
    
    # Test MIXTE
    print("\n🎲 Test MIXTE:")
    result = generate_ai_exercise("mixte", "initie")
    print(f"Résultat: {result}")
    
    # Test TEXTE
    print("\n📝 Test TEXTE:")
    result = generate_ai_exercise("texte", "initie")
    print(f"Résultat: {result}")

if __name__ == "__main__":
    test_direct_ai() 